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
        pool = await self._get_pool()
        user_data = {}
        async with pool.acquire() as conn:
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

    async def get_users_info(self, userids: list[int], time: int = 0):
        datalist = []
        for user_id in userids:
            userinfo = await self.get_user_info(userid=user_id, time=time)
            datalist.append(userinfo)
        return datalist

    async def pull_morning_ids(self):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "SELECT user_id From morning_task_pool;"
                await cursor.execute(sql)
                datas = await cursor.fetchall()
                return [data['user_id'] for data in datas]

    async def pull_evening_ids(self):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = """
SELECT user_id FROM task WHERE id in (SELECT task_id From task_pool);
                """
                await cursor.execute(sql)
                datas = await cursor.fetchall()
                return [data['user_id'] for data in datas]

    async def reduce_balance(self, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "UPDATE user SET balance = balance - 1 WHERE id = %s;"
                await cursor.execute(sql, (user_id,))
                await conn.commit()

    async def add_ret(self, user_id:int ,ret:int):
        """ret 0成功 1失败"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = "INSERT INTO morning_task_ret (time, status, user_id) VALUES (%s, %s, %s)"
                time = str(date.today())
                await cursor.execute(sql, (time, ret, user_id))
                await conn.commit()

if __name__ == "__main__":
    import asyncio

    async def main():
        pool = await aiomysql.create_pool(host=DB_CONF['host'], user=DB_CONF['user'], password=DB_CONF['password'], db=DB_CONF['database'], cursorclass=aiomysql.DictCursor)
        sql = Sql(pool)
        await sql.user_reduce_balance(1)
        await pool.close()

    asyncio.run(main())