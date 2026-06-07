from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import config, database, models
from app.routers import auth, students, analytics, career

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Tables automatically (Alembic-free)
    models.Base.metadata.create_all(bind=database.engine)
    
    # 2. Seed development-only credentials and data if ENV=development
    if config.ENV == "development":
        from app.seed import seed_data
        db = database.SessionLocal()
        try:
            seed_data(db)
        except Exception as e:
            print(f"Error seeding database: {e}")
        finally:
            db.close()
            
    # 3. Auto-train & save prediction model if model.pkl is missing
    from app.ml_model import ensure_storage, load_model
    try:
        ensure_storage()
        load_model()  # This trains the model if pkl is missing
    except Exception as e:
        print(f"Error initializing ML model: {e}")
        
    yield

# Create FastAPI App with Lifespan
app = FastAPI(
    title="StudentCareer System API",
    description="Backend API for AI-Based Student Performance Analytics & Career Guidance System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = []
if config.FRONTEND_URL:
    if "," in config.FRONTEND_URL:
        origins = [o.strip() for o in config.FRONTEND_URL.split(",") if o.strip()]
    else:
        origins = [config.FRONTEND_URL]
else:
    origins = ["*"]

# In FastAPI, allow_credentials=True cannot be used with "*" origins
allow_all_origins = "*" in origins or not origins
allow_creds = not allow_all_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Railway Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# 5. Include API Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(analytics.router)
app.include_router(career.router)
