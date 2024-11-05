from pydantic import BaseModel, Field, EmailStr


class Participant(BaseModel):
    sex: str = Field()
    first_name: str = Field()
    last_name: str = Field()
    email: EmailStr | None = Field()
    password: str | bytes = Field()
