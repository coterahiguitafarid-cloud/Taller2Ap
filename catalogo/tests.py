import json

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .authentication import create_access_token
from .models import Aprendiz, Vehiculo


class VehiculoCatalogoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="motorhaus",
            email="admin@example.com",
            password="ClaveSegura2026!",
        )
        self.carro = Vehiculo.objects.create(
            tipo=Vehiculo.Tipo.CARRO,
            marca="Porsche",
            modelo="911 Carrera",
            anio=2024,
            precio=750000000,
            kilometraje=5000,
            descripcion="Deportivo de alto rendimiento.",
            correo_contacto="ventas@example.com",
            destacado=True,
        )
        self.moto = Vehiculo.objects.create(
            tipo=Vehiculo.Tipo.MOTO,
            marca="Ducati",
            modelo="Monster",
            anio=2023,
            precio=75000000,
            kilometraje=1200,
            cilindraje=937,
            descripcion="Motocicleta naked para carretera.",
            correo_contacto="motos@example.com",
        )

    def test_inventario_es_publico_y_muestra_carros_y_motos(self):
        response = self.client.get(reverse("catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Porsche 911 Carrera")
        self.assertContains(response, "Ducati Monster")
        self.assertEqual(response.context["total_carros"], 1)
        self.assertEqual(response.context["total_motos"], 1)

    def test_inventario_filtra_por_busqueda_tipo_y_marca(self):
        response = self.client.get(
            reverse("catalogo"),
            {"q": "Monster", "tipo": "moto", "marca": "Ducati"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtered_count"], 1)
        self.assertContains(response, "Ducati Monster")
        self.assertNotContains(response, "Porsche 911 Carrera")

    def test_comando_de_demo_es_idempotente(self):
        call_command("seed_vehicles", verbosity=0)
        count_after_first_run = Vehiculo.objects.count()
        call_command("seed_vehicles", verbosity=0)

        self.assertGreater(count_after_first_run, 2)
        self.assertEqual(Vehiculo.objects.count(), count_after_first_run)

    def test_publicar_vehiculo_requiere_token(self):
        response = self.client.get(reverse("vehiculo_create"))

        self.assertRedirects(response, reverse("login"))

    def test_usuario_autenticado_puede_publicar_vehiculo(self):
        self.client.cookies["access_token"] = create_access_token(self.user)
        response = self.client.post(
            reverse("vehiculo_create"),
            {
                "tipo": "moto",
                "marca": "Triumph",
                "modelo": "Bonneville T120",
                "anio": 2022,
                "precio": 65000000,
                "kilometraje": 3500,
                "cilindraje": 1200,
                "descripcion": "Clásica moderna para disfrutar la ruta.",
                "imagen_url": "",
                "correo_contacto": "ventas@example.com",
            },
        )

        self.assertRedirects(response, reverse("catalogo"))
        self.assertTrue(
            Vehiculo.objects.filter(marca="Triumph", modelo="Bonneville T120").exists()
        )

    def test_registros_de_aprendices_se_conservan(self):
        aprendiz = Aprendiz.objects.create(
            document="12345",
            first_name="Ana",
            last_name="Lopez",
            email="ana@example.com",
            age=22,
            program="Desarrollo de software",
            record_number=1001,
        )

        self.assertTrue(Aprendiz.objects.filter(pk=aprendiz.pk).exists())

    def test_login_emite_cookie_jwt(self):
        response = self.client.post(
            reverse("login"),
            {"username": "motorhaus", "password": "ClaveSegura2026!"},
        )

        self.assertRedirects(response, reverse("catalogo"))
        self.assertTrue(response.cookies["access_token"]["httponly"])

    def test_login_incorrecto_no_emite_token(self):
        response = self.client.post(
            reverse("login"),
            {"username": "motorhaus", "password": "incorrecta"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access_token", response.cookies)

    def test_logout_elimina_cookie_jwt(self):
        self.client.cookies["access_token"] = create_access_token(self.user)
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)

    def test_api_token_y_perfil_aceptan_bearer(self):
        response = self.client.post(
            reverse("api_token"),
            data=json.dumps(
                {"username": "motorhaus", "password": "ClaveSegura2026!"}
            ),
            content_type="application/json",
        )
        token = response.json()["access"]
        profile_response = self.client.get(
            reverse("api_current_user"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.json()["username"], "motorhaus")

    def test_endpoint_de_usuarios_requiere_staff_para_listar(self):
        token = create_access_token(self.user)
        response = self.client.get(
            reverse("api_users"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_administrador_puede_listar_usuarios(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        token = create_access_token(self.user)
        response = self.client.get(
            reverse("api_users"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["users"][0]["username"], "motorhaus")

    def test_token_invalido_no_accede_al_perfil(self):
        response = self.client.get(
            reverse("api_current_user"),
            HTTP_AUTHORIZATION="Bearer token-invalido",
        )

        self.assertEqual(response.status_code, 401)

    def test_registro_api_crea_usuario_y_token(self):
        response = self.client.post(
            reverse("api_users"),
            data=json.dumps(
                {
                    "username": "nuevo_usuario",
                    "email": "nuevo@example.com",
                    "password1": "UnaClaveSegura2026!",
                    "password2": "UnaClaveSegura2026!",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())
        self.assertIn("access", response.json())
