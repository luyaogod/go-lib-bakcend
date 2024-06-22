import aiomysql
from typing import Optional
from datetime import date

DB_CONF = {
    # "host": "8.130.141.190",
    "user": "root",
    "password": "maluyao123",
    "database": "go-lib-backend"
}

class Sql():
    """sql pool"""
    def __init__(self,host:str, pool: Optional[aiomysql.Pool] = None) -> None:
        self.pool = pool
        self.host = host

    async def _get_pool(self):
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                user=DB_CONF['user'],
                password=DB_CONF['password'],
                db=DB_CONF['database'],
                cursorclass=aiomysql.DictCursor,
                autocommit=True
            )
        return self.pool

    async def get_user_info(self, userid: int, time: int = 0):
        """参数0是晚间任务池 1是早上任务池"""
        user_data = {}
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = """
SELECT u.*, t.wx_cookie
FROM  user u
LEFT JOIN task t on u.id = t.user_id
WHERE u.id = %s;
                """
                await cursor.execute(sql, (userid,))
                data = await cursor.fetchone()
                user_data.update(data)

                sql_seats = f"""
SELECT su.user_id, s.seat_key, l.lib_id
FROM seat s
JOIN lib l ON s.lib_id = l.id
JOIN {'seat_user' if time == 0 else 'morning_seat_user'} su ON s.id = su.seat_id
WHERE su.user_id = %s
                """
                await cursor.execute(sql_seats, (userid,))
                datas = await cursor.fetchall()
                seats = [{"Key": data['seat_key'].rstrip('.') if time == 1 else data['seat_key'], "LibId": data['lib_id']} for data in datas]
                
                user_data.update({"seats": seats})
                
        return user_data

    async def pull_users_info(self, userids: list[int], time: int = 0):
        """
        拉取用户数据\n
        [
            {
                'id': 22, 
                'username': '客户18', 
                'uuid': 'str', 
                'balance': 9999, 
                'wx_cookie': 'str', 
                'seats': [{'Key': '29,12.', 'LibId': 11138},...]
            }, \n
            ...
        ]
        """
        datalist = []
        for user_id in userids:
            userinfo = await self.get_user_info(userid=user_id, time=time)
            datalist.append(userinfo)
        return datalist

    async def pull_eve_ids(self, worker_size:int, worker_id:int):
        """拉取晚上id"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = """
SELECT user_id FROM task WHERE id in (SELECT task_id From task_pool);
                """
                await cursor.execute(sql)
                datas = await cursor.fetchall()
                ids = [data['user_id'] for data in datas]
                #取余算法分配任务
                ass_ids = []
                for index, id in enumerate(ids):
                    if index % worker_size == worker_id:
                        ass_ids.append(id)
                return ass_ids

    async def reduce_b(self, user_id:int):
        """余额减-1"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "UPDATE user SET balance = balance - 1 WHERE id = %s;"
                await cursor.execute(sql, user_id)
                await conn.commit()

    async def update_ret(self, user_id:int ,ret:int):
        """ret 0成功 1失败"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "INSERT INTO task_ret (time, status, user_id) VALUES (%s, %s, %s)"
                time = str(date.today())
                await cursor.execute(sql, (time, ret, user_id))
                await conn.commit()

if __name__ == "__main__":
    import asyncio

    async def main():
        host = "8.130.141.190"
        sql = Sql(host)
        await sql._get_pool()
        print(await sql.get_user_info(userid=1))

    asyncio.run(main())