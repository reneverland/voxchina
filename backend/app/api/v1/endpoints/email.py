from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import SessionLocal
from app.services.email_service import email_service
from app.schemas.email import (
    Subscriber, SubscriberCreate, 
    EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate,
    EmailConfig, EmailConfigCreate,
    EmailSendRequest
)

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Subscribers ---
@router.get("/subscribers", response_model=List[Subscriber])
def read_subscribers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve subscribers.
    """
    subscribers = email_service.get_subscribers(db, skip=skip, limit=limit)
    return subscribers

@router.post("/subscribers", response_model=Subscriber)
def create_subscriber(subscriber: SubscriberCreate, db: Session = Depends(get_db)):
    """
    Create new subscriber.
    """
    return email_service.create_subscriber(db, subscriber)

@router.post("/subscribers/upload")
async def upload_subscribers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload Excel/CSV to bulk import subscribers.
    """
    return await email_service.import_subscribers(db, file)

@router.delete("/subscribers/{subscriber_id}")
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    """
    Delete a subscriber.
    """
    success = email_service.delete_subscriber(db, subscriber_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return {"status": "success"}

# --- Templates ---
@router.get("/templates", response_model=List[EmailTemplate])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve email templates.
    """
    return email_service.get_templates(db, skip=skip, limit=limit)

@router.post("/templates", response_model=EmailTemplate)
def create_template(template: EmailTemplateCreate, db: Session = Depends(get_db)):
    """
    Create new email template.
    """
    return email_service.create_template(db, template)

@router.put("/templates/{template_id}", response_model=EmailTemplate)
def update_template(template_id: int, template: EmailTemplateUpdate, db: Session = Depends(get_db)):
    """
    Update email template.
    """
    db_template = email_service.update_template(db, template_id, template.model_dump(exclude_unset=True))
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """
    Delete email template.
    """
    success = email_service.delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "success"}

# --- Config ---
@router.get("/config", response_model=EmailConfig)
def read_config(db: Session = Depends(get_db)):
    """
    Get current active email config.
    """
    config = email_service.get_config(db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not set")
    return config

@router.post("/test-connection")
async def test_smtp_connection(config: EmailConfigCreate):
    """
    Test SMTP connection without saving.
    """
    from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
    
    try:
        # Configure FastMail with provided settings
        conf = ConnectionConfig(
            MAIL_USERNAME=config.smtp_username,
            MAIL_PASSWORD=config.smtp_password,
            MAIL_FROM=config.sender_email,
            MAIL_PORT=config.smtp_port,
            MAIL_SERVER=config.smtp_server,
            MAIL_FROM_NAME=config.sender_name or "VoxChina",
            MAIL_STARTTLS=config.use_tls,
            MAIL_SSL_TLS=not config.use_tls,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        fm = FastMail(conf)
        
        # Try to send a test email to sender's own email
        message = MessageSchema(
            subject="VoxChina SMTP 连接测试 / Connection Test",
            recipients=[config.sender_email],
            body="""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">✅ SMTP 连接测试成功！</h2>
                <p>您的邮件服务器配置正确，可以正常发送邮件。</p>
                <hr>
                <h2 style="color: #2563eb;">✅ SMTP Connection Test Successful!</h2>
                <p>Your email server configuration is correct and ready to send emails.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Server: {}<br>
                    Port: {}<br>
                    TLS: {}<br>
                    From: {} &lt;{}&gt;
                </p>
            </body>
            </html>
            """.format(
                config.smtp_server,
                config.smtp_port,
                "Enabled" if config.use_tls else "Disabled",
                config.sender_name or "VoxChina",
                config.sender_email
            ),
            subtype=MessageType.html
        )
        
        await fm.send_message(message)
        
        return {
            "success": True,
            "message": "SMTP连接测试成功！已发送测试邮件到您的邮箱。",
            "message_en": "SMTP connection test successful! Test email sent to your mailbox."
        }
        
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        
        return {
            "success": False,
            "message": f"SMTP连接失败：{error_detail}",
            "message_en": f"SMTP connection failed: {error_detail}",
            "error_detail": error_trace
        }

@router.post("/config", response_model=EmailConfig)
def update_config(config: EmailConfigCreate, db: Session = Depends(get_db)):
    """
    Set/Update email configuration.
    """
    return email_service.update_config(db, config)

# --- Sending ---
@router.post("/send")
async def send_email(
    request: EmailSendRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send emails (Test or Batch).
    If test_email is provided, sends immediately to that address.
    Otherwise, schedules a background task to send to subscribers.
    """
    if request.test_email:
        # Send immediately for test
        result = await email_service.send_email_batch(
            db, 
            request.template_id, 
            test_email=request.test_email
        )
        return result
    else:
        # Background task for batch
        background_tasks.add_task(
            email_service.send_email_batch, 
            db, 
            request.template_id, 
            request.subscriber_ids
        )
        return {"message": "Batch email sending started in background"}
