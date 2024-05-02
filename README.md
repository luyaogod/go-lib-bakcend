### fast-api server启动指令
```bash
docker compose -f docker-compose.server.yml up -d

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
docker compose -f docker-compose.booker.yml up -d

DB_HOST= 47.94.172.195 \
docker compose -f docker-compose.morning.yml up -d
```