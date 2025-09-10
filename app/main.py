from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import bcrypt
import requests
import os
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno desde .env (solo en local)
load_dotenv()

app = FastAPI()

# 🔹 Datos de Supabase desde variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation"
}

class UsuarioIn(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol: str = "CLIENTE"  # Por defecto CLIENTE

@app.get("/favicon.ico")
def favicon():
    # Evita el error 404 del navegador cuando busca el ícono
    return {}

@app.post("/usuarios/")
def insertar_usuario(usuario: UsuarioIn):
    """
    Inserta un nuevo usuario en la base de datos Supabase.
    Si el correo ya existe, devuelve un mensaje controlado.
    """
    # Hash de la contraseña
    password_hash = bcrypt.hashpw(
        usuario.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    data = {
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "password_hash": password_hash,
        "rol": usuario.rol
    }

    url = f"{SUPABASE_URL}/rest/v1/usuarios"
    response = requests.post(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        return {"status": "success", "data": response.json()}
    elif response.status_code == 409:
        return {"status": "error", "message": "Usuario ya existe"}
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "details": response.text
        }

@app.get("/usuarios/")
def obtener_usuarios():
    """
    Obtiene la lista completa de usuarios.
    """
    url = f"{SUPABASE_URL}/rest/v1/usuarios?select=*"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "details": response.text
        }
