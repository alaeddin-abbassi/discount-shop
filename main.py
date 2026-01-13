import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import discovery, commerce
from database import init_db

# --- LIFESPAN MANAGER (Der "Clean Code" Weg) ---
# Das garantiert, dass die DB erstellt wird, EGAL wie du den Server startest.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Datenbank prüfen & erstellen
    print("⚡ Server startet... Initialisiere Datenbank.")
    init_db()
    yield
    # 2. Shutdown: Hier könnte man Aufräum-Arbeiten machen (z.B. DB schließen)
    print("💤 Server fährt herunter.")

# Setup App mit Lifespan
app = FastAPI(
    title="OmniRetail Core (Clean Arch)",
    version="2.0",
    lifespan=lifespan  # <--- Hier verknüpfen wir die Start-Logik
)

# Register Routers
app.include_router(discovery.router)
app.include_router(commerce.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)