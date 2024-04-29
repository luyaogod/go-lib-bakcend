### fast-api server启动指令
```bash
docker compose up -f docker-compose.server.yml -d

docker exec -it bash backend

docker pyhton3 db_init.py
```

### 通过shell脚本启动fast-api server
```bash
chmod +x start.sh
./start.sh
```

### 抢座进程启动指令
```bash
docker docker compose up -f docker-compose.booker.yml -d

DB_HOST=47.94.172.195 BOOKER1_ID=2 BOOKER1_ID=3 \
docker-compose up -f docker-compose.booker.yml -d
```