from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserCreate, Token
from services.auth_service import AuthService
from pydantic import BaseModel
import os

router = APIRouter(prefix="/auth", tags=["Authentification"])

class LoginRequest(BaseModel):
    email: str
    password: str

def get_db():
    from server import db
    return db

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    Seul l'admin peut créer des comptes pour le personnel.
    """
    auth_service = AuthService(db)
    user = await auth_service.create_user(user_data)
    return {"message": "Utilisateur créé avec succès", "user_id": user.id}

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Connexion et génération du token JWT.
    """
    auth_service = AuthService(db)
    return await auth_service.login(login_data.email, login_data.password)

@router.get("/me")
async def get_current_user_info(current_user = Depends(lambda: None)):
    """
    Récupère les informations de l'utilisateur connecté.
    """
    return current_user