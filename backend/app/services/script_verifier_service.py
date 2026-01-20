"""
口播稿生成 - 事实核验服务（Verify阶段）
核对claim_checklist与ledgers的一致性，自动补丁修复
"""
import json
from typing import List, Dict, Any, Tuple
from loguru import logger
from app.services.llm_service import llm_service


SYSTEM_PROMPT = """你是VoxChina口播稿事实核验专家。规则：
- 严格核对每条claim是否能在ledger的evidence.quote中找到支持；
- 对UNSUPPORTED/OVERSTATED的claim，必须给出DELETE或REPLACE方案；
- 输出JSON格式，包含issues列表和patched_script。"""


PROMPT_VERIFY_CLAIMS = """请对以下口播稿进行事实一致性核验。

**原始稿件**：
{final_script}

**Claim Checklist**（待核验列表）：
{claim_checklist_json}

**证据台账**（唯一真实来源）：
{ledgers_json}

**核验任务**：
逐条检查claim_checklist中的每个claim：
1. 根据source字段（如"doc1:key_findings[0]"）定位到ledgers中的对应条目；
2. 检查claim是否与该条目的evidence.quote一致（数字、方向、对象、因果）；
3. 如果不一致或无法找到支持，标记为UNSUPPORTED或OVERSTATED；
4. 给出修复方案：DELETE（删除该句）或REPLACE（替换为更保守的表述）。

**输出JSON格式**（严格遵守）：
{{
  "verdict": "PASS|FAIL",
  "issues": [
    {{
      "severity": "critical|major|minor",
      "location": "S1段落2",
      "claim": "原稿中的具体陈述",
      "status": "UNSUPPORTED|OVERSTATED|AMBIGUOUS",
      "why": "不一致原因（如：数字不匹配、因果关系过强等）",
      "fix": {{
        "action": "DELETE|REPLACE",
        "replacement_text": "修订后的文本（如action=REPLACE）",
        "replacement_source": "新的source（如有更合适的证据）"
      }}
    }}
  ],
  "patched_script": "修订后的完整口播稿（已应用所有fix）"
}}

**通过标准**：
- verdict=PASS: 所有critical/major issues为0
- verdict=FAIL: 存在critical/major issues

请直接返回JSON，不要添加任何解释："""


class ScriptVerifierService:
    """事实核验服务"""
    
    def __init__(self):
        self.max_retries = 2
    
    def _lookup_evidence(
        self,
        source: str,
        ledgers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        根据source字符串查找对应的evidence
        
        Args:
            source: 如"doc1:key_findings[0]"
            ledgers: 证据台账列表
            
        Returns:
            对应的evidence条目，如果找不到返回None
        """
        try:
            # 解析source: "doc1:key_findings[0]"
            parts = source.split(":")
            if len(parts) != 2:
                return None
            
            doc_id = parts[0]
            path = parts[1]  # "key_findings[0]"
            
            # 查找ledger
            ledger = next((l for l in ledgers if l.get("doc_id") == doc_id), None)
            if not ledger:
                return None
            
            # 解析路径：key_findings[0]
            if "[" in path and "]" in path:
                field_name = path[:path.index("[")]
                idx_str = path[path.index("[")+1:path.index("]")]
                idx = int(idx_str)
                
                field_data = ledger.get(field_name, [])
                if idx < len(field_data):
                    return field_data[idx]
            
            return None
        except Exception as e:
            logger.warning(f"Failed to lookup evidence for source '{source}': {e}")
            return None
    
    async def verify_script(
        self,
        final_script: str,
        claim_checklist: List[Dict[str, Any]],
        ledgers: List[Dict[str, Any]]
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        核验口播稿事实一致性
        
        Args:
            final_script: 原始稿件
            claim_checklist: claim列表
            ledgers: 证据台账
            
        Returns:
            (verdict, patched_script, issues)
        """
        claim_checklist_json = json.dumps(claim_checklist, ensure_ascii=False, indent=2)
        ledgers_json = json.dumps(ledgers, ensure_ascii=False, indent=2)
        
        prompt = PROMPT_VERIFY_CLAIMS.format(
            final_script=final_script,
            claim_checklist_json=claim_checklist_json,
            ledgers_json=ledgers_json
        )
        
        for retry in range(self.max_retries + 1):
            try:
                response = await llm_service._generate_with_provider(
                    prompt=f"{SYSTEM_PROMPT}\n\n{prompt}",
                    timeout=180.0
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
                if "verdict" not in result or "patched_script" not in result:
                    raise ValueError("Missing required fields in verify result")
                
                verdict = result["verdict"]
                patched_script = result["patched_script"]
                issues = result.get("issues", [])
                
                # 统计issues
                critical_count = sum(1 for i in issues if i.get("severity") == "critical")
                major_count = sum(1 for i in issues if i.get("severity") == "major")
                minor_count = sum(1 for i in issues if i.get("severity") == "minor")
                
                logger.info(
                    f"Verification {verdict}: "
                    f"{critical_count} critical, {major_count} major, {minor_count} minor issues"
                )
                
                return verdict, patched_script, issues
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed for verification (retry {retry+1}): {e}")
                if retry < self.max_retries:
                    prompt += "\n\n注意：请确保返回纯JSON格式。"
                    continue
                else:
                    logger.error("Failed to verify script after retries")
                    # 如果核验失败，返回原稿
                    return "FAIL", final_script, [{
                        "severity": "critical",
                        "location": "核验系统",
                        "claim": "核验过程失败",
                        "status": "UNSUPPORTED",
                        "why": f"JSON解析错误: {str(e)}",
                        "fix": {"action": "DELETE", "replacement_text": ""}
                    }]
            except Exception as e:
                logger.error(f"Error verifying script: {e}")
                if retry < self.max_retries:
                    continue
                else:
                    return "FAIL", final_script, [{
                        "severity": "critical",
                        "location": "核验系统",
                        "claim": "核验过程失败",
                        "status": "UNSUPPORTED",
                        "why": str(e),
                        "fix": {"action": "DELETE", "replacement_text": ""}
                    }]


script_verifier_service = ScriptVerifierService()

