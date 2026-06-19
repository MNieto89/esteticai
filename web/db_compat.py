"""
Capa de compatibilidad de base de datos: SQLite (local) y PostgreSQL (produccion).

Si la variable de entorno DATABASE_URL esta configurada y psycopg2 esta instalado,
usa PostgreSQL. En caso contrario, usa SQLite como siempre.

Todas las funciones exponen la misma interfaz que sqlite3, de forma que el resto
del codigo de app.py no necesita saber cual es el backend.
"""

import os
import re
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger("esteticai")

# ---------------------------------------------------------------------------
# Deteccion del backend
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
    _HAS_PG = True
except ImportError:
    _HAS_PG = False

USE_POSTGRES = bool(DATABASE_URL and _HAS_PG)

# Ruta SQLite (solo cuando no hay PostgreSQL)
BASE_DIR = Path(__file__).parent
IS_PRODUCTION = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER"))

if USE_POSTGRES:
    DB_PATH = None
    logger.info("Base de datos: PostgreSQL (DATABASE_URL configurada)")
else:
    if IS_PRODUCTION and Path("/data").exists():
        DB_PATH = Path("/data/esteticai.db")
    else:
        DB_PATH = BASE_DIR / "esteticai.db"
    logger.info("Base de datos: SQLite (%s)", DB_PATH)


# ---------------------------------------------------------------------------
# Conversion de SQL
# ---------------------------------------------------------------------------

def _sql_to_pg(sql):
    """Convierte placeholders ? de SQLite a %s de PostgreSQL."""
    return sql.replace("?", "%s")


def _schema_to_pg(sql):
    """Convierte DDL de SQLite a sintaxis PostgreSQL."""
    sql = _sql_to_pg(sql)
    sql = re.sub(
        r'(\w+)\s+INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
        r'\1 SERIAL PRIMARY KEY',
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(r"\(datetime\('now'\)\)", "CURRENT_TIMESTAMP", sql)
    return sql


# ---------------------------------------------------------------------------
# Wrappers PostgreSQL -> sqlite3 API
# ---------------------------------------------------------------------------

class _PgCursor:
    """Cursor PostgreSQL con la misma interfaz que sqlite3.Cursor."""

    def __init__(self, pg_cursor):
        self._c = pg_cursor

    def execute(self, sql, params=None):
        stripped = sql.strip().upper()
        if stripped.startswith("PRAGMA"):
            return self
        sql = _sql_to_pg(sql)
        self._c.execute(sql, params or ())
        return self

    def fetchone(self):
        try:
            row = self._c.fetchone()
            return dict(row) if row else None
        except psycopg2.ProgrammingError:
            return None

    def fetchall(self):
        try:
            rows = self._c.fetchall()
            return [dict(r) for r in rows]
        except psycopg2.ProgrammingError:
            return []

    @property
    def rowcount(self):
        return self._c.rowcount

    def __iter__(self):
        return iter(self._c)

    def __next__(self):
        return next(self._c)


class _PgConnection:
    """Conexion PostgreSQL con la misma interfaz que sqlite3.Connection."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cursor = _PgCursor(
            self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        )
        return cursor.execute(sql, params)

    def executescript(self, sql):
        sql = _schema_to_pg(sql)
        cursor = self._conn.cursor()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.upper().startswith("PRAGMA"):
                try:
                    cursor.execute(stmt)
                    self._conn.commit()
                except Exception as e:
                    self._conn.rollback()
                    logger.warning("DDL omitido (%s): %s", stmt[:60], e)
        return self

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


# ---------------------------------------------------------------------------
# Funciones publicas (misma interfaz para ambos backends)
# ---------------------------------------------------------------------------

def get_db():
    """Devuelve una conexion a la base de datos (PostgreSQL o SQLite)."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return _PgConnection(conn)
    else:
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA synchronous=NORMAL")
        db.execute("PRAGMA cache_size=-8000")
        db.execute("PRAGMA foreign_keys=ON")
        return db


@contextmanager
def db_connection():
    """Context manager para conexiones DB: with db_connection() as db: ..."""
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Inicializacion de esquema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre TEXT NOT NULL,
        plan TEXT DEFAULT 'trial',
        trial_ends_at TEXT DEFAULT '',
        stripe_customer_id TEXT DEFAULT '',
        stripe_subscription_id TEXT DEFAULT '',
        email_verificado INTEGER DEFAULT 0,
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

    CREATE TABLE IF NOT EXISTS email_verificaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        usado INTEGER DEFAULT 0,
        creado_en TEXT DEFAULT (datetime('now'))
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
"""

_INDEXES_SQL = """
    CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
    CREATE INDEX IF NOT EXISTS idx_generaciones_usuario ON generaciones(usuario_id, creado_en DESC);
    CREATE INDEX IF NOT EXISTS idx_uso_mensual_lookup ON uso_mensual(usuario_id, anio, mes);
    CREATE INDEX IF NOT EXISTS idx_perfiles_usuario ON perfiles(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_password_resets_token ON password_resets(token, usado);
    CREATE INDEX IF NOT EXISTS idx_email_verif_token ON email_verificaciones(token, usado);
"""


def _migrate_pg(db):
    """Migraciones usando ADD COLUMN IF NOT EXISTS (PostgreSQL >= 9.6)."""
    migrations = [
        "ALTER TABLE perfiles ADD COLUMN IF NOT EXISTS valores TEXT DEFAULT '[]'",
        "ALTER TABLE perfiles ADD COLUMN IF NOT EXISTS publico TEXT DEFAULT ''",
        "ALTER TABLE perfiles ADD COLUMN IF NOT EXISTS redes TEXT DEFAULT '[\"Instagram\"]'",
        "ALTER TABLE perfiles ADD COLUMN IF NOT EXISTS mejores_horarios TEXT DEFAULT '{}'",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS plan TEXT DEFAULT 'trial'",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS trial_ends_at TEXT DEFAULT ''",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT DEFAULT ''",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT DEFAULT ''",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verificado INTEGER DEFAULT 0",
    ]
    for m in migrations:
        try:
            db.execute(m)
            db._conn.commit()
        except Exception as e:
            db._conn.rollback()
            logger.warning("Migracion PG omitida: %s", e)


def _migrate_sqlite(db):
    """Migraciones para SQLite (no soporta ADD COLUMN IF NOT EXISTS)."""
    try:
        db.execute("SELECT valores FROM perfiles LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE perfiles ADD COLUMN valores TEXT DEFAULT '[]'")
        db.execute("ALTER TABLE perfiles ADD COLUMN publico TEXT DEFAULT ''")
        db.execute("ALTER TABLE perfiles ADD COLUMN redes TEXT DEFAULT '[\"Instagram\"]'")
        db.execute("ALTER TABLE perfiles ADD COLUMN mejores_horarios TEXT DEFAULT '{}'")

    try:
        db.execute("SELECT plan FROM usuarios LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE usuarios ADD COLUMN plan TEXT DEFAULT 'trial'")
        db.execute("ALTER TABLE usuarios ADD COLUMN trial_ends_at TEXT DEFAULT ''")
        db.execute("ALTER TABLE usuarios ADD COLUMN stripe_customer_id TEXT DEFAULT ''")
        db.execute("ALTER TABLE usuarios ADD COLUMN stripe_subscription_id TEXT DEFAULT ''")

    try:
        db.execute("SELECT email_verificado FROM usuarios LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE usuarios ADD COLUMN email_verificado INTEGER DEFAULT 0")


def init_db():
    """Crea tablas, indices y ejecuta migraciones. Funciona con ambos backends."""
    db = get_db()

    # Crear tablas
    db.executescript(_SCHEMA_SQL)

    # Migraciones
    if USE_POSTGRES:
        _migrate_pg(db)
    else:
        _migrate_sqlite(db)

    # Indices
    db.executescript(_INDEXES_SQL)

    db.commit()
    db.close()
    logger.info("Base de datos inicializada correctamente (%s)",
                "PostgreSQL" if USE_POSTGRES else "SQLite")
