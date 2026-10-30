import json
from json import JSONDecodeError

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .authentication import (
    ACCESS_TOKEN_COOKIE,
    ACCESS_TOKEN_SECONDS,
    create_access_token,
    get_token_user,
    jwt_required,
    set_access_token_cookie,
)
from .forms import RegistroForm, VehiculoForm
from .models import Vehiculo


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            response = redirect("catalogo")
            return set_access_token_cookie(response, create_access_token(user))
        messages.error(request, "Usuario o contraseña incorrectos.")
    elif get_token_user(request) is not None:
        return redirect("catalogo")

    return render(request, "catalogo/login.html")


def register_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
            response = redirect("catalogo")
            return set_access_token_cookie(response, create_access_token(user))
    else:
        form = RegistroForm()
    return render(request, "catalogo/register.html", {"form": form})


@require_POST
def logout_view(request):
    response = redirect("login")
    response.delete_cookie(ACCESS_TOKEN_COOKIE, samesite="Lax")
    messages.info(request, "Sesión cerrada correctamente.")
    return response


def catalogo_view(request):
    query = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    marca = request.GET.get("marca", "").strip()
    vehiculos = Vehiculo.objects.all()
    if query:
        vehiculos = vehiculos.filter(
            Q(marca__icontains=query)
            | Q(modelo__icontains=query)
            | Q(descripcion__icontains=query)
        )
    if tipo in Vehiculo.Tipo.values:
        vehiculos = vehiculos.filter(tipo=tipo)
    if marca:
        vehiculos = vehiculos.filter(marca=marca)
    return render(
        request,
        "catalogo/list.html",
        {
            "vehiculos": vehiculos,
            "jwt_user": get_token_user(request),
            "query": query,
            "selected_tipo": tipo,
            "selected_marca": marca,
            "tipos": Vehiculo.Tipo.choices,
            "marcas": Vehiculo.objects.order_by("marca")
            .values_list("marca", flat=True)
            .distinct(),
            "total_vehiculos": Vehiculo.objects.count(),
            "total_carros": Vehiculo.objects.filter(tipo=Vehiculo.Tipo.CARRO).count(),
            "total_motos": Vehiculo.objects.filter(tipo=Vehiculo.Tipo.MOTO).count(),
            "filtered_count": vehiculos.count(),
        },
    )


@jwt_required
def vehiculo_create(request):
    form = VehiculoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Vehículo publicado en el inventario.")
        return redirect("catalogo")
    return render(
        request,
        "catalogo/vehiculo_form.html",
        {"form": form, "titulo": "Publicar vehículo", "jwt_user": get_token_user(request)},
    )


@jwt_required
def vehiculo_update(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, instance=vehiculo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Vehículo actualizado.")
        return redirect("catalogo")
    return render(
        request,
        "catalogo/vehiculo_form.html",
        {
            "form": form,
            "titulo": "Editar vehículo",
            "jwt_user": get_token_user(request),
        },
    )


@jwt_required
@require_POST
def vehiculo_delete(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    vehiculo.delete()
    messages.success(request, "Vehículo eliminado del inventario.")
    return redirect("catalogo")


def _read_json(request):
    try:
        data = json.loads(request.body)
    except (JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


@csrf_exempt
@require_POST
def api_token(request):
    data = _read_json(request)
    if data is None:
        return JsonResponse({"detail": "Se esperaba un objeto JSON válido."}, status=400)

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse(
            {"detail": "username y password son obligatorios."},
            status=400,
        )

    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return JsonResponse({"detail": "Credenciales incorrectas."}, status=401)

    token = create_access_token(user)
    response = JsonResponse(
        {
            "access": token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_SECONDS,
        }
    )
    return set_access_token_cookie(response, token)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_users(request):
    if request.method == "POST":
        data = _read_json(request)
        if data is None:
            return JsonResponse(
                {"detail": "Se esperaba un objeto JSON válido."},
                status=400,
            )
        form = RegistroForm(data)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
        user = form.save()
        token = create_access_token(user)
        response = JsonResponse(
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "access": token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_SECONDS,
            },
            status=201,
        )
        return set_access_token_cookie(response, token)

    user = get_token_user(request)
    if user is None:
        return JsonResponse({"detail": "Token inválido o ausente."}, status=401)
    if not user.is_staff:
        return JsonResponse({"detail": "Se requieren permisos de administrador."}, status=403)
    users = User.objects.order_by("username").values("id", "username", "email", "is_active")
    return JsonResponse({"users": list(users)})


@require_http_methods(["GET"])
def api_current_user(request):
    user = get_token_user(request)
    if user is None:
        return JsonResponse({"detail": "Token inválido o ausente."}, status=401)
    return JsonResponse(
        {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
        }
    )
