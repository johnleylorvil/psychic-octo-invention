from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import User, UserCreate, UserInDB, Token
from utils.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from typing import Optional

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        # Vérifier si l'email existe déjà
        existing = await self.db.users.find_one({"email": user_data.email}, {"_id": 0})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        
        # Hash du mot de passe
        password_hash = get_password_hash(user_data.password)
        
        # Création de l'utilisateur
        user_dict = user_data.model_dump(exclude={"password"})
        user_in_db = UserInDB(**user_dict, password_hash=password_hash)
        
        # Conversion pour MongoDB
        doc = user_in_db.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        
        await self.db.users.insert_one(doc)
        
        return User(**user_dict, id=user_in_db.id, created_at=user_in_db.created_at, updated_at=user_in_db.updated_at)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user_doc = await self.db.users.find_one({"email": email}, {"_id": 0})
        if not user_doc:
            return None
        
        user = UserInDB(**user_doc)
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not user.actif:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte est désactivé"
            )
        
        # Création du token JWT
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email, "role": user.role}
        )
        
        user_response = User(**user.model_dump(exclude={"password_hash"}))
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_doc = await self.db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            return None
        return User(**user_doc)