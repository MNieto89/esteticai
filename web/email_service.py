"""
ESTETICAI - Servicio de Email
==============================
Envío de emails transaccionales con Resend.
Fallback: log en consola (modo desarrollo sin API key).

Configuración:
- RESEND_API_KEY: API key de Resend (obtener en resend.com)
- EMAIL_FROM: dirección de envío (ej: hola@esteticai.com)

Resend tiene un plan gratuito de 100 emails/día, ideal para empezar.
"""

import os
import logging
import json

logger = logging.getLogger("esteticai.email")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Esteticai <hola@esteticai.com>")
BASE_URL = os.environ.get("BASE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "http://localhost:8000"


def _enviar_con_resend(to: str, subject: str, html: str) -> bool:
    """Envía email usando la API de Resend. Retorna True si OK."""
    try:
        import requests
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            logger.info("Email sent to %s (id: %s)", to, data.get("id"))
            return True
        else:
            logger.error("Resend API error %s: %s", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def enviar_email(to: str, subject: str, html: str) -> bool:
    """Envía un email. Usa Resend si está configurado, si no, logea."""
    if RESEND_API_KEY:
        return _enviar_con_resend(to, subject, html)
    else:
        logger.info(
            "[DEV MODE] Email que se enviaría:\n  To: %s\n  Subject: %s\n  (configura RESEND_API_KEY para enviar de verdad)",
            to, subject
        )
        return False


# ============================================================
# PLANTILLAS DE EMAIL
# ============================================================

def _plantilla_base(contenido: str) -> str:
    """Wrapper HTML con estilos para todos los emails."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8faf9;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8faf9; padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
    <tr><td style="background:linear-gradient(135deg, #62C9B8, #4DB8A7); padding:24px 32px; text-align:center;">
        <h1 style="color:#fff; margin:0; font-size:22px; font-weight:700;">Esteticai</h1>
    </td></tr>
    <tr><td style="padding:32px;">
        {contenido}
    </td></tr>
    <tr><td style="padding:16px 32px; background:#fafafa; text-align:center; font-size:12px; color:#999;">
        &copy; Esteticai &mdash; IA para profesionales de la est&eacute;tica<br>
        <a href="{BASE_URL}/privacidad" style="color:#999;">Pol&iacute;tica de privacidad</a>
    </td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def enviar_reset_password(to: str, nombre: str, reset_link: str) -> bool:
    """Envía email de recuperación de contraseña."""
    url = f"{BASE_URL}{reset_link}"
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">Hola {nombre},</h2>
        <p style="color:#555; line-height:1.6;">
            Has solicitado restablecer tu contrase&ntilde;a en Esteticai.
            Haz clic en el bot&oacute;n de abajo para crear una nueva:
        </p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{url}"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Restablecer contrase&ntilde;a
            </a>
        </div>
        <p style="color:#999; font-size:13px; line-height:1.5;">
            Este enlace expira en 1 hora. Si no solicitaste este cambio, puedes ignorar este email.
        </p>
        <p style="color:#ccc; font-size:11px; word-break:break-all;">
            Si el bot&oacute;n no funciona, copia este enlace:<br>{url}
        </p>
    """)
    return enviar_email(to, "Restablecer tu contrase\u00f1a - Esteticai", html)


def enviar_verificacion_email(to: str, nombre: str, verify_link: str) -> bool:
    """Envía email de verificación de cuenta."""
    url = f"{BASE_URL}{verify_link}"
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">&iexcl;Bienvenida, {nombre}!</h2>
        <p style="color:#555; line-height:1.6;">
            Gracias por registrarte en Esteticai. Solo falta un paso:
            verifica tu email para activar tu cuenta y tu periodo de prueba gratuito de 7 d&iacute;as.
        </p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{url}"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Verificar mi email
            </a>
        </div>
        <p style="color:#999; font-size:13px;">
            Este enlace expira en 24 horas.
        </p>
        <p style="color:#ccc; font-size:11px; word-break:break-all;">
            Si el bot&oacute;n no funciona, copia este enlace:<br>{url}
        </p>
    """)
    return enviar_email(to, "Verifica tu email - Esteticai", html)


def enviar_bienvenida(to: str, nombre: str) -> bool:
    """Envía email de bienvenida tras verificar el email."""
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">&iexcl;Todo listo, {nombre}!</h2>
        <p style="color:#555; line-height:1.6;">
            Tu cuenta est&aacute; verificada y tu periodo de prueba gratuito de 7 d&iacute;as
            ya est&aacute; activo. Tienes acceso a todas las funcionalidades Pro.
        </p>
        <p style="color:#555; line-height:1.6;">
            Con Esteticai puedes crear:
        </p>
        <ul style="color:#555; line-height:2;">
            <li>Copys profesionales con hashtags y CTA</li>
            <li>Im&aacute;genes con IA para tus posts</li>
            <li>Videos para Reels y TikTok</li>
            <li>Composiciones antes/despu&eacute;s</li>
            <li>Calendarios semanales completos</li>
        </ul>
        <div style="text-align:center; margin:28px 0;">
            <a href="{BASE_URL}/dashboard"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Ir al dashboard
            </a>
        </div>
    """)
    return enviar_email(to, "\u00a1Bienvenida a Esteticai!", html)


def enviar_cuenta_eliminada(to: str, nombre: str) -> bool:
    """Envía confirmación de eliminación de cuenta."""
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">Cuenta eliminada</h2>
        <p style="color:#555; line-height:1.6;">
            Hola {nombre}, tu cuenta y todos tus datos han sido eliminados
            de Esteticai de forma permanente, tal como solicitaste.
        </p>
        <p style="color:#555; line-height:1.6;">
            Si cambias de idea en el futuro, siempre puedes crear una cuenta nueva
            en <a href="{BASE_URL}" style="color:#62C9B8;">esteticai.com</a>.
        </p>
        <p style="color:#999; font-size:13px;">
            Gracias por haber confiado en nosotras. &iexcl;Te deseamos lo mejor!
        </p>
    """)
    return enviar_email(to, "Tu cuenta ha sido eliminada - Esteticai", html)


def enviar_trial_expirando(to: str, nombre: str, dias_restantes: int) -> bool:
    """Envía aviso de que el trial está a punto de expirar."""
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">Tu prueba gratuita termina pronto</h2>
        <p style="color:#555; line-height:1.6;">
            Hola {nombre}, te quedan <strong>{dias_restantes} d&iacute;as</strong>
            de tu periodo de prueba en Esteticai.
        </p>
        <p style="color:#555; line-height:1.6;">
            Cuando termine, pasar&aacute;s al plan gratuito con funcionalidades limitadas.
            Para seguir creando contenido profesional sin l&iacute;mites, activa un plan:
        </p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{BASE_URL}/upgrade"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Ver planes y precios
            </a>
        </div>
        <p style="color:#999; font-size:13px;">
            Si tienes dudas, escr&iacute;benos a hola@esteticai.com
        </p>
    """)
    return enviar_email(to, f"Tu prueba gratuita termina en {dias_restantes} d\u00edas - Esteticai", html)


# ============================================================
# EMAILS DE ENGAGEMENT
# ============================================================

def enviar_reengagement(to: str, nombre: str, dias_inactiva: int) -> bool:
    """Email para usuarias inactivas (no acceden hace X dias)."""
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">Te echamos de menos, {nombre}</h2>
        <p style="color:#555; line-height:1.6;">
            Hace <strong>{dias_inactiva} d&iacute;as</strong> que no pasas por Esteticai.
            Tu contenido no se crea solo... &iquest;o s&iacute;?
        </p>
        <p style="color:#555; line-height:1.6;">
            Con la IA de Esteticai puedes tener el contenido de toda la semana
            listo en 15 minutos. Copys, im&aacute;genes, calendarios... todo
            adaptado a tu negocio.
        </p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{BASE_URL}/dashboard"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Volver a crear contenido
            </a>
        </div>
    """)
    return enviar_email(to, f"Hace {dias_inactiva} d\u00edas que no creas contenido - Esteticai", html)


def enviar_resumen_semanal(to: str, nombre: str, stats: dict) -> bool:
    """Resumen semanal de actividad: contenido generado, sugerencias."""
    copys = stats.get("copys", 0)
    imagenes = stats.get("imagenes", 0)
    videos = stats.get("videos", 0)
    fotos = stats.get("fotos", 0)
    total = copys + imagenes + videos + fotos

    if total == 0:
        resumen = """
        <p style="color:#555; line-height:1.6;">
            Esta semana no has generado contenido. Recuerda que puedes crear
            copys, im&aacute;genes y calendarios en minutos con la IA.
        </p>
        """
    else:
        resumen = f"""
        <p style="color:#555; line-height:1.6;">
            Esta semana has creado <strong>{total} contenidos</strong>:
        </p>
        <table style="width:100%; border-collapse:collapse; margin:16px 0;">
            <tr style="border-bottom:1px solid #eee;">
                <td style="padding:8px 0; color:#555;">Copys</td>
                <td style="padding:8px 0; color:#333; font-weight:600; text-align:right;">{copys}</td>
            </tr>
            <tr style="border-bottom:1px solid #eee;">
                <td style="padding:8px 0; color:#555;">Im&aacute;genes</td>
                <td style="padding:8px 0; color:#333; font-weight:600; text-align:right;">{imagenes}</td>
            </tr>
            <tr style="border-bottom:1px solid #eee;">
                <td style="padding:8px 0; color:#555;">Videos</td>
                <td style="padding:8px 0; color:#333; font-weight:600; text-align:right;">{videos}</td>
            </tr>
            <tr>
                <td style="padding:8px 0; color:#555;">Fotos mejoradas</td>
                <td style="padding:8px 0; color:#333; font-weight:600; text-align:right;">{fotos}</td>
            </tr>
        </table>
        """

    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">Tu semana en Esteticai</h2>
        <p style="color:#555; line-height:1.6;">Hola {nombre}, aqu&iacute; tienes tu resumen:</p>
        {resumen}
        <div style="text-align:center; margin:28px 0;">
            <a href="{BASE_URL}/dashboard"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Seguir creando
            </a>
        </div>
    """)
    return enviar_email(to, "Tu resumen semanal - Esteticai", html)


def enviar_tip_contenido(to: str, nombre: str, tip_titulo: str, tip_texto: str) -> bool:
    """Email con un consejo de contenido para redes sociales."""
    html = _plantilla_base(f"""
        <h2 style="color:#333; margin-top:0;">{tip_titulo}</h2>
        <p style="color:#555; line-height:1.6;">Hola {nombre},</p>
        <p style="color:#555; line-height:1.6;">{tip_texto}</p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{BASE_URL}/dashboard"
               style="display:inline-block; background:#62C9B8; color:#fff; padding:14px 32px;
                      border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;">
                Probar ahora en Esteticai
            </a>
        </div>
        <p style="color:#999; font-size:13px;">
            Si no quieres recibir estos consejos, puedes desactivarlos en tu configuraci&oacute;n.
        </p>
    """)
    return enviar_email(to, f"{tip_titulo} - Esteticai", html)
