"""
ESTETICAI - Aplicacion Web v1.0
================================
Backend con FastAPI + SQLite + Auth
Ejecutar: uvicorn web.app:app --reload --port 8000
"""

import os
import sys
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_engine import generar_contenido_semanal, generar_copy_individual
from agents.image_engine import generar_imagen_automatica, generar_prompt_automatico, ESTILOS_PUBLICACION
from agents.video_engine import generar_video_desde_imagen, MOVIMIENTOS_VIDEO, MOVIMIENTO_RECOMENDADO

import sqlite3

# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).parent
# En produccion, usar /tmp para la DB (filesystem escribible en Railway)
if os.environ.get("RAILWAY_ENVIRONMENT"):
    DB_PATH = Path("/tmp/esteticai.db")
else:
    DB_PATH = BASE_DIR / "esteticai.db"
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app = FastAPI(title="Esteticai", version="1.0")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Health check para verificar que la app arranca
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0"}


# ============================================================
# BASE DE DATOS
# ============================================================

def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            creado_en TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS perfiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre_negocio TEXT NOT NULL,
            propietaria TEXT,
            ciudad TEXT,
            tipo_negocio TEXT DEFAULT 'Centro de estetica',
            servicios TEXT DEFAULT '[]',
            productos TEXT DEFAULT '[]',
            tono TEXT DEFAULT 'cercano',
            instagram_handle TEXT DEFAULT '',
            creado_en TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS generaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            perfil_id INTEGER,
            tipo TEXT NOT NULL,
            contenido TEXT,
            imagen_url TEXT,
            video_url TEXT,
            metadata TEXT DEFAULT '{}',
            creado_en TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)
    db.commit()
    db.close()


init_db()


# ============================================================
# AUTENTICACION
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_usuario_actual(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user


def requiere_login(request: Request):
    user = get_usuario_actual(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def get_perfil_activo(user_id):
    db = get_db()
    perfil = db.execute(
        "SELECT * FROM perfiles WHERE usuario_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    db.close()
    if perfil:
        return {
            "id": perfil["id"],
            "nombre_negocio": perfil["nombre_negocio"],
            "propietaria": perfil["propietaria"] or "",
            "ciudad": perfil["ciudad"] or "",
            "tipo_negocio": perfil["tipo_negocio"],
            "servicios": json.loads(perfil["servicios"]),
            "productos": json.loads(perfil["productos"]),
            "tono": perfil["tono"],
            "instagram_handle": perfil["instagram_handle"],
        }
    return None


def guardar_generacion(user_id, perfil_id, tipo, contenido=None,
                        imagen_url=None, video_url=None, metadata=None):
    db = get_db()
    db.execute(
        "INSERT INTO generaciones (usuario_id, perfil_id, tipo, contenido, imagen_url, video_url, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, perfil_id, tipo, contenido, imagen_url, video_url, json.dumps(metadata or {}))
    )
    db.commit()
    db.close()


# ============================================================
# PAGINAS PUBLICAS
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_usuario_actual(request)
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("home.html", context={"request": request}, request=request)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request, "error": None}, request=request)


@app.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    db.close()
    if not user or user["password_hash"] != hash_password(password):
        return templates.TemplateResponse("login.html", context={
            "request": request, "error": "Email o contrasena incorrectos"
        }, request=request)
    request.session["user_id"] = user["id"]
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request):
    return templates.TemplateResponse("registro.html", context={"request": request, "error": None}, request=request)


@app.post("/registro")
async def registro_submit(request: Request, nombre: str = Form(...),
                           email: str = Form(...), password: str = Form(...)):
    db = get_db()
    existe = db.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    if existe:
        db.close()
        return templates.TemplateResponse("registro.html", context={
            "request": request, "error": "Este email ya esta registrado"
        }, request=request)
    db.execute(
        "INSERT INTO usuarios (email, password_hash, nombre) VALUES (?, ?, ?)",
        (email, hash_password(password), nombre)
    )
    db.commit()
    user = db.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    db.close()
    request.session["user_id"] = user["id"]
    return RedirectResponse("/perfil/crear", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return RedirectResponse("/perfil/crear", status_code=303)

    db = get_db()
    generaciones = db.execute(
        "SELECT * FROM generaciones WHERE usuario_id = ? ORDER BY creado_en DESC LIMIT 20",
        (user["id"],)
    ).fetchall()
    db.close()

    return templates.TemplateResponse("dashboard.html", context={
        "request": request,
        "user": user,
        "perfil": perfil,
        "generaciones": generaciones,
    }, request=request)


# ============================================================
# PERFIL DE MARCA
# ============================================================

@app.get("/perfil/crear", response_class=HTMLResponse)
async def perfil_crear_page(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("perfil_crear.html", context={"request": request, "user": user}, request=request)


@app.post("/perfil/crear")
async def perfil_crear_submit(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    form = await request.form()
    servicios = [s.strip() for s in form.get("servicios", "").split("\n") if s.strip()]
    productos = [p.strip() for p in form.get("productos", "").split("\n") if p.strip()]
    db = get_db()
    db.execute(
        """INSERT INTO perfiles (usuario_id, nombre_negocio, propietaria, ciudad,
           tipo_negocio, servicios, productos, tono, instagram_handle)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user["id"], form.get("nombre_negocio", ""), form.get("propietaria", ""),
         form.get("ciudad", ""), form.get("tipo_negocio", "Centro de estetica"),
         json.dumps(servicios), json.dumps(productos),
         form.get("tono", "cercano"), form.get("instagram_handle", ""))
    )
    db.commit()
    db.close()
    return RedirectResponse("/dashboard", status_code=303)


# ============================================================
# API - GENERACION DE CONTENIDO
# ============================================================

@app.post("/api/generar/copy")
async def api_generar_copy(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    data = await request.json()
    tipo = data.get("tipo", "EDUCATIVO")
    servicio = data.get("servicio", perfil["servicios"][0] if perfil["servicios"] else "Tratamiento facial")
    descripcion = data.get("descripcion", None)

    try:
        copy = generar_copy_individual(
            perfil=perfil,
            tipo_contenido=tipo,
            servicio_o_producto=servicio,
            descripcion_foto=descripcion,
        )
        guardar_generacion(user["id"], perfil["id"], "copy",
                          contenido=json.dumps(copy, ensure_ascii=False))
        return JSONResponse({"ok": True, "copy": copy})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/generar/imagen")
async def api_generar_imagen(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    data = await request.json()
    servicio = data.get("servicio", "Tratamiento facial")
    tipo_pub = data.get("tipo_publicacion", "post_feed")
    modo = data.get("modo", "servicio")

    try:
        resultado = generar_imagen_automatica(
            servicio=servicio,
            tipo_publicacion=tipo_pub,
            perfil=perfil,
            modo=modo,
        )
        if "error" not in resultado:
            guardar_generacion(user["id"], perfil["id"], "imagen",
                              imagen_url=resultado.get("url"),
                              metadata={"servicio": servicio, "tipo": tipo_pub})
        return JSONResponse({"ok": True, "imagen": resultado})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/generar/video")
async def api_generar_video(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)

    data = await request.json()
    url_imagen = data.get("url_imagen", "")
    tipo_movimiento = data.get("tipo_movimiento", "zoom_suave")
    duracion = data.get("duracion", 5)

    if not url_imagen.startswith("http"):
        return JSONResponse({"error": "URL de imagen no valida"}, status_code=400)

    try:
        resultado = generar_video_desde_imagen(
            url_imagen=url_imagen,
            tipo_movimiento=tipo_movimiento,
            duracion=duracion,
        )
        perfil = get_perfil_activo(user["id"])
        if "error" not in resultado:
            guardar_generacion(user["id"], perfil["id"] if perfil else None, "video",
                              imagen_url=url_imagen,
                              video_url=resultado.get("url"),
                              metadata={"movimiento": tipo_movimiento, "duracion": duracion})
        return JSONResponse({"ok": True, "video": resultado})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/generar/calendario")
async def api_generar_calendario(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    data = await request.json()
    contexto = data.get("contexto", None)

    try:
        cal = generar_contenido_semanal(perfil=perfil, contenido_extra=contexto)
        guardar_generacion(user["id"], perfil["id"], "calendario",
                          contenido=json.dumps(cal, ensure_ascii=False))
        return JSONResponse({"ok": True, "calendario": cal})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ============================================================
# API - DATOS
# ============================================================

@app.get("/api/perfil")
async def api_perfil(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    perfil = get_perfil_activo(user["id"])
    return JSONResponse({"perfil": perfil})


@app.get("/api/opciones")
async def api_opciones(request: Request):
    """Devuelve las opciones disponibles para los formularios."""
    tipos_contenido = ["EDUCATIVO", "ANTES_DESPUES", "TESTIMONIO", "PRODUCTO",
                       "DETRAS_DE_CAMARAS", "TENDENCIA", "PROMOCION", "PERSONAL"]
    tipos_publicacion = list(ESTILOS_PUBLICACION.keys())
    movimientos = {k: v["descripcion"] for k, v in MOVIMIENTOS_VIDEO.items()}
    return JSONResponse({
        "tipos_contenido": tipos_contenido,
        "tipos_publicacion": tipos_publicacion,
        "movimientos_video": movimientos,
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
