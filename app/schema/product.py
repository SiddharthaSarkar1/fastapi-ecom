from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Annotated, List, Optional
from datetime import datetime

class Product(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discountPercentage: float
    rating: float
    stock: int
    is_active: bool
    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Upto 10 tags"),
    ]
    brand: str
    sku: Annotated[
        str,
        Field(
            min_length=6,
            max_length=30,
            title="SKU",
            description="Stock keeping unit",
            examples=["grt-345-jdr-342", "rta-435-j78-lkf"],
        ),
    ]
    weight: int
    createdAt: datetime



    @field_validator("sku", mode="after")
    @classmethod

    def validate_sku_format(cls, value: str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")
        
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU end with a 3-digit sequence like -234")
        
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_business_rule(cls, model: "Product"):
        if model.stock == 0 and model.is_active == True:
            raise ValueError("If stock is 0, is_active must be false")
        
        if model.discountPercentage > 0 and model.rating == 0:
            raise ValueError("Discounted product mush have the rating (rating != 0)")
        
        return model

    @computed_field

    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discountPercentage / 100), 2)

class ProductUpdate(BaseModel):
    title: str
    description: str
    category: str
    price: float
    discountPercentage: float
    rating: float
    stock: int
    is_active: bool
    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Upto 10 tags"),
    ]
    brand: str
    sku: Annotated[
        str,
        Field(
            min_length=6,
            max_length=30,
            title="SKU",
            description="Stock keeping unit",
            examples=["grt-345-jdr-342", "rta-435-j78-lkf"],
        ),
    ]
    weight: int


