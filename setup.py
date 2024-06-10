import uvicorn
import argparse
from book_task.book_sync import setup as book_setup

def setup_fastapi()->None:
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)

def setup():
    parser = argparse.ArgumentParser(description='Setup different applications based on command.')
    parser.add_argument('command', type=str, choices=['main', 'booker'], help='The command to execute.')
    parser.add_argument('--host', type=str, help='The host for the booker command.')
    args = parser.parse_args()

    if args.command == "main":
        setup_fastapi()
    elif args.command == "booker":
        if args.host is None :
            print('The booker command requires --host')
        else:
            book_setup(host=args.host)
if __name__ == '__main__':
    setup()

#   python3 setup.py main
#   python3 setup.py booker --host 8.130.141.190
