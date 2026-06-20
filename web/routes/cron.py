"""
Esteticai - Endpoints CRON
============================
Tareas programadas: trial reminders, engagement, resumen semanal,
backup, cleanup. Protegidos por CRON_SECRET.
"""

import os
import logging
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger("esteticai")
router = APIRouter(tags=["cron"])

CRON_SECRET = os.environ.get("CRON_SECRET", "")


def _check_cron_secret(request: Request):
    """Valida el token CRON_SECRET en la query string."""
    token = request.query_params.get("secret", "")
    if not CRON_SECRET or token != CRON_SECRET:
        raise HTTPException(status_code=404)


@router.get("/cron/trial-reminder")
async def cron_trial_reminder(request: Request):
    """Envia recordatorio a usuarios cuyo trial expira en 2 dias.
    Llamar: GET /cron/trial-reminder?secret=<CRON_SECRET>
    """
    _check_cron_secret(request)

    from web.email_service import enviar_trial_expirando
    from web.db_compat import get_db

    db = get_db()
    ahora = datetime.utcnow()
    limite_min = (ahora + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    limite_max = (ahora + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

    usuarios_trial = db.execute(
        """SELECT id, email, nombre, trial_ends_at FROM usuarios
           WHERE plan = 'trial' AND trial_ends_at > ? AND trial_ends_at <= ?
           AND email_verificado = 1""",
        (limite_min, limite_max)
    ).fetchall()
    db.close()

    enviados = 0
    for u in usuarios_trial:
        try:
            fin = datetime.strptime(u["trial_ends_at"], "%Y-%m-%d %H:%M:%S")
            dias = max(1, (fin - ahora).days)
            if enviar_trial_expirando(u["email"], u["nombre"], dias):
                enviados += 1
        except Exception as e:
            logger.error("Trial reminder failed for user %s: %s", u["id"], e)

    logger.info("Trial reminder cron: %d emails sent out of %d users", enviados, len(usuarios_trial))
    return JSONResponse({"ok": True, "enviados": enviados, "total": len(usuarios_trial)})


@router.get("/cron/engagement")
async def cron_engagement(request: Request):
    """Envia emails de re-engagement a usuarias inactivas (7+ dias).
    Llamar: GET /cron/engagement?secret=<CRON_SECRET>
    """
    _check_cron_secret(request)

    from web.email_service import enviar_reengagement
    from web.db_compat import get_db

    corte_7d = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    corte_30d = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    inactivas = db.execute(
        """SELECT id, email, nombre, ultimo_acceso FROM usuarios
           WHERE ultimo_acceso != '' AND ultimo_acceso < ? AND ultimo_acceso > ?
           AND email_verificado = 1 AND plan != 'free'""",
        (corte_7d, corte_30d)
    ).fetchall()
    db.close()

    enviados = 0
    for u in inactivas:
        try:
            ultimo = datetime.strptime(u["ultimo_acceso"], "%Y-%m-%d %H:%M:%S")
            dias = (datetime.utcnow() - ultimo).days
            if enviar_reengagement(u["email"], u["nombre"], dias):
                enviados += 1
        except Exception as e:
            logger.error("Engagement email failed for user %s: %s", u["id"], e)

    logger.info("Engagement cron: %d emails sent out of %d inactive users", enviados, len(inactivas))
    return JSONResponse({"ok": True, "enviados": enviados, "inactivas": len(inactivas)})


@router.get("/cron/resumen-semanal")
async def cron_resumen_semanal(request: Request):
    """Envia resumen semanal de actividad a todas las usuarias activas.
    Llamar los lunes: GET /cron/resumen-semanal?secret=<CRON_SECRET>
    """
    _check_cron_secret(request)

    from web.email_service import enviar_resumen_semanal
    from web.db_compat import get_db

    ahora = datetime.utcnow()
    hace_7d = (ahora - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    usuarias = db.execute(
        """SELECT id, email, nombre FROM usuarios
           WHERE email_verificado = 1 AND plan != 'free'"""
    ).fetchall()

    enviados = 0
    for u in usuarias:
        try:
            gens = db.execute(
                """SELECT tipo, COUNT(*) as c FROM generaciones
                   WHERE usuario_id = ? AND creado_en > ?
                   GROUP BY tipo""",
                (u["id"], hace_7d)
            ).fetchall()
            stats = {}
            for g in gens:
                t = g["tipo"]
                if t in ("copy",):
                    stats["copys"] = stats.get("copys", 0) + g["c"]
                elif t in ("imagen",):
                    stats["imagenes"] = stats.get("imagenes", 0) + g["c"]
                elif t in ("video",):
                    stats["videos"] = stats.get("videos", 0) + g["c"]
                elif t in ("foto_mejorada",):
                    stats["fotos"] = stats.get("fotos", 0) + g["c"]

            if enviar_resumen_semanal(u["email"], u["nombre"], stats):
                enviados += 1
        except Exception as e:
            logger.error("Weekly summary failed for user %s: %s", u["id"], e)

    db.close()
    logger.info("Weekly summary cron: %d emails sent out of %d users", enviados, len(usuarias))
    return JSONResponse({"ok": True, "enviados": enviados, "total": len(usuarias)})


@router.get("/cron/backup")
async def cron_backup(request: Request):
    """Crea backup de la base de datos.
    Con PostgreSQL, los backups son automaticos del proveedor.
    Con SQLite, crea copia local.
    """
    _check_cron_secret(request)

    from web.db_compat import USE_POSTGRES, DB_PATH

    if USE_POSTGRES:
        return JSONResponse({
            "ok": True,
            "message": "PostgreSQL: backups gestionados por el proveedor",
        })

    import shutil

    backup_dir = DB_PATH.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"esteticai_{timestamp}.db"

    try:
        src_db = sqlite3.connect(str(DB_PATH))
        dst_db = sqlite3.connect(str(backup_path))
        src_db.backup(dst_db)
        dst_db.close()
        src_db.close()

        backups = sorted(backup_dir.glob("esteticai_*.db"))
        while len(backups) > 7:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info("Deleted old backup: %s", oldest.name)

        size_kb = backup_path.stat().st_size // 1024
        logger.info("Backup created: %s (%d KB)", backup_path.name, size_kb)
        return JSONResponse({
            "ok": True, "file": backup_path.name, "size_kb": size_kb,
            "backups_total": len(list(backup_dir.glob("esteticai_*.db"))),
        })

    except Exception as e:
        logger.error("Backup failed: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/cron/cleanup")
async def cron_cleanup(request: Request):
    """Limpia tokens expirados de password_resets y email_verificaciones.
    Llamar: GET /cron/cleanup?secret=<CRON_SECRET>
    """
    _check_cron_secret(request)

    from web.db_compat import get_db

    db = get_db()
    corte = (datetime.utcnow() - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S")

    r1 = db.execute("DELETE FROM password_resets WHERE creado_en < ?", (corte,))
    reset_borrados = r1.rowcount

    r2 = db.execute("DELETE FROM email_verificaciones WHERE creado_en < ?", (corte,))
    verif_borrados = r2.rowcount

    db.commit()
    db.close()

    logger.info("Cleanup cron: deleted %d password_resets, %d email_verificaciones",
                reset_borrados, verif_borrados)
    return JSONResponse({
        "ok": True,
        "password_resets_borrados": reset_borrados,
        "email_verificaciones_borradas": verif_borrados,
    })
