import os
from typing import Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        # AI API 配置
        self.ai_url: str = os.getenv('AI_URL', 'https://api.bochaai.com/v1/ai-search')
        self.api_key: Optional[str] = os.getenv('API_KEY')
        
        # Slack 配置
        self.slack_webhook_url: Optional[str] = os.getenv('SLACK_WEBHOOK_URL')
        
        # AI 请求配置
        self.default_query: str = os.getenv('DEFAULT_QUERY', '总结昨天的美股金融财经新闻')
        self.freshness: str = os.getenv('FRESHNESS', 'oneDay')
        self.count: int = int(os.getenv('COUNT', '50'))
        self.answer: bool = os.getenv('ANSWER', 'True').lower() == 'true'
        self.stream: bool = os.getenv('STREAM', 'False').lower() == 'true'
    
    def validate(self) -> bool:
        """验证必需的配置是否存在"""
        if not self.api_key:
            print("错误: 缺少 API_KEY 环境变量")
            return False
        
        if not self.slack_webhook_url:
            print("错误: 缺少 SLACK_WEBHOOK_URL 环境变量")
            return False
        
        return True
    
    def get_headers(self) -> dict:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
    
    def get_payload(self, custom_query: Optional[str] = None) -> dict:
        """获取API请求体"""
        return {
            "query": custom_query or self.default_query,
            "freshness": self.freshness,
            "count": self.count,
            "answer": self.answer,
            "stream": self.stream
        } 