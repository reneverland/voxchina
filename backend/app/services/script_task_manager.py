"""
口播稿生成任务管理器
负责长任务的状态跟踪、进度推送、结果存储
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class TaskState:
    """任务状态"""
    def __init__(self, task_id: str, params: Dict[str, Any]):
        self.task_id = task_id
        self.params = params
        self.status = "pending"  # pending, processing, completed, failed
        self.stage = "init"  # init, parsing, chunking, extracting, outlining, writing, verifying, exporting
        self.progress = {
            "percent": 0,
            "doc_current": 0,
            "doc_total": 0,
            "chunk_current": 0,
            "chunk_total": 0
        }
        self.timing = {
            "start_time": time.time(),
            "elapsed_ms": 0
        }
        self.detail = ""
        self.severity = "info"  # info, warning, error, success
        
        # 结果
        self.result = None
        self.error = None
        
        # 中间数据（用于审计）
        self.evidence_ledgers = []
        self.audit_report = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "stage": self.stage,
            "progress": self.progress,
            "timing": {
                **self.timing,
                "elapsed_ms": int((time.time() - self.timing["start_time"]) * 1000)
            },
            "detail": self.detail,
            "severity": self.severity,
            "result": self.result,
            "error": self.error
        }


class ScriptTaskManager:
    """口播稿生成任务管理器（单例）"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskState] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(self, task_id: str, params: Dict[str, Any]) -> TaskState:
        """创建新任务"""
        async with self._lock:
            task = TaskState(task_id, params)
            self.tasks[task_id] = task
            logger.info(f"Created task: {task_id}")
            return task
    
    async def get_task(self, task_id: str) -> Optional[TaskState]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    async def update_stage(
        self, 
        task_id: str, 
        stage: str, 
        detail: str = "", 
        severity: str = "info"
    ):
        """更新任务阶段"""
        task = self.tasks.get(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return
        
        task.stage = stage
        task.detail = detail
        task.severity = severity
        task.status = "processing"
        
        # 计算总体进度
        stage_weights = {
            "init": 0,
            "parsing": 10,
            "chunking": 20,
            "extracting": 50,
            "outlining": 65,
            "writing": 80,
            "verifying": 90,
            "exporting": 95
        }
        task.progress["percent"] = stage_weights.get(stage, 0)
        
        logger.info(f"Task {task_id} -> {stage}: {detail}")
    
    async def update_progress(
        self,
        task_id: str,
        doc_current: int = None,
        doc_total: int = None,
        chunk_current: int = None,
        chunk_total: int = None
    ):
        """更新任务进度"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        if doc_current is not None:
            task.progress["doc_current"] = doc_current
        if doc_total is not None:
            task.progress["doc_total"] = doc_total
        if chunk_current is not None:
            task.progress["chunk_current"] = chunk_current
        if chunk_total is not None:
            task.progress["chunk_total"] = chunk_total
    
    async def complete_task(
        self, 
        task_id: str, 
        result: Dict[str, Any],
        evidence_ledgers: list = None,
        audit_report: dict = None
    ):
        """完成任务"""
        task = self.tasks.get(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return
        
        task.status = "completed"
        task.stage = "completed"
        task.progress["percent"] = 100
        task.result = result
        task.evidence_ledgers = evidence_ledgers or []
        task.audit_report = audit_report or {}
        task.severity = "success"
        task.detail = "口播稿生成成功"
        
        logger.info(f"Task {task_id} completed successfully")
    
    async def fail_task(self, task_id: str, error: str):
        """任务失败"""
        task = self.tasks.get(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return
        
        task.status = "failed"
        task.stage = "failed"
        task.error = error
        task.severity = "error"
        task.detail = f"生成失败: {error}"
        
        logger.error(f"Task {task_id} failed: {error}")
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务（可选，避免内存泄漏）"""
        async with self._lock:
            current_time = time.time()
            to_remove = []
            
            for task_id, task in self.tasks.items():
                age_hours = (current_time - task.timing["start_time"]) / 3600
                if age_hours > max_age_hours:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
                logger.info(f"Cleaned up old task: {task_id}")


# 全局单例
script_task_manager = ScriptTaskManager()

