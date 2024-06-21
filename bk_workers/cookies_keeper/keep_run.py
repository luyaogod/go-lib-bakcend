import asyncio
from cookies_keeper.keep_consumer_func import keeper
from settings import QUEUE

async def consumer(queue,user_id):
    try:
        await keeper(user_id=user_id,queue=queue)
    except:
        queue.task_done()

async def main():
    while True:
        user_id =  await QUEUE.get()
        asyncio.create_task(consumer(QUEUE,user_id))

if __name__ == "__main__":
    asyncio.run(main())