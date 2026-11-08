from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

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
        create_product({"name": "Teclado", "category": "Periféricos"})
        self.assertEqual(
            request_mock.call_args.kwargs["headers"]["Authorization"],
            "Bearer portal-test-token",
        )


PRODUCT = {
    "id": "64b000000000000000000001",
    "name": "Teclado mecánico RGB",
    "description": "Teclado mecánico para computador.",
    "category": "Periféricos",
    "price": "249.90",
    "stock": 10,
    "created_at": "2026-01-01T10:00:00Z",
}


class StorePagesTests(TestCase):
    @patch("store.views.list_products", side_effect=StoreAPIError("FastAPI no está iniciada."))
    def test_homepage_stays_branded_and_explains_api_outage(self, list_products_mock) -> None:
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "Tecnología para llegar más lejos", status_code=503)
        self.assertContains(response, "FastAPI no está iniciada.", status_code=503)
        self.assertContains(response, "no mostramos productos de muestra", status_code=503)

    @patch("store.views.list_products", return_value=[PRODUCT])
    def test_public_catalog_filters_by_category(self, list_products_mock) -> None:
        response = self.client.get(
            reverse("store:product_list"),
            {"category": "Periféricos"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, PRODUCT["name"])
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
                "price": PRODUCT["price"],
                "stock": PRODUCT["stock"],
            },
        )
        self.assertRedirects(
            response,
            reverse("store:admin_products"),
            fetch_redirect_response=False,
        )
        create_product_mock.assert_called_once()

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
            },
        )
        self.assertRedirects(
            response,
            reverse("store:admin_products"),
            fetch_redirect_response=False,
        )
        get_product_mock.assert_called_once_with(PRODUCT["id"])
        update_product_mock.assert_called_once()

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
