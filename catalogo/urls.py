from django.urls import path

from . import views

urlpatterns = [
    path("", views.catalogo_view, name="catalogo"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.register_view, name="registro"),
    path("logout/", views.logout_view, name="logout"),
    path("vehiculos/nuevo/", views.vehiculo_create, name="vehiculo_create"),
    path("vehiculos/<int:pk>/editar/", views.vehiculo_update, name="vehiculo_update"),
    path("vehiculos/<int:pk>/eliminar/", views.vehiculo_delete, name="vehiculo_delete"),
    path("api/token/", views.api_token, name="api_token"),
    path("api/usuarios/", views.api_users, name="api_users"),
    path("api/usuarios/me/", views.api_current_user, name="api_current_user"),
]
