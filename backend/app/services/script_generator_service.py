"""
口播稿生成 - 主服务（Orchestrator）
协调所有子服务，完成端到端的口播稿生成流程
"""
import asyncio
import json
import uuid
from typing import List, Dict, Any
from loguru import logger

from app.services.document_parser_service import document_parser_service
from app.services.script_task_manager import script_task_manager
from app.services.script_chunking_service import script_chunking_service
from app.services.script_ledger_service import script_ledger_service
from app.services.script_outline_service import script_outline_service
from app.services.script_writer_service import script_writer_service
from app.services.script_verifier_service import script_verifier_service
from app.services.script_docx_service import script_docx_service


class ScriptGeneratorService:
    """口播稿生成主服务"""
    
    async def generate_script(
        self,
        files_data: List[Dict[str, Any]],  # [{"filename": str, "content": bytes}]
        speaker_name: str = "VoxChina主播",
        speaker_affiliation: str = "VoxChina团队",
        episode_topic: str = None,
        duration_target_sec: int = 150,
        language: str = "zh-CN"
    ) -> str:
        """
        启动口播稿生成任务（异步后台执行）
        
        Args:
            files_data: 上传的文件列表
            speaker_name: 主播姓名
            speaker_affiliation: 主播机构
            episode_topic: 期数主题
            duration_target_sec: 目标时长（秒）
            language: 语言
            
        Returns:
            task_id
        """
        # 创建任务
        task_id = str(uuid.uuid4())
        params = {
            "speaker_name": speaker_name,
            "speaker_affiliation": speaker_affiliation,
            "episode_topic": episode_topic,
            "duration_target_sec": duration_target_sec,
            "language": language,
            "file_count": len(files_data)
        }
        
        await script_task_manager.create_task(task_id, params)
        
        # 启动后台任务
        asyncio.create_task(self._execute_generation(task_id, files_data, params))
        
        return task_id
    
    async def _execute_generation(
        self,
        task_id: str,
        files_data: List[Dict[str, Any]],
        params: Dict[str, Any]
    ):
        """
        执行完整的生成流程（后台任务）
        """
        try:
            logger.info(f"Starting script generation task: {task_id}")
            
            # ========== 阶段1: 文档解析 ==========
            await script_task_manager.update_stage(
                task_id, 
                "parsing", 
                f"正在解析 {len(files_data)} 个文档...",
                "info"
            )
            
            parsed_docs = []
            for idx, file_data in enumerate(files_data):
                filename = file_data["filename"]
                content = file_data["content"]
                
                await script_task_manager.update_progress(
                    task_id,
                    doc_current=idx + 1,
                    doc_total=len(files_data)
                )
                
                try:
                    doc_data = document_parser_service.parse_document(content, filename)
                    parsed_docs.append({
                        "doc_id": f"doc{idx+1}",
                        "filename": filename,
                        "data": doc_data
                    })
                    logger.info(f"Parsed document {idx+1}/{len(files_data)}: {filename}")
                except Exception as e:
                    logger.error(f"Failed to parse {filename}: {e}")
                    raise Exception(f"文档解析失败 ({filename}): {str(e)}")
            
            # ========== 阶段2: 分块 ==========
            await script_task_manager.update_stage(
                task_id,
                "chunking",
                "正在对文档进行智能分块...",
                "info"
            )
            
            chunked_docs = []
            total_chunks = 0
            
            for doc in parsed_docs:
                doc_id = doc["doc_id"]
                paragraphs = doc["data"]["paragraphs"]
                
                chunking_result = script_chunking_service.chunk_document(paragraphs, doc_id)
                
                # 覆盖率验证
                coverage = script_chunking_service.verify_coverage(
                    chunking_result,
                    doc["data"]["total_paragraphs"]
                )
                
                if not coverage["is_complete"]:
                    logger.warning(
                        f"Document {doc_id} coverage incomplete: "
                        f"{coverage['coverage_rate']:.1%}"
                    )
                
                chunked_docs.append({
                    "doc_id": doc_id,
                    "filename": doc["filename"],
                    "title": doc["data"]["title"],
                    "chunking_result": chunking_result,
                    "coverage": coverage
                })
                
                total_chunks += chunking_result["total_chunks"]
            
            await script_task_manager.update_progress(
                task_id,
                chunk_total=total_chunks
            )
            
            logger.info(f"Total chunks across all documents: {total_chunks}")
            
            # ========== 阶段3: 证据台账生成（Map阶段）==========
            await script_task_manager.update_stage(
                task_id,
                "extracting",
                f"正在从 {total_chunks} 个文本块提取证据...",
                "info"
            )
            
            ledgers = []
            processed_chunks = 0
            
            for doc in chunked_docs:
                doc_id = doc["doc_id"]
                chunks = doc["chunking_result"]["chunks"]
                
                logger.info(f"Generating ledger for {doc_id}...")
                
                ledger = await script_ledger_service.generate_document_ledger(
                    doc_id,
                    chunks,
                    task_id
                )
                
                # 补充元信息
                ledger["title"] = doc["title"]
                ledger["filename"] = doc["filename"]
                
                ledgers.append(ledger)
                
                processed_chunks += len(chunks)
                await script_task_manager.update_progress(
                    task_id,
                    chunk_current=processed_chunks
                )
            
            logger.info(f"Generated {len(ledgers)} evidence ledgers")
            
            # ========== 阶段4: 跨文档大纲（Plan阶段）==========
            await script_task_manager.update_stage(
                task_id,
                "outlining",
                "正在生成跨文档大纲...",
                "info"
            )
            
            outline = await script_outline_service.generate_outline(
                ledgers,
                speaker_name=params["speaker_name"],
                speaker_affiliation=params["speaker_affiliation"],
                episode_topic=params.get("episode_topic"),
                duration_target_sec=params["duration_target_sec"],
                language=params["language"]
            )
            
            logger.info(f"Generated outline: {outline['episode_title']}")
            
            # ========== 阶段5: 写作成稿（Write阶段）==========
            await script_task_manager.update_stage(
                task_id,
                "writing",
                "正在撰写口播稿...",
                "info"
            )
            
            final_script, claim_checklist = await script_writer_service.draft_script(
                outline,
                ledgers
            )
            
            logger.info(f"Drafted script: {len(final_script)} chars")
            
            # ========== 阶段6: 事实核验（Verify阶段）==========
            await script_task_manager.update_stage(
                task_id,
                "verifying",
                "正在进行事实核验...",
                "info"
            )
            
            verdict, patched_script, issues = await script_verifier_service.verify_script(
                final_script,
                claim_checklist,
                ledgers
            )
            
            if verdict == "FAIL":
                logger.warning(f"Verification failed with {len(issues)} issues, using patched script")
            else:
                logger.info("Verification passed")
            
            # ========== 阶段7: DOCX导出 ==========
            await script_task_manager.update_stage(
                task_id,
                "exporting",
                "正在导出DOCX文件...",
                "info"
            )
            
            download_url = script_docx_service.export_to_docx(
                patched_script,
                task_id,
                outline["episode_title"]
            )
            
            logger.info(f"Exported DOCX: {download_url}")
            
            # ========== 完成任务 ==========
            result = {
                "task_id": task_id,
                "episode_title": outline["episode_title"],
                "download_url": download_url,
                "script_text": patched_script,
                "verification": {
                    "verdict": verdict,
                    "issues_count": len(issues)
                },
                "word_count": len(patched_script)
            }
            
            # 构建审计报告
            audit_report = {
                "documents": [
                    {
                        "doc_id": doc["doc_id"],
                        "filename": doc["filename"],
                        "coverage": doc["coverage"]
                    }
                    for doc in chunked_docs
                ],
                "total_chunks": total_chunks,
                "processed_chunks": processed_chunks,
                "verification": {
                    "verdict": verdict,
                    "issues": issues
                }
            }
            
            await script_task_manager.complete_task(
                task_id,
                result,
                evidence_ledgers=ledgers,
                audit_report=audit_report
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await script_task_manager.fail_task(task_id, str(e))


script_generator_service = ScriptGeneratorService()

