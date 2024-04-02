import asyncio
from fastapi import FastAPI
from book_task.book_run import main

def register_book_task(app:FastAPI)->None:
    @app.on_event("startup")
    async def book_task_inject():
        asyncio.create_task(main())

