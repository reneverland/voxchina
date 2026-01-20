"""
口播稿生成 - 写作服务（Write阶段）
基于大纲和证据台账生成口播稿，同时生成claim_checklist
"""
import json
from typing import List, Dict, Any, Tuple
from loguru import logger
from app.services.llm_service import llm_service


SYSTEM_PROMPT = """你是VoxChina口播稿撰稿人。规则：
- 只能使用evidence_plan指定的ledger条目；
- 所有具体事实必须来自evidence.quote；
- 允许少量泛化引导句（不含具体数字/不含确定性因果）；
- 输出JSON格式，包含稿件文本和claim_checklist。"""


PROMPT_DRAFT_SCRIPT = """请基于以下大纲和证据台账，撰写完整的口播稿。

**大纲**：
{outline_json}

**证据台账**：
{ledgers_json}

**风格要求**：
- 语气：大众可听懂，但专业；短句为主；逻辑强（承接/转折清晰）；
- 口播节奏：适合口语表达，避免书面语；
- 段落长度：遵循大纲的target_length_chars；
- Figure占位：如大纲中有figure_placeholders，独立一行插入。

**输出JSON格式**（严格遵守）：
{{
  "final_script": "完整口播稿文本（按自然段换行）\\n\\n包含：\\n- 标题行（{episode_title}）\\n- 主播介绍（2段）\\n- Hook + 核心论点\\n- 三段式（每段以小标题开头）\\n- Figure占位行（如有）\\n- 结尾",
  "claim_checklist": [
    {{
      "section_id": "S1",
      "claims": [
        {{
          "claim": "具体事实陈述",
          "source": "doc1:key_findings[0]",
          "quote": "对应的evidence.quote"
        }}
      ]
    }},
    {{
      "section_id": "S2",
      "claims": [...]
    }},
    {{
      "section_id": "S3",
      "claims": [...]
    }}
  ]
}}

**硬性约束**：
- final_script中每条带事实的句子必须来自evidence_plan里指定的条目；
- claim_checklist中每个claim必须能在ledgers的evidence.quote中找到支持；
- 允许少量"泛化引导句"（如"政府在创新与治理间需平衡"），但不能带具体数字。

请直接返回JSON，不要添加任何解释："""


class ScriptWriterService:
    """口播稿写作服务"""
    
    def __init__(self):
        self.max_retries = 2
    
    def _build_evidence_context(
        self,
        section: Dict[str, Any],
        ledgers: List[Dict[str, Any]]
    ) -> str:
        """
        为某一段构建可用证据上下文
        
        Args:
            section: 大纲中的某一段
            ledgers: 所有证据台账
            
        Returns:
            该段可用的证据摘要
        """
        evidence_lines = []
        evidence_plan = section.get("evidence_plan", [])
        
        for plan_item in evidence_plan:
            doc_id = plan_item["doc_id"]
            use_findings = plan_item.get("use_findings", [])
            
            # 查找对应ledger
            ledger = next((l for l in ledgers if l.get("doc_id") == doc_id), None)
            if not ledger:
                continue
            
            key_findings = ledger.get("key_findings", [])
            for idx in use_findings:
                if idx < len(key_findings):
                    finding = key_findings[idx]
                    evidence_lines.append(
                        f"[{doc_id}:key_findings[{idx}]] "
                        f"{finding.get('finding', '')} "
                        f"(证据: {finding.get('evidence', {}).get('quote', '')})"
                    )
        
        return "\n".join(evidence_lines) if evidence_lines else "无可用证据"
    
    async def draft_script(
        self,
        outline: Dict[str, Any],
        ledgers: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        生成完整口播稿 + claim_checklist
        
        Args:
            outline: Episode Outline
            ledgers: 所有证据台账
            
        Returns:
            (final_script, claim_checklist)
        """
        outline_json = json.dumps(outline, ensure_ascii=False, indent=2)
        ledgers_json = json.dumps(ledgers, ensure_ascii=False, indent=2)
        
        prompt = PROMPT_DRAFT_SCRIPT.format(
            outline_json=outline_json,
            ledgers_json=ledgers_json,
            episode_title=outline.get("episode_title", "")
        )
        
        for retry in range(self.max_retries + 1):
            try:
                response = await llm_service._generate_with_provider(
                    prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
                    timeout=180.0  # 写作可能需要更长时间
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
                
                result = json.loads(response)
                
                # 验证结构
                if "final_script" not in result or "claim_checklist" not in result:
                    raise ValueError("Missing required fields in draft result")
                
                final_script = result["final_script"]
                claim_checklist = result["claim_checklist"]
                
                logger.info(f"Generated script: {len(final_script)} chars, {len(claim_checklist)} sections")
                return final_script, claim_checklist
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed for draft (retry {retry+1}): {e}")
                if retry < self.max_retries:
                    prompt += "\n\n注意：请确保返回纯JSON格式。"
                    continue
                else:
                    logger.error("Failed to draft script after retries")
                    raise Exception(f"口播稿写作失败: {str(e)}")
            except Exception as e:
                logger.error(f"Error drafting script: {e}")
                if retry < self.max_retries:
                    continue
                else:
                    raise


script_writer_service = ScriptWriterService()

