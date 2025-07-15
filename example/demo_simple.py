#!/usr/bin/env python3
"""
简化版Demo: BochaAI搜索 + DeepSeek分析 + Slack通知
"""

import requests
import json
from openai import OpenAI
from datetime import datetime

# ================================
# 配置信息
# ================================

# BochaAI API配置
BOCHAAI_API_URL = "https://api.bochaai.com/v1/web-search"
BOCHAAI_API_KEY = "sk-5e0289f81a964b09bba95a06cff8f711"  # 你的BochaAI API KEY

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-c60312b45d254ca1903bf9754babe453"  # 你的DeepSeek API KEY

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Slack Webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# Slack消息格式配置
USE_SLACK_BLOCKS = True  # True: 使用Block Kit格式, False: 使用简单文本格式

# ================================
# BochaAI搜索函数
# ================================

def search_with_bochaai(query, freshness="day", count=50):
    """
    使用BochaAI进行搜索并获取摘要
    """
    try:
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {BOCHAAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 设置请求体
        data = {
            "query": query,
            "freshness": freshness,
            "summary": True,
            "count": count
        }
        
        print(f"🔍 正在搜索: {query}")
        print(f"📅 时间范围: {freshness}")
        
        # 发送POST请求
        response = requests.post(BOCHAAI_API_URL, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            response_data = response.json()
            
            # 提取summary字段并拼接成context
            summaries = [item.get("summary", "") for item in response_data.get("data", {}).get("webPages", {}).get("value", [])]
            context = " ".join(summaries)
            
            print(f"✅ 搜索成功，获得 {len(summaries)} 条结果")
            print(f"📝 Context长度: {len(context)} 字符")
            
            return context
        else:
            print(f"❌ BochaAI请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ BochaAI搜索异常: {str(e)}")
        return None

# ================================
# DeepSeek分析函数
# ================================

def analyze_with_deepseek(context, custom_prompt=None):
    """
    使用DeepSeek分析搜索结果
    """
    try:
        # 默认提示词
        if custom_prompt is None:
            custom_prompt = """
请基于以下搜索结果内容，进行专业分析和总结：

1. 核心信息摘要
2. 关键数据和趋势
3. 重要观点和结论
4. 影响和意义

请用中文回答，结构清晰，重点突出。
注意：请使用纯文本格式，不要使用任何Markdown语法（如**加粗**、##标题等），直接用文字表达即可。
"""
        
        print("🧠 正在使用DeepSeek分析...")
        
        # 调用DeepSeek API（新版本接口）
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的信息分析师，擅长从大量信息中提取核心要点并进行深度分析。"},
                {"role": "user", "content": f"{custom_prompt}\n\n搜索结果内容：\n{context}"}
            ],
            stream=False
        )
        
        analysis = response.choices[0].message.content
        print("✅ DeepSeek分析完成")
        
        return analysis
        
    except Exception as e:
        print(f"❌ DeepSeek分析失败: {str(e)}")
        return None

# ================================
# Slack通知函数
# ================================

def send_to_slack(query, analysis):
    """
    发送分析结果到Slack（支持Block Kit和简单文本两种格式）
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if USE_SLACK_BLOCKS:
            # 使用Slack Block Kit格式（更美观）
            slack_data = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 AI智能分析报告"
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
                                "text": f"*🔍 搜索查询:*\n{query}"
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
                            "text": f"*📊 分析结果:*\n{analysis}"
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
            slack_message = f"""🤖 AI智能分析报告

📅 生成时间: {current_time}
🔍 搜索查询: {query}

📊 分析结果:
{analysis}

───────────────────────────
本报告由BochaAI搜索 + DeepSeek分析自动生成"""
            
            slack_data = {
                'text': slack_message
            }
        
        print("📱 正在发送到Slack...")
        
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ 消息成功发送到Slack!")
            return True
        else:
            print(f"❌ Slack发送失败，状态码: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 发送到Slack失败: {str(e)}")
        return False

# ================================
# 主程序
# ================================

def main():
    """
    主函数：搜索 → 分析 → 通知
    """
    print("🚀 开始AI智能分析任务...")
    print("=" * 50)
    
    # 可以自定义查询
    queries = [
        "阿里巴巴2024年的esg报告",
        "美股最新市场动态",
        "人工智能行业发展趋势",
    ]
    
    # 选择查询（可以修改为接收命令行参数）
    query = queries[0]  # 默认使用第一个查询
    
    # 步骤1：BochaAI搜索
    print(f"📰 步骤1: 使用BochaAI搜索...")
    context = search_with_bochaai(query, freshness="day", count=50)
    
    if not context:
        print("❌ 未获取到搜索结果")
        return
    
    # 显示context预览
    print(f"\n📋 搜索结果预览:")
    print(context[:300] + "..." if len(context) > 300 else context)
    
    # 步骤2：DeepSeek分析
    print(f"\n🧠 步骤2: 使用DeepSeek分析...")
    analysis = analyze_with_deepseek(context)
    
    if not analysis:
        print("❌ DeepSeek分析失败")
        return
    
    print(f"\n📊 分析结果预览:")
    print(analysis[:200] + "..." if len(analysis) > 200 else analysis)
    
    # 步骤3：发送到Slack
    print(f"\n📱 步骤3: 发送到Slack...")
    success = send_to_slack(query, analysis)
    
    if success:
        print("🎉 任务完成！分析结果已发送到Slack")
    else:
        print("⚠️ 任务部分完成，但Slack发送失败")
    
    print("=" * 50)

# ================================
# 自定义查询版本
# ================================

def run_custom_query(query, freshness="day", count=50, custom_prompt=None):
    """
    运行自定义查询
    """
    print(f"🔍 运行自定义查询: {query}")
    
    # 搜索
    context = search_with_bochaai(query, freshness, count)
    if not context:
        return False
    
    # 分析
    analysis = analyze_with_deepseek(context, custom_prompt)
    if not analysis:
        return False
    
    # 发送
    return send_to_slack(query, analysis)

if __name__ == "__main__":
    # 运行主程序
    main()
    
    # 或者运行自定义查询的例子
    # run_custom_query("特斯拉最新财报分析", freshness="week", count=30) 