import asyncio
import logging
from textwrap import dedent
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from crewai_saas import crud
from crewai_saas.model import TaskWithContext, AgentWithTool, CrewWithAll, CycleCreate, MessageCreate, ChatCreate
from crewai_saas.tool import function_map

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CrewAiStartService:
    def __init__(self, session):
        self.cycle_id = None
        self.chat_id = None
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.session = session
        self.loop = asyncio.get_event_loop()

    async def append_message(self, task_id, message_data):
        logger.info("Appending message for cycle: %s task: %s message: %s", self.cycle_id, task_id, message_data)
        try:
            cycle = await crud.cycle.get(self.session, id=self.cycle_id)
            if cycle is None:
                logger.error("Cycle does not exist %s", self.cycle_id)
                return {'message': "Cycle does not exist"}

            message_response = await crud.message.create(
                self.session,
                obj_in=MessageCreate(content=message_data, task_id=task_id, role="AGENT", chat_id=self.chat_id)
            )
            return message_response
        except Exception as e:
            logger.error("Error in append_message: %s", e)
            return {'message': "Error in append_message"}

    async def append_message_callback(self, task_id, task_output):
        logger.info("Callback called: %s", task_output)
        await self.append_message(task_id, task_output.exported_output)

    def async_callback_wrapper(self, callback, *args, **kwargs):
        logger.info("Async callback wrapper called")
        asyncio.run_coroutine_threadsafe(callback(*args, **kwargs), self.loop)

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

    async def start(self, employed_crew_id):
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

        # Create a new cycle and store its ID
        cycle = await crud.cycle.create(self.session, obj_in=CycleCreate(crew_id=crew_id, status="STARTED"))
        self.cycle_id = cycle.id

        chat = await (crud.chat.create(self.session, obj_in=ChatCreate(employed_crew_id=employed_crew_id))
                      if cycle.chat_id is None else crud.chat.get(self.session, id=cycle.chat_id))
        self.chat_id = chat.id

        # Helper function to create Agent instances
        async def get_agent(agent):
            tools_from_db = await crud.tool.get_all_by_ids(self.session, agent.tool_ids)
            tools = [function_map[tool.key] for tool in tools_from_db]

            if not tools:
                raise ValueError("Tools list is empty")

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
                description=task.description,
                expected_output=task.expected_output,
                agent=agent_dict[task.agent_id],
                context=context_tasks,
                callback=lambda task_output: self.async_callback_wrapper(self.append_message_callback, task.id,
                                                                         task_output),
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
        await self.append_message(None, "Crew AI Service Complete")

        return result
