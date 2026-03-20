from fastapi import FastAPI, HTTPException, Query, Path
from service.product import get_all_products
from schema.product import Product

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
    data = get_all_products()
    products = data["products"]

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404, detail=f"Product not found with id={product_id}"
    )


# POST Routes


@app.post("/products")
def add_products(product: Product):
    print(product)
    return product
