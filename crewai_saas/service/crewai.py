from textwrap import dedent
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import threading

from crewai_saas import crud
from crewai_saas.model import TaskWithContext, AgentWithTool, CrewWithAll, CycleCreate, MessageCreate
from crewai_saas.tool import function_map
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import asyncio

# 나중에 수정해야함.
llm = ChatOpenAI(model="gpt-4o-mini")


# async def append_event_callback(self, event_name: str, task_output: str):
#     # logger.info("Callback called: %s", task_output)
#     print("Callback called: %s", task_output)
#     await append_event(self.job_id, event_name, task_output.exported_output)
#
#
# def async_callback_wrapper(self, callback, *args, **kwargs):
#     asyncio.run_coroutine_threadsafe(callback(*args, **kwargs), self.loop)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

loop = asyncio.new_event_loop()
thread = threading.Thread(target=start_loop, args=(loop,))
thread.start()

async def append_event(cycle_id, task_id, event_data):
    try:
        # with jobs_lock:
        cycle =  await crud.cycle.get(cycle_id)
        if cycle is None:
            # logger.info("Job does not exist  %s", job_id)
            print("cycle does not exist  %s", cycle_id)
            return {'message': ("cycle does not exist  %s", cycle_id)}
        else:
            print("Appending message for cycle : %s task : %s event : %s", cycle_id, task_id, event_data)
            # logger.info("Appending event for job %s: %s", job_id, event_data)
            message_response = await crud.message.create(MessageCreate(content=event_data, task_id=task_id, role="AGENT"))
            return message_response
    except Exception as e:
        print("Error in append_event", e)
        return {'message': "Error in append_event"}

async def append_event_callback(cycle_id, task_id, task_output):
    logger.info("Callback called: %s", task_output)
    await append_event(cycle_id, task_id, task_output.exported_output)


def async_callback_wrapper(callback, *args, **kwargs):
    print("async_callback_wrapper called")
    asyncio.run_coroutine_threadsafe(callback(*args, **kwargs), loop)

async def make_response(session, employed_crew_id):
    employed_crew = await crud.employed_crew.get(session, id=employed_crew_id)
    if not employed_crew:
        logger.error(f"EmployedCrew not found. employed_crew_id: {employed_crew_id}")
        return Exception("EmployedCrew not found.")

    crew = await crud.crew.get_active(session, id=employed_crew.crew_id)
    if not crew:
        logger.error(f"Crew not found. crew_id: {employed_crew.crew_id}")
        return Exception("Crew not found.")

    tasks = await crud.task.get_all_active_by_crew_id(session, crew.id)
    if not tasks:
        logger.error(f"Task not found. crew_id: {crew.id}")
        return Exception("Task not found.")

    tasks_with_context = [
        TaskWithContext(**task.dict(), context_task_ids=await crud.task_context.get_child_task_id_all_by_task_id(session, task.id))
        for task in tasks
    ]

    agents = await crud.agent.get_all_active_by_crew_id(session, crew.id)
    if not agents:
        logger.error(f"Agent not found. crew_id: {crew.id}")
        return Exception("Agent not found.")

    agent_with_tools = [
        AgentWithTool(**agent.dict(), tools=await crud.tool.get_all_by_ids(session, agent.tool_ids))
        for agent in agents
    ]

    crew_dict = crew.dict()
    crew_dict['tasks'] = tasks_with_context
    crew_dict['agents'] = agent_with_tools
    crew_with_task = CrewWithAll(**crew_dict)
    return {"crew": crew_with_task}

async def start(session, crew_id):

    crew = await crud.crew.get_active(session, id=crew_id)
    if not crew:
        logger.error(f"Crew not found. crew_id: {crew_id}")
        raise Exception("Crew not found.")

    agents = await crud.agent.get_all_active_by_crew_id(session, crew.id)
    if not agents:
        logger.error(f"Agent not found. crew_id: {crew.id}")
        return Exception("Agent not found.")

    cycle = await crud.cycle.create(session, obj_in=CycleCreate(crew_id=crew_id, status="STARTED"))
    async def get_agent(agent):
        # Fetch tools from the database
        tools_from_db = await crud.tool.get_all_by_ids(session, agent.tool_ids)

        # Map tools using function_map
        tools = [function_map[tool.key] for tool in tools_from_db]

        # Debugging: Print the tools for verification
        # print("Tools fetched and mapped:", tools)

        # Ensure the tools list is correctly populated
        if tools is None:
            raise ValueError("Tools list is None")

        if not tools:
            raise ValueError("Tools list is empty")

        # Construct the data dictionary
        data = {
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "tools": tools,
            "verbose": True,
            "llm": llm,
        }

        # Debugging: Print the entire data dictionary
        # print("Data dictionary for Agent:", data)

        # Return the Agent instance
        return Agent(**data)

    agent_dict = {agent.id: await get_agent(agent) for agent in agents}

    tasks = await crud.task.get_all_active_by_crew_id(session, crew.id)
    if not tasks:
        logger.error(f"Tasks not found for crew_id: {crew.id}")
        raise Exception("Tasks not found.")

    task_dict = {}

    async def get_task(task):
        print(task.dict())
        return Task(
            description=task.description,
            expected_output=task.expected_output,
            agent=agent_dict[task.agent_id],
            context=[task_dict[task_id] for task_id in await crud.task_context.get_child_task_id_all_by_task_id(session, task.id)],
            callback=lambda task_output: async_callback_wrapper(append_event_callback, cycle.id, task.id, task_output),
        )

    for task_id in crew.task_ids:
        task_dict[task_id] = await get_task(await crud.task.get_active(session, id=task_id))

    crew = Crew(
        agents=agent_dict.values(),
        tasks=task_dict.values(),
        verbose=True,
    )
    # result = crew.kickoff()
    return None
