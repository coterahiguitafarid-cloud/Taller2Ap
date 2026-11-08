# TechGear

Proyecto de tienda en línea: FastAPI administra productos y pedidos en MongoDB,
y Django ofrece el portal web.

## Componentes

- `techgear_api/`: API FastAPI para productos y pedidos.
- `techgear_web/`: portal Django con catálogo, carrito, cuentas y administración.
- `src/` y `catalogo/`: API CLI y catálogo de vehículos del proyecto original.

## Ejecutar la API

Desde la raíz, crea un entorno e instala las dependencias:

```powershell
python -m venv .venv-api
.\.venv-api\Scripts\Activate.ps1
pip install -r techgear_api\requirements.txt
```

Configura MongoDB en un archivo `.env` en la raíz (no lo subas a Git):

```dotenv
MONGODB_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>/
MONGODB_DATABASE=techgear
TECHGEAR_API_TOKEN=<token-privado>
```

Inicia la API desde la raíz:

```powershell
uvicorn techgear_api.main:app --reload --port 8000
```

La documentación de la API está en `http://127.0.0.1:8000/docs`.

## Ejecutar el portal web

En otra terminal, desde la raíz, crea un entorno independiente:

```powershell
python -m venv .venv-web
.\.venv-web\Scripts\Activate.ps1
pip install -r techgear_web\requirements.txt
python techgear_web\manage.py migrate
python techgear_web\manage.py runserver 8001
```

Abre `http://127.0.0.1:8001/`. El catálogo obtiene el inventario de FastAPI;
inicia primero la API para ver productos. El portal también puede abrirse sin
la API, aunque mostrará un aviso de conexión y no inventará productos de muestra.
Las acciones administrativas requieren que `TECHGEAR_API_TOKEN` coincida en
ambos servicios.

## Despliegue de la API

`render.yaml` configura el servicio FastAPI y la comprobación `/health`. En
Render, configura `MONGODB_URI` y `TECHGEAR_API_TOKEN` como variables secretas.
`MONGODB_DATABASE` usa `techgear` de forma predeterminada.

## Proyecto original

El código de `src/` contiene el cliente CLI para la API de aprendices. La app
Django `catalogo` mantiene por separado el catálogo de vehículos en SQLite.
Sus comandos de administración y pruebas se ejecutan desde la raíz:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_vehicles
python manage.py test catalogo
python manage.py runserver
```
