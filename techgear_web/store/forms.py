from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        labels = {"username": "Nombre de usuario"}

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email


class ProductForm(forms.Form):
    name = forms.CharField(max_length=120, label="Nombre")
    description = forms.CharField(
        max_length=2000,
        label="Descripción",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    category = forms.CharField(
        max_length=80,
        label="Categoría",
        help_text="Ejemplos: Computadores, Componentes, Periféricos, Accesorios.",
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label="Precio",
    )
    stock = forms.IntegerField(min_value=0, label="Existencias")


class CartQuantityForm(forms.Form):
    product_id = forms.CharField(max_length=24, widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, max_value=99, label="Cantidad")
