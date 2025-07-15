import requests
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from config.config import Config

class AIService:
    """AI API 服务类 - 使用 BochaAI 搜索 + DeepSeek 分析"""
    
    def __init__(self, config: Config):
        self.config = config
        # 初始化 DeepSeek 客户端
        if not config.deepseek_api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.deepseek_client = OpenAI(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url
        )
    
    def get_financial_news_summary(self, custom_query: Optional[str] = None) -> Optional[str]:
        """
        获取金融新闻摘要 - 使用 BochaAI 搜索 + DeepSeek 分析的新流程
        
        Args:
            custom_query: 自定义查询，如果为None则使用默认查询
            
        Returns:
            AI生成的分析内容，如果失败返回None
        """
        try:
            # 步骤1: 使用 BochaAI 搜索
            search_context = self._search_with_bochaai(custom_query)
            if not search_context:
                return None
            
            # 步骤2: 使用 DeepSeek 分析搜索结果
            analysis = self._analyze_with_deepseek(search_context, custom_query)
            return analysis
            
        except Exception as e:
            print(f"AI服务调用异常: {str(e)}")
            return None
    
    def _search_with_bochaai(self, custom_query: Optional[str] = None) -> Optional[str]:
        """使用 BochaAI 搜索并获取摘要"""
        try:
            headers = self.config.get_bochaai_headers()
            payload = self.config.get_search_payload(custom_query)
            
            query = custom_query or self.config.default_query
            print(f"🔍 正在搜索: {query}")
            print(f"📅 时间范围: {self.config.freshness}")
            
            response = requests.post(
                self.config.bochaai_search_url, 
                headers=headers, 
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # 提取搜索结果摘要
                summaries = [
                    item.get("summary", "") 
                    for item in response_data.get("data", {}).get("webPages", {}).get("value", [])
                ]
                context = " ".join(summaries)
                
                print(f"✅ 搜索成功，获得 {len(summaries)} 条结果")
                print(f"📝 Context长度: {len(context)} 字符")
                
                return context
            else:
                print(f"❌ BochaAI搜索失败，状态码: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ BochaAI搜索异常: {str(e)}")
            return None
    
    def _analyze_with_deepseek(self, context: str, query: Optional[str] = None) -> Optional[str]:
        """使用 DeepSeek 分析搜索结果"""
        try:
            # 构建分析提示词
            analysis_prompt = f"""
请基于以下搜索结果内容，进行专业分析和总结：

1. 核心信息摘要
2. 关键数据和趋势
3. 重要观点和结论
4. 影响和意义

请用中文回答，结构清晰，重点突出。
注意：请使用纯文本格式，不要使用任何Markdown语法（如**加粗**、##标题等），直接用文字表达即可。
"""
            
            print("🧠 正在使用DeepSeek分析...")
            
            response = self.deepseek_client.chat.completions.create(
                model=self.config.deepseek_model,
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
            
            return analysis
            
        except Exception as e:
            print(f"❌ DeepSeek分析失败: {str(e)}")
            return None 