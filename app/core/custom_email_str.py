from pydantic import EmailStr
from pydantic_core import PydanticCustomError


class CustomEmailStr(EmailStr):
    @classmethod
    def _validate(cls, input_value: str, /) -> str:
        try:
            return super()._validate(input_value)
        except PydanticCustomError as e:
            raise PydanticCustomError(e.type, e.message().capitalize())
