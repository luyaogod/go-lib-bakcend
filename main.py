import uvicorn
from fastapi import FastAPI,HTTPException
from fastapi.exceptions import RequestValidationError
from settings import TORTOISE_ORM,ALLOWHOSTS
from tortoise.contrib.fastapi import register_tortoise
from api import user,admin
from tortoise.exceptions import OperationalError, DoesNotExist, IntegrityError, ValidationError
from utils import exception
from fastapi.middleware.cors import CORSMiddleware
from bk_workers.cookies_keeper import register_cookie_keeper


app = FastAPI()


#路由
app.include_router(user.router, prefix='/user', tags=['用户API'])
app.include_router(admin.router, prefix='/admin', tags=['管理API'])


#异常捕获
app.add_exception_handler(HTTPException, exception.http_error_handler)
app.add_exception_handler(RequestValidationError, exception.http422_error_handler)
app.add_exception_handler(exception.UnicornException, exception.unicorn_exception_handler)
app.add_exception_handler(DoesNotExist, exception.mysql_does_not_exist)
app.add_exception_handler(IntegrityError, exception.mysql_integrity_error)
app.add_exception_handler(ValidationError, exception.mysql_validation_error)
app.add_exception_handler(OperationalError, exception.mysql_operational_error)


#注册数据库
register_tortoise(app=app,config=TORTOISE_ORM)


#注册cookie保活程序
register_cookie_keeper(app=app)


#跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWHOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    # uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, workers=1)
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)



