# 🛍️ TcnoCO

Tienda web para productos tecnológicos. FastAPI expone el catálogo y los
pedidos; el portal Django permite explorar productos, administrar el inventario
y realizar compras. Los datos del catálogo se almacenan en MongoDB.

## 🧰 Tecnologías

| Componente | Tecnología |
|---|---|
| API | Python, FastAPI, Pydantic |
| Persistencia de la API | MongoDB con Motor/PyMongo |
| Portal web | Django, plantillas HTML y CSS propio adaptable |
| Comunicación web/API | HTTP con Requests y token Bearer entre servicios |
| Base de datos local del portal | SQLite |
| Pruebas | `unittest` y Django TestCase |
| Despliegue de la API | Vercel y Render |

## 📁 Estructura del proyecto

```text
techgear_api/
  auth.py                 Autenticación del portal a la API
  database.py             Configuración y conexión a MongoDB
  main.py                 Aplicación FastAPI y health check
  models.py               Esquemas y validaciones
  routers/                Endpoints de productos y pedidos
techgear_web/
  store/
    forms.py              Formularios de usuario, carrito y productos
    models.py             Perfil local del cliente
    services.py           Cliente HTTP de FastAPI
    views.py              Flujo de tienda, pedidos y administración
    templates/store/      Páginas HTML
    static/store/images/  Icono SVG de TcnoCO
  techgear_web/           Configuración del proyecto Django
src/                      Cliente CLI del proyecto original
catalogo/                 Catálogo de vehículos del proyecto original
test/                     Pruebas de FastAPI
render.yaml               Configuración de despliegue de la API
pyproject.toml             Punto de entrada FastAPI para Vercel
requirements.txt           Dependencias Python detectadas por Vercel
```

## 🚀 Instalación y ejecución local

Requiere Python y una instancia de MongoDB. Abre dos terminales desde la raíz
del repositorio.

### 1. Configurar y ejecutar FastAPI

```powershell
python -m venv .venv-api
.\.venv-api\Scripts\Activate.ps1
pip install -r techgear_api\requirements.txt
```

En la raíz crea un archivo `.env` con la URI de MongoDB y un token privado. No
subas este archivo ni compartas sus credenciales:

```dotenv
MONGODB_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>/
MONGODB_DATABASE=techgear
TECHGEAR_API_TOKEN=<token-privado>
```

Activa el entorno y arranca la API:

```powershell
uvicorn techgear_api.main:app --reload --port 8000
```

La documentación interactiva estará en `http://127.0.0.1:8000/docs` y el health
check en `http://127.0.0.1:8000/health`.

### Desplegar la API en Vercel

Configura el directorio raíz del proyecto en Vercel como la raíz del repositorio.
El punto de entrada de FastAPI está declarado en `pyproject.toml` y sus
dependencias se instalan desde `requirements.txt`. En la configuración de
entorno de Vercel agrega `MONGODB_URI`, `MONGODB_DATABASE` (por ejemplo,
`techgear`) y `TECHGEAR_API_TOKEN`. No guardes estos valores en el repositorio.

### 2. Configurar y ejecutar Django

En la segunda terminal:

```powershell
python -m venv .venv-web
.\.venv-web\Scripts\Activate.ps1
pip install -r techgear_web\requirements.txt
python techgear_web\manage.py migrate
$env:TECHGEAR_API_TOKEN = "<el-mismo-token-privado>"
python techgear_web\manage.py runserver 8001
```

Abre `http://127.0.0.1:8001/`. Si no activas un entorno separado, usa el Python
del entorno virtual correspondiente para instalar dependencias y ejecutar los
comandos.

## 🛍️ Flujo de uso

1. Inicia FastAPI y Django con el mismo `TECHGEAR_API_TOKEN`.
2. Desde la tienda, registra una cuenta de cliente o inicia sesión.
3. El catálogo consulta los productos de FastAPI; se puede filtrar por
   categoría y agregar productos disponibles al carrito. Cada producto puede
   tener una URL opcional de imagen, que se agrega o cambia desde el formulario
   de administración. Para cargar imágenes de demostración en los cinco
   productos predefinidos (o completar las imágenes faltantes sin reemplazar
   las personalizadas), ejecuta `python techgear_web\manage.py seed_products`
   con ambas aplicaciones activas y `TECHGEAR_API_TOKEN` configurado en Django.
   Las imágenes de demostración se sirven desde Unsplash y requieren conexión
   a internet; puedes reemplazarlas usando cualquier URL directa HTTPS.
4. El cliente autenticado confirma el pedido. La API valida y descuenta el
   inventario de forma transaccional; el historial muestra solo sus pedidos.
5. Para administrar productos, crea una cuenta administradora con
   `python techgear_web\manage.py createsuperuser`, inicia sesión y abre
   `/administracion/productos/`.

### ⚠️ Manejo de errores

- Si FastAPI no responde, la tienda muestra un aviso y no presenta inventario
  ficticio.
- Los productos con stock cero aparecen como agotados y no se pueden agregar.
- La API vuelve a validar el stock al confirmar el pedido. Si se agotó mientras
  el producto estaba en el carrito, muestra el error y conserva el carrito.
- Los errores de autenticación o de respuesta de la API se muestran al usuario
  sin ocultar el fallo.

## 🔌 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/products` | Listar productos |
| `POST` | `/api/products` | Crear producto (token requerido) |
| `GET` | `/api/products/{product_id}` | Consultar producto |
| `PUT` | `/api/products/{product_id}` | Actualizar producto (token requerido) |
| `DELETE` | `/api/products/{product_id}` | Eliminar producto (token requerido) |
| `POST` | `/api/orders` | Crear pedido (token requerido, valida stock) |
| `GET` | `/api/orders` | Listar pedidos (token requerido) |
| `GET` | `/api/orders/{order_id}` | Consultar pedido (token requerido) |

## ✅ Pruebas

Desde la raíz del repositorio:

```powershell
.\.venv-web\Scripts\python.exe techgear_web\manage.py check
.\.venv-web\Scripts\python.exe techgear_web\manage.py test store
.\.venv-api\Scripts\python.exe -m unittest test.test_api_auth -v
.\.venv-api\Scripts\python.exe -m unittest test.test_api_products -v
```

## ☁️ Despliegue

`render.yaml` prepara el portal Django, la API FastAPI y PostgreSQL en Render.
Al crear el Blueprint, configura `MONGODB_URI` y `TECHGEAR_API_TOKEN` como
variables secretas para la API; el portal obtiene el token de ese servicio.
Render genera `DJANGO_SECRET_KEY` y conecta PostgreSQL. Revisa y confirma el
costo y la disponibilidad de los planes elegidos en tu cuenta antes de crear
los recursos.

- 🌐 **Portal Django:** `https://technoco-web.onrender.com/` después del
  despliegue.
- ⚡ **API FastAPI:** `https://techgear-api.onrender.com/docs` después del
  despliegue; health check en `/health`.
- 🖥️ **Vista local:** [http://127.0.0.1:8001/](http://127.0.0.1:8001/).
- 🧪 **API local:** [documentación](http://127.0.0.1:8000/docs).
- 🐙 **Repositorio:** [Taller2Ap en GitHub](https://github.com/coterahiguitafarid-cloud/Taller2Ap).

Después del primer despliegue, crea la cuenta administradora dentro del
servicio web de Render:

```bash
cd techgear_web
python manage.py createsuperuser
```

El primer arranque migra PostgreSQL automáticamente. Los archivos estáticos se
recopilan durante la compilación y se sirven mediante WhiteNoise.

## 👤 Autoría

- **Autor:** `coterahiguitafarid-cloud`

## 🧩 Proyecto original

`src/` contiene el cliente CLI de aprendices. `catalogo/` es una aplicación
Django independiente para el inventario de vehículos en SQLite. Se administra
desde la raíz con `python manage.py` y sus dependencias están en
`requirements.txt`.
