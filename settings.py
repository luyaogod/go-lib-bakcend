#DATABASES
TORTOISE_ORM = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.mysql',
                'credentials': {
                    'host': 'localhost',
                    # 'host': 'db',
                    'port': '3306',
                    'user': 'root',
                    'password': 'maluyao123',
                    'database': 'go-lib-backend',
                }
            },
        },
        'apps': {
            'models': {
                #aerich配置
                # 'models': ['models','aerich.models'],
                'models': ['models'],
                'default_connection': 'default',
            }
        }
    }

#跨域本地调试配置
ALLOWHOSTS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

#跨域服务器配置
# ALLOWHOSTS = [
#     "*"
# ]

BROKER_URL = 'redis://redis:6379/0' #存放结果
BACKEND_URL = 'redis://redis:6379/1' #消息中间件

USER_SEAT_SIZE = 6

ADMIN_NAME = 'mario'

ADMIN_UUID = '6f981e3e-73d4-4701-9296-28ffafc0e8eb'