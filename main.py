from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json 

class Patients(BaseModel):

    id: Annotated[str, Field(... , description = 'ID of the Patient', example = 'P001')]
    name: Annotated[str, Field(..., description = 'name of the patient', example = 'yash')]
    city: Annotated[str, Field(..., description = 'name of the city where the patient lives')]
    age: Annotated[int, Field(..., gt=0, lt=120, description = 'age of the patient')] 
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description = 'gender of the patient ')]
    height: Annotated[float, Field(..., gt=0, description = 'height of the patient in meters')]
    weight: Annotated[float, Field(..., gt=0, description = 'weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight/(self.height**2)),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


class Patient_update(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default = None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with open('patients.json' ,'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data,f)

app = FastAPI()
@app.get("/")
def hello():
    return{"message":"Patients Management System"}

@app.get("/about")
def about():
    return{"message":"a fully functional Api to manage your patients records"}

@app.get('/view')
def view():
    data = load_data()
    return data    

@app.get('/patient/{patient_id}')
def view_pateints(patient_id: str = Path(..., description = 'id of the patient in the DB', example = 'P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code = 404, detail = 'Patient not found')

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description="Sort on the basis of height, weight and BMI"),
    order: str = Query('asc', description='sort in asc or desc order')
):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field, select from {valid_fields}"
        )

    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail="Invalid order, select asc or desc"
        )
    data = load_data()

    sort_order = True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patients):

    #load the existiting data from the database
    data = load_data()

    #check of the patient already exists 
    if patient.id in data:
        raise HTTPException(status_code = 400, detail  = 'Patlient ID already exists')

    #new patient add to the database , conversion of pydantic object to py dictionary 
    data[patient.id] = patient.model_dump(exclude=['id'])

    #save into the json file
    save_data(data)

    return JSONResponse(status_code = 201, content = {'message':'patient created sucessfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: Patient_update):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = 'patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset = True)   #exclude_unset bcz sari unwanted fields bhi hoti fir

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value 

    # existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patients_pydantic_object = Patients(**existing_patient_info)
    # -› pydantic object -› dict
    existing_patient_info = patients_pydantic_object.model_dump(exclude = {'id'})

    data[patient_id] = existing_patient_info

    #save data
    save_data(data)

    return JSONResponse(status_code = 200,  content = {'message': 'patient updated sucessfully'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    #load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = 'patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code = 200, content = {'message':'patient deleted'})