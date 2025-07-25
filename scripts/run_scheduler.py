#!/usr/bin/env python3
"""
智能任务调度器

自动读取所有配置文件，根据每个任务的schedule字段判断是否需要在当前时间运行。
这个脚本应该每分钟由cron调用一次，它会检查所有任务并运行到期的任务。
"""

import os
import sys
import yaml
import glob
from pathlib import Path
from datetime import datetime
from croniter import croniter
from typing import List, Dict, Any

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

class SmartScheduler:
    """智能调度器 - 根据配置文件中的schedule字段执行任务"""
    
    def __init__(self):
        self.config_dir = project_root / "config"
        self.current_time = datetime.now()
        
    def find_config_files(self) -> List[Path]:
        """查找所有任务配置文件"""
        config_files = set()  # 使用set避免重复
        
        # 查找所有以tasks.yaml结尾的文件
        for pattern in ["*tasks.yaml", "*_tasks.yaml"]:
            files = glob.glob(str(self.config_dir / pattern))
            config_files.update([Path(f) for f in files])
        
        return sorted(list(config_files))
    
    def load_tasks_from_config(self, config_file: Path) -> List[Dict[str, Any]]:
        """从配置文件加载任务列表"""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            tasks = config_data.get('tasks', [])
            
            # 为每个任务添加配置文件信息
            for task in tasks:
                task['_config_file'] = str(config_file)
            
            return tasks
        except Exception as e:
            print(f"❌ 加载配置文件失败 {config_file}: {str(e)}")
            return []
    
    def should_run_now(self, schedule: str, last_run_time: datetime = None) -> bool:
        """判断任务是否应该在当前时间运行"""
        try:
            cron = croniter(schedule, self.current_time)
            
            # 获取上一次应该运行的时间
            prev_time = cron.get_prev(datetime)
            
            # 如果当前时间和上一次运行时间在同一分钟内，则应该运行
            current_minute = self.current_time.replace(second=0, microsecond=0)
            prev_minute = prev_time.replace(second=0, microsecond=0)
            
            return current_minute == prev_minute
            
        except Exception as e:
            print(f"❌ 解析cron表达式失败 '{schedule}': {str(e)}")
            return False
    
    def get_tasks_to_run(self) -> List[Dict[str, Any]]:
        """获取当前时间需要运行的所有任务"""
        tasks_to_run = []
        config_files = self.find_config_files()
        
        print(f"🔍 扫描配置文件: {len(config_files)} 个")
        for config_file in config_files:
            print(f"   📄 {config_file.name}")
        
        for config_file in config_files:
            tasks = self.load_tasks_from_config(config_file)
            
            for task in tasks:
                # 检查任务是否启用
                if not task.get('enabled', True):
                    continue
                
                schedule = task.get('schedule')
                if not schedule:
                    continue
                
                # 判断是否需要运行
                if self.should_run_now(schedule):
                    tasks_to_run.append(task)
                    print(f"✅ 任务需要运行: {task.get('name', task.get('id'))} (来源: {config_file.name})")
        
        return tasks_to_run
    
    def run_task(self, task: Dict[str, Any]) -> bool:
        """运行单个任务"""
        try:
            config_file = task['_config_file']
            task_id = task.get('id', 'unknown')
            
            print(f"\n🚀 执行任务: {task.get('name', task_id)}")
            print(f"📄 配置文件: {config_file}")
            print(f"⏰ 调度: {task.get('schedule')}")
            
            # 创建任务调度器并运行指定任务
            scheduler = TaskScheduler(config_file)
            result = scheduler.execute_agent_by_id(task_id)
            
            success = result.get('success', False)
            if success:
                print(f"✅ 任务 '{task_id}' 执行成功")
            else:
                print(f"❌ 任务 '{task_id}' 执行失败: {result.get('error', '未知错误')}")
            
            return success
            
        except Exception as e:
            print(f"❌ 任务执行异常: {str(e)}")
            return False
    
    def run(self):
        """运行智能调度器"""
        print(f"🕐 智能调度器启动 - {self.current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取需要运行的任务
        tasks_to_run = self.get_tasks_to_run()
        
        if not tasks_to_run:
            print("😴 当前时间没有需要运行的任务")
            return True
        
        print(f"\n🎯 发现 {len(tasks_to_run)} 个待运行任务")
        
        # 按配置文件分组运行任务，避免同一配置文件的任务冲突
        config_groups = {}
        for task in tasks_to_run:
            config_file = task['_config_file']
            if config_file not in config_groups:
                config_groups[config_file] = []
            config_groups[config_file].append(task)
        
        total_success = 0
        total_tasks = len(tasks_to_run)
        
        # 分组执行任务
        for config_file, tasks in config_groups.items():
            print(f"\n📂 处理配置文件: {Path(config_file).name}")
            for task in tasks:
                if self.run_task(task):
                    total_success += 1
        
        print(f"\n📊 执行完成: {total_success}/{total_tasks} 个任务成功")
        return total_success == total_tasks

def main():
    """主函数"""
    try:
        scheduler = SmartScheduler()
        success = scheduler.run()
        
        if success:
            print("✅ 智能调度器执行成功")
            sys.exit(0)
        else:
            print("❌ 智能调度器执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 智能调度器异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 