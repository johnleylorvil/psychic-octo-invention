from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

TypeRdv = Literal["présentiel", "en_ligne"]
StatutRdv = Literal["planifié", "confirmé", "annulé", "terminé", "en_attente"]

class RendezVousBase(BaseModel):
    patient_id: str
    medecin_id: str
    date_rdv: datetime
    type_rdv: TypeRdv = "présentiel"
    motif: Optional[str] = None
    online_meeting_url: Optional[str] = None
    statut: StatutRdv = "planifié"
    notes: Optional[str] = None

class RendezVousCreate(RendezVousBase):
    pass

class RendezVousUpdate(BaseModel):
    date_rdv: Optional[datetime] = None
    type_rdv: Optional[TypeRdv] = None
    motif: Optional[str] = None
    online_meeting_url: Optional[str] = None
    statut: Optional[StatutRdv] = None
    notes: Optional[str] = None

class RendezVous(RendezVousBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))