from fastapi import FastAPI, HTTPException, Query
from service.product import get_all_products

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI."}


@app.get("/dummy-products/{id}")
def get_dummy_product(id: int):
    products = ["Laptop", "Iphone", "Charger", "Tab", "Monitor", "Mouse", "Adapter"]
    return products[id]


@app.get("/all-products")
def get_all_the_products():
    return get_all_products()


# /products?name="XYZ"
@app.get("/products")
def list_products(
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search product by name (case insensitive)",
    ),
    sort_by_price: bool = Query(default=False, description="Sort by product price"),
    order: str = Query(default="asc", description="Sort order when sort_by_price=true (asc, desc)")
):
    data = get_all_products()
    products = data["products"]

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
            matching_products = sorted(matching_products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(matching_products)

    return {"total": total, "products": matching_products}
