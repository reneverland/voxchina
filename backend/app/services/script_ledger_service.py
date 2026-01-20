"""
口播稿生成 - 证据台账服务（Map阶段）
从多个文档chunks提取结构化事实，生成Evidence Ledger
"""
import json
import asyncio
from typing import List, Dict, Any
from loguru import logger
from app.services.llm_service import llm_service


# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """你是严谨的VoxChina研究内容处理助手。规则：
- 只能基于输入文本与证据；禁止编造；
- 所有数字/年份/因果/比较必须能在证据quote中逐字找到；
- 需要给出证据quote（≤60字）与段落范围para_start~para_end；
- JSON输出必须可解析，无多余解释文字。"""


# ==================== Prompt A: Chunk Facts ====================
PROMPT_CHUNK_FACTS = """请从下列文本块中"只抽取客观事实"，输出JSON，格式必须符合：
{{
  "chunk_id": "{chunk_id}",
  "facts": [
    {{
      "type": "author_affiliation|research_question|data_sample|method|finding|mechanism|implication|caveat|figure",
      "claim": "可验证陈述（≤45字）",
      "numbers": ["2011-2018", "3.1%"],
      "evidence": {{
        "quote": "原文直接摘录（≤60字）",
        "para_range": "p{para_start}-p{para_end}"
      }}
    }}
  ]
}}

硬性约束：
- 只抽取本chunk里明确出现的信息；不允许推断；
- numbers只填chunk内出现的数字/年份/百分比/比例；
- evidence.quote必须是原文直接摘录（≤60字）；
- 作者信息必须提取实际机构全称+中文姓名+实际职称，禁止占位符。

文本块：
[Chunk {chunk_id}, 段落范围: p{para_start}-p{para_end}]
{chunk_text}

请直接返回JSON，不要添加任何解释："""


# ==================== Prompt B: Merge Ledger ====================
PROMPT_MERGE_LEDGER = """请将所有chunk的facts合并为一个Evidence Ledger JSON，字段必须完全一致：
{{
  "doc_id": "{doc_id}",
  "title": "文章标题",
  "authors": ["完整机构+姓名+职称，如：暨南大学经济与社会研究院薄诗雨教授"],
  "date_or_id": "日期标识（如从文件名提取的241106）",
  "one_sentence_claim": "一句话概括（≤40字）",
  "research_question": "研究问题",
  "method_and_data": {{
    "setting": "研究背景",
    "data_sources": ["数据来源"],
    "design": "DID/RCT/DDD/结构模型等",
    "time_range": "时间范围",
    "sample_size": "样本量（如有）"
  }},
  "key_findings": [
    {{
      "finding": "核心发现（≤45字）",
      "type": "descriptive|causal|mechanism|policy",
      "numbers": ["关键数字"],
      "evidence": {{
        "quote": "原文摘录（≤60字）",
        "para_range": "p..-p.."
      }}
    }}
  ],
  "mechanisms_or_channels": [
    {{
      "mechanism": "机制解释",
      "evidence": {{"quote": "...", "para_range": "p..-p.."}}
    }}
  ],
  "policy_implications": [
    {{
      "implication": "政策含义",
      "evidence": {{"quote": "...", "para_range": "p..-p.."}}
    }}
  ],
  "figures": [
    {{
      "figure_id": "Figure 1",
      "caption_or_topic": "图表主题",
      "para_range": "p..-p.."
    }}
  ],
  "risk_or_limitations": [
    {{
      "item": "局限性",
      "evidence": {{"quote": "...", "para_range": "p..-p.."}}
    }}
  ],
  "keywords": ["3-8个关键词"],
  "notes": "口径警告/外推限制/是否因果等"
}}

规则：
- 去重合并同义事实，保留信息量更大且证据更清晰的版本；
- key_findings至少保留最重要的2-4条（若文中有）；
- 每个finding/mechanism/implication必须有evidence.quote和para_range。

所有chunks的facts：
{all_chunk_facts}

请直接返回JSON，不要添加任何解释："""


class ScriptLedgerService:
    """证据台账服务"""
    
    def __init__(self):
        self.max_retries = 2
    
    async def extract_chunk_facts(
        self, 
        chunk: Dict[str, Any],
        task_id: str = None
    ) -> Dict[str, Any]:
        """
        从单个chunk提取事实（带重试机制）
        
        Args:
            chunk: {chunk_id, text, para_start, para_end}
            task_id: 任务ID（用于日志）
            
        Returns:
            chunk_facts JSON
        """
        chunk_id = chunk["chunk_id"]
        chunk_text = chunk["text"]
        para_start = chunk["para_start"]
        para_end = chunk["para_end"]
        
        prompt = PROMPT_CHUNK_FACTS.format(
            chunk_id=chunk_id,
            para_start=para_start,
            para_end=para_end,
            chunk_text=chunk_text
        )
        
        for retry in range(self.max_retries + 1):
            try:
                response = await llm_service._generate_with_provider(
                    prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
                    timeout=90.0
                )
                
                # 清理response（去除markdown标记）
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                chunk_facts = json.loads(response)
                
                # 验证结构
                if "chunk_id" not in chunk_facts or "facts" not in chunk_facts:
                    raise ValueError("Invalid chunk_facts structure")
                
                logger.info(f"Extracted {len(chunk_facts.get('facts', []))} facts from {chunk_id}")
                return chunk_facts
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed for {chunk_id} (retry {retry+1}/{self.max_retries+1}): {e}")
                if retry < self.max_retries:
                    prompt += "\n\n注意：请确保返回纯JSON格式，不要包含markdown标记或解释文字。"
                    continue
                else:
                    logger.error(f"Failed to extract facts from {chunk_id} after retries")
                    return {
                        "chunk_id": chunk_id,
                        "facts": [],
                        "error": str(e)
                    }
            except Exception as e:
                logger.error(f"Error extracting facts from {chunk_id}: {e}")
                return {
                    "chunk_id": chunk_id,
                    "facts": [],
                    "error": str(e)
                }
    
    async def merge_ledger(
        self,
        doc_id: str,
        all_chunk_facts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        合并所有chunk facts为统一Evidence Ledger
        
        Args:
            doc_id: 文档ID
            all_chunk_facts: 所有chunk_facts的列表
            
        Returns:
            Evidence Ledger JSON
        """
        prompt = PROMPT_MERGE_LEDGER.format(
            doc_id=doc_id,
            all_chunk_facts=json.dumps(all_chunk_facts, ensure_ascii=False, indent=2)
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
                
                ledger = json.loads(response)
                
                logger.info(f"Merged ledger for {doc_id}: {len(ledger.get('key_findings', []))} findings")
                return ledger
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed for ledger merge (retry {retry+1}): {e}")
                if retry < self.max_retries:
                    prompt += "\n\n注意：请确保返回纯JSON格式。"
                    continue
                else:
                    logger.error(f"Failed to merge ledger for {doc_id}")
                    raise Exception(f"Ledger合并失败: {str(e)}")
            except Exception as e:
                logger.error(f"Error merging ledger for {doc_id}: {e}")
                raise
    
    async def generate_document_ledger(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        task_id: str = None
    ) -> Dict[str, Any]:
        """
        为单个文档生成完整Evidence Ledger
        
        Args:
            doc_id: 文档ID
            chunks: 分块结果
            task_id: 任务ID
            
        Returns:
            完整的Evidence Ledger
        """
        logger.info(f"Generating ledger for document: {doc_id}")
        
        # 1. 并行提取所有chunk的facts
        tasks = [self.extract_chunk_facts(chunk, task_id) for chunk in chunks]
        all_chunk_facts = await asyncio.gather(*tasks)
        
        # 统计成功提取的chunks
        processed = sum(1 for cf in all_chunk_facts if cf.get("facts"))
        logger.info(f"Processed {processed}/{len(chunks)} chunks for {doc_id}")
        
        # 2. 合并为完整ledger
        ledger = await self.merge_ledger(doc_id, all_chunk_facts)
        
        # 3. 添加覆盖率元数据
        ledger["_metadata"] = {
            "total_chunks": len(chunks),
            "processed_chunks": processed,
            "coverage_rate": f"{processed/len(chunks)*100:.1f}%"
        }
        
        return ledger


script_ledger_service = ScriptLedgerService()

