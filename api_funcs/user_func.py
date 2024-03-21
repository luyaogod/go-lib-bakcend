from models import User,Seat,Lib
from utils.get_cookie import get_wx_cookie
from utils.time_tools import get_set_time,time_validate
from my_celery import add_task
from datetime import datetime, timedelta ,timezone
from settings import USER_SEAT_SIZE


#tools
async def get_user(uuid):
    user = await User.get_or_none(uuid=uuid)
    if user:
        return user
    else:
        return None

#tools
async def get_seat(lib_id,seat_name_id):
    lib = await  Lib.get_or_none(pk=lib_id)
    if lib:
        data =  await Seat.get_or_none(seat_id=seat_name_id,lib=lib)
        if data:
            return data
        else:
            return None
    else:
        return None

#tools 用户常用座位数量限制
async def user_seat_size_validate(user)->int:
    data = await user.seats.all()
    user_seat_size = len(data)
    if user_seat_size>USER_SEAT_SIZE:
        return False
    else:
        return True

#func 添加座位
async def add_seat_user_relation(user,lib_id,seat_name_id):
    # user = await get_user(uuid)
    # if user:
    seat_size_validate = await user_seat_size_validate(user)
    if seat_size_validate:
        seat = await get_seat(lib_id,seat_name_id)
        if seat:
            await seat.user.add(user)
            return 0 #添加成功
        else:
            return -3 #座位不存在
    else:
        return -2 #用户可添加座位已满
    # else:
        # return -1 #用户不存在

#tools 校验自足座位信息并返回座位id列表
async def get_and_validate_seat_list(datalist):
    """
    datalist = [
        {"lib_id": 5, "seat_name_id": 604},
        {"lib_id": 5, "seat_name_id": 605},
        {"lib_id": 5, "seat_name_id": 606},
        {"lib_id": 5, "seat_name_id": 607},
        {"lib_id": 5, "seat_name_id": 608},
        {"lib_id": 5, "seat_name_id": 609},
    ]
    """
    id_list = []
    count = 1
    for data in datalist:
        seat = await get_seat(lib_id=data['lib_id'],seat_name_id=data['seat_name_id'])
        if seat:
             id_list.append(seat.id)
             count += 1
        else:
            return count
    else:
        return id_list

#tools 同时更新一组座位
async def update_user_seat_list(user,datalist):
    seat_id_list = await get_and_validate_seat_list(datalist)
    print(seat_id_list)
    if type(seat_id_list) == int:
        return seat_id_list #校验失败返回错误数据的位序
    else:
        await user.seats.clear()
        seats = await Seat.filter(id__in = seat_id_list)
        await user.seats.add(*seats)
        return 0

#func 删除座位
async def delete_seat_user_relation(user,seat_id):
    # user = await get_user(uuid)
    # if user:
    seat = await Seat.get_or_none(id=seat_id)
    if seat:
        await seat.user.remove(user)
        return 0 #删除成功
    else:
        return -2 #座位不存在
    # else:
        # return -1 #用户不存在

#func 获取所有座位
async def user_all_seat(user):
    # user = await get_user(uuid)
    # if user:
    data =  await user.seats.all().prefetch_related('lib')
    if not len(data)<1:
        seat_list = []
        for i in data:
            data_dict = {}
            data_dict['seat_data'] = dict(i)
            data_dict['seat_lib'] = dict(i.lib)
            seat_list.append(data_dict)
        return seat_list
    else:
        return None #用户无座位
    # else:
    #     return None  # 用户不存在

#tools 所有座位列表取楼层id和座位key
async def user_all_seats_clean(data):
    task_data_list = []
    for i in data:
        data_dict = {}
        data_dict["lib_id"] = str(i["seat_lib"]["lib_id"])
        data_dict["seat_key"] = i["seat_data"]["seat_key"]
        task_data_list.append(data_dict)
        return task_data_list

#tools-获取微信cookie
async def get_wechat_cookie(url:str):
    try:
        cookie =  await get_wx_cookie(url)
        if cookie and "Authorization" in cookie:
            return cookie
        else:
            return None
    except Exception as e:
        return None

#func 测试
async def add_task_func(user,wx_url):
    data =  await user_all_seat(user)
    if data:
        try:
            data =  await user_all_seats_clean(data)
            wx_cookie = await get_wechat_cookie(url =wx_url)
            if wx_cookie:
                data = add_task.delay(wx_cookie, data)
                print('- 任务已添加:', data.id)
                return 0
            else:
                return -3 #wxcookie无效
        except Exception:
            return -2 #数据处理未知错误
    else:
        return -1 #用户未绑定座位

#func 提交任务
# async def add_task_func(user,wx_url):
#     data =  await user_all_seat(user)
#     current_utc_time = datetime.now(timezone.utc)
#     result = time_validate(current_utc_time)
#     if result:
#         if data:
#             try:
#                 data = await user_all_seats_clean(data)
#                 wx_cookie = await get_wechat_cookie(url=wx_url)
#                 if wx_cookie:
#                     set_time = get_set_time(current_utc_time)
#                     data = add_task.apply_async(args=[wx_cookie, data], eta=set_time)
#                     print('- 任务已添加:', data.id)
#                     return 0
#                 else:
#                     return -3  # wxcookie无效
#             except Exception:
#                 return -2  # 数据处理未知错误
#         else:
#             return -1  # 用户不存在或者用户未绑定座位
#     else:
#         return -4 #不在时间范围内

