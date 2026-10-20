from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Agregar la URI de conexión a tu base de datos MongoDB
MONGO_URI = "mongodb+srv://cacjx84_db_user:5RURwjlWinSkv3gT@cluster0.vafpbez.mongodb.net/?appName=Cluster0"

# Crear una instancia del cliente de MongoDB y asignar un tiempo de espera para la selección del servidor
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

# Crear la base de datos y la colección
db = client.dataap
collection = db.trainee

try:
    # Intentar obtener información del servidor para verificar la conexión
    client.server_info()
    client.admin.command("ping")
    print("Conexión exitosa a MongoDB")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Error al conectar a MongoDB: {e}")
# finally:
#     # Cerrar la conexión al cliente de MongoDB
#     client.close()