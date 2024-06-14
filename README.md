### 启动命令
```bash
#后端服务
docker compose -f docker-compose.server.yml up -d

#手动初始DB数据
docker exec -it backend bash
python3 db_init.py

#booker进程和pool进程
DB_HOST=8.130.141.190 WOKER_ID=1 WOKER_SIZE=2 docker compose -f docker-compose.booker.yml up -d
DB_HOST=8.130.141.190 WOKER_ID=0 WOKER_SIZE=2 docker compose -f docker-compose.booker.yml up -d
```