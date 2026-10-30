from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Aprendiz, Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            "tipo",
            "marca",
            "modelo",
            "anio",
            "precio",
            "kilometraje",
            "cilindraje",
            "descripcion",
            "imagen_url",
            "correo_contacto",
            "destacado",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
        self.fields["imagen_url"].required = False
        self.fields["cilindraje"].required = False


class AprendizForm(forms.ModelForm):
    class Meta:
        model = Aprendiz
        fields = [
            "document",
            "first_name",
            "last_name",
            "email",
            "age",
            "program",
            "record_number",
        ]
        widgets = {
            "age": forms.NumberInput(attrs={"min": 1}),
            "record_number": forms.NumberInput(attrs={"min": 1}),
        }


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
