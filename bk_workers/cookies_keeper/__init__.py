import asyncio
from fastapi import FastAPI
from cookies_keeper.keep_run import main

def register_cookie_keeper(app:FastAPI)->None:
    @app.on_event("startup")
    async def cookie_keeper_inject():
        asyncio.create_task(main())