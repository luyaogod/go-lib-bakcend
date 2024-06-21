import uvicorn
from workers import *
import argparse

def fastapi_up()->None:
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)

def setup():
    parser = argparse.ArgumentParser(description='Setup different applications based on command.')
    parser.add_argument('command', type=str, choices=['main', 'eve', 'morn', 'group'], help='可执行命令组.')
    parser.add_argument('--host', type=str, help='数据库端口.')
    parser.add_argument('--worker_size', type=int, help='eve的worker数量.')
    parser.add_argument('--worker_id', type=int, help='eve的worker-id.')

    args = parser.parse_args()

    if args.command == "main":
        fastapi_up()
    elif args.command == "eve":
        if args.host is None or args.worker_size is None or args.worker_id is None:
            print('需要参数 --host, --worker_size, --worker_id')
        else:
            eve_up(host=args.host, worker_size=args.worker_size, worker_id=args.worker_id)
    elif args.command == "morn":
        if args.host is None:
            print('需要参数 --host.')
        morn_up(host=args.host)
    elif args.command == "group":
        if args.host is None:
            print('需要参数 --host.')
        group_up(host=args.host)
  
if __name__ == '__main__':
    setup()

#   python3 setup.py main
#   python3 setup.py eve --host 8.130.141.190 --worker_size 1 --worker_id 0
#   python3 setup.py morn --host 8.130.141.190
#   python3 setup.py group --host 8.130.141.190