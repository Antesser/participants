from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth.bacis_auth import router as basic_auth_router
from logger import logging
from participants.all_participants_router import router as all_clients_router
from participants.database import create_table, drop_table
from participants.router import router as user_creation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # using lifespan to establish db conn once before starting an app and shut it down afterwards
    # await drop_table()
    logging.debug("DB is empty")
    await create_table()
    logging.debug("DB has been created")
    yield
    logging.debug("It's over now")


app = FastAPI(lifespan=lifespan)


app.include_router(user_creation_router)
app.include_router(basic_auth_router)
app.include_router(all_clients_router)
