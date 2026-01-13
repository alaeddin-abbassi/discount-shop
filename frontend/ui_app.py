import streamlit as st
import requests
import pandas as pd
import uuid
import sys
import os
import time

# --- SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="OmniMarket", page_icon="🛍️", layout="wide")
API_URL = "http://127.0.0.1:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- CUSTOM CSS (Das macht den "Shop-Look") ---
st.markdown("""
<style>
    /* Verstecke Streamlit Header/Footer für cleanen Look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Buttons runder und freundlicher machen */
    .stButton button {
        border-radius: 20px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    
    /* Primär-Button (Kaufen) hervorheben */
    div[data-testid="stVerticalBlock"] button[kind="primary"] {
        background-color: #ff4b4b;
        color: white;
    }

    /* Produkt-Karten Look */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
    }
    
    /* Preis Styling */
    .price-tag {
        font-size: 22px;
        font-weight: 800;
        color: #2c3e50;
    }
    
    /* Shop Badge Styling */
    .shop-badge {
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- API CLIENT (Logik bleibt gleich) ---
def get_products(query="", category=None, max_price=None):
    params = {"q": query}
    if category and category != "Alle": params["category"] = category
    if max_price: params["max_price"] = max_price
    try:
        return requests.get(f"{API_URL}/api/products", params=params).json()
    except:
        return []

def add_to_cart_api(pid):
    try:
        requests.post(f"{API_URL}/api/cart", json={"product_id": pid, "quantity": 1, "session_id": st.session_state.session_id})
        st.toast("In den Warenkorb gelegt!", icon="🛒")
        time.sleep(0.2) # UI Update Zeit geben
    except:
        st.error("Backend offline")

def get_cart_api():
    try:
        r = requests.get(f"{API_URL}/api/cart/{st.session_state.session_id}")
        return r.json() if r.status_code == 200 else []
    except:
        return []

def checkout_api():
    try:
        payload = {"session_id": st.session_state.session_id, "payment_token": "tok_demo_123"}
        return requests.post(f"{API_URL}/api/checkout", json=payload).json()
    except:
        return {"status": "error"}

# --- UI LAYOUT ---

# 1. HERO SECTION (Banner)
# Ein neutrales Food-Bild für den "App-Charakter"
# ALT (Führt zum Fehler):
# NEU (Funktioniert und sieht besser aus):
hero_url = "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=2574&auto=format&fit=crop"
st.markdown(
    f"""
    <div style="
        width: 100%;
        height: 200px;
        overflow: hidden;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <img src="{hero_url}" style="
            width: 100%;
            height: 100%;
            object-fit: cover;
        ">
    </div>
    """,
    unsafe_allow_html=True
)
st.title("OmniMarket")
st.caption("Your Unified Shopping Experience • Powered by UCP")

col_main, col_sidebar = st.columns([3, 1.2])

# --- LINKER BEREICH: PRODUKTE ---
with col_main:
    # Suche & Filter in einer Reihe
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search_q = st.text_input("🔍 Was suchst du heute?", placeholder="Steak, Milch, Party...")
    with c2:
        cat_filter = st.selectbox("Kategorie", ["Alle", "Fresh", "Drinks", "Non-Food"])
    with c3:
        price_filter = st.slider("Max Preis (€)", 0, 50, 50)

    st.divider()

    products = get_products(search_q, cat_filter, price_filter)

    if products:
        # Responsive Grid: 3 Produkte pro Reihe
        cols = st.columns(3)
        for i, p in enumerate(products):
            with cols[i % 3]:
                # Karte start
                with st.container(border=True):
                    # Großes Emoji als Bild-Ersatz (zentriert)
                    st.markdown(f"<div style='text-align:center; font-size: 60px; margin-bottom: 10px;'>{p['img']}</div>", unsafe_allow_html=True)

                    # Produktname (gekürzt falls zu lang)
                    name = p['name']
                    if len(name) > 25: name = name[:22] + "..."
                    st.markdown(f"**{name}**")

                    # Herkunft Badge (Farblich codiert)
                    shop = p['shop']
                    color = "#27ae60" if "Premium" in shop else ("#2980b9" if "Budget" in shop else "#e67e22")
                    short_shop = "LOC" if "Local" in shop else ("WHS" if "Warehouse" in shop else "DLV")

                    # Preis & Shop Zeile
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                        <span class='price-tag'>{p['price']:.2f} €</span>
                        <span class='shop-badge' style='background-color: {color};' title='{shop}'>{short_shop}</span>
                    </div>
                    <div style='font-size: 12px; color: gray; margin-bottom: 10px;'>{p.get('description', '')}</div>
                    """, unsafe_allow_html=True)

                    # Button über die ganze Breite
                    if st.button("Hinzufügen", key=p['id'], use_container_width=True):
                        add_to_cart_api(p['id'])
                        st.rerun()

    else:
        st.info("Das Backend scheint offline zu sein oder keine Produkte gefunden.")
        st.code("uvicorn main:app --reload --port 8000")

# --- RECHTER BEREICH: WARENKORB (Kassenbon Style) ---
with col_sidebar:
    with st.container(border=True):
        st.subheader("🛒 Dein Korb")
        cart_items = get_cart_api()

        if cart_items:
            total_sum = 0
            for item in cart_items:
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.write(f"1x {item['product_name']}")
                    st.caption(f"via {item['shop']}")
                with c_b:
                    st.write(f"**{item['total']:.2f}€**")
                total_sum += item['total']
                st.markdown("---")

            # Summenbereich
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; font-size: 18px; font-weight: bold;'>
                <span>Gesamt</span>
                <span>{total_sum:.2f} €</span>
            </div>
            """, unsafe_allow_html=True)

            st.write("") # Spacer

            if st.button("Jetzt bezahlen", type="primary", use_container_width=True):
                with st.spinner("Authorisiere Zahlung..."):
                    time.sleep(1.5)
                    res = checkout_api()

                if res.get("status") == "confirmed":
                    st.balloons()
                    st.success("Bestellung bestätigt!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.caption("Dein Warenkorb ist leer.")
            st.markdown("---")
            st.write("Füge Produkte hinzu, um den UCP-Split zu testen.")