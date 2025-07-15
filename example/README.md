# 示例：BochaAI + DeepSeek 智能分析

这个示例展示了如何结合 BochaAI 搜索和 DeepSeek 模型进行智能信息分析。

## 📁 文件说明

- **`demo_simple.py`**: 主程序 - BochaAI搜索 + DeepSeek分析 + Slack通知
- **`demo_config.py`**: 配置文件 - API密钥和参数设置

## 🚀 功能特性

- **搜索引擎**: 使用 BochaAI 进行实时网络搜索
- **AI 分析**: 使用 DeepSeek Chat 模型进行深度分析
- **自动通知**: 分析结果自动发送到 Slack 频道
- **格式优化**: AI 直接生成 Slack 兼容的纯文本格式
- **灵活配置**: 支持自定义搜索查询和分析提示
- **多种显示**: 支持 Block Kit 和简单文本两种 Slack 显示格式

## 📋 快速开始

### 1. 配置 API 密钥

编辑 `demo_config.py` 文件：

```python
# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-your-deepseek-api-key"  # 替换为你的DeepSeek API Key

# BochaAI API配置  
BOCHAAI_API_KEY = "sk-your-bochaai-api-key"   # 替换为你的BochaAI API Key

# Slack配置
SLACK_WEBHOOK_URL = "your-slack-webhook-url"   # 替换为你的Slack Webhook URL
```

### 2. 安装依赖

```bash
# 进入项目根目录
cd ..

# 安装依赖
pip install requests openai

# 或使用 uv
uv add requests openai
```

### 3. 运行示例

```bash
# 进入example目录
cd example

# 运行默认查询
python demo_simple.py
```

## 🔧 自定义使用

### 修改查询内容

编辑 `demo_simple.py` 中的查询列表：

```python
queries = [
    "阿里巴巴2024年的esg报告",
    "美股最新市场动态", 
    "人工智能行业发展趋势",
    "你的自定义查询",  # 添加新查询
]
```

### 使用自定义函数

```python
from demo_simple import run_custom_query

# 运行自定义查询
run_custom_query(
    query="特斯拉最新财报分析",
    freshness="week",
    count=30,
    custom_prompt="请从投资角度分析以下信息..."
)
```

## 📊 工作流程

```
1. BochaAI搜索 🔍
   ↓
2. 提取搜索结果摘要 📝  
   ↓
3. DeepSeek Chat 分析 🧠
   ↓
4. 格式化报告 📋
   ↓
5. 发送到Slack 📱
```

## ⚙️ 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `freshness` | 搜索时间范围 | `"day"` |
| `count` | 搜索结果数量 | `50` |
| `model` | DeepSeek模型 | `"deepseek-chat"` |
| `USE_SLACK_BLOCKS` | Slack显示格式 | `True` |

可选的 `freshness` 值：
- `"day"`: 最近一天
- `"week"`: 最近一周  
- `"month"`: 最近一月
- `"year"`: 最近一年

### Slack 格式配置

```python
# 在 demo_simple.py 中设置
USE_SLACK_BLOCKS = True   # 使用 Block Kit 格式（推荐）
USE_SLACK_BLOCKS = False  # 使用简单文本格式
```

**Block Kit 格式优势：**
- 更美观的卡片式布局
- 更好的信息层次结构
- 支持分割线和字段对齐

**简单文本格式优势：**
- 兼容性更好
- 适用于较旧的 Slack 版本
- 更简洁的显示方式

### 格式优化

AI 会直接生成适合 Slack 显示的纯文本格式，避免使用 Markdown 语法，确保在 Slack 中完美显示。

## 📝 API 获取指南

### DeepSeek API Key
1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册并登录账户
3. 创建 API Key
4. 复制密钥（格式：`sk-xxxxxxxxxxxxxxxx`）

### BochaAI API Key  
1. 访问 [BochaAI 平台](https://api.bochaai.com/)
2. 注册账户并获取 API 访问权限
3. 获取 API Key

### Slack Webhook URL
1. 在 Slack 中创建新的 App
2. 启用 Incoming Webhooks 功能
3. 选择发送频道并获取 Webhook URL

## 🚨 注意事项

1. **API 费用**: DeepSeek 和 BochaAI 可能产生使用费用
2. **请求限制**: 注意 API 的请求频率限制
3. **数据隐私**: 确保不在查询中包含敏感信息
4. **网络环境**: 确保能正常访问相关 API 服务

## 🔍 故障排查

### 常见错误

1. **API Key 无效**
   ```
   解决：检查 demo_config.py 中的 API Key 配置
   ```

2. **网络连接失败**
   ```
   解决：检查网络连接和防火墙设置
   ```

3. **模型调用失败**
   ```
   解决：确认 DeepSeek 账户有足够余额
   ```

### 调试模式

在 `demo_simple.py` 开头添加：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 扩展建议

1. **多模型支持**: 添加其他 AI 模型的支持
2. **结果存储**: 将分析结果保存到数据库
3. **定时任务**: 设置定时执行分析任务
4. **Web 界面**: 开发简单的 Web 管理界面
5. **多渠道通知**: 支持邮件、企业微信等通知方式

---

**🎉 开始你的智能分析之旅！** 