import secrets
from _sha256 import sha256

import uvicorn
from typing import Dict

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


class Patient(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: dict


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.counter: int = 0
app.storage: Dict[int, Patient] = {}
app.tokens = []

security = HTTPBasic()
app.secret_key = "3586551867030721809738080201689944348810193121742430128090228167"


def check_login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username + ":" + credentials.password


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.api_route(path="/welcome", methods=["GET"])
def welcome(request: Request, auth: str = Depends(check_login)):
    return templates.TemplateResponse("greeting.html", {"request": request, "user": auth.split(':', 1)[0]})


"""auth.split(':', 1)[0]"""


@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def method(request: Request):
    return {"method": request.method}


@app.post("/patient", response_model=PatientResp)
def add_patient(patient: Patient, auth: str = Depends(check_login)):
    resp = {"id": app.counter, "patient": patient}
    app.storage[app.counter] = patient
    app.counter += 1
    return resp


@app.get("/patient/{pk}")
async def get_patient(pk: int):
    if pk in app.storage:
        return app.storage.get(pk)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def check_login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username + ":" + credentials.password


@app.post("/login")
async def login(login_pass: str = Depends(check_login)):
    response = RedirectResponse(url='/welcome')
    secret_token = sha256(bytes(f"{login_pass.split(':', 1)[0]}{login_pass.split(':', 1)[1]}{app.secret_key}",
                                encoding='utf8')).hexdigest()
    app.tokens += secret_token
    response.set_cookie(key="session_token", value=secret_token)
    return response


@app.post("/logout")
def logout(auth: str = Depends(check_login)):
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response
