from typing import Dict, Any, Type
from .agents.base_agent import BaseAgent
from .agents.financial_agent import FinancialAgent

class AgentFactory:
    """Agent工厂 - 根据配置自动装配Agent"""
    
    # 注册的Agent类型映射
    _agent_types: Dict[str, Type[BaseAgent]] = {
        'financial': FinancialAgent,
        'financial_news': FinancialAgent,  # 别名
        'news': FinancialAgent,           # 别名
    }
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[BaseAgent]):
        """
        注册新的Agent类型
        
        Args:
            agent_type: Agent类型名称
            agent_class: Agent类
        """
        cls._agent_types[agent_type] = agent_class
        print(f"📝 已注册Agent类型: {agent_type} -> {agent_class.__name__}")
    
    @classmethod
    def create_agent(cls, agent_config: Dict[str, Any]) -> BaseAgent:
        """
        根据配置创建Agent实例
        
        Args:
            agent_config: Agent配置字典
            
        Returns:
            Agent实例
            
        Raises:
            ValueError: 当Agent类型不存在时
        """
        agent_type = agent_config.get('type', 'financial')
        
        if agent_type not in cls._agent_types:
            available_types = ', '.join(cls._agent_types.keys())
            raise ValueError(f"未知的Agent类型: {agent_type}. 可用类型: {available_types}")
        
        agent_class = cls._agent_types[agent_type]
        
        print(f"🏭 创建Agent: {agent_config.get('id', 'unknown')} (类型: {agent_type})")
        
        return agent_class(agent_config)
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """获取所有可用的Agent类型"""
        return list(cls._agent_types.keys())
    
    @classmethod
    def validate_agent_type(cls, agent_type: str) -> bool:
        """验证Agent类型是否存在"""
        return agent_type in cls._agent_types
    
    @classmethod
    def get_agent_info(cls) -> Dict[str, str]:
        """获取所有注册的Agent类型信息"""
        return {
            agent_type: agent_class.__name__
            for agent_type, agent_class in cls._agent_types.items()
        } 