import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models.email import Subscriber, EmailTemplate, EmailConfig, EmailTask
from app.schemas.email import SubscriberCreate, EmailTemplateCreate, EmailConfigCreate
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List, Optional
import io
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        pass

    # --- Subscriber Methods ---
    def get_subscribers(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Subscriber).offset(skip).limit(limit).all()

    def create_subscriber(self, db: Session, subscriber: SubscriberCreate):
        db_subscriber = Subscriber(**subscriber.model_dump())
        db.add(db_subscriber)
        db.commit()
        db.refresh(db_subscriber)
        return db_subscriber

    def delete_subscriber(self, db: Session, subscriber_id: int):
        db_subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
        if db_subscriber:
            db.delete(db_subscriber)
            db.commit()
            return True
        return False

    async def import_subscribers(self, db: Session, file: UploadFile):
        content = await file.read()
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            # Normalize columns
            df.columns = [c.lower().strip() for c in df.columns]
            
            if 'email' not in df.columns:
                raise HTTPException(status_code=400, detail="File must contain an 'email' column")
            
            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                email = str(row['email']).strip()
                name = str(row['name']).strip() if 'name' in df.columns else None
                
                # Check if exists
                existing = db.query(Subscriber).filter(Subscriber.email == email).first()
                if not existing:
                    try:
                        new_sub = Subscriber(email=email, name=name)
                        db.add(new_sub)
                        success_count += 1
                    except Exception as e:
                        errors.append(f"Row {index}: {str(e)}")
                else:
                    # Update name if provided
                    if name:
                        existing.name = name
            
            db.commit()
            return {"success_count": success_count, "errors": errors}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    # --- Template Methods ---
    def get_templates(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(EmailTemplate).offset(skip).limit(limit).all()

    def create_template(self, db: Session, template: EmailTemplateCreate):
        db_template = EmailTemplate(**template.model_dump())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
        
    def get_template(self, db: Session, template_id: int):
        return db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    def update_template(self, db: Session, template_id: int, template_data: dict):
        db_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        if not db_template:
            return None
        for key, value in template_data.items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
        return db_template

    def delete_template(self, db: Session, template_id: int):
        db_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        if db_template:
            db.delete(db_template)
            db.commit()
            return True
        return False

    # --- Config Methods ---
    def get_config(self, db: Session):
        return db.query(EmailConfig).filter(EmailConfig.is_active == True).first()

    def update_config(self, db: Session, config: EmailConfigCreate):
        # Deactivate all existing configs
        db.query(EmailConfig).update({"is_active": False})
        
        # Create new active config
        new_config = EmailConfig(**config.model_dump())
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config

    # --- Sending Logic ---
    async def send_email_batch(self, db: Session, template_id: int, subscriber_ids: Optional[List[int]] = None, test_email: Optional[str] = None):
        # 1. Get Config
        config = self.get_config(db)
        if not config:
            raise HTTPException(status_code=400, detail="Email configuration not found")
        
        # 2. Get Template
        template = self.get_template(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 3. Configure FastMail
        conf = ConnectionConfig(
            MAIL_USERNAME=config.smtp_username,
            MAIL_PASSWORD=config.smtp_password,
            MAIL_FROM=config.sender_email,
            MAIL_PORT=config.smtp_port,
            MAIL_SERVER=config.smtp_server,
            MAIL_FROM_NAME=config.sender_name or "VoxChina",
            MAIL_STARTTLS=config.use_tls,
            MAIL_SSL_TLS=not config.use_tls, # Assuming if not TLS then SSL, simplified logic
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        fm = FastMail(conf)
        
        # 4. Determine Recipients
        recipients = []
        if test_email:
            recipients.append({"email": test_email, "name": "Test User"})
        else:
            query = db.query(Subscriber).filter(Subscriber.is_active == True)
            if subscriber_ids:
                query = query.filter(Subscriber.id.in_(subscriber_ids))
            subs = query.all()
            for sub in subs:
                recipients.append({"email": sub.email, "name": sub.name})
        
        # 5. Send (Simplified loop, ideally use background tasks for individual or batch sending)
        # For bulk sending, FastMail supports list of recipients but template rendering might need individual context
        
        success = 0
        failed = 0
        
        # Create Task Record
        task = EmailTask(template_id=template_id, total_recipients=len(recipients), status="processing")
        if not test_email:
            db.add(task)
            db.commit()
        
        for recipient in recipients:
            try:
                message = MessageSchema(
                    subject=template.subject,
                    recipients=[recipient["email"]],
                    body=template.content, # TODO: Add variable substitution (e.g. {{name}})
                    subtype=MessageType.html
                )
                await fm.send_message(message)
                success += 1
                logger.info(f"✅ Email sent successfully to {recipient['email']}")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"❌ Failed to send to {recipient['email']}: {str(e)}")
                logger.error(f"详细错误:\n{error_trace}")
                logger.error(f"SMTP 配置: server={config.smtp_server}, port={config.smtp_port}, username={config.smtp_username}, from={config.sender_email}")
                failed += 1
        
        if not test_email:
            task.status = "completed"
            task.success_count = success
            task.failed_count = failed
            task.completed_at = func.now()
            db.commit()
            
        return {"total": len(recipients), "success": success, "failed": failed}

email_service = EmailService()
