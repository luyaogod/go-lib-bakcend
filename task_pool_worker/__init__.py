import asyncio
from fastapi import FastAPI
from task_pool_worker.task_pool_run import main

def register_task_pool(app:FastAPI)->None:
    @app.on_event("startup")
    async def task_pool_inject():
        asyncio.create_task(main())