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


async def make_response(session, crew_id):
    crew = await crud.crew.get_active(session, id=crew_id)
    if not crew:
        logger.error(f"Crew not found. crew_id: {crew_id}")
        return Exception("Crew not found.")

    tasks = await crud.task.get_all_active_by_crew_id(session, crew.id)
    if not tasks:
        logger.error(f"Task not found. crew_id: {crew.id}")
        return Exception("Task not found.")


    if len(crew.task_ids) != len(tasks):
        logger.error(f"Task count is not matched. crew_id: {crew.id}, tasks : {tasks}, task_ids : {crew.task_ids}")
        return Exception("Task count is not matched.")

    # Sort tasks by crew's task_ids
    sorted_tasks = sorted(tasks, key=lambda task: crew.task_ids.index(task.id))

    agents = await crud.agent.get_all_active_by_crew_id(session, crew.id)
    if not agents:
        logger.error(f"Agent not found. crew_id: {crew.id}")
        return Exception("Agent not found.")

    agent_with_tools = [
        AgentWithTool(**agent.dict(), tools=await crud.tool.get_all_by_ids(session, agent.tool_ids))
        for agent in agents
    ]

    crew_dict = crew.dict()
    crew_dict['tasks'] = sorted_tasks
    crew_dict['agents'] = agent_with_tools
    crew_with_task = CrewWithAll(**crew_dict)
    return {"crew": crew_with_task}
