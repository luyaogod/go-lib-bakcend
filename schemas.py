from pydantic import BaseModel,Field

class CreateSeatIn(BaseModel):
    lib_id:int
    seat_name_id:int

class CreateTaskIn(BaseModel):
    wx_url:str

class CreateUserIn(BaseModel):
    username:str