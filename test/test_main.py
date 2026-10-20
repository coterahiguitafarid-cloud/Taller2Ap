from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Agregamos la conexion a la base de datos mongo db
MONGO_URI = "mongodb+srv://balyifarid_db_user:0pwFY9ZCa8YFICrk@cluster0.vycjgtv.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

# Crar la base de datos y la coleccion
db = client.amb703
collection = db.Mesa

# Crear la base de datos y la coleccion
nueva_Mesa = {
    "name": "Alma marcela Gozo",
    "status": "Alive",
    "species": "Human",
    "gender": "Male"
}

collection.insert_one(nueva_Mesa) 
print("Mesa agregada exitosamente")


try:
    client.server_info()
    client.admin.command('ping')
    print("Conexión exitosa a MongoDB")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Error al conectar a MongoDB: {e}")
    
finally:
    client.close()  