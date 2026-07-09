from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import alerts, products

app = FastAPI(title="E-commerce Watch API")

app.include_router(products.router)
app.include_router(alerts.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    return {"message": "API opérationnelle"}
