import asyncio
from datetime import date
from typing import Annotated

import aiofiles
import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.bacis_auth import get_current_active_user, get_password_hash
from auth.schemas import User
from config import conf
from participants.database import get_async_session
from participants.models import participant, rating
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


@router.post("/{id}/match")
async def rate_member(
    current_user: Annotated[User, Depends(get_current_active_user)],
    id: int,
    session: AsyncSession = Depends(get_async_session),
):
    # Check if the member has already rated the other member today
    today = date.today()
    if id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot rate yourself")
    rating_query = select(rating).where(
        rating.c.member_id == current_user.id,
        rating.c.rated_member_id == id,
        rating.c.date == today,
    )
    rating_result = await session.execute(rating_query)
    if not rating_result.fetchone():
        # Add the rating to the database
        rating_insert = insert(rating).values(
            member_id=current_user.id, rated_member_id=id, date=today
        )
        await session.execute(rating_insert)
        await session.commit()
    else:
        raise HTTPException(
            status_code=400, detail="You have already rated this member today"
        )
    # Check if there is a mutual attraction
    try:
        mutual_rating_query_first = select(rating).where(
            rating.c.member_id == id,
            rating.c.rated_member_id == current_user.id,
        )
        mutual_rating_query_second = select(rating).where(
            rating.c.member_id == current_user.id,
            rating.c.rated_member_id == id,
        )

        mutual_rating_result_first = await session.execute(
            mutual_rating_query_first
        )

        mutual_rating_result_second = await session.execute(
            mutual_rating_query_second
        )

        first_query_dict = mutual_rating_result_first.fetchone()._mapping
        print("1", first_query_dict)
        second_query_dict = mutual_rating_result_second.fetchone()._mapping
        print("2", second_query_dict)
    except AttributeError:
        return {"message": "Rating successful"}

    if first_query_dict.get("member_id") == second_query_dict.get(
        "rated_member_id"
    ) and second_query_dict.get("member_id") == first_query_dict.get(
        "rated_member_id"
    ):
        # Send email to the members
        member_query = select(participant).where(
            participant.c.id == current_user.id
        )
        member_result = await session.execute(member_query)
        member_result_dict = member_result.fetchone()._mapping
        member_email = member_result_dict.get("email")
        rated_member_query = select(participant).where(participant.c.id == id)
        rated_member_result = await session.execute(rated_member_query)
        rated_member_result_dict = rated_member_result.fetchone()._mapping
        rated_member_email = rated_member_result_dict.get("email")
        print("member_email", member_email)
        print("rated_member_email", rated_member_email)
        message = MessageSchema(
            subject="You liked a member!",
            recipients=[
                member_email,
                rated_member_email,
            ],
            body=f"Member {rated_member_email} liked {rated_member_email}!",
            subtype="plain",
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"message": "We're golden"}
    else:
        raise HTTPException(
            status_code=400, detail="There is no mutual attraction"
        )
