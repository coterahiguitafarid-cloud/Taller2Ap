from datetime import datetime, timezone
from decimal import Decimal

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import APIRouter, HTTPException, Path, status
from pymongo import ReturnDocument

from techgear_api.database import get_database, get_mongo_client
from techgear_api.models import (
    Order,
    OrderCreate,
    OrderLineItem,
    OrderStatus,
)


router = APIRouter(prefix="/api/orders", tags=["Pedidos"])


def decimal_value(value: Decimal128 | Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


def serialize_order(document: dict) -> Order:
    items = [
        OrderLineItem(
            product_id=item["product_id"],
            product_name=item["product_name"],
            quantity=item["quantity"],
            unit_price=decimal_value(item["unit_price"]),
        )
        for item in document["items"]
    ]
    return Order(
        id=str(document["_id"]),
        customer_id=document["customer_id"],
        items=items,
        total=decimal_value(document["total"]),
        status=document["status"],
        created_at=document["created_at"],
    )


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate) -> Order:
    database = get_database()
    products = database["products"]
    order_document = {
        "customer_id": order.customer_id,
        "items": [],
        "total": Decimal128("0"),
        "status": OrderStatus.pending.value,
        "created_at": datetime.now(timezone.utc),
    }
    total = Decimal("0")

    async with await get_mongo_client().start_session() as session:
        async with session.start_transaction():
            for item in order.items:
                product_id = ObjectId(item.product_id)
                product = await products.find_one_and_update(
                    {
                        "_id": product_id,
                        "stock": {"$gte": item.quantity},
                    },
                    {"$inc": {"stock": -item.quantity}},
                    return_document=ReturnDocument.AFTER,
                    session=session,
                )
                if product is None:
                    exists = await products.find_one(
                        {"_id": product_id},
                        {"_id": 1},
                        session=session,
                    )
                    if exists is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Producto {item.product_id} no encontrado.",
                        )
                    raise HTTPException(
                        status_code=409,
                        detail=f"Stock insuficiente para el producto {item.product_id}.",
                    )

                unit_price = decimal_value(product["price"])
                total += unit_price * item.quantity
                order_document["items"].append(
                    {
                        "product_id": str(product_id),
                        "product_name": product["name"],
                        "quantity": item.quantity,
                        "unit_price": Decimal128(str(unit_price)),
                    }
                )

            order_document["total"] = Decimal128(str(total))
            result = await database["orders"].insert_one(
                order_document,
                session=session,
            )
            order_document["_id"] = result.inserted_id

    return serialize_order(order_document)


@router.get("", response_model=list[Order])
async def list_orders() -> list[Order]:
    orders = get_database()["orders"]
    documents = await orders.find().sort("created_at", -1).to_list(length=500)
    return [serialize_order(document) for document in documents]


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str = Path(pattern=r"^[0-9a-fA-F]{24}$"),
) -> Order:
    document = await get_database()["orders"].find_one(
        {"_id": ObjectId(order_id)}
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return serialize_order(document)
