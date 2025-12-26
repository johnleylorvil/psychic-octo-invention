from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

class ServiceBase(BaseModel):
    nom: str
    description: Optional[str] = None
    chef_service_id: Optional[str] = None
    nombre_lits: int = 0
    etage: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    chef_service_id: Optional[str] = None
    nombre_lits: Optional[int] = None
    etage: Optional[str] = None

class Service(ServiceBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

StatutLit = Literal["disponible", "occupé", "maintenance", "réservé"]

class LitBase(BaseModel):
    numero: str
    service_id: str
    statut: StatutLit = "disponible"
    patient_id: Optional[str] = None
    date_admission: Optional[datetime] = None
    notes: Optional[str] = None

class LitCreate(LitBase):
    pass

class LitUpdate(BaseModel):
    statut: Optional[StatutLit] = None
    patient_id: Optional[str] = None
    date_admission: Optional[datetime] = None
    notes: Optional[str] = None

class Lit(LitBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))