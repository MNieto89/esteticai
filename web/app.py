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
import logging
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("esteticai")

from fastapi import FastAPI, Request, HTTPException, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_engine import generar_contenido_semanal, generar_copy_individual
from agents.image_engine import generar_imagen_automatica, generar_prompt_automatico, ESTILOS_PUBLICACION
from agents.video_engine import generar_video_desde_imagen, MOVIMIENTOS_VIDEO, MOVIMIENTO_RECOMENDADO
from agents.photo_engine import procesar_foto_tratamiento, subir_imagen_a_fal, FONDOS_PROFESIONALES, obtener_fondos_disponibles
from agents.composer_engine import componer_antes_despues, obtener_plantillas_disponibles, PLANTILLA_INFO

import sqlite3

# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).parent
# En produccion, usar volumen persistente /data para la DB
if os.environ.get("RAILWAY_ENVIRONMENT"):
    DB_PATH = Path("/data/esteticai.db")
else:
    DB_PATH = BASE_DIR / "esteticai.db"
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app = FastAPI(title="Esteticai", version="1.0")

# Seguridad: HTTPS y cookies seguras en producción
IS_PRODUCTION = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=IS_PRODUCTION,
    same_site="lax",
    max_age=86400 * 7,  # 7 días
)

# Trusted Host en producción para prevenir host header attacks
if IS_PRODUCTION:
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    allowed_hosts = os.environ.get("ALLOWED_HOSTS", "esteticai.com,*.up.railway.app").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[h.strip() for h in allowed_hosts])

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ============================================================
# RATE LIMITING (en memoria, sin Redis)
# ============================================================

from collections import defaultdict
import time as _time

# {user_id: {endpoint: [timestamps]}}
_rate_limits = defaultdict(lambda: defaultdict(list))

# Limites: (max_requests, window_seconds)
RATE_LIMITS = {
    "/api/generar/copy": (20, 3600),        # 20 copys/hora
    "/api/generar/imagen": (15, 3600),       # 15 imagenes/hora
    "/api/generar/video": (5, 3600),         # 5 videos/hora
    "/api/generar/calendario": (10, 3600),   # 10 calendarios/hora
    "/api/mejorar-foto": (15, 3600),         # 15 fotos/hora
    "/api/componer-antes-despues": (20, 3600),  # 20 composiciones/hora
    "/api/calendario/pdf": (20, 3600),       # 20 PDFs/hora
}


def check_rate_limit(user_id, endpoint):
    """Verifica si el usuario ha excedido el límite. Retorna True si OK, False si excedido."""
    if endpoint not in RATE_LIMITS:
        return True
    max_req, window = RATE_LIMITS[endpoint]
    now = _time.time()
    # Limpiar timestamps viejos
    _rate_limits[user_id][endpoint] = [
        t for t in _rate_limits[user_id][endpoint] if now - t < window
    ]
    if len(_rate_limits[user_id][endpoint]) >= max_req:
        return False
    _rate_limits[user_id][endpoint].append(now)
    return True


# ============================================================
# ERROR HANDLERS
# ============================================================

from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request, "error.html", context={
        "titulo": "P\u00e1gina no encontrada",
        "mensaje": "La p\u00e1gina que buscas no existe o ha sido movida.",
        "icono": "&#128269;",
    }, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(request, "error.html", context={
        "titulo": "Error del servidor",
        "mensaje": "Algo ha ido mal. Int\u00e9ntalo de nuevo en unos minutos.",
        "icono": "&#9888;&#65039;",
    }, status_code=500)


# Health check para verificar que la app arranca
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0"}


# ============================================================
# SEO
# ============================================================

@app.get("/robots.txt")
async def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /perfil/
Disallow: /api/
Sitemap: https://esteticai.com/sitemap.xml
"""
    from starlette.responses import PlainTextResponse
    return PlainTextResponse(content)


@app.get("/sitemap.xml")
async def sitemap_xml():
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://esteticai.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://esteticai.com/precios</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://esteticai.com/registro</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>
  <url><loc>https://esteticai.com/login</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>
  <url><loc>https://esteticai.com/privacidad</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
  <url><loc>https://esteticai.com/legal</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
</urlset>"""
    from starlette.responses import Response
    return Response(content=sitemap, media_type="application/xml")


# ============================================================
# BASE DE DATOS
# ============================================================

def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


from contextlib import contextmanager

@contextmanager
def db_connection():
    """Context manager para conexiones DB. Usa: with db_connection() as db: ..."""
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


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
            valores TEXT DEFAULT '[]',
            publico TEXT DEFAULT '',
            redes TEXT DEFAULT '["Instagram"]',
            mejores_horarios TEXT DEFAULT '{}',
            creado_en TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            usado INTEGER DEFAULT 0,
            creado_en TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS uso_mensual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            copys INTEGER DEFAULT 0,
            imagenes INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            fotos INTEGER DEFAULT 0,
            composiciones INTEGER DEFAULT 0,
            calendarios INTEGER DEFAULT 0,
            UNIQUE(usuario_id, anio, mes),
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
    # Migraciones: anadir columnas si no existen (para DBs creadas antes)
    try:
        db.execute("SELECT valores FROM perfiles LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE perfiles ADD COLUMN valores TEXT DEFAULT '[]'")
        db.execute("ALTER TABLE perfiles ADD COLUMN publico TEXT DEFAULT ''")
        db.execute("ALTER TABLE perfiles ADD COLUMN redes TEXT DEFAULT '[\"Instagram\"]'")
        db.execute("ALTER TABLE perfiles ADD COLUMN mejores_horarios TEXT DEFAULT '{}'")
    # Migracion: plan y trial en usuarios
    try:
        db.execute("SELECT plan FROM usuarios LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE usuarios ADD COLUMN plan TEXT DEFAULT 'trial'")
        db.execute("ALTER TABLE usuarios ADD COLUMN trial_ends_at TEXT DEFAULT ''")
        db.execute("ALTER TABLE usuarios ADD COLUMN stripe_customer_id TEXT DEFAULT ''")
        db.execute("ALTER TABLE usuarios ADD COLUMN stripe_subscription_id TEXT DEFAULT ''")
    db.commit()
    db.close()


init_db()


# ============================================================
# SISTEMA DE PLANES
# ============================================================

PLANES = {
    "free": {
        "nombre": "Free",
        "precio": 0,
        "limites": {
            "copys": 5, "imagenes": 3, "videos": 0,
            "fotos": 0, "composiciones": 2, "calendarios": 2,
        },
    },
    "trial": {
        "nombre": "Trial (Pro)",
        "precio": 0,
        "limites": {
            "copys": 50, "imagenes": 50, "videos": 10,
            "fotos": 30, "composiciones": 20, "calendarios": 10,
        },
    },
    "starter": {
        "nombre": "Starter",
        "precio": 59,
        "limites": {
            "copys": -1, "imagenes": 15, "videos": 0,
            "fotos": 0, "composiciones": 5, "calendarios": -1,
        },
    },
    "pro": {
        "nombre": "Pro",
        "precio": 149,
        "limites": {
            "copys": -1, "imagenes": 50, "videos": 10,
            "fotos": 30, "composiciones": 20, "calendarios": -1,
        },
    },
    "business": {
        "nombre": "Business",
        "precio": 249,
        "limites": {
            "copys": -1, "imagenes": -1, "videos": 30,
            "fotos": -1, "composiciones": -1, "calendarios": -1,
        },
    },
}

# Mapeo tipo de generación → campo en uso_mensual
TIPO_A_CAMPO_USO = {
    "copy": "copys",
    "imagen": "imagenes",
    "video": "videos",
    "foto": "fotos",
    "composicion": "composiciones",
    "calendario": "calendarios",
}


def get_plan_usuario(user):
    """Devuelve el plan efectivo del usuario (considera expiración del trial)."""
    plan = user.get("plan") or user["plan"] if isinstance(user, dict) else "trial"
    if plan == "trial":
        trial_ends = user.get("trial_ends_at") or user["trial_ends_at"] if isinstance(user, dict) else ""
        if trial_ends:
            from datetime import datetime as dt
            try:
                fin = dt.strptime(trial_ends, "%Y-%m-%d %H:%M:%S")
                if dt.utcnow() > fin:
                    return "free"  # Trial expirado
            except (ValueError, TypeError):
                pass
    return plan if plan in PLANES else "free"


def get_uso_mensual(user_id):
    """Devuelve el uso del mes actual."""
    now = datetime.utcnow()
    db = get_db()
    uso = db.execute(
        "SELECT * FROM uso_mensual WHERE usuario_id = ? AND anio = ? AND mes = ?",
        (user_id, now.year, now.month)
    ).fetchone()
    db.close()
    if uso:
        return dict(uso)
    return {
        "copys": 0, "imagenes": 0, "videos": 0,
        "fotos": 0, "composiciones": 0, "calendarios": 0,
    }


def incrementar_uso(user_id, tipo_gen):
    """Incrementa el contador de uso mensual para un tipo de generación."""
    campo = TIPO_A_CAMPO_USO.get(tipo_gen)
    if not campo:
        return
    now = datetime.utcnow()
    with db_connection() as db:
        db.execute(f"""
            INSERT INTO uso_mensual (usuario_id, anio, mes, {campo})
            VALUES (?, ?, ?, 1)
            ON CONFLICT(usuario_id, anio, mes)
            DO UPDATE SET {campo} = {campo} + 1
        """, (user_id, now.year, now.month))


def verificar_limite_plan(user, tipo_gen):
    """Verifica si el usuario puede generar. Retorna (ok, mensaje_error)."""
    plan_id = get_plan_usuario(user)
    plan = PLANES.get(plan_id, PLANES["free"])
    campo = TIPO_A_CAMPO_USO.get(tipo_gen)
    if not campo:
        return True, ""

    limite = plan["limites"].get(campo, 0)
    if limite == -1:  # Ilimitado
        return True, ""
    if limite == 0:  # No incluido en el plan
        return False, f"Tu plan {plan['nombre']} no incluye esta funci\u00f3n. Actualiza a un plan superior."

    uso = get_uso_mensual(user["id"])
    usado = uso.get(campo, 0)
    if usado >= limite:
        return False, f"Has alcanzado el l\u00edmite mensual de {limite} {campo} en tu plan {plan['nombre']}. Actualiza tu plan para generar m\u00e1s."

    return True, ""


def get_info_plan_usuario(user):
    """Retorna info completa del plan y uso para mostrar en el dashboard."""
    plan_id = get_plan_usuario(user)
    plan = PLANES.get(plan_id, PLANES["free"])
    uso = get_uso_mensual(user["id"])

    # Calcular días de trial restantes
    dias_trial = 0
    en_trial = plan_id == "trial"
    if en_trial:
        trial_ends = user.get("trial_ends_at") or ""
        if trial_ends:
            from datetime import datetime as dt
            try:
                fin = dt.strptime(trial_ends, "%Y-%m-%d %H:%M:%S")
                dias_trial = max(0, (fin - dt.utcnow()).days)
            except (ValueError, TypeError):
                pass

    # Construir info de cada recurso
    recursos = {}
    for campo, limite in plan["limites"].items():
        usado = uso.get(campo, 0)
        recursos[campo] = {
            "usado": usado,
            "limite": limite,
            "ilimitado": limite == -1,
            "no_incluido": limite == 0,
            "porcentaje": min(100, int(usado / limite * 100)) if limite > 0 else 0,
        }

    return {
        "plan_id": plan_id,
        "plan_nombre": plan["nombre"],
        "precio": plan["precio"],
        "en_trial": en_trial,
        "dias_trial": dias_trial,
        "recursos": recursos,
    }


# ============================================================
# AUTENTICACION
# ============================================================

def hash_password(password):
    """Hash con bcrypt (seguro, con salt automático)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password, stored_hash):
    """Verifica password. Compatible con bcrypt y SHA256 legacy.
    Si detecta hash SHA256 antiguo, lo migra a bcrypt automáticamente."""
    if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    else:
        # Legacy SHA256 — verificar y migrar
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def _migrar_password_si_legacy(user_id, password, stored_hash):
    """Si el hash es SHA256 legacy, actualiza a bcrypt en la DB."""
    if not (stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$")):
        nuevo_hash = hash_password(password)
        with db_connection() as db:
            db.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?",
                       (nuevo_hash, user_id))


import re

def validar_email(email):
    """Valida formato básico de email."""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def sanitizar_texto(texto, max_len=500):
    """Limpia y limita longitud de texto del usuario."""
    if not texto:
        return ""
    texto = texto.strip()
    if len(texto) > max_len:
        texto = texto[:max_len]
    return texto


def validar_registro(nombre, email, password):
    """Valida datos de registro. Retorna error string o None."""
    if not nombre or len(nombre.strip()) < 2:
        return "El nombre debe tener al menos 2 caracteres."
    if len(nombre) > 100:
        return "El nombre es demasiado largo (m\u00e1ximo 100 caracteres)."
    if not email or not validar_email(email):
        return "Introduce un email v\u00e1lido."
    if len(email) > 200:
        return "El email es demasiado largo."
    if not password or len(password) < 6:
        return "La contrase\u00f1a debe tener al menos 6 caracteres."
    if len(password) > 200:
        return "La contrase\u00f1a es demasiado larga."
    return None


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
            "valores": json.loads(perfil["valores"] or "[]"),
            "publico": perfil["publico"] or "",
            "redes": json.loads(perfil["redes"] or '["Instagram"]'),
            "mejores_horarios": json.loads(perfil["mejores_horarios"] or "{}"),
        }
    return None


def guardar_generacion(user_id, perfil_id, tipo, contenido=None,
                        imagen_url=None, video_url=None, metadata=None):
    with db_connection() as db:
        db.execute(
            "INSERT INTO generaciones (usuario_id, perfil_id, tipo, contenido, imagen_url, video_url, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, perfil_id, tipo, contenido, imagen_url, video_url, json.dumps(metadata or {}))
        )


# ============================================================
# PAGINAS PUBLICAS
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_usuario_actual(request)
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(request, "home.html")


@app.get("/precios", response_class=HTMLResponse)
async def precios_page(request: Request):
    return templates.TemplateResponse(request, "precios.html")


@app.get("/privacidad", response_class=HTMLResponse)
async def privacidad_page(request: Request):
    return templates.TemplateResponse(request, "privacidad.html")


@app.get("/legal", response_class=HTMLResponse)
async def legal_page(request: Request):
    return templates.TemplateResponse(request, "legal.html")


@app.get("/cookies", response_class=HTMLResponse)
async def cookies_page(request: Request):
    return templates.TemplateResponse(request, "cookies.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", context={"error": None})


@app.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    db.close()
    if not user or not verificar_password(password, user["password_hash"]):
        return templates.TemplateResponse(request, "login.html", context={
            "error": "Email o contrase\u00f1a incorrectos"
        })
    # Migrar hash legacy a bcrypt si es necesario
    _migrar_password_si_legacy(user["id"], password, user["password_hash"])
    request.session["user_id"] = user["id"]
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request):
    return templates.TemplateResponse(request, "registro.html", context={"error": None})


@app.post("/registro")
async def registro_submit(request: Request, nombre: str = Form(...),
                           email: str = Form(...), password: str = Form(...)):
    # Sanitizar
    nombre = sanitizar_texto(nombre, 100)
    email = sanitizar_texto(email, 200).lower()
    # Validar
    error = validar_registro(nombre, email, password)
    if error:
        return templates.TemplateResponse(request, "registro.html", context={"error": error})
    db = get_db()
    existe = db.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    if existe:
        db.close()
        return templates.TemplateResponse(request, "registro.html", context={
            "error": "Este email ya est\u00e1 registrado"
        })
    trial_ends = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO usuarios (email, password_hash, nombre, plan, trial_ends_at) VALUES (?, ?, ?, 'trial', ?)",
        (email, hash_password(password), nombre, trial_ends)
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
# RECUPERAR CONTRASEÑA
# ============================================================

@app.get("/recuperar", response_class=HTMLResponse)
async def recuperar_page(request: Request):
    return templates.TemplateResponse(request, "recuperar.html", context={
        "error": None, "success": None, "reset_link": None
    })


@app.post("/recuperar")
async def recuperar_submit(request: Request, email: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not user:
        db.close()
        # No revelar si el email existe o no (seguridad)
        return templates.TemplateResponse(request, "recuperar.html", context={
            "error": None, "reset_link": None,
            "success": "Si el email existe, se ha generado un enlace de recuperaci\u00f3n."
        })
    # Invalidar tokens anteriores
    db.execute("UPDATE password_resets SET usado = 1 WHERE email = ? AND usado = 0", (email,))
    # Crear nuevo token
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO password_resets (email, token) VALUES (?, ?)", (email, token))
    db.commit()
    db.close()
    # En producción: enviar email con el enlace
    # Por ahora: mostrar enlace directamente (modo desarrollo/demo)
    reset_link = f"/reset/{token}"
    return templates.TemplateResponse(request, "recuperar.html", context={
        "error": None, "reset_link": reset_link,
        "success": "Enlace de recuperaci\u00f3n generado. En producci\u00f3n se enviar\u00e1 por email."
    })


@app.get("/reset/{token}", response_class=HTMLResponse)
async def reset_page(request: Request, token: str):
    db = get_db()
    reset = db.execute(
        "SELECT * FROM password_resets WHERE token = ? AND usado = 0", (token,)
    ).fetchone()
    db.close()
    if not reset:
        return templates.TemplateResponse(request, "recuperar.html", context={
            "error": "Enlace inv\u00e1lido o expirado. Solicita uno nuevo.",
            "success": None, "reset_link": None
        })
    # Verificar que no tenga más de 1 hora
    from datetime import datetime as dt
    creado = dt.strptime(reset["creado_en"], "%Y-%m-%d %H:%M:%S")
    if (dt.utcnow() - creado).total_seconds() > 3600:
        return templates.TemplateResponse(request, "recuperar.html", context={
            "error": "El enlace ha expirado (m\u00e1ximo 1 hora). Solicita uno nuevo.",
            "success": None, "reset_link": None
        })
    return templates.TemplateResponse(request, "reset_password.html", context={
        "token": token, "error": None
    })


@app.post("/reset/{token}")
async def reset_submit(request: Request, token: str, password: str = Form(...)):
    if len(password) < 6:
        return templates.TemplateResponse(request, "reset_password.html", context={
            "token": token,
            "error": "La contrase\u00f1a debe tener al menos 6 caracteres."
        })
    db = get_db()
    reset = db.execute(
        "SELECT * FROM password_resets WHERE token = ? AND usado = 0", (token,)
    ).fetchone()
    if not reset:
        db.close()
        return templates.TemplateResponse(request, "recuperar.html", context={
            "error": "Enlace inv\u00e1lido o ya usado.",
            "success": None, "reset_link": None
        })
    # Actualizar password
    db.execute("UPDATE usuarios SET password_hash = ? WHERE email = ?",
               (hash_password(password), reset["email"]))
    db.execute("UPDATE password_resets SET usado = 1 WHERE token = ?", (token,))
    db.commit()
    db.close()
    return templates.TemplateResponse(request, "login.html", context={
        "error": None,
        "success": "Contrase\u00f1a actualizada. Ya puedes iniciar sesi\u00f3n."
    })


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

    plan_info = get_info_plan_usuario(user)

    return templates.TemplateResponse(request, "dashboard.html", context={
        "user": user,
        "perfil": perfil,
        "generaciones": generaciones,
        "plan": plan_info,
    })


# ============================================================
# PERFIL DE MARCA
# ============================================================

TIPOS_NEGOCIO_VALIDOS = [
    "Centro de estetica", "Clinica de estetica facial y corporal",
    "Salon de belleza", "Spa", "Freelance esteticista",
    "Peluqueria con estetica", "Distribuidora de cosmetica",
    "Tienda de cosmetica online"
]
TONOS_VALIDOS = ["cercano", "profesional", "divertido", "elegante", "educativo"]
REDES_VALIDAS = ["Instagram", "Facebook", "TikTok", "LinkedIn"]


def _parsear_form_perfil(form):
    """Extrae, sanitiza y valida los datos del formulario de perfil."""
    # Sanitizar textos con límites
    nombre_negocio = sanitizar_texto(form.get("nombre_negocio", ""), 150)
    propietaria = sanitizar_texto(form.get("propietaria", ""), 100)
    ciudad = sanitizar_texto(form.get("ciudad", ""), 100)
    publico = sanitizar_texto(form.get("publico", ""), 500)
    instagram_handle = sanitizar_texto(form.get("instagram_handle", ""), 50)

    # Validar tipo negocio y tono contra whitelist
    tipo_negocio = form.get("tipo_negocio", "Centro de estetica")
    if tipo_negocio not in TIPOS_NEGOCIO_VALIDOS:
        tipo_negocio = "Centro de estetica"
    tono = form.get("tono", "cercano")
    if tono not in TONOS_VALIDOS:
        tono = "cercano"

    # Listas con límite de items y longitud por item
    servicios_raw = form.get("servicios", "").split("\n")
    servicios = [sanitizar_texto(s, 100) for s in servicios_raw if s.strip()][:30]
    productos_raw = form.get("productos", "").split("\n")
    productos = [sanitizar_texto(p, 100) for p in productos_raw if p.strip()][:30]
    valores_raw = form.get("valores", "").split("\n")
    valores = [sanitizar_texto(v, 100) for v in valores_raw if v.strip()][:15]

    # Redes: validar contra whitelist
    redes_seleccionadas = [r for r in form.getlist("redes") if r in REDES_VALIDAS]
    if not redes_seleccionadas:
        redes_seleccionadas = ["Instagram"]

    mejores_horarios = {}
    horarios_validos = ["", "9:00-10:00", "12:00-13:00", "18:00-19:00", "20:00-21:00"]
    for red in redes_seleccionadas:
        horario = form.get(f"horario_{red.lower()}", "")
        if horario in horarios_validos and horario:
            mejores_horarios[red] = horario

    return {
        "nombre_negocio": nombre_negocio,
        "propietaria": propietaria,
        "ciudad": ciudad,
        "tipo_negocio": tipo_negocio,
        "servicios": json.dumps(servicios),
        "productos": json.dumps(productos),
        "tono": tono,
        "instagram_handle": instagram_handle,
        "valores": json.dumps(valores),
        "publico": publico,
        "redes": json.dumps(redes_seleccionadas),
        "mejores_horarios": json.dumps(mejores_horarios),
    }


@app.get("/perfil/crear", response_class=HTMLResponse)
async def perfil_crear_page(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request, "perfil_crear.html", context={
        "user": user, "perfil": None, "modo": "crear",
    })


@app.post("/perfil/crear")
async def perfil_crear_submit(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    form = await request.form()
    datos = _parsear_form_perfil(form)
    # Validar campos obligatorios
    if not datos["nombre_negocio"]:
        return templates.TemplateResponse(request, "perfil_crear.html", context={
            "user": user, "perfil": None, "modo": "crear",
            "error": "El nombre del negocio es obligatorio."
        })
    servicios_list = json.loads(datos["servicios"])
    if not servicios_list:
        return templates.TemplateResponse(request, "perfil_crear.html", context={
            "user": user, "perfil": None, "modo": "crear",
            "error": "A\u00f1ade al menos un servicio."
        })
    db = get_db()
    db.execute(
        """INSERT INTO perfiles (usuario_id, nombre_negocio, propietaria, ciudad,
           tipo_negocio, servicios, productos, tono, instagram_handle,
           valores, publico, redes, mejores_horarios)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user["id"], datos["nombre_negocio"], datos["propietaria"],
         datos["ciudad"], datos["tipo_negocio"],
         datos["servicios"], datos["productos"],
         datos["tono"], datos["instagram_handle"],
         datos["valores"], datos["publico"],
         datos["redes"], datos["mejores_horarios"])
    )
    db.commit()
    db.close()
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/perfil/editar", response_class=HTMLResponse)
async def perfil_editar_page(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return RedirectResponse("/perfil/crear", status_code=303)
    return templates.TemplateResponse(request, "perfil_crear.html", context={
        "user": user, "perfil": perfil, "modo": "editar",
    })


@app.post("/perfil/editar")
async def perfil_editar_submit(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return RedirectResponse("/perfil/crear", status_code=303)
    form = await request.form()
    datos = _parsear_form_perfil(form)
    db = get_db()
    db.execute(
        """UPDATE perfiles SET nombre_negocio=?, propietaria=?, ciudad=?,
           tipo_negocio=?, servicios=?, productos=?, tono=?, instagram_handle=?,
           valores=?, publico=?, redes=?, mejores_horarios=?
           WHERE id=?""",
        (datos["nombre_negocio"], datos["propietaria"],
         datos["ciudad"], datos["tipo_negocio"],
         datos["servicios"], datos["productos"],
         datos["tono"], datos["instagram_handle"],
         datos["valores"], datos["publico"],
         datos["redes"], datos["mejores_horarios"],
         perfil["id"])
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
    ok, msg = verificar_limite_plan(user, "copy")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)
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
        incrementar_uso(user["id"], "copy")
        return JSONResponse({"ok": True, "copy": copy})
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return JSONResponse({"error": "API key no configurada. Contacta al administrador."}, status_code=500)
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            return JSONResponse({"error": "La generaci\u00f3n tard\u00f3 demasiado. Int\u00e9ntalo de nuevo."}, status_code=500)
        logger.error("Copy generation failed: %s", error_msg)
        return JSONResponse({"error": "No se pudo generar el copy. Int\u00e9ntalo de nuevo."}, status_code=500)


@app.post("/api/generar/imagen")
async def api_generar_imagen(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    ok, msg = verificar_limite_plan(user, "imagen")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)
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
                              imagen_url=resultado.get("url") if not resultado.get("es_demo") else None,
                              metadata={"servicio": servicio, "tipo": tipo_pub, "es_demo": resultado.get("es_demo", False)})
            incrementar_uso(user["id"], "imagen")
        return JSONResponse({"ok": True, "imagen": resultado})
    except Exception as e:
        logger.error("Image generation failed: %s", e)
        return JSONResponse({"error": "No se pudo generar la imagen. Int\u00e9ntalo de nuevo."}, status_code=500)


@app.post("/api/generar/video")
async def api_generar_video(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    ok, msg = verificar_limite_plan(user, "video")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)

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
        if "error" not in resultado and not resultado.get("es_demo"):
            guardar_generacion(user["id"], perfil["id"] if perfil else None, "video",
                              imagen_url=url_imagen,
                              video_url=resultado.get("url"),
                              metadata={"movimiento": tipo_movimiento, "duracion": duracion})
            incrementar_uso(user["id"], "video")
        return JSONResponse({"ok": True, "video": resultado})
    except Exception as e:
        error_msg = str(e)
        logger.error("Video generation failed: %s", error_msg)
        if "timeout" in error_msg.lower():
            return JSONResponse({"error": "La generaci\u00f3n de video tard\u00f3 demasiado. Prueba con 5 segundos."}, status_code=500)
        return JSONResponse({"error": "No se pudo generar el video. Int\u00e9ntalo de nuevo."}, status_code=500)


@app.post("/api/generar/calendario")
async def api_generar_calendario(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    ok, msg = verificar_limite_plan(user, "calendario")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    data = await request.json()
    contexto = data.get("contexto", None)

    try:
        cal = generar_contenido_semanal(perfil=perfil, contenido_extra=contexto)
        guardar_generacion(user["id"], perfil["id"], "calendario",
                          contenido=json.dumps(cal, ensure_ascii=False))
        incrementar_uso(user["id"], "calendario")
        return JSONResponse({"ok": True, "calendario": cal})
    except Exception as e:
        logger.error("Calendar generation failed: %s", e)
        return JSONResponse({"error": "No se pudo generar el calendario. Int\u00e9ntalo de nuevo."}, status_code=500)


# ============================================================
# API - EXPORTAR CALENDARIO A PDF
# ============================================================

@app.post("/api/calendario/pdf")
async def api_calendario_pdf(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    data = await request.json()
    cal = data.get("calendario", {})
    if not cal:
        return JSONResponse({"error": "No hay calendario para exportar"}, status_code=400)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import mm
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=25*mm, bottomMargin=20*mm,
                                leftMargin=20*mm, rightMargin=20*mm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='BrandTitle', fontSize=20, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#e86586'), spaceAfter=6))
        styles.add(ParagraphStyle(name='SubTitle', fontSize=11, fontName='Helvetica',
                                  textColor=colors.HexColor('#888'), spaceAfter=14))
        styles.add(ParagraphStyle(name='DayTitle', fontSize=13, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#333'), spaceBefore=10, spaceAfter=4))
        styles.add(ParagraphStyle(name='CopyText', fontSize=10, fontName='Helvetica',
                                  textColor=colors.HexColor('#444'), leading=14, spaceAfter=4))
        styles.add(ParagraphStyle(name='MetaText', fontSize=9, fontName='Helvetica-Oblique',
                                  textColor=colors.HexColor('#999'), spaceAfter=8))
        styles.add(ParagraphStyle(name='StrategyBox', fontSize=10, fontName='Helvetica-Oblique',
                                  textColor=colors.HexColor('#e86586'), backColor=colors.HexColor('#fef0f3'),
                                  borderPadding=8, spaceAfter=14, leading=14))

        elements = []

        # Header
        elements.append(Paragraph(f"Calendario Semanal", styles['BrandTitle']))
        elements.append(Paragraph(f"{perfil['nombre_negocio']} &mdash; Generado con Esteticai", styles['SubTitle']))
        elements.append(Spacer(1, 4*mm))

        # Estrategia
        estrategia = cal.get("estrategia_semanal") or cal.get("estrategia", "")
        if estrategia:
            elements.append(Paragraph(f"<b>Estrategia de la semana:</b> {estrategia}", styles['StrategyBox']))

        # Publicaciones
        pubs = cal.get("calendario_semanal") or cal.get("publicaciones", [])
        for pub in pubs:
            dia = pub.get("dia", "")
            hora = pub.get("hora_publicacion") or pub.get("hora", "")
            red = pub.get("red_social", "")
            formato = pub.get("formato", "")
            tipo = pub.get("tipo_contenido") or pub.get("tipo", "")
            copy = pub.get("copy", "")
            hashtags = pub.get("hashtags", "")
            cta = pub.get("cta", "")

            elements.append(Paragraph(f"{dia}", styles['DayTitle']))
            meta_parts = [p for p in [hora, red, formato, tipo] if p]
            elements.append(Paragraph(" &bull; ".join(meta_parts), styles['MetaText']))

            if copy:
                # Escapar caracteres especiales para ReportLab
                copy_clean = copy.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(copy_clean, styles['CopyText']))

            if hashtags:
                if isinstance(hashtags, list):
                    hashtags = " ".join(hashtags)
                elements.append(Paragraph(hashtags, styles['MetaText']))

            if cta:
                elements.append(Paragraph(f"CTA: {cta}", styles['MetaText']))

            elements.append(Spacer(1, 3*mm))

        # Consejo
        consejo = cal.get("consejo_de_la_semana") or cal.get("consejo", "")
        if consejo:
            elements.append(Spacer(1, 4*mm))
            elements.append(Paragraph(f"<b>Consejo de la semana:</b> {consejo}", styles['StrategyBox']))

        # Footer
        elements.append(Spacer(1, 8*mm))
        elements.append(Paragraph("Generado con Esteticai &mdash; esteticai.com", styles['MetaText']))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        import base64
        pdf_b64 = base64.b64encode(pdf_bytes).decode()
        return JSONResponse({
            "ok": True,
            "pdf_base64": f"data:application/pdf;base64,{pdf_b64}",
            "filename": f"calendario_{perfil['nombre_negocio'].replace(' ', '_')}.pdf"
        })

    except Exception as e:
        logger.error("PDF calendar export failed: %s", e)
        return JSONResponse({"error": "No se pudo generar el PDF"}, status_code=500)


# ============================================================
# API - MEJORAR FOTO REAL
# ============================================================

@app.post("/api/mejorar-foto")
async def api_mejorar_foto(
    request: Request,
    foto: UploadFile = File(...),
    tipo_fondo: str = Form("clinica_blanco"),
    tipo_tratamiento: str = Form("default"),
    eliminar_fondo: str = Form("true"),
    mejorar_calidad: str = Form("true"),
):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    ok, msg = verificar_limite_plan(user, "foto")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    # Leer la foto subida
    contenido = await foto.read()
    if len(contenido) > 10 * 1024 * 1024:  # max 10MB
        return JSONResponse({"error": "La foto es demasiado grande (max 10MB)"}, status_code=400)

    try:
        # Subir a fal.ai storage
        image_url = subir_imagen_a_fal(contenido, filename=foto.filename or "foto.jpg")
        if not image_url:
            return JSONResponse({"error": "No se pudo subir la imagen"}, status_code=500)

        # Procesar con pipeline
        opciones = {
            "eliminar_fondo": eliminar_fondo.lower() == "true",
            "mejorar_calidad": mejorar_calidad.lower() == "true",
            "tipo_fondo": tipo_fondo,
            "tipo_tratamiento": tipo_tratamiento,
        }
        resultado = procesar_foto_tratamiento(
            image_url=image_url,
            opciones=opciones,
        )

        # Guardar en historial
        guardar_generacion(
            user["id"], perfil["id"], "foto_mejorada",
            imagen_url=resultado.get("url_final"),
            metadata={
                "original_url": resultado.get("original_url"),
                "pasos": resultado.get("pasos_completados", []),
                "tipo_fondo": tipo_fondo,
                "tipo_tratamiento": tipo_tratamiento,
            },
        )
        incrementar_uso(user["id"], "foto")
        return JSONResponse({"ok": True, "resultado": resultado})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/fondos-disponibles")
async def api_fondos_disponibles():
    """Devuelve la lista de fondos profesionales disponibles."""
    return JSONResponse({"fondos": obtener_fondos_disponibles()})


# ============================================================
# API - COMPOSICION ANTES/DESPUES
# ============================================================

@app.post("/api/componer-antes-despues")
async def api_componer_antes_despues(
    request: Request,
    foto_antes: UploadFile = File(...),
    foto_despues: UploadFile = File(...),
    plantilla: str = Form("side_by_side"),
    tratamiento: str = Form(""),
    sesiones: str = Form(""),
    cta: str = Form(""),
):
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    ok, msg = verificar_limite_plan(user, "composicion")
    if not ok:
        return JSONResponse({"error": msg}, status_code=429)
    perfil = get_perfil_activo(user["id"])
    if not perfil:
        return JSONResponse({"error": "Crea un perfil primero"}, status_code=400)

    # Leer las fotos
    bytes_antes = await foto_antes.read()
    bytes_despues = await foto_despues.read()

    max_size = 10 * 1024 * 1024
    if len(bytes_antes) > max_size or len(bytes_despues) > max_size:
        return JSONResponse({"error": "Las fotos son demasiado grandes (max 10MB cada una)"}, status_code=400)

    # Config de composicion con datos del perfil
    config = {
        "nombre_negocio": perfil.get("nombre_negocio", ""),
        "tratamiento": tratamiento or "Resultados reales",
        "sesiones": sesiones,
        "cta": cta or "Reserva tu valoracion gratuita",
        "color_marca": (199, 121, 135),  # Rosa Esteticai
    }

    try:
        resultado = componer_antes_despues(
            img_antes_bytes=bytes_antes,
            img_despues_bytes=bytes_despues,
            plantilla=plantilla,
            config=config,
        )

        if "error" in resultado:
            return JSONResponse({"error": resultado["error"]}, status_code=500)

        # No guardamos image_bytes en la respuesta JSON
        respuesta = {k: v for k, v in resultado.items() if k != "image_bytes"}

        # Guardar en historial
        guardar_generacion(
            user["id"], perfil["id"], "antes_despues",
            imagen_url=None,
            metadata={
                "plantilla": plantilla,
                "tratamiento": tratamiento,
                "tamano_kb": resultado.get("tamano_kb"),
            },
        )

        incrementar_uso(user["id"], "composicion")
        return JSONResponse({"ok": True, "resultado": respuesta})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/plantillas-disponibles")
async def api_plantillas_disponibles():
    """Devuelve las plantillas de composicion disponibles."""
    return JSONResponse({"plantillas": obtener_plantillas_disponibles()})


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


# ============================================================
# STRIPE - PAGOS (skeleton, activar con STRIPE_SECRET_KEY)
# ============================================================

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Mapeo plan → Stripe Price ID (configurar en Stripe Dashboard)
STRIPE_PRICE_IDS = {
    "starter": os.environ.get("STRIPE_PRICE_STARTER", ""),
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "business": os.environ.get("STRIPE_PRICE_BUSINESS", ""),
}


@app.get("/upgrade", response_class=HTMLResponse)
async def upgrade_page(request: Request):
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    plan_info = get_info_plan_usuario(user)
    return templates.TemplateResponse(request, "upgrade.html", context={
        "user": user, "plan": plan_info, "planes": PLANES,
        "stripe_activo": bool(STRIPE_SECRET_KEY),
    })


@app.post("/api/crear-checkout")
async def api_crear_checkout(request: Request):
    """Crea una sesión de Stripe Checkout para upgrade de plan."""
    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)

    if not STRIPE_SECRET_KEY:
        return JSONResponse({
            "error": "El sistema de pagos a\u00fan no est\u00e1 configurado. Contacta con hola@esteticai.com para activar tu plan."
        }, status_code=503)

    data = await request.json()
    plan_elegido = data.get("plan", "")
    if plan_elegido not in STRIPE_PRICE_IDS or not STRIPE_PRICE_IDS[plan_elegido]:
        return JSONResponse({"error": "Plan no v\u00e1lido"}, status_code=400)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        # Crear o recuperar customer de Stripe
        customer_id = user.get("stripe_customer_id") or ""
        if not customer_id:
            customer = stripe.Customer.create(
                email=user["email"],
                name=user["nombre"],
                metadata={"user_id": str(user["id"])}
            )
            customer_id = customer.id
            db = get_db()
            db.execute("UPDATE usuarios SET stripe_customer_id = ? WHERE id = ?",
                       (customer_id, user["id"]))
            db.commit()
            db.close()

        # Crear sesión de checkout
        base_url = str(request.base_url).rstrip("/")
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_IDS[plan_elegido], "quantity": 1}],
            success_url=f"{base_url}/upgrade/exito?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/upgrade",
            metadata={"user_id": str(user["id"]), "plan": plan_elegido},
        )
        return JSONResponse({"ok": True, "checkout_url": session.url})

    except ImportError:
        return JSONResponse({"error": "Stripe no est\u00e1 instalado en el servidor."}, status_code=503)
    except Exception as e:
        logger.error("Stripe checkout failed: %s", e)
        return JSONResponse({"error": "Error al crear la sesi\u00f3n de pago."}, status_code=500)


@app.get("/upgrade/exito", response_class=HTMLResponse)
async def upgrade_exito(request: Request):
    """Página de éxito tras completar el pago."""
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    # En producción el webhook actualiza el plan; esto es fallback de UX
    plan_info = get_info_plan_usuario(user)
    return templates.TemplateResponse(request, "upgrade_exito.html", context={
        "user": user, "plan_nombre": plan_info["plan_nombre"],
    })


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Webhook de Stripe para confirmar pagos y gestionar suscripciones."""
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        return JSONResponse({"error": "No configurado"}, status_code=503)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = int(session["metadata"]["user_id"])
            plan = session["metadata"]["plan"]
            subscription_id = session.get("subscription", "")
            db = get_db()
            db.execute(
                "UPDATE usuarios SET plan = ?, stripe_subscription_id = ? WHERE id = ?",
                (plan, subscription_id, user_id)
            )
            db.commit()
            db.close()
            logger.info("Stripe: user %s upgraded to plan %s", user_id, plan)

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            sub_id = subscription["id"]
            db = get_db()
            db.execute(
                "UPDATE usuarios SET plan = 'free', stripe_subscription_id = '' WHERE stripe_subscription_id = ?",
                (sub_id,)
            )
            db.commit()
            db.close()
            logger.info("Stripe: subscription %s cancelled, user downgraded to free", sub_id)

        return JSONResponse({"ok": True})

    except Exception as e:
        logger.error("Stripe webhook failed: %s", e)
        return JSONResponse({"error": str(e)}, status_code=400)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
