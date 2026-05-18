# ============================================================
# terraform/main.tf — Infraestructura AWS para F1 Tech Hub
# Proyecto Final Telemática
# ============================================================
# Requisitos previos:
#   - Terraform >= 1.5 instalado
#   - AWS CLI configurado (aws configure)
#   - Credenciales de AWS Academy en ~/.aws/credentials
#
# Comandos:
#   terraform init      → Inicializa providers y módulos
#   terraform plan      → Muestra los cambios antes de aplicar
#   terraform apply     → Crea la infraestructura en AWS
#   terraform destroy   → Elimina todos los recursos creados
# ============================================================

# --- Provider AWS ---
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  # Región donde se despliega la infraestructura
  # us-east-1 es la que generalmente tiene el mejor soporte en AWS Academy
  region = var.aws_region
}

# ============================================================
# VARIABLES
# ============================================================

variable "aws_region" {
  description = "Región de AWS donde desplegar"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t2.micro"   # Free Tier elegible
}

variable "project_name" {
  description = "Nombre del proyecto (se usa como prefijo en recursos)"
  type        = string
  default     = "f1-tech-hub"
}

variable "key_pair_name" {
  description = "Nombre del Key Pair SSH creado en AWS (para acceso a la instancia)"
  type        = string
  default     = "f1-keypair"
}

# ============================================================
# DATA SOURCES — obtener información de AWS dinámicamente
# ============================================================

# AMI más reciente de Amazon Linux 2023 (gratuita, optimizada para AWS)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPC por defecto de la cuenta AWS Academy
data "aws_vpc" "default" {
  default = true
}

# Subnets disponibles en la VPC por defecto
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ============================================================
# SECURITY GROUP — Reglas de firewall
# ============================================================

resource "aws_security_group" "f1_sg" {
  name        = "${var.project_name}-sg"
  description = "Security Group para F1 Tech Hub - permite HTTP y SSH"
  vpc_id      = data.aws_vpc.default.id

  # Regla de entrada: HTTP (puerto 80)
  ingress {
    description = "HTTP - acceso a la aplicación web"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Abierto al mundo
  }

  # Regla de entrada: SSH (puerto 22) — para administración
  ingress {
    description = "SSH - administración del servidor"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # En producción real: limitar a tu IP
  }

  # Regla de salida: permitir todo el tráfico saliente
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-sg"
    Project = var.project_name
  }
}

# ============================================================
# INSTANCIA EC2 — Servidor de producción
# ============================================================

resource "aws_instance" "f1_server" {
  # AMI y tipo de instancia
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  # Par de llaves SSH para acceso remoto
  key_name = var.key_pair_name

  # Subnet y seguridad
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.f1_sg.id]
  associate_public_ip_address = true

  # Disco principal: 20GB (Free Tier permite hasta 30GB)
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }

  # ── User Data: script que se ejecuta al iniciar la instancia ──
  # Instala Docker, Docker Compose, clona el repo y levanta la app
  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e

    # --- Actualizar el sistema ---
    yum update -y

    # --- Instalar Docker ---
    yum install -y docker git
    systemctl enable docker
    systemctl start docker

    # Agregar ec2-user al grupo docker (no necesitar sudo)
    usermod -aG docker ec2-user

    # --- Instalar Docker Compose v2 ---
    COMPOSE_VERSION="v2.27.0"
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-linux-x86_64" \
         -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

    # --- Clonar el repositorio ---
    git clone https://github.com/TU_USUARIO/f1-tech-hub.git /opt/f1-tech-hub

    # --- Levantar la aplicación ---
    cd /opt/f1-tech-hub
    docker compose up -d --build

    echo "✅ F1 Tech Hub desplegado correctamente" > /var/log/f1-deploy.log
  EOF
  )

  tags = {
    Name    = "${var.project_name}-server"
    Project = var.project_name
    Env     = "production"
  }
}

# ============================================================
# ELASTIC IP — IP pública fija (no cambia al reiniciar)
# ============================================================

resource "aws_eip" "f1_eip" {
  instance = aws_instance.f1_server.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-eip"
    Project = var.project_name
  }
}

# ============================================================
# OUTPUTS — Información útil después del apply
# ============================================================

output "server_public_ip" {
  description = "IP pública del servidor EC2"
  value       = aws_eip.f1_eip.public_ip
}

output "server_public_dns" {
  description = "DNS público del servidor"
  value       = aws_instance.f1_server.public_dns
}

output "app_url" {
  description = "URL para acceder a la aplicación"
  value       = "http://${aws_eip.f1_eip.public_ip}"
}

output "ssh_command" {
  description = "Comando SSH para conectarse al servidor"
  value       = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_eip.f1_eip.public_ip}"
}
