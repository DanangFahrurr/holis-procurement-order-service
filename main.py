import json
import pika
from fastapi import FastAPI, HTTPException, Header

app = FastAPI(title="Holis Procurement Service - Service 3")

# Fungsi untuk mengirim pesan ke RabbitMQ
def send_to_queue(queue_name: str, message: dict):
    try:
        # KONEKSI: Karena berjalan di lokal (sebelum digabung docker), arahkan ke localhost
        # Nanti saat digabung di docker-compose, 'localhost' diganti jadi 'message-broker'
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        
        # MEMBUAT KOTAK SURAT: Pastikan antrean dengan nama ini sudah terbuat
        channel.queue_declare(queue=queue_name, durable=True)
        
        # MENGIRIM PESAN: Ubah dictionary Python menjadi string JSON biasa
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Membuat pesan persisten (tidak hilang jika broker restart)
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Gagal mengirim pesan ke RabbitMQ: {e}")
        return False

# ENDPOINT: Membuat Order Pengadaan Barang Baru
@app.post("/orders")
def create_order(item_id: int, quantity: int, authorization: str = Header(None)):
    # 1. SIMULASI VALIDASI KTP DIGITAL (JWT): 
    # Idealnya nanti menggunakan PyJWT untuk decode token dari Josfi
    # if not authorization:
    #     raise HTTPException(status_code=401, detail="Token login tidak ditemukan!")
    
    # Simulasi data user yang didapat dari token login Josfi
    # Anggap saja token yang dikirim valid dan isinya adalah Manager Cabang 5
    user_role = "manager_cabang"
    user_branch_id = 5 
    
    if user_role != "manager_cabang":
        raise HTTPException(status_code=403, detail="Hanya Manager Cabang yang boleh membuat order!")

    # 2. STRUKTUR DATA ORDER YAKIN SAMA (KONTRAK DATA)
    payload_order = {
        "order_id": 999,  # Contoh dummy ID otomatis
        "item_id": item_id,
        "quantity": quantity,
        "branch_id": user_branch_id,
        "status_order": "SELESAI" # Langsung diset SELESAI untuk mentrigger update stok Irham
    }
    
    # 3. KIRIM DATA KE RABBITMQ
    queue_name = "holis.procurement.order"
    sukses_kirim = send_to_queue(queue_name, payload_order)
    
    if not sukses_kirim:
        raise HTTPException(status_code=500, detail="Gagal memasukkan order ke antrean logistik!")
        
    return {
        "message": "Order sukses dibuat dan dikirim ke antrean RabbitMQ!",
        "data_order": payload_order
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)