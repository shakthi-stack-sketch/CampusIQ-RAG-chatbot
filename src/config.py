import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Documents folder
DATA_PATH = BASE_DIR / "data" / "college_documents"

# Vector database folder
VECTORSTORE_PATH = BASE_DIR / "vectorstore"