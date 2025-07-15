import os
from typing import Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        # BochaAI 搜索 API 配置
        self.bochaai_search_url: str = os.getenv('BOCHAAI_SEARCH_URL', 'https://api.bochaai.com/v1/web-search')
        self.bochaai_api_key: Optional[str] = os.getenv('BOCHAAI_API_KEY')
        
        # DeepSeek 分析 API 配置
        self.deepseek_api_key: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.deepseek_model: str = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
        
        # Slack 配置
        self.slack_webhook_url: Optional[str] = os.getenv('SLACK_WEBHOOK_URL')
        self.use_slack_blocks: bool = os.getenv('USE_SLACK_BLOCKS', 'True').lower() == 'true'
        
        # 搜索请求配置
        self.default_query: str = os.getenv('DEFAULT_QUERY', '总结昨天的美股金融财经新闻')
        self.freshness: str = os.getenv('FRESHNESS', 'day')
        self.count: int = int(os.getenv('COUNT', '50'))
        
        # 向后兼容（保留旧的环境变量名作为备用）
        if not self.bochaai_api_key and os.getenv('API_KEY'):
            self.bochaai_api_key = os.getenv('API_KEY')
    
    def validate(self) -> bool:
        """验证必需的配置是否存在"""
        if not self.bochaai_api_key:
            print("错误: 缺少 BOCHAAI_API_KEY 环境变量")
            return False
            
        if not self.deepseek_api_key:
            print("错误: 缺少 DEEPSEEK_API_KEY 环境变量")
            return False
        
        if not self.slack_webhook_url:
            print("错误: 缺少 SLACK_WEBHOOK_URL 环境变量")
            return False
        
        return True
    
    def get_bochaai_headers(self) -> dict:
        """获取BochaAI API请求头"""
        return {
            "Authorization": f"Bearer {self.bochaai_api_key}",
            "Content-Type": "application/json"
        }
    
    def get_search_payload(self, custom_query: Optional[str] = None) -> dict:
        """获取搜索API请求体"""
        return {
            "query": custom_query or self.default_query,
            "freshness": self.freshness,
            "summary": True,
            "count": self.count
        } 