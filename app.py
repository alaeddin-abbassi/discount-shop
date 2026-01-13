import streamlit as st
import sys
import os

# Pfad-Setup für Imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Page Config muss ganz am Anfang stehen
st.set_page_config(page_title="OmniRetail UCP Demo", page_icon="🏢", layout="wide")

# Navigation in der Sidebar
st.sidebar.title("📱 UCP Ebene wählen")
app_mode = st.sidebar.radio("Ansicht wechseln:", ["🛍️ Kunden Shop App", "📈 Management Cockpit"])

st.sidebar.divider()
st.sidebar.info("Diese App läuft in einem Docker-Container. Frontend und Dashboard greifen live auf dieselbe lokale FastAPI-Schnittstelle zu.")

# --- DIE MAGIE: Wir laden den Code dynamisch ---

if app_mode == "🛍️ Kunden Shop App":
    # Wir führen den Code der ui_app.py hier aus
    # (Wir müssen sys.argv manipulieren, damit streamlit nicht verwirrt ist)
    with open("frontend/ui_app.py", "r", encoding='utf-8') as f:
        code = f.read()
        # Wir entfernen die set_page_config aus dem Code, da wir sie schon gesetzt haben
        code = code.replace('st.set_page_config', '# st.set_page_config')
        exec(code, globals())

elif app_mode == "📈 Management Cockpit":
    with open("frontend/market_dashboard.py", "r", encoding='utf-8') as f:
        code = f.read()
        code = code.replace('st.set_page_config', '# st.set_page_config')
        exec(code, globals())