from fastapi import APIRouter

router = APIRouter()

@router.get("/.well-known/ucp", tags=["Discovery"])
def get_manifest():
    """
    UCP Discovery Endpoint.
    Agents start here to learn capabilities.
    """
    return {
        "ucp_version": "1.0",
        "id": "omniretail-core",
        "capabilities": [
            {
                "id": "search",
                "endpoint": "/api/products",
                "description": "Semantic search for global inventory",
                "params": ["q", "category", "max_price"]
            },
            {
                "id": "cart",
                "endpoint": "/api/cart",
                "description": "Session-based cart management"
            },
            {
                "id": "checkout",
                "endpoint": "/api/checkout",
                "description": "Tokenized payment processing"
            }
        ]
    }