"""Configuración central. Gestor: PostgreSQL (tres bases: stg_oece, dw_oece, dm_monitoreo).
Usuario/clave/servidor por variables de entorno PGUSER, PGPASSWORD, PGHOST, PGPORT (por defecto postgres/postgres@localhost:5432).
Para pruebas sin PostgreSQL: DB_MOTOR=sqlite."""
import os
from urllib.parse import quote_plus
from pathlib import Path
from sqlalchemy import create_engine

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("OECE_DATA", BASE / "data"))        # CSV descargados: data/<año>/<año>/*.csv
SALIDA = BASE / "salida"; SALIDA.mkdir(exist_ok=True)
(BASE / "db").mkdir(exist_ok=True)

# --- Conexión a PostgreSQL (valores por defecto; cámbialos con variables de entorno) -----------------
PG_USER = os.environ.get("PGUSER", "postgres")
PG_PASS = os.environ.get("PGPASSWORD", "postgres")
PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = os.environ.get("PGPORT", "5432")
PG_DRIVER = os.environ.get("PG_DRIVER", "psycopg2")        # o "psycopg" (v3) si psycopg2 no instala en tu Python
DB_STG, DB_DW, DB_DM = "stg_oece", "dw_oece", "dm_monitoreo"

def _url(db):
    if os.environ.get("DB_MOTOR") == "sqlite":               # opcional, solo para pruebas
        return f"sqlite:///{BASE / 'db' / (db + '.db')}"
    return f"postgresql+{PG_DRIVER}://{PG_USER}:{quote_plus(PG_PASS)}@{PG_HOST}:{PG_PORT}/{db}"

URL_STG = os.environ.get("STG_URL", _url(DB_STG))
URL_DW = os.environ.get("DW_URL", _url(DB_DW))
URL_DM = os.environ.get("DM_URL", _url(DB_DM))
URL_ADMIN = _url("postgres")                                 # base de mantenimiento, para crear las otras tres

ANIOS_INICIALES = ["2023", "2024", "2025"]   # carga inicial
ANIO_INCREMENTAL = "2026"                    # carga incremental
DM_DESDE, DM_HASTA = 2022, 2026              # alcance del Data Mart

def motor(url):
    return create_engine(url, future=True)
def stg(): return motor(URL_STG)
def dw(): return motor(URL_DW)
def dm(): return motor(URL_DM)
