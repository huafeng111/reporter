#!/usr/bin/env python3
"""
基于Agent的财经新闻报告器

支持配置文件驱动的多Agent执行模式，每个Agent都有独立的配置和查询
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
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
        print("警告: .env 文件不存在，请根据需要创建")
except ImportError:
    print("警告: python-dotenv 未安装，将直接使用环境变量")

from src.reporter.task_scheduler import TaskScheduler
from src.reporter.agent_factory import AgentFactory

class AgentRunner:
    """Agent运行器主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化Agent运行器
        
        Args:
            config_file: 任务配置文件路径
        """
        self.scheduler = TaskScheduler(config_file)
    
    def run_all(self, parallel: bool = True) -> bool:
        """
        运行所有启用的Agent
        
        Args:
            parallel: 是否并行执行
            
        Returns:
            所有Agent都成功返回True，否则返回False
        """
        print("🚀 开始执行多Agent财经新闻分析任务...")
        
        # 验证配置
        if not self.scheduler.validate_all_agents():
            print("❌ Agent配置验证失败，请检查配置文件")
            return False
        
        # 执行所有Agent
        results = self.scheduler.execute_all_agents(parallel=parallel)
        
        if not results:
            print("⚠️  没有执行任何Agent")
            return False
        
        # 检查执行结果
        success_count = sum(1 for result in results.values() if result.get('success'))
        total_count = len(results)
        
        print(f"\n🎯 执行完成: {success_count}/{total_count} 个Agent成功")
        
        return success_count == total_count
    
    def run_single(self, agent_id: str) -> bool:
        """
        运行单个Agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            执行成功返回True，否则返回False
        """
        print(f"🚀 开始执行单个Agent: {agent_id}")
        
        result = self.scheduler.execute_agent_by_id(agent_id)
        
        if result.get('success'):
            print(f"✅ Agent '{agent_id}' 执行成功")
            return True
        else:
            print(f"❌ Agent '{agent_id}' 执行失败: {result.get('error', '未知错误')}")
            return False
    
    def list_agents(self):
        """列出所有Agent配置"""
        self.scheduler.list_agents()
    
    def validate_config(self) -> bool:
        """验证配置"""
        return self.scheduler.validate_all_agents()
    
    def show_agent_types(self):
        """显示可用的Agent类型"""
        types = AgentFactory.get_available_types()
        agent_info = AgentFactory.get_agent_info()
        
        print("📋 可用的Agent类型:")
        for agent_type in types:
            class_name = agent_info.get(agent_type, 'Unknown')
            print(f"   • {agent_type} -> {class_name}")

def main():
    """主函数 - 支持命令行参数"""
    parser = argparse.ArgumentParser(
        description="基于Agent的财经新闻AI分析报告器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                          # 执行所有启用的Agent
  %(prog)s --agent daily_news       # 执行指定Agent
  %(prog)s --list                   # 列出所有Agent配置
  %(prog)s --validate               # 验证配置文件
  %(prog)s --types                  # 显示可用Agent类型
  %(prog)s --config ./my_tasks.yaml # 使用自定义任务配置文件

任务配置文件结构:
  config/tasks.yaml        # 统一的任务配置文件

配置文件格式:
  global:
    slack_webhook_url: "your-webhook-url"
    agent_type: "financial"
  
  tasks:
    - id: daily_news
      name: 每日财经新闻摘要
      query: 总结昨天的美股金融财经新闻
      schedule: "0 2 * * *"
      # ... 其他配置
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='任务配置文件路径（默认: config/tasks.yaml）'
    )
    
    parser.add_argument(
        '--agent', '-a',
        type=str,
        help='执行指定的Agent ID'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='执行所有启用的Agent（默认行为）'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        default=True,
        help='并行执行模式（默认启用）'
    )
    
    parser.add_argument(
        '--serial', '-s',
        action='store_true',
        help='串行执行模式'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有Agent配置'
    )
    
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='验证Agent配置文件'
    )
    
    parser.add_argument(
        '--types', '-t',
        action='store_true',
        help='显示可用的Agent类型'
    )
    
    args = parser.parse_args()
    
    # 处理并行/串行参数
    parallel = not args.serial
    
    try:
        # 初始化Agent运行器
        runner = AgentRunner(args.config)
        
        # 处理不同的命令
        if args.list:
            runner.list_agents()
            sys.exit(0)
        
        if args.validate:
            success = runner.validate_config()
            if success:
                print("✅ 所有Agent配置验证通过")
                sys.exit(0)
            else:
                print("❌ Agent配置验证失败")
                sys.exit(1)
        
        if args.types:
            runner.show_agent_types()
            sys.exit(0)
        
        if args.agent:
            # 执行指定Agent
            success = runner.run_single(args.agent)
        else:
            # 执行所有Agent（默认行为）
            success = runner.run_all(parallel=parallel)
        
        if success:
            print("✅ 任务执行成功！")
            sys.exit(0)
        else:
            print("❌ 任务执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序执行异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 