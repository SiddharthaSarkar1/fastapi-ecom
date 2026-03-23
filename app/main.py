from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
import os

from fastapi import Depends, FastAPI, HTTPException, Query, Path, Request
from fastapi.responses import JSONResponse

from service.product import (
    get_all_products,
    add_product,
    remove_product,
    change_product,
    load_products,
)
from schema.product import Product, ProductUpdate

load_dotenv()

app = FastAPI()


# Middleware
@app.middleware("http")
async def lifecycle(request: Request, call_next):
    print("Before Request!!!")
    response = await call_next(request)
    print("After Request!!!")
    return response


def common_logic():
    print("This is common logic.")
    return "This is common logic."


@app.get("/", response_model=Dict)
def root(dep=Depends(common_logic)):
    DB_PATH = os.getenv("BASE_URL")
    # return {"message": "Welcome to FastAPI.", "dependency": dep, "data_path": DB_PATH}
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to FastAPI.",
            "dependency": dep,
            "data_path": DB_PATH,
        },
    )


@app.get("/dummy-products/{id}")
def get_dummy_product(id: int):
    products = ["Laptop", "Iphone", "Charger", "Tab", "Monitor", "Mouse", "Adapter"]
    return products[id]


@app.get("/all-products", response_model=List[Dict])
def get_all_the_products(dep=Depends(load_products)):  # dep is dependency injection
    # return get_all_products()
    return dep


# /products?name="XYZ"....
@app.get("/products")
def list_products(
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search product by name (case insensitive)",
        examples="furniture",
    ),
    sort_by_price: bool = Query(default=False, description="Sort by product price"),
    order: str = Query(
        default="asc", description="Sort order when sort_by_price=true (asc, desc)"
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=50,
        description="No of items to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset",
    ),
):
    products = get_all_products()

    if name:
        needle = name.strip().lower()

        matching_products = [
            p for p in products if needle in p.get("title", "").lower()
        ]

        if not matching_products:
            raise HTTPException(
                status_code=404, detail=f"No product found with matching name={name}"
            )

        if sort_by_price:
            reverse = order == "desc"
            matching_products = sorted(
                matching_products, key=lambda p: p.get("price", 0), reverse=reverse
            )

    matching_products = matching_products[offset : offset + limit]
    total = len(matching_products)
    return {"total": total, "products": matching_products}


@app.get("/products/{product_id}")
def get_prodict_by_id(
    product_id: int = Path(
        ..., ge=1, le=101, description="Id of the product", examples="1"
    )
):
    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404, detail=f"Product not found with id={product_id}"
    )


# POST Routes


@app.post("/products", status_code=201)
def create_products(product: Product):
    product_dict = product.model_dump(mode="json")
    products = get_all_products()
    products_len = len(products)
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    product_dict["id"] = int(products_len + 1)
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return product.model_dump(mode="json")


# DELETE


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int = Path(..., description="Product ID", examples="11")
):
    try:
        res = remove_product(product_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Update


@app.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate = ...):
    try:
        update_product = change_product(
            product_id, payload.model_dump(mode="json", exclude_unset=True)
        )
        return update_product
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
