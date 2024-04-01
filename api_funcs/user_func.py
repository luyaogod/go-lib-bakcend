from models import User,Seat,Lib
from utils.get_cookie import get_wx_cookie
from utils.time_tools import get_set_time,time_validate
from my_celery import add_task
from datetime import datetime,timezone
from settings import USER_SEAT_SIZE


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
        if cookie and "Authorization" in cookie:
            return cookie
        else:
            return None
    except Exception as e:
        return None

#func 提交任务
async def add_task_func(user,wx_url):
    current_time = datetime.now()
    today = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    if user.task is None:
        pass
    elif user.task.date() == today.date():
        return -4 #重复提交任务
    if user.balance <= 0:
        return 0  # 用户余额不足
    current_utc_time = datetime.now(timezone.utc)
    result = time_validate(current_utc_time)
    if not result:
        return -1 #没到时间
    data = await user_all_seat(user)
    if not data:
        return -2 #未绑定座位
    data = await user_all_seats_clean(data)
    wx_cookie = await get_wechat_cookie(url=wx_url)
    if not wx_cookie:
        return -3 #微信令牌失效
    set_time = get_set_time(current_utc_time)
    data = add_task.apply_async(args=[wx_cookie, data], eta=set_time)
    # data = add_task.delay(wx_cookie, data) #test
    user.balance -= 1
    user.task = current_time
    await user.save()
    print('- 任务已添加:', data.id)
    return 1 #添加成功


