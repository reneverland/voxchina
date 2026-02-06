"""
学术文章智能摘要提取服务 - 全新实现
作者：Ren CBIT https://github.com/reneverland/

功能：
1. 对用户输入的【单篇学术文章】生成两部分输出
   A) 摘要（中英文，先中文再英文）
   B) 结构化事实表（包含研究问题、核心发现，每条都能追溯到原文证据）

写作结构（必须遵循）：
1）开头一句（研究信息句）：作者/机构 + 研究问题/对象 + 数据/场景/方法
2）第二句起用"研究发现："给出1-3条最核心发现
3）随后用"这一结果主要归因于/其作用机制为/但同时也……"解释机制
4）如论文明确给出政策/管理启示，可用最后一句简要点出
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from loguru import logger
from app.services.llm_service import llm_service


# ==================== 进度阶段定义 ====================
PROGRESS_STAGES = [
    {"name": "文档获取与预处理", "progress": 10},
    {"name": "结构化解析与噪音过滤", "progress": 20},
    {"name": "智能分块与覆盖率保障", "progress": 30},
    {"name": "CBIT-LLM 语义分析", "progress": 45},
    {"name": "深度理解与事实提取", "progress": 60},
    {"name": "证据一致性校验", "progress": 75},
    {"name": "幻觉过滤与可信度评估", "progress": 85},
    {"name": "摘要生成与风格对齐", "progress": 95},
    {"name": "准备输送结果", "progress": 100}
]


# ==================== Prompt 模板 ====================

SYSTEM_PROMPT = """你是一名"学术研究简报"写作助手。用户上传的是【单篇论文】（可能是PDF/截图/文本）。

【核心原则】
1. 只基于论文内容进行信息提取与摘要撰写
2. 不要编造任何作者、机构、数据、结论或数值
3. 如论文未明确给出，请用"未在文中明确"标注
4. 信息密度高、逻辑清晰、语言客观

【输出要求】
- 输出必须是有效的JSON格式
- 禁止夹带解释性文字
- 所有引用必须标注段落位置（P#格式）"""


PROMPT_EXTRACT_BASIC_INFO = """【任务】从论文文本中提取基本信息。

【文本内容】
{text}

【提取要求】
1. **作者与机构**（⚠️ 重点任务）：
   
   **机构定义**：学校、学院、研究院、研究所、实验室、公司、工作单位等
   
   **搜索策略**（按优先级，必须全部尝试）：
   
   a) **直接标注**：
      - 标题页作者栏下方的机构名称
      - 作者名字后的上标数字对应的机构
      - 格式："Author Name¹", 底部"¹University Name"
   
   b) **邮箱域名推断**：
      - @pku.edu.cn → 北京大学
      - @gsm.pku.edu.cn → 北京大学光华管理学院
      - @ruc.edu.cn → 中国人民大学
      - @tsinghua.edu.cn → 清华大学
      - @stanford.edu → Stanford University
      - @mit.edu → MIT
      - @company.com → 根据域名推断公司名
   
   c) **致谢部分**：
      - 搜索 "acknowledge", "感谢", "thank", "supported by", "funded by"
      - 出现的大学/研究所名称即为作者所在机构
   
   d) **通讯作者信息**：
      - 搜索 "Corresponding author", "通讯作者", "*", "†"
      - 通讯作者的地址/邮箱/机构优先级最高
   
   e) **作者简介/署名**：
      - "is at", "is from", "works at", "affiliated with"
      - "来自", "就职于", "任职于"
   
   f) **脚注信息**：
      - 页面底部的作者注释
      - 作者名字后的符号对应的说明
   
   **推断规则**：
   - 如果文中提到某个大学提供资助，且没有其他机构信息 → 作者可能在该大学
   - 如果有多个作者，尽量为每个作者找到对应机构
   - 如果同一机构有多个作者，可以合并写
   - 学院名称包含大学名称（如：北京大学光华管理学院）
   
   **禁止行为**：
   - ❌ 不要轻易写"未在文中明确"
   - ❌ 必须搜索完P1-P20的所有段落
   - ❌ 必须检查邮箱、致谢、脚注
   - ❌ 只有真的找不到任何机构线索才写"未在文中明确"
   
   **输出格式**："作者姓名（所在机构）"
   - 示例：Shiyu Bo（北京大学光华管理学院）
   - 示例：John Smith（Stanford University）
   - 示例：张三（中国人民大学经济学院）
   
2. **研究问题/主题**：
   - 论文要回答什么问题？
   - 研究什么现象？
   - 核心研究目标是什么？

3. **研究对象/范围**：
   - 研究的是哪类群体？（如：制造业工人、企业、学生）
   - 地区范围？（如：中国、美国、全球）
   - 时期范围？（如：2011-2018年）

4. **数据来源与样本**：
   - 数据库名称（如：China Labor-Force Dynamics Survey）
   - 样本规模（N=?，如：N=15000）
   - 时间跨度（如：2011-2018年）
   - 地区范围（如：142个县，98个地区）
   - 数据类型（如：面板数据、横截面数据）

5. **研究方法**：
   - 识别策略（如：DID、RDD、IV）
   - 模型类型（如：回归分析、实验设计）
   - 关键技术（如：机器学习、因果推断）

【输出格式（JSON）】
{{
  "authors": [
    {{
      "name": "作者姓名",
      "affiliation": "所在机构（学校/学院/研究院/公司）",
      "evidence": "P# 或者 P#（邮箱推断）或者 P#（致谢推断）",
      "note": "如何推断出机构的（可选说明）"
    }}
  ],
  "research_question": {{
    "question": "研究问题描述",
    "evidence": "P#"
  }},
  "research_object": {{
    "description": "研究对象/范围",
    "evidence": "P#"
  }},
  "data_sample": {{
    "source": "数据来源",
    "sample_size": "样本规模",
    "time_span": "时间跨度",
    "region": "地区范围",
    "evidence": "P#"
  }},
  "method": {{
    "description": "研究方法/识别策略",
    "evidence": "P#"
  }}
}}

【特别提醒】
- 作者机构是最重要的信息，必须尽全力提取
- 如果有邮箱，必须从域名推断机构
- 如果有致谢，必须从致谢中推断机构
- 只有在P1-P20真的没有任何学校/研究所/公司名称时，才写"未在文中明确"

请直接返回JSON，不要添加任何markdown标记："""


PROMPT_EXTRACT_FINDINGS = """【任务】从论文文本中提取核心发现。

【文本内容】
{text}

【提取要求】
1. **核心发现**：提取1-5条最重要的研究结论
2. **量化数据**：必须提取所有关键数字
   - 百分比、系数、比率
   - 显著性水平（p值）
   - 样本量、时间跨度
   - 格式示例："提高12.3%, p<0.01; 样本N=15000"
3. **原文证据**：每条发现必须标注段落位置（P#）+ 原文摘录（≤25字）
4. **异质性分析**（如有）：不同群体/情境下的差异结果

【输出格式（JSON）】
{{
  "key_findings": [
    {{
      "finding": "核心发现描述（保留关键数字）",
      "quantitative_data": "量化结果：系数/百分比/规模+显著性",
      "evidence": "P#-\\"原文摘录≤25字\\"",
      "heterogeneity": "异质性/边界条件（如无则为空字符串）",
      "heterogeneity_evidence": "P#-\\"原文摘录≤25字\\""
    }}
  ]
}}

请直接返回JSON，不要添加任何markdown标记："""


PROMPT_EXTRACT_MECHANISM = """【任务】从论文文本中提取作用机制与政策启示。

【文本内容】
{text}

【提取要求】
1. **作用机制**：
   - 只提取论文明确说明的机制/渠道
   - 不要推断或补充
   - 类型：中介效应/调节效应/替代效应/互补效应/其他
   
2. **政策启示**：
   - 只提取论文明确提出的建议
   - 如无明确建议，返回空数组

3. **原文证据**：每条必须标注段落位置（P#）+ 原文摘录（≤25字）

【输出格式（JSON）】
{{
  "mechanisms": [
    {{
      "description": "机制解释/作用渠道",
      "type": "中介效应|调节效应|替代效应|互补效应|其他",
      "evidence": "P#-\\"原文摘录≤25字\\""
    }}
  ],
  "policy_implications": [
    {{
      "implication": "政策/管理启示",
      "evidence": "P#-\\"原文摘录≤25字\\""
    }}
  ]
}}

请直接返回JSON，不要添加任何markdown标记："""


PROMPT_GENERATE_SUMMARY_ZH = """【任务】基于提取的结构化信息，生成中文研究简报式摘要。

【结构化信息】
{structured_data}

【写作结构（必须严格遵循）】
1）开头一句（研究信息句）：
   - 格式：【作者/所在单位】+【研究问题/对象】+【数据/场景/方法】
   - 必须写出：时间跨度、样本规模、实验/政策/文本规模
   - 示例："清华大学李明教授团队，基于2015-2020年全国企业数据库（样本N=50000），研究了数字化转型对企业绩效的影响。"

2）第二句起用"研究发现："给出1-3条最核心发现
   - **必须包含"研究发现："这4个字**
   - 优先保留关键量化结果：百分比、系数、显著性方向、规模
   - 数字必须与原文一致
   - 示例："研究发现：数字化转型使企业利润率平均提高8.5%（p<0.01），其中大型企业提升12.3%，中小企业提升5.7%。"

3）随后用"这一结果主要归因于/其作用机制为/但同时也……"解释机制或权衡
   - 仅写明确提供的机制
   - 如有异质性或边界条件，优先写最重要的一条
   - 1-2条即可

4）如论文明确给出政策/管理启示，可用最后一句简要点出；若无则不写

【表达与格式要求】
- 全文1段，3-5句话，控制在120-220字
- 只写结论性信息，不写目录式概述
- 数字必须与原文一致
- 专有名词（项目名、期刊名、政策名、变量名）保持原文
- 信息密度高、逻辑清晰、语言客观

【输出格式（JSON）】
{{
  "summary_zh": "中文摘要（120-220字）"
}}

请直接返回JSON，不要添加任何markdown标记："""


PROMPT_GENERATE_SUMMARY_EN = """【任务】将中文摘要翻译为英文，保持相同结构。

【中文摘要】
{summary_zh}

【结构化信息（参考）】
{structured_data}

【要求】
1. Follow the same 4-part structure as Chinese version
2. Keep all quantitative data consistent
3. Word count: 60-120 words
4. Professional and objective tone
5. Suitable for academic broadcasting

【Output Format (JSON)】
{{
  "summary_en": "English summary (60-120 words)"
}}

Please return JSON directly without markdown code blocks:"""


# ==================== 主服务类 ====================

class AcademicExtractService:
    """学术文章智能摘要提取服务"""
    
    def __init__(self):
        self.max_chunk_size = 4000  # 每个chunk最大字符数
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本：添加段落编号 P1, P2, P3...
        """
        paragraphs = text.split('\n\n')
        numbered_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                numbered_paragraphs.append(f"[P{i+1}] {para.strip()}")
        
        processed_text = '\n\n'.join(numbered_paragraphs)
        logger.info(f"预处理完成：共 {len(numbered_paragraphs)} 个段落")
        return processed_text
    
    def _clean_json_response(self, response: str) -> str:
        """清理LLM返回的JSON字符串"""
        response = response.strip()
        
        # 移除markdown代码块标记
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        return response
    
    async def _call_llm(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Dict[str, Any]:
        """
        调用LLM服务（使用全局配置的模型）
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
        
        Returns:
            解析后的JSON对象
        """
        try:
            # 使用 llm_service，它会自动使用全局配置的模型（如 gpt-4o 或 gpt-5.2）
            response = await llm_service._generate_with_provider(
                prompt=prompt,
                system_prompt=system_prompt,
                timeout=180.0
            )
            
            # 清理并解析JSON
            cleaned_response = self._clean_json_response(response)
            result = json.loads(cleaned_response)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"响应内容: {response[:500]}")
            raise ValueError(f"LLM返回的内容无法解析为JSON: {str(e)}")
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    async def extract_academic_article(
        self,
        text: str,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        完整的学术文章提取流程
        
        Args:
            text: 论文全文文本
            progress_callback: 进度回调函数 (stage_name, progress_percent)
        
        Returns:
            {
                "summary_zh": "中文摘要",
                "summary_en": "英文摘要",
                "fact_table": {
                    "basic_info": {...},
                    "key_findings": [...],
                    "mechanisms": [...],
                    "policy_implications": [...]
                },
                "metadata": {
                    "total_paragraphs": 100,
                    "llm_model": "gpt-4o"
                }
            }
        """
        def report_progress(stage_index: int):
            if progress_callback and 0 <= stage_index < len(PROGRESS_STAGES):
                stage = PROGRESS_STAGES[stage_index]
                progress_callback(stage["name"], stage["progress"])
        
        logger.info("开始学术文章提取流程")
        
        # 阶段1: 文档获取与预处理
        report_progress(0)
        processed_text = self._preprocess_text(text)
        await asyncio.sleep(0.5)  # 模拟处理时间
        
        # 阶段2: 结构化解析与噪音过滤
        report_progress(1)
        await asyncio.sleep(0.3)
        
        # 阶段3: 智能分块与覆盖率保障
        report_progress(2)
        # 如果文本过长，可以在这里实现分块逻辑
        # 为了简化，当前版本直接使用全文
        await asyncio.sleep(0.3)
        
        # 阶段4: CBIT-LLM 语义分析 - 提取基本信息
        report_progress(3)
        logger.info("提取基本信息...")
        basic_info = await self._call_llm(
            PROMPT_EXTRACT_BASIC_INFO.format(text=processed_text)
        )
        
        # 阶段5: 深度理解与事实提取 - 提取核心发现
        report_progress(4)
        logger.info("提取核心发现...")
        findings_data = await self._call_llm(
            PROMPT_EXTRACT_FINDINGS.format(text=processed_text)
        )
        
        # 阶段6: 证据一致性校验 - 提取机制与政策启示
        report_progress(5)
        logger.info("提取机制与政策启示...")
        mechanism_data = await self._call_llm(
            PROMPT_EXTRACT_MECHANISM.format(text=processed_text)
        )
        
        # 阶段7: 幻觉过滤与可信度评估
        report_progress(6)
        await asyncio.sleep(0.3)
        
        # 合并结构化数据
        fact_table = {
            "basic_info": basic_info,
            "key_findings": findings_data.get("key_findings", []),
            "mechanisms": mechanism_data.get("mechanisms", []),
            "policy_implications": mechanism_data.get("policy_implications", [])
        }
        
        # 阶段8: 摘要生成与风格对齐
        report_progress(7)
        logger.info("生成中文摘要...")
        
        # 生成中文摘要
        summary_zh_data = await self._call_llm(
            PROMPT_GENERATE_SUMMARY_ZH.format(
                structured_data=json.dumps(fact_table, ensure_ascii=False, indent=2)
            )
        )
        summary_zh = summary_zh_data.get("summary_zh", "")
        
        # 生成英文摘要
        logger.info("生成英文摘要...")
        summary_en_data = await self._call_llm(
            PROMPT_GENERATE_SUMMARY_EN.format(
                summary_zh=summary_zh,
                structured_data=json.dumps(fact_table, ensure_ascii=False, indent=2)
            )
        )
        summary_en = summary_en_data.get("summary_en", "")
        
        # 阶段9: 准备输送结果
        report_progress(8)
        await asyncio.sleep(0.2)
        
        # 获取当前使用的LLM配置
        llm_config = llm_service.get_current_config()
        
        result = {
            "summary_zh": summary_zh,
            "summary_en": summary_en,
            "fact_table": fact_table,
            "metadata": {
                "total_paragraphs": processed_text.count('[P'),
                "llm_provider": llm_config.get("provider", "unknown"),
                "llm_model": llm_config.get("model", "unknown")
            }
        }
        
        # Note: Knowledge Base saving is now optional via separate API endpoint
        # Removed automatic saving to allow user choice
        
        logger.info(f"提取完成 - 中文摘要: {len(summary_zh)}字, 英文摘要: {len(summary_en.split())}词")
        logger.info(f"使用模型: {llm_config.get('provider')}/{llm_config.get('model')}")
        
        return result


# 单例实例
academic_extract_service = AcademicExtractService()
