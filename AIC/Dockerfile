FROM python:3.9-slim

WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'ensemble du projet dans le conteneur
COPY . .

EXPOSE 8050

# Lancer l'application
CMD ["python", "front3.py"]
