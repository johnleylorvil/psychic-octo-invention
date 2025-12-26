from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

ActionType = Literal["lecture", "création", "modification", "suppression"]
RessourceType = Literal["patient", "consultation", "prescription", "facture", "utilisateur", "autre"]

class AuditLogBase(BaseModel):
    user_id: str
    user_role: str
    action: ActionType
    ressource_type: RessourceType
    ressource_id: str
    details: Optional[str] = None
    ip_address: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))