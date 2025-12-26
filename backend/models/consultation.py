from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class MedicamentPrescrit(BaseModel):
    medicament_id: str
    nom: str
    dosage: str
    frequence: str
    duree: str

class ConsultationBase(BaseModel):
    patient_id: str
    medecin_id: str
    rendez_vous_id: Optional[str] = None
    date_consultation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    motif: str
    symptomes: Optional[str] = None
    diagnostic: Optional[str] = None
    traitement: Optional[str] = None
    notes: Optional[str] = None
    examens_demandes: Optional[str] = None

class ConsultationCreate(ConsultationBase):
    pass

class ConsultationUpdate(BaseModel):
    motif: Optional[str] = None
    symptomes: Optional[str] = None
    diagnostic: Optional[str] = None
    traitement: Optional[str] = None
    notes: Optional[str] = None
    examens_demandes: Optional[str] = None

class Consultation(ConsultationBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PrescriptionBase(BaseModel):
    consultation_id: str
    patient_id: str
    medecin_id: str
    medicaments: List[MedicamentPrescrit]
    instructions_generales: Optional[str] = None
    date_validite: Optional[datetime] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))