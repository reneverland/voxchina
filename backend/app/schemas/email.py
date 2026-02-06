from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Subscriber Schemas ---
class SubscriberBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    is_active: Optional[bool] = True

class SubscriberCreate(SubscriberBase):
    pass

class SubscriberUpdate(SubscriberBase):
    pass

class Subscriber(SubscriberBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Template Schemas ---
class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    content: str

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateUpdate(EmailTemplateBase):
    pass

class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Config Schemas ---
class EmailConfigBase(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: EmailStr
    sender_name: Optional[str] = None
    use_tls: Optional[bool] = True
    is_active: Optional[bool] = True

class EmailConfigCreate(EmailConfigBase):
    pass

class EmailConfigUpdate(EmailConfigBase):
    pass

class EmailConfig(EmailConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Task Schemas ---
class EmailTaskBase(BaseModel):
    template_id: int
    status: str
    total_recipients: int
    success_count: int
    failed_count: int
    error_message: Optional[str] = None

class EmailTaskCreate(BaseModel):
    template_id: int
    subject_override: Optional[str] = None # Allow overriding template subject

class EmailTask(EmailTaskBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmailSendRequest(BaseModel):
    template_id: int
    subscriber_ids: Optional[List[int]] = None # If None, send to all active
    test_email: Optional[EmailStr] = None # If provided, only send test email
