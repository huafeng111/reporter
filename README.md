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

复制 `.env.example` 为 `.env` 并填入实际的配置值：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key 和 Slack Webhook URL。

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

- `API_KEY`: AI API 密钥（必需）
- `SLACK_WEBHOOK_URL`: Slack Webhook URL（必需）
- `AI_URL`: AI API 端点（可选，默认：https://api.bochaai.com/v1/ai-search）
- `DEFAULT_QUERY`: 默认查询（可选，默认：总结昨天的美股金融财经新闻）
- `FRESHNESS`: 新闻时效性（可选，默认：oneDay）
- `COUNT`: 返回结果数量（可选，默认：50）
- `ANSWER`: 是否返回答案（可选，默认：True）
- `STREAM`: 是否流式响应（可选，默认：False）

## 功能特性

- 🔧 模块化设计，易于维护和扩展
- ⚙️ 环境变量配置，安全管理敏感信息
- 🚀 支持自定义查询
- 📊 完整的错误处理和日志输出
- 🔄 支持多种运行方式
- ⏰ 自动定时任务（每天北京时间上午10点）
- 🐳 支持 Docker 部署
- 🛠️ 一键自动部署脚本
- 📋 完整的部署和监控文档

## 🚀 快速部署到服务器

如果你想将此项目部署到服务器并设置定时任务，请查看：

- **[DEPLOY.md](./DEPLOY.md)** - 快速部署指南
- **[deploy/README.md](./deploy/README.md)** - 详细部署文档

### 一键部署命令：
```bash
sudo bash deploy/deploy.sh
```

部署后将自动：
- ✅ 每天北京时间上午10点发送金融新闻摘要
- ✅ 创建日志系统用于监控
- ✅ 设置专用用户和环境