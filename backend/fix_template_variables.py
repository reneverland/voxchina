#!/usr/bin/env python3
"""修复模板中的变量格式：{variable} -> {{variable}}"""
import sys
import re
sys.path.append('/www/wwwroot/voxchina/backend')

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import EmailTemplate

db = SessionLocal()
try:
    templates = db.query(EmailTemplate).all()
    print(f"修复 {len(templates)} 个模板的变量格式...")
    print()
    
    for t in templates:
        old_content = t.content
        new_content = old_content
        
        # 只替换单个花括号的变量为双花括号
        # 使用负向环视确保不重复替换已经是 {{}} 的部分
        new_content = re.sub(r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})', r'{{\1}}', new_content)
        
        if old_content != new_content:
            t.content = new_content
            changes = len(re.findall(r'\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}', new_content))
            print(f"✓ {t.name}")
            print(f"  修复了变量格式，现在有 {changes} 个变量")
        else:
            print(f"○ {t.name} - 无需修复")
        print()
    
    db.commit()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 所有模板变量格式已修复！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
