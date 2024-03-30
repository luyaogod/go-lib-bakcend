from tortoise import Tortoise,run_async
from models import Lib,Seat,User
import json
from settings import TORTOISE_ORM
from settings import ADMIN_UUID,ADMIN_NAME
from api_funcs.admin_func import create_user


json_file_path = 'static/lib_and_id.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    data_lib_id = json.load(file)

async def init():
    await Tortoise.init(
        config=TORTOISE_ORM
    )

async def insert_lib(data):
    for key,value in data.items():
        await Lib.create(lib_name=key,lib_id=value)

libs = [10073, 10065, 10071, 10072, 10080, 10081, 10082, 10083, 10084, 10085, 10086, 10087, 10088, 10089, 10090, 10091, 10092, 11019, 11033, 11040, 11300, 11054, 11061, 11068, 11075, 11096, 11117, 11131, 11138, 11082, 11103, 11124, 11748]

async def insert_seat(libs):
    for i in libs:
        path = f'static/datastore/{i}.json'
        lib = await Lib.get_or_none(lib_id = i)
        # print(i)
        with open(path,'r',encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if item['name'] == None:
                    pass
                else:
                    seat_name = int(item['name'])
                    sea_key = item['key'] + '.'
                    await Seat.create(seat_id=seat_name, seat_key=sea_key, lib=lib)
            f.close()

#test---


async def main():
    await init()
    await Tortoise.generate_schemas()
    await insert_lib(data_lib_id)
    await insert_seat(libs)
    await User.create(username=ADMIN_NAME, uuid=ADMIN_UUID, balance=9999)
    # await create_user(username="李世辉",balance=9999)
    # await create_user(username="李冰冰",balance=9999)
    # await create_user(username="赵泽萱",balance=9999)
    # await create_user(username="赵梓涵",balance=9999)
    # await create_user(username="黄欣",balance=9999)
    # await create_user(username="杨蝶",balance=9999)
    # await create_user(username="张益瑄",balance=9999)
    # await create_user(username="洪昊仁",balance=30)



run_async(main())