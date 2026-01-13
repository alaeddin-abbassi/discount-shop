import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
import sys
import os

# Setup Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- CONFIG ---
st.set_page_config(page_title="OmniRetail Control Tower", page_icon="📈", layout="wide")
API_URL = "http://127.0.0.1:8000"

# Auto-Refresh Mechanismus (Simuliert Echtzeit-Monitoring)
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# --- API FUNCTIONS ---
def get_orders():
    try:
        return requests.get(f"{API_URL}/api/orders").json()
    except:
        return []

def get_inventory():
    try:
        return requests.get(f"{API_URL}/api/products").json()
    except:
        return []

# --- DASHBOARD UI ---

st.title("🎛️ OmniRetail Control Tower")
st.markdown("**Status:** `LIVE` | **Region:** `DACH` | **Node:** `Master-View`")
st.divider()

# Daten laden
orders = get_orders()
inventory = get_inventory()

# KPIs (Key Performance Indicators)
col1, col2, col3, col4 = st.columns(4)

total_revenue = sum([o['total'] for o in orders])
order_count = len(orders)
avg_order = total_revenue / order_count if order_count > 0 else 0

with col1:
    st.metric("Gesamtumsatz (YTD)", f"{total_revenue:.2f} €", delta="+Live")
with col2:
    st.metric("Transaktionen", order_count)
with col3:
    st.metric("Ø Warenkorb", f"{avg_order:.2f} €")
with col4:
    # Simulierter Server-Status
    st.metric("UCP API Latency", "12ms", delta="-2ms", delta_color="inverse")

st.divider()

# --- ZWEISPALTIGES LAYOUT ---
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader("📊 Umsatz-Verteilung nach Quelle")

    if inventory:
        # Wir berechnen Umsatzanteile basierend auf den Shops (Simulation)
        df_inv = pd.DataFrame(inventory)

        # Chart 1: Inventar Verteilung
        fig = px.bar(df_inv, x="name", y="stock", color="shop",
                     title="Live Lagerbestand pro Node",
                     color_discrete_map={
                         "Premium Market (Local)": "#e74c3c", # Rot (Edeka)
                         "Budget Online (Warehouse)": "#f1c40f", # Gelb (Netto)
                         "Quick Delivery (Service)": "#2ecc71" # Grün (Picnic)
                     })
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Warte auf Daten...")

with c_right:
    st.subheader("🚨 Low Stock Alerts")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        # Filter auf geringen Bestand
        low_stock = df_inv[df_inv['stock'] < 30]

        if not low_stock.empty:
            for _, row in low_stock.iterrows():
                st.error(f"**{row['name']}**")
                st.caption(f"Bestand: {row['stock']} | Node: {row['shop']}")
        else:
            st.success("Lagerbestand optimal.")

st.divider()

# --- ORDER LIVE STREAM ---
st.subheader("📝 Live Transaktions-Log (Blockchain Ledger Simulation)")

if orders:
    df_orders = pd.DataFrame(orders)
    # Timestamp schöner formatieren
    df_orders['timestamp'] = pd.to_datetime(df_orders['timestamp']).dt.strftime('%H:%M:%S')

    st.dataframe(
        df_orders[['timestamp', 'order_id', 'total', 'status']],
        column_config={
            "timestamp": "Zeit",
            "order_id": "Transaktions-Hash",
            "total": st.column_config.NumberColumn("Betrag", format="%.2f €"),
            "status": st.column_config.TextColumn("Status"),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Noch keine Transaktionen im Ledger verzeichnet.")

# --- AUTO REFRESH BUTTON ---
if st.button("🔄 Dashboard aktualisieren"):
    st.rerun()