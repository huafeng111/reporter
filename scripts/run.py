#!/usr/bin/env python3
"""
运行脚本 - 加载环境变量并执行金融新闻报告器
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    # 加载.env文件
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("已加载 .env 文件")
    else:
        print("警告: .env 文件不存在，请根据 .env.example 创建")
except ImportError:
    print("警告: python-dotenv 未安装，将直接使用环境变量")

# 直接设置环境变量（如果.env不可用）
if not os.getenv('API_KEY'):
    os.environ['API_KEY'] = 'sk-5e0289f81a964b09bba95a06cff8f711'
    
if not os.getenv('SLACK_WEBHOOK_URL'):
    os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/services/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'

# 导入并运行主程序
from src.reporter.main import main

if __name__ == "__main__":
    main() 