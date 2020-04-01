from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request

class PatientRq(BaseModel):
	name: str
	surname: str

class PatientResp(BaseModel):
	id: int
	patient: dict


app = FastAPI()
patient_counter = 0

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def method(request: Request):
	return {"method": request.method}


@app.post("/patient", response_model=PatientResp)
def add_patient(patientRq: PatientRq):
	patient_counter += 1
	return PatientResp(id=patient_counter, patient=patientRq.dict())

