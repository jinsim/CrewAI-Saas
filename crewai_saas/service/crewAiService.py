import asyncio
import os
import logging
import threading
from textwrap import dedent
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from crewai_saas import crud
from crewai_saas.core.enum import CycleStatus, MessageRole
from crewai_saas.model import TaskWithContext, AgentWithTool, CrewWithAll, CycleCreate, MessageCreate, ChatCreate
from crewai_saas.tool import function_map

from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CrewAiStartService:
    def __init__(self, session):
        self.cycle_id = None
        self.chat_id = None
        # self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                           verbose=True,
                           temperature=0,
                           google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.session = session
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.thread.start()

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def append_message(self, task_id, task_mame, task_output): #특정 작업(task_id)에 메시지를 추가
        logger.info("Appending message for cycle: %s task: %s task_output: %s", self.cycle_id, task_mame, task_output)

        message_response = await crud.message.create(
            self.session,
            obj_in=MessageCreate(content=str(task_output), task_id=task_id, role=MessageRole.ASSISTANT, chat_id=self.chat_id, cycle_id=self.cycle_id)
        )

    def create_callback(self, task_id, task_name, task_output):
        async def async_callback():
            await self.append_message(task_id, task_name, task_output)

        return async_callback


    async def get_agent(self, agent):
        tools_from_db = await crud.tool.get_all_by_ids(self.session, agent.tool_ids)
        tools = [function_map[tool.key] for tool in tools_from_db]
        if not tools:
            raise ValueError("Tools list is invalid")

        return Agent(
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=tools,
            verbose=True,
            llm=self.llm
        )

    async def start(self, employed_crew_id, chat_id):
        # Fetch the employed_crew
        employed_crew = await crud.employed_crew.get_active(self.session, id=employed_crew_id)
        if not employed_crew:
            logger.error(f"Employed crew not found. employed_crew_id: {employed_crew_id}")
            raise Exception("Employed crew not found.")

        crew_id = employed_crew.crew_id
        # Fetch the crew
        crew = await crud.crew.get_active(self.session, id=crew_id)
        if not crew:
            logger.error(f"Crew not found. crew_id: {crew_id}")
            raise Exception("Crew not found.")

        # Fetch agents associated with the crew
        agents = await crud.agent.get_all_active_by_crew_id(self.session, crew.id)
        if not agents:
            logger.error(f"Agents not found for crew_id: {crew.id}")
            raise Exception("Agents not found.")

        new_cycle = await crud.cycle.create(self.session, obj_in=CycleCreate(chat_id=chat_id))
        self.cycle_id = new_cycle.id
        self.chat_id = chat_id

        conversation = "\n\nConversation History:\n"
        cycles = await crud.cycle.get_all_finished_by_chat_id(self.session, chat_id=chat_id)
        for cycle in cycles:
            messages_in_cycle = await crud.message.get_all_by_cycle_id(self.session, cycle_id=cycle.id)
            for message in messages_in_cycle:
                conversation += f'{{"role": "{message.role}", "message": "{message.content}"}}\n'


        logger.info(f"Conversation: {conversation}")

        # Helper function to create Agent instances
        async def get_agent(agent):
            tools = []
            if agent.tool_ids:
                tools_from_db = await crud.tool.get_all_by_ids(self.session, agent.tool_ids)
                tools = [function_map[tool.key] for tool in tools_from_db]

            data = {
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "tools": tools,
                "verbose": True,
                "llm": self.llm,
            }
            return Agent(**data)

        # Create a dictionary to hold Agent instances
        agent_dict = {agent.id: await get_agent(agent) for agent in agents}

        # Fetch tasks associated with the crew
        tasks = await crud.task.get_all_active_by_crew_id(self.session, crew.id)
        if not tasks:
            logger.error(f"Tasks not found for crew_id: {crew.id}")
            raise Exception("Tasks not found.")

        # Create a dictionary to hold Task instances
        task_dict = {}

        # Helper function to create Task instances
        async def get_task(task):
            # Get context tasks IDs
            context_task_ids = await crud.task_context.get_child_task_id_all_by_task_id(self.session, task.id)
            # Ensure context tasks are resolved before using them
            context_tasks = [task_dict.get(task_id) for task_id in context_task_ids]

            return Task(
                description=task.description+conversation,
                expected_output=task.expected_output,
                agent=agent_dict[task.agent_id],
                context=context_tasks,
                callback=lambda task_output: asyncio.run_coroutine_threadsafe(
                    self.create_callback(task.id, task.name, task_output)(), self.loop
                ).result()
            )

        # Populate task_dict with Task instances
        for task_id in crew.task_ids:
            task = await crud.task.get_active(self.session, id=task_id)
            if task:
                task_dict[task_id] = await get_task(task)

        # Create the Crew instance
        crew_instance = Crew(
            agents=list(agent_dict.values()),  # Convert dict values to list
            tasks=list(task_dict.values()),  # Convert dict values to list
            verbose=True,
        )

        result = crew_instance.kickoff()
        metrics = crew_instance.usage_metrics
        logger.info(f"metric : {metrics}")
        await self.append_message(None, "metrics: " + str(metrics))
        await self.append_message(None, "Crew AI Service Complete")
        return result
