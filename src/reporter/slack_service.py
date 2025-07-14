import requests
import json
from typing import Optional
from config.config import Config

class SlackService:
    """Slack 服务类"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def send_message(self, content: str, prefix: str = "AI摘要") -> bool:
        """
        发送消息到Slack
        
        Args:
            content: 要发送的消息内容
            prefix: 消息前缀
            
        Returns:
            发送成功返回True，否则返回False
        """
        try:
            slack_data = {
                'text': f"{prefix}：\n{content}"
            }
            
            print("正在发送消息到Slack...")
            response = requests.post(
                self.config.slack_webhook_url,
                data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("消息成功发送到Slack！")
                return True
            else:
                print(f"Slack请求失败，状态码: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"Slack服务异常: {str(e)}")
            return False
    
    def send_error_message(self, error_msg: str) -> bool:
        """发送错误消息到Slack"""
        return self.send_message(error_msg, "错误报告") 