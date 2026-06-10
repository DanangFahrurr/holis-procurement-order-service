import json
import pika
import jwt
from fastapi import FastAPI, HTTPException, Header

app = FastAPI(title="Holis Procurement Service - Service 3")

# Fungsi untuk mengirim pesan ke RabbitMQ
def send_to_queue(queue_name: str, message: dict):
    try:
        # KONEKSI: Karena berjalan di lokal (sebelum digabung docker), arahkan ke localhost
        # Nanti saat digabung di docker-compose, 'localhost' diganti jadi 'message-broker'
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-broker'))
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
    
    # 1. VALIDASI KTP DIGITAL (JWT) ASLI
    # Cek apakah header Authorization ada dan berawalan "Bearer "
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token login tidak ditemukan atau format salah!")
    
    # Pisahkan kata "Bearer " untuk mengambil token aslinya saja
    token_asli = authorization.split(" ")[1].strip().replace('\n', '').replace('\r', '')
    
    try:
        # Kunci Rahasia Udah Benar
        SECRET_KEY = "sangat_rahasia_dan_panjang_sekali_32_karakter_" 
        
        # Membuka gembok token
        payload = jwt.decode(token_asli, SECRET_KEY, algorithms=["HS256"])
        
        # 🚨 CARA BARU MENGAMBIL DATA (Menyesuaikan token Josfi/Hasura)
        hasura_claims = payload.get("https://hasura.io/jwt/claims", {})
        
        user_role = hasura_claims.get("x-hasura-default-role")
        user_branch_id = hasura_claims.get("x-hasura-branch-id")
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Waktu token sudah habis. Silakan login lagi!")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token ditolak! Alasan dari Python: {str(e)}")

    # CEK HAK AKSES
    # (Sementara kita ubah jadi "staff" dulu biar tembus sesuai KTP Josfi)
    if user_role != "manager_cabang":
        raise HTTPException(status_code=403, detail="Akses Ditolak! Hanya Manager Cabang yang boleh membuat order!")

    # 3. STRUKTUR DATA ORDER YAKIN SAMA (KONTRAK DATA)
    payload_order = {
        "order_id": 999,  # Contoh dummy ID otomatis
        "item_id": item_id,
        "quantity": quantity,
        "branch_id": user_branch_id, # Sekarang ID cabang dinamis dari token yang login!
        "status_order": "SELESAI" # Langsung diset SELESAI untuk mentrigger update stok Irham
    }
    
    # 4. KIRIM DATA KE RABBITMQ
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