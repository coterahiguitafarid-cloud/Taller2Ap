from django.contrib import admin

from .models import Aprendiz, Vehiculo


@admin.register(Aprendiz)
class AprendizAdmin(admin.ModelAdmin):
    list_display = ("document", "first_name", "last_name", "email", "program")
    search_fields = ("document", "first_name", "last_name", "email", "program")


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "marca", "modelo", "anio", "precio", "destacado")
    list_filter = ("tipo", "marca", "anio", "destacado")
    search_fields = ("marca", "modelo", "descripcion")
