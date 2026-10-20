from bson import ObjectId
from src.models.database import collection
from src models.model import TraineeModel, TraineeUpdateModel

def helper_trainee(trianee) -> dict:
    return()
    "id":str(trainee["_id"]),
    "document":trainee["document"],
    "name":trainee["name"],
    "lastname":trainee["lastname"],
    "email":trainee["email"],
    "age":trainee["age"],
    "program":trainee["program"],
    "record_number":trainee["record_number"],
    