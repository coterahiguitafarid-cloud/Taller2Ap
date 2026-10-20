from bson import ObjectId
from src.models.database import collection
from src.models.model import TraineeModel, TraineeUpdateModel

def helper_trainee(trainee) -> dict:
    return {
        "id": str(trainee["_id"]),
        "document": str(trainee["document"]),
        "firstname": trainee["firstname"],
        "lastname": trainee["lastname"],
        "email": trainee["email"],
        "age": trainee["age"],
        "program": trainee["program"],
        "record_number": trainee["record_number"]
    }
    
# Crear datos de un Aprendiz
def create_trainee(trainee: TraineeModel):
    trainee_dict = trainee.model_dump()
    result = collection.insert_one(trainee_dict)
    new_trainee = collection.find_one({"_id": result.inserted_id})
    return helper_trainee(new_trainee)

# Obtener todos los aprendices
def get_all_trainees():
    trainees = []
    for trainee in collection.find():
        trainees.append(helper_trainee(trainee))
    return trainees

# Obtener datos del aprendiz por ID
def get_trainee_by_id(id: str):
    trainee = collection.find_one({"_id": ObjectId(id)})
    if trainee:
        return helper_trainee(trainee)
    return None

# Actualizar datos del aprendiz
def update_trainee(id: str, data: TraineeUpdateModel):
    data_update = {
        k: v for k, v in data.model_dump().items() if v is not None 
    }
    if data_update:
        collection.update_one({"_id": ObjectId(id)}, {"$set": data_update})
        trainee_updated = collection.find_one({"_id": ObjectId(id)})
        return helper_trainee(trainee_updated)
    return None

# Eliminar datos del aprendiz
def delete_trainee(id: str):
    trainee = collection.find_one({"_id": ObjectId(id)})
    if trainee:
        collection.delete_one({"_id": ObjectId(id)})
        return True
    return False