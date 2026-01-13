import streamlit as st
import requests
import pandas as pd
import uuid

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"  # Interne Docker-Adresse

st.set_page_config(page_title="EDEKA UCP Demo", page_icon="🛒", layout="wide")

# Session Management
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- HELPER FUNCTIONS ---
def get_products(query=""):
    try:
        r = requests.get(f"{API_URL}/api/products", params={"q": query})
        return r.json()
    except:
        return []

def add_to_cart_api(pid):
    payload = {"product_id": pid, "quantity": 1, "session_id": st.session_state.session_id}
    requests.post(f"{API_URL}/api/cart", json=payload)
    st.toast("In den Warenkorb gelegt!", icon="✅")

def get_cart_api():
    try:
        r = requests.get(f"{API_URL}/api/cart/{st.session_state.session_id}")
        return r.json()
    except:
        return []

def checkout_api():
    try:
        r = requests.post(f"{API_URL}/api/checkout", params={"session_id": st.session_state.session_id})
        return r.json()
    except:
        return {"status": "error"}

# --- UI LAYOUT ---

st.title("🛒 EDEKA Unified Commerce")
st.caption(f"Frontend verbunden mit UCP Backend auf {API_URL}")

# Sidebar Warenkorb
with st.sidebar:
    st.header("Dein Warenkorb")
    cart_items = get_cart_api()
    
    if cart_items:
        df = pd.DataFrame(cart_items)
        st.dataframe(df[["product", "shop", "price"]], hide_index=True)
        total = sum(item["total"] for item in cart_items)
        st.metric("Summe", f"{total:.2f} €")
        
        if st.button("Kostenpflichtig bestellen", type="primary"):
            result = checkout_api()
            if result.get("status") == "confirmed":
                st.balloons()
                st.success(f"Bestellung {result['order_id']} erfolgreich!")
                st.info("Das Backend hat den Token validiert und den Bestand gebucht.")
    else:
        st.info("Der Warenkorb ist leer.")

# Main Area
col1, col2 = st.columns([3, 1])
with col1:
    search_q = st.text_input("Suche im Edeka-Universum", placeholder="z.B. Steak, Bier, Netto...")

# Produkte laden
products = get_products(search_q)

# Grid Anzeige
if products:
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.header(p["img"])
                st.subheader(p["name"])
                st.caption(f"Verkauf durch: {p['shop']}")
                st.write(f"**{p['price']:.2f} €**")
                if st.button("In den Korb", key=p["id"]):
                    add_to_cart_api(p["id"])
                    st.rerun() # Refresh um Warenkorb zu updaten
else:
    st.warning("Keine Verbindung zum Backend oder keine Produkte gefunden.")