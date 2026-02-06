"""
VoxChina 多文献整合口播稿件策划服务 (Evidence-based Scriptwriter)
基于用户上传的多篇文档，生成可直接录制的短视频口播稿
"""
import uuid
import json
import re
import asyncio
import os
from datetime import datetime
from pathlib import Path
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
        # 持久化文件路径
        self.tasks_file = Path("/www/wwwroot/voxchina/backend/static/integrated_voiceover_tasks.json")
        
        # 任务存储 {task_id: task_data}
        self.tasks = {}
        
        # 加载历史任务
        self._load_tasks()
    
    def _save_tasks(self):
        """保存任务数据到文件"""
        try:
            # 确保目录存在
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 序列化任务数据
            tasks_data = {}
            for task_id, task in self.tasks.items():
                # 深拷贝任务数据
                task_copy = {}
                for key, value in task.items():
                    # 转换日期时间为字符串
                    if isinstance(value, datetime):
                        task_copy[key] = value.isoformat()
                    else:
                        task_copy[key] = value
                tasks_data[task_id] = task_copy
            
            # 写入文件（临时文件 + 原子替换）
            temp_file = self.tasks_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 原子替换
            temp_file.replace(self.tasks_file)
            
            logger.debug(f"✅ 已保存 {len(self.tasks)} 个任务")
            
        except Exception as e:
            logger.error(f"❌ 保存任务失败: {e}", exc_info=True)
    
    def _load_tasks(self):
        """从文件加载任务数据"""
        try:
            if not self.tasks_file.exists():
                logger.info("📂 任务文件不存在，从空开始")
                return
            
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # 恢复任务数据
            for task_id, task in tasks_data.items():
                # 转换字符串为日期时间
                if 'created_at' in task and isinstance(task['created_at'], str):
                    task['created_at'] = datetime.fromisoformat(task['created_at'])
                if 'updated_at' in task and isinstance(task['updated_at'], str):
                    task['updated_at'] = datetime.fromisoformat(task['updated_at'])
                self.tasks[task_id] = task
            
            logger.info(f"✅ 已加载 {len(self.tasks)} 个历史任务")
            
        except Exception as e:
            logger.error(f"❌ 加载任务失败: {e}", exc_info=True)
            self.tasks = {}
    
    async def _call_llm_with_retry(
        self,
        prompt: str,
        timeout: float = 300.0,
        max_retries: int = 3,
        step_name: str = "LLM调用"
    ) -> str:
        """
        带自动重试的LLM调用
        
        Args:
            prompt: 提示词
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            step_name: 步骤名称（用于日志）
        
        Returns:
            LLM响应文本
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"{step_name} - 尝试 {attempt + 1}/{max_retries}")
                
                response = await llm_service._generate_with_provider(
                    prompt=prompt,
                    timeout=timeout
                )
                
                logger.info(f"{step_name} - 成功")
                return response
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"{step_name} - 尝试 {attempt + 1} 失败: {error_msg}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5秒, 10秒, 15秒...
                    logger.info(f"{step_name} - 等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{step_name} - 所有重试均失败")
        
        # 所有重试都失败
        raise last_error
        
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
        
        # 保存任务到文件
        self._save_tasks()
        
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
                self._save_tasks()  # 保存任务状态
    
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
                    doc_id = f"D{len(parsed_docs) + 1}"
                    parsed_doc["doc_id"] = doc_id
                    
                    # 详细记录图片信息
                    images_count = len(parsed_doc.get("images", []))
                    logger.info(f"📄 文档 {doc_id} ({filename}): {images_count} 张图片")
                    if images_count > 0:
                        for idx, img in enumerate(parsed_doc.get("images", [])):
                            logger.info(f"   - 图片 {idx+1}: {img.get('url')}")
                    
                    parsed_docs.append(parsed_doc)
                except Exception as e:
                    logger.error(f"Failed to parse {filename}: {e}")
                    continue
            
            logger.info(f"📦 总共解析了 {len(parsed_docs)} 个文档")
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
            
            # 详细记录 Visual Asset Ledger 内容
            logger.info(f"📊 Visual Asset Ledger 构建完成:")
            logger.info(f"   - 总资产数: {len(visual_asset_ledger.get('assets', []))}")
            for asset in visual_asset_ledger.get('assets', []):
                logger.info(f"   - {asset['asset_id']} ({asset['asset_type']}): image_url={'存在' if 'image_url' in asset else '不存在'}")
                if 'image_url' in asset:
                    logger.info(f"      URL: {asset['image_url']}")
            
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
            
            # 保存任务状态
            self._save_tasks()
            
            logger.info(f"Task {task_id}: Completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} processing failed at {task_data.get('current_step', 'Unknown')}: {e}")
            task_data["status"] = "failed"
            
            # 提供更友好的错误信息
            current_step = task_data.get('current_step', 'Unknown')
            step_names = {
                'Parsing': '文档解析',
                'Step0': '风格配置生成',
                'StepA': '证据提取',
                'StepA2': '图表识别',
                'StepB': '结构设计',
                'StepC': '审阅版生成',
                'StepD': '上屏版生成'
            }
            
            step_name = step_names.get(current_step, current_step)
            error_msg = f"处理失败于【{step_name}】步骤"
            
            # 检查是否是超时错误
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                error_msg += " - LLM响应超时，请稍后重试"
            elif "rate limit" in str(e).lower():
                error_msg += " - API调用频率限制，请稍后重试"
            else:
                error_msg += f" - {str(e)}"
            
            task_data["error"] = error_msg
            task_data["updated_at"] = datetime.now().isoformat()
            self._save_tasks()  # 保存任务状态
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

请输出以下内容（严格JSON格式，不要附加任何解释）:
{{
    "enable_vox_intro": {str(request.include_vox_intro).lower()},
    "main_structure": "S1/S2/S3/S4之一",
    "figure_style": "A或B",
    "rules": ["规则1", "规则2", "规则3", "规则4", "规则5"]
}}

【结构说明】
- S1: 三维度/三主线（适合多角度分析）
- S2: 时间线/阶段推进（适合历史演进）
- S3: 现状—机制—对策（适合政策分析）
- S4: 机制链条（适合因果分析）

【图表风格】
- A: 独立行展示（图/表 + 标题 + 要点）
- B: 正文内嵌（〔画面：asset_id（标题）— 要点〕）

【STYLE RULES 生成要求——必须严格遵守】
rules 数组必须恰好包含 5 条规则，每条规则必须是**针对本次文档主题的具体指导**，不允许写泛泛的通用规则。

5 条规则必须分别覆盖以下 5 个维度（每个维度 1 条）:
1. 叙事逻辑：描述整体口播的叙事推进方式，要结合具体主题说明采用什么论证逻辑（如因果链条、对比分析、政策推演等），明确各段的逻辑衔接方式
2. 机制链/论证链：说明核心论证链的构成要素——起点变量、中介机制、结果变量分别是什么，要用文档中的实际概念填充
3. 引用规范：要求关键结论必须引用具体研究或政策来源，说明引用的优先级（如优先引用哪些文档的实证结果，政策背景和现实举例可辅以哪些文档）
4. 数据口径：涉及数字时必须说明时间、地区、样本或政策背景等口径信息；没有确切数字时避免"翻倍""大幅"等模糊表述
5. 证据优先级：说明各文档（D1-D{len(parsed_docs)}）的使用策略——哪些文档的实证结果作为核心证据，哪些作为背景补充

【好规则 vs 差规则示例】
差规则（太泛，禁止）: "每段必须有证据支撑"
好规则（具体到主题）: "整体采用'问题提出—机制拆解—实证证据—影响与启示'的口播逻辑，突出因果链条"

差规则（太泛，禁止）: "禁止外推和主观推断"
好规则（具体到主题）: "每一条机制链都要明确：起点变量（如数字分心/免费教育）—中介机制（行为改变、资源配置）—结果变量（学业表现、劳动市场回报）"

差规则（太泛，禁止）: "数字必须带单位和时间口径"
好规则（具体到主题）: "涉及数字时，必须说明时间、地区、样本或政策背景等口径信息；没有确切数字时避免'翻倍''大幅'等模糊表述"
"""
        
        # 使用自动重试机制
        response = await self._call_llm_with_retry(
            prompt=prompt,
            timeout=180.0,  # 3分钟
            max_retries=2,  # 这个步骤较简单，2次重试足够
            step_name="Step 0: 生成风格配置"
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
            
            # 使用自动重试机制
            response = await self._call_llm_with_retry(
                prompt=prompt,
                timeout=180.0,  # 3分钟
                max_retries=2,
                step_name=f"Step A: 提取文档 {doc_id} 的证据"
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
            logger.info(f"[Visual Assets] 处理文档 {doc_id}, images字段: {'存在' if 'images' in doc else '不存在'}")
            if "images" in doc:
                logger.info(f"[Visual Assets] 文档 {doc_id} 包含 {len(doc['images'])} 张图片")
            
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
                    logger.info(f"[Visual Assets] 处理 {asset_id}, img 数据类型: {type(img)}, 内容: {img}")
                    
                    if img_url:
                        asset_data["image_url"] = img_url
                        logger.info(f"[Visual Assets] ✅ {asset_id} - 添加 image_url: {img_url}")
                    else:
                        logger.warning(f"[Visual Assets] ❌ {asset_id} - 没有URL！img数据: {img}")
                    
                    if img_filename:
                        asset_data["image_filename"] = img_filename
                    if img_path:
                        asset_data["image_path"] = img_path
                    
                    logger.info(f"[Visual Assets] {asset_id} 最终 asset_data 包含字段: {list(asset_data.keys())}")
                    assets.append(asset_data)
        
        logger.info(f"[Visual Assets] 总共生成 {len(assets)} 个视觉资产")
        for asset in assets:
            if asset["asset_type"] == "FIG":
                has_url = "image_url" in asset
                logger.info(f"[Visual Assets] {asset['asset_id']}: {asset['caption_or_title']} - URL: {'有' if has_url else '无'}")
        
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
        
        # 使用自动重试机制
        response = await self._call_llm_with_retry(
            prompt=prompt,
            timeout=180.0,  # 3分钟
            max_retries=2,
            step_name="Step B: 选择结构"
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
        
        # 字数限制说明
        word_limit_instruction = ""
        if request.word_limit and request.word_limit > 0:
            word_limit_instruction = f"""
【字数要求】
请将口播稿总字数控制在 {request.word_limit} 字左右（允许±10%浮动）。
在保证内容完整性的前提下，精简表达，突出重点。
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
{word_limit_instruction}
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
R4: 图表引用必须来自Visual Asset Ledger，并严格使用【图表：asset_id】格式（如【图表：D1-FIG-1】）。禁止使用〔画面：...〕、[图：...]等其他格式
R5: 语气大众可懂但专业克制，多短句
R6: 每个正文小节至少引用一个相关图表（如果Visual Asset Ledger中存在相关图表的话）

请开始撰写:
"""
        
        # 使用自动重试机制调用LLM
        script_review = await self._call_llm_with_retry(
            prompt=prompt,
            timeout=300.0,  # 5分钟超时
            max_retries=3,
            step_name="Step C: 生成审阅版口播稿"
        )
        
        return script_review
    
    async def _generate_script_final(self, script_review: str) -> str:
        """Step D: 生成上屏版口播稿（删除证据标注，保留图表标记供前端渲染）"""
        
        script_final = script_review
        
        # 删除所有证据标注（覆盖全角、半角、圆括号等多种变体）
        # 全角方括号：【证据：...】
        script_final = re.sub(r'【证据[：:]([^】]+)】', '', script_final)
        # 半角方括号：[证据：...] 或 [证据:...]
        script_final = re.sub(r'\[证据[：:]([^\]]+)\]', '', script_final)
        # 圆括号变体：（证据：...）
        script_final = re.sub(r'（证据[：:]([^）]+)）', '', script_final)
        # 英文格式变体：[Evidence: ...] 或 【Evidence: ...】
        script_final = re.sub(r'[\[【]Evidence[：:][^\]】]+[\]】]', '', script_final, flags=re.IGNORECASE)
        
        # 清理行末多余空格（证据标注删除后可能留下的）
        script_final = re.sub(r' +$', '', script_final, flags=re.MULTILINE)
        
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
            logger.warning(f"Task {task_id} not found in tasks")
            return None
        
        try:
            # 调试日志
            logger.info(f"Getting task result for {task_id}, status: {task_data.get('status')}")
            
            # 统一转换日期格式为字符串（如果是 datetime 对象）
            created_at = task_data["created_at"]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            updated_at = task_data["updated_at"]
            if isinstance(updated_at, datetime):
                updated_at = updated_at.isoformat()
            
            # 构建响应对象
            response = IntegratedVoiceoverResponse(
                task_id=task_data["task_id"],
                status=task_data["status"],
                style_profile=StyleProfile(**task_data["style_profile"]) if task_data.get("style_profile") else None,
                evidence_ledger=[EvidenceLedger(**ledger) for ledger in task_data.get("evidence_ledger", [])] if task_data.get("evidence_ledger") else None,
                visual_asset_ledger=VisualAssetLedger(**task_data["visual_asset_ledger"]) if task_data.get("visual_asset_ledger") else None,
                structure=task_data.get("structure"),
                script_review=task_data.get("script_review"),
                script_final=task_data.get("script_final"),
                created_at=created_at,
                updated_at=updated_at
            )
            
            logger.info(f"✅ Task result built successfully for {task_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error building task result for {task_id}: {e}", exc_info=True)
            logger.error(f"Task data keys: {task_data.keys()}")
            if task_data.get("visual_asset_ledger"):
                logger.error(f"Visual asset ledger: {task_data['visual_asset_ledger']}")
            raise


# 单例
integrated_voiceover_service = IntegratedVoiceoverService()
