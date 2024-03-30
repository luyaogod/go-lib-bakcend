#DATABASES
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

BROKER_URL = 'redis://redis:6379/0' #存放结果
BACKEND_URL = 'redis://redis:6379/1' #消息中间件

USER_SEAT_SIZE = 4

ADMIN_NAME = 'mario'

ADMIN_UUID = '6f981e3e-73d4-4701-9296-28ffafc0e8eb'

#errors
#请线排队再选座
POST_ERROR_WS_TIME_OVER=r'{"errors":[{"msg":"\u8bf7\u5148\u6392\u961f\u518d\u9009\u5ea7","code":40006}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#座位已被抢
POST_ERROR_SEATS_GETED=r'{"ns":"prereserve\/queue","msg":"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684,\u90d1\u4e1c\u6821\u533a-2\u697c\u897f\u9605\u89c8\u533a 105\u53f7 \u5ea7\u4f4d","code":0,"data":0}'
#座位已被预约
POST_ERROR_SEATS_BOOKED=r'{"errors":[{"msg":"\u8be5\u5ea7\u4f4d\u5df2\u7ecf\u88ab\u9884\u7ea6,\u8bf7\u6362\u4e2a\u5ea7\u4f4d\u3002","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#场馆已满
POST_ERROR_LIB_IS_FULL=r'{"errors":[{"msg":"\u8be5\u573a\u9986\u4eca\u5929\u7684\u540d\u989d\u5df2\u6ee1,\u6362\u4e2a\u9986\u5ba4\u6216\u8005\u660e\u65e9\u8fdb\u884c\u9009\u5ea7","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#无效座位
POST_SEAT_UNDEFINED=r'{"errors":[{"msg":"\u8be5\u5ea7\u4f4d\u4e0d\u5b58\u5728","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#选座请求过于频繁
TRY_AGAIN_BUSY=r'{"errors":[{"msg":"\u8bf7\u91cd\u65b0\u5c1d\u8bd5","code":1}],"data":{"userAuth":{"prereserve":{"save":null}}}}'
#微信令牌失效
WS_WX_ERROR_COOKIE_OVER = r'{"ns":"prereserve\/queue","msg":1000}'
#排队成功
WS_SUCCESS_QUEUE = r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}'
#预约成功
WS_SUCCESS_BOOK = r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684"
#不在时间范围内
WS_ERROR_OUT_TIME_SIZE=r'{"ns":"prereserve\/queue","msg":"\u4e0d\u5728\u9884\u7ea6\u65f6\u95f4\u5185,\u8bf7\u5728 20:00-23:59 \u6765\u9884\u7ea6","code":0,"data":0}'