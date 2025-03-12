# Utilisation d'une image Python
FROM python:3.11-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration des dépendances
COPY docker-requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip
RUN pip install -r docker-requirements.txt

# Copie des fichiers de l'application
COPY . .

# Ouverture du port Streamlit
EXPOSE 8501

# Démarrage de l'application Streamlit
CMD ["streamlit", "run", "main.py"]