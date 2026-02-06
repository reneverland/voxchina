#!/usr/bin/env python3
"""
更新所有邮件模板，在顶部添加 VoxChina Logo
"""
import sys
sys.path.append('/www/wwwroot/voxchina/backend')

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import EmailTemplate

# Logo HTML (居中显示，宽度200px)
LOGO_HTML = '''
<div style="text-align: center; margin-bottom: 30px;">
  <img src="http://llmhi.com:8400/voxchinalogo1.jpg" alt="VoxChina Logo" style="width: 200px; height: auto;">
</div>
'''

def update_templates():
    db: Session = SessionLocal()
    try:
        # 获取所有模板
        templates = db.query(EmailTemplate).all()
        
        print(f"找到 {len(templates)} 个模板")
        
        for template in templates:
            # 检查是否已经包含 logo
            if 'voxchinalogo' in template.content.lower():
                print(f"✓ 模板 '{template.name}' 已包含 logo，跳过")
                continue
            
            # 在内容顶部添加 logo
            # 找到 <body> 标签后的位置插入
            if '<body' in template.content:
                # 找到 <body> 标签的结束位置
                body_start = template.content.find('<body')
                body_tag_end = template.content.find('>', body_start) + 1
                
                # 在 <body> 后插入 logo
                new_content = (
                    template.content[:body_tag_end] + 
                    LOGO_HTML + 
                    template.content[body_tag_end:]
                )
                template.content = new_content
                print(f"✓ 已更新模板 '{template.name}'")
            else:
                # 如果没有 <body> 标签，在开头添加
                template.content = LOGO_HTML + template.content
                print(f"✓ 已更新模板 '{template.name}' (无body标签)")
        
        # 提交更改
        db.commit()
        print(f"\n✅ 成功更新所有模板！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_templates()
