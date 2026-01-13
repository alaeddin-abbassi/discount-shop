import sqlite3
import os

DB_NAME = "omniretail.db"

def get_db_connection():
    """
    Stellt eine Verbindung zur SQLite-Datenbank her.
    Nutzt Row-Factory für dict-ähnlichen Zugriff (z.B. row['name']).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialisiert die Tabellen und füllt Mock-Daten, falls leer.
    Wird beim Start von main.py oder tests aufgerufen.
    """
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Tabelle: PRODUCTS (Erweitert um 'img' und 'category')
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  description TEXT,
                  price REAL,
                  shop TEXT,
                  img TEXT,
                  category TEXT,
                  stock INTEGER)''')

    # 2. Tabelle: CART_ITEMS
    c.execute('''CREATE TABLE IF NOT EXISTS cart_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  product_id TEXT,
                  qty INTEGER)''')

    # 3. Tabelle: ORDERS
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (order_id TEXT PRIMARY KEY,
                  session_id TEXT,
                  total REAL,
                  timestamp TEXT,
                  status TEXT)''')

    conn.commit()

    # --- MOCK DATEN CHECK ---
    # Wir prüfen, ob Produkte da sind. Wenn nicht -> Einfügen.
    try:
        c.execute("SELECT count(*) FROM products")
        if c.fetchone()[0] == 0:
            print("⚡ Datenbank leer. Fülle Mock-Daten...")
            mock_data = [
                ("p1", "Bio Rindersteak (Dry Aged)", "Premium Fleisch aus lokaler Zucht", 24.90, "Premium Market (Local)", "🥩", "Fresh", 50),
                ("b1", "Grill-Holzkohle 3kg", "Buchenholz, lange Brenndauer", 4.99, "Budget Online (Warehouse)", "🔥", "Non-Food", 100),
                ("d1", "Pilsener Premium (Kasten)", "20x0,5l Flaschen", 14.99, "Quick Delivery (Service)", "🍺", "Drinks", 20),
                ("m1", "Weidemilch 3.8%", "Frische Vollmilch", 1.49, "Premium Market (Local)", "🥛", "Fresh", 200),
                ("s1", "BBQ Saucen Set", "5 verschiedene Saucen", 8.99, "Quick Delivery (Service)", "🥣", "Food", 15),
                ("w1", "Rotwein Reserve", "Trockener Merlot aus Frankreich", 9.99, "Budget Online (Warehouse)", "🍷", "Drinks", 60),
            ]
            c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", mock_data)
            conn.commit()
            print("✅ Mock-Daten erfolgreich eingefügt.")
    except Exception as e:
        print(f"⚠️ Fehler beim Mock-Daten Insert: {e}")

    conn.close()