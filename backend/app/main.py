from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.drops import router as drops_router

from app.api.routes.products import router as product_router
from app.api.routes.carts import router as cart_router
from app.api.routes.orders import router as order_router
from app.api.routes import (
    products,
    carts,
    orders,
    drops,
    checkout,
)
from app.api.routes import webhooks


app = FastAPI(
    title="DropCart API",
    description="Nexterse Technical Assessment - DropCart",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(drops_router)
app.include_router(checkout.router)
app.include_router(webhooks.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to DropCart API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }