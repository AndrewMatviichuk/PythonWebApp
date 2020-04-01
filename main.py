from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def method(request: Request):
	return {"method": request.method}

