from typing import ClassVar
from typing import Optional

from crewai_saas.model.base import InDBBase, ResponseBase

class Llm(ResponseBase):
    name: str
    description: Optional[str] = ""
    detail: Optional[str] = ""
    is_popular: Optional[bool] = False
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    llm_provider_id: int

    table_name: ClassVar[str] = "llm"

class LlmInDB(InDBBase):
    name: str
    description: Optional[str] = ""
    detail: Optional[str] = ""
    is_popular: Optional[bool] = False
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    llm_provider_id: int


class LlmProvider(ResponseBase):
    name: Optional[str] = ""

    table_name: ClassVar[str] = "llm_provider"

class LlmProviderWithLlms(LlmProvider):
    llms: list[Llm] = []

class LlmProviderInDB(InDBBase):
    name: Optional[str] = ""

