from typing import Optional                                                        
from pydantic import BaseModel, EmailStr 

class TraineeModel(BaseModel):
    document: str
    first_name: str    
    last_name: str
    email: EmailStr
    age: int
    program: str
    record_number:int

class TraineeUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    program: Optional[str] = None
    record_numbre: Optional[int] = None


