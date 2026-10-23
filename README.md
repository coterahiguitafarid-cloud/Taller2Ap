# TechGear

Proyecto híbrido: FastAPI administra el catálogo y los pedidos con MongoDB, y Django será el portal web.

## Estructura inicial

- `techgear_api/`: API FastAPI, conexión a MongoDB y esquemas Pydantic.
- `techgear_web/`: proyecto Django inicial.

## FastAPI

Desde PowerShell, entra a `techgear_api` e instala sus dependencias:

```powershell
cd techgear_api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea `techgear_api/.env` con la URI privada de MongoDB Atlas y el nombre de la base:

```dotenv
MONGODB_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>/
MONGODB_DATABASE=techgear
```

Inicia la API con `uvicorn main:app --reload --port 8000`. La documentación Swagger estará en `http://127.0.0.1:8000/docs`.

## Django

Desde la raíz del proyecto:

```powershell
cd techgear_web
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

El portal estará en `http://127.0.0.1:8001`. Instala cada `requirements.txt` en su entorno virtual correspondiente.