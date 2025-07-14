import requests
import json
from typing import Optional, Dict, Any
from config.config import Config

class AIService:
    """AI API 服务类"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_financial_news_summary(self, custom_query: Optional[str] = None) -> Optional[str]:
        """
        获取金融新闻摘要
        
        Args:
            custom_query: 自定义查询，如果为None则使用默认查询
            
        Returns:
            AI生成的摘要内容，如果失败返回None
        """
        try:
            # 准备请求数据
            headers = self.config.get_headers()
            payload = self.config.get_payload(custom_query)
            data = json.dumps(payload)
            
            # 发送请求
            print(f"正在调用AI API: {self.config.ai_url}")
            response = requests.post(self.config.ai_url, headers=headers, data=data)
            
            if response.status_code == 200:
                print("AI调用成功")
                ai_response = response.json()
                return self._extract_content(ai_response)
            else:
                print(f"AI调用失败，状态码: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"AI服务调用异常: {str(e)}")
            return None
    
    def _extract_content(self, ai_response: Dict[Any, Any]) -> Optional[str]:
        """从AI响应中提取内容"""
        for message in ai_response.get('messages', []):
            if message.get('type') == 'answer' and message.get('content_type') == 'text':
                return message.get('content')
        
        print("未找到有效的AI回答内容")
        return None 