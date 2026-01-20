#!/usr/bin/env python3
"""
测试异步任务处理
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import IntegratedVoiceoverRequest
from app.services.integrated_voiceover_service import integrated_voiceover_service


async def test_async_task():
    """测试异步任务创建"""
    print("=" * 60)
    print("Testing Async Task Creation")
    print("=" * 60)
    
    # 创建测试请求
    request = IntegratedVoiceoverRequest(
        topic_hint="测试主题：中国数字经济发展",
        speaker_affiliation="VoxChina",
        speaker_name="测试主播",
        include_vox_intro=True,
        language="zh"
    )
    
    # 创建测试文件内容（简单的文本）
    test_content = b"""
Test Document

This is a test document for integrated voiceover.

Background
China's digital economy has grown rapidly in recent years.

Data
In 2020, the digital economy reached 39.2 trillion yuan.
This represents 38.6% of GDP.

Conclusion
The digital economy is becoming increasingly important.
"""
    
    files = [("test_document.txt", test_content)]
    
    print("\n1. Creating task...")
    task_id = await integrated_voiceover_service.create_task(request, files)
    print(f"✅ Task created: {task_id}")
    print("✅ Function returned immediately (async background processing)")
    
    print("\n2. Checking initial status...")
    await asyncio.sleep(0.5)  # Wait a bit for task to start
    task_status = integrated_voiceover_service.get_task_status(task_id)
    if task_status:
        print(f"✅ Status: {task_status['status']}")
        print(f"✅ Progress: {task_status['progress']}%")
        print(f"✅ Current step: {task_status['current_step']}")
    else:
        print("❌ Task not found")
    
    print("\n3. Waiting for task to progress...")
    for i in range(10):  # Wait up to 30 seconds
        await asyncio.sleep(3)
        task_status = integrated_voiceover_service.get_task_status(task_id)
        if task_status:
            print(f"   [{i*3}s] Status: {task_status['status']}, Progress: {task_status['progress']}%, Step: {task_status['current_step']}")
            if task_status['status'] in ['completed', 'failed']:
                break
    
    print("\n4. Final status...")
    task_status = integrated_voiceover_service.get_task_status(task_id)
    if task_status:
        print(f"✅ Final status: {task_status['status']}")
        if task_status['status'] == 'failed':
            print(f"❌ Error: {task_status.get('error', 'Unknown error')}")
        elif task_status['status'] == 'completed':
            print(f"✅ Task completed successfully!")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_async_task())
