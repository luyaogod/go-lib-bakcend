from tortoise import Tortoise,run_async
from models import Lib,Seat,User,Task
from settings import TORTOISE_ORM
from settings import ADMIN_UUID,ADMIN_NAME
import json
from datetime import datetime,timedelta

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
    data = [
        {
            "username": "李世辉",
            "uuid": "8ee575c1-3cab-483e-bc2b-2d0061f7094d",
            "balance": 9999
        },
        {
            "username": "李冰冰",
            "uuid": "f3388810-9ee1-4559-991c-d4bf2a424813",
            "balance": 9999
        },
        {
            "username": "赵泽萱",
            "uuid": "7b4c71f4-4f8a-4ba0-b0ba-5ed8b3921cf0",
            "balance": 9999
        },
        {
            "username": "赵梓涵",
            "uuid": "cdacca01-7b6a-4f81-8b39-c3968d43de8a",
            "balance": 9999
        },
        {
            "username": "黄欣",
            "uuid": "8cc4a5e6-7b75-4bd4-8ed6-392728cadd01",
            "balance": 9999
        },
        {
            "username": "杨蝶",
            "uuid": "72850c7c-7eca-423b-b386-7c5f41cb164e",
            "balance": 9999
        },
        {
            "username": "刘力菀",
            "uuid": "081974bb-06cf-4e18-a3ea-7ca1ae3d90d1",
            "balance": 9999
        },
        {
            "username": "黄欣室友",
            "uuid": "05d413c0-2f9d-404d-93de-334c0d921a50",
            "balance": 9999
        },
        {
            "username": "张益瑄",
            "uuid": "b7e9abad-5981-4eed-b42a-847d03f95b08",
            "balance": 0
        },
        {
            "username": "洪昊仁",
            "uuid": "4e35dc67-07cf-431e-810b-808407df16ef",
            "balance": 30
        },
        {
            "username": "客户1",
            "uuid": "0d25aa38-3bd3-4f68-8140-c26979994b9d",
            "balance": 0
        },
        {
            "username": "王姿童",
            "uuid": "1a7e7a53-e204-4dd7-9eb0-b8a7c373a161",
            "balance": 26
        },
        {
            "username": "客户3",
            "uuid": "4d69cb47-86bc-4473-ab26-44ebe699c1e8",
            "balance": 0
        },
        {
            "username": "客户2",
            "uuid": "0ca24344-d424-4fe1-95d1-4a22fb6d5e3a",
            "balance": 26
        },
        {
            "username": "客户4",
            "uuid": "4b149cc9-3ecc-4333-9998-940bedab4346",
            "balance": 0
        },
        {
            "username": "客户5",
            "uuid": "7c018e97-1a82-475e-8b20-77d37a7c512d",
            "balance": 20
        },
        {
            "username": "客户6",
            "uuid": "1cae56d9-4fdb-4850-aec0-2e8d135ac360",
            "balance": 19
        },
        {
            "username": "客户7",
            "uuid": "e3ebd448-2539-4521-8206-78f404e39ebf",
            "balance": 0
        },
        {
            "username": "客户8",
            "uuid": "708d2a8f-f521-4dcc-b5e7-ee4c2f2f4977",
            "balance": 0
        },
        {
            "username": "客户9",
            "uuid": "8468698d-5069-414b-be2d-fe17aec51ec9",
            "balance": 0
        },
        {
            "username": "施韵",
            "uuid": "4862a048-a34f-4eb8-802c-979f3d1c38bf",
            "balance": 23
        },
        {
            "username": "客户10",
            "uuid": "4732a691-96d2-4c0f-ab00-dc4ca761fcf0",
            "balance": 0
        },
        {
            "username": "客户11",
            "uuid": "db889a77-bb24-41ef-8d4f-5de2158daad2",
            "balance": 0
        },
        {
            "username": "客户12",
            "uuid": "f450f9fd-b0a4-409c-9ed3-9afae6f355fb",
            "balance": 0
        },
        {
            "username": "客户13",
            "uuid": "e1f90841-8f6e-480c-9bb8-fae1f2f1c956",
            "balance": 16
        },
        {
            "username": "客户14",
            "uuid": "5f0a3545-8f81-4511-b0ac-a91bd39418a7",
            "balance": 19
        },
        {
            "username": "客户15",
            "uuid": "60874674-2193-4e08-b084-1abbc131d7f6",
            "balance": 25
        },
        {
            "username": "客户16",
            "uuid": "76b350f8-1437-4be3-89e1-0d8441145534",
            "balance": 22
        },
        {
            "username": "客户17",
            "uuid": "1dddbccb-45d7-448f-9a47-83dc1be3c2bd",
            "balance": 20
        },
        {
            "username": "客户18",
            "uuid": "043ffe61-63ae-41e1-8ccf-3369f6912654",
            "balance": 21
        },
        {
            "username": "客户19",
            "uuid": "afeb3c89-ea12-420c-b54a-8503ecd0df8e",
            "balance": 18
        },
        {
            "username": "客户20",
            "uuid": "49e1104e-dc9e-49c6-abed-d31ebf3b1170",
            "balance": 29
        },
        {
            "username": "客户21",
            "uuid": "1cdd6e33-11ca-48d9-8d50-7d329d8bb557",
            "balance": 0
        },
        {
            "username": "客户22",
            "uuid": "70840bd8-47a3-4fb6-a226-73614081b4fa",
            "balance": 28
        },
        {
            "username": "客户23",
            "uuid": "b6181614-f9ac-4806-b11f-88c3b630252e",
            "balance": 67
        },
        {
            "username": "客户24",
            "uuid": "3ccb8595-d68a-41be-9594-8b76b8a3f30a",
            "balance": 25
        },
        {
            "username": "客户25",
            "uuid": "a1d5f0cc-e9d4-46c8-b3ec-0cbd9484f856",
            "balance": 27
        },
        {
            "username": "客户26",
            "uuid": "4ae39ee3-2fb6-4454-8284-248de031e08d",
            "balance": 55
        },
        {
            "username": "客户27",
            "uuid": "47527ab6-63cc-4120-adc6-3ded74418f80",
            "balance": 30
        },
        {
            "username": "客户28",
            "uuid": "8199c088-3a28-48e5-b16c-0528c2fcec98",
            "balance": 0
        },
    ]
    for i in data:
        await User.create(username=i['username'], uuid=i['uuid'],balance=i['balance'])

    #高优先级任务
    now = datetime.now()
    now -= timedelta(days=1)
    add_time = datetime(now.year, now.month, now.day,8,0,0)
    wx_cookie = "cookie"
    vips = [ADMIN_NAME,"李世辉","黄欣","杨蝶","赵梓涵","刘力菀","李冰冰","赵泽萱"]
    for vip in vips:
        user = await User.get_or_none(username=vip)
        if user:
            await Task.create(add_time=add_time, wx_cookie=wx_cookie, user=user, status=0)
        else:
            print("用户不存在")


if __name__ == "__main__":
    run_async(main())