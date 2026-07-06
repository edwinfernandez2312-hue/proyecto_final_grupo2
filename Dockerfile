FROM python:3.12

# 2. Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copiar los requerimientos
COPY requirements.txt .

# 5. EL ARREGLO: Actualizar pip primero y luego instalar las librerías
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar los archivos del proyecto
COPY src/ ./src/
COPY sql/ ./sql/

# 7. Crear las carpetas
RUN mkdir -p /app/data_warehouse /app/reportes_visuales /app/secrets

# 8. Ejecutar
CMD ["python", "src/main.py"]