import asyncio
from datetime import datetime, timedelta

async def sleep_to(target_time,adjust=0):
    now = datetime.now()
    if now > target_time:
        target_time += timedelta(days=1)
    remaining =  (target_time - now).total_seconds()
    await asyncio.sleep(remaining+adjust)