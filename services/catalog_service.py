import sqlite3
from typing import List, Optional
from domain.models import Product

class CatalogService:
    def __init__(self, db_path="omniretail.db"):
        self.db_path = db_path

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search_products(self, query: Optional[str], category: Optional[str], max_price: Optional[float]) -> List[Product]:
        conn = self._get_conn()
        sql = "SELECT * FROM products WHERE 1=1"
        params = []

        if query:
            sql += " AND (lower(name) LIKE ? OR lower(description) LIKE ?)"
            params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])

        if category and category != "Alle":
            sql += " AND category = ?"
            params.append(category)

        if max_price:
            sql += " AND price <= ?"
            params.append(max_price)

        rows = conn.execute(sql, params).fetchall()
        conn.close()

        # Konvertierung in saubere Domain-Modelle
        return [Product(**dict(r)) for r in rows]