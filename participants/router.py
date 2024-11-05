from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.bacis_auth import get_password_hash
from participants.database import get_async_session
from participants.models import participant
from participants.schemas import Participant

router = APIRouter(prefix="", tags=["/api/clients"])


@router.post("/create")
async def create_participant(
    avatar: UploadFile = File(),
    data: Participant = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    data.password = get_password_hash(data.password)
    image_path = f"images/old_images/{data.email}_{avatar.filename}"
    try:
        statement = insert(participant).values(data.model_dump())
    except IntegrityError:
        session.rollback()

    with open(image_path, "wb") as image_file:
        image_file.write(avatar.file.read())
    await session.execute(statement)
    await session.commit()
    return {"status": "success"}
