# 部署指南

本目录包含了在服务器上部署金融新闻报告器的配置文件和脚本。

## 部署方式

### 方式1: 直接部署到服务器（推荐）

适用于 Ubuntu/Debian 系统的自动化部署脚本。

```bash
# 1. 上传项目到服务器
scp -r . user@your-server:/tmp/financial-reporter

# 2. 登录服务器并运行部署脚本
ssh user@your-server
cd /tmp/financial-reporter
sudo bash deploy/deploy.sh
```

**部署脚本会自动完成：**
- 安装系统依赖（Python, uv, cron 等）
- 创建专用用户 `reporter`
- 设置项目环境和依赖
- 配置定时任务（每天北京时间上午10点）
- 创建日志系统

### 方式2: Docker 部署

适用于支持 Docker 的任何系统。

```bash
# 1. 进入部署目录
cd deploy

# 2. 复制环境变量文件并配置
cp .env.docker .env
# 编辑 .env 文件，填入你的 API Key 和 Slack Webhook URL

# 3. 启动容器
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

## 定时任务说明

- **执行时间**: 每天北京时间上午10点
- **UTC 时间**: 每天 02:00 UTC（北京时间 = UTC+8）
- **Cron 表达式**: `0 2 * * *`

## 日志管理

### 直接部署方式
```bash
# 查看实时日志
tail -f /var/log/financial-reporter/daily.log

# 查看历史日志
cat /var/log/financial-reporter/daily.log
```

### Docker 部署方式
```bash
# 查看容器日志
docker-compose logs financial-reporter

# 查看日志文件
cat ./logs/daily.log
```

## 管理命令

### 直接部署方式

```bash
# 查看定时任务
crontab -u reporter -l

# 手动执行任务
sudo -u reporter bash -c 'cd /opt/financial-reporter && source .venv/bin/activate && python scripts/run.py'

# 编辑定时任务
crontab -u reporter -e

# 重启 cron 服务
sudo systemctl restart cron
```

### Docker 部署方式

```bash
# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新并重启
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 手动执行任务
docker-compose exec financial-reporter /app/.venv/bin/python /app/scripts/run.py
```

## 故障排查

### 1. 检查定时任务是否运行
```bash
# 直接部署
grep "financial-reporter" /var/log/syslog

# Docker 部署
docker-compose logs | grep -i error
```

### 2. 检查网络连接
```bash
# 测试 AI API 连接
curl -H "Authorization: Bearer your_api_key" https://api.bochaai.com/v1/ai-search

# 测试 Slack Webhook
curl -X POST -H 'Content-type: application/json' --data '{"text":"测试消息"}' your_slack_webhook_url
```

### 3. 手动测试
```bash
# 直接部署
sudo -u reporter bash -c 'cd /opt/financial-reporter && source .venv/bin/activate && python scripts/run.py'

# Docker 部署
docker-compose exec financial-reporter /app/.venv/bin/python /app/scripts/run.py
```

## 安全注意事项

1. **环境变量保护**: 确保 `.env` 文件权限设置为 600
2. **防火墙配置**: 如果需要，配置防火墙规则
3. **定期更新**: 定期更新系统和依赖包
4. **日志轮转**: 配置日志轮转避免磁盘空间不足

## 升级部署

### 直接部署方式
```bash
# 1. 备份当前版本
sudo cp -r /opt/financial-reporter /opt/financial-reporter.backup

# 2. 上传新版本并重新部署
# ... 按照部署步骤操作
```

### Docker 部署方式
```bash
# 1. 拉取新版本
git pull

# 2. 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
``` 