from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, date, timezone
import uuid

GroupeSanguin = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

class DonneurSangBase(BaseModel):
    nom: str
    prenom: str
    groupe_sanguin: GroupeSanguin
    telephone: str
    email: Optional[str] = None
    adresse: Optional[str] = None
    date_derniere_donation: Optional[date] = None
    eligible: bool = True
    notes_medicales: Optional[str] = None

class DonneurSangCreate(DonneurSangBase):
    pass

class DonneurSangUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    groupe_sanguin: Optional[GroupeSanguin] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    date_derniere_donation: Optional[date] = None
    eligible: Optional[bool] = None
    notes_medicales: Optional[str] = None

class DonneurSang(DonneurSangBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StockSangBase(BaseModel):
    groupe_sanguin: GroupeSanguin
    quantite_ml: int
    numero_poche: str
    date_collecte: date
    date_expiration: date
    donneur_id: Optional[str] = None
    statut: Literal["disponible", "réservé", "utilisé", "expiré"] = "disponible"

class StockSangCreate(StockSangBase):
    pass

class StockSangUpdate(BaseModel):
    quantite_ml: Optional[int] = None
    statut: Optional[Literal["disponible", "réservé", "utilisé", "expiré"]] = None

class StockSang(StockSangBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))