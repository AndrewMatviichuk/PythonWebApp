import secrets
import sqlite3
from _sha256 import sha256
import uvicorn

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Cookie
from starlette.responses import JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.counter: int = 0
app.templates = Jinja2Templates(directory="templates")
app.cookies = {}
app.security = HTTPBasic()
app.secret_key = "3586551867030721809738080201689944348810193121742430128090228167"
app.storage = {}
app.db_connection = None

class Patient(BaseModel):
    name: str
    surname: str
    id: str = 0


class PatientsResp(BaseModel):
    response: dict


def check_session(session_token: str = Cookie(None)):
    if session_token not in app.cookies:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )
    return session_token


def create_session(credentials: HTTPBasicCredentials = Depends(app.security)):
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


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/")
async def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.post("/login")
async def login(response: Response, new_session: str = Depends(create_session)):
    response.status_code = status.HTTP_302_FOUND
    response.set_cookie(key="session_token", value=new_session)
    response.headers["Location"] = "/welcome"


@app.post("/logout")
async def logout(response: Response, session: str = Depends(check_session)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    app.cookies.pop(session)


@app.get("/welcome")
async def welcome(request: Request, response: Response, session: str = Depends(check_session)):
        return app.templates.TemplateResponse("greeting.html", {"request": request, "user": app.cookies[session]})



@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])
async def method(request: Request):
    return {"method": request.method}


@app.post("/patient")
async def add_patient(response: Response, patient: Patient, session: str = Depends(check_session)):
    patient.id = "id_" + str(app.counter)
    app.storage[app.counter] = patient
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{app.counter}"
    app.counter += 1


@app.get("/patient")
async def get_patients(response: Response, session: str = Depends(check_session)):
    resp = {}
    for x in app.storage.values():
        resp[x.id] = {'name': x.name, 'surname': x.surname}
    if resp:
        return JSONResponse(resp)
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/patient/{pk}")
async def get_patient(pk: int, response: Response, session: str = Depends(check_session)):
    if pk in app.storage:
        return app.storage.get(pk)
    response.status_code = status.HTTP_204_NO_CONTENT


@app.delete("/patient/{pk}")
async def get_patient(pk: int, response: Response, session: str = Depends(check_session)):
    if pk in app.storage:
        app.storage.pop(pk, None)
        response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/tracks")
async def get_tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT * FROM tracks ORDER BY TrackId LIMIT ? OFFSET ?", (per_page, page*per_page,)).fetchall()
    return data


@app.get("/tracks/composers")
async def get_tracks(composer_name: str = ""):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name", (composer_name,)).fetchall()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found!"},
        )
    return data


@app.get("/tracks/composers")
async def get_tracks(composer_name: str = ""):
    app.db_connection.row_factory = lambda cursor, x: x[0]
    data = app.db_connection.execute(
        "SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name", (composer_name,)).fetchall()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found!"},
        )
    return data
