from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, date, timezone
import uuid

SexeType = Literal["M", "F", "Autre"]
GroupeSanguin = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

class PatientBase(BaseModel):
    user_id: str
    numero_dossier: str
    date_naissance: date
    sexe: SexeType
    groupe_sanguin: Optional[GroupeSanguin] = None
    adresse: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_tel: Optional[str] = None
    historique_medical: Optional[str] = None
    allergies: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    date_naissance: Optional[date] = None
    sexe: Optional[SexeType] = None
    groupe_sanguin: Optional[GroupeSanguin] = None
    adresse: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_tel: Optional[str] = None
    historique_medical: Optional[str] = None
    allergies: Optional[str] = None

class Patient(PatientBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))