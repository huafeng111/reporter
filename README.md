# Financial Reporter

AI-powered financial news reporter that fetches summaries from AI API and sends them to Slack.

## 项目结构

```
reporter/
├── src/
│   └── reporter/
│       ├── agents/          # Agent系统
│       │   ├── base_agent.py      # 基础Agent类
│       │   └── financial_agent.py # 财经新闻Agent
│       ├── agent_factory.py       # Agent工厂
│       ├── task_scheduler.py      # 任务调度器
│       └── slack_service.py       # Slack 服务
├── config/
│   ├── config.py           # 基础配置管理
│   └── tasks.yaml          # 任务配置文件
├── scripts/
│   └── run_agents.py       # Agent系统运行脚本
├── deploy/                # 部署配置
│   ├── deploy.sh          # 自动部署脚本
│   ├── Dockerfile         # Docker 配置
│   ├── docker-compose.yml # Docker Compose 配置
│   ├── crontab           # 定时任务配置
│   ├── env.docker.template # Docker 环境变量模板
│   └── README.md         # 详细部署文档
├── .env.example          # 环境变量示例
├── pyproject.toml        # 项目配置
├── DEPLOY.md            # 快速部署指南
└── README.md
```

## 安装与设置

### 1. 安装 uv 包管理器

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 创建虚拟环境并安装依赖

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# 或在 Windows: .venv\Scripts\activate

uv sync
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下环境变量：

```bash
# BochaAI 搜索 API 配置
BOCHAAI_API_KEY=your_bochaai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

**完整配置示例：**
```bash
# BochaAI 搜索 API 配置
BOCHAAI_SEARCH_URL=https://api.bochaai.com/v1/web-search
BOCHAAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# DeepSeek 分析 API 配置  
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner

# Slack 配置
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
USE_SLACK_BLOCKS=True

# 搜索配置
DEFAULT_QUERY=总结昨天的美股金融财经新闻
FRESHNESS=day
COUNT=50
```

## 使用方法

### 新的Agent系统（推荐）

```bash
# 执行所有查询任务
python scripts/run_agents.py

# 执行特定查询
python scripts/run_agents.py --agent daily_news

# 查看所有可用的查询
python scripts/run_agents.py --list

# 验证配置
python scripts/run_agents.py --validate
```

### 传统单查询模式（已废弃）

新系统支持多个查询任务的并行执行，包括：
- 每日财经新闻摘要
- 美股宏观经济因素分析  
- 未来一周美股风险与机会分析

## 配置说明

项目支持以下环境变量配置：

**必需配置：**
- `BOCHAAI_API_KEY`: BochaAI 搜索 API 密钥
- `DEEPSEEK_API_KEY`: DeepSeek 分析 API 密钥  
- `SLACK_WEBHOOK_URL`: Slack Webhook URL

**可选配置：**
- `BOCHAAI_SEARCH_URL`: BochaAI 搜索端点（默认：https://api.bochaai.com/v1/web-search）
- `DEEPSEEK_BASE_URL`: DeepSeek API 端点（默认：https://api.deepseek.com）
- `DEEPSEEK_MODEL`: DeepSeek 模型名称（默认：deepseek-reasoner）
- `USE_SLACK_BLOCKS`: 是否使用 Slack Block Kit 格式（默认：True）
- `DEFAULT_QUERY`: 默认查询（默认：总结昨天的美股金融财经新闻）
- `FRESHNESS`: 搜索时效性（默认：day）
- `COUNT`: 返回结果数量（默认：50）

**向后兼容：**
- `API_KEY`: 等同于 `BOCHAAI_API_KEY`（为兼容旧版本）

## 功能特性

- 🤖 **Agent系统架构**：基于Agent的模块化设计，易于扩展
- 🔍 **智能搜索**：使用 BochaAI 进行实时网络搜索
- 🧠 **AI 分析**：使用 DeepSeek 模型进行深度分析  
- 📱 **智能通知**：支持 Slack Block Kit 和文本格式
- 🧹 **自动格式清理**：自动去除Markdown格式，优化Slack显示
- 📄 **统一配置管理**：通过YAML文件管理所有查询任务
- 🚀 **并行执行**：多个查询同时执行，提高效率
- 🎯 **多查询支持**：
  - 每日财经新闻摘要
  - 美股宏观经济因素分析
  - 未来一周美股风险与机会分析
- ⚙️ **环境变量配置**：安全管理敏感信息
- 📊 **完整的错误处理**：详细的日志输出
- 🔄 **多种运行方式**：手动、定时、Docker
- ⏰ **自动定时任务**：每天北京时间上午10点
- 🐳 **支持 Docker 部署**：容器化部署
- 🛠️ **一键自动部署脚本**：简化服务器部署

## 🚀 快速部署到服务器

如果你想将此项目部署到服务器并设置定时任务，请查看：

- **[DEPLOY.md](./DEPLOY.md)** - 快速部署指南
- **[deploy/README.md](./deploy/README.md)** - 详细部署文档
- **[MIGRATION.md](./MIGRATION.md)** - 旧版本升级指南

## 🔄 版本升级

如果你正在使用旧版本（单一 AI API），请参考：
- **[MIGRATION.md](./MIGRATION.md)** - 完整的升级指南，包含配置迁移和故障排查

### 一键部署命令：
```bash
sudo bash deploy/deploy.sh
```

部署后将自动：
- ✅ 每天北京时间上午10点发送金融新闻摘要
- ✅ 创建日志系统用于监控
- ✅ 设置专用用户和环境

## 🧪 部署后测试验证

部署完成后，请按照以下步骤验证系统是否正常工作：

### 1. 验证环境变量配置

```bash
# 测试环境变量是否正确加载
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f\"BOCHAAI_API_KEY: {os.getenv(\"BOCHAAI_API_KEY\", \"NOT_FOUND\")[:20]}...\")
print(f\"DEEPSEEK_API_KEY: {os.getenv(\"DEEPSEEK_API_KEY\", \"NOT_FOUND\")[:20]}...\")
url = os.getenv(\"SLACK_WEBHOOK_URL\", \"NOT_FOUND\")
print(f\"SLACK_WEBHOOK_URL: {url[:50]}...\")
print(f\"USE_SLACK_BLOCKS: {os.getenv(\"USE_SLACK_BLOCKS\", \"NOT_FOUND\")}\")
print(f\"Webhook URL长度: {len(url) if url != \"NOT_FOUND\" else 0}\")
"'
```

**预期输出示例：**
```
BOCHAAI_API_KEY: sk-xxxxxxxxxxxx...
DEEPSEEK_API_KEY: sk-xxxxxxxxxxxx...
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/T08DDTXBU06/B095H...
USE_SLACK_BLOCKS: False
Webhook URL长度: 81
```

### 2. 测试 Slack Webhook 连接

```bash
# 直接测试 Slack webhook（替换为你的实际 webhook URL）
curl --location 'YOUR_SLACK_WEBHOOK_URL' \
--header 'Content-type: application/json' \
--data '{"text":"🧪 部署测试 - Webhook连接正常"}'
```

**成功输出：** `ok`

### 3. 验证系统配置

```bash
# 验证配置文件和Agent设置
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py --validate'
```

**预期输出：**
```
✅ Configuration validation successful
✅ Environment variables loaded
✅ All 3 agents configured properly
✅ Slack webhook URL configured
```

### 4. 测试单个 Agent 运行

```bash
# 测试每日新闻Agent（最快的测试）
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py --agent daily_news'
```

**预期行为：**
- 显示搜索进度和结果
- 显示分析过程
- 发送消息到 Slack 频道
- 无 403 或其他错误

### 5. 测试完整系统运行

```bash
# 运行所有三个查询任务
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py'
```

**预期输出：**
```
🚀 Starting Financial Reporter Agent System...
📊 Found 3 configured agents

🤖 Running agent: daily_news
🔍 Searching with query: [查询内容]
📊 Search completed: 50 results found
🔄 Applying rerank filtering...
📊 After rerank filtering: X results remaining
🧠 Analyzing with DeepSeek...
📱 Sending to Slack...
✅ daily_news completed successfully

🤖 Running agent: macro_factors
[类似输出...]

🤖 Running agent: weekly_outlook  
[类似输出...]

🎉 All agents completed successfully!
```

### 6. 检查日志文件

```bash
# 查看系统日志
sudo tail -f /var/log/reporter/cron.log

# 查看最近的运行记录
sudo ls -la /var/log/reporter/
```

### 7. 验证定时任务设置

```bash
# 检查 crontab 是否正确设置
sudo crontab -u reporter -l
```

**预期输出：**
```
# Financial Reporter - Daily at 8:00 AM Beijing Time (00:00 UTC)
0 0 * * * cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py >> /var/log/reporter/cron.log 2>&1
```

### 8. 手动触发定时任务测试

```bash
# 手动执行定时任务命令测试
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py >> /var/log/reporter/cron.log 2>&1'

# 检查日志输出
sudo tail -20 /var/log/reporter/cron.log
```

## 🔧 常见问题排查

### Slack Webhook 403 错误
```bash
# 检查 webhook URL 是否完整正确
sudo cat /opt/reporter/.env | grep SLACK_WEBHOOK_URL

# 确保没有多余的空格或隐藏字符
sudo cat /opt/reporter/.env | hexdump -C | grep -A2 -B2 SLACK
```

### API 密钥问题
```bash
# 验证 API 密钥格式
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
bochaai_key = os.getenv(\"BOCHAAI_API_KEY\", \"\")
deepseek_key = os.getenv(\"DEEPSEEK_API_KEY\", \"\")
print(f\"BochaAI key format: {\"✅\" if bochaai_key.startswith(\"sk-\") else \"❌\"}\")
print(f\"DeepSeek key format: {\"✅\" if deepseek_key.startswith(\"sk-\") else \"❌\"}\")
"'
```

### 权限问题
```bash
# 检查文件权限
sudo ls -la /opt/reporter/
sudo ls -la /opt/reporter/.env
sudo ls -la /var/log/reporter/
```

### 手动修复配置
```bash
# 如果需要修改配置
sudo nano /opt/reporter/.env

# 修改后重新测试
sudo -u reporter bash -c 'cd /opt/reporter && source .venv/bin/activate && python scripts/run_agents.py --validate'
```

**测试完成标志：**
- ✅ 环境变量正确加载  
- ✅ Slack webhook 连接成功
- ✅ 所有 API 密钥有效
- ✅ Agent 运行无错误  
- ✅ Slack 收到测试消息
- ✅ 定时任务配置正确
- ✅ 日志文件正常生成