import pika
import json
from database import SessionLocal
from models import InventoryItem

def process_order(ch, method, properties, body):
    # 1. Buka surat pesanan dari RabbitMQ
    pesanan = json.loads(body)
    print(f"[x] Mendapat Surat Order Baru: {pesanan}")
    
    item_id_pesanan = pesanan.get("item_id")
    jumlah_dipesan = pesanan.get("quantity")
    
    # 2. Buka koneksi ke Database Irham
    db = SessionLocal()
    try:
        # Cari barangnya di gudang (Database Postgres)
        barang = db.query(InventoryItem).filter(InventoryItem.item_id == item_id_pesanan).first()
        
        if barang:
            # 3. Kurangi stoknya!
            if barang.stock >= jumlah_dipesan:
                barang.stock -= jumlah_dipesan
                db.commit() # Simpan perubahan ke database!
                print(f"[⚡] SUKSES! Stok barang {item_id_pesanan} berhasil dikurangi. Sisa stok: {barang.stock}")
            else:
                print(f"[⚠️] GAGAL! Stok barang {item_id_pesanan} tidak cukup! Sisa stok: {barang.stock}, tapi dipesan: {jumlah_dipesan}")
        else:
            print(f"[❌] ERROR! Barang dengan ID {item_id_pesanan} tidak ditemukan di database Irham!")
            
    except Exception as e:
        print(f"[💥] Terjadi kesalahan saat update database: {e}")
        db.rollback() # Batalkan jika ada error
    finally:
        db.close() # Tutup koneksi database
        ch.basic_ack(delivery_tag=method.delivery_tag) # Lapor ke RabbitMQ kalau tugas selesai

def start_worker():
    try:
        # Pastikan host-nya sesuai nama container RabbitMQ lu
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-broker'))
        channel = connection.channel()
        
        queue_name = "holis.procurement.order"
        channel.queue_declare(queue=queue_name, durable=True)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=process_order)
        
        print(f"[*] Worker Logistik siap! Menunggu pesanan di antrean '{queue_name}'...")
        channel.start_consuming()
    except Exception as e:
        print(f"Gagal menyalakan worker: {e}")

if __name__ == "__main__":
    start_worker()