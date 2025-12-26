from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime, timezone
import uuid

class ItemFacture(BaseModel):
    description: str
    quantite: int = 1
    prix_unitaire: float
    total: float

class FactureBase(BaseModel):
    patient_id: str
    montant_total: float
    statut: Literal["en_attente", "payée", "partiellement_payée", "annulée"] = "en_attente"
    items: List[ItemFacture]
    notes: Optional[str] = None
    date_echeance: Optional[datetime] = None

class FactureCreate(FactureBase):
    pass

class FactureUpdate(BaseModel):
    statut: Optional[Literal["en_attente", "payée", "partiellement_payée", "annulée"]] = None
    notes: Optional[str] = None
    date_echeance: Optional[datetime] = None

class Facture(FactureBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_facture: str = Field(default_factory=lambda: f"FAC-{uuid.uuid4().hex[:8].upper()}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaiementBase(BaseModel):
    facture_id: str
    montant: float
    methode: Literal["espèces", "carte", "virement", "assurance", "mobile_money"]
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaiementCreate(PaiementBase):
    pass

class Paiement(PaiementBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date_paiement: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))