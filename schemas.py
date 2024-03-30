from pydantic import BaseModel,Field
from typing import List

class CreateSeatIn(BaseModel):
    lib_id:int
    seat_name_id:int

class CreateTaskIn(BaseModel):
    wx_url:str

class CreateUserIn(BaseModel):
    username:str
    balance:int

class SeatsListIn(BaseModel):
    seats: List[CreateSeatIn]
    class Config:
        json_schema_extra = {
            "example": {
                "seats": [
                    {"lib_id": 10073, "seat_name_id": 1},
                    {"lib_id": 10073, "seat_name_id": 2},
                    {"lib_id": 10073, "seat_name_id": 3},
                    {"lib_id": 10073, "seat_name_id": 4},
                    # {"lib_id": 10080, "seat_name_id": 608},
                    # {"lib_id": 10080, "seat_name_id": 609},
                ]
            }
        }
