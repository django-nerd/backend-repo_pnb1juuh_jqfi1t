import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_document, get_documents, db
from schemas import Order

app = FastAPI(title="Leather Wallets API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Leather Wallets Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Simple public catalog for two wallet variants
class CatalogItem(BaseModel):
    id: str
    title: str
    color: str
    description: str
    price: float
    images: List[str]
    gift_box: bool = True

CATALOG: List[CatalogItem] = [
    CatalogItem(
        id="wallet-black",
        title="Кожаный кошелёк — Чёрный",
        color="black",
        description="Премиальная натуральная кожа, аккуратная прострочка, отделы для карт и купюр.",
        price=2490.0,
        images=[
            "/images/wallet-black-1.jpg",
            "/images/wallet-black-2.jpg"
        ],
        gift_box=True
    ),
    CatalogItem(
        id="wallet-brown",
        title="Кожаный кошелёк — Коричневый",
        color="brown",
        description="Тёплый оттенок коричневой кожи. Приятный на ощупь, долговечный, стильный.",
        price=2490.0,
        images=[
            "/images/wallet-brown-1.jpg",
            "/images/wallet-brown-2.jpg"
        ],
        gift_box=True
    ),
]

@app.get("/api/catalog", response_model=List[CatalogItem])
def get_catalog():
    return CATALOG

@app.post("/api/order")
def create_order(order: Order):
    try:
        order_id = create_document("order", order)
        return {"success": True, "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
