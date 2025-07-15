# 🚀 快速部署指南

将金融新闻报告器部署到轻量级服务器，每天北京时间上午10点自动发送摘要。

## 📋 准备工作

1. **服务器要求**：
   - Ubuntu/Debian 系统
   - 至少 512MB 内存
   - 有 sudo 权限
   - 可访问互联网

2. **必需信息**：
   - BochaAI API Key（用于网络搜索）
   - DeepSeek API Key（用于AI分析）
   - Slack Webhook URL（用于消息通知）

## 🎯 一键部署（推荐）

### 步骤1：上传项目到服务器

```bash
# 方式1：使用 scp（如果在本地）
scp -r . user@your-server:/tmp/financial-reporter

# 方式2：直接在服务器上克隆
ssh user@your-server
git clone https://github.com/your-username/financial-reporter.git
cd financial-reporter
```

### 步骤2：运行自动部署脚本

```bash
sudo bash deploy/deploy.sh
```

**脚本会提示你输入：**
- BochaAI API Key: `sk-5e0289f81a964b09bba95a06cff8f711`
- DeepSeek API Key: `sk-your-deepseek-api-key`  
- Slack Webhook URL: `https://hooks.slack.com/services/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`

部署完成后会自动配置：
- ✅ 专用用户和环境
- ✅ 定时任务（每天北京时间10点）
- ✅ 日志系统
- ✅ 自动启动

## 🐳 Docker 部署（可选）

如果你的服务器支持 Docker：

```bash
# 1. 进入部署目录
cd deploy

# 2. 配置环境变量
cp env.docker.template .env
# 编辑 .env 文件，填入你的配置

# 3. 启动服务
docker-compose up -d
```

## 📊 验证部署

### 手动测试运行
```bash
sudo -u reporter bash -c 'cd /opt/financial-reporter && source .venv/bin/activate && python scripts/run.py'
```

### 查看定时任务
```bash
crontab -u reporter -l
```

### 查看日志
```bash
tail -f /var/log/financial-reporter/daily.log
```

## ⏰ 定时任务详情

- **执行时间**: 每天北京时间上午10:00
- **UTC 时间**: 每天 02:00 UTC
- **Cron 表达式**: `0 2 * * *`
- **日志位置**: `/var/log/financial-reporter/daily.log`

## 🔧 管理命令

```bash
# 查看服务状态
systemctl status cron

# 编辑定时任务
crontab -u reporter -e

# 查看执行日志
tail -f /var/log/financial-reporter/daily.log

# 重启 cron 服务
sudo systemctl restart cron
```

## 🆘 故障排查

### 1. 任务没有执行
```bash
# 检查 cron 服务状态
systemctl status cron

# 检查定时任务是否设置
crontab -u reporter -l

# 查看系统日志
grep cron /var/log/syslog
```

### 2. API 调用失败
```bash
# 测试 AI API
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.bochaai.com/v1/ai-search

# 测试 Slack Webhook
curl -X POST -H 'Content-type: application/json' --data '{"text":"测试"}' YOUR_WEBHOOK_URL
```

### 3. 权限问题
```bash
# 检查文件权限
ls -la /opt/financial-reporter/
ls -la /var/log/financial-reporter/

# 修复权限
sudo chown -R reporter:reporter /opt/financial-reporter
sudo chown -R reporter:reporter /var/log/financial-reporter
```

## 📈 监控建议

1. **设置告警**：如果任务失败，可以配置 Slack 通知
2. **日志轮转**：配置 logrotate 防止日志文件过大
3. **定期检查**：每周检查一次日志确保正常运行

## 🔄 更新部署

### 方式1：一键更新脚本（推荐）
```bash
# 在服务器上运行更新脚本
sudo bash deploy/update.sh
```

**更新脚本会自动：**
- ✅ 备份当前版本
- ✅ 拉取最新代码
- ✅ 更新依赖包
- ✅ 测试运行
- ✅ 失败时自动回滚

### 方式2：手动更新
```bash
# 1. 备份当前版本
sudo cp -r /opt/financial-reporter /opt/financial-reporter.backup

# 2. 拉取新代码
cd /opt/financial-reporter
sudo -u reporter git pull

# 3. 更新依赖
sudo -u reporter bash -c 'source .venv/bin/activate && uv sync'

# 4. 测试运行
sudo -u reporter bash -c 'source .venv/bin/activate && python scripts/run.py'
```

---

**🎉 部署完成后，你的金融新闻报告器将每天北京时间上午10点自动发送 AI 生成的美股金融新闻摘要到你的 Slack 频道！** 