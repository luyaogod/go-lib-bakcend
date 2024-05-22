import uvicorn
from book_task.book_run import Worker
from pool.pool_manager import PoolM
import argparse
from cancel.cance_run import setup_cancel

def setup_fastapi()->None:
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)

def setup_booker(host:str,worker_size:int,worker_id:int)->None:
    worker =  Worker(host=host,worker_size=worker_size,worker_id=worker_id)
    worker.setup()

def setup_task_pool_manager(host:str)->None:
    pool =  PoolM(host=host)
    pool.setup()

def setup():
    parser = argparse.ArgumentParser(description='Setup different applications based on command.')
    parser.add_argument('command', type=str, choices=['main', 'booker', 'pool', 'cancel'], help='The command to execute.')
    parser.add_argument('--host', type=str, help='The host for the booker command.')
    parser.add_argument('--worker_size', type=int, help='The worker size for the booker command.')
    parser.add_argument('--worker_id', type=int, help='The worker id for the booker command.')

    args = parser.parse_args()

    if args.command == "main":
        setup_fastapi()
    elif args.command == "booker":
        if args.host is None or args.worker_size is None or args.worker_id is None:
            print('The booker command requires --host, --worker_size, and --worker_id arguments.')
        else:
            setup_booker(host=args.host, worker_size=args.worker_size, worker_id=args.worker_id)
    elif args.command == "pool":
        if args.host is None:
            print('The pool command requires --host.')
        setup_task_pool_manager(host=args.host)
    elif args.command == "cancel":
        if args.host is None:
            print('The cancel command requires --host.')
        setup_cancel(host=args.host)


if __name__ == '__main__':
    setup()

#   python3 setup.py main
#   python3 setup.py booker --host 8.130.141.190 --worker_size 1 --worker_id 0
#   python3 setup.py pool --host 8.130.141.190
#   python3 setup.py cancel --host 8.130.141.190