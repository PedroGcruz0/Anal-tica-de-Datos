"""Crea en PostgreSQL las tres bases vacías (stg_oece, dw_oece, dm_monitoreo) si no existen.
Usa PGUSER / PGPASSWORD / PGHOST / PGPORT (ver config.py)."""
from sqlalchemy import create_engine, text
import config

if config.URL_ADMIN.startswith("sqlite"):
    print("Motor SQLite: no hace falta crear bases.")
else:
    eng = create_engine(config.URL_ADMIN, isolation_level="AUTOCOMMIT")
    with eng.connect() as cn:
        for db in (config.DB_STG, config.DB_DW, config.DB_DM):
            if cn.execute(text("SELECT 1 FROM pg_database WHERE datname = :d"), {"d": db}).scalar():
                print(f"{db}: ya existe")
            else:
                cn.execute(text(f'CREATE DATABASE "{db}"')); print(f"{db}: creada")
