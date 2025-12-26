from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import des routers
from routers import auth, users, patients, appointments, consultations
from routers import pharmacy, blood_bank, billing, services, dashboard

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(
    title="Système de Gestion de Clinique",
    description="API REST pour la gestion complète d'une clinique médicale",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Include all routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(consultations.router, prefix="/api")
app.include_router(pharmacy.router, prefix="/api")
app.include_router(blood_bank.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/api")
async def root():
    return {
        "message": "Bienvenue sur l'API du Système de Gestion de Clinique",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
