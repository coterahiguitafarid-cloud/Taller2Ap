import unittest
from datetime import datetime, timezone
from decimal import Decimal

from bson import ObjectId
from bson.decimal128 import Decimal128

from techgear_api.models import ProductCreate
from techgear_api.routers.products import product_document, serialize_product


class ProductImageTests(unittest.TestCase):
    def test_image_url_is_stored_as_a_mongo_compatible_string(self) -> None:
        product = ProductCreate(
            name="Teclado",
            description="Teclado mecánico.",
            category="Periféricos",
            price=Decimal("249.90"),
            stock=5,
            image_url="https://example.com/teclado.jpg",
        )

        document = product_document(product)

        self.assertEqual(document["image_url"], "https://example.com/teclado.jpg")
        self.assertIsInstance(document["price"], Decimal128)

    def test_existing_product_without_image_remains_compatible(self) -> None:
        product = serialize_product(
            {
                "_id": ObjectId("64b000000000000000000001"),
                "name": "Teclado",
                "description": "Teclado mecánico.",
                "category": "Periféricos",
                "price": Decimal128("249.90"),
                "stock": 5,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            }
        )

        self.assertIsNone(product.image_url)
