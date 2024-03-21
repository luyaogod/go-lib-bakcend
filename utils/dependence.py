from models import User
from fastapi import HTTPException,status
from settings import ADMIN_NAME

user_auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid user",
)

admin_auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin",
)

async def user_auth_dependencie(uuid: str):
    user = await User.get_or_none(uuid=uuid)
    if not user:
        raise user_auth_exception
    return user

async def admin_auth_dependencie(uuid:str):
    user = await User.get_or_none(uuid=uuid)
    if user:
        if user.username == ADMIN_NAME:
            return user
        else:
            raise admin_auth_exception
    else:
        raise admin_auth_exception