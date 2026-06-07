import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required!")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "d8f74e6c38b292e1069dfb4a45ad8cbe5fe6d4f10738a95d0bf0a1f0a1c1d8ea")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")
ENV = os.getenv("ENV", "production")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
