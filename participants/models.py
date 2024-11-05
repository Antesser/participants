from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    String,
    Table,
)

from participants.database import metadata

participant = Table(
    "participants",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sex", String),
    Column("first_name", String),
    Column("last_name", String),
    Column("email", String, unique=True),
    Column("password", LargeBinary),
)
