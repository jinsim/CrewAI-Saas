import os
import sys
import asyncio
import logging
import threading
import inspect
from textwrap import dedent
from typing import Dict, List, Any, Optional, Callable, Type
from contextlib import asynccontextmanager

from crewai import Agent, Task, Crew
from crewai_saas import crud
from crewai_saas.core.enum import CycleStatus, MessageRole, MessageType
from crewai_saas.model import MessageCreate
from crewai_saas.tool import function_map

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
# from langchain_upstage import ChatUpstage
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CrewAiStartService:
    def __init__(self, session):
        self.cycle_id = None
        self.chat_id = None
        self.api_key = None
        self.llm = None
        self.session = session
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.thread.start()
        self.thread_loop = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def start_loop(self, loop: asyncio.AbstractEventLoop):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        asyncio.set_event_loop(loop)
        loop.run_forever()
        logger.info("Threading loop ended")

    async def append_message(self, content: str, role: MessageRole, task_id: Optional[int] = None,
                             agent_id: Optional[int] = None, type: Optional[MessageType] = None):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        await self.check_cycle_status()
        logger.info(f"Appending message for cycle: {self.cycle_id} content: {content}")

        message_response = await crud.message.create(
            self.session,
            obj_in=MessageCreate(content=content, task_id=task_id, agent_id=agent_id,
                                 role=role, chat_id=self.chat_id, cycle_id=self.cycle_id, type=type)
        )

    def create_task_callback(self, task_id: int, task_name: str):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        async def async_callback(task_output: str):
            logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
            await self.append_message(f"[task] {task_name} : {task_output}",
                                      role=MessageRole.ASSISTANT, task_id=task_id, type=MessageType.TASK)

        return async_callback

    def create_agent_callback(self, agent_id: int, agent_name: str):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        async def async_callback(agent_output: str):
            logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
            await self.append_message(f"[agent] {agent_name} : {agent_output}",
                                      role=MessageRole.ASSISTANT, agent_id=agent_id, type=MessageType.AGENT)

        return async_callback

    def run_coroutine_in_thread(self, coro: Any):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        """Run a coroutine in the thread's event loop and wait for the result."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    async def start(self, employed_crew_id: int, chat_id: int, cycle_id: int):
        self.cycle_id = cycle_id
        self.chat_id = chat_id

        # Log the current thread and event loop
        current_thread = threading.current_thread()
        current_loop = asyncio.get_event_loop()
        logging.info(f"Start method - Thread: {current_thread.name}, Loop: {id(current_loop)}")
        logger.info(
            f"Starting Crew AI Service for employed_crew_id: {employed_crew_id}, chat_id: {self.chat_id}, cycle_id: {self.cycle_id}")

        # await crud.cycle.update_execution_id(self.session, cycle_id=self.cycle_id, execution_id=self.thread_id)
        logger.info(
            f"Starting Crew AI Service for employed_crew_id: {employed_crew_id}, chat_id: {self.chat_id}, cycle_id: {self.cycle_id}")

        employed_crew = await self.get_or_raise(crud.employed_crew.get_active, "id", employed_crew_id, "EmployedCrew")
        crew = await self.get_or_raise(crud.crew.get_active, "id", employed_crew.crew_id, "Crew")
        published_crew = await self.get_or_raise(crud.published_crew.get_active_by_crew_id_latest, "crew_id", crew.id,
                                                 "PublishedCrew")
        is_owner = employed_crew.is_owner
        running_crew = crew if is_owner else published_crew
        logger.info(f"Running Crew: {running_crew}")

        await self.setup_llm(employed_crew.profile_id, running_crew.llm_id, employed_crew.is_owner)

        conversation = await self.get_conversation_history(chat_id)

        agent_dict = await self.create_agents(is_owner, running_crew)
        task_dict = await self.create_tasks(is_owner, running_crew, agent_dict, conversation)
        logger.info(f"Agents: {agent_dict}")
        logger.info(f"Tasks: {task_dict}")

        crew_instance = Crew(
            agents=list(agent_dict.values()),
            tasks=list(task_dict.values()),
            verbose=True,
        )
        logger.info(crew_instance)

        await self.check_cycle_status()
        result = await crew_instance.kickoff_async()
        metrics = crew_instance.usage_metrics
        logger.info(f"metric: {metrics}")
        logger.info(f"result: {result}")

        if result:
            logger.info("result : %s", result)
            self.run_coroutine_in_thread(
                self.append_message("[system] system : metrics: " + str(metrics), role=MessageRole.SYSTEM)
            )
            self.run_coroutine_in_thread(
                crud.cycle.update_status(self.session, cycle_id=self.cycle_id, status=CycleStatus.FINISHED)
            )

        return result

    async def get_or_raise(self, getter: Callable, param_name: str, param_value: Any, entity_name: str):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        result = await getter(self.session, **{param_name: param_value})
        if not result:
            logger.error(f"{entity_name} not found. {param_name}: {param_value}")
            raise ValueError(f"{entity_name} not found.")
        return result
    # async def setup_upstage_llm(self):
    #     pass
    async def setup_llm(self, profile_id: int, llm_id: int, is_owner: bool):
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        # 우선 api key 존재 여부와, 소유자를 체크하지 않음
        # if is_owner:
        #     api_key = await crud.api_key.get_active_by_profile_id_and_llm(self.session, profile_id=profile_id, llm_id=llm_id)
        #     if not api_key:
        #         raise ValueError(f"API key not found for profile_id: {profile_id}, llm_id: {llm_id}")
        #     self.api_key = api_key.value
        # else:
            # Use default API keys for non-owners
        openai_api_key = os.getenv("OPENAI_API_KEY")  # Default OpenAI key
        google_api_key = os.getenv("GOOGLE_API_KEY")  # Default Google API key

        llm = await crud.llm.get(self.session, id=llm_id)
        if not llm:
            raise ValueError(f"LLM not found. llm_id: {llm_id}")

        if llm.llm_provider_id == 1:
            self.llm = ChatOpenAI(model=llm.name, verbose=True, temperature=0, openai_api_key=openai_api_key)
        elif llm.llm_provider_id == 2:
            self.llm = ChatGoogleGenerativeAI(model=llm.name, verbose=True, temperature=0,
                                              google_api_key=google_api_key)
        else:
            raise ValueError(f"LLM provider not found. llm_provider_id: {llm.llm_provider_id}")

    async def get_conversation_history(self, chat_id: int) -> str:
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        conversation = "\n\nConversation History:\n"
        cycles = await crud.cycle.get_all_finished_by_chat_id(self.session, chat_id=chat_id)
        for cycle in cycles:
            messages_in_cycle = await crud.message.get_all_by_cycle_id(self.session, cycle_id=cycle.id)
            conversation += '\n'.join(
                f'{{"role": "{message.role}", "message": "{message.content}"}}' for message in messages_in_cycle)
        return conversation

    async def create_agents(self, is_owner, running_crew) -> Dict[int, Agent]:
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        if is_owner:
            agents = await crud.agent.get_all_active_by_crew_id(self.session, crew_id=running_crew.id)
        else:
            agents = await crud.published_agent.get_all_active_by_published_crew_id(self.session,
                                                                                    published_crew_id=running_crew.id)
        if not agents:
            raise Exception(f"Agents not found for running_crew_id: {running_crew.id}")

        result = {}
        for agent in agents:
            logger.info(f"thread Id : {threading.get_ident()}, method Id : create_agent")
            tools = []
            if agent.tool_ids:
                tools_from_db = await crud.tool.get_all_by_ids(self.session, agent.tool_ids)
                tools = [function_map[tool.key] for tool in tools_from_db]

            result[agent.id] = Agent(
                role=dedent(agent.role),
                goal=dedent(agent.goal),
                backstory=dedent(agent.backstory),
                tools=tools,
                verbose=True,
                llm=self.llm,
                max_iter=10,
                step_callback=lambda agent_output: asyncio.run_coroutine_threadsafe(
                    self.create_agent_callback(agent.id, agent.name)(agent_output), self.loop
                ).result()
            )

        return result

    async def create_tasks(self, is_owner, running_crew, agent_dict: Dict[int, Agent], conversation: str) -> Dict[int, Task]:
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")

        if is_owner:
            tasks = await crud.task.get_all_active_by_crew_id(self.session, crew_id=running_crew.id)
            task_ids = running_crew.task_ids
        else:
            tasks = await crud.published_task.get_all_active_by_published_crew_id(self.session,
                                                                                  published_crew_id=running_crew.id)
            task_ids = running_crew.published_task_ids

        if not tasks:
            raise Exception(f"Tasks not found for running_crew_id: {running_crew.id}")

        task_dict = {}
        for task_id in task_ids:
            task = await crud.task.get_active(self.session, id=task_id) if is_owner else await crud.published_task.get_active(self.session, id=task_id)
            if task:
                context_tasks = [task_dict.get(task_id) for task_id in (task.context_task_ids or [])] if is_owner else [task_dict.get(task_id) for task_id in (task.context_published_task_ids or [])]
                task_dict[task_id] = Task(
                    description=dedent(task.description + conversation),
                    expected_output=dedent(task.expected_output),
                    agent=agent_dict[task.published_agent_id],
                    context=context_tasks,
                    callback=lambda task_output: asyncio.run_coroutine_threadsafe(
                        self.create_task_callback(task.id, task.name)(task_output), self.loop
                    ).result()
                )
        return task_dict

    async def check_cycle_status(self):
        # Log the current thread and event loop
        current_thread = threading.current_thread()
        current_loop = asyncio.get_event_loop()
        logging.info(f"Check cycle status - Thread: {current_thread.name}, Loop: {id(current_loop)}")

        try:
            get_cycle = await crud.cycle.get(self.session, id=self.cycle_id)
            logger.info(f"Cycle status: {get_cycle.status}")
            if get_cycle.status == CycleStatus.STOPPED.value:
                logging.info(f"Cycle stopped. cycle_id: {self.cycle_id}")
                raise Exception("Cycle stopped!")
        except Exception as e:
            logging.error(f"Error checking cycle status: {e}")
            raise e

    async def stop(self, cycle_id: int) -> Dict[str, Any]:
        logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
        cycle = await crud.cycle.get(self.session, id=cycle_id)
        if cycle.status == CycleStatus.STARTED.value:
            await crud.cycle.update_status(self.session, cycle_id=cycle_id, status=CycleStatus.STOPPED)
            return {"cycle id": cycle_id, "success": True, "msg": "Cycle status changed to STOPPED."}
        else:
            return {"cycle id": cycle_id, "success": False, "msg": "Cycle can only be stopped when status is STARTED."}
