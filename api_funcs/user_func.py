from models import User,Seat,Lib,Task,Morning_Task_Pool,User_First_Seat
from utils.get_cookie import get_wx_cookie
from datetime import datetime
from settings import USER_SEAT_SIZE
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
    """
    校验座位信息并对第一个座位做查重

    :param datalist: 座位数据列表[ {lib_id:int, seat_name_id:int} ]
    :param user: 用户query对象
    :return: 返回seat对象数组[seat,seat]
    """
    #查询封装所用用户第一个座位列表
    all_user_first_seat = await User_First_Seat.all()
    # all_user_first_seat_id_list = []
    # for user_first_seat in all_user_first_seat:
    #     all_user_first_seat_id_list.append(user_first_seat.first_seat_id)

    validate_seat_list = []
    count = 1
    for data in datalist:
        seat = await get_seat(lib_id=data['lib_id'], seat_name_id=data['seat_name_id'])
        if not seat:
            return count #返回正位序表示座位不存在
        if count == 1:
            for data in all_user_first_seat:
                if seat.id == data.first_seat_id and user.id != data.user_id:
                    return -count  # 返回负位序表示座位被占

        validate_seat_list.append(seat)
        count += 1
    return validate_seat_list


#func 同时更新一组座位
async def update_user_seat_list(user,datalist):
    #更新用户座位列表
    seat_list = await get_and_validate_seat_list(datalist=datalist,user=user)
    if type(seat_list) == int:
        return seat_list #校验失败返回错误数据的位序
    await user.seats.clear()
    await user.seats.add(*seat_list)
    user_first_seat = await User_First_Seat.get_or_none(user_id=user.id)
    #更新用户第一个座位
    if user_first_seat == None:
        await User_First_Seat.create(user_id=user.id,first_seat_id=seat_list[0].id)
    else:
        user_first_seat.first_seat_id=seat_list[0].id
        await user_first_seat.save()
    return 0
#---------------------------------------------------------------------
async def get_and_validate_seat_list_morning(datalist,user:User):
    seat_list = []
    count = 1
    for data in datalist:
        seat = await get_seat(lib_id=data['lib_id'], seat_name_id=data['seat_name_id'])
        if not seat:
            return count
        #此处的座位重复校验已删除
        seat_list.append(seat)
        count += 1
    return seat_list


#func 更新morning座位
async def update_user_seat_list_morning(user,datalist):
    seat_list = await get_and_validate_seat_list_morning(datalist=datalist,user=user)
    if type(seat_list) == int:
        return seat_list #校验失败返回错误数据的位序
    await user.morning_seats.clear()
    await user.morning_seats.add(*seat_list)
    return 0
#--------------------------------------------------------------------

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
async def user_all_seats_clean(data,is_book=True):
    task_data_list = []
    for i in data:
        data_dict = {}
        data_dict["lib_id"] = str(i["seat_lib"]["lib_id"])
        seat_key =i["seat_data"]["seat_key"]
        if is_book:
            pass
        else:
            seat_key =seat_key.replace(".","")
        data_dict["seat_key"] = seat_key
        task_data_list.append(data_dict)
    return task_data_list

#func 获取所有早晨座位
async def user_all_morning_seat(user):
    data =  await user.morning_seats.all().prefetch_related('lib')
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
    await QUEUE.put(user.id)
    return 1 #添加成功

async def add_morning_task(user):
    if user.balance <= 0:
        return -1  # 用户余额不足
    user_seats = await user_all_morning_seat(user)
    if not user_seats:
        return -2  # 未绑定座位
    wx_cooke_data = await Task.get_or_none(user=user)
    if wx_cooke_data == None:
        return -3 # 没有令牌
    if (wx_cooke_data.status == 0):
        return -4 #令牌过期
    morning_task = await Morning_Task_Pool.get_or_none(user=user)
    if morning_task:
        return -5 #禁止重复提交
    await Morning_Task_Pool.create(user=user)
    return 0 #创建成功


