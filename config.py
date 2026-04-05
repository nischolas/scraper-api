from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.0.194:5173",
    "http://mbpvn.local:5173",
]