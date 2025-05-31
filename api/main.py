# api/main.py
from fastapi import FastAPI, Request

app = FastAPI(title="FastAPI on Vercel")

# GET with query parameters
@app.get("/hello")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}

# POST with JSON body
@app.post("/echo", status_code=201)
async def echo(payload: Request):
    data = await payload.json()
    return {"received": data}
