from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Vehiculo(models.Model):
    class Tipo(models.TextChoices):
        CARRO = "carro", "Carro"
        MOTO = "moto", "Moto"

    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices)
    marca = models.CharField("marca", max_length=60)
    modelo = models.CharField("modelo", max_length=100)
    anio = models.PositiveSmallIntegerField(
        "año",
        validators=[MinValueValidator(1950), MaxValueValidator(2035)],
    )
    precio = models.DecimalField(
        "precio (COP)",
        max_digits=14,
        decimal_places=0,
        validators=[MinValueValidator(1)],
    )
    kilometraje = models.PositiveIntegerField("kilometraje (km)", default=0)
    cilindraje = models.PositiveSmallIntegerField(
        "cilindraje (cc)",
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    descripcion = models.TextField("descripción", max_length=1000)
    imagen_url = models.URLField("URL de imagen", blank=True)
    correo_contacto = models.EmailField("correo de contacto")
    destacado = models.BooleanField("destacado", default=False)
    creado = models.DateTimeField("fecha de publicación", auto_now_add=True)

    class Meta:
        ordering = ["-destacado", "-creado"]
        verbose_name = "vehículo"
        verbose_name_plural = "vehículos"

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio})"


class Aprendiz(models.Model):
    document = models.CharField("documento", max_length=30, unique=True)
    first_name = models.CharField("nombres", max_length=100)
    last_name = models.CharField("apellidos", max_length=100)
    email = models.EmailField("correo electrónico", unique=True)
    age = models.PositiveSmallIntegerField(
        "edad",
        validators=[MinValueValidator(1)],
    )
    program = models.CharField("programa", max_length=150)
    record_number = models.PositiveIntegerField("número de ficha", unique=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "aprendiz"
        verbose_name_plural = "aprendices"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
