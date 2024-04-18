from models import User,Seat,Lib,Task
from utils.get_cookie import get_wx_cookie
from datetime import datetime,time
from settings import USER_SEAT_SIZE,USER_ADD_TASK_BEGIN,USER_ADD_TASK_END
from settings import QUEUE


#tools 获取用户
async def get_user(uuid):
    user = await User.get_or_none(uuid=uuid)
    if user:
        return user
    else:
        return None

#tools 获取用户座位
async def get_seat(lib_id,seat_name_id):
    lib = await  Lib.get_or_none(lib_id=lib_id) #更改为使用lib_id查找
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

#tools 校验座位信息并返回座位id列表（带有座位查重）
async def get_and_validate_seat_list(datalist,user:User):
    seat_list = []
    count = 1
    for data in datalist:
        seat = await get_seat(lib_id=data['lib_id'], seat_name_id=data['seat_name_id'])
        if not seat:
            return count
        if count == 1:
            users_on_seat = await User.filter(seats=seat)
            users_on_seat_id_list = []
            for i in users_on_seat:
                users_on_seat_id_list.append(i.id)
            if users_on_seat_id_list:
                if not user.id in users_on_seat_id_list:
                    return -count
        seat_list.append(seat)
        count += 1
    return seat_list

#func 同时更新一组座位
async def update_user_seat_list(user,datalist):
    seat_list = await get_and_validate_seat_list(datalist=datalist,user=user)
    if type(seat_list) == int:
        return seat_list #校验失败返回错误数据的位序
    await user.seats.clear()
    await user.seats.add(*seat_list)
    return 0

#func 删除座位
async def delete_seat_user_relation(user,seat_id):
    seat = await Seat.get_or_none(id=seat_id)
    if seat:
        await seat.user.remove(user)
        return 0 #删除成功
    else:
        return -2 #座位不存在

#func 获取所有座位
async def user_all_seat(user):
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
        if "Authorization" in cookie:
            return cookie
        else:
            return None
    except Exception :
        return None

#func 提交任务
# async def add_task_func(user,wx_url):
#     today = datetime.now()
#     print(today)
#     task = await Task.get_or_none(user=user)
#     have_task = False
#     if task:
#         have_task = True
#         store_time =  task.add_time.date()
#         if store_time == today.date():
#             return -4 #任务已提交
#     if user.balance <= 0:
#         return 0  # 用户余额不足
#     start_time = time(*USER_ADD_TASK_BEGIN)
#     end_time = time(*USER_ADD_TASK_END)
#     if not (start_time <= today.time() <= end_time):
#         return -1 #没到时间
#     user_seats = await user_all_seat(user)
#     if not user_seats:
#         return -2 #未绑定座位
#     wx_cookie = await get_wechat_cookie(url=wx_url)
#     if not wx_cookie:
#         return -3 #微信令牌失效
#     if have_task:
#         task.add_time = datetime.now()
#         task.status = 1
#         task.wx_cookie = wx_cookie
#         await task.save()
#     else:
#         await Task.create(add_time=today,wx_cookie=wx_cookie,user=user)
#     user.balance -= 1
#     await user.save()
#     return 1 #添加成功

#func-保存cookie
async def save_cookie(user,wx_url):
    if user.balance <= 0:
        return 0  # 用户余额不足
    user_seats = await user_all_seat(user)

    if not user_seats:
        return -1  # 未绑定座位

    wx_cookie = await get_wechat_cookie(url=wx_url)
    if not wx_cookie:
        return -2  # 微信令牌失效

    task = await Task.get_or_none(user=user)
    if task:
        if task.status == 1:
            return -3 #cookie仍有效不需要提交
        task.add_time = datetime.now()
        task.wx_cookie = wx_cookie
        task.status = 1 #更新cookie设置状态为1
        await task.save()
    else:
        today = datetime.now()
        await Task.create(add_time=today, wx_cookie=wx_cookie, user=user)
    # print("[测试-user-id]",user.id)
    await QUEUE.put(user.id)
    return 1 #添加成功




