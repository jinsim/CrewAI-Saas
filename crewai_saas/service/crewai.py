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
