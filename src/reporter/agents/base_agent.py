from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import os

class BaseAgent(ABC):
    """基础Agent抽象类 - 定义所有Agent的通用接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Agent
        
        Args:
            config: Agent配置字典
        """
        self.config = config
        self.agent_id = config.get('id', 'default')
        self.agent_name = config.get('name', 'Default Agent')
        self.agent_type = config.get('type', 'base')
        self.enabled = config.get('enabled', True)
        
        # 查询配置
        self.query = config.get('query', '')
        
        # Slack配置
        self.slack_webhook_url = self._resolve_env_var(config.get('slack_webhook_url', ''))
        self.use_slack_blocks = config.get('use_slack_blocks', True)
        
        # 调度配置
        self.schedule = config.get('schedule')  # cron表达式
        
        # 验证配置
        self._validate_config()
    
    def _resolve_env_var(self, value: str) -> str:
        """解析环境变量"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, value)
        return value
    
    def _validate_config(self) -> None:
        """验证Agent基础配置"""
        if not self.agent_id:
            raise ValueError("Agent ID不能为空")
        
        if not self.query:
            raise ValueError(f"Agent '{self.agent_id}': 查询内容不能为空")
        
        # Slack配置从环境变量验证，不再验证tasks.yaml中的配置
        import os
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if not slack_webhook:
            raise ValueError(f"Agent '{self.agent_id}': 缺少 SLACK_WEBHOOK_URL 环境变量")
        
        if not slack_webhook.startswith('https://hooks.slack.com/'):
            raise ValueError(f"Agent '{self.agent_id}': SLACK_WEBHOOK_URL 环境变量格式无效")
        
        # 调用子类的验证方法
        self._validate_agent_config()
    
    @abstractmethod
    def _validate_agent_config(self) -> None:
        """验证Agent特定配置 - 子类必须实现"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行Agent任务 - 子类必须实现
        
        Args:
            **kwargs: 额外参数
            
        Returns:
            执行结果字典，包含success, content, error等
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            'id': self.agent_id,
            'name': self.agent_name,
            'type': self.agent_type,
            'enabled': self.enabled,
            'query': self.query,
            'schedule': self.schedule,
            'slack_webhook': self.slack_webhook_url[:50] + '...' if len(self.slack_webhook_url) > 50 else self.slack_webhook_url
        }
    
    def is_enabled(self) -> bool:
        """检查Agent是否启用"""
        return self.enabled
    
    def validate(self) -> tuple[bool, str]:
        """
        验证Agent配置
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            self._validate_config()
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def post_execute(self, content: str) -> str:
        """
        AI回复的后处理方法 - 清理Markdown格式
        
        Args:
            content: AI生成的原始内容
            
        Returns:
            处理后的内容
        """
        if not content:
            return content
        
        return self._clean_markdown_format(content)
    
    def _clean_markdown_format(self, text: str) -> str:
        """
        清理Markdown格式标记，转换为纯文本
        
        Args:
            text: 包含Markdown格式的文本
            
        Returns:
            清理后的纯文本
        """
        if not text:
            return text
        
        import re
        
        # 去除粗体标记 **文本** 或 __文本__
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        
        # 去除斜体标记 *文本* 或 _文本_
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        
        # 去除标题标记 # ## ### 等
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 去除代码块标记 ```
        text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), text)
        text = re.sub(r'```', '', text)
        
        # 去除行内代码标记 `代码`
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # 去除链接标记 [文本](链接)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # 去除引用标记 > 
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # 将Markdown列表标记转换为简单的项目符号
        text = re.sub(r'^[-*+]\s+', '• ', text, flags=re.MULTILINE)
        
        # 去除分割线 --- 或 ***
        text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)
        
        # 清理多余的空行（保留段落间的单个空行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 去除行首行尾的空白字符
        text = text.strip()
        
        return text 