FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias de Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ .

# Crear directorio para uploads
RUN mkdir -p uploads

# Exponer puerto
EXPOSE 8001

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
