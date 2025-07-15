import requests
import json
from typing import Optional
from datetime import datetime
from config.config import Config

class SlackService:
    """Slack 服务类 - 支持 Block Kit 和简单文本格式"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def send_message(self, content: str, prefix: str = "AI分析报告") -> bool:
        """
        发送分析报告到Slack（支持Block Kit和简单文本两种格式）
        
        Args:
            content: 要发送的消息内容
            prefix: 消息前缀
            
        Returns:
            发送成功返回True，否则返回False
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if self.config.use_slack_blocks:
                # 使用 Slack Block Kit 格式（更美观）
                slack_data = {
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"🤖 {prefix}"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*📅 生成时间:*\n{current_time}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*🔍 查询内容:*\n{self.config.default_query}"
                                }
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*📊 分析结果:*\n{content}"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "_本报告由BochaAI搜索 + DeepSeek分析自动生成_"
                                }
                            ]
                        }
                    ]
                }
            else:
                # 使用简单文本格式（兼容性更好）
                slack_message = f"""🤖 {prefix}

📅 生成时间: {current_time}
🔍 查询内容: {self.config.default_query}

📊 分析结果:
{content}

───────────────────────────
本报告由BochaAI搜索 + DeepSeek分析自动生成"""
                
                slack_data = {
                    'text': slack_message
                }
            
            print("📱 正在发送消息到Slack...")
            response = requests.post(
                self.config.slack_webhook_url,
                data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ 消息成功发送到Slack！")
                return True
            else:
                print(f"❌ Slack请求失败，状态码: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Slack服务异常: {str(e)}")
            return False
    
    def send_error_message(self, error_msg: str) -> bool:
        """发送错误消息到Slack"""
        return self.send_message(error_msg, "错误报告") 