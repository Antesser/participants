from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.bacis_auth import get_current_user
from participants.database import get_async_session
from participants.models import participant

router = APIRouter(prefix="/api", tags=["/list_of_clients"])


@router.get("/list")
async def list_participants(
    sex: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    distance: Optional[float] = None,
    sort_by: str = Query("date", regex="^(date|sex|first_name|last_name)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[dict] = Depends(get_current_user),
):
    earth_rad = 6371
    query = select(participant)
    if sex:
        query = query.where(participant.c.sex == sex)
    if first_name:
        query = query.where(participant.c.first_name == first_name)
    if last_name:
        query = query.where(participant.c.last_name == last_name)
    if distance and current_user:
        # Calculate the distance between the current user and each participant
        distance_expr = (
            func.acos(
                func.sin(func.radians(participant.c.latitude))
                * func.sin(func.radians(current_user.latitude))
                + func.cos(func.radians(participant.c.latitude))
                * func.cos(func.radians(current_user.latitude))
                * func.cos(
                    func.radians(participant.c.longitude)
                    - func.radians(current_user.longitude)
                )
            )
            * earth_rad
        )
        query = query.where(distance_expr <= distance)
    if sort_by == "date":
        query = query.order_by(
            participant.c.date.desc()
            if sort_order == "desc"
            else participant.c.date.asc()
        )
    elif sort_by == "sex":
        query = query.order_by(
            participant.c.sex.desc()
            if sort_order == "desc"
            else participant.c.sex.asc()
        )
    elif sort_by == "first_name":
        query = query.order_by(
            participant.c.first_name.desc()
            if sort_order == "desc"
            else participant.c.first_name.asc()
        )
    elif sort_by == "last_name":
        query = query.order_by(
            participant.c.last_name.desc()
            if sort_order == "desc"
            else participant.c.last_name.asc()
        )
    result = await session.execute(query)
    participants = result.fetchall()

    # Convert the list of tuples to a list of dictionaries
    participants_dict = []
    for p in participants:
        participant_dict = {
            "id": p.id,
            "sex": p.sex,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "email": p.email,
            "date": p.date,
            "password": p.password,
            "latitude": p.latitude,
            "longitude": p.longitude,
        }
        participants_dict.append(participant_dict)

    return participants_dict
