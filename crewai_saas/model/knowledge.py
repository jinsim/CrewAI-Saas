from typing import ClassVar
from typing import Optional

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase


class KnowledgeCreate(CreateBase):
    agent_id: Optional[int]
    published_agent_id: Optional[int]
    file_path: Optional[str]

class Knowledge(ResponseBase):
    agent_id: Optional[int]
    published_agent_id: Optional[int]
    file_path: Optional[str]
    is_deleted: bool

    table_name: ClassVar[str] = "knowledge"

class KnowledgeInDB(InDBBase):
    agent_id: Optional[int]
    published_agent_id: Optional[int]
    file_path: Optional[str]
    is_deleted: bool
