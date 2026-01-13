from fastapi import APIRouter, HTTPException, Depends, Query
from domain.models import Product, CartItem, CheckoutRequest, OrderSummary
from services.catalog_service import CatalogService
from services.order_service import OrderService

router = APIRouter(prefix="/api")

# Dependency Injection (Clean Code Pattern)
def get_catalog(): return CatalogService()
def get_orders(): return OrderService()

@router.get("/products", response_model=list[Product], tags=["Commerce"])
def search(
        q: str = None,
        category: str = None,
        max_price: float = None,
        service: CatalogService = Depends(get_catalog)
):
    return service.search_products(q, category, max_price)

@router.post("/cart", tags=["Commerce"])
def add_to_cart(item: CartItem, service: OrderService = Depends(get_orders)):
    try:
        return service.add_item(item)
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.get("/cart/{session_id}", tags=["Commerce"])
def view_cart(session_id: str, service: OrderService = Depends(get_orders)):
    return service.get_cart_content(session_id)

@router.post("/checkout", tags=["Commerce"])
def checkout(req: CheckoutRequest, service: OrderService = Depends(get_orders)):
    try:
        return service.process_checkout(req.session_id, req.payment_token)
    except PermissionError:
        raise HTTPException(403, "Payment Token rejected")
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/orders", response_model=list[OrderSummary], tags=["Management"])
def get_orders(service: OrderService = Depends(get_orders)):
    return service.get_all_orders()