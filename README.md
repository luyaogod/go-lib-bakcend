###fast-api server启动指令
```bash
docker compose up -d
docker exec -it bash backend
docker pyhton3 db_init.py
```
###抢座进程启动指令
```bash
docker build -t booker .

docker run -it --rm --name mybooker0 \
booker bash -c "python3 book_main.py 127.0.0.1 2 0"
```