# Gunakan base image yang cocok untuk ML
FROM python:3.11-slim

# Install dependency sistem
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    default-libmysqlclient-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set direktori kerja
WORKDIR /app

# Salin requirement dan install dependensi Python
COPY requirements.txt .

# Konfigurasi pip untuk mengatasi timeout dan menggunakan mirror PyPI yang lebih cepat
RUN pip config set global.timeout 1000 && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir -r requirements.txt

# Salin semua file dari project
COPY . .

# Jalankan aplikasi dengan Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]