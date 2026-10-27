# TechGear

Proyecto híbrido: FastAPI administra el catálogo y los pedidos con MongoDB, y Django será el portal web.

## Estructura inicial

- `techgear_api/`: API FastAPI, conexión a MongoDB y esquemas Pydantic.
- `techgear_web/`: proyecto Django inicial.
- `render.yaml`: configuración de despliegue de la API en Render.

## FastAPI

Desde la raíz del repositorio, crea un entorno virtual e instala las dependencias de la API:

```powershell
python -m venv .venv-api
.\.venv-api\Scripts\Activate.ps1
pip install -r techgear_api\requirements.txt
```

Crea o actualiza el archivo `.env` en la raíz del repositorio con la URI privada de MongoDB Atlas. No subas este archivo a Git:

```dotenv
MONGODB_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>/
MONGODB_DATABASE=techgear
```

Inicia la API desde la raíz:

```powershell
uvicorn techgear_api.main:app --reload --port 8000
```

Swagger estará en `http://127.0.0.1:8000/docs`. Endpoints disponibles:

| Método | Ruta | Función |
|---|---|---|
| `POST` | `/api/products` | Crear producto |
| `GET` | `/api/products` | Listar productos |
| `GET` | `/api/products/{product_id}` | Consultar producto |
| `PUT` | `/api/products/{product_id}` | Reemplazar datos del producto |
| `DELETE` | `/api/products/{product_id}` | Eliminar producto |
| `POST` | `/api/orders` | Crear pedido y descontar existencias |
| `GET` | `/api/orders` | Listar pedidos |
| `GET` | `/api/orders/{order_id}` | Consultar pedido |

Para probar pedidos en Swagger, primero crea un producto y copia su `id`. Usa ese mismo ID como `product_id` y un ID de 24 caracteres hexadecimales para `customer_id`. La API valida la existencia y el stock de cada producto. Los esquemas Pydantic de usuarios están definidos, pero los endpoints y la autenticación de usuarios quedan para una etapa posterior.

## Despliegue de la API en Render

El archivo `render.yaml` configura el servicio web, el comando de arranque y la comprobación `/health`. En Render, conecta el repositorio y configura la variable secreta `MONGODB_URI` con la URI de Atlas. `MONGODB_DATABASE` ya tiene el valor predeterminado `techgear`. No pegues credenciales en el repositorio.

## Django

Usa otro entorno virtual para el portal Django. Desde la raíz del repositorio:

```powershell
python -m venv .venv-web
.\.venv-web\Scripts\Activate.ps1
pip install -r techgear_web\requirements.txt
python techgear_web\manage.py migrate
python techgear_web\manage.py runserver 8001
```

El portal estará en `http://127.0.0.1:8001`. Instala las dependencias de cada proyecto en su propio entorno virtual; no reutilices uno para ambos.