# 1. Basis: Python 3.9
FROM python:3.9-slim

# 2. System-Updates
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Arbeitsverzeichnis
WORKDIR /app

# 4. Dateien kopieren
COPY . .

# 5. Abhängigkeiten installieren
RUN pip3 install --no-cache-dir -r requirements.txt

# 6. Port für Hugging Face freigeben
EXPOSE 7860

# 7. START-SCRIPT
# - Startet FastAPI auf Port 8000 im Hintergrund (&)
# - Startet die neue app.py auf Port 7860 im Vordergrund
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & \
    streamlit run app.py --server.port=7860 --server.address=0.0.0.0