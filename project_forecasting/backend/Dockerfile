FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app/backend

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le code + le CSV
COPY backend_app.py .
COPY data/data_merged.csv ./data/data_merged.csv

EXPOSE 5000

CMD ["python", "backend_app.py"]
