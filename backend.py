from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="EDEKA UCP Backend", version="1.0.0")

# --- MOCK DATENBANK ---
INVENTORY = [
    {"id": "e1", "name": "Edeka Bio Rindersteak", "price": 24.90, "shop": "Edeka Filiale", "img": "🥩", "stock": 50},
    {"id": "n1", "name": "Gut&Günstig Holzkohle 3kg", "price": 4.99, "shop": "Netto Online", "img": "🔥", "stock": 100},
    {"id": "p1", "name": "Krombacher Pils (Kasten)", "price": 14.99, "shop": "Picnic Delivery", "img": "🍺", "stock": 20},
    {"id": "e2", "name": "Bio Weidemilch 1L", "price": 1.49, "shop": "Edeka Filiale", "img": "🥛", "stock": 200},
    {"id": "p2", "name": "Grill-Saucen Set", "price": 8.99, "shop": "Picnic Delivery", "img": "bad", "stock": 15},
]

carts = {}  # Einfacher In-Memory Speicher für Warenkörbe

# --- MODELS ---
class CartItem(BaseModel):
    product_id: str
    quantity: int
    session_id: str

# --- UCP ENDPUNKTE ---

@app.get("/.well-known/ucp")
def get_manifest():
    return {
        "ucp_version": "0.1.0",
        "id": "edeka-group-api",
        "name": "Edeka Group Unified Commerce",
        "capabilities": [
            {"id": "search", "uri": "/api/products", "method": "GET"},
            {"id": "cart", "uri": "/api/cart", "method": "POST"},
            {"id": "checkout", "uri": "/api/checkout", "method": "POST"}
        ]
    }

@app.get("/api/products")
def search_products(q: Optional[str] = None):
    if not q:
        return INVENTORY
    q = q.lower()
    return [p for p in INVENTORY if q in p["name"].lower() or q in p["shop"].lower()]

@app.post("/api/cart")
def add_to_cart(item: CartItem):
    # Produkt suchen
    product = next((p for p in INVENTORY if p["id"] == item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    
    # Warenkorb anlegen/holen
    if item.session_id not in carts:
        carts[item.session_id] = []
    
    # Item hinzufügen
    cart_entry = {
        "product": product["name"],
        "price": product["price"],
        "shop": product["shop"],
        "qty": item.quantity,
        "total": product["price"] * item.quantity
    }
    carts[item.session_id].append(cart_entry)
    
    return {"status": "success", "cart": carts[item.session_id]}

@app.get("/api/cart/{session_id}")
def get_cart(session_id: str):
    return carts.get(session_id, [])

@app.post("/api/checkout")
def checkout(session_id: str):
    if session_id not in carts or not carts[session_id]:
        raise HTTPException(status_code=400, detail="Warenkorb leer")
    
    total = sum(item["total"] for item in carts[session_id])
    order_data = carts[session_id]
    carts[session_id] = [] # Korb leeren
    
    return {
        "status": "confirmed",
        "order_id": f"ORD-{session_id[-4:]}-X",
        "total_amount": total,
        "items": len(order_data),
        "message": "Zahlung via UCP Token akzeptiert."
    }

# Startet den Server nur, wenn direkt ausgeführt (für lokale Tests)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)