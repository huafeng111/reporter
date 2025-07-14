#!/usr/bin/env python3
"""
金融新闻AI摘要报告器

从AI API获取金融新闻摘要并发送到Slack
"""

import os
import sys
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import Config
from src.reporter.ai_service import AIService
from src.reporter.slack_service import SlackService

class FinancialReporter:
    """金融新闻报告器主类"""
    
    def __init__(self):
        self.config = Config()
        self.ai_service = AIService(self.config)
        self.slack_service = SlackService(self.config)
    
    def run(self, custom_query: Optional[str] = None) -> bool:
        """
        运行报告器
        
        Args:
            custom_query: 自定义查询
            
        Returns:
            成功返回True，失败返回False
        """
        # 验证配置
        if not self.config.validate():
            return False
        
        print("开始执行金融新闻摘要任务...")
        
        # 获取AI摘要
        content = self.ai_service.get_financial_news_summary(custom_query)
        
        if content:
            # 发送到Slack
            success = self.slack_service.send_message(content)
            return success
        else:
            # 发送错误消息到Slack
            error_msg = "获取AI新闻摘要失败，请检查API配置和网络连接"
            self.slack_service.send_error_message(error_msg)
            return False

def main():
    """主函数"""
    reporter = FinancialReporter()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        print(f"使用自定义查询: {custom_query}")
        success = reporter.run(custom_query)
    else:
        success = reporter.run()
    
    if success:
        print("任务执行成功！")
        sys.exit(0)
    else:
        print("任务执行失败！")
        sys.exit(1)

if __name__ == "__main__":
    main() 