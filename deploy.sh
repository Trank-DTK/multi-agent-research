# deploy.sh - 生产环境部署脚本

set -e

echo "开始部署..."

# 拉取最新代码
git pull origin main

# 构建前端
cd frontend
npm install
npm run build
cd ..

# 停止旧容器
docker-compose -f docker-compose.prod.yml down

# 构建并启动新容器
docker-compose -f docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 收集静态文件
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "部署完成！"