# t1_pyapif
# Cliente CLI para la API de aprendices

Este proyecto incluye una API FastAPI y un cliente de consola para consultar y
administrar aprendices.

## Requisitos

- Python instalado
- Dependencias del proyecto instaladas con `pip install -r requirements.txt`
- MongoDB configurado para el proyecto

## Iniciar la API

Desde la carpeta raíz del proyecto, abre una terminal y ejecuta:

```powershell
python -m uvicorn src.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. La documentación
interactiva está en `http://127.0.0.1:8000/docs`.

## Usar el CLI

Abre otra terminal en la carpeta raíz del proyecto. Para ver los comandos:

```powershell
python -m src.views.view --help
```

### Listar aprendices

```powershell
python -m src.views.view list
```

### Consultar un aprendiz

```powershell
python -m src.views.view get ID_DEL_APRENDIZ
```

### Crear un aprendiz

```powershell
python -m src.views.view create --document "123456" --first-name "Ana" --last-name "Lopez" --email "ana@example.com" --age 22 --program "Desarrollo de software" --record-number 1001
```

### Actualizar un aprendiz

Indica el ID y al menos un campo:

```powershell
python -m src.views.view update ID_DEL_APRENDIZ --program "Análisis de software"
```

También puedes actualizar varios campos a la vez:

```powershell
python -m src.views.view update ID_DEL_APRENDIZ --first-name "Ana Maria" --age 23
```

### Eliminar un aprendiz

```powershell
python -m src.views.view delete ID_DEL_APRENDIZ
```

## Configurar otra dirección de API

Por defecto, el cliente usa `http://127.0.0.1:8000`. Para usar otra dirección
en PowerShell, configura la variable antes de ejecutar el CLI:

```powershell
$env:API_BASE_URL = "http://localhost:8000"
```

La variable solo aplica a la sesión actual de esa terminal.

## Catálogo web de carros y motos

La app Django `catalogo` ofrece un inventario de vehículos guardado en SQLite,
independiente de la API FastAPI y su colección MongoDB. La interfaz usa
Bootstrap 5.3 para diseño adaptable e incluye filtros por tipo y marca,
publicación y edición de vehículos, además de registro e inicio de sesión con
JWT. Los datos de aprendices existentes se conservan.

En PowerShell, desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py makemigrations catalogo
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_vehicles
.\venv\Scripts\python.exe manage.py test catalogo
.\venv\Scripts\python.exe manage.py runserver
```

Abre `http://127.0.0.1:8000/` para explorar el inventario público. El comando
`seed_vehicles` agrega vehículos de demostración de Porsche, Ducati y Triumph
sin duplicarlos; puedes omitirlo si vas a cargar tus propios vehículos. Para
publicar, editar o eliminar inventario, crea una cuenta e inicia sesión. Las
imágenes de muestra y Bootstrap se cargan desde CDN y necesitan conexión a
internet.

### Endpoints JWT

- `POST /api/token/`: recibe `{"username": "...", "password": "..."}` y devuelve
  un token de acceso.
- `POST /api/usuarios/`: registra una cuenta y devuelve un token.
- `GET /api/usuarios/me/`: devuelve el usuario autenticado.
- `GET /api/usuarios/`: lista usuarios y requiere un token de un administrador.

Para llamadas API, envía el token con `Authorization: Bearer <token>`. Los
tokens duran 30 minutos. En desarrollo Django genera una clave secreta al
iniciar; define `DJANGO_SECRET_KEY` en el entorno si necesitas conservar tokens
entre reinicios. No uses `DEBUG=True` ni la clave de desarrollo en producción.
