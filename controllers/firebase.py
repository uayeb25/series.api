import os
import json
import logging
import firebase_admin
import requests

from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from dotenv import load_dotenv


from utils.database import execute_query_json
from utils.security import create_jwt_token
from models.userregister import UserRegister
from models.userlogin import UserLogin

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la app de Firebase Admin
cred = credentials.Certificate("secrets/firebase-secret.json")
firebase_admin.initialize_app(cred)

load_dotenv()

async def register_user_firebase(user: UserRegister) -> dict:
    user_record = {}
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )

    query = f" exec series.users_insert ?, ?, ?, ? "
    params = (
        user_record.email,
        user.first_name,
        user.last_name,
        user.active
    )
    try:
        result_json = await execute_query_json(query, params, needs_commit=True)
        return json.loads(result_json)
    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        raise HTTPException(status_code=500, detail=str(e))


async def login_user_firebase(user: UserLogin):
    # Autenticar usuario con Firebase Authentication usando la API REST
    api_key = os.getenv("FIREBASE_API_KEY")  # Reemplaza esto con tu apiKey de Firebase
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail=f"Error al autenticar usuario: {response_data['error']['message']}"
        )

    query = f"""select
                    email
                    , firstname
                    , lastname
                    , active
                from [series].[users]
                where email = ?
                """

    try:
        result_json = await execute_query_json(query, (user.email,), needs_commit=False)
        result_dict = json.loads(result_json)
        return {
            "message": "Usuario autenticado exitosamente",
            "idToken": create_jwt_token(
                result_dict[0]["firstname"],
                result_dict[0]["lastname"],
                user.email,
                result_dict[0]["active"]
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))