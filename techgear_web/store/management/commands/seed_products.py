from django.core.management.base import BaseCommand, CommandError

from store.services import StoreAPIError, create_product, list_products


SAMPLE_PRODUCTS = [
    {
        "name": "Teclado mecánico RGB",
        "description": "Teclado mecánico de tamaño completo con retroiluminación RGB.",
        "category": "Periféricos",
        "price": "249.90",
        "stock": 25,
    },
    {
        "name": "Mouse inalámbrico ergonómico",
        "description": "Mouse óptico inalámbrico con diseño ergonómico y conexión USB.",
        "category": "Periféricos",
        "price": "89.00",
        "stock": 30,
    },
    {
        "name": "SSD NVMe 1 TB",
        "description": "Unidad de estado sólido NVMe de 1 TB para equipos compatibles.",
        "category": "Almacenamiento",
        "price": "329.50",
        "stock": 40,
    },
    {
        "name": "Memoria RAM DDR5 16 GB",
        "description": "Módulo de memoria DDR5 de 16 GB para computadores de escritorio.",
        "category": "Componentes",
        "price": "179.00",
        "stock": 18,
    },
    {
        "name": "Audífonos USB con micrófono",
        "description": "Audífonos estéreo con micrófono integrado para trabajo y estudio.",
        "category": "Accesorios",
        "price": "119.90",
        "stock": 22,
    },
]


class Command(BaseCommand):
    help = "Agrega productos de hardware de demostración sin duplicarlos."

    def handle(self, *args, **options) -> None:
        try:
            existing_names = {product["name"] for product in list_products()}
            for product in SAMPLE_PRODUCTS:
                if product["name"] in existing_names:
                    self.stdout.write(f"Ya existe: {product['name']}")
                    continue
                create_product(product)
                self.stdout.write(self.style.SUCCESS(f"Agregado: {product['name']}"))
        except StoreAPIError as exc:
            raise CommandError(str(exc)) from exc
