from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import User
from participants.database import get_async_session
from participants.models import participant

router = APIRouter(prefix="/api/auth", tags=["auth"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain_password, hashed_password):
    byte_pwd = plain_password.encode("utf-8")
    return bcrypt.checkpw(byte_pwd, hashed_password)


def get_password_hash(password):
    byte_pwd = password.encode("utf-8")
    my_salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_pwd, my_salt)


async def get_current_user(
    db: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
):
    query = select(participant).where(participant.c.email == token)
    result = await db.execute(query)
    user = result.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    query = select(participant).where(
        participant.c.email == form_data.username
    )
    result = await db.execute(query)

    user = result.fetchone()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.email, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return JSONResponse(
        status_code=200,
        content={
            "message": f"User {current_user.email} is currently logged in"
        },
    )
