from fastapi import APIRouter

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import test_item
from crewai_saas.schema import TestItem, TestItemCreate, TestItemUpdate

router = APIRouter()


@router.post("/create-test_item")
async def create_test_item(test_item_in: TestItemCreate, session: SessionDep) -> TestItem:
    return await test_item.create(session, obj_in=test_item_in)


@router.get("/read-all-test_item")
async def read_test_items(session: SessionDep) -> list[TestItem]:
    return await test_item.get_all(session)


@router.get("/get-by-id/{id}")
async def read_test_item_by_id(id: str, session: SessionDep) -> TestItem | None:
    return await test_item.get(session, id=id)


@router.get("/get-by-owner")
async def read_test_item_by_owner(session: SessionDep, user: CurrentUser) -> list[TestItem]:
    return await test_item.get_multi_by_owner(session, user=user)


@router.put("/update-test_item")
async def update_test_item(test_item_in: TestItemUpdate, session: SessionDep) -> TestItem:
    return await test_item.update(session, obj_in=test_item_in)


@router.delete("/delete/{id}")
async def delete_test_item(id: str, session: SessionDep) -> TestItem:
    return await test_item.delete(session, id=id)