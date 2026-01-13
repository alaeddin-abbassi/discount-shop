import sys
import os

# Pfad-Hack (damit main.py gefunden wird)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, init_db  # WICHTIG: Wir importieren jetzt auch init_db!
import uuid

# --- DAS IST NEU: SETUP FIXTURE ---
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Diese Funktion läuft automatisch VOR allen Tests.
    Sie erstellt die Tabellen, damit der Fehler 'no such table' verschwindet.
    """
    print("\n⚡ Initialisiere Test-Datenbank...")
    init_db()  # Erstellt Tabellen & Mock-Daten
    print("✅ Datenbank bereit.")

# Client initialisieren
client = TestClient(app)

# --- DEINE TESTS (Unverändert) ---

def test_ucp_manifest_exists():
    """Governance Check"""
    response = client.get("/.well-known/ucp")
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    assert data["ucp_version"] == "1.0"
    print("\n✅ Governance Check: UCP Manifest valid.")

def test_search_inventory():
    """Inventory Check"""
    # Wir suchen nach "Steak" (wissen wir, dass es da ist)
    response = client.get("/api/products?q=Steak")
    assert response.status_code == 200
    products = response.json()

    # Falls die Mock-Daten anders heißen, prüfen wir generisch
    assert len(products) > 0
    print(f"\n✅ Inventory Check: Found {len(products)} items for 'Steak'.")

def test_full_purchase_flow():
    """Integration Flow"""
    session_id = f"test-sess-{uuid.uuid4()}"

    # 1. Produkt finden
    products = client.get("/api/products").json()
    assert len(products) > 0
    target_product = products[0]
    product_id = target_product["id"]

    print(f"\n🔄 Starte Kaufsimulation für: {target_product['name']} ({product_id})")

    # 2. In den Warenkorb
    cart_payload = {
        "product_id": product_id,
        "quantity": 2,
        "session_id": session_id
    }
    response = client.post("/api/cart", json=cart_payload)
    assert response.status_code == 200

    # 3. Warenkorb prüfen
    cart_response = client.get(f"/api/cart/{session_id}")
    cart_items = cart_response.json()
    assert len(cart_items) == 1

    # 4. Checkout
    checkout_payload = {
        "session_id": session_id,
        "payment_token": "tok_test_123_secure"
    }
    checkout_response = client.post("/api/checkout", json=checkout_payload)

    assert checkout_response.status_code == 200
    order_data = checkout_response.json()
    assert order_data["status"] == "confirmed"
    print(f"✅ Checkout Check: Order confirmed ({order_data['order_id']}).")

def test_checkout_security_fail():
    """Security Check"""
    bad_payload = {
        "session_id": "fake-session",
        "payment_token": "INVALID_TOKEN"
    }
    response = client.post("/api/checkout", json=bad_payload)
    # Erwartet 403 Forbidden
    assert response.status_code == 403
    print("\n✅ Security Check: Invalid token correctly blocked.")