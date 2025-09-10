from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import bcrypt
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Datos de Supabase desde variables de entorno
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
    return {}

@app.post("/usuarios/")
def insertar_usuario(usuario: UsuarioIn):
    password_hash = bcrypt.hashpw(usuario.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
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
        return {"status": "error", "code": response.status_code, "details": response.text}

@app.get("/usuarios/")
def obtener_usuarios():
    url = f"{SUPABASE_URL}/rest/v1/usuarios?select=*"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {"status": "error", "code": response.status_code, "details": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8081)), reload=True)
