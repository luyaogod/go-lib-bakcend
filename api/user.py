from fastapi import APIRouter,Depends
from utils.dependence import user_auth_dependencie
from api_funcs import user_func
from utils.response import success_response,error_response
import schemas

router = APIRouter()

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
    else:
        return error_response('出错了！请稍后再试！')

