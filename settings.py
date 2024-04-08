#TORTOISE_ORM数据库配置
TORTOISE_ORM = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.mysql',
                'credentials': {
                    # 'host': 'localhost',
                    'host': 'db',
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
# ALLOWHOSTS = [
#     "http://127.0.0.1",
#     "http://localhost",
#     "http://localhost:8000",
#     "http://localhost:5173",
# ]

#跨域服务器配置
ALLOWHOSTS = [
    "*"
]

USER_SEAT_SIZE = 6

ADMIN_NAME = 'mario'

ADMIN_UUID = '6f981e3e-73d4-4701-9296-28ffafc0e8eb'

#任务提交接口时间限制
USER_ADD_TASK_BEGIN = [18,20,0]
USER_ADD_TASK_END = [19,55,0]

#后台抢座任务时间控制
BOOK_TASK_PULL = [10,57,0]
BOOK_TASK_CONNECT = [10,59,55]
BOOK_TASK_RUN = [11,0,0]

