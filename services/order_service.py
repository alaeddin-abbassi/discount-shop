import sqlite3
import uuid
from datetime import datetime
from domain.models import CartItem, CartEntry, OrderConfirmation, OrderSummary


class OrderService:
    def __init__(self, db_path="omniretail.db"):
        self.db_path = db_path

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_item(self, item: CartItem):
        conn = self._get_conn()
        # 1. Validieren: Gibt es das Produkt?
        prod = conn.execute("SELECT * FROM products WHERE id = ?", (item.product_id,)).fetchone()
        if not prod:
            conn.close()
            raise ValueError(f"Product {item.product_id} not found")

        # 2. Add (Business Logic)
        conn.execute("INSERT INTO cart_items (session_id, product_id, qty) VALUES (?, ?, ?)",
                     (item.session_id, item.product_id, item.quantity))
        conn.commit()
        conn.close()
        return {"msg": "Added"}

    def get_cart_content(self, session_id: str) -> list[CartEntry]:
        conn = self._get_conn()
        rows = conn.execute('''
                            SELECT p.name as product_name, p.price, p.shop, c.qty, (p.price * c.qty) as total
                            FROM cart_items c JOIN products p ON c.product_id = p.id
                            WHERE c.session_id = ?
                            ''', (session_id,)).fetchall()
        conn.close()
        return [CartEntry(**dict(r)) for r in rows]

    def process_checkout(self, session_id: str, token: str) -> OrderConfirmation:
        # 1. Security Check (UCP Requirement)
        if not token.startswith("tok_"):
            raise PermissionError("Invalid Payment Token")

        conn = self._get_conn()
        items = self.get_cart_content(session_id)

        if not items:
            conn.close()
            raise ValueError("Cart is empty")

        total = sum(i.total for i in items)
        order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"

        # 2. Transaction (Atomic Write)
        try:
            conn.execute("INSERT INTO orders (order_id, session_id, total, timestamp, status) VALUES (?, ?, ?, ?, ?)",
                         (order_id, session_id, total, datetime.now().isoformat(), "CONFIRMED"))

            # Warenkorb leeren
            conn.execute("DELETE FROM cart_items WHERE session_id = ?", (session_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return OrderConfirmation(
            order_id=order_id,
            status="confirmed",
            total_amount=total,
            message="Transaction settled via UCP Ledger"
        )


    # Füge das in die Klasse OrderService ein:
    def get_all_orders(self) -> list[OrderSummary]:
        conn = self._get_conn()
        # Hole die neuesten Bestellungen zuerst
        rows = conn.execute("SELECT * FROM orders ORDER BY timestamp DESC").fetchall()
        conn.close()
        return [OrderSummary(order_id=r["order_id"], session_id=r["session_id"],
                             total=r["total"], timestamp=r["timestamp"], status=r["status"])
                for r in rows]