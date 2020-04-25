import secrets
from _sha256 import sha256

import uvicorn
from typing import Dict

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Cookie
from starlette.responses import JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.counter: int = 0
templates = Jinja2Templates(directory="templates")
app.cookies = {}
security = HTTPBasic()
app.secret_key = "3586551867030721809738080201689944348810193121742430128090228167"
app.storage = {}


class Patient(BaseModel):
    name: str
    surname: str
    id: str = 0


class PatientsResp(BaseModel):
    response: dict


def check_session(session_token: str = Cookie(None)):
    if session_token not in app.cookies:
        session_token = None
    return session_token


def create_session(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    secret_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}",
                                encoding='utf8')).hexdigest()
    app.cookies[secret_token] = credentials.username
    return secret_token


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.post("/login")
async def login(response: Response, new_session: str = Depends(create_session)):
    response.status_code = status.HTTP_302_FOUND
    response.set_cookie(key="session_token", value=new_session)
    response.headers["Location"] = "/welcome"


@app.post("/logout")
def logout(response: Response, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    app.cookies.pop(session)


@app.get("/welcome")
def welcome(request: Request, response: Response, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    return templates.TemplateResponse("greeting.html", {"request": request, "user": app.cookies[session]})



@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
def method(request: Request):
    return {"method": request.method}


@app.post("/patient")
async def add_patient(response: Response, patient: Patient, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    patient.id = "id_" + str(app.counter)
    app.storage[app.counter] = patient
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{app.counter}"
    app.counter += 1


@app.get("/patient")
def get_patients(response: Response, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    resp = {}
    for x in app.storage.values():
        resp[x.id] = {'name': x.name, 'surname': x.surname}
    if resp:
        return JSONResponse(resp)
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/patient/{pk}")
def get_patient(pk: int, response: Response, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    if pk in app.storage:
        return app.storage.get(pk)
    response.status_code = status.HTTP_204_NO_CONTENT


@app.delete("/patient/{pk}")
def get_patient(pk: int, response: Response, session: str = Depends(check_session)):
    if session is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "UNAUTHORIZED"
    if pk in app.storage:
        app.storage.pop(pk, None)
        response.status_code = status.HTTP_204_NO_CONTENT
