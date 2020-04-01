import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.requests import Request
from fastapi.responses import JSONResponse



class PatientRq(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: dict


app = FastAPI()
patients = dict()


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
    d = {len(patients): patientRq.dict()}
    patients.update(d)
    return PatientResp(id=len(patients) - 1, patient=patientRq.dict())


@app.get("/patient/{pk}")
async def get_patient(pk: int):
    if len(patients) - 1 >= pk:
        return patients.get(pk)
    else:
        return JSONResponse(status_code=204, content={"message": "Patient not exists"})
