import time
import pymysql
import requests
import datetime
import websocket
from urllib.parse import unquote
from . import book_utils 
from utils.clock import clock_sync
from settings import mlog as log
import concurrent.futures
from concurrent.futures import wait, ALL_COMPLETED

PyMysql_DB_CONFIG = {
    'host':'8.130.141.190',
    'user':'root',
    'password':'maluyao123',
    'database':'go-lib-backend'
}

TIME_PULL_TASK = (19,59,30)
TIME_WS_CONNECT = (19,59,58)
TIME_WS_SEND = (20, 0, 0)
TIME_CANCEL_SEAT = (22,30,0)


class Booker:
    def __init__(
        self,
        user_id: int,
        wx_cookie: str,
        seats: list,
        ws_interval: float = 0.1,
        post_interval: int = 0.8,
        ws_size: int = 100,
        ws_send_time: tuple = TIME_WS_SEND
    ):
        log.debug(f'Booker-实例创建<{user_id}>')
        self._user_id = user_id
        self._ws_size = ws_size
        self._ws_send_time = ws_send_time
        self._ws_interval = ws_interval
        self._post_interval = post_interval
        self._seats = seats
        self._cookie = wx_cookie
        self._response_validate = {
            "ws_bad_cookie": r'{"ns":"prereserve\/queue","msg":1000}',
            "ws_have_booked": r"\u4f60\u5df2\u7ecf\u6210\u529f\u767b\u8bb0\u4e86\u660e\u5929\u7684",
            "ws_sucess_queue": r'{"ns":"prereserve\/queue","msg":"\u6392\u961f\u6210\u529f\uff01\u8bf7\u57282\u5206\u949f\u5185\u9009\u62e9\u5ea7\u4f4d\uff0c\u5426\u5219\u9700\u8981\u91cd\u65b0\u6392\u961f\u3002","code":0,"data":0}',
            "ws_queue_ing": r"prereserve/queue",
            "ws_bad_time": r'{"ns":"prereserve\/queue","msg":"\u4e0d\u5728\u9884\u7ea6\u65f6\u95f4\u5185,\u8bf7\u5728 20:00-23:59 \u6765\u9884\u7ea6","code":0,"data":0}',
        }
        self._ws_headers = book_utils.make_ws_headers(self._cookie)
        self._post_headers = book_utils.make_post_headers(self._cookie)

    def do_ws(self) -> bool:
        """
        ws连接\n
        return int '0, 1, 2'  0失败, 1成功, 2已选座位
        """
        ws_url = "wss://wechat.v2.traceint.com/ws?ns=prereserve/queue"
        ws = websocket.create_connection(ws_url, header=self._ws_headers)
        ws.send('{"ns":"prereserve/queue","msg":""}') #发送预请求
        try:
            ws.settimeout(1)  
            ws.recv()  # 尝试接收消息防止积压，如果1秒内没有消息到达，则抛出超时异常
        except websocket._exceptions.WebSocketTimeoutException:
            log.debug("ws-接收预请求超时")
        finally:
            ws.settimeout(None) 

        clock_sync(self._ws_send_time) 
        ws.send('{"ns":"prereserve/queue","msg":""}') #正点发送第一条ws
        log.debug("do_ws")
        count = 0
        while count <= self._ws_size:
            response = ws.recv()
            if count == 0:
                log.info(f'ws-名次：{unquote(response)}')
            log.debug(f"ws-debug-print-{unquote(response)}")

            if response == self._response_validate["ws_sucess_queue"]:
                log.info('ws-排队成功')
                ws.close()
                return 1
            elif response == self._response_validate['ws_bad_time']:
                log.info('ws-不在预约时间')
            elif self._response_validate['ws_have_booked'] in response:
                log.warning("ws-已预约座位")
                ws.close()
                return 2
            elif response == self._response_validate["ws_bad_cookie"]:
                log.warning("ws-失效cookie")
                ws.close()
                return 0
            elif self._response_validate["ws_queue_ing"] in response:
                log.debug("ws-正在排队")
            else:
                log.debug(f"ws-未捕获响应-{response}")
            count += 1
            time.sleep(self._ws_interval)
            ws.send('{"ns":"prereserve/queue","msg":""}')
        ws.close()
        log.warning('ws-排队超时')
        return 0
    
    def do_post(self) -> bool:
        """post请求"""
        for seat in self._seats:
            try:
                url = "https://wechat.v2.traceint.com/index.php/graphql/"
                requests.post(
                    url=url,
                    json=book_utils.make_json_for_lib(lib_id=seat['lib_id']),
                    headers=self._post_headers
                )
                response = requests.post(
                    url=url,
                    json=book_utils.make_json_for_seat(lib_id=seat['lib_id'], seat_key=seat['seat_key']),
                    headers=self._post_headers
                )
                
                # 检查响应状态码
                if response.status_code == 200:
                    # 尝试解析JSON之前，检查内容是否为空
                    if response.text:
                        if "error" not in response.text:
                            return True
                        else:
                            log.warning(f'post-选座失败<user{self._user_id}>{response.json()}')
                    else:
                        log.warning(f'post-返回为空<user{self._user_id}>')
                else:
                    log.warning(f'post-请求失败<user{self._user_id}> 状态码: {response.status_code}')
                time.sleep(self._post_interval)
            except Exception as e:
                log.warning(f"post-报错:{e}")
        return False

    def book_chain(self):
        """预约抢座动作链"""
        ws_ret = self.do_ws()
        if ws_ret == 0:
            # 排队失败
            return False
        elif ws_ret == 2:
            # 已预约座位
            return True
        else:
            # 排队成功
            post_ret = self.do_post()
            return post_ret


class DailyTasks():
    """每日任务"""
    def __init__(
        self,
        pull_task_time:tuple = TIME_PULL_TASK,  #提前30秒拉取任务
        ws_connect_time:tuple = TIME_WS_CONNECT, #提前两秒连接ws
        cancel_time:tuple = TIME_CANCEL_SEAT,
        db_config=PyMysql_DB_CONFIG
    ) -> None:
        self._pull_task_time=pull_task_time
        self._ws_connect_time=ws_connect_time
        self._cancel_time = cancel_time
        self.db_connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    #每日任务拉取和数据处理相关sql--------------------------------------------------------------------------

    def task_pull(self) -> list[int]:
        """拉取每日任务user_id"""
        with self.db_connection.cursor() as cursor:
            sql = """
            SELECT user_id FROM task
            WHERE status = 1 AND open = 1
            AND wx_cookie LIKE 'Authorization=%'
            AND user_id IN (SELECT id FROM user WHERE balance > 0);
            """
            cursor.execute(sql)
            data_list = cursor.fetchall()
            if data_list:
                return [data['user_id'] for data in data_list]
            else:
                return []
            
    def task_pull_user_id_and_wx_cookie(self):
        """
        拉取每日任务包含user_id和wx_cookie\n
        return [{'user_id':,'wx_cookie':}]
        """
        with self.db_connection.cursor() as cursor:
            sql = """
            SELECT user_id,wx_cookie FROM task
            WHERE status = 1 AND open = 1
            AND wx_cookie LIKE 'Authorization=%'
            AND user_id IN (SELECT id FROM user WHERE balance > 0);
            """
            cursor.execute(sql)
            data_list = cursor.fetchall()
            return data_list

    def get_users_seats(self, user_ids):
        """获取多个用户的座位表"""
        placeholders = ','.join(['%s'] * len(user_ids))  # 根据user_ids的数量创建占位符字符串
        with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"""
                SELECT su.user_id, s.seat_key, l.lib_id
                FROM seat s
                JOIN lib l ON s.lib_id = l.id
                JOIN seat_user su ON s.id = su.seat_id
                WHERE su.user_id IN ({placeholders})
            """, user_ids)  # 使用列表解包提供所有user_id作为参数
            return cursor.fetchall()

    def get_users_cookie(self, user_ids):
        """获取多个用户的cookie"""
        placeholders = ','.join(['%s'] * len(user_ids))  # 根据user_ids的数量创建占位符字符串
        with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"""
                SELECT su.user_id, s.seat_key, l.lib_id
                FROM seat s
                JOIN lib l ON s.lib_id = l.id
                JOIN seat_user su ON s.id = su.seat_id
                WHERE su.user_id IN ({placeholders})
            """, user_ids)  # 使用列表解包提供所有user_id作为参数
            return cursor.fetchall()

    def organize_seats_by_user_id(self, query_results):
        """封装user_id和seats"""
        organized_results = []
        user_seats_mapping = {}

        # 遍历原始查询结果
        for record in query_results:
            user_id = record['user_id']
            seat_info = {'seat_key': record['seat_key'], 'lib_id': record['lib_id']}

            # 如果user_id已经在我们的字典中，直接添加座位信息
            if user_id in user_seats_mapping:
                user_seats_mapping[user_id].append(seat_info)
            else:
                # 否则，初始化这个user_id的座位列表
                user_seats_mapping[user_id] = [seat_info]

        # 将字典转换成所需的列表格式
        for user_id, seats in user_seats_mapping.items():
            organized_results.append({'user_id': user_id, 'seats': seats})

        return organized_results
    
    def pull_task_do_chain(self):
        """
        拉取每日任务数据并封装\n
        return [{"user_id":, "seats":, "cookie": }]
        """
        # 拉取每日任务包含user_id和wx_cookie
        data_id_and_cookie = self.task_pull_user_id_and_wx_cookie()
        user_ids = [item['user_id'] for item in data_id_and_cookie]
        #将user_id映射到wx_cookie
        user_id_to_cookie = {item['user_id']: item['wx_cookie'] for item in data_id_and_cookie}
        # 获取多个用户的座位表
        user_seats_row = self.get_users_seats(user_ids)
        # 封装user_id和seats
        user_id_and_seats = self.organize_seats_by_user_id(user_seats_row)
        # 使用user_id_to_cookie字典来分配cookie给相应的用户
        for item in user_id_and_seats:
            user_id = item['user_id']
            item['wx_cookie'] = user_id_to_cookie.get(user_id)
        log.debug(user_id_and_seats)
        return user_id_and_seats
    
    #任务结果处理相关sql----------------------------------------------------------------------------------
    def query_usernames_by_userids(self, userids:list[int])->None:
        try:
            with self.db_connection.cursor() as cursor:
                sql = f"""SELECT username FROM user WHERE id IN {tuple(userids)};"""
                cursor.execute(sql)
                data_list = cursor.fetchall()
                log.info('今日任务-{}'.format([data['username'] for data in data_list]))
        except Exception as e:
            log.warning(f"username查询失败{e}")

    def bulk_reduce_balance(self, user_ids)->None:
        """批量用户余额-1，使用参数化查询防止SQL注入"""
        if not user_ids:  # 如果列表为空，直接返回
            return
        placeholders = ','.join(['%s'] * len(user_ids))
        query = f"UPDATE user SET balance = balance - 1 WHERE id IN ({placeholders})"
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, user_ids)
            self.db_connection.commit()

    def bulk_add_task_ret(self, user_ids, status)->None:
        """批量添加任务结果记录"""
        if not user_ids:  # 如果列表为空，直接返回
            return
        current_time = datetime.datetime.now().date()
        values = ', '.join([f"({user_id}, '{current_time}', {status})" for user_id in user_ids])
        query = f"INSERT INTO task_ret (user_id, time, status) VALUES {values}"
        with self.db_connection.cursor() as cursor:
            cursor.execute(query)
            self.db_connection.commit()

    #座位取消--------------------------------------------------------------------------

    def pull_cookies(self):
        """拉取cookie列表sql"""
        with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """SELECT wx_cookie FROM task WHERE wx_cookie LIKE 'Authorization=%';"""
                cursor.execute(sql)
                data_list = cursor.fetchall()
                return [data['wx_cookie'] for data in data_list]

    def cancel_seat(self, cookie:str)->None:
        """取消座位"""
        url = 'https://wechat.v2.traceint.com/index.php/graphql/'
        headers = book_utils.make_post_headers(cookie)
        
        payload1 = {"operationName": "index",
                "query": "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
                "variables": {"pos": "App-首页"}}
        rep = requests.post(url=url, headers=headers, json=payload1)
        rep_json = rep.json()
        stoken = rep_json['data']['userAuth']['reserve']['getSToken']
        log.debug("stoken-{}".format(stoken))
        payload2 = {"operationName": "reserveCancle",
                "query": "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: $sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
                "variables": {"sToken": stoken}}
        rep = requests.post(url=url, headers=headers, json=payload2)
        log.debug(rep.json())

    def cancel_seats(self):
        """拉取cookie列表取消全部座位"""
        cookies = self.pull_cookies()
        for cookie in cookies:
            try:
                self.cancel_seat(cookie)
            except Exception:
                pass
    
    #每日任务--------------------------------------------------------------------------

    def main_loop(self)->None:
        """批量抢座、座位取消主程序"""
        log.info("进程启动")
        log.info(f"HOST: {PyMysql_DB_CONFIG}")
        while True:
            # 数据库测试
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = 1")
                admin = cursor.fetchone()
                if admin:
                    log.info(f'数据库测试成功-{admin["username"]}')
                else:
                    raise ValueError("数据库初始化失败")
            
            # 拉取任务
            clock_sync(self._pull_task_time)
            data = self.pull_task_do_chain()
            ids = [item['user_id'] for item in data]
            self.query_usernames_by_userids(ids) #输出username
        
            #创建booker实例
            bookers = []
            for item in data:
                bookers.append(Booker(**item))
            
            success_user_ids = []
            failed_user_ids = []
            time_out_ids = []
            
            # 创建任务，任务执行至完成ws连接并发送预请求
            clock_sync(self._ws_connect_time) 
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                # 创建一个映射，将每个future与其对应的user_id关联起来
                futures = {executor.submit(booker.book_chain): booker._user_id for booker in bookers}
                # 设置任务超时时间为120秒
                done, not_done = wait(futures.keys(), timeout=120, return_when=ALL_COMPLETED)
                # 处理已完成的任务
                for future in done:
                    user_id = futures[future]
                    try:
                        result = future.result()
                        if result:
                            success_user_ids.append(user_id)
                        else:
                            failed_user_ids.append(user_id)
                    except Exception as e:
                        log.warning(f"task报错: {e} for user_id {user_id}")
                # 获取未完成任务的相关信息
                for future in not_done:
                    user_id = int(futures[future])
                    time_out_ids.append(user_id)
                    log.warning(f"取消超时任务-结果：{future.cancel()}")
                
                failed_user_ids.extend(time_out_ids)
            # 一次性减少成功用户的余额
            log.info(f"success:{success_user_ids}")
            log.info(f"fail:{failed_user_ids}")
            try:
                self.bulk_reduce_balance(success_user_ids)
            except Exception as e:
                log.warning(f"余额扣除sql程序报错:{e}")
            # 一次性插入成功和失败的任务记录
            try:
                self.bulk_add_task_ret(success_user_ids, 1)  # 1 表示成功
                self.bulk_add_task_ret(failed_user_ids, 0)  # 0 表示失败
            except Exception:
                log.warning(f"结果存储sql程序报错:{e}")
            
            # 清理座位
            clock_sync(self._cancel_time)
            log.info("正在执行座位清理...")
            self.cancel_seats()
            log.info("座位清理完成.")

            # time.sleep(3600) #仅测试

def setup(host:str):
    global PyMysql_DB_CONFIG
    PyMysql_DB_CONFIG[host]=host
    DT = DailyTasks()
    DT.main_loop()


