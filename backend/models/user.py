from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

RoleType = Literal["admin", "médecin", "infirmière", "pharmacien", "comptable", "patient"]

class UserBase(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    role: RoleType
    telephone: Optional[str] = None
    specialite: Optional[str] = None  # Pour les médecins
    actif: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    specialite: Optional[str] = None
    actif: Optional[bool] = None

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserInDB(User):
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None