from _sha256 import sha256

import uvicorn
from typing import Dict

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException
from starlette.responses import RedirectResponse


class Patient(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: dict


app = FastAPI()
app.counter: int = 0
app.storage: Dict[int, Patient] = {}

security = HTTPBasic()
app.secret_key = "3586551867030721809738080201689944348810193121742430128090228167"



@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/welcome")
def welcome():
    return {"Welcome from London English British School, my friend!"}


@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def method(request: Request):
    return {"method": request.method}


@app.post("/patient", response_model=PatientResp)
def add_patient(patient: Patient):
    resp = {"id": app.counter, "patient": patient}
    app.storage[app.counter] = patient
    app.counter += 1
    return resp


@app.get("/patient/{pk}")
async def get_patient(pk: int):
    if pk in app.storage:
        return app.storage.get(pk)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/login")
async def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "trudnY" and credentials.password == "PaC13Nt":
        response = RedirectResponse(url='/welcome')
        session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}")).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        response.status_code=status.HTTP_307_TEMPORARY_REDIRECT
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
