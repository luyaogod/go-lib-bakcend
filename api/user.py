from fastapi import APIRouter,Depends
from utils.dependence import user_auth_dependencie
from api_funcs import user_func
from utils.response import success_response,error_response
import schemas
# from typing import List

router = APIRouter()

@router.get('/get_user/{uuid}',summary='用户校验')
async def get_user(user=Depends(user_auth_dependencie)):
    if user:
        return success_response(dict(user))
    else:
        return error_response('用户不存在')

@router.get('/ge_all_lib/{uuid}',summary='获取座位列表')
async def ge_all_lib(user=Depends(user_auth_dependencie)):
    result =  await user_func.user_all_seat(user)
    if result:
        return success_response(result)
    else:
        return error_response("请绑定座位")

@router.post('/create_seat/{uuid}',summary='创建常用座位')
async def create_role_permission(data:schemas.CreateSeatIn,user=Depends(user_auth_dependencie)):
    result =  await user_func.add_seat_user_relation(user=user,lib_id=data.lib_id,seat_name_id=data.seat_name_id)
    if result == 0:
        return success_response('添加成功')
    if result == -2:
        return error_response('您的座位已达上限')
    if result == -3:
        return error_response('座位不存在！')
    else:
        return error_response('未知错误！')

@router.get('/delete_seat/{seat_id}/{uuid}',summary='删除常用座位')
async def delete_seat(seat_id:int,user=Depends(user_auth_dependencie)):
    result = await user_func.delete_seat_user_relation(user,seat_id)
    if result == 0:
        return success_response('删除成功')
    if result == -2:
        return error_response('删除失败，座位不存在！')
    else:
        return error_response('出错了！请稍后再试！')

@router.post('/add_task/{uuid}',summary='增加任务')
async def create_role_permission(data:schemas.CreateTaskIn,user=Depends(user_auth_dependencie)):
    wx_url = data.wx_url
    result = await user_func.add_task_func(user,wx_url=wx_url)
    if result == 0:
        return success_response('任务添加成功')
    if result == -1:
        return error_response('请先绑定座位')
    if result == -3:
        return error_response('微信身份链接已失效，请重新获取！')
    if result == -2:
        return error_response('出错了！请稍后再试')
    if result == -4:
        return error_response('不在提交时间范围内！')
    else:
        return error_response('出错了！请稍后再试！')

@router.post('/update_seat_list/{uuid}',summary='更新座位列表')
async def update_seat_list(data:schemas.SeatsListIn,user=Depends(user_auth_dependencie)):
    data_list = data.model_dump()['seats']
    data =  await user_func.update_user_seat_list(user,data_list)
    if data == 0:
        return success_response('保存成功')
    else:
        return error_response(f'第{data}个座位不存在！')