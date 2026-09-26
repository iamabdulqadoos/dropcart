from fastapi import FastAPI
from sqlalchemy import text


from app.api.routes.products import router as product_router
from app.api.routes.carts import router as cart_router
from app.api.routes.orders import router as order_router

from app.core.database import engine

app = FastAPI(
    title="DropCart API",
    version="1.0.0",
)

app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
@app.get("/")
def root():
    return {
        "message": "Welcome to DropCart API"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/db-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar()
    }