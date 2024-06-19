import pymysql
from pymysql.connections import Connection

DB_CONF = {
            "host":"8.130.141.190",
            "user":"root",
            "password":"maluyao123",
            "database":"go-lib-backend"
        }

class Sql():
    """
    注意实例连接可能会过期，一次性查询使用\n
    
    """
    def __init__(self) -> None:
        self._cnn:Connection = pymysql.connect(
            host=DB_CONF['host'],
            user=DB_CONF['user'],
            password=DB_CONF['password'],
            database=DB_CONF['database'],
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_user_info(self, userid:int, time:int=0):
        """
        time :0获取晚上任务座位表, 1获取早上任务座位表\n
        获取用户完整数据，包含座位以及cookie\n
        {
            "id": 1,
            "username": "mario",
            "uuid": "6f981e3e-73d4-4701-9296-28ffafc0e8eb",
            "balance": 9967,
            "wx_cookie": "Authorization=",
            "seats": [
                {
                    "Key": "10,14",
                    "LibId": 10072
                },\n
                ...
            ]
        }
        """
        user_data = {}
        with self._cnn.cursor() as cursor:
            sql = """
SELECT u.*, t.wx_cookie
FROM  user u
LEFT JOIN task t on u.id = t.user_id
WHERE u.id = %s;
            """
            cursor.execute(sql, userid)
            datas = cursor.fetchone()
            user_data.update(datas)
            if time == 0:
                sql_seats = f"""
SELECT su.user_id, s.seat_key, l.lib_id
FROM seat s
JOIN lib l ON s.lib_id = l.id
JOIN seat_user su ON s.id = su.seat_id
WHERE su.user_id = %s
                """
                cursor.execute(sql_seats, userid)
                datas = cursor.fetchall()
            else:
                sql_seats = f"""
SELECT su.user_id, s.seat_key, l.lib_id
FROM seat s
JOIN lib l ON s.lib_id = l.id
JOIN morning_seat_user su ON s.id = su.seat_id
WHERE su.user_id = %s
                """
                cursor.execute(sql_seats, userid)
                datas = cursor.fetchall()
            seats = []
            
            
            for data in datas:
                row_seat_key:str = data['seat_key']
                #早上任务参数总Key不带"."需要剔除
                if time == 1:
                    seat_key = row_seat_key.rstrip('.')
                else:
                    seat_key = row_seat_key
                seats.append({"Key":seat_key, "LibId":data['lib_id']})
            user_seats = {"seats":seats}
            user_data.update(user_seats)
            return user_data
    
    def get_users_info(self, userids:list[int], time:int=0):
        """
        time :0获取晚上任务座位表, 1获取早上任务座位表\n
        根据id获取一组用户的全部数据\n
        [
            {
                "id": 1,
                "username": "mario",
                "uuid": "6f981e3e-73d4-4701-9296-28ffafc0e8eb",
                "balance": 9967,
                "wx_cookie": "Authorization=",
                "seats": [
                    {
                        "Key": "10,14",
                        "LibId": 10072
                    },\n
                    ...
                ]
            },\n
            ....
        ]
        """
        datalist = []
        for id in userids:
            userinfo = self.get_user_info(userid=id, time=time)
            datalist.append(userinfo)
        return datalist

    def pull_morning_ids(self):
        """获取早上任务池的全部id"""
        with self._cnn.cursor() as cursor:
            sql = """
SELECT user_id From morning_task_pool;
"""         
            cursor.execute(sql)
            datas = cursor.fetchall()
            return [data['user_id'] for data in datas]
    
    def pull_evening_ids(self):
        """获取晚上任务池的全部id"""
        with self._cnn.cursor() as cursor:
            sql = """
SELECT user_id FROM task WHERE id in (SELECT task_id From task_pool);
"""         
            cursor.execute(sql)
            datas = cursor.fetchall()
            print(datas)
            return [data['user_id'] for data in datas]
        

    
if __name__ == "__main__":
    sql = Sql()
    data = sql.pull_morning_ids()
    print(data)