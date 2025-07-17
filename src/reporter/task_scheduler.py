import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .agent_factory import AgentFactory
from .agents.base_agent import BaseAgent

class TaskScheduler:
    """任务调度器 - 管理和执行多个Agent任务"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化任务调度器
        
        Args:
            config_file: 任务配置文件路径
        """
        self.config_file = config_file or self._get_default_config_file()
        self.agents: List[BaseAgent] = []
        self.global_config = {}
        
        # 加载所有任务配置
        self._load_tasks()
    
    def _get_default_config_file(self) -> str:
        """获取默认的任务配置文件"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "config" / "tasks.yaml")
    
    def _load_tasks(self):
        """从配置文件加载所有任务"""
        print(f"📄 加载任务配置文件: {self.config_file}")
        
        if not os.path.exists(self.config_file):
            print(f"⚠️  任务配置文件不存在: {self.config_file}")
            print("正在创建默认任务配置...")
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            # 加载全局配置
            self.global_config = config_data.get('global', {})
            print(f"✅ 加载全局配置: {len(self.global_config)} 项")
            
            # 加载任务列表
            tasks = config_data.get('tasks', [])
            
            for task_config in tasks:
                try:
                    self._create_agent_from_task(task_config)
                except Exception as e:
                    print(f"❌ 创建任务Agent失败 '{task_config.get('id', 'unknown')}': {str(e)}")
            
            print(f"✅ 成功加载 {len(self.agents)} 个任务Agent")
            
        except Exception as e:
            print(f"❌ 加载任务配置文件失败: {str(e)}")
            print("正在创建默认任务配置...")
            self._create_default_config()
    
    def _create_agent_from_task(self, task_config: Dict[str, Any]):
        """从任务配置创建Agent"""
        # 合并全局配置和任务配置
        agent_config = {}
        
        # 应用全局配置
        agent_config.update(self.global_config)
        
        # 应用任务特定配置（会覆盖全局配置）
        agent_config.update(task_config)
        
        # 确保必需字段存在
        if 'type' not in agent_config:
            agent_config['type'] = self.global_config.get('agent_type', 'financial')
        
        if 'slack_webhook_url' not in agent_config:
            agent_config['slack_webhook_url'] = self.global_config.get('slack_webhook_url', '')
        
        # 创建Agent实例
        agent = AgentFactory.create_agent(agent_config)
        
        # 验证Agent配置
        is_valid, error_msg = agent.validate()
        if not is_valid:
            print(f"❌ 任务Agent '{agent.agent_id}' 配置验证失败: {error_msg}")
            return
        
        self.agents.append(agent)
        print(f"✅ 任务Agent '{agent.agent_id}' 创建成功")
    
    def _create_default_config(self):
        """创建默认的任务配置文件"""
        # 如果已经存在配置文件，直接加载
        if os.path.exists(self.config_file):
            print(f"✅ 使用现有任务配置文件: {self.config_file}")
            # 只需要重新加载，不需要递归调用
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            self.global_config = config_data.get('global', {})
            tasks = config_data.get('tasks', [])
            
            for task_config in tasks:
                try:
                    self._create_agent_from_task(task_config)
                except Exception as e:
                    print(f"❌ 创建任务Agent失败 '{task_config.get('id', 'unknown')}': {str(e)}")
            
            print(f"✅ 成功加载 {len(self.agents)} 个任务Agent")
        else:
            print(f"❌ 配置文件不存在且无法自动创建: {self.config_file}")
            print("请手动创建配置文件或检查路径是否正确")
    
    def get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
        """根据ID获取Agent"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
    
    def get_enabled_agents(self) -> List[BaseAgent]:
        """获取所有启用的Agent"""
        return [agent for agent in self.agents if agent.is_enabled()]
    
    def execute_agent(self, agent: BaseAgent) -> Dict[str, Any]:
        """执行单个Agent"""
        try:
            result = agent.execute()
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent.agent_id
            }
    
    def execute_agent_by_id(self, agent_id: str) -> Dict[str, Any]:
        """根据ID执行特定Agent"""
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            return {
                'success': False,
                'error': f'未找到Agent: {agent_id}',
                'agent_id': agent_id
            }
        
        if not agent.is_enabled():
            return {
                'success': False,
                'error': f'Agent已禁用: {agent_id}',
                'agent_id': agent_id
            }
        
        return self.execute_agent(agent)
    
    def execute_all_agents(self, parallel: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        执行所有启用的Agent
        
        Args:
            parallel: 是否并行执行
            
        Returns:
            每个Agent的执行结果字典
        """
        enabled_agents = self.get_enabled_agents()
        
        if not enabled_agents:
            print("⚠️  没有启用的Agent")
            return {}
        
        print(f"🎯 准备执行 {len(enabled_agents)} 个Agent")
        results = {}
        
        if parallel and len(enabled_agents) > 1:
            # 并行执行
            print("🔄 使用并行模式执行...")
            with ThreadPoolExecutor(max_workers=3) as executor:
                # 提交所有任务
                future_to_agent = {
                    executor.submit(self.execute_agent, agent): agent.agent_id
                    for agent in enabled_agents
                }
                
                # 收集结果
                for future in as_completed(future_to_agent):
                    agent_id = future_to_agent[future]
                    try:
                        results[agent_id] = future.result()
                    except Exception as e:
                        print(f"❌ Agent '{agent_id}' 执行异常: {str(e)}")
                        results[agent_id] = {
                            'success': False,
                            'error': str(e),
                            'agent_id': agent_id
                        }
        else:
            # 串行执行
            print("⏳ 使用串行模式执行...")
            for agent in enabled_agents:
                results[agent.agent_id] = self.execute_agent(agent)
                # 添加延迟避免API限制
                if len(enabled_agents) > 1:
                    time.sleep(2)
        
        # 打印执行结果摘要
        success_count = sum(1 for result in results.values() if result.get('success'))
        print(f"\n📊 执行结果摘要:")
        print(f"   总数: {len(results)}")
        print(f"   成功: {success_count}")
        print(f"   失败: {len(results) - success_count}")
        
        return results
    
    def list_agents(self):
        """列出所有Agent"""
        if not self.agents:
            print("📝 没有配置的Agent")
            return
        
        print(f"📝 Agent列表 (共 {len(self.agents)} 个):")
        for i, agent in enumerate(self.agents, 1):
            status = "✅ 启用" if agent.is_enabled() else "❌ 禁用"
            print(f"   {i}. [{agent.agent_id}] {agent.agent_name} - {status}")
            print(f"      类型: {agent.agent_type}")
            print(f"      查询: {agent.query[:50]}{'...' if len(agent.query) > 50 else ''}")
            if agent.schedule:
                print(f"      计划: {agent.schedule}")
    
    def validate_all_agents(self) -> bool:
        """验证所有Agent配置的有效性"""
        all_valid = True
        print("🔍 验证Agent配置...")
        
        for agent in self.agents:
            is_valid, error_msg = agent.validate()
            if not is_valid:
                print(f"❌ Agent '{agent.agent_id}': {error_msg}")
                all_valid = False
            else:
                print(f"✅ Agent '{agent.agent_id}' 配置有效")
        
        return all_valid 