#!/usr/bin/env python3
"""
测试 Integrated Voiceover API
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import (
    IntegratedVoiceoverRequest,
    EvidenceLedger,
    EvidenceFinding,
    VisualAsset,
    VisualAssetLedger,
    StyleProfile
)

def test_schemas():
    """测试数据模型"""
    print("Testing schemas...")
    
    # Test IntegratedVoiceoverRequest
    request = IntegratedVoiceoverRequest(
        topic_hint="测试主题",
        speaker_affiliation="VoxChina",
        speaker_name="测试主播",
        include_vox_intro=True,
        style_preference="S1",
        language="zh"
    )
    print(f"✓ IntegratedVoiceoverRequest: {request.topic_hint}")
    
    # Test EvidenceFinding
    finding = EvidenceFinding(
        finding_index=1,
        type="数据描述",
        claim="测试事实",
        numbers=["2020年", "15%"],
        linked_assets=["D1-FIG-1"],
        source_doc_id="D1"
    )
    print(f"✓ EvidenceFinding: {finding.claim}")
    
    # Test VisualAsset
    asset = VisualAsset(
        asset_id="D1-FIG-1",
        asset_type="FIG",
        original_label="图1",
        caption_or_title="测试图表",
        location_anchor="测试锚点",
        key_numbers=["100", "200"],
        takeaway_claim="测试要点",
        linked_findings=[1, 2],
        editing_instruction="突出主要趋势"
    )
    print(f"✓ VisualAsset: {asset.asset_id}")
    
    # Test EvidenceLedger
    ledger = EvidenceLedger(
        doc_id="D1",
        title="测试文档",
        time_range="2020-2025",
        findings=[finding]
    )
    print(f"✓ EvidenceLedger: {ledger.doc_id}")
    
    # Test VisualAssetLedger
    asset_ledger = VisualAssetLedger(
        assets=[asset]
    )
    print(f"✓ VisualAssetLedger: {len(asset_ledger.assets)} assets")
    
    # Test StyleProfile
    style = StyleProfile(
        enable_vox_intro=True,
        main_structure="S1",
        figure_style="A",
        rules=["规则1", "规则2"]
    )
    print(f"✓ StyleProfile: {style.main_structure}")
    
    print("\n✅ All schema tests passed!")

def test_service_import():
    """测试服务导入"""
    print("\nTesting service imports...")
    
    try:
        from app.services.integrated_voiceover_service import integrated_voiceover_service
        print("✓ IntegratedVoiceoverService imported successfully")
        
        # 检查服务方法
        assert hasattr(integrated_voiceover_service, 'create_task')
        assert hasattr(integrated_voiceover_service, 'get_task_status')
        assert hasattr(integrated_voiceover_service, 'get_task_result')
        print("✓ Service methods available")
        
        print("\n✅ Service import tests passed!")
        
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        raise

def test_api_import():
    """测试API导入"""
    print("\nTesting API imports...")
    
    try:
        from app.api.v1.endpoints import integrated_voiceover
        print("✓ API endpoint imported successfully")
        
        # 检查路由
        assert hasattr(integrated_voiceover, 'router')
        print("✓ Router available")
        
        print("\n✅ API import tests passed!")
        
    except Exception as e:
        print(f"❌ API import failed: {e}")
        raise

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Integrated Voiceover Feature Tests")
    print("=" * 60)
    
    try:
        test_schemas()
        test_service_import()
        test_api_import()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TESTS FAILED: {e}")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
