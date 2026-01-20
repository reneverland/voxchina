"""
口播稿生成 - 跨文档大纲服务（Plan阶段）
基于多个Evidence Ledgers生成结构化口播大纲
"""
import json
from typing import List, Dict, Any
from loguru import logger
from app.services.llm_service import llm_service


SYSTEM_PROMPT = """你是VoxChina口播稿策划专家。规则：
- 基于提供的Evidence Ledgers规划大纲；
- 大纲结构必须对齐示例：标题、主播介绍、hook、三段式、closing；
- 每段必须明确引用来源（doc_id + findings索引）；
- 输出JSON格式，结构严格。"""


PROMPT_EPISODE_OUTLINE = """请基于以下多篇文章的Evidence Ledgers，生成一期VoxChina口播稿大纲。

**风格参考**：
- 标题：简洁有力（≤28字）
- 主播介绍：2段（第1段自我介绍，第2段"很高兴在VOXCHINA和大家见面"）
- Hook：1-2句开场白（吸引注意）
- 核心论点：1句概括三维度
- 三段式结构：每段一个小标题，逻辑清晰
- 可插入Figure占位行（如需要）
- 结尾：总结 + "欢迎继续关注VOXCHINA，我们下期再见！"

**参数**：
- 主播姓名：{speaker_name}
- 主播机构：{speaker_affiliation}
- 期数主题：{episode_topic}（可选，不填则自动生成）
- 目标时长：{duration_target_sec}秒（每段约{sec_per_section}秒）

**Evidence Ledgers**：
{ledgers_json}

**输出JSON格式**（严格遵守）：
{{
  "episode_title": "≤28字",
  "speaker_intro": [
    "大家好，我是{speaker_name}，来自{speaker_affiliation}。",
    "很高兴在VOXCHINA和大家见面。"
  ],
  "hook": "1-2句开场白",
  "core_thesis": "1句核心论点（可不含具体数字）",
  "structure": [
    {{
      "section_id": "S1",
      "section_title": "第一个维度的小标题",
      "goal": "这一段讲清什么",
      "evidence_plan": [
        {{"doc_id": "doc1", "use_findings": [0, 2]}},
        {{"doc_id": "doc2", "use_findings": [1]}}
      ],
      "figure_placeholders": ["Figure 1. 图表描述（如需要）"],
      "target_length_chars": {sec_per_section_chars}
    }},
    {{
      "section_id": "S2",
      "section_title": "第二个维度的小标题",
      "goal": "...",
      "evidence_plan": [...],
      "figure_placeholders": [],
      "target_length_chars": {sec_per_section_chars}
    }},
    {{
      "section_id": "S3",
      "section_title": "第三个维度的小标题",
      "goal": "...",
      "evidence_plan": [...],
      "figure_placeholders": [],
      "target_length_chars": {sec_per_section_chars}
    }}
  ],
  "closing": "2-3句总结 + 关注引导"
}}

请直接返回JSON，不要添加任何解释："""


class ScriptOutlineService:
    """跨文档大纲服务"""
    
    def __init__(self):
        self.max_retries = 2
        self.default_duration = 150  # 默认150秒（2分30秒）
        self.chars_per_second = 4.5  # 口播速度：约4.5字/秒
    
    async def generate_outline(
        self,
        ledgers: List[Dict[str, Any]],
        speaker_name: str = "VoxChina主播",
        speaker_affiliation: str = "VoxChina团队",
        episode_topic: str = None,
        duration_target_sec: int = None,
        language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        生成跨文档大纲
        
        Args:
            ledgers: 多个文档的Evidence Ledgers
            speaker_name: 主播姓名
            speaker_affiliation: 主播机构
            episode_topic: 期数主题（可选）
            duration_target_sec: 目标时长（秒）
            language: 语言
            
        Returns:
            Episode Outline JSON
        """
        duration = duration_target_sec or self.default_duration
        
        # 计算每段目标长度
        # 总时长 - 标题介绍结尾（约30秒） = 主体时长
        main_duration = max(duration - 30, 90)
        sec_per_section = main_duration // 3
        sec_per_section_chars = int(sec_per_section * self.chars_per_second)
        
        # 准备ledgers JSON
        ledgers_json = json.dumps(ledgers, ensure_ascii=False, indent=2)
        
        prompt = PROMPT_EPISODE_OUTLINE.format(
            speaker_name=speaker_name,
            speaker_affiliation=speaker_affiliation,
            episode_topic=episode_topic or "（根据内容自动生成）",
            duration_target_sec=duration,
            sec_per_section=sec_per_section,
            sec_per_section_chars=sec_per_section_chars,
            ledgers_json=ledgers_json
        )
        
        for retry in range(self.max_retries + 1):
            try:
                response = await llm_service._generate_with_provider(
                    prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
                    timeout=120.0
                )
                
                # 清理response
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                outline = json.loads(response)
                
                # 验证结构
                required_fields = ["episode_title", "speaker_intro", "hook", "structure", "closing"]
                for field in required_fields:
                    if field not in outline:
                        raise ValueError(f"Missing required field: {field}")
                
                if len(outline["structure"]) != 3:
                    raise ValueError("Structure must have exactly 3 sections")
                
                logger.info(f"Generated outline: {outline['episode_title']}")
                return outline
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed for outline (retry {retry+1}): {e}")
                if retry < self.max_retries:
                    prompt += "\n\n注意：请确保返回纯JSON格式。"
                    continue
                else:
                    logger.error("Failed to generate outline after retries")
                    raise Exception(f"大纲生成失败: {str(e)}")
            except Exception as e:
                logger.error(f"Error generating outline: {e}")
                if retry < self.max_retries:
                    continue
                else:
                    raise


script_outline_service = ScriptOutlineService()

