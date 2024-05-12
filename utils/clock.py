import asyncio
from datetime import datetime, timedelta
from typing import Tuple

async def sleep_to(target_time,adjust=0):
    now = datetime.now()
    if now > target_time:
        target_time += timedelta(days=1)
    remaining =  (target_time - now).total_seconds()
    await asyncio.sleep(remaining+adjust)

async def clock(target:Tuple[int]):
    now = datetime.now()
    run_time = datetime(now.year, now.month, now.day, *target)
    await sleep_to(run_time)