from fastapi import APIRouter,Depends
from api_funcs import admin_func
from utils.dependence import admin_auth_dependencie
import schemas
from utils.response import success_response,error_response

router = APIRouter()

@router.get('/admin_auth/{uuid}',summary='管理员验证')
async def create_user(user=Depends(admin_auth_dependencie)):
    if user:
        return success_response('验证成功')
    else:
        return error_response('非法管理员')

@router.post('/create_user/{uuid}',summary='用户创建')
async def create_user(data:schemas.CreateUserIn,user=Depends(admin_auth_dependencie)):
    await admin_func.create_user(data.username)
    return success_response('创建成功')

@router.get('/delete_user/{user_id}/{uuid}',summary='用户删除')
async def delete_user(user_id:int,user=Depends(admin_auth_dependencie)):
    result = await admin_func.delete_user(user_id=user_id)
    if result:
        return success_response(f'删除成功-{result}')
    else:
        return error_response('删除失败，用户不存在')

@router.get('/all_user/{uuid}',summary='用户列表')
async def all_user(user=Depends(admin_auth_dependencie)):
    result = await admin_func.get_all_user()
    return result
