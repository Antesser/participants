from pydantic import BaseModel, EmailStr, Field


class Participant(BaseModel):
    sex: str = Field()
    first_name: str = Field()
    last_name: str = Field()
    email: EmailStr | None = Field()
    password: str | bytes = Field()
    latitude: float = Field()
    longitude: float = Field()
