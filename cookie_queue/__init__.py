import asyncio
from fastapi import FastAPI
from cookie_queue.queue_test import main
from asyncio import Queue

def register_cookie_keeper(app:FastAPI,queue:Queue)->None:
    @app.on_event("startup")
    async def book_task_inject():
        asyncio.create_task(main(queue))