"""
口播稿生成API端点
支持多文档上传、异步生成、进度查询、结果下载
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from loguru import logger

from app.services.script_generator_service import script_generator_service
from app.services.script_task_manager import script_task_manager
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


@router.post("/generate")
async def generate_script(
    files: List[UploadFile] = File(...),
    speaker_name: str = Form("VoxChina主播"),
    speaker_affiliation: str = Form("VoxChina团队"),
    episode_topic: str = Form(None),
    duration_target_sec: int = Form(150),
    language: str = Form("zh-CN"),
    user: str = Depends(get_current_user)
):
    """
    启动口播稿生成任务
    
    Args:
        files: 上传的文档列表（DOCX/PDF，最多10个）
        speaker_name: 主播姓名
        speaker_affiliation: 主播机构
        episode_topic: 期数主题（可选）
        duration_target_sec: 目标时长（秒，默认150秒）
        language: 语言（默认zh-CN）
        
    Returns:
        {
            "task_id": str,
            "message": str,
            "file_count": int
        }
    """
    try:
        logger.info(f"Received script generation request from user: {user}")
        logger.info(f"Files: {len(files)}, Speaker: {speaker_name}, Duration: {duration_target_sec}s")
        
        # 验证文件数量
        if len(files) < 1:
            raise HTTPException(status_code=400, detail="请至少上传1个文档")
        
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail=f"最多支持10个文档，当前上传了{len(files)}个"
            )
        
        # 读取所有文件内容
        files_data = []
        for file in files:
            filename = file.filename
            content = await file.read()
            
            if not content:
                raise HTTPException(status_code=400, detail=f"文件 {filename} 为空")
            
            # 验证文件格式
            if not (filename.lower().endswith('.docx') or 
                    filename.lower().endswith('.doc') or 
                    filename.lower().endswith('.pdf')):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件格式: {filename}，仅支持 DOCX/DOC/PDF"
                )
            
            files_data.append({
                "filename": filename,
                "content": content
            })
        
        # 启动生成任务
        task_id = await script_generator_service.generate_script(
            files_data,
            speaker_name=speaker_name,
            speaker_affiliation=speaker_affiliation,
            episode_topic=episode_topic,
            duration_target_sec=duration_target_sec,
            language=language
        )
        
        logger.info(f"Script generation task created: {task_id}")
        
        return JSONResponse(content={
            "task_id": task_id,
            "message": "口播稿生成任务已启动",
            "file_count": len(files_data)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start script generation: {e}")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    user: str = Depends(get_current_user)
):
    """
    查询任务状态
    
    Returns:
        {
            "task_id": str,
            "status": "pending|processing|completed|failed",
            "stage": str,
            "progress": {...},
            "timing": {...},
            "detail": str,
            "severity": str,
            "result": {...} (if completed),
            "error": str (if failed)
        }
    """
    try:
        task = await script_task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return JSONResponse(content=task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/tasks/{task_id}/ledgers")
async def get_task_ledgers(
    task_id: str,
    user: str = Depends(get_current_user)
):
    """
    获取任务的证据台账（用于审计）
    
    Returns:
        {
            "task_id": str,
            "evidence_ledgers": [...],
            "audit_report": {...}
        }
    """
    try:
        task = await script_task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        return JSONResponse(content={
            "task_id": task_id,
            "evidence_ledgers": task.evidence_ledgers,
            "audit_report": task.audit_report
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task ledgers: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    user: str = Depends(get_current_user)
):
    """
    删除任务（清理内存）
    """
    try:
        task = await script_task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 从任务管理器中删除
        del script_task_manager.tasks[task_id]
        
        logger.info(f"Deleted task: {task_id}")
        
        return JSONResponse(content={
            "message": "任务已删除",
            "task_id": task_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

