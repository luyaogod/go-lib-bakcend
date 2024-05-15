import asyncio
import logging

#我的log
mlog = logging.getLogger('mlog')
mlog.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s')
handler.setFormatter(formatter)
mlog.addHandler(handler)

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

# TORTOISE_ORM = orm_conf("localhost") #test
TORTOISE_ORM = orm_conf("db")


#跨域服务器配置
ALLOWHOSTS = [
    "*"
]

USER_SEAT_SIZE = 6

ADMIN_NAME = 'mario'

ADMIN_UUID = '6f981e3e-73d4-4701-9296-28ffafc0e8eb'

#全局队列
QUEUE = asyncio.Queue()
