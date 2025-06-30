import uvicorn
from fastapi import FastAPI, Response, Request
from controllers.firebase import register_user_firebase, login_user_firebase
from models.userregister import UserRegister
from models.userlogin import UserLogin

from utils.security import validate

app = FastAPI()

@app.get("/")
@validate
async def read_root(request: Request, response: Response):
    return {
        "version": "0.0.1"
        , "user": f"{request.state.firstname} {request.state.lastname} ( {request.state.email} ) "
    }

@app.post("/signup")
async def signup(user: UserRegister):
    result = await register_user_firebase(user)
    return result

@app.post("/login")
async def login(user: UserLogin):
    result = await login_user_firebase(user)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0", port=8000, log_level="info")