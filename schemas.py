from pydantic import BaseModel,Field
from typing import List

class CreateSeatIn(BaseModel):
    lib_id:int
    seat_name_id:int

class CreateTaskIn(BaseModel):
    wx_url:str

class CreateUserIn(BaseModel):
    username:str

class SeatsListIn(BaseModel):
    seats: List[CreateSeatIn]
    class Config:
        json_schema_extra = {
            "example": {
                "seats": [
                    {"lib_id": 5, "seat_name_id": 604},
                    {"lib_id": 5, "seat_name_id": 605},
                    {"lib_id": 5, "seat_name_id": 606},
                    {"lib_id": 5, "seat_name_id": 607},
                    {"lib_id": 5, "seat_name_id": 608},
                    {"lib_id": 5, "seat_name_id": 609},
                ]
            }
        }
