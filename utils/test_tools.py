from tortoise import Tortoise
from settings import orm_conf
from models import Seat
import asyncio
from enum import Enum

HOST= '8.130.141.190'

async def init(host):
    await Tortoise.init(
        config=orm_conf(host)
    )

async def seat_query(lib:id,dir:str,dian:True,seat:int):
    """
    座位参数查询工具

    :param lib: 楼层号
    :param dian: 是否为电子阅览区
    :param seat: 座位号
    :param dir: 阅览区方向: 东 西 中
    :return:
    """
    if dian:
        lib_name = f"郑东校区-{lib}楼{dir}电子阅览区"
    else:
        lib_name = f"郑东校区-{lib}楼{dir}阅览区"

    host = HOST
    await init(host)
    print(lib_name)
    data = await Seat.get_or_none(lib__lib_name = lib_name,seat_id=seat)
    if data ==None:
        print('查无此座位')
    else:
        print(dict(data))

if __name__ == "__main__":
    asyncio.run(seat_query(2,'西',True,451))

