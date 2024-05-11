import asyncio
from fastapi import FastAPI
from task_pool_worker.task_pool_run import daily_task_pull_main
from task_pool_worker.morning_task_clean import morning_pool_clean_main


def register_task_pool(app:FastAPI,logger)->None:
    @app.on_event("startup")
    async def task_pool_inject():
        asyncio.create_task(daily_task_pull_main(logger))

def register_morning_pool_clean(app:FastAPI,logger)->None:
    @app.on_event("startup")
    async def morning_pool_clean_inject():
        asyncio.create_task(morning_pool_clean_main(logger))