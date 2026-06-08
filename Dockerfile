# 1. Gunakan sistem operasi Linux dengan Python versi ringan
FROM python:3.11-slim

# 2. Buat dan masuk ke folder /app di dalam container
WORKDIR /app

# 3. Pindahkan file requirements.txt dari laptop ke dalam container
COPY requirements.txt .

# 4. Install semua library Python yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# 5. Pindahkan semua file kodingan kamu (main.py, worker.py, dll) ke dalam container
COPY . .

# 6. Buka jalur port 8000 untuk FastAPI
EXPOSE 8000

# 7. Perintah yang otomatis dijalankan saat container hidup (Menyalakan Server FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]