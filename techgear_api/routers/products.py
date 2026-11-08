from datetime import datetime, timezone
from decimal import Decimal

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from techgear_api.auth import require_portal_token
from techgear_api.database import get_database
from techgear_api.models import Product, ProductCreate


router = APIRouter(prefix="/api/products", tags=["Productos"])


def serialize_product(document: dict) -> Product:
    price = document["price"]
    if isinstance(price, Decimal128):
        price = price.to_decimal()
    else:
        price = Decimal(str(price))

    return Product(
        id=str(document["_id"]),
        name=document["name"],
        description=document["description"],
        category=document["category"],
        price=price,
        stock=document["stock"],
        image_url=document.get("image_url"),
        created_at=document["created_at"],
    )


def product_document(product: ProductCreate) -> dict:
    document = product.model_dump()
    document["price"] = Decimal128(str(document["price"]))
    if document["image_url"] is not None:
        document["image_url"] = str(document["image_url"])
    return document


@router.post(
    "",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_portal_token)],
)
async def create_product(product: ProductCreate) -> Product:
    products = get_database()["products"]
    document = product_document(product)
    document["created_at"] = datetime.now(timezone.utc)
    result = await products.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize_product(document)


@router.get("", response_model=list[Product])
async def list_products() -> list[Product]:
    products = get_database()["products"]
    documents = await products.find().sort("created_at", -1).to_list(length=500)
    return [serialize_product(document) for document in documents]


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str = Path(pattern=r"^[0-9a-fA-F]{24}$"),
) -> Product:
    document = await get_database()["products"].find_one(
        {"_id": ObjectId(product_id)}
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return serialize_product(document)


@router.put(
    "/{product_id}",
    response_model=Product,
    dependencies=[Depends(require_portal_token)],
)
async def update_product(
    product: ProductCreate,
    product_id: str = Path(pattern=r"^[0-9a-fA-F]{24}$"),
) -> Product:
    products = get_database()["products"]
    document = product_document(product)
    result = await products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": document},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    updated_document = await products.find_one({"_id": ObjectId(product_id)})
    if updated_document is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return serialize_product(updated_document)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_portal_token)],
)
async def delete_product(
    product_id: str = Path(pattern=r"^[0-9a-fA-F]{24}$"),
) -> Response:
    result = await get_database()["products"].delete_one(
        {"_id": ObjectId(product_id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
