from datetime import datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Column,
    Date,
    Float,
    ForeignKey,
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
    Column(
        "date", TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)
    ),
    Column("password", LargeBinary),
    Column("latitude", Float),
    Column("longitude", Float),
)


rating = Table(
    "ratings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("member_id", Integer, ForeignKey("participants.id")),
    Column("rated_member_id", Integer, ForeignKey("participants.id")),
    Column("date", Date),
)
