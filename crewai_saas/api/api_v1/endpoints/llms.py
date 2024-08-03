from fastapi import APIRouter


from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import llm, llm_provider
from crewai_saas.schema import Llm, LlmProvider, LlmProviderWithLlms

router = APIRouter()

@router.get("/")
async def read_llms(session: SessionDep) -> list[LlmProviderWithLlms]:
    llm_providers = await llm_provider.get_all(session)
    ret = [
        LlmProviderWithLlms(**it.dict(), llms=await llm.get_all_by_provider_id(session, provider_id=it.id))
        for it in llm_providers
    ]
    return ret
