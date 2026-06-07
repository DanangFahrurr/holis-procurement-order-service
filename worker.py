import json
import time
import pika

def callback(ch, method, properties, body):
    # 1. MEMBACA PESAN YANG MASUK
    data_order = json.loads(body)
    print(f" [x] Mendapat Surat Order Baru: {data_order}")
    
    # Simulasi proses jeda waktu logistik/sistem membaca data
    time.sleep(1) 
    
    # 2. JALUR INTEGRASI KE TEMPAT IRHAM (HASURA)
    # Di Fase 3 nanti, di sinilah kamu menulis kode koneksi database (SQLAlchemy)
    # untuk menembak DB Postgres Irham (port 5433)
    print(f" [⚡] WORKER AKSI: Sukses memproses order_id {data_order['order_id']}.")
    print(f" [⚡] WORKER AKSI: Otomatis menambah STOK item_id {data_order['item_id']} sebanyak {data_order['quantity']} di Cabang {data_order['branch_id']}.")
    print("--------------------------------------------------")
    
    # Menandakan ke RabbitMQ bahwa pesan sukses diproses dan boleh dihapus dari antrean
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    try:
        # KONEKSI: Menghubungkan ke RabbitMQ lokal
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        
        # Memastikan nama kotak surat yang ditunggui SAMA PERSIS dengan punya main.py
        queue_name = "holis.procurement.order"
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Mengatur agar worker hanya menerima 1 pesan dulu sebelum selesai diproses
        channel.basic_qos(prefetch_count=1)
        
        # Mendaftarkan fungsi callback sebagai penangan pesan masuk
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        
        print(' [*] Worker HOLIS menyala. Menunggu surat order masuk... Tekan CTRL+C untuk keluar.')
        channel.start_consuming()
    
    except KeyboardInterrupt:
        # Menangkap sinyal CTRL+C biar nggak ngeluarin error merah panjang
        print("\n [!] Worker dimatikan oleh user. Sampai jumpa!")
        try:
            connection.close() # Menutup koneksi RabbitMQ dengan rapi
        except Exception:
            pass
    except Exception as e:
        print(f"Worker Error: {e}")

if __name__ == '__main__':
    start_worker()