"""
Integrated Voiceover API Endpoints
多文献整合口播稿件策划接口
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from loguru import logger
from app.models.schemas import (
    IntegratedVoiceoverRequest,
    IntegratedVoiceoverResponse,
    IntegratedVoiceoverStatus
)
from app.services.integrated_voiceover_service import integrated_voiceover_service
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/create", response_model=dict)
async def create_integrated_voiceover_task(
    topic_hint: str = Form(..., description="主题/问题一句话"),
    speaker_affiliation: Optional[str] = Form(None, description="主播机构"),
    speaker_name: Optional[str] = Form(None, description="主播姓名"),
    include_vox_intro: bool = Form(True, description="是否包含VOXCHINA片头"),
    style_preference: Optional[str] = Form(None, description="结构偏好: S1/S2/S3/S4"),
    language: str = Form("zh", description="语言"),
    files: List[UploadFile] = File(..., description="上传的文档（Word/PDF）"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建整合口播稿生成任务
    
    上传多个文档，系统将：
    1. 解析文档内容（文字、表格、图表）
    2. 提取证据和图表
    3. 生成结构化口播稿
    
    返回task_id，可用于查询任务状态和结果
    """
    try:
        # 验证文件
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="至少需要上传一个文档")
        
        # 验证文件格式
        allowed_extensions = ['.docx', '.doc', '.pdf']
        for file in files:
            file_ext = '.' + file.filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件格式: {file.filename}，仅支持 .docx, .doc, .pdf"
                )
        
        # 读取文件内容
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((file.filename, content))
        
        # 创建请求对象
        request = IntegratedVoiceoverRequest(
            topic_hint=topic_hint,
            speaker_affiliation=speaker_affiliation,
            speaker_name=speaker_name,
            include_vox_intro=include_vox_intro,
            style_preference=style_preference,
            language=language
        )
        
        # 创建任务
        task_id = await integrated_voiceover_service.create_task(request, file_data)
        
        logger.info(f"Created integrated voiceover task: {task_id} by user {current_user.get('username')}")
        
        return {
            "task_id": task_id,
            "message": "任务创建成功，正在处理中...",
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create integrated voiceover task: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    查询任务状态
    
    返回任务的当前状态、进度和当前步骤
    包含 parsed_docs 用于文档详情查看
    """
    try:
        task_data = integrated_voiceover_service.get_task_status(task_id)
        
        if not task_data:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 如果任务完成，返回完整结果
        result = None
        if task_data["status"] == "completed":
            result = integrated_voiceover_service.get_task_result(task_id)
        
        # 构建响应，包含 parsed_docs
        response = {
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data["progress"],
            "current_step": task_data["current_step"],
            "error": task_data.get("error"),
            "result": result,
            "parsed_docs": task_data.get("parsed_docs", [])  # 添加 parsed_docs
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")


@router.get("/result/{task_id}", response_model=IntegratedVoiceoverResponse)
async def get_task_result(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取任务结果
    
    返回完整的口播稿生成结果，包括：
    - 风格配置
    - 证据台账
    - 图表台账
    - 结构设计
    - 审阅版口播稿
    - 上屏版口播稿
    """
    try:
        task_data = integrated_voiceover_service.get_task_status(task_id)
        
        if not task_data:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task_data["status"] == "processing":
            raise HTTPException(status_code=400, detail="任务还在处理中，请稍后再试")
        
        if task_data["status"] == "failed":
            error_msg = task_data.get("error", "未知错误")
            raise HTTPException(status_code=500, detail=f"任务处理失败: {error_msg}")
        
        result = integrated_voiceover_service.get_task_result(task_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="任务结果不存在")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task result: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@router.get("/list", response_model=List[dict])
async def list_tasks(
    current_user: dict = Depends(get_current_user)
):
    """
    列出所有任务
    
    返回用户的所有任务列表（简化信息）
    """
    try:
        # 获取所有任务
        tasks = []
        for task_id, task_data in integrated_voiceover_service.tasks.items():
            tasks.append({
                "task_id": task_id,
                "status": task_data["status"],
                "progress": task_data["progress"],
                "current_step": task_data["current_step"],
                "topic_hint": task_data["request"].get("topic_hint", ""),
                "files_count": len(task_data.get("files", [])),
                "created_at": task_data["created_at"],
                "updated_at": task_data["updated_at"]
            })
        
        # 按创建时间倒序排序
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.delete("/delete/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除任务
    
    删除指定的任务及其所有数据
    """
    try:
        if task_id not in integrated_voiceover_service.tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        del integrated_voiceover_service.tasks[task_id]
        
        logger.info(f"Deleted task {task_id} by user {current_user.get('username')}")
        
        return {
            "message": "任务已删除",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")
