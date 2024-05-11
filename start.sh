#!/bin/bash
echo "启动docker容器..."
docker compose -f docker-compose.server.yml up -d

echo "等待mysql可用..."
sleep 40

echo "执行数据库初始化..."
docker exec -it backend python3 db_init.py