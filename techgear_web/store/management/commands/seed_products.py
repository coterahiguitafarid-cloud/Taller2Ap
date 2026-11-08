from django.core.management.base import BaseCommand, CommandError

from store.services import StoreAPIError, create_product, list_products, update_product


SAMPLE_PRODUCTS = [
    {
        "name": "Teclado mecánico RGB",
        "description": "Teclado mecánico de tamaño completo con retroiluminación RGB.",
        "category": "Periféricos",
        "price": "249.90",
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Mouse inalámbrico ergonómico",
        "description": "Mouse óptico inalámbrico con diseño ergonómico y conexión USB.",
        "category": "Periféricos",
        "price": "89.00",
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "SSD NVMe 1 TB",
        "description": "Unidad de estado sólido NVMe de 1 TB para equipos compatibles.",
        "category": "Almacenamiento",
        "price": "329.50",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Memoria RAM DDR5 16 GB",
        "description": "Módulo de memoria DDR5 de 16 GB para computadores de escritorio.",
        "category": "Componentes",
        "price": "179.00",
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Audífonos USB con micrófono",
        "description": "Audífonos estéreo con micrófono integrado para trabajo y estudio.",
        "category": "Accesorios",
        "price": "119.90",
        "stock": 22,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    },
]


class Command(BaseCommand):
    help = "Agrega productos de hardware de demostración sin duplicarlos."

    def handle(self, *args, **options) -> None:
        try:
            existing_products = {
                product["name"]: product
                for product in list_products()
            }
            for product in SAMPLE_PRODUCTS:
                existing = existing_products.get(product["name"])
                if existing and existing.get("image_url"):
                    self.stdout.write(f"Ya existe con imagen: {product['name']}")
                    continue
                if existing:
                    update_product(
                        existing["id"],
                        {
                            "name": existing["name"],
                            "description": existing["description"],
                            "category": existing["category"],
                            "price": existing["price"],
                            "stock": existing["stock"],
                            "image_url": product["image_url"],
                        },
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Imagen agregada: {product['name']}")
                    )
                else:
                    create_product(product)
                    self.stdout.write(
                        self.style.SUCCESS(f"Agregado: {product['name']}")
                    )
        except StoreAPIError as exc:
            raise CommandError(str(exc)) from exc
