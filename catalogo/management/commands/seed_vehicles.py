from django.core.management.base import BaseCommand

from catalogo.models import Vehiculo


DEMO_VEHICLES = [
    {
        "tipo": Vehiculo.Tipo.CARRO,
        "marca": "Porsche",
        "modelo": "911 Carrera",
        "anio": 2024,
        "precio": 750000000,
        "kilometraje": 5000,
        "descripcion": "Deportivo de referencia con motor trasero y diseño atemporal.",
        "correo_contacto": "ventas@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
        "destacado": True,
    },
    {
        "tipo": Vehiculo.Tipo.CARRO,
        "marca": "Porsche",
        "modelo": "Macan",
        "anio": 2023,
        "precio": 420000000,
        "kilometraje": 12000,
        "descripcion": "SUV deportivo con espacio para acompañarte en cada plan.",
        "correo_contacto": "ventas@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?auto=format&fit=crop&w=1200&q=85",
    },
    {
        "tipo": Vehiculo.Tipo.MOTO,
        "marca": "Ducati",
        "modelo": "Monster",
        "anio": 2024,
        "precio": 78000000,
        "kilometraje": 1800,
        "cilindraje": 937,
        "descripcion": "Naked ligera y ágil, pensada para disfrutar tanto la ciudad como la ruta.",
        "correo_contacto": "motos@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=85",
        "destacado": True,
    },
    {
        "tipo": Vehiculo.Tipo.MOTO,
        "marca": "Ducati",
        "modelo": "Panigale V2",
        "anio": 2023,
        "precio": 112000000,
        "kilometraje": 2400,
        "cilindraje": 955,
        "descripcion": "Diseño deportivo y prestaciones para quienes buscan sensaciones de pista.",
        "correo_contacto": "motos@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=1200&q=85",
    },
    {
        "tipo": Vehiculo.Tipo.MOTO,
        "marca": "Triumph",
        "modelo": "Bonneville T120",
        "anio": 2022,
        "precio": 65000000,
        "kilometraje": 4200,
        "cilindraje": 1200,
        "descripcion": "Estilo clásico británico combinado con tecnología moderna.",
        "correo_contacto": "motos@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=85",
    },
    {
        "tipo": Vehiculo.Tipo.MOTO,
        "marca": "Triumph",
        "modelo": "Tiger 900",
        "anio": 2024,
        "precio": 92000000,
        "kilometraje": 1600,
        "cilindraje": 888,
        "descripcion": "Aventura, comodidad y versatilidad para explorar nuevos caminos.",
        "correo_contacto": "motos@example.com",
        "imagen_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=85",
    },
]


class Command(BaseCommand):
    help = "Agrega vehículos de ejemplo al inventario sin duplicarlos."

    def handle(self, *args, **options):
        created_count = 0
        for vehicle in DEMO_VEHICLES:
            _, created = Vehiculo.objects.get_or_create(
                marca=vehicle["marca"],
                modelo=vehicle["modelo"],
                anio=vehicle["anio"],
                defaults=vehicle,
            )
            created_count += int(created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Inventario de demostración listo: {created_count} vehículos nuevos."
            )
        )
