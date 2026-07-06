# 1. Usamos una imagen ligera de Python
FROM python:3.11-slim

# 2. Configurar variables de entorno para que los logs salgan en tiempo real
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Copiar e instalar las librerías del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar los archivos del proyecto 
COPY src/ ./src/
COPY sql/ ./sql/

# 6. Crear las carpetas locales para la BD SQLite y los reportes gráficos
RUN mkdir -p /app/data_warehouse /app/reportes_visuales

# 7. Ejecutar directamente tu archivo main.py
CMD ["python", "src/main.py"]