import asyncio
from datetime import datetime, timedelta
from typing import Tuple
import time

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

def sleep_to_sync(target_time, adjust=0):
    now = datetime.now()
    if now > target_time:
        target_time += timedelta(days=1)
    remaining = (target_time - now).total_seconds()
    time.sleep(remaining + adjust)

def clock_sync(target:Tuple[int]):
    now = datetime.now()
    run_time = datetime(now.year, now.month, now.day, *target)
    sleep_to_sync(run_time)