from typing_extensions import Self
from pydantic import BaseModel, Field, field_validator, model_validator
from ..core.custom_email_str import CustomEmailStr


class BaseUser(BaseModel):
    full_name: str = Field(description="Name and surname", min_length=5)
    email: CustomEmailStr


class UserIn(BaseUser):
    password: str = Field(min_length=5, max_length=20)

    @field_validator('password')
    @classmethod
    def check_password_complexity(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        return value


class UserRegister(UserIn):
    confirm_password: str
    agreement: bool

    @field_validator('agreement')
    @classmethod
    def check_agreement(cls, value):
        if not value:
            raise ValueError('You must accept terms')
        return value

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class UserOut(BaseUser):
    id: str


class UserInDb(UserOut):
    hashed_password: str
