from sqlalchemy import Column, Integer, String
from database import Base

# Ini adalah representasi tabel barang milik Irham di Postgres
class InventoryItem(Base):
    __tablename__ = "inventory" # <--- Ganti dengan nama tabel asli dari Irham

    # Pastikan nama kolom ini sama persis dengan yang ada di database Irham
    item_id = Column(Integer, primary_key=True, index=True) 
    item_name = Column(String)
    stock = Column(Integer) # <--- Kolom yang bakal kita kurangi