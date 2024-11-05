import asyncio
import aiofiles

import cv2
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.bacis_auth import get_password_hash
from participants.database import get_async_session
from participants.models import participant
from participants.schemas import Participant

router = APIRouter(prefix="/api/clients", tags=["/clients"])


@router.post("/create")
async def create_participant(
    avatar: UploadFile = File(),
    data: Participant = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    data.password = get_password_hash(data.password)
    file_name = avatar.filename
    image_path = f"images/old_images/{data.email}_{file_name}"

    try:
        statement = insert(participant).values(data.model_dump())
    except IntegrityError:
        session.rollback()
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(await avatar.read())
    # dealing with a blocking code
    await add_watermark(image_path, file_name)

    await session.execute(statement)
    await session.commit()
    return {"status": "success"}


# runing sync func in a separate thread
async def add_watermark(image_path, file_name):
    await asyncio.to_thread(sync_add_watermark, image_path, file_name)


def sync_add_watermark(
    path_to_image, file_name, watermark_file="images/uplocheno.jpg"
):
    result = f"images/new_images/{file_name}"
    image = cv2.imread(path_to_image)
    watermark = cv2.imread(watermark_file)

    watermark = cv2.resize(
        watermark, (image.shape[1] // 4, image.shape[0] // 4)
    )
    x_offset = image.shape[1] - watermark.shape[1] - 10
    y_offset = image.shape[0] - watermark.shape[0] - 10
    overlay = image.copy()
    overlay[
        y_offset : y_offset + watermark.shape[0],
        x_offset : x_offset + watermark.shape[1],
    ] = watermark
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    cv2.imwrite(result, image)
