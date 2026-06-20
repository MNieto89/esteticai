"""
Esteticai - Endpoints de Stripe
================================
Checkout, webhook, billing portal. Activar con STRIPE_SECRET_KEY.
"""

import os
import logging

from fastapi import APIRouter, Request, HTTPException
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

logger = logging.getLogger("esteticai")
router = APIRouter(tags=["stripe"])

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_IDS = {
    "starter": os.environ.get("STRIPE_PRICE_STARTER", ""),
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "business": os.environ.get("STRIPE_PRICE_BUSINESS", ""),
}


@router.get("/upgrade", response_class=HTMLResponse)
async def upgrade_page(request: Request):
    from web.app import get_usuario_actual, get_info_plan_usuario, templates, PLANES
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    plan_info = get_info_plan_usuario(user)
    return templates.TemplateResponse(request, "upgrade.html", context={
        "user": user, "plan": plan_info, "planes": PLANES,
        "stripe_activo": bool(STRIPE_SECRET_KEY),
    })


@router.post("/api/crear-checkout")
async def api_crear_checkout(request: Request):
    """Crea una sesion de Stripe Checkout para upgrade de plan."""
    from web.app import get_usuario_actual
    from web.db_compat import get_db

    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)

    if not STRIPE_SECRET_KEY:
        return JSONResponse({
            "error": "El sistema de pagos aún no está configurado. Contacta con hola@esteticai.com para activar tu plan."
        }, status_code=503)

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Datos no validos"}, status_code=400)
    plan_elegido = data.get("plan", "")
    if plan_elegido not in STRIPE_PRICE_IDS or not STRIPE_PRICE_IDS[plan_elegido]:
        return JSONResponse({"error": "Plan no válido"}, status_code=400)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

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
        return JSONResponse({"error": "Stripe no está instalado en el servidor."}, status_code=503)
    except Exception as e:
        logger.error("Stripe checkout failed: %s", e)
        return JSONResponse({"error": "Error al crear la sesión de pago."}, status_code=500)


@router.get("/upgrade/exito", response_class=HTMLResponse)
async def upgrade_exito(request: Request):
    """Pagina de exito tras completar el pago."""
    from web.app import get_usuario_actual, get_info_plan_usuario, templates
    user = get_usuario_actual(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    plan_info = get_info_plan_usuario(user)
    return templates.TemplateResponse(request, "upgrade_exito.html", context={
        "user": user, "plan_nombre": plan_info["plan_nombre"],
    })


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Webhook de Stripe para confirmar pagos y gestionar suscripciones."""
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        return JSONResponse({"error": "No configurado"}, status_code=503)

    from web.db_compat import get_db

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


@router.post("/api/billing-portal")
async def api_billing_portal(request: Request):
    """Crea una sesion de Stripe Billing Portal para autogestion de suscripcion."""
    from web.app import get_usuario_actual, BASE_URL

    user = get_usuario_actual(request)
    if not user:
        return JSONResponse({"error": "No autenticado"}, status_code=401)

    if not STRIPE_SECRET_KEY:
        return JSONResponse({
            "error": "El sistema de pagos aún no está configurado."
        }, status_code=503)

    customer_id = user.get("stripe_customer_id") or ""
    if not customer_id:
        return JSONResponse({
            "error": "No tienes una suscripción activa. Elige un plan primero."
        }, status_code=400)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        base_url = str(request.base_url).rstrip("/")
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{base_url}/dashboard",
        )
        return JSONResponse({"ok": True, "portal_url": session.url})
    except ImportError:
        return JSONResponse({"error": "Stripe no está instalado."}, status_code=503)
    except Exception as e:
        logger.error("Stripe billing portal failed: %s", e)
        return JSONResponse({"error": "Error al abrir el portal de facturación."}, status_code=500)
