from pathlib import Path
from dotenv import load_dotenv

import os

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"


load_dotenv(PROJECT_ROOT / ".env", override=True)

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

FRENCH_MONTHS = {
    "janvier": "01",
    "février": "02",
    "mars": "03",
    "avril": "04",
    "mai": "05",
    "juin": "06",
    "juillet": "07",
    "août": "08",
    "septembre": "09",
    "octobre": "10",
    "novembre": "11",
    "décembre": "12",
}
if __name__ == "__main__":
    print(PROJECT_ROOT)