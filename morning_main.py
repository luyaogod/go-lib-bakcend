import sys
import asyncio

from morning_task.morning_run import main

print(sys.argv[1])
asyncio.run(main(host=sys.argv[1]))