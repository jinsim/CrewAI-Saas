from textwrap import dedent

from crewai_saas import crud
from crewai_saas.schema import TaskWithContext, AgentWithTool, CrewWithTask, TaskWithAgent

from crewai_saas.schema import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate, Chat, ChatCreate, ChatUpdate
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import asyncio


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

    # async def get_task_with_agents(task):
    #     context_task_id = await crud.task_context.get_child_task_id_all_by_task_id(session, task_id=task.id)
    #     agents = await crud.agent.get_all_by_task_id(session, task.id)
    #     agent_with_tools = [
    #         AgentWithTool(**agent.dict(), tools=await crud.tool.get_all_by_ids(session, agent.tool_ids))
    #         for agent in agents
    #     ]
    #     task_with_agent = TaskWithAgent(**task.dict(), context_task_ids=context_task_id, agents=agent_with_tools)
    #     return task_with_agent

    task_with_agents = await asyncio.gather(*[get_task_with_agents(task) for task in tasks])
    crew_dict = crew.dict()
    crew_dict['tasks'] = task_with_agents
    crew_with_task = CrewWithTask(**crew_dict)
    return {"crew": crew_with_task}

# async def start(session, employed_crew_id):
#     employed_crew = await crud.employed_crew.get(session, id=employed_crew_id)
#     if not employed_crew:
#         logger.error(f"EmployedCrew not found. employed_crew_id: {employed_crew_id}")
#         return Exception("EmployedCrew not found.")
#
#     crew = await crud.crew.get_active(session, id=employed_crew.crew_id)
#     if not crew:
#         logger.error(f"Crew not found. crew_id: {employed_crew.crew_id}")
#         return Exception("Crew not found.")
#
#     tasks = await crud.task.get_all_active_by_crew_id(session, crew.id)
#     if not tasks:
#         logger.error(f"Task not found. crew_id: {crew.id}")
#         return Exception("Task not found.")
#
#     await crud.agent.get_all
#
#     async def get_agents(task):
#         context_task_id = await crud.task_context.get_child_task_id_all_by_task_id(session, task.id)
#         agents_model = await crud.agent.get_by_task_id(session, task.id)
#         agents = [
#             Agent(
#                 role=agent.role,
#                 goal=agent.goal,
#                 backstory=agent.backstory,
#                 tools=await crud.tool.get_all_by_ids(session, agent.tool_ids),
#                 verbose=True,
#             )
#             for agent in agents_model
#         ]
#         task_with_agent = TaskWithAgent(**task.dict(), context_task_ids=context_task_id, agents=agent_with_tools)
#         return task_with_agent
#
#     task_with_agents = await asyncio.gather(*[get_task_with_agents(task) for task in tasks])
#
#     Crew()
#
#
#     return {"crew": crew_with_task}