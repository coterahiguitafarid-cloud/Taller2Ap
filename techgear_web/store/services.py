from typing import Any

import requests
from django.conf import settings


class StoreAPIError(Exception):
    pass


def api_request(method: str, path: str, *, authenticated: bool = False, **kwargs: Any) -> Any:
    headers = kwargs.pop("headers", {})
    if authenticated:
        token = settings.TECHGEAR_API_TOKEN
        if not token:
            raise StoreAPIError(
                "Falta configurar TECHGEAR_API_TOKEN en el portal Django."
            )
        headers = {**headers, "Authorization": f"Bearer {token}"}

    try:
        response = requests.request(
            method,
            f"{settings.FASTAPI_BASE_URL}{path}",
            timeout=5,
            headers=headers,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise StoreAPIError(
            "No fue posible conectar con la API. Comprueba que FastAPI esté iniciada."
        ) from exc

    if not response.ok:
        try:
            detail = response.json().get("detail", "La API rechazó la solicitud.")
        except ValueError:
            detail = "La API rechazó la solicitud."
        raise StoreAPIError(str(detail))

    if response.status_code == 204:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise StoreAPIError(
            f"La API devolvió una respuesta inválida (código {response.status_code}, "
            f"tipo {response.headers.get('content-type')}): {response.text[:200]}"
        ) from exc


def list_products() -> list[dict[str, Any]]:
    return api_request("GET", "/api/products")


def get_product(product_id: str) -> dict[str, Any]:
    return api_request("GET", f"/api/products/{product_id}")


def create_product(data: dict[str, Any]) -> dict[str, Any]:
    payload = {**data, "price": str(data["price"])}
    return api_request("POST", "/api/products", authenticated=True, json=payload)


def update_product(product_id: str, data: dict[str, Any]) -> dict[str, Any]:
    payload = {**data, "price": str(data["price"])}
    return api_request(
        "PUT",
        f"/api/products/{product_id}",
        authenticated=True,
        json=payload,
    )


def delete_product(product_id: str) -> None:
    api_request("DELETE", f"/api/products/{product_id}", authenticated=True)


def create_order(customer_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    return api_request(
        "POST",
        "/api/orders",
        authenticated=True,
        json={"customer_id": customer_id, "items": items},
    )


def list_orders() -> list[dict[str, Any]]:
    return api_request("GET", "/api/orders", authenticated=True)