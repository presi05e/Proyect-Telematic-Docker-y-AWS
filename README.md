# 🏎️ F1 Tech Hub — Proyecto Final Telemática

> **Servicio telemático web** sobre Fórmula 1 e innovación automotriz, desplegado con contenedores Docker en infraestructura AWS mediante Infraestructura como Código (IaC) con Terraform y entrega continua con GitHub Actions.


## 🧪 Realizado por: 
### Esteban Présiga Posada

## 🌐 Para la Materia de: 
### Telematica 

## 🏟️ Fecha:  
### 18/05/2026
---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Requisitos Previos](#requisitos-previos)
5. [Despliegue Rápido (Local)](#despliegue-rápido-local)
6. [Despliegue en AWS con Terraform](#despliegue-en-aws-con-terraform)
7. [Pipeline CI/CD con GitHub Actions](#pipeline-cicd-con-github-actions)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Estructura del Proyecto](#estructura-del-proyecto)
10. [Manual del Desarrollador](#manual-del-desarrollador)

---

## Descripción del Proyecto

**F1 Tech Hub** es un servicio telemático web que ofrece información sobre los equipos, pilotos y tecnologías de la Fórmula 1. La aplicación expone tanto una interfaz web visual como una **API REST** consumible por cualquier cliente externo.

### Características principales
- ✅ Interfaz web responsiva con diseño dark-mode estilo F1
- ✅ API REST en formato JSON (endpoints `/api/teams`, `/api/technologies`, `/api/health`)
- ✅ Contenedor Docker con servidor WSGI Gunicorn de producción
- ✅ Orquestación con Docker Compose
- ✅ Infraestructura en AWS EC2 definida con Terraform
- ✅ Pipeline CI/CD con GitHub Actions (test → build → deploy)
- ✅ Health checks automáticos para monitoreo

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET                              │
└─────────────────┬───────────────────────────────────────┘
                  │  HTTP :80
┌─────────────────▼───────────────────────────────────────┐
│           AWS EC2 (t2.micro)  —  Elastic IP             │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Docker Compose Network                    │   │
│  │  ┌─────────────────────────────────────────────┐ │   │
│  │  │  Contenedor: f1_tech_hub                    │ │   │
│  │  │  Imagen: python:3.12-slim                   │ │   │
│  │  │  Puerto interno: 5000                       │ │   │
│  │  │  Servidor: Gunicorn (4 workers)             │ │   │
│  │  │  App: Flask — F1 Tech Hub                   │ │   │
│  │  └─────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
│  Security Group: 80 (HTTP), 22 (SSH)                     │
└─────────────────────────────────────────────────────────┘

CI/CD:
GitHub (push main) → GitHub Actions → Docker Hub → EC2
```

---

## Tecnologías Utilizadas

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje | Python | 3.12 |
| Framework web | Flask | 3.0.3 |
| Servidor WSGI | Gunicorn | 22.0.0 |
| Contenedor | Docker | 24+ |
| Orquestación | Docker Compose | v2.27 |
| Cloud | AWS EC2 | Amazon Linux 2023 |
| IaC | Terraform | 1.5+ |
| CI/CD | GitHub Actions | — |
| Registro de imágenes | Docker Hub | — |

---

## Requisitos Previos

### Para despliegue local
- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- Git

### Para despliegue en AWS
- Cuenta AWS Academy activa
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5 instalado
- [AWS CLI](https://aws.amazon.com/cli/) configurado con tus credenciales
- Key Pair SSH creado en AWS

---

## Despliegue Rápido (Local)

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/f1-tech-hub.git
cd f1-tech-hub

# 2. Levantar el servicio
docker compose up -d --build

# 3. Verificar que está corriendo
docker compose ps
docker compose logs -f

# 4. Abrir en el navegador
# http://localhost

# 5. Para detener el servicio
docker compose down
```

### Opción 2: Solo Docker

```bash
# Construir la imagen
docker build -t f1-tech-hub ./app

# Ejecutar el contenedor
docker run -d -p 80:5000 --name f1_hub f1-tech-hub

# Ver logs
docker logs -f f1_hub
```

### Opción 3: Desarrollo local (sin Docker)

```bash
# Crear entorno virtual
cd app
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
# Disponible en http://localhost:5000
```

---

## Despliegue en AWS con Terraform

### Paso 1: Configurar credenciales AWS Academy

```bash
# Copiar las credenciales desde AWS Academy Learner Lab
# (pestaña "AWS Details" → "AWS CLI")
aws configure
# AWS Access Key ID: [pegar de Academy]
# AWS Secret Access Key: [pegar de Academy]
# Default region name: us-east-1
# Default output format: json
```

### Paso 2: Crear Key Pair en AWS

```bash
# Crear el key pair y guardar la llave privada
aws ec2 create-key-pair \
    --key-name f1-keypair \
    --query 'KeyMaterial' \
    --output text > f1-keypair.pem

# Dar permisos correctos a la llave
chmod 400 f1-keypair.pem
```

### Paso 3: Inicializar y aplicar Terraform

```bash
cd terraform

# Inicializar Terraform (descarga providers)
terraform init

# Ver el plan de cambios (qué se va a crear)
terraform plan

# Crear la infraestructura en AWS
terraform apply
# Escribe "yes" cuando pida confirmación

# Al finalizar verás los outputs:
# app_url        = "http://XX.XX.XX.XX"
# ssh_command    = "ssh -i f1-keypair.pem ec2-user@XX.XX.XX.XX"
```

### Paso 4: Actualizar el repo en el User Data

> ⚠️ Antes de hacer `terraform apply`, edita `terraform/main.tf` y reemplaza `TU_USUARIO` con tu usuario real de GitHub en la línea del `git clone`.

### Paso 5: Destruir la infraestructura (cuando termines)

```bash
# IMPORTANTE: destruir cuando no uses para no gastar créditos
terraform destroy
```

---

## Pipeline CI/CD con GitHub Actions

El pipeline se activa automáticamente con cada `git push` a la rama `main`.

### Configurar los Secrets en GitHub

Ve a: `Repositorio → Settings → Secrets and variables → Actions → New repository secret`

| Secret | Descripción |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Token de acceso de Docker Hub (no la contraseña) |
| `EC2_HOST` | IP pública de tu instancia EC2 |
| `EC2_KEY` | Contenido completo de tu archivo `.pem` |

### Flujo del Pipeline

```
push a main
    │
    ▼
🧪 test          → instala deps, verifica health check
    │
    ▼
🐳 build-and-push → construye imagen, sube a Docker Hub
    │
    ▼
🚀 deploy         → SSH a EC2, git pull, docker compose up
    │
    ▼
🏥 health-check   → verifica HTTP 200 en /api/health
```

### Trigger manual del workflow

```bash
# Hacer un cambio y publicarlo activa el pipeline
git add .
git commit -m "feat: actualizar datos de equipos"
git push origin main

# Ver el pipeline en:
# GitHub → Actions → 🏎️ CI/CD — F1 Tech Hub
```

---

## Endpoints de la API

La aplicación expone una API REST consumible:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página principal |
| `GET` | `/teams` | Página de equipos |
| `GET` | `/technology` | Página de tecnologías |
| `GET` | `/api/teams` | JSON con todos los equipos |
| `GET` | `/api/technologies` | JSON con todas las tecnologías |
| `GET` | `/api/health` | Health check del servicio |

### Ejemplo de respuesta `/api/health`

```json
{
  "status": "healthy",
  "service": "F1 Tech Hub",
  "timestamp": "2024-11-20T10:30:00.000Z",
  "version": "1.0.0"
}
```

### Ejemplo de uso con curl

```bash
# Health check
curl http://TU_IP/api/health

# Obtener equipos
curl http://TU_IP/api/teams | python3 -m json.tool

# Obtener tecnologías
curl http://TU_IP/api/technologies
```

---

## Estructura del Proyecto

```
f1-tech-hub/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pipeline CI/CD GitHub Actions
│
├── app/
│   ├── app.py                  # Aplicación Flask principal
│   ├── requirements.txt        # Dependencias Python
│   ├── Dockerfile              # Imagen Docker de producción
│   └── templates/
│       ├── base.html           # Plantilla base (navbar, footer, CSS global)
│       ├── index.html          # Página de inicio con estadísticas
│       ├── teams.html          # Página de equipos F1
│       └── technology.html     # Página de tecnologías
│
├── terraform/
│   └── main.tf                 # Infraestructura AWS como código
│
├── docker-compose.yml          # Orquestación de contenedores
├── .gitignore                  # Archivos a ignorar en Git
└── README.md                   # Este archivo
```

---

## Manual del Desarrollador

### Modificar los datos de la aplicación

Los datos (equipos, tecnologías, estadísticas) están en `app/app.py` en las variables globales `TEAMS`, `TECHNOLOGIES` y `STATS`. Para agregar un equipo:

```python
TEAMS.append({
    "id": 6,
    "name": "Alpine",
    "country": "Francia",
    "color": "#FF87BC",
    "accent": "#0090FF",
    "engine": "Renault E-Tech",
    "championships": 2,
    "innovations": ["..."],
    "drivers": ["Esteban Ocon", "Pierre Gasly"]
})
```

### Agregar una nueva ruta

```python
@app.route("/nueva-seccion")
def nueva_seccion():
    return render_template("nueva.html", datos=MIS_DATOS)
```

### Reconstruir el contenedor tras cambios

```bash
docker compose up -d --build
```

### Ver logs en tiempo real

```bash
docker compose logs -f web
```

### Conectarse al servidor EC2

```bash
ssh -i f1-keypair.pem ec2-user@TU_IP_EC2
```

### Comandos Docker útiles

```bash
# Ver contenedores activos
docker compose ps

# Reiniciar el servicio
docker compose restart web

# Ver uso de recursos
docker stats

# Entrar al contenedor
docker exec -it f1_tech_hub bash
```

---

## Rúbrica de Evaluación (Referencia)

| Criterio | Peso | Implementación en este proyecto |
|----------|------|--------------------------------|
| Despliegue correcto desde Dockerfile, contenedores estables | 40% | Dockerfile + docker-compose.yml con restart:always y health checks |
| Manual del desarrollador y código comentado | 20% | Este README + comentarios en todos los archivos |
| Repositorio con trazabilidad (Git) | 30% | GitHub con historial de commits y pipeline CI/CD |
| Funcionalidad completa en producción | 10% | App Flask con 3 páginas + API REST + AWS |

---

*Proyecto Final — Telemática | Ingeniería en Sistemas e Informática | Semestre 3*

