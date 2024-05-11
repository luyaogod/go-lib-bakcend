import asyncio

#TORTOISE_ORM数据库配置
def orm_conf(host):
    conf = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.mysql',
                'credentials': {
                    'host': host,
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
    return conf

# TORTOISE_ORM = orm_conf("localhost")
TORTOISE_ORM = orm_conf("db")


#跨域服务器配置
ALLOWHOSTS = [
    "*"
]

USER_SEAT_SIZE = 6

ADMIN_NAME = 'mario'

ADMIN_UUID = '6f981e3e-73d4-4701-9296-28ffafc0e8eb'


#后台抢座任务时间控制
TIME_PUSH_TASK_IN_POOL = [19,59,0]
TIME_PULL_TASK_FROM_POOL = [19,59,10]
TIME_WS_CONNECT = [19,59,59]
TIME_BOOK_GO = [20,00,00]
TIME_CLEAR_POOL = [20,5,0]

#早晨抢座任务时间控制
TIME_PULL_MORNING_TASK_FROM_POOL=[6,29,50]
TIME_MORNING_BOOK_GO=[6,30,0]
TIME_CLEAR_MORNING_TASK_POOL = [6,35,0]

#全局队列
QUEUE = asyncio.Queue()
