#!/usr/bin/env python3
"""
Demo配置文件 - 请在这里设置你的API密钥
"""

# ================================
# API配置
# ================================

# DeepSeek API配置
# 请到 https://platform.deepseek.com/ 获取你的API密钥
DEEPSEEK_API_KEY = "sk-c60312b45d254ca1903bf9754babe453"  # 请替换为你的实际DeepSeek API KEY

# Slack Webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# ================================
# 网页爬取配置
# ================================

# 要爬取的金融新闻网站
NEWS_URLS = [
    "https://finance.yahoo.com/news/",
    "https://www.marketwatch.com/latest-news",
    "https://www.cnbc.com/finance/",
]

# 每个网站最大爬取文章数
MAX_ARTICLES_PER_SITE = 5

# 请求间隔（秒）
REQUEST_DELAY = 1

# ================================
# DeepSeek模型配置
# ================================

# 使用的模型名称
MODEL_NAME = "deepseek-chat"

# 生成参数
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# 系统提示词
SYSTEM_PROMPT = """你是一个专业的金融分析师。请分析以下金融新闻，提供简洁的市场洞察和趋势分析。用中文回答。"""

# 用户提示词模板
USER_PROMPT_TEMPLATE = """
请分析以下金融新闻标题，提供市场洞察：

{news_text}

请按以下格式总结：
1. 市场主要趋势
2. 重要事件影响
3. 投资关注点
4. 风险提示

请保持简洁明了，重点突出。
"""

# ================================
# 其他配置
# ================================

# 请求超时时间（秒）
REQUEST_TIMEOUT = 10

# 最大重试次数
MAX_RETRIES = 3

# User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" 