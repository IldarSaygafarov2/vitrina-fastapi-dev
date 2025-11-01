from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import AdvertisementDTO
from backend.core.interfaces.agent import AgentDetailDTO, AgentListDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.agents,
    tags=["Агенты"],
)


@router.get("/")
async def get_all_agents(
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> list[AgentListDTO]:
    agents = await repo.users.get_users_by_role(role="REALTOR")
    return agents


@router.get("/{agent_id}/")
async def get_agent_detail(
    agent_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> AgentDetailDTO:
    agent = await repo.users.get_user_by_id(user_id=agent_id)
    advertisements = await repo.advertisements.get_user_advertisements(user_id=agent.id)
    advertisements = [
        AdvertisementDTO.model_validate(obj, from_attributes=True)
        for obj in advertisements
    ]

    return AgentDetailDTO(
        id=agent.id,
        first_name=agent.first_name,
        lastname=agent.lastname,
        tg_username=agent.tg_username,
        phone_number=agent.phone_number,
        user_photo=agent.profile_image,
        advertisements=advertisements,
    )
