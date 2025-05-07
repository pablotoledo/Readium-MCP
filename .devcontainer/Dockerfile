FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python-is-python3 \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Asegurar que el usuario ubuntu tenga permisos de sudo sin contraseña
RUN echo 'ubuntu ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu && chmod 0440 /etc/sudoers.d/ubuntu

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Agregar Poetry al PATH para todos los usuarios
ENV PATH="/root/.local/bin:$PATH"
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/ubuntu/.bashrc

# Configurar Poetry para crear virtualenvs en el proyecto
RUN poetry config virtualenvs.in-project true

# Instalar pipx para herramientas globales de usuario
RUN apt-get update && apt-get install -y pipx && pipx ensurepath

# Instalar herramientas adicionales de desarrollo de forma aislada
RUN pipx install pyright && pipx install ruff

# Configurar usuario por defecto
USER ubuntu
WORKDIR /workspace

# Configurar Poetry para el usuario ubuntu
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc