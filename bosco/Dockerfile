# Usa una imagen base de Python
FROM python:3.9-slim

# Establece un directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt primero para aprovechar el caching de Docker
COPY src/requirements.txt .

# Configura repositorios confiables y añade claves GPG necesarias
RUN apt-get update -y && \
    apt install graphviz -y

# libgraphviz-dev

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY src/ .

# Exponer un puerto (opcional, si la app lo necesita)
EXPOSE 8081

# Comando por defecto para ejecutar la aplicación
CMD ["python", "main.py"]