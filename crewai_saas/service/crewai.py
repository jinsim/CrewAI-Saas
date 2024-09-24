from textwrap import dedent
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import threading
import inspect

from crewai_saas import crud
from crewai_saas.model import TaskWithContext, AgentWithTool, CrewWithAll, CycleCreate, MessageCreate

import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def make_response(session, crew_id):
    logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
    crew = await crud.crew.get_active(session, id=crew_id)
    if not crew:
        logger.error(f"Crew not found. crew_id: {crew_id}")
        return Exception("Crew not found.")

    tasks = await crud.task.get_all_active_by_crew_id(session, crew.id)
    if not tasks:
        logger.error(f"Task not found. crew_id: {crew.id}")
        sorted_tasks = []
    elif crew.task_ids is not None:
        sorted_tasks = [task for task_id in crew.task_ids for task in tasks if task.id == task_id]
        if len(crew.task_ids) != len(tasks):
            logger.error(f"Task count is not matched. crew_id: {crew.id}, tasks : {tasks}, task_ids : {crew.task_ids}")
            sorted_task_table = sorted(tasks, key=lambda task: task.id, reverse=True)
            sorted_tasks += [task for task in sorted_task_table if task.id not in sorted_tasks]
    else:
        sorted_tasks = sorted(tasks, key=lambda task: task.id, reverse=True)

    agents = await crud.agent.get_all_active_by_crew_id(session, crew.id)
    if not agents:
        logger.error(f"Agent not found. crew_id: {crew.id}")
        agent_with_tools = []
    else:
        agent_with_tools = [
            AgentWithTool(**agent.dict(), tools=await crud.tool.get_all_by_ids(session, agent.tool_ids))
            for agent in agents
        ]

    crew_dict = crew.dict()
    crew_dict['tasks'] = sorted_tasks
    crew_dict['agents'] = agent_with_tools
    crew_with_task = CrewWithAll(**crew_dict)
    return {"crew": crew_with_task}
