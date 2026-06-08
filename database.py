# Contoh isi database.py di kemudian hari
from sqlalchemy import create_all, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. URL KONEKSI: Menuju ke Postgres milik Irham (menggunakan nama service Docker)
DATABASE_URL = "postgres://postgres:postgrespassword@db-postgres-inventory:5432/holis_inventory_db"

# 2. MEMBUAT ENGINE LOGISTIK: Jembatan penghubung ke database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 3. FUNGSI AMBIL KONEKSI: Untuk dipakai di main.py atau worker.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()