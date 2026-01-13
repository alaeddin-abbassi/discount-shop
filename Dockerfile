# Basis Image
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Kopiere alle Dateien
COPY . .

# Installiere Pakete
RUN pip install --no-cache-dir -r requirements.txt

# Öffne den Hugging Face Port
EXPOSE 7860

# DER TRICK: Wir starten erst Uvicorn (API) im Hintergrund (&) 
# und dann Streamlit im Vordergrund.
CMD uvicorn backend:app --host 0.0.0.0 --port 8000 & \
    streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0