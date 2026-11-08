from django.urls import path

from store import views


app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("registro/", views.register, name="register"),
    path("iniciar-sesion/", views.StoreLoginView.as_view(), name="login"),
    path("cerrar-sesion/", views.logout, name="logout"),
    path("carrito/", views.cart, name="cart"),
    path("carrito/agregar/<str:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("carrito/quitar/<str:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("pedidos/", views.orders, name="orders"),
    path("pedidos/confirmar/", views.checkout, name="checkout"),
    path("administracion/productos/", views.admin_products, name="admin_products"),
    path("administracion/productos/nuevo/", views.product_create, name="product_create"),
    path(
        "administracion/productos/<str:product_id>/editar/",
        views.product_edit,
        name="product_edit",
    ),
    path(
        "administracion/productos/<str:product_id>/eliminar/",
        views.product_delete,
        name="product_delete",
    ),
]
