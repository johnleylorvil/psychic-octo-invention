from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date, timezone
import uuid

class CategorieMedicamentBase(BaseModel):
    nom: str
    description: Optional[str] = None

class CategorieMedicamentCreate(CategorieMedicamentBase):
    pass

class CategorieMedicament(CategorieMedicamentBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MedicamentBase(BaseModel):
    nom: str
    categorie_id: str
    description: Optional[str] = None
    forme: Optional[str] = None  # comprimé, sirop, injection, etc.
    dosage: Optional[str] = None
    prix_unitaire: float
    seuil_stock_min: int = 10
    fabricant: Optional[str] = None

class MedicamentCreate(MedicamentBase):
    pass

class MedicamentUpdate(BaseModel):
    nom: Optional[str] = None
    categorie_id: Optional[str] = None
    description: Optional[str] = None
    forme: Optional[str] = None
    dosage: Optional[str] = None
    prix_unitaire: Optional[float] = None
    seuil_stock_min: Optional[int] = None
    fabricant: Optional[str] = None

class Medicament(MedicamentBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StockPharmacieBase(BaseModel):
    medicament_id: str
    quantite: int
    date_peremption: date
    numero_lot: str
    emplacement: Optional[str] = None

class StockPharmacieCreate(StockPharmacieBase):
    pass

class StockPharmacieUpdate(BaseModel):
    quantite: Optional[int] = None
    date_peremption: Optional[date] = None
    numero_lot: Optional[str] = None
    emplacement: Optional[str] = None

class StockPharmacie(StockPharmacieBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))