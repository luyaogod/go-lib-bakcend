import sys
import asyncio

from morning_task.morning_run import main

asyncio.run(main(host=sys.argv[1]))