import asyncio
import ctypes
import os
import logging
import threading
from textwrap import dedent
from crewai import Agent, Task, Crew
from crewai_saas import crud
from crewai_saas.core.enum import CycleStatus, MessageRole
from crewai_saas.model import TaskWithContext, AgentWithTool, CrewWithAll, CycleCreate, MessageCreate, ChatCreate
from crewai_saas.tool import function_map

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CrewAiStartService:
    def __init__(self, session):
        self.cycle_id = None
        self.chat_id = None
        # self.api_key = os.getenv("GOOGLE_API_KEY")
        # self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
        #                    verbose=True,
        #                    temperature=0,
        #                    google_api_key=self.api_key)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model="gpt-4o-mini",
                           verbose=True,
                           temperature=0,
                           openai_api_key=self.api_key)
        self.session = session
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.thread.start()
        self.thread_id = threading.get_ident()
        self.stop_requested = threading.Event() # 종료 플래그. start 메소드의 주요 루프에서 이 플래그를 확인

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def append_message(self, task_id, task_name, task_output, role):
        logger.info("Appending message for cycle: %s task: %s task_output: %s", self.cycle_id, task_name, task_output)

        message_response = await crud.message.create(
            self.session,
            obj_in=MessageCreate(content=task_name + " : " + str(task_output), task_id=task_id, role=role, chat_id=self.chat_id, cycle_id=self.cycle_id)
        )

    def create_callback(self, task_id, task_name, task_output):
        async def async_callback():
            await self.append_message(task_id, task_name, task_output, role=MessageRole.ASSISTANT)

        return async_callback

    def run_coroutine_in_thread(self, coro):
        """Run a coroutine in the thread's event loop and wait for the result."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    async def start(self, employed_crew_id, chat_id, cycle_id):
        self.cycle_id = cycle_id
        self.chat_id = chat_id
        await crud.cycle.update_execution_id(self.session, cycle_id=self.cycle_id, execution_id=self.thread_id)
        logger.info(f"Starting Crew AI Service for employed_crew_id: {employed_crew_id}, chat_id: {self.chat_id}, cycle_id: {self.cycle_id}, execution_id: {self.thread_id}")

        employed_crew = await crud.employed_crew.get_active(self.session, id=employed_crew_id)
        if not employed_crew:
            logger.error(f"Employed crew not found. employed_crew_id: {employed_crew_id}")
            raise Exception("Employed crew not found.")

        crew_id = employed_crew.crew_id

        crew = await crud.crew.get_active(self.session, id=crew_id)
        if not crew:
            logger.error(f"Crew not found. crew_id: {crew_id}")
            raise Exception("Crew not found.")

        published_crew = await crud.published_crew.get_active_by_crew_id_latest(self.session, crew_id=crew.id)
        if not published_crew:
            logger.error(f"Published crew not found. crew_id: {crew.id}")
            raise Exception("Published crew not found.")

        if employed_crew.is_owner:
            api_key = await crud.api_key.get_active_by_user_id_and_llm(self.session, user_id=employed_crew.user_id, llm_id=crew.llm_id)
            if not api_key:
                logger.error(f"API key not found for user_id: {employed_crew.user_id}, llm_id: {crew.llm_id}")
                raise Exception("API key not found.")
            self.api_key = api_key.value

        agents = await crud.published_agent.get_all_active_by_published_crew_id(self.session, published_crew_id=published_crew.id)
        if not agents:
            logger.error(f"Agents not found for published_crew_id: {published_crew.id}")
            raise Exception("Agents not found.")

        conversation = "\n\nConversation History:\n"
        cycles = await crud.cycle.get_all_finished_by_chat_id(self.session, chat_id=chat_id)
        for cycle in cycles:
            messages_in_cycle = await crud.message.get_all_by_cycle_id(self.session, cycle_id=cycle.id)
            for message in messages_in_cycle:
                conversation += f'{{"role": "{message.role}", "message": "{message.content}"}}\n'

        async def get_agent(agent):
            tools = []
            if agent.tool_ids:
                tools_from_db = await crud.tool.get_all_by_ids(self.session, agent.tool_ids)
                tools = [function_map[tool.key] for tool in tools_from_db]

            return Agent(
                role=dedent(agent.role),
                goal=dedent(agent.goal),
                backstory=dedent(agent.backstory),
                tools=tools,
                verbose=True,
                llm=self.llm,
                max_iter=10
            )

        agent_dict = {agent.id: await get_agent(agent) for agent in agents}
        print(agent_dict)
        tasks = await crud.published_task.get_all_active_by_published_crew_id(self.session, published_crew_id=published_crew.id)
        if not tasks:
            logger.error(f"Tasks not found for published_crew_id: {published_crew.id}")
            raise Exception("Tasks not found.")

        task_dict = {}

        async def get_task(task):
            context_tasks = []
            if task.context_published_task_ids:
                context_tasks = [task_dict.get(task_id) for task_id in task.context_published_task_ids]
            return Task(
                description=dedent(task.description+conversation),
                expected_output=dedent(task.expected_output),
                agent=agent_dict[task.published_agent_id],
                context=context_tasks,
                callback=lambda task_output: asyncio.run_coroutine_threadsafe(
                    self.create_callback(task.id, task.name, task_output)(), self.loop
                ).result()
            )
        for task_id in published_crew.published_task_ids:
            task = await crud.published_task.get_active(self.session, id=task_id)
            if task:
                task_dict[task_id] = await get_task(task)

        # logger.info(f"agent_dict : {agent_dict}")
        # logger.info(f"task_dict : {task_dict}")
        crew_instance = Crew(
            agents=list(agent_dict.values()),
            tasks=list(task_dict.values()),
            verbose=True,
        )
        logger.info(crew_instance)

        if not self.stop_requested.is_set():
            result = crew_instance.kickoff()
        else:
            logger.error(f"Operation stopped before kickoff. cycle_id: {self.cycle_id}")
            raise Exception("Operation stopped before kickoff")

        metrics = crew_instance.usage_metrics
        logger.info(f"metric : {metrics}")
        if result:
            logger.info("result : %s", result)
            self.run_coroutine_in_thread(
                self.append_message(None, "system", "metrics: " + str(metrics), role=MessageRole.SYSTEM)
            )
            if self.stop_requested.is_set():
                logger.error(f"Operation stopped after kickoff. cycle_id: {self.cycle_id}")
                await crud.cycle.update_status(self.session, cycle_id=self.cycle_id, status=CycleStatus.STOPPED)
            else:
                self.run_coroutine_in_thread(
                    crud.cycle.update_status(self.session, cycle_id=self.cycle_id, status=CycleStatus.FINISHED)
                )
        return result

    async def stop(self, cycle_id):
        cycle = await crud.cycle.get(self.session, id=cycle_id)
        if cycle.status == CycleStatus.STARTED:
            self.stop_requested.set()

            # 안전한 종료 대기
            wait_time = 0
            while wait_time < 10:  # 최대 10초 대기
                if cycle.status != CycleStatus.STARTED:
                    break
                await asyncio.sleep(1)
                wait_time += 1

            # 안전한 종료 실패 시 강제 종료
            if cycle.status == CycleStatus.STARTED:
                thread_id = cycle.thread_id
                if thread_id:
                    for thread in threading.enumerate():
                        if thread.ident == thread_id:
                            # 강제 종료 (주의: 이 방법은 위험할 수 있음)
                            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id),
                                                                       ctypes.py_object(SystemExit))
                            break

            await crud.cycle.update_status(self.session, cycle_id=cycle_id, status=CycleStatus.STOPPED)
            await self.cleanup_resources()

    async def cleanup_resources(self):
        logger.info(f"Cleaning up resources for cycle: {self.cycle_id}")
        await self.session.close()
        logging.shutdown()