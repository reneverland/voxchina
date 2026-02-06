from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from typing import List
import os
from app.api.v1.endpoints.auth import get_superadmin_user
from loguru import logger

router = APIRouter()


@router.get("/list")
async def list_images(current_user: dict = Depends(get_superadmin_user)):
    """
    列出所有提取的图片
    需要 SUPERADMIN 权限
    """
    try:
        image_dir = Path("static/images/extracted")
        if not image_dir.exists():
            return {"images": [], "total": 0}
        
        images = []
        for img_file in image_dir.glob("*.*"):
            if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                stat = img_file.stat()
                images.append({
                    "filename": img_file.name,
                    "url": f"/static/images/extracted/{img_file.name}",
                    "size": stat.st_size,
                    "created": stat.st_mtime
                })
        
        # 按创建时间倒序排序
        images.sort(key=lambda x: x['created'], reverse=True)
        
        return {
            "images": images,
            "total": len(images),
            "total_size": sum(img['size'] for img in images)
        }
    except Exception as e:
        logger.error(f"Failed to list images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{filename}")
async def delete_image(filename: str, current_user: dict = Depends(get_superadmin_user)):
    """
    删除指定图片
    需要 SUPERADMIN 权限
    """
    try:
        # 安全检查：防止路径遍历攻击
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        image_path = Path("static/images/extracted") / filename
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # 删除文件
        image_path.unlink()
        logger.info(f"Deleted image: {filename} by user {current_user.get('username')}")
        
        return {"status": "success", "message": f"Image {filename} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete image {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_images(days: int = 30, current_user: dict = Depends(get_superadmin_user)):
    """
    清理超过指定天数的旧图片
    需要 SUPERADMIN 权限
    """
    try:
        import time
        
        image_dir = Path("static/images/extracted")
        if not image_dir.exists():
            return {"deleted": 0, "message": "Image directory not found"}
        
        now = time.time()
        cutoff = now - (days * 24 * 60 * 60)
        
        deleted_count = 0
        deleted_size = 0
        
        for img_file in image_dir.glob("*.*"):
            if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                if img_file.stat().st_mtime < cutoff:
                    size = img_file.stat().st_size
                    img_file.unlink()
                    deleted_count += 1
                    deleted_size += size
        
        logger.info(f"Cleaned up {deleted_count} images ({deleted_size} bytes) older than {days} days")
        
        return {
            "deleted": deleted_count,
            "freed_space": deleted_size,
            "message": f"Deleted {deleted_count} images older than {days} days"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
