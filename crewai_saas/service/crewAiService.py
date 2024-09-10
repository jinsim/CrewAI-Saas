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

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        logger.info("Treading loop end")

    async def append_message(self, task_id, task_name, task_output, role):
        await self.check_cycle_status()
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
                max_iter=3
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

        await self.check_cycle_status()
        result = await crew_instance.kickoff_async()
        metrics = crew_instance.usage_metrics
        logger.info(f"metric : {metrics}")
        logger.info(f"result : {result}")

        if result:
            logger.info("result : %s", result)
            self.run_coroutine_in_thread(
                self.append_message(None, "system", "metrics: " + str(metrics), role=MessageRole.SYSTEM)
            )
            self.run_coroutine_in_thread(
                crud.cycle.update_status(self.session, cycle_id=self.cycle_id, status=CycleStatus.FINISHED)
            )
        return result

    async def check_cycle_status(self):
        get_cycle = await crud.cycle.get(self.session, id=self.cycle_id)
        if get_cycle.status == CycleStatus.STOPPED.value:
            logger.info(f"Cycle stopped. cycle_id: {self.cycle_id}")
            self.loop.stop()
            logger.info(f"Loop stopped. cycle_id: {self.cycle_id}")
            raise Exception("Cycle stopped!!!!!")
        
    async def stop(self, cycle_id):
        success = False
        msg = "cycle 의 status 가 STARTED 일때만 stop 가능합니다."
        cycle = await crud.cycle.get(self.session, id=cycle_id)
        logger.info(f"Stopping Crew AI Service for cycle: {cycle_id}, status: {cycle.status}")
        if cycle.status == CycleStatus.STARTED.value:
            success = True
            msg = "cycle 의 status 가 STOPPED 로 변경합니다."
            await crud.cycle.update_status(self.session, cycle_id=cycle_id, status=CycleStatus.STOPPED)
        return {"cycle id": cycle_id, "success": success, "msg": msg}