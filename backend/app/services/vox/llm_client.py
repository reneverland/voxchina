"""
LLM 客户端模块
支持 OpenAI、Anthropic、Azure OpenAI 等
统一接口调用
"""

import os
import json
from typing import List, Dict, Any, Optional, Literal


def call_llm(
    provider: Literal["openai", "anthropic", "azure"] = "openai",
    model: str = "gpt-4o-mini",
    messages: List[Dict[str, str]] = None,
    response_format: Optional[Literal["text", "json"]] = "text",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    统一 LLM 调用接口
    
    Args:
        provider: LLM 提供商 (openai/anthropic/azure)
        model: 模型名称
        messages: 消息列表 [{'role': 'system/user/assistant', 'content': '...'}]
        response_format: 响应格式 (text/json)
        temperature: 温度参数
        max_tokens: 最大 token 数
    
    Returns:
        LLM 响应文本
    """
    if provider == "openai":
        return _call_openai(model, messages, response_format, temperature, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(model, messages, temperature, max_tokens)
    elif provider == "azure":
        return _call_azure(model, messages, response_format, temperature, max_tokens)
    else:
        raise ValueError(f"不支持的 provider: {provider}")


def _call_openai(
    model: str,
    messages: List[Dict[str, str]],
    response_format: str,
    temperature: float,
    max_tokens: Optional[int]
) -> str:
    """调用 OpenAI API"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai 库未安装。请运行: pip install openai")
    
    # 优先使用平台配置，其次使用环境变量
    api_key = None
    api_base = "https://api.openai.com/v1"
    
    try:
        from app.core.config import settings
        api_key = settings.OPENAI_API_KEY
        api_base = settings.OPENAI_API_BASE
    except ImportError:
        # 如果无法导入 settings，尝试从环境变量获取
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    
    if not api_key:
        raise ValueError("未设置 OPENAI_API_KEY 环境变量")
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    # 构建请求参数
    request_params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    
    if max_tokens:
        request_params["max_tokens"] = max_tokens
    
    # JSON 模式
    if response_format == "json":
        request_params["response_format"] = {"type": "json_object"}
    
    # 调用 API
    response = client.chat.completions.create(**request_params)
    
    return response.choices[0].message.content


def _call_anthropic(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: Optional[int]
) -> str:
    """调用 Anthropic Claude API"""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic 库未安装。请运行: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("未设置 ANTHROPIC_API_KEY 环境变量")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Claude 需要分离 system 和 user messages
    system_msg = None
    claude_messages = []
    
    for msg in messages:
        if msg['role'] == 'system':
            system_msg = msg['content']
        else:
            claude_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
    
    request_params = {
        "model": model,
        "messages": claude_messages,
        "temperature": temperature,
        "max_tokens": max_tokens or 4096
    }
    
    if system_msg:
        request_params["system"] = system_msg
    
    response = client.messages.create(**request_params)
    
    return response.content[0].text


def _call_azure(
    model: str,
    messages: List[Dict[str, str]],
    response_format: str,
    temperature: float,
    max_tokens: Optional[int]
) -> str:
    """调用 Azure OpenAI API"""
    try:
        from openai import AzureOpenAI
    except ImportError:
        raise ImportError("openai 库未安装。请运行: pip install openai")
    
    # Azure 需要额外的环境变量
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not api_key or not endpoint:
        raise ValueError("未设置 AZURE_OPENAI_API_KEY 或 AZURE_OPENAI_ENDPOINT 环境变量")
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    request_params = {
        "model": model,  # Azure 中这是 deployment name
        "messages": messages,
        "temperature": temperature,
    }
    
    if max_tokens:
        request_params["max_tokens"] = max_tokens
    
    if response_format == "json":
        request_params["response_format"] = {"type": "json_object"}
    
    response = client.chat.completions.create(**request_params)
    
    return response.choices[0].message.content


# ===== Mock 模式（用于测试） =====

_MOCK_MODE = False
_MOCK_RESPONSES = {}


def enable_mock_mode(mock_responses: Dict[str, str] = None):
    """
    启用 Mock 模式（用于测试，不调用真实 API）
    
    Args:
        mock_responses: 预定义的响应字典 {'prompt_key': 'response_text'}
    """
    global _MOCK_MODE, _MOCK_RESPONSES
    _MOCK_MODE = True
    _MOCK_RESPONSES = mock_responses or {}
    print("[LLM Client] Mock 模式已启用")


def disable_mock_mode():
    """禁用 Mock 模式"""
    global _MOCK_MODE
    _MOCK_MODE = False
    print("[LLM Client] Mock 模式已禁用")


def _get_mock_response(messages: List[Dict[str, str]]) -> str:
    """获取 Mock 响应"""
    # 简单的 Mock 逻辑：根据关键字返回不同响应
    user_content = ""
    for msg in messages:
        if msg['role'] == 'user':
            user_content += msg['content']
    
    # 判断模式
    if "SINGLE_SUMMARY" in user_content:
        return json.dumps({
            "mode": "SINGLE_SUMMARY",
            "title_guess": "测试论文标题",
            "summary_text": "这是一篇测试论文的摘要。研究团队分析了某个重要问题，使用了某种方法。研究发现：结论1、结论2、结论3。这一结果主要归因于某种机制。"
        }, ensure_ascii=False)
    
    elif "可用于口播的要点" in user_content:
        return json.dumps({
            "doc_id": "doc_0",
            "title_guess": "测试文档标题",
            "bullets": [
                "要点1: 研究主题介绍",
                "要点2: 核心发现描述",
                "要点3: 政策含义分析",
                "要点4: 实际应用案例",
                "要点5: 未来展望"
            ]
        }, ensure_ascii=False)
    
    elif "最终口播稿" in user_content or "MULTI_SCRIPT" in user_content:
        return json.dumps({
            "mode": "MULTI_SCRIPT",
            "episode_title": "测试口播稿标题",
            "script_text": """测试口播稿标题

大家好，我是测试机构的测试主播。
很高兴在VOXCHINA和大家见面。

今天我们从三个维度探讨这个话题：创新引领、资源协调和风险管控。

创新引领：
第一个维度关注创新。研究显示，创新是发展的重要动力。多个案例表明，技术创新能够带来显著效益。

资源协调：
第二个维度是资源协调。有效的资源配置对成功至关重要。研究发现，协调机制能够提升整体效率。

Figure 1. 创新与资源协调的关系示意图

风险管控：
第三个维度涉及风险管控。任何发展都伴随风险，需要建立完善的管控体系。实践证明，前瞻性的风险识别能够减少损失。

Figure 2. 风险管控框架图

总结来说，创新、协调与管控三位一体，共同推动可持续发展。

欢迎继续关注 VOXCHINA，我们下期再见！"""
        }, ensure_ascii=False)
    
    # 默认响应
    return "Mock response: 这是一个测试响应"


# 拦截调用（如果启用 Mock）
_original_call_openai = _call_openai
_original_call_anthropic = _call_anthropic
_original_call_azure = _call_azure


def call_llm(
    provider: Literal["openai", "anthropic", "azure"] = "openai",
    model: str = "gpt-4o-mini",
    messages: List[Dict[str, str]] = None,
    response_format: Optional[Literal["text", "json"]] = "text",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """统一 LLM 调用接口（支持 Mock）"""
    
    # Mock 模式
    if _MOCK_MODE:
        print(f"[Mock] 调用 {provider}/{model}")
        return _get_mock_response(messages)
    
    # 真实调用
    if provider == "openai":
        return _original_call_openai(model, messages, response_format, temperature, max_tokens)
    elif provider == "anthropic":
        return _original_call_anthropic(model, messages, temperature, max_tokens)
    elif provider == "azure":
        return _original_call_azure(model, messages, response_format, temperature, max_tokens)
    else:
        raise ValueError(f"不支持的 provider: {provider}")


if __name__ == "__main__":
    # 测试（Mock 模式）
    enable_mock_mode()
    
    print("=== 测试 OpenAI 调用 (Mock) ===")
    messages = [
        {'role': 'system', 'content': '你是助手'},
        {'role': 'user', 'content': '请输出 SINGLE_SUMMARY 格式'}
    ]
    
    response = call_llm(
        provider="openai",
        model="gpt-4o-mini",
        messages=messages,
        response_format="json"
    )
    
    print(f"响应: {response[:200]}...")
    
    # 验证 JSON
    try:
        parsed = json.loads(response)
        print(f"JSON 解析成功: mode={parsed.get('mode')}")
    except json.JSONDecodeError:
        print("JSON 解析失败")
