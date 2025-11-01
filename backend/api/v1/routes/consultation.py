from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo, get_google_sheet
from backend.core.interfaces.consultation import ConsultationCreateDTO, ConsultationDTO
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.googlesheets.main import GoogleSheet

router = APIRouter(
    prefix=config.api_prefix.v1.consultation,
    tags=["Consultation"],
)


@router.post("/create")
async def create_consultation(
    consultation_data: ConsultationCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    google_sheet: Annotated[GoogleSheet, Depends(get_google_sheet)],
):
    new = await repo.consultation.create(
        fullname=consultation_data.fullname, phone_number=consultation_data.phone_number
    )

    consultations = await repo.consultation.get_consultations()
    result = []
    for cons in consultations:
        result.append(
            [
                cons.fullname,
                cons.phone_number,
                cons.created_at.strftime("%Y:%m:%d %H:%M:%S"),
            ]
        )
    google_sheet.update(worksheet_name="Заявки на консультацию", lists=result)
    return ConsultationDTO.model_validate(new, from_attributes=True)
