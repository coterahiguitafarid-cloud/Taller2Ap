from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from store.management.commands.seed_products import SAMPLE_PRODUCTS
from store.models import CustomerProfile
from store.services import StoreAPIError


@override_settings(TECHGEAR_API_TOKEN="portal-test-token")
class StoreAPITests(TestCase):
    @patch("store.services.requests.request")
    def test_admin_api_request_includes_portal_bearer_token(self, request_mock) -> None:
        from store.services import create_product

        request_mock.return_value.ok = True
        request_mock.return_value.status_code = 201
        request_mock.return_value.json.return_value = PRODUCT
        create_product(
            {
                "name": "Teclado",
                "category": "Periféricos",
                "price": "249.90",
                "image_url": "https://example.com/teclado.jpg",
            }
        )
        self.assertEqual(
            request_mock.call_args.kwargs["headers"]["Authorization"],
            "Bearer portal-test-token",
        )
        self.assertEqual(
            request_mock.call_args.kwargs["json"]["image_url"],
            "https://example.com/teclado.jpg",
        )
        self.assertEqual(request_mock.call_args.kwargs["json"]["price"], "249.90")

    @patch("store.services.requests.request")
    def test_product_updates_send_image_url_and_json_compatible_price(self, request_mock) -> None:
        from store.services import update_product

        request_mock.return_value.ok = True
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = PRODUCT
        update_product(
            PRODUCT["id"],
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": Decimal("249.90"),
                "stock": 10,
                "image_url": PRODUCT["image_url"],
            },
        )

        self.assertEqual(
            request_mock.call_args.kwargs["json"]["image_url"],
            PRODUCT["image_url"],
        )
        self.assertEqual(request_mock.call_args.kwargs["json"]["price"], "249.90")


PRODUCT = {
    "id": "64b000000000000000000001",
    "name": "Teclado mecánico RGB",
    "description": "Teclado mecánico para computador.",
    "category": "Periféricos",
    "price": "249.90",
    "stock": 10,
    "image_url": "https://example.com/teclado.jpg",
    "created_at": "2026-01-01T10:00:00Z",
}


class StorePagesTests(TestCase):
    @patch("store.views.list_products", side_effect=StoreAPIError("FastAPI no está iniciada."))
    def test_homepage_stays_branded_and_explains_api_outage(self, list_products_mock) -> None:
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "Tecnología para llegar más lejos", status_code=503)
        self.assertContains(response, "<title>Tienda | TcnoCO</title>", status_code=503)
        self.assertContains(
            response,
            "store/images/technoco-icon.svg",
            status_code=503,
        )
        self.assertContains(response, "FastAPI no está iniciada.", status_code=503)
        self.assertContains(response, "no mostramos productos de muestra", status_code=503)

    @patch("store.views.list_products", return_value=[{**PRODUCT, "stock": 0}])
    def test_out_of_stock_product_cannot_be_added_from_catalog(self, list_products_mock) -> None:
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agotado")
        self.assertNotContains(
            response,
            f'action="{reverse("store:add_to_cart", args=[PRODUCT["id"]])}"',
        )

    @patch("store.views.get_product", return_value={**PRODUCT, "stock": 0})
    def test_add_to_cart_rejects_product_without_stock(self, get_product_mock) -> None:
        response = self.client.post(
            reverse("store:add_to_cart", args=[PRODUCT["id"]]),
            {"product_id": PRODUCT["id"], "quantity": "1"},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("store:product_list"),
        )
        self.assertNotIn(PRODUCT["id"], self.client.session.get("cart", {}))
        self.assertContains(response, "No hay existencias suficientes")
        get_product_mock.assert_called_once_with(PRODUCT["id"])

    @patch("store.views.list_products", return_value=[PRODUCT])
    def test_public_catalog_filters_by_category(self, list_products_mock) -> None:
        response = self.client.get(
            reverse("store:product_list"),
            {"category": "Periféricos"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, PRODUCT["name"])
        self.assertContains(response, PRODUCT["image_url"])
        self.assertContains(response, f'alt="{PRODUCT["name"]}"')
        self.assertEqual(len(response.context["products"]), 1)

    @patch("store.views.list_products", return_value=[PRODUCT])
    def test_admin_dashboard_requires_staff_role(self, list_products_mock) -> None:
        response = self.client.get(reverse("store:admin_products"))
        self.assertRedirects(
            response,
            f"{reverse('store:login')}?next={reverse('store:admin_products')}",
        )
        list_products_mock.assert_not_called()

    @patch("store.views.list_products", return_value=[PRODUCT])
    def test_staff_can_open_admin_dashboard(self, list_products_mock) -> None:
        user = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("store:admin_products"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administrar productos")

    @patch("store.views.create_product", return_value=PRODUCT)
    def test_staff_can_create_product(self, create_product_mock) -> None:
        user = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)
        self.client.force_login(user)
        response = self.client.post(
            reverse("store:product_create"),
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": Decimal(PRODUCT["price"]),
                "stock": PRODUCT["stock"],
                "image_url": PRODUCT["image_url"],
            },
        )
        self.assertRedirects(
            response,
            reverse("store:admin_products"),
            fetch_redirect_response=False,
        )
        create_product_mock.assert_called_once_with(
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": Decimal(PRODUCT["price"]),
                "stock": PRODUCT["stock"],
                "image_url": PRODUCT["image_url"],
            }
        )

    @patch("store.views.update_product", return_value=PRODUCT)
    @patch("store.views.get_product", return_value=PRODUCT)
    def test_staff_can_update_product(self, get_product_mock, update_product_mock) -> None:
        user = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)
        self.client.force_login(user)
        response = self.client.post(
            reverse("store:product_edit", args=[PRODUCT["id"]]),
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": PRODUCT["price"],
                "stock": "8",
                "image_url": PRODUCT["image_url"],
            },
        )
        self.assertRedirects(
            response,
            reverse("store:admin_products"),
            fetch_redirect_response=False,
        )
        get_product_mock.assert_called_once_with(PRODUCT["id"])
        update_product_mock.assert_called_once_with(
            PRODUCT["id"],
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": Decimal(PRODUCT["price"]),
                "stock": 8,
                "image_url": PRODUCT["image_url"],
            },
        )

    @patch("store.views.create_product")
    def test_staff_cannot_create_product_with_invalid_image_url(self, create_product_mock) -> None:
        user = User.objects.create_user(
            username="admin",
            password="VeryStrongPass123!",
            is_staff=True,
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse("store:product_create"),
            {
                "name": PRODUCT["name"],
                "description": PRODUCT["description"],
                "category": PRODUCT["category"],
                "price": PRODUCT["price"],
                "stock": PRODUCT["stock"],
                "image_url": "javascript:alert(1)",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URL")
        create_product_mock.assert_not_called()

    @patch("store.views.delete_product")
    def test_staff_can_delete_product_only_with_post(self, delete_product_mock) -> None:
        user = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)
        self.client.force_login(user)
        path = reverse("store:product_delete", args=[PRODUCT["id"]])
        self.assertEqual(self.client.get(path).status_code, 405)
        response = self.client.post(path)
        self.assertRedirects(
            response,
            reverse("store:admin_products"),
            fetch_redirect_response=False,
        )
        delete_product_mock.assert_called_once_with(PRODUCT["id"])

    def test_registration_creates_customer_profile(self) -> None:
        response = self.client.post(
            reverse("store:register"),
            {
                "username": "cliente",
                "email": "cliente@example.com",
                "password1": "VeryStrongPass123!",
                "password2": "VeryStrongPass123!",
            },
        )
        self.assertRedirects(
            response,
            reverse("store:product_list"),
            fetch_redirect_response=False,
        )
        profile = CustomerProfile.objects.get(user__username="cliente")
        self.assertEqual(len(profile.api_customer_id), 24)

    @patch("store.views.create_order", return_value={"id": "pedido-1"})
    def test_checkout_requires_login_and_clears_cart(self, create_order_mock) -> None:
        session = self.client.session
        session["cart"] = {PRODUCT["id"]: 2}
        session.save()
        checkout_url = reverse("store:checkout")
        response = self.client.post(checkout_url)
        self.assertRedirects(response, f"{reverse('store:login')}?next={checkout_url}")
        create_order_mock.assert_not_called()

        user = User.objects.create_user(username="cliente", password="StrongPass123!")
        profile = CustomerProfile.objects.create(user=user)
        self.client.force_login(user)
        response = self.client.post(checkout_url)
        self.assertRedirects(
            response,
            reverse("store:orders"),
            fetch_redirect_response=False,
        )
        create_order_mock.assert_called_once_with(
            profile.api_customer_id,
            [{"product_id": PRODUCT["id"], "quantity": 2}],
        )
        self.assertEqual(self.client.session["cart"], {})

    @patch(
        "store.views.create_order",
        side_effect=StoreAPIError("Stock insuficiente para el producto."),
    )
    def test_checkout_stock_error_keeps_cart_and_shows_message(self, create_order_mock) -> None:
        user = User.objects.create_user(
            username="cliente",
            password="VeryStrongPass123!",
        )
        CustomerProfile.objects.create(user=user)
        self.client.force_login(user)
        session = self.client.session
        session["cart"] = {PRODUCT["id"]: 2}
        session.save()

        with patch("store.views.list_products", return_value=[PRODUCT]):
            response = self.client.post(reverse("store:checkout"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("store:cart"))
        self.assertContains(response, "Stock insuficiente para el producto.")
        self.assertEqual(self.client.session["cart"], {PRODUCT["id"]: 2})
        create_order_mock.assert_called_once()

    @patch(
        "store.views.list_orders",
        return_value=[
            {"id": "propio", "customer_id": "cliente-id", "items": [], "total": "10", "status": "pending"},
            {"id": "otro", "customer_id": "otro-id", "items": [], "total": "20", "status": "pending"},
        ],
    )
    def test_order_history_only_shows_current_customer_orders(self, list_orders_mock) -> None:
        user = User.objects.create_user(username="cliente", password="StrongPass123!")
        CustomerProfile.objects.create(user=user, api_customer_id="cliente-id")
        self.client.force_login(user)
        response = self.client.get(reverse("store:orders"))
        self.assertContains(response, "propio")
        self.assertNotContains(response, "otro")


class SeedProductsCommandTests(TestCase):
    @patch("store.management.commands.seed_products.update_product")
    @patch("store.management.commands.seed_products.create_product")
    @patch("store.management.commands.seed_products.list_products")
    def test_seed_adds_missing_images_without_replacing_custom_images(
        self,
        list_products_mock,
        create_product_mock,
        update_product_mock,
    ) -> None:
        list_products_mock.return_value = [
            {
                "id": "64b000000000000000000001",
                "name": SAMPLE_PRODUCTS[0]["name"],
                "description": "Descripción personalizada",
                "category": "Mi categoría",
                "price": "99.90",
                "stock": 7,
            },
            {
                "id": "64b000000000000000000002",
                "name": SAMPLE_PRODUCTS[1]["name"],
                "description": "Mouse personalizado",
                "category": "Periféricos",
                "price": "89.00",
                "stock": 6,
                "image_url": "https://example.com/custom.jpg",
            },
        ]

        call_command("seed_products", stdout=StringIO())

        update_product_mock.assert_called_once_with(
            "64b000000000000000000001",
            {
                "name": SAMPLE_PRODUCTS[0]["name"],
                "description": "Descripción personalizada",
                "category": "Mi categoría",
                "price": "99.90",
                "stock": 7,
                "image_url": SAMPLE_PRODUCTS[0]["image_url"],
            },
        )
        self.assertEqual(create_product_mock.call_count, len(SAMPLE_PRODUCTS) - 2)
