# ============================================================
# Dockerfile — F1 Tech Hub
# Imagen de producción para contenedor Docker
# Proyecto Final Telemática
# ============================================================

# --- Etapa 1: Imagen base ---
# Usamos Python 3.12 slim para mantener la imagen pequeña
FROM python:3.12-slim

# --- Metadatos de la imagen ---
LABEL maintainer="Estudiante Telematica"
LABEL version="1.0.0"
LABEL description="F1 Tech Hub - Servicio web telemático sobre Fórmula 1"

# --- Variables de entorno ---
# PYTHONDONTWRITEBYTECODE: evita crear archivos .pyc innecesarios
# PYTHONUNBUFFERED:         muestra los logs en tiempo real (importante para Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# --- Directorio de trabajo dentro del contenedor ---
WORKDIR /app

# --- Instalar dependencias del sistema operativo ---
# build-essential y libpq-dev son comunes; aquí solo necesitamos lo mínimo
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# --- Copiar e instalar dependencias de Python ---
# Copiamos requirements.txt ANTES del código para aprovechar el caché de Docker
# Si el código cambia pero no los requirements, esta capa no se reconstruye
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Copiar el código fuente de la aplicación ---
COPY . .

# --- Crear usuario no-root por seguridad ---
# Nunca correr contenedores como root en producción
RUN addgroup --system appgroup && \
    adduser  --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# --- Exponer el puerto que usa la aplicación ---
EXPOSE 5000

# --- Health check: Docker verifica que el contenedor esté sano ---
# Llama al endpoint /api/health cada 30 segundos
# Si falla 3 veces seguidas, Docker marca el contenedor como "unhealthy"
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# --- Comando de inicio en producción ---
# Gunicorn: servidor WSGI robusto para producción
# -w 4       → 4 workers (procesos paralelos)
# -b 0.0.0.0 → escuchar en todas las interfaces de red
# app:app    → módulo:objeto_flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "--access-logfile", "-", "app:app"]
