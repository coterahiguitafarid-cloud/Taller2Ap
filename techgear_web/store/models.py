import secrets

from django.conf import settings
from django.db import models


def generate_api_customer_id() -> str:
    return secrets.token_hex(12)


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    api_customer_id = models.CharField(
        max_length=24,
        unique=True,
        default=generate_api_customer_id,
    )

    def __str__(self) -> str:
        return f"Perfil de {self.user.username}"
