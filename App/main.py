from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from Database.db_connect import Base, engine
from config import response
from Routers import (category_api,
                     size_type_api,
                     user_api,
                     menu_products,
                     address_zone,
                     payment_api,
                     shift_management,
                     order_api,
                     invoice_api)

# حذف الجداول القديمة وإعادة إنشائها (مؤقتاً للتطوير)
# Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="E-Commerce System 'Wempy'")

# Static Files - لعرض الصور
app.mount("/images", StaticFiles(directory="Static_Data/images"), name="images")

# Include routers
app.include_router(user_api.router)
app.include_router(category_api.router)
app.include_router(menu_products.products_router)
app.include_router(size_type_api.size_router)
app.include_router(size_type_api.type_router)
app.include_router(menu_products.variants_router)

app.include_router(address_zone.zone_router)
app.include_router(address_zone.address_router)
app.include_router(payment_api.payment_router)
app.include_router(shift_management.router)
app.include_router(order_api.router)
app.include_router(invoice_api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    if "/register" in request.url.path:
        message = response.REGISTER_VALIDATION_ERROR
    elif "/login" in request.url.path:
        message = response.LOGIN_VALIDATION_ERROR
    else:
        message = "البيانات غير صحيحة"
    return JSONResponse(status_code=422, content={"error": message})