from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from participants.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from participants.models import participant

router = APIRouter(prefix="/api", tags=["/list_of_clients"])


@router.get("/list")
async def list_participants(
    sex: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    sort_by: str = Query("date", regex="^(date|sex|first_name|last_name)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(participant)
    if sex:
        query = query.where(participant.c.sex == sex)
    if first_name:
        query = query.where(participant.c.first_name == first_name)
    if last_name:
        query = query.where(participant.c.last_name == last_name)
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
        }
        participants_dict.append(participant_dict)

    return participants_dict
