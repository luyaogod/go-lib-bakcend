import sys
from book_task.book_run import Worker

if __name__ == "__main__":
    worker =  Worker(host=sys.argv[1],worker_size=int(sys.argv[2]),worker_id=int(sys.argv[3]))
    worker.setup()

#python3 book_main.py 8.130.141.190 1 0
