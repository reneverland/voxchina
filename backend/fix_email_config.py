#!/usr/bin/env python3
"""
修正邮件配置 - 自动同步发件人邮箱为用户名
作者：Ren CBIT https://github.com/reneverland/
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import EmailConfig

def fix_email_config():
    """修正邮件配置，确保发件人邮箱和用户名一致"""
    db = SessionLocal()
    
    try:
        config = db.query(EmailConfig).filter(EmailConfig.is_active == True).first()
        
        if not config:
            print("❌ 没有找到活动的 SMTP 配置")
            return
        
        print("=" * 60)
        print("📧 当前配置:")
        print("=" * 60)
        print(f"SMTP 服务器: {config.smtp_server}")
        print(f"SMTP 端口: {config.smtp_port}")
        print(f"用户名: {config.smtp_username}")
        print(f"密码: {'*' * len(config.smtp_password) if config.smtp_password else 'None'}")
        print(f"发件人邮箱: {config.sender_email}")
        print(f"发件人名称: {config.sender_name}")
        print(f"TLS: {config.use_tls}")
        print()
        
        # 检查是否需要修正
        if config.sender_email != config.smtp_username:
            print("⚠️  发现问题：")
            print(f"   用户名: {config.smtp_username}")
            print(f"   发件人: {config.sender_email}")
            print()
            print("❌ 发件人邮箱和用户名不一致！")
            print("   这会导致邮件发送失败（Gmail、Outlook 等服务器会拒绝）")
            print()
            
            response = input("是否自动修正为相同邮箱？(y/n): ").strip().lower()
            
            if response == 'y':
                old_sender = config.sender_email
                config.sender_email = config.smtp_username
                db.commit()
                
                print()
                print("✅ 已修正配置:")
                print(f"   旧的发件人: {old_sender}")
                print(f"   新的发件人: {config.sender_email}")
                print()
                print("✅ 配置已保存！")
                print()
                print("📝 下一步：")
                print("   1. 刷新 VoxChina 页面")
                print("   2. 点击'测试连接'按钮")
                print("   3. 检查您的邮箱（包括垃圾邮件文件夹）")
            else:
                print()
                print("⚠️  未修改配置")
                print("   建议手动在前端修改发件人邮箱为:", config.smtp_username)
        else:
            print("✅ 配置正确：发件人邮箱和用户名一致")
            print()
            
            # 提供额外的检查建议
            print("📝 额外检查建议:")
            print()
            
            if 'gmail.com' in config.smtp_server:
                print("🔹 Gmail 配置:")
                print("   ✓ 服务器: smtp.gmail.com")
                print("   ✓ 端口: 587")
                print("   ✓ TLS: 启用")
                print("   ✓ 密码: 应用专用密码（不是账户密码）")
                print("   🔗 生成应用密码: https://myaccount.google.com/apppasswords")
            elif 'outlook.com' in config.smtp_server or 'office365.com' in config.smtp_server:
                print("🔹 Outlook 配置:")
                print("   ✓ 服务器: smtp-mail.outlook.com")
                print("   ✓ 端口: 587")
                print("   ✓ TLS: 启用")
                print("   ✓ 密码: 应用密码（不是账户密码）")
                print("   🔗 生成应用密码: https://account.microsoft.com/security")
            
            print()
            print("如果还是收不到邮件，请检查：")
            print("   • 密码是否使用应用专用密码（而不是账户密码）")
            print("   • 邮箱是否被锁定或限制")
            print("   • 垃圾邮件文件夹")
    
    finally:
        db.close()

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🔧 VoxChina 邮件配置修复工具")
    print("=" * 60)
    print()
    
    fix_email_config()
    
    print()
    print("=" * 60)
