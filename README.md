###fast-api server启动指令
```bash
docker compose up -d
docker exec -it bash backend
docker pyhton3 db_init.py
```
###抢座进程启动指令
```bash
docker build -t booker .

docker run -d --name mybooker0 --restart unless-stopped \
booker bash -c "python3 book_main.py 127.0.0.1 2 0"

docker run -d --name mybooker0 booker \
bash -c "python3 book_main.py 127.0.0.1 2 0"
```