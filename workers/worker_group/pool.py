import aiomysql
from aiomysql import Pool,Cursor
from utils.clock import clock
from settings import mlog as log
from .settings import TIME_MORNING_CLEAN,TIME_EVE_PUSH,TIME_EVE_CLEAN

def db_config(host:str):
    return {
        "host":host,
        "port":3306,
        "user":"root",
        "password":"maluyao123",
        "db":"go-lib-backend"
    }

#早上任务  
#--------------------------------------------------------------------------------------
async def morning_clean(db: Pool)->None:
    """清理早晨任务池和早晨座位池"""
    async with db.acquire() as conn:
        cur:Cursor
        async with conn.cursor() as cur:
            sql_clean = """
DELETE FROM morning_seat_user;
DELETE FROM morning_task_pool;
"""
            await cur.execute(sql_clean)
            await conn.commit()

async def morning(db: Pool)->None:
    """早晨清理任务池"""
    log.info("早晨程序启动.")
    while True:
        await clock(TIME_MORNING_CLEAN)
        await morning_clean(db)
        log.info("早晨清理完成")

#晚上任务   
#--------------------------------------------------------------------------------------
async def eve_push(db: Pool)->None:
    """推送晚上任务"""
    async with db.acquire() as conn:
        cur: Cursor
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 查询用户ID和用户名
            sql_v_userid = """
SELECT id, username FROM user
WHERE id IN
(SELECT user_id FROM task
WHERE status = 1 AND open = 1
AND wx_cookie LIKE 'Authorization=%'
AND user_id IN (SELECT id FROM user WHERE balance > 0));
"""
            await cur.execute(sql_v_userid)
            data = await cur.fetchall()
            ids = [item['id'] for item in data]
            usernames = [item['username'] for item in data]
            log.info(f"今日任务 {usernames}")
            # 插入任务ID到task_pool表中
            if ids:
                values_str ='(' + ', '.join(['%s'] * len(ids)) + ')'
                sql_task_ids = f"SELECT id FROM task WHERE user_id in {values_str}"
                await cur.execute(sql_task_ids,ids)
                data = await cur.fetchall()
                task_ids = [item['id'] for item in data]

                values_str = ', '.join(['(%s)'] * len(task_ids))
                sql_insert = f"INSERT INTO task_pool (task_id) VALUES {values_str}"
                await cur.execute(sql_insert, task_ids)
                await conn.commit()

async def eve_clean(db: Pool)->None:
    """清理晚上任务池"""
    async with db.acquire() as conn:
        cur: Cursor
        async with conn.cursor(aiomysql.DictCursor) as cur:
            sql = """
DELETE FROM task_pool;
"""
            await cur.execute(sql)
            await conn.commit()

async def evening(db: Pool) -> None:
    """晚间任务"""
    log.info("晚间程序启动.")
    while True:
        await clock(TIME_EVE_PUSH)
        await eve_push(db)
        log.info("晚间推送完成")
        log.info("晚间清理待命")
        await clock(TIME_EVE_CLEAN)
        await eve_clean(db)
        log.info("晚间清理完成")


