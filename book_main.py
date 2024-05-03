import sys
import asyncio

from book_task.book_run import main

asyncio.run(main(host=sys.argv[1],worker_size=sys.argv[2],worker_id=sys.argv[3]))