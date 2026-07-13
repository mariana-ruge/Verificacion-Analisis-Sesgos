# Imagen base de Python 3.11
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app


# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero requirements.txt para aprovechar caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto 8080
EXPOSE 8080

# Variable de entorno para que uvicorn corra en 0.0.0.0
ENV PYTHONUNBUFFERED=1

#Directorio desde donde se debe cargar el contenedor
CMD ["python", "run.py"]
