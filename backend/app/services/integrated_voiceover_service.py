"""
VoxChina 多文献整合口播稿件策划服务 (Evidence-based Scriptwriter)
基于用户上传的多篇文档，生成可直接录制的短视频口播稿
"""
import uuid
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services.llm_service import llm_service
from app.services.document_parser_service import document_parser_service
from app.models.schemas import (
    IntegratedVoiceoverRequest,
    IntegratedVoiceoverResponse,
    EvidenceLedger,
    EvidenceFinding,
    VisualAssetLedger,
    VisualAsset,
    StyleProfile
)


class IntegratedVoiceoverService:
    """整合口播稿件生成服务"""
    
    def __init__(self):
        self.tasks = {}  # 任务存储 {task_id: task_data}
        
    async def create_task(
        self,
        request: IntegratedVoiceoverRequest,
        files: List[tuple]  # [(filename, file_content), ...]
    ) -> str:
        """
        创建新的口播稿生成任务
        
        Args:
            request: 请求参数
            files: 上传的文档列表
            
        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid.uuid4())
        
        # 初始化任务
        task_data = {
            "task_id": task_id,
            "status": "processing",
            "progress": 0,
            "current_step": "Step0",
            "request": request.dict(),
            "files": [],
            "parsed_docs": [],
            "style_profile": None,
            "evidence_ledger": [],
            "visual_asset_ledger": None,
            "structure": None,
            "script_review": None,
            "script_final": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存文件信息
        for filename, file_content in files:
            task_data["files"].append({
                "filename": filename,
                "size": len(file_content)
            })
        
        self.tasks[task_id] = task_data
        
        # 启动后台异步处理任务（不等待完成）
        import asyncio
        asyncio.create_task(self._process_task_wrapper(task_id, request, files))
        
        return task_id
    
    async def _process_task_wrapper(
        self,
        task_id: str,
        request: IntegratedVoiceoverRequest,
        files: List[tuple]
    ):
        """包装器：处理任务并捕获异常"""
        try:
            await self._process_task(task_id, request, files)
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task_data = self.tasks.get(task_id)
            if task_data:
                task_data["status"] = "failed"
                task_data["error"] = str(e)
                task_data["updated_at"] = datetime.now().isoformat()
    
    async def _process_task(
        self,
        task_id: str,
        request: IntegratedVoiceoverRequest,
        files: List[tuple]
    ):
        """处理任务的主流程"""
        task_data = self.tasks[task_id]
        
        try:
            # Step 0: 解析文档
            logger.info(f"Task {task_id}: Parsing documents...")
            task_data["current_step"] = "Parsing"
            task_data["progress"] = 5
            task_data["updated_at"] = datetime.now().isoformat()
            
            parsed_docs = []
            for filename, file_content in files:
                try:
                    parsed_doc = document_parser_service.parse_document(file_content, filename)
                    parsed_doc["doc_id"] = f"D{len(parsed_docs) + 1}"
                    parsed_docs.append(parsed_doc)
                except Exception as e:
                    logger.error(f"Failed to parse {filename}: {e}")
                    continue
            
            task_data["parsed_docs"] = parsed_docs
            task_data["progress"] = 10
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step 0: Style Profile
            logger.info(f"Task {task_id}: Generating Style Profile...")
            task_data["current_step"] = "Step0"
            style_profile = await self._generate_style_profile(request, parsed_docs)
            task_data["style_profile"] = style_profile
            task_data["progress"] = 20
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step A: Evidence Ledger
            logger.info(f"Task {task_id}: Building Evidence Ledger...")
            task_data["current_step"] = "StepA"
            evidence_ledger = await self._build_evidence_ledger(parsed_docs, request.topic_hint)
            task_data["evidence_ledger"] = evidence_ledger
            task_data["progress"] = 35
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step A2: Visual Asset Ledger
            logger.info(f"Task {task_id}: Building Visual Asset Ledger...")
            task_data["current_step"] = "StepA2"
            visual_asset_ledger = await self._build_visual_asset_ledger(parsed_docs, evidence_ledger)
            task_data["visual_asset_ledger"] = visual_asset_ledger
            task_data["progress"] = 50
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step B: Structure Selector
            logger.info(f"Task {task_id}: Selecting Structure...")
            task_data["current_step"] = "StepB"
            structure = await self._select_structure(
                request.topic_hint,
                evidence_ledger,
                visual_asset_ledger,
                style_profile,
                request.style_preference
            )
            task_data["structure"] = structure
            task_data["progress"] = 65
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step C: Script Review Version
            logger.info(f"Task {task_id}: Generating Script (Review Version)...")
            task_data["current_step"] = "StepC"
            script_review = await self._generate_script_review(
                request,
                style_profile,
                evidence_ledger,
                visual_asset_ledger,
                structure
            )
            task_data["script_review"] = script_review
            task_data["progress"] = 85
            task_data["updated_at"] = datetime.now().isoformat()
            
            # Step D: Script Final Version
            logger.info(f"Task {task_id}: Generating Script (Final Version)...")
            task_data["current_step"] = "StepD"
            script_final = await self._generate_script_final(script_review)
            task_data["script_final"] = script_final
            task_data["progress"] = 100
            task_data["status"] = "completed"
            task_data["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Task {task_id}: Completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} processing failed: {e}")
            task_data["status"] = "failed"
            task_data["error"] = str(e)
            task_data["updated_at"] = datetime.now().isoformat()
            raise
    
    async def _generate_style_profile(
        self,
        request: IntegratedVoiceoverRequest,
        parsed_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Step 0: 生成风格配置"""
        
        # 构建文档概览
        docs_overview = "\n\n".join([
            f"文档{doc['doc_id']}: {doc['title']}\n段落数: {doc['total_paragraphs']}"
            for doc in parsed_docs
        ])
        
        prompt = f"""
你是VoxChina口播稿风格分析专家。请根据以下信息，确定本次口播稿的风格配置。

主题提示: {request.topic_hint}
文档概览:
{docs_overview}

请输出以下内容（JSON格式）:
{{
    "enable_vox_intro": {str(request.include_vox_intro).lower()},
    "main_structure": "S1/S2/S3/S4之一",
    "figure_style": "A或B",
    "rules": ["规则1", "规则2", ...]
}}

结构说明:
- S1: 三维度/三主线（适合多角度分析）
- S2: 时间线/阶段推进（适合历史演进）
- S3: 现状—机制—对策（适合政策分析）
- S4: 机制链条（适合因果分析）

图表风格:
- A: 独立行展示（图/表 + 标题 + 要点）
- B: 正文内嵌（〔画面：asset_id（标题）— 要点〕）

规则示例:
- "每段必须有证据支撑"
- "数字必须带单位和时间口径"
- "禁止外推和主观推断"
"""
        
        response = await llm_service._generate_with_provider(
            prompt=prompt,
            timeout=120.0
        )
        
        try:
            # 尝试解析JSON
            style_profile = json.loads(response)
        except:
            # 如果解析失败，使用默认配置
            style_profile = {
                "enable_vox_intro": request.include_vox_intro,
                "main_structure": request.style_preference or "S1",
                "figure_style": "A",
                "rules": [
                    "只使用Evidence Ledger中存在的事实",
                    "数字必须带单位与时间口径",
                    "每段末尾加证据标注",
                    "图表必须来自文档",
                    "禁止外推和脑补"
                ]
            }
        
        return style_profile
    
    async def _build_evidence_ledger(
        self,
        parsed_docs: List[Dict[str, Any]],
        topic_hint: str
    ) -> List[Dict[str, Any]]:
        """Step A: 构建文字证据台账"""
        
        evidence_ledger = []
        
        for doc in parsed_docs:
            doc_id = doc["doc_id"]
            title = doc["title"]
            
            # 提取段落文本
            paragraphs_text = "\n\n".join([
                f"[{p['paragraph_id']}] {p['text']}"
                for p in doc["paragraphs"]
                if p['type'] in ['paragraph', 'table_row']
            ])
            
            prompt = f"""
你是证据提取专家。请从以下文档中提取3-10条最小事实单元（findings）。

文档标题: {title}
主题提示: {topic_hint}

文档内容:
{paragraphs_text[:8000]}  # 限制长度

每条finding必须包含:
- finding_index: 序号（从1开始）
- type: 类型（研究发现/数据描述/作者观点/政策信息）
- claim: 事实陈述（一句话，必须基于原文）
- numbers: 涉及的数字列表（含单位，如["2020年增长15%", "样本量1000人"]）
- linked_assets: 关联的图表ID列表（暂时为空）

请以JSON数组格式输出，例如:
[
    {{
        "finding_index": 1,
        "type": "数据描述",
        "claim": "2020年中国GDP增长2.3%",
        "numbers": ["2020年", "2.3%"],
        "linked_assets": []
    }},
    ...
]

注意:
1. 只提取原文明确提到的事实
2. 禁止推断、外推、常识补充
3. 数字必须带单位和时间口径
"""
            
            response = await llm_service._generate_with_provider(
                prompt=prompt,
                timeout=120.0
                
            )
            
            try:
                findings = json.loads(response)
            except:
                # 如果解析失败，尝试提取JSON部分
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    findings = json.loads(json_match.group())
                else:
                    findings = []
            
            # 添加source_doc_id
            for finding in findings:
                finding["source_doc_id"] = doc_id
            
            evidence_ledger.append({
                "doc_id": doc_id,
                "title": title,
                "time_range": None,  # 可以后续从文档中提取
                "findings": findings
            })
        
        return evidence_ledger
    
    async def _build_visual_asset_ledger(
        self,
        parsed_docs: List[Dict[str, Any]],
        evidence_ledger: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Step A2: 构建图表证据台账"""
        
        assets = []
        
        for doc in parsed_docs:
            doc_id = doc["doc_id"]
            
            # 提取表格
            table_paragraphs = [
                p for p in doc["paragraphs"]
                if p['type'] == 'table_row'
            ]
            
            if table_paragraphs:
                # 按表格分组（简化处理，每个table_row作为一个表格）
                for idx, table_para in enumerate(table_paragraphs[:5]):  # 限制最多5个表格
                    asset_id = f"{doc_id}-TAB-{idx + 1}"
                    
                    assets.append({
                        "asset_id": asset_id,
                        "asset_type": "TAB",
                        "original_label": None,
                        "caption_or_title": f"表格 {idx + 1}",
                        "location_anchor": table_para['text'][:100],
                        "key_numbers": self._extract_numbers_from_text(table_para['text']),
                        "takeaway_claim": None,
                        "linked_findings": [],
                        "editing_instruction": "突出关键数据列"
                    })
            
            # 提取图片
            if "images" in doc and doc["images"]:
                for idx, img in enumerate(doc["images"]):  # 提取所有图片
                    asset_id = f"{doc_id}-FIG-{idx + 1}"
                    
                    # 尝试从周围文本找图注
                    caption = self._find_caption_near_image(doc, idx)
                    
                    # 获取图片URL和其他信息
                    img_url = None
                    img_filename = None
                    img_path = None
                    
                    if isinstance(img, dict):
                        img_url = img.get("url")
                        img_filename = img.get("filename")
                        img_path = img.get("path")
                    
                    asset_data = {
                        "asset_id": asset_id,
                        "asset_type": "FIG",
                        "original_label": None,
                        "caption_or_title": caption or f"图 {idx + 1}",
                        "location_anchor": caption[:100] if caption else None,
                        "key_numbers": [],
                        "takeaway_claim": None,
                        "linked_findings": [],
                        "editing_instruction": "突出主要趋势"
                    }
                    
                    # 添加图片相关信息
                    if img_url:
                        asset_data["image_url"] = img_url
                    if img_filename:
                        asset_data["image_filename"] = img_filename
                    if img_path:
                        asset_data["image_path"] = img_path
                    
                    assets.append(asset_data)
        
        return {
            "assets": assets
        }
    
    def _extract_numbers_from_text(self, text: str) -> List[str]:
        """从文本中提取数字（带单位）"""
        # 匹配数字+单位的模式
        patterns = [
            r'\d+\.?\d*%',  # 百分比
            r'\d+\.?\d*[亿万千百十]?[元人次个]',  # 中文单位
            r'\d{4}年',  # 年份
            r'\d+\.?\d*\s*[a-zA-Z]+',  # 英文单位
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)
        
        return numbers[:8]  # 最多返回8个
    
    def _find_caption_near_image(self, doc: Dict[str, Any], img_idx: int) -> Optional[str]:
        """在图片附近查找图注"""
        # 查找包含"图"字的段落，并尝试提取更准确的标题
        for para in doc["paragraphs"]:
            text = para.get("text", "")
            # 匹配 "图X：标题" 或 "图X 标题" 或 "Figure X: 标题" 等格式
            import re
            patterns = [
                r'图\s*\d+[：:]\s*(.+)',  # 图1：标题
                r'图\s*\d+[\s\.]+(.+)',   # 图1 标题 或 图1. 标题
                r'Figure\s+\d+[：:]\s*(.+)',  # Figure 1: 标题
                r'Fig\.\s*\d+[：:]\s*(.+)',   # Fig. 1: 标题
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    caption = match.group(1).strip()
                    # 限制长度，去掉过长的描述
                    if len(caption) > 100:
                        caption = caption[:100] + "..."
                    return caption
            
            # 如果没有匹配到特定格式，但包含"图"字且长度合适
            if ("图" in text or "Figure" in text or "Fig" in text) and 10 < len(text) < 200:
                # 清理文本
                caption = text.strip()
                if len(caption) > 100:
                    caption = caption[:100] + "..."
                return caption
        
        return None
    
    async def _select_structure(
        self,
        topic_hint: str,
        evidence_ledger: List[Dict[str, Any]],
        visual_asset_ledger: Dict[str, Any],
        style_profile: Dict[str, Any],
        style_preference: Optional[str]
    ) -> Dict[str, Any]:
        """Step B: 选择结构"""
        
        # 如果用户指定了结构，直接使用
        if style_preference and style_preference in ["S1", "S2", "S3", "S4"]:
            main_structure = style_preference
        else:
            main_structure = style_profile.get("main_structure", "S1")
        
        # 构建证据摘要
        evidence_summary = "\n".join([
            f"文档{ledger['doc_id']}: {len(ledger['findings'])}条证据"
            for ledger in evidence_ledger
        ])
        
        prompt = f"""
你是口播稿结构设计专家。请为以下主题设计口播稿结构。

主题: {topic_hint}
选定结构: {main_structure}
证据概览:
{evidence_summary}

请输出3-6个一级小标题（每个≤12字），并为每个小标题分配相关文档和图表。

输出格式（JSON）:
{{
    "structure_type": "{main_structure}",
    "sections": [
        {{
            "section_id": 1,
            "title": "小标题1",
            "related_docs": ["D1", "D2"],
            "related_assets": ["D1-FIG-1", "D2-TAB-1"]
        }},
        ...
    ]
}}
"""
        
        response = await llm_service._generate_with_provider(
            prompt=prompt,
            timeout=120.0
            
        )
        
        try:
            structure = json.loads(response)
        except:
            # 默认结构
            structure = {
                "structure_type": main_structure,
                "sections": [
                    {"section_id": 1, "title": "引言", "related_docs": [], "related_assets": []},
                    {"section_id": 2, "title": "主体", "related_docs": [], "related_assets": []},
                    {"section_id": 3, "title": "结论", "related_docs": [], "related_assets": []}
                ]
            }
        
        return structure
    
    async def _generate_script_review(
        self,
        request: IntegratedVoiceoverRequest,
        style_profile: Dict[str, Any],
        evidence_ledger: List[Dict[str, Any]],
        visual_asset_ledger: Dict[str, Any],
        structure: Dict[str, Any]
    ) -> str:
        """Step C: 生成审阅版口播稿（带证据标注）"""
        
        # 构建完整的证据和图表信息
        evidence_text = json.dumps(evidence_ledger, ensure_ascii=False, indent=2)
        assets_text = json.dumps(visual_asset_ledger, ensure_ascii=False, indent=2)
        structure_text = json.dumps(structure, ensure_ascii=False, indent=2)
        
        # 构建片头
        intro_text = ""
        if style_profile.get("enable_vox_intro", True):
            speaker_aff = request.speaker_affiliation or "VoxChina"
            speaker_name = request.speaker_name or "主播"
            intro_text = f"""
大家好，我是{speaker_aff}的{speaker_name}。
很高兴在VOXCHINA和大家见面。
"""
        
        prompt = f"""
你是VoxChina口播稿撰写专家。请基于以下材料，生成一份完整的口播稿（审阅版，带证据标注）。

【主题】
{request.topic_hint}

【风格配置】
{json.dumps(style_profile, ensure_ascii=False, indent=2)}

【证据台账】
{evidence_text[:10000]}

【图表台账】
{assets_text[:5000]}

【结构设计】
{structure_text}

【输出要求】
请按以下格式输出完整口播稿:

## 标题
（≤20字，吸引人的标题）

## 片头
{intro_text}

## 点题段
（1段，说明现实冲击/矛盾 + 本期结构说明，必须有证据支撑）
【证据：来源文档ID - finding编号】

## 正文
### 小标题1
段落1内容...
【证据：D1-F1】
【图表：D1-FIG-1】

段落2内容...
【证据：D1-F2, D2-F1】

### 小标题2
...

## 结尾
（回扣结构 + 收束语）
感谢大家观看本期视频，欢迎继续关注 VOXCHINA，我们下期再见！

【硬性规则】
R1: 只使用Evidence Ledger中存在的事实，禁止外推
R2: 数字必须带单位与时间口径
R3: 每段末尾必须加【证据：...】标注
R4: 图表必须来自Visual Asset Ledger
R5: 语气大众可懂但专业克制，多短句

请开始撰写:
"""
        
        script_review = await llm_service._generate_with_provider(
            prompt=prompt,
            timeout=120.0
        )
        
        return script_review
    
    async def _generate_script_final(self, script_review: str) -> str:
        """Step D: 生成上屏版口播稿（删除证据标注）"""
        
        # 删除所有【证据：...】标注
        script_final = re.sub(r'【证据：[^】]+】', '', script_review)
        
        # 清理多余空行
        script_final = re.sub(r'\n{3,}', '\n\n', script_final)
        
        return script_final.strip()
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_task_result(self, task_id: str) -> Optional[IntegratedVoiceoverResponse]:
        """获取任务结果"""
        task_data = self.tasks.get(task_id)
        if not task_data:
            return None
        
        return IntegratedVoiceoverResponse(
            task_id=task_data["task_id"],
            status=task_data["status"],
            style_profile=StyleProfile(**task_data["style_profile"]) if task_data.get("style_profile") else None,
            evidence_ledger=[EvidenceLedger(**ledger) for ledger in task_data.get("evidence_ledger", [])],
            visual_asset_ledger=VisualAssetLedger(**task_data["visual_asset_ledger"]) if task_data.get("visual_asset_ledger") else None,
            structure=task_data.get("structure"),
            script_review=task_data.get("script_review"),
            script_final=task_data.get("script_final"),
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"]
        )


# 单例
integrated_voiceover_service = IntegratedVoiceoverService()
