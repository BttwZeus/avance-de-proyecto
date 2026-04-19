# Imagen base oficial de Python ligera
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (aprovecha caché de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY app.py .

# Puerto que expone la aplicación
EXPOSE 5000

# Comando para arrancar Flask
CMD ["python", "app.py"]
