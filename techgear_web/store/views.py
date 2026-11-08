from functools import wraps
from decimal import Decimal
from typing import Any, Callable, TypeVar

from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from store.forms import CartQuantityForm, ProductForm, RegistrationForm
from store.models import CustomerProfile
from store.services import (
    StoreAPIError,
    create_order,
    create_product,
    delete_product,
    get_product,
    list_orders,
    list_products,
    update_product,
)

ViewFunction = TypeVar("ViewFunction", bound=Callable[..., HttpResponse])


def show_api_errors(view: ViewFunction) -> ViewFunction:
    @wraps(view)
    def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            return view(request, *args, **kwargs)
        except StoreAPIError as exc:
            return render(
                request,
                "store/api_error.html",
                {"error": str(exc)},
                status=503,
            )

    return wrapped  # type: ignore[return-value]


class StoreLoginView(LoginView):
    template_name = "store/login.html"
    redirect_authenticated_user = True


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("store:product_list")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        CustomerProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Tu cuenta fue creada correctamente.")
        return redirect("store:product_list")
    return render(request, "store/register.html", {"form": form})


@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    messages.success(request, "Has cerrado sesión.")
    return redirect("store:product_list")


def product_list(request: HttpRequest) -> HttpResponse:
    api_error = None
    try:
        products = list_products()
    except StoreAPIError as exc:
        products = []
        api_error = str(exc)

    selected_category = request.GET.get("category", "").strip()
    categories = sorted({str(product["category"]) for product in products})
    if selected_category:
        products = [
            product
            for product in products
            if product["category"].casefold() == selected_category.casefold()
        ]
    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "api_error": api_error,
        },
        status=503 if api_error else 200,
    )


@require_POST
def add_to_cart(request: HttpRequest, product_id: str) -> HttpResponse:
    form = CartQuantityForm(request.POST)
    if not form.is_valid() or form.cleaned_data["product_id"] != product_id:
        messages.error(request, "La cantidad indicada no es válida.")
        return redirect("store:product_list")

    try:
        product = get_product(product_id)
    except StoreAPIError as exc:
        messages.error(request, str(exc))
        return redirect("store:product_list")

    if product["stock"] < form.cleaned_data["quantity"]:
        messages.error(request, "No hay existencias suficientes para esa cantidad.")
        return redirect("store:product_list")

    cart = request.session.get("cart", {})
    current_quantity = int(cart.get(product_id, 0))
    requested_quantity = current_quantity + form.cleaned_data["quantity"]
    if requested_quantity > product["stock"]:
        messages.error(request, "La cantidad supera las existencias disponibles.")
        return redirect("store:product_list")

    cart[product_id] = requested_quantity
    request.session["cart"] = cart
    messages.success(request, "Producto agregado al carrito.")
    return redirect("store:cart")


@show_api_errors
def cart(request: HttpRequest) -> HttpResponse:
    product_ids = request.session.get("cart", {})
    product_map = {product["id"]: product for product in list_products()}
    items = []
    unavailable_ids = set(product_ids) - set(product_map)
    if unavailable_ids:
        for product_id in unavailable_ids:
            product_ids.pop(product_id, None)
        request.session["cart"] = product_ids
        messages.warning(
            request,
            "Se retiraron del carrito productos que ya no están disponibles.",
        )
    for product_id, quantity in product_ids.items():
        product = product_map.get(product_id)
        if product is not None:
            quantity = int(quantity)
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "subtotal": Decimal(str(product["price"])) * quantity,
                }
            )
    return render(request, "store/cart.html", {"items": items})


@require_POST
def remove_from_cart(request: HttpRequest, product_id: str) -> HttpResponse:
    cart_items = request.session.get("cart", {})
    cart_items.pop(product_id, None)
    request.session["cart"] = cart_items
    messages.success(request, "Producto retirado del carrito.")
    return redirect("store:cart")


@login_required
@require_POST
def checkout(request: HttpRequest) -> HttpResponse:
    cart_items = request.session.get("cart", {})
    if not cart_items:
        messages.error(request, "Agrega productos antes de confirmar el pedido.")
        return redirect("store:cart")

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    order_items = [
        {"product_id": product_id, "quantity": quantity}
        for product_id, quantity in cart_items.items()
    ]
    try:
        order = create_order(profile.api_customer_id, order_items)
    except StoreAPIError as exc:
        messages.error(request, str(exc))
        return redirect("store:cart")

    request.session["cart"] = {}
    messages.success(request, f"Pedido {order['id']} creado correctamente.")
    return redirect("store:orders")


@login_required
@show_api_errors
def orders(request: HttpRequest) -> HttpResponse:
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    customer_orders = [
        order
        for order in list_orders()
        if order["customer_id"] == profile.api_customer_id
    ]
    return render(request, "store/orders.html", {"orders": customer_orders})


def is_store_admin(user: Any) -> bool:
    return user.is_authenticated and user.is_staff


@user_passes_test(is_store_admin)
@show_api_errors
def admin_products(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "store/admin_products.html",
        {"products": list_products()},
    )


@user_passes_test(is_store_admin)
@require_http_methods(["GET", "POST"])
def product_create(request: HttpRequest) -> HttpResponse:
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_product(form.cleaned_data)
        except StoreAPIError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Producto creado correctamente.")
            return redirect("store:admin_products")
    return render(request, "store/product_form.html", {"form": form, "title": "Nuevo producto"})


@user_passes_test(is_store_admin)
@show_api_errors
@require_http_methods(["GET", "POST"])
def product_edit(request: HttpRequest, product_id: str) -> HttpResponse:
    product = get_product(product_id)
    form = ProductForm(request.POST or None, initial=product)
    if request.method == "POST" and form.is_valid():
        try:
            update_product(product_id, form.cleaned_data)
        except StoreAPIError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("store:admin_products")
    return render(
        request,
        "store/product_form.html",
        {"form": form, "title": "Editar producto"},
    )


@user_passes_test(is_store_admin)
@require_POST
def product_delete(request: HttpRequest, product_id: str) -> HttpResponse:
    try:
        delete_product(product_id)
    except StoreAPIError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Producto eliminado correctamente.")
    return redirect("store:admin_products")
