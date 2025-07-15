# Financial Reporter

AI-powered financial news reporter that fetches summaries from AI API and sends them to Slack.

## 项目结构

```
reporter/
├── src/
│   └── reporter/
│       ├── main.py          # 主程序
│       ├── ai_service.py    # AI API 服务
│       └── slack_service.py # Slack 服务
├── config/
│   └── config.py           # 配置管理
├── scripts/
│   └── run.py             # 运行脚本
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

### 方式1: 使用运行脚本（推荐）

```bash
python scripts/run.py
```

### 方式2: 直接运行主程序

```bash
python src/reporter/main.py
```

### 自定义查询

你可以传入自定义查询参数：

```bash
python scripts/run.py "总结今天的科技股新闻"
```

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

- 🔍 **智能搜索**：使用 BochaAI 进行实时网络搜索
- 🧠 **AI 分析**：使用 DeepSeek 模型进行深度分析  
- 📱 **智能通知**：支持 Slack Block Kit 和文本格式
- 🔧 **模块化设计**：易于维护和扩展
- ⚙️ **环境变量配置**：安全管理敏感信息
- 🚀 **支持自定义查询**：灵活的搜索参数
- 📊 **完整的错误处理**：详细的日志输出
- 🔄 **多种运行方式**：手动、定时、Docker
- ⏰ **自动定时任务**：每天北京时间上午10点
- 🐳 **支持 Docker 部署**：容器化部署
- 🛠️ **一键自动部署脚本**：简化服务器部署
- 📋 **完整的部署和监控文档**：详细的使用指南

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