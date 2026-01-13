from pydantic import BaseModel, Field
from typing import Optional, List

# --- UCP Standard Schemas ---

class Product(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "EUR"
    shop: str
    # HIER FEHLTE DAS FELD:
    img: str
    category: str
    stock: int

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    session_id: str

class CartEntry(BaseModel):
    """Interne Darstellung im Warenkorb inkl. Produktdetails"""
    product_name: str
    price: float
    qty: int
    total: float
    shop: str

class CheckoutRequest(BaseModel):
    session_id: str
    payment_token: str

class OrderConfirmation(BaseModel):
    order_id: str
    status: str
    total_amount: float
    message: str


class OrderSummary(BaseModel):
    order_id: str
    session_id: str
    total: float
    timestamp: str
    status: str