"""
ESTETICAI - Motor de Mejora de Fotos Reales
============================================
Pipeline de procesamiento para fotos de tratamientos:
1. Eliminar fondo (BiRefNet v2)
2. Reemplazar fondo con uno profesional (Bria Background Replace)
3. Mejorar calidad y luz (Crystal Upscaler)

Cada paso es opcional y configurable por la clienta.
"""

import os
import json
import base64
import requests

try:
    import fal_client
    FAL_DISPONIBLE = True
except ImportError:
    FAL_DISPONIBLE = False


# ============================================================
# FONDOS PROFESIONALES PARA ESTETICA
# ============================================================

FONDOS_PROFESIONALES = {
    "clinica_blanco": (
        "Clean white professional medical aesthetic clinic background, "
        "soft diffused overhead studio lighting, minimalist high-end beauty clinic, "
        "subtle shadow on pristine white floor, clinical yet welcoming, "
        "out-of-focus treatment bed or equipment in background, photorealistic"
    ),
    "spa_elegante": (
        "Elegant luxury spa treatment room background, warm ambient lighting, "
        "light beige and cream marble surfaces, fresh white orchid arrangement "
        "in soft focus, folded luxury towels, serene and premium atmosphere, "
        "candle glow, photorealistic interior design"
    ),
    "neutro_gris": (
        "Professional beauty portrait photography studio, "
        "smooth neutral gray seamless paper backdrop, "
        "Rembrandt-style soft even key lighting with fill, "
        "clean modern commercial look, no distractions, photorealistic"
    ),
    "rosa_suave": (
        "Soft dusty pink and blush gradient studio background, "
        "gentle diffused studio lighting, feminine beauty brand editorial, "
        "subtle golden bokeh highlights, warm skin-flattering tones, "
        "Instagram-ready aesthetic, photorealistic"
    ),
    "naturaleza_zen": (
        "Serene zen garden spa setting, soft green bamboo and smooth river stones, "
        "warm golden-hour natural light filtering through sheer curtains, "
        "small water feature in background, eucalyptus leaves, "
        "peaceful holistic wellness atmosphere, slightly blurred depth, photorealistic"
    ),
    "dorado_lujo": (
        "Premium golden champagne gradient backdrop, "
        "warm elegant side lighting with soft shimmer, "
        "luxury beauty brand editorial aesthetic, "
        "subtle metallic texture, sophisticated exclusive feeling, "
        "high-fashion beauty commercial, photorealistic"
    ),
}

# Fondos recomendados segun tipo de tratamiento
FONDO_RECOMENDADO = {
    "facial": "clinica_blanco",
    "corporal": "neutro_gris",
    "laser": "clinica_blanco",
    "spa": "spa_elegante",
    "producto": "rosa_suave",
    "antes_despues": "neutro_gris",
    "unas": "rosa_suave",
    "belleza": "rosa_suave",
    "masaje": "spa_elegante",
    "relajacion": "naturaleza_zen",
    "premium": "dorado_lujo",
    "default": "clinica_blanco",
}


# ============================================================
# PASO 1: ELIMINAR FONDO
# ============================================================

def eliminar_fondo(image_url, api_key=None):
    """
    Elimina el fondo de una imagen usando BiRefNet v2.
    Devuelve la imagen con fondo transparente (PNG).
    Coste: ~$0.01 por imagen.
    """
    key = api_key or os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        print("[MODO DEMO] Simulando eliminacion de fondo")
        return {"url": image_url, "demo": True}

    os.environ["FAL_KEY"] = key
    print("[Esteticai] Paso 1: Eliminando fondo con BiRefNet v2...")

    try:
        result = fal_client.subscribe(
            "fal-ai/birefnet/v2",
            arguments={
                "image_url": image_url,
                "model": "General Use (Heavy)",
                "operating_resolution": "2048x2048",
                "output_format": "png",
                "refine_foreground": True,
            },
            with_logs=False,
        )
        url_sin_fondo = result["image"]["url"]
        print(f"[Esteticai] Fondo eliminado: {url_sin_fondo}")
        return {"url": url_sin_fondo, "demo": False}
    except Exception as e:
        print(f"[ERROR] Fallo al eliminar fondo: {e}")
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 2: REEMPLAZAR FONDO
# ============================================================

def reemplazar_fondo(image_url, tipo_fondo="clinica_blanco",
                     prompt_personalizado=None, api_key=None):
    """
    Reemplaza el fondo con uno profesional generado por IA.
    Usa Bria Background Replace.
    Coste: ~$0.02 por imagen.
    """
    key = api_key or os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        print("[MODO DEMO] Simulando reemplazo de fondo")
        return {"url": image_url, "demo": True}

    os.environ["FAL_KEY"] = key
    prompt = prompt_personalizado or FONDOS_PROFESIONALES.get(
        tipo_fondo, FONDOS_PROFESIONALES["clinica_blanco"]
    )
    print(f"[Esteticai] Paso 2: Reemplazando fondo ({tipo_fondo})...")

    try:
        result = fal_client.subscribe(
            "fal-ai/bria/background/replace",
            arguments={
                "image_url": image_url,
                "prompt": prompt,
                "num_images": 1,
            },
            with_logs=False,
        )
        url_con_fondo = result["images"][0]["url"]
        print(f"[Esteticai] Fondo reemplazado: {url_con_fondo}")
        return {"url": url_con_fondo, "demo": False}
    except Exception as e:
        print(f"[ERROR] Fallo al reemplazar fondo: {e}")
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 3: MEJORAR CALIDAD (UPSCALE + ENHANCE)
# ============================================================

def mejorar_calidad(image_url, api_key=None):
    """
    Mejora la calidad de la imagen: mas nitidez, mejor luz,
    detalles mas claros. Especializado en retratos y piel.
    Usa Crystal Upscaler de ClarityAI.
    Coste: ~$0.016 por megapixel.
    """
    key = api_key or os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        print("[MODO DEMO] Simulando mejora de calidad")
        return {"url": image_url, "demo": True}

    os.environ["FAL_KEY"] = key
    print("[Esteticai] Paso 3: Mejorando calidad con Crystal Upscaler...")

    try:
        result = fal_client.subscribe(
            "clarityai/crystal-upscaler",
            arguments={
                "image_url": image_url,
                "scale_factor": 2,
            },
            with_logs=False,
        )
        url_mejorada = result["image"]["url"]
        print(f"[Esteticai] Calidad mejorada: {url_mejorada}")
        return {"url": url_mejorada, "demo": False}
    except Exception as e:
        print(f"[ERROR] Fallo al mejorar calidad: {e}")
        return {"url": image_url, "error": str(e)}


# ============================================================
# PIPELINE COMPLETO
# ============================================================

def procesar_foto_tratamiento(image_url, opciones=None, api_key=None):
    """
    Pipeline completo de procesamiento de foto de tratamiento.

    Parametros:
        image_url: URL de la foto original subida por la clienta
        opciones: dict con configuracion:
            - eliminar_fondo: bool (default True)
            - tipo_fondo: str - clave de FONDOS_PROFESIONALES (default "clinica_blanco")
            - fondo_personalizado: str - prompt libre para el fondo
            - mejorar_calidad: bool (default True)
            - tipo_tratamiento: str - para recomendar fondo automaticamente
        api_key: clave de fal.ai

    Retorna dict con URLs de cada paso y metadata.
    """
    if opciones is None:
        opciones = {}

    quitar_fondo = opciones.get("eliminar_fondo", True)
    mejorar = opciones.get("mejorar_calidad", True)
    tipo_tratamiento = opciones.get("tipo_tratamiento", "default")
    tipo_fondo = opciones.get("tipo_fondo") or FONDO_RECOMENDADO.get(
        tipo_tratamiento, "clinica_blanco"
    )
    fondo_custom = opciones.get("fondo_personalizado")

    resultado = {
        "original_url": image_url,
        "pasos_completados": [],
        "errores": [],
    }
    url_actual = image_url

    # PASO 1: Eliminar fondo
    if quitar_fondo:
        paso1 = eliminar_fondo(url_actual, api_key=api_key)
        if paso1.get("error"):
            resultado["errores"].append(f"Fondo: {paso1['error']}")
        else:
            url_actual = paso1["url"]
            resultado["url_sin_fondo"] = url_actual
            resultado["pasos_completados"].append("eliminar_fondo")

        # PASO 2: Reemplazar con fondo profesional
        paso2 = reemplazar_fondo(
            url_actual,
            tipo_fondo=tipo_fondo,
            prompt_personalizado=fondo_custom,
            api_key=api_key,
        )
        if paso2.get("error"):
            resultado["errores"].append(f"Reemplazo: {paso2['error']}")
        else:
            url_actual = paso2["url"]
            resultado["url_con_fondo"] = url_actual
            resultado["tipo_fondo"] = tipo_fondo
            resultado["pasos_completados"].append("reemplazar_fondo")

    # PASO 3: Mejorar calidad
    if mejorar:
        paso3 = mejorar_calidad(url_actual, api_key=api_key)
        if paso3.get("error"):
            resultado["errores"].append(f"Calidad: {paso3['error']}")
        else:
            url_actual = paso3["url"]
            resultado["url_mejorada"] = url_actual
            resultado["pasos_completados"].append("mejorar_calidad")

    resultado["url_final"] = url_actual
    resultado["total_pasos"] = len(resultado["pasos_completados"])

    print(f"\n[Esteticai] Procesamiento completo: {resultado['total_pasos']} pasos")
    if resultado["errores"]:
        print(f"[Esteticai] Errores: {resultado['errores']}")

    return resultado


# ============================================================
# UTILIDADES
# ============================================================

def obtener_fondos_disponibles():
    """Devuelve la lista de fondos disponibles para mostrar en el UI."""
    return {
        key: {
            "nombre": key.replace("_", " ").title(),
            "descripcion": prompt[:60] + "..."
        }
        for key, prompt in FONDOS_PROFESIONALES.items()
    }


def subir_imagen_a_fal(file_bytes, filename="foto.jpg"):
    """
    Sube una imagen local a fal.ai storage para poder procesarla.
    Devuelve la URL publica de la imagen.
    """
    if not FAL_DISPONIBLE:
        return None
    try:
        url = fal_client.upload(file_bytes, content_type="image/jpeg")
        print(f"[Esteticai] Imagen subida: {url}")
        return url
    except Exception as e:
        print(f"[ERROR] Fallo al subir imagen: {e}")
        return None
