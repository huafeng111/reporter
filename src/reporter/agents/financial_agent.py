from typing import Dict, Any, Optional
import requests
import json
from openai import OpenAI

from .base_agent import BaseAgent
from ..slack_service import SlackService
from config.config import Config

class FinancialAgent(BaseAgent):
    """财经新闻分析Agent - 使用BochaAI搜索 + DeepSeek分析"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化财经新闻Agent"""
        # 设置Agent类型
        config['type'] = 'financial'
        
        # 先设置搜索配置，再调用父类初始化
        self.freshness = config.get('freshness', 'day')
        self.count = config.get('count', 50)
        self.analysis_prompt = config.get('analysis_prompt')
        
        # 加载基础配置（API密钥等）
        self.base_config = Config()
        
        # 调用父类初始化（会触发验证）
        super().__init__(config)
        
        # 初始化DeepSeek客户端
        self.deepseek_client = OpenAI(
            api_key=self.base_config.deepseek_api_key,
            base_url=self.base_config.deepseek_base_url
        )
        
        # 创建Slack服务实例
        self._setup_slack_service()
    
    def _validate_agent_config(self) -> None:
        """验证财经Agent特定配置"""
        if self.freshness not in ['day', 'week', 'month', 'year']:
            raise ValueError(f"Agent '{self.agent_id}': freshness值无效，应为 day/week/month/year")
        
        if self.count <= 0 or self.count > 100:
            raise ValueError(f"Agent '{self.agent_id}': count值应在1-100之间")
        
        # 验证API密钥
        if not self.base_config.bochaai_api_key:
            raise ValueError("缺少 BOCHAAI_API_KEY 环境变量")
        
        if not self.base_config.deepseek_api_key:
            raise ValueError("缺少 DEEPSEEK_API_KEY 环境变量")
    
    def _setup_slack_service(self):
        """设置Slack服务"""
        # 创建专用的Slack服务实例
        slack_config = Config()
        slack_config.slack_webhook_url = self.slack_webhook_url
        slack_config.use_slack_blocks = self.use_slack_blocks
        self.slack_service = SlackService(slack_config)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行财经新闻分析任务
        
        Args:
            **kwargs: 额外参数
            
        Returns:
            执行结果字典
        """
        try:
            print(f"\n🚀 [{self.agent_name}] 开始执行")
            print(f"📋 查询内容: {self.query}")
            
            # 步骤1: BochaAI搜索
            search_context = self._search_with_bochaai(self.query)
            if not search_context:
                return {
                    'success': False,
                    'error': 'BochaAI搜索失败',
                    'agent_id': self.agent_id
                }
            
            # 步骤2: DeepSeek分析
            analysis_content = self._analyze_with_deepseek(search_context, self.query)
            if not analysis_content:
                return {
                    'success': False,
                    'error': 'DeepSeek分析失败',
                    'agent_id': self.agent_id
                }
            
            # 步骤3: 发送到Slack
            slack_success = self.slack_service.send_message(analysis_content, self.agent_name)
            
            result = {
                'success': slack_success,
                'content': analysis_content,
                'agent_id': self.agent_id,
                'query': self.query
            }
            
            if not slack_success:
                result['error'] = 'Slack发送失败'
            
            print(f"✅ [{self.agent_name}] 执行{'成功' if slack_success else '失败'}")
            return result
            
        except Exception as e:
            error_msg = f"Agent执行异常: {str(e)}"
            print(f"❌ [{self.agent_name}] {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'agent_id': self.agent_id
            }
    
    def _search_with_bochaai(self, query: str) -> Optional[str]:
        """使用BochaAI搜索"""
        try:
            headers = {
                'Authorization': f'Bearer {self.base_config.bochaai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'query': query,
                'freshness': self.freshness,
                'count': self.count
            }
            
            print(f"🔍 正在搜索: {query}")
            print(f"📅 时间范围: {self.freshness}, 结果数量: {self.count}")
            
            response = requests.post(
                self.base_config.bochaai_search_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                summaries = []
                
                # 方法1: 使用正确的字段名 - snippet而不是summary
                webpages = response_data.get("data", {}).get("webPages", {}).get("value", [])
                if webpages:
                    # 使用snippet字段获取内容
                    summaries = [item.get("snippet", "") for item in webpages]
                    print(f"📝 使用webPages路径，获得 {len(summaries)} 条内容片段")
                    
                    # 过滤有效内容
                    valid_summaries = [s for s in summaries if s and len(s.strip()) > 10]
                    print(f"📝 有效内容片段: {len(valid_summaries)} 条")
                    
                    if valid_summaries:
                        summaries = valid_summaries
                        print(f"✅ 使用snippet字段成功获取内容")
                
                # 如果没有获取到有效内容，输出调试信息
                if not summaries:
                    print(f"⚠️  未获取到有效搜索内容，原始数据条数: {len(webpages)}")
                    if webpages:
                        print(f"🔍 第一条数据字段: {list(webpages[0].keys())}")
                
                # 最终过滤，确保内容质量
                summaries = [s for s in summaries if s and len(s.strip()) > 10]
                
                # 如果有搜索结果，使用rerank API过滤
                if summaries:
                    summaries = self._rerank_documents(query, summaries)
                
                context = " ".join(summaries)
                
                print(f"✅ 搜索成功，获得 {len(summaries)} 条有效结果")
                print(f"📝 Context长度: {len(context)} 字符")
                
                if len(context) < 100:
                    print(f"⚠️  Context内容过短，前100字符: {context[:100]}")
                
                return context if context else None
            else:
                print(f"❌ BochaAI搜索失败，状态码: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ BochaAI搜索异常: {str(e)}")
            return None
    
    def _rerank_documents(self, query: str, documents: list) -> list:
        """
        使用BochaAI rerank API过滤低相关性文档
        
        Args:
            query: 查询内容
            documents: 原始文档列表
            
        Returns:
            过滤后的高相关性文档列表
        """
        try:
            if not documents:
                return documents
            
            print(f"🔄 正在使用rerank API过滤文档...")
            print(f"📊 原始文档数量: {len(documents)}")
            
            headers = {
                'Authorization': f'Bearer {self.base_config.bochaai_api_key}',
                'Content-Type': 'application/json'
            }
            
            rerank_data = {
                "model": "gte-rerank",
                "query": query,
                "documents": documents,
                "top_n": len(documents),
                "return_documents": True
            }
            
            response = requests.post(
                'https://api.bochaai.com/v1/rerank',
                headers=headers,
                data=json.dumps(rerank_data),
                timeout=30
            )
            
            if response.status_code == 200:
                rerank_results = response.json()
                
                # 过滤相关性分数 > 0.5 的文档
                high_quality_docs = []
                filtered_count = 0
                
                for item in rerank_results['data']['results']:
                    relevance_score = item['relevance_score']
                    document_text = item['document']['text']
                    
                    if relevance_score > 0.5:
                        high_quality_docs.append(document_text)
                        print(f"✅ 保留文档 (相关性: {relevance_score:.3f})")
                    else:
                        filtered_count += 1
                        print(f"🗑️  过滤文档 (相关性: {relevance_score:.3f})")
                
                print(f"📈 Rerank完成: 保留 {len(high_quality_docs)} 条, 过滤 {filtered_count} 条")
                print(f"✨ 平均相关性提升: 保留文档质量更高")
                
                return high_quality_docs if high_quality_docs else documents[:5]  # 如果全部被过滤，保留前5条
            else:
                print(f"❌ Rerank API失败，状态码: {response.status_code}")
                print(f"⚠️  使用原始文档: {response.text}")
                return documents
                
        except Exception as e:
            print(f"❌ Rerank API异常: {str(e)}")
            print(f"⚠️  使用原始文档")
            return documents
    
    def _analyze_with_deepseek(self, context: str, query: str) -> Optional[str]:
        """使用DeepSeek分析"""
        try:
            # 使用自定义分析提示词或默认提示词
            if self.analysis_prompt:
                analysis_prompt = self.analysis_prompt
            else:
                analysis_prompt = f"""
请以专业金融分析师的角度分析以下搜索结果，针对查询"{query}"提供深度分析。

要求：
1. 使用简洁明了的中文
2. 避免使用Markdown格式，使用纯文本
3. 结构清晰，逻辑分明
4. 重点突出关键信息和趋势
5. 提供实用的投资参考价值

请按以下结构组织内容：
• 核心要点总结
• 市场影响分析  
• 关键数据解读
• 风险与机会
• 投资建议
"""
            
            print("🧠 正在使用DeepSeek分析...")
            
            response = self.deepseek_client.chat.completions.create(
                model=self.base_config.deepseek_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的金融信息分析师，擅长从大量信息中提取核心要点并进行深度分析。"
                    },
                    {
                        "role": "user",
                        "content": f"{analysis_prompt}\n\n搜索结果内容：\n{context}"
                    }
                ],
                stream=False
            )
            
            analysis = response.choices[0].message.content
            print("✅ DeepSeek分析完成")
            
            # 使用父类的后处理方法清理Markdown格式
            cleaned_analysis = self.post_execute(analysis)
            print("🧹 已清理Markdown格式")
            
            return cleaned_analysis
            
        except Exception as e:
            print(f"❌ DeepSeek分析失败: {str(e)}")
            return None 