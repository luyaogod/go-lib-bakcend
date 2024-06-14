import uvicorn
import argparse
from book_task.book_sync import setup as book_setup

def setup_fastapi()->None:
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)

def setup():
    parser = argparse.ArgumentParser(description='Setup different applications based on command.')
    parser.add_argument('command', type=str, choices=['main', 'booker'], help='The command to execute.')
    parser.add_argument('--host', type=str, help='数据库地址.')
    parser.add_argument('--id', type=int, help='服务器编号.')
    parser.add_argument('--size', type=int, help='服务器总数.')
    args = parser.parse_args()

    if args.command == "main":
        setup_fastapi()
    elif args.command == "booker":
        if args.host is None :
            print('booker需要传入参数--host')
        if args.id is None:
            print('booker需要传入--id')
        if args.size is None:
            print('booker需要传入--size')
        else:
            book_setup(host=args.host, worker_id=args.id, worker_size=args.size)
if __name__ == '__main__':
    setup()

#   python3 setup.py main
#   python3 setup.py booker --host 8.130.141.190 --id 1 --size 2
#   python3 setup.py booker --host 8.130.141.190 --id 0 --size 2
