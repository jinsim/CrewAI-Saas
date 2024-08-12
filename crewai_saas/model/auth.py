from gotrue import User, UserAttributes
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class UserIn(Token, User):
    pass


class UserCreate(BaseModel):
    pass


class UserUpdate(UserAttributes):
    pass



class UserInDBBase(BaseModel):
    pass

class UserOut(Token):
    pass


class UserInDB(User):
    pass