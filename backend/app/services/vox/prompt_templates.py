"""
Prompt 模板模块
三个核心模板：
1. SINGLE_SUMMARY: 单篇摘要
2. QUICK_BRIEF: 多篇要点提取
3. FINAL_SCRIPT: 多篇整合口播稿
"""

from typing import List, Dict, Any
import json


def build_single_summary_prompt(doc_text: str, duration_target_sec: int = 150) -> List[Dict[str, str]]:
    """
    构建单篇摘要 Prompt
    
    Args:
        doc_text: 文档文本
        duration_target_sec: 目标时长（秒），用于计算摘要长度
    
    Returns:
        [{'role': 'system', 'content': '...'}, {'role': 'user', 'content': '...'}]
    """
    # 根据目标时长计算字数范围
    # 阅读速度：约4-6字/秒（中文），约2-3词/秒（英文）
    min_chars_zh = int(duration_target_sec * 3.5)  # 约3.5字/秒
    max_chars_zh = int(duration_target_sec * 6)    # 约6字/秒
    min_words_en = int(duration_target_sec * 1.8)  # 约1.8词/秒
    max_words_en = int(duration_target_sec * 2.5)  # 约2.5词/秒
    
    system_prompt = """你是 VoxChina 文章摘要助手。速度优先，但禁止编造。数字/年份/作者/机构若无法从文本确认就不要写。语言要像"研究速递"，信息密度高，短句为主。

**重要规则（必须100%遵守）**：
1. 对于中文人名，必须保留中文原文，绝对不要翻译成英文或拼音
2. 如果原文同时包含中英文人名（如"薄诗雨（Shiyu Bo）"），只保留中文部分（"薄诗雨"）
3. 对于不确定如何翻译的中文人名，必须保留英文原文，不要强行翻译"""
    
    user_prompt = f"""请阅读以下单篇文章全文，输出中文摘要、英文摘要及结构化事实表。

【⚠️ 字数要求（必须严格遵守）】：
- 目标时长：{duration_target_sec}秒
- 中文摘要：{min_chars_zh}-{max_chars_zh}字
- 英文摘要：{min_words_en}-{max_words_en}词
- ❌ 字数超出范围会导致口播时间不符合要求，必须严格控制

输出严格 JSON 格式：
{{
  "mode": "SINGLE_SUMMARY",
  "title_guess": "...(从文中提取的标题)",
  "summary_zh": "...(中文摘要，{min_chars_zh}-{max_chars_zh}字。第一段：作者+机构+研究主题+数据/方法；第二段：核心结论+机制/归因)",
  "summary_en": "...(English abstract, {min_words_en}-{max_words_en} words. Paragraph 1: Authors + Institution + Research topic; Paragraph 2: Key findings + Mechanism. **For Chinese names, keep the original English spelling if uncertain about translation**)",
  "structured_fact_table": {{
    "author_affiliation": "...(作者及所属机构/大学/研究院。**关键规则**：中文人名必须保留中文，如"暨南大学经济与社会研究院薄诗雨教授"；对于不确定翻译的中文人名，在英文摘要中保留英文形式)",
    "research_question": "...(研究问题)",
    "core_findings": [
      {{
        "finding": "...(核心发现点，用中文描述)",
        "source_snippet": "...(原文相关片段，保持原文语言不翻译，尽可能包含关键数据如百分比、具体数值等)",
        "data_points": "...(关键数据：如回归系数、显著性水平、百分比变化等，保留原文表达)"
      }}
    ],
    "mechanism_explanation": "...(机制解释)"
  }}
}}

要求：
1) 禁止编造，保留原文关键数据。
2) source_snippet必须是原文片段，不要翻译，保持原语言。
3) 核心发现至少包含2-3个，每个都要有原文支撑和具体数据。
4) ⚠️ 严格控制字数：中文摘要{min_chars_zh}-{max_chars_zh}字，英文摘要{min_words_en}-{max_words_en}词（这是根据{duration_target_sec}秒目标时长计算的）。
5) **人名处理规则（严格遵守）**：
   - 中文摘要和author_affiliation字段：必须使用中文人名（如"薄诗雨"、"王祎"）
   - 英文摘要：对于不确定如何翻译的中文人名，保留英文原文（如"Shiyu Bo"、"Yi Wang"）
   - 绝对不要在中文部分使用英文人名或拼音

文章全文：
{doc_text}
"""
    
    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]


def build_quick_brief_prompt(doc_text: str, doc_id: str) -> List[Dict[str, str]]:
    """
    构建 QuickBrief Prompt（多篇模式中的单篇要点提取）
    
    Args:
        doc_text: 文档文本
        doc_id: 文档ID（用于追踪）
    
    Returns:
        Prompt messages
    """
    system_prompt = """你是研究内容编辑助手。目标是为短视频口播快速提炼要点。速度优先，避免编造。若不确定数字/年份，不要硬写。"""
    
    user_prompt = f"""请阅读以下文章全文，输出 5-8 条"可用于口播的要点"，每条尽量短，包含：研究主题/关键结论/政策含义/可讲的例子或数字（仅在原文明确时写）。

输出严格 JSON 格式：
{{
  "doc_id": "{doc_id}",
  "title_guess": "...(从文中提取的标题)",
  "bullets": [
    "要点1: ...",
    "要点2: ...",
    "要点3: ...",
    "...(5-8条)"
  ]
}}

文章全文：
{doc_text}
"""
    
    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]


def build_final_script_prompt(
    briefs_list: List[Dict[str, Any]],
    speaker_name: str,
    speaker_affiliation: str,
    duration_target_sec: int,
    topic_hint: str = '',
    include_figure_placeholders: bool = True
) -> List[Dict[str, str]]:
    """
    构建最终口播稿 Prompt
    
    Args:
        briefs_list: 所有文档的 QuickBrief 列表
        speaker_name: 主播姓名
        speaker_affiliation: 主播单位
        duration_target_sec: 目标时长（秒）
        topic_hint: 话题提示（可选）
        include_figure_placeholders: 是否包含 Figure 占位
    
    Returns:
        Prompt messages
    """
    system_prompt = """你是 VoxChina 短视频专题口播稿写作助手。速度优先，但禁止明显胡编。

规则：
1) 仅使用输入的 bullets/材料写作；不确定的数字/年份不要硬写。
2) 输出结构必须严格包含：标题、自我介绍两行、点题段落、2-4个主题段落（每段带小标题）、Figure占位（如启用）、结尾关注句。
3) 语言口播友好：短句、转折清晰、信息密度高但不学术堆砌。
4) ⚠️ 【字数控制是最高优先级】必须严格按照目标字数范围生成内容，超出或不足都会导致口播时间不符合要求。这是硬性要求！"""
    
    # 计算建议字数范围（根据目标时长）
    min_chars = int(duration_target_sec * 5.5)  # 约 5.5 字/秒（含停顿）
    max_chars = int(duration_target_sec * 9)    # 约 9 字/秒（较快）
    
    # 格式化所有文档的 bullets
    briefs_json = json.dumps(briefs_list, ensure_ascii=False, indent=2)
    
    # 构建 topic_hint 说明
    topic_section = ""
    if topic_hint:
        topic_section = f"- 话题提示: {topic_hint}（可参考此提示来组织主题，但最终主题必须基于文章实际内容提取）"
    else:
        topic_section = "- 根据文章内容自行提取2-4个核心主题"
    
    # Figure 占位说明
    figure_section = ""
    if include_figure_placeholders:
        figure_section = """
【Figure 占位格式（独立一行，必须至少两处）】
Figure 1. [描述与第一个关键点相关的数据/图表]
Figure 2. [描述与第二个关键点相关的数据/图表]
（可以有更多 Figure，根据内容需要）"""
    
    user_prompt = f"""请根据以下输入生成最终口播稿。输出严格 JSON 格式：
{{
  "mode": "MULTI_SCRIPT",
  "episode_title": "...(节目标题，不超过28字)",
  "script_text": "完整口播稿，按自然段换行，必须包含所有结构要素"
}}

【⚠️⚠️⚠️ 字数要求（这是最高优先级，必须100%严格遵守）】：
- 🎯 目标时长: {duration_target_sec}秒
- 🎯 要求字数范围: {min_chars}–{max_chars}字（必须在此范围内，不能超出！）
- ✅ 时长较短时（<180秒）：精简内容，每段1-2个核心点，严格控制字数在 {min_chars}-{max_chars} 字
- ✅ 时长较长时（≥180秒）：可以展开细节，每段2-3个核心点，但仍需控制字数在 {min_chars}-{max_chars} 字
- ❌ 字数超出或不足都会导致口播时间不符合要求
- 💡 建议：先构思内容框架，计算各部分字数分配，确保总字数在要求范围内

【输入参数】：
- speaker_name: {speaker_name}
- speaker_affiliation: {speaker_affiliation}
- duration_target_sec: {duration_target_sec}秒（这决定了字数范围：{min_chars}-{max_chars}字）
- include_figure_placeholders: {include_figure_placeholders}

【必须使用的固定开场句（必须完整出现在 script_text 开头部分）】
大家好，我是{speaker_affiliation}的{speaker_name}。
很高兴在VOXCHINA和大家见面。

【点题段要求】
在自我介绍后，用1段话简要点题，介绍本期将要讨论的2-4个主题维度。
{topic_section}

【主体内容结构】
根据输入的多篇文章内容，提取2-4个核心主题，每个主题一段：

第一个主题：[根据文章内容提取的小标题]
[1-4个自然段，整合相关文章的要点、数据、结论]

第二个主题：[根据文章内容提取的小标题]
[1-4个自然段，整合相关文章的要点、数据、结论]

第三个主题（如适用）：[根据文章内容提取的小标题]
[1-4个自然段，整合相关文章的要点、数据、结论]

第四个主题（如适用）：[根据文章内容提取的小标题]
[1-4个自然段，整合相关文章的要点、数据、结论]

⚠️ 重要：
- 主题小标题必须从实际文章内容中提取，不要使用固定模板
- 主题数量（2-4个）和每个主题的段落数量要根据目标字数灵活调整
- 时长较短时（如100秒）可能只需要2个主题，每个主题1-2段
- 时长较长时（如1500秒）需要3-4个主题，每个主题3-4段
- 字数控制是最高优先级！
{figure_section}

【必须包含的结尾句（必须完整出现在 script_text 结尾）】
欢迎继续关注 VOXCHINA，我们下期再见！

输入材料（多篇 bullets）：
{briefs_json}

请严格按照上述结构输出 JSON。
"""
    
    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]


if __name__ == "__main__":
    # 测试 Prompt 构建
    print("=== 测试 SINGLE_SUMMARY Prompt ===")
    messages = build_single_summary_prompt("这是一篇测试文章...")
    print(f"System: {messages[0]['content'][:100]}...")
    print(f"User: {messages[1]['content'][:200]}...")
    
    print("\n=== 测试 QUICK_BRIEF Prompt ===")
    messages = build_quick_brief_prompt("测试文档内容...", "doc_0")
    print(f"User prompt 包含 doc_id: {'doc_0' in messages[1]['content']}")
    
    print("\n=== 测试 FINAL_SCRIPT Prompt ===")
    test_briefs = [
        {'doc_id': 'doc_0', 'title_guess': '测试标题1', 'bullets': ['要点1', '要点2']},
        {'doc_id': 'doc_1', 'title_guess': '测试标题2', 'bullets': ['要点3', '要点4']}
    ]
    messages = build_final_script_prompt(
        briefs_list=test_briefs,
        speaker_name='测试主播',
        speaker_affiliation='测试机构',
        duration_target_sec=150
    )
    print(f"System: {messages[0]['content'][:100]}...")
    print(f"User prompt 长度: {len(messages[1]['content'])} 字符")
    print(f"包含固定开场句: {'很高兴在VOXCHINA和大家见面' in messages[1]['content']}")
