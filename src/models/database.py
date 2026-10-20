from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Agregamos la conexion a la base de datos mongo db
MONGO_URI = "mongodb+srv://balyifarid_db_user:0pwFY9ZCa8YFICrk@cluster0.vycjgtv.mongodb.net/?appName=Cluster0" 

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)


db = client.datape
collection = db.trainee


try:
    client.server_info()
    client.admin.command('ping')
    print("Conexión exitosa a MongoDB")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Error al conectar a MongoDB: {e}")
    
finally:
    client.close()  