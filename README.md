### 启动命令
```bash
#后端服务
docker compose -f docker-compose.server.yml up -d

#手动初始DB数据
docker exec -it backend bash
python3 db_init.py

```