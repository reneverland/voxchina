from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import shutil
import os
import uuid
import json
import time
import threading
from pathlib import Path
from app.services.vox.vox_unified_generator import VoxContentGenerator
from app.services.llm_service import llm_service
from loguru import logger

router = APIRouter()

# 临时文件存储路径
TEMP_UPLOAD_DIR = Path("static/uploads/vox_workshop")
TEMP_OUTPUT_DIR = Path("static/outputs/vox_workshop")

# 确保目录存在
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# In-memory task store (Use Redis for production)
tasks: Dict[str, Dict[str, Any]] = {}
tasks_lock = threading.Lock()

def background_generate_task(task_id: str, inputs: List[str], options: Dict[str, Any], llm_provider: str, model_name: str):
    """后台任务：在独立线程中执行内容生成"""
    try:
        logger.info(f"[Task {task_id}] 开始处理 - LLM: {llm_provider}/{model_name}, 文件数: {len(inputs)}")
        
        with tasks_lock:
            tasks[task_id]['status'] = 'processing'
            tasks[task_id]['progress'] = 0
            tasks[task_id]['step'] = '初始化...'

        def progress_callback(step: str, percent: int):
            with tasks_lock:
                tasks[task_id]['step'] = step
                tasks[task_id]['progress'] = percent
            logger.info(f"[Task {task_id}] {percent}%: {step}")

        generator = VoxContentGenerator(
            llm_provider=llm_provider,
            model_name=model_name
        )
        
        logger.info(f"[Task {task_id}] 调用生成器...")
        result = generator.generate_vox_content(
            inputs=inputs,
            options=options,
            progress_callback=progress_callback
        )
        
        # 详细日志：记录生成结果的键
        logger.info(f"[Task {task_id}] 生成器返回结果键: {list(result.keys())}")
        logger.info(f"[Task {task_id}] mode={result.get('mode')}, summary_zh长度={len(result.get('summary_zh', result.get('content', '')))}")
        
        # 构建返回结果
        session_id = options.get('_session_id')
        output_docx_name = Path(options['output_docx']).name
        relative_docx_path = f"/static/outputs/vox_workshop/{session_id}/{output_docx_name}"

        # 确保所有字段都存在
        summary_zh = result.get("summary_zh", result.get("content", ""))
        summary_en = result.get("summary_en", "")
        
        logger.info(f"[Task {task_id}] 最终 summary_zh 类型={type(summary_zh)}, 长度={len(summary_zh) if summary_zh else 0}")

        with tasks_lock:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['progress'] = 100
            tasks[task_id]['step'] = '完成'
        tasks[task_id]['result'] = {
            "success": True,
            "mode": result["mode"],
            "content": result["content"],
            "summary_zh": summary_zh,
            "summary_en": summary_en,
            "title": result.get("title", ""),
            "structured_fact_table": result.get("structured_fact_table", {}),
            "docx_url": relative_docx_path,
            "processing_time": result["processing_time_sec"],
            "api_version": "CBIT-Elite v4.2"
        }
        
        logger.info(f"[Task {task_id}] 完成！耗时 {result['processing_time_sec']}s, 摘要字数: {len(summary_zh)}")
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        error_type = type(e).__name__
        error_detail = str(e)
        
        # 详细错误日志
        logger.error(f"[Task {task_id}] 失败: {error_type}: {error_detail}")
        logger.error(f"[Task {task_id}] 完整堆栈:\n{error_msg}")
        
        # 如果是KeyError，记录缺少的键
        if isinstance(e, KeyError):
            logger.error(f"[Task {task_id}] KeyError - 缺少的键: {error_detail}")
        
        with tasks_lock:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = f"{error_type}: {error_detail}"
            tasks[task_id]['progress'] = 0
            # 即使失败也返回默认结果结构，避免前端访问undefined字段
            tasks[task_id]['result'] = {
                "success": False,
                "mode": "UNKNOWN",
                "content": "",
                "summary_zh": "",
                "summary_en": "",
                "title": "",
                "structured_fact_table": {},
                "docx_url": "",
                "processing_time": 0,
                "api_version": "CBIT-Elite v4.2",
                "error": f"{error_type}: {error_detail}",
                "traceback": error_msg if logger.level <= 10 else None  # 仅在DEBUG模式下返回堆栈
            }

@router.post("/generate")
async def generate_vox_content_endpoint(
    files: List[UploadFile] = File(...),
    speaker_name: str = Form("研究员"),
    speaker_affiliation: str = Form("VoxChina"),
    topic_hint: str = Form(""),
    duration_target_sec: int = Form(150),
    include_figure_placeholders: bool = Form(True)
):
    """
    异步生成内容接口
    立即返回 task_id，客户端通过 /status/{task_id} 查询进度
    注意：LLM配置从全局统一配置中获取，不再接受前端传入
    """
    try:
        session_id = str(uuid.uuid4())
        task_id = session_id
        
        # 从统一配置获取LLM参数
        llm_config = llm_service.get_current_config()
        llm_provider = llm_config['provider']
        model_name = llm_config['model']
        
        logger.info(f"[API] 收到生成请求，task_id={task_id}, files={len(files)}, LLM={llm_provider}/{model_name}")
        
        # 1. 快速保存上传的文件
        session_upload_dir = TEMP_UPLOAD_DIR / session_id
        session_upload_dir.mkdir(parents=True, exist_ok=True)
        
        saved_file_paths = []
        for file in files:
            file_path = session_upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(str(file_path))
        
        logger.info(f"[API] 文件保存完成: {saved_file_paths}")
            
        # 2. 准备输出路径
        session_output_dir = TEMP_OUTPUT_DIR / session_id
        session_output_dir.mkdir(parents=True, exist_ok=True)
        output_docx_name = f"vox_content_{session_id}.docx"
        output_docx_path = session_output_dir / output_docx_name
        
        # 3. 准备 Options
        options = {
            'speaker_name': speaker_name,
            'speaker_affiliation': speaker_affiliation,
            'topic_hint': topic_hint,
            'duration_target_sec': duration_target_sec,
            'include_figure_placeholders': include_figure_placeholders,
            'output_docx': str(output_docx_path),
            '_session_id': session_id
        }
        
        # 4. 初始化任务状态
        with tasks_lock:
            tasks[task_id] = {
                "id": task_id,
                "status": "pending",
                "progress": 0,
                "step": "等待处理...",
                "created_at": time.time()
            }
        
        # 5. 在独立线程中启动后台任务（避免阻塞FastAPI）
        thread = threading.Thread(
            target=background_generate_task,
            args=(task_id, saved_file_paths, options, llm_provider, model_name),
            daemon=True
        )
        thread.start()
        
        logger.info(f"[API] 后台任务已启动，thread_id={thread.ident}")
        
        # 立即返回
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "任务已启动，请通过 /status/{task_id} 查询进度",
            "api_version": "CBIT-Elite v4.2"
        }
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"[API] 启动任务失败: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务状态和进度
    返回: {status, progress, step, result(if completed), error(if failed)}
    """
    with tasks_lock:
        if task_id not in tasks:
            logger.warning(f"[API] 任务不存在: {task_id}")
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        task_data = tasks[task_id].copy()
    
    logger.debug(f"[API] 查询任务状态: {task_id} -> {task_data['status']} ({task_data['progress']}%)")
    return task_data


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务记录（可选的清理接口）
    """
    with tasks_lock:
        if task_id in tasks:
            del tasks[task_id]
            logger.info(f"[API] 删除任务: {task_id}")
            return {"message": "任务已删除"}
        else:
            raise HTTPException(status_code=404, detail="任务不存在")


@router.get("/tasks")
async def list_tasks(limit: int = 20):
    """
    列出所有任务（调试用）
    """
    with tasks_lock:
        all_tasks = list(tasks.values())
    
    # 按创建时间倒序
    all_tasks.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    return {"tasks": all_tasks[:limit], "total": len(all_tasks)}
