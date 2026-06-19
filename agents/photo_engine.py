"""
ESTETICAI - Motor Profesional de Mejora de Fotos Reales
========================================================
Pipeline de 6 pasos inspirado en el flujo de trabajo de un fotografo
profesional de estetica y belleza:

  1. LIMPIAR    - Eliminar objetos, cables, distracciones del fondo
  2. ROSTRO     - Restaurar y mejorar detalles faciales preservando textura
  3. ILUMINAR   - Reemplazar luz amateur por iluminacion de estudio profesional
  4. FONDO      - Quitar fondo y reemplazar con entorno profesional
  5. RETOCAR    - Color grading, balance de blancos, retoque fino de piel
  6. CALIDAD    - Upscaling inteligente con difusion (detalle real, no solo agrandar)

Principio fundamental:
  "El mejor retoque es invisible. Corregir errores tecnicos (luz, fondo,
   color) preservando la naturalidad de la piel y el tratamiento.
   Ajusta al punto que se ve bien, luego retrocede un 20%."

Cada paso es opcional. Tres niveles predefinidos:
  - RAPIDO      (2 pasos): fondo + calidad (~$0.04)
  - PROFESIONAL (4 pasos): limpieza + luz + fondo + calidad (~$0.08)
  - PREMIUM     (6 pasos): pipeline completo (~$0.12-0.15)

Modelos utilizados (todos via fal.ai):
  - FLUX Kontext Pro     : edicion por instrucciones en lenguaje natural
  - CodeFormer           : restauracion y mejora facial con control de fidelidad
  - IC-Light V2          : relighting por texto (simular luz de estudio)
  - BiRefNet v2          : eliminacion de fondo (segmentacion)
  - Bria Background Replace : generacion de fondos profesionales
  - Clarity Upscaler     : upscaling con difusion (detalle real)
"""

import os
import logging

logger = logging.getLogger("esteticai.photo")

try:
    import fal_client
    FAL_DISPONIBLE = True
except ImportError:
    FAL_DISPONIBLE = False


# ============================================================
# NIVELES DE PROCESAMIENTO
# ============================================================

NIVELES = {
    "rapido": {
        "nombre": "Rapido",
        "descripcion": "Fondo profesional + mejora de calidad",
        "pasos": ["fondo", "calidad"],
        "coste_aprox": "$0.04",
    },
    "profesional": {
        "nombre": "Profesional",
        "descripcion": "Limpieza + iluminacion de estudio + fondo + calidad",
        "pasos": ["limpiar", "iluminar", "fondo", "calidad"],
        "coste_aprox": "$0.08",
    },
    "premium": {
        "nombre": "Premium",
        "descripcion": "Pipeline completo: limpieza, rostro, luz, fondo, retoque, calidad",
        "pasos": ["limpiar", "rostro", "iluminar", "fondo", "retocar", "calidad"],
        "coste_aprox": "$0.12-0.15",
    },
}


# ============================================================
# CONOCIMIENTO DE FOTOGRAFIA DE ESTETICA
# ============================================================
# Basado en investigacion de flujos de trabajo de fotografos
# profesionales de belleza, clinicas de estetica y spas.
# Cada seccion contiene prompts especializados que replican
# las tecnicas profesionales para cada tipo de foto.

# --- FONDOS PROFESIONALES ---
# Un fotografo de estetica elige el fondo segun el tratamiento,
# la emocion que quiere transmitir, y el uso final de la imagen.
# Cada prompt esta escrito como una direccion de arte detallada.

FONDOS_PROFESIONALES = {
    "clinica_blanco": (
        "Pristine white professional aesthetic clinic interior, "
        "seamless white cyclorama wall curving into white floor, "
        "large diffused overhead softbox creating even shadowless illumination, "
        "minimalist high-end dermatology clinic atmosphere, "
        "out-of-focus modern treatment chair and LED panel in far background, "
        "sterile yet welcoming, no clutter, architectural clean lines, "
        "8K photorealistic interior photography, commercial beauty campaign"
    ),
    "spa_elegante": (
        "Luxury five-star spa treatment suite, warm 3200K ambient lighting, "
        "polished light travertine marble countertop and walls, "
        "single fresh white phalaenopsis orchid in frosted glass vase, "
        "neatly folded premium Egyptian cotton towels in cream, "
        "subtle golden candlelight glow from artisan candle, "
        "eucalyptus sprig and smooth hot stones as accents, "
        "serene premium wellness atmosphere, shallow depth of field, "
        "8K photorealistic luxury hotel spa photography"
    ),
    "neutro_gris": (
        "Professional beauty photography studio, "
        "seamless medium gray Savage paper backdrop (#808080), "
        "two-light setup: large octabox as key light at 45 degrees, "
        "silver reflector fill from opposite side, "
        "clean even tonal gradation from center to edges, "
        "no texture no pattern no distractions, "
        "commercial beauty portrait standard, "
        "8K photorealistic studio photography"
    ),
    "menta_suave": (
        "Soft gradient studio backdrop transitioning from seafoam mint (#A8E6CF) "
        "to pale sage (#E8F5E9), gentle diffused beauty dish lighting from above, "
        "subtle circular bokeh highlights in cool silver tones, "
        "fresh luminous spring atmosphere, "
        "premium skincare brand editorial aesthetic, "
        "Instagram-ready clean modern look, "
        "8K photorealistic beauty campaign photography"
    ),
    "naturaleza_zen": (
        "Serene Japanese-inspired zen wellness garden, "
        "living green moss wall and smooth river pebbles, "
        "warm golden-hour light filtering through sheer linen curtains, "
        "small bamboo water fountain creating gentle movement, "
        "fresh eucalyptus and lavender sprigs as natural accents, "
        "peaceful holistic wellness sanctuary atmosphere, "
        "background in soft bokeh f/2.8 depth of field, "
        "8K photorealistic wellness interior photography"
    ),
    "negro_lujo": (
        "Premium deep matte black seamless backdrop, "
        "dramatic Rembrandt lighting with single beauty dish from 45 degrees, "
        "subtle warm rim light separating subject from background, "
        "deep charcoal gradient vignette at edges, "
        "luxury haute couture beauty editorial aesthetic, "
        "sophisticated exclusive high-fashion feeling, "
        "Vogue Beauty commercial campaign, "
        "8K photorealistic fashion photography"
    ),
    "rosa_suave": (
        "Soft blush pink gradient studio backdrop transitioning from "
        "dusty rose (#DCAE96) to pale ballet pink (#FDE8E0), "
        "warm diffused beauty lighting with golden undertones, "
        "delicate dried pampas grass and pink peonies in soft focus, "
        "feminine luxury skincare brand aesthetic, "
        "warm romantic atmosphere without being saccharine, "
        "8K photorealistic beauty editorial photography"
    ),
    "marmol_lujo": (
        "Polished Calacatta gold marble surface with subtle gray and gold veining, "
        "clean flat surface extending to infinity, "
        "soft overhead diffused lighting creating gentle reflections, "
        "premium cosmetics counter display aesthetic, "
        "high-end beauty brand product photography backdrop, "
        "luxury department store beauty hall atmosphere, "
        "8K photorealistic commercial product photography"
    ),
}

# --- FONDO RECOMENDADO POR TIPO DE TRATAMIENTO ---
# Cada tipo de tratamiento tiene un fondo que maximiza el impacto visual.
# Los fotografos profesionales eligen segun la emocion y el contexto.

FONDO_RECOMENDADO = {
    # Tratamientos clinicos: fondos limpios que transmiten confianza
    "facial": "clinica_blanco",
    "laser": "clinica_blanco",
    "aparatologia": "clinica_blanco",
    "peeling": "clinica_blanco",
    "microblading": "neutro_gris",
    "micropigmentacion": "neutro_gris",
    "antes_despues": "neutro_gris",
    # Tratamientos corporales: fondos neutros que no compiten con el cuerpo
    "corporal": "neutro_gris",
    "reductor": "neutro_gris",
    "reafirmante": "neutro_gris",
    # Bienestar y relajacion: fondos que transmiten calma
    "spa": "spa_elegante",
    "masaje": "spa_elegante",
    "relajacion": "naturaleza_zen",
    "aromaterapia": "naturaleza_zen",
    # Belleza y estetica: fondos frescos y modernos
    "unas": "rosa_suave",
    "manicura": "rosa_suave",
    "pedicura": "rosa_suave",
    "maquillaje": "rosa_suave",
    "belleza": "menta_suave",
    "skincare": "menta_suave",
    # Producto: fondos que realzan el envase
    "producto": "marmol_lujo",
    "cosmetico": "marmol_lujo",
    # Premium / editorial
    "premium": "negro_lujo",
    "editorial": "negro_lujo",
    "default": "clinica_blanco",
}


# --- ILUMINACION PROFESIONAL POR TIPO DE FOTO ---
# Un fotografo de estetica usa distintos esquemas de luz segun
# lo que esta fotografiando. Estos prompts replican esas tecnicas
# para el modelo IC-Light V2.

ILUMINACION_PROFESIONAL = {
    "facial": (
        "Professional beauty dish butterfly lighting from directly above and "
        "slightly in front, large circular catchlight in eyes, "
        "soft diffused fill light from below to eliminate under-eye shadows, "
        "gentle Rembrandt triangle on cheek, even skin illumination, "
        "flattering wraparound light that minimizes pores and texture, "
        "beauty campaign studio lighting setup, 5500K daylight balanced"
    ),
    "corporal": (
        "Two large softbox studio lighting setup, main key light from "
        "45 degrees left creating gentle body contouring, "
        "large silver reflector fill from right side to open shadows, "
        "subtle rim light from behind to separate subject from background, "
        "even diffused illumination that flatters body contours, "
        "commercial beauty photography lighting, 5200K neutral"
    ),
    "manos_unas": (
        "Overhead ring light creating perfectly even shadowless illumination, "
        "macro-style close-up lighting with diffused fill from all sides, "
        "subtle specular highlights on nail surface showing glossy finish, "
        "clean bright light that reveals color accuracy and detail, "
        "professional manicure photography lighting, 5500K daylight"
    ),
    "producto": (
        "Professional product photography two-light setup, "
        "large softbox key light from upper left at 45 degrees, "
        "white bounce card fill from right creating soft graduated shadow, "
        "subtle backlight rim to separate product edges from background, "
        "controlled specular highlights on product surface showing texture, "
        "commercial cosmetics photography, 5600K balanced, sharp clean"
    ),
    "spa_ambiente": (
        "Warm ambient spa atmosphere lighting, soft golden 3000K warm tones, "
        "diffused window light from one side creating gentle shadows, "
        "warm candle-like fill creating cozy intimate atmosphere, "
        "gentle highlights on skin suggesting relaxation and wellbeing, "
        "lifestyle wellness photography natural warm lighting"
    ),
    "antes_despues": (
        "Consistent clinical documentation lighting, "
        "two matched softboxes from 45 degrees on each side, "
        "even flat illumination with minimal shadows for accurate comparison, "
        "neutral 5500K daylight balanced, no color cast, "
        "standardized medical aesthetic photography lighting setup, "
        "clear detail rendering for treatment results documentation"
    ),
    "default": (
        "Professional beauty photography soft studio lighting, "
        "large octabox key light from front-left creating gentle wrap, "
        "fill reflector from opposite side for open shadows, "
        "subtle hair light from behind, flattering even illumination, "
        "beauty editorial standard lighting, 5400K balanced"
    ),
}


# --- RETOQUE DE PIEL POR TIPO ---
# Los prompts de retoque son deliberadamente conservadores.
# Un retocador profesional sigue la regla: "ajusta al punto que
# se ve bien, luego retrocede un 20%". La piel NUNCA debe parecer
# plastica. Se corrigen errores tecnicos, no la biologia.

RETOQUE_PIEL = {
    "facial": (
        "Subtle professional skin retouching: gently even out skin tone, "
        "reduce visible redness and blotchiness while keeping natural flush, "
        "soften minor blemishes and acne marks but preserve every pore "
        "and natural skin texture completely, "
        "correct any yellow or green color cast from fluorescent lighting "
        "to neutral healthy skin tones, "
        "brighten eye whites very subtly, enhance iris detail slightly, "
        "do NOT make skin look plastic smooth or airbrushed, "
        "do NOT alter facial structure or proportions, "
        "the goal is skin that looks healthy and well-lit, not edited"
    ),
    "corporal": (
        "Gentle body skin retouching: even out blotchy skin tone, "
        "reduce visible redness from treatment while preserving real results, "
        "correct fluorescent yellow color cast to clean neutral tones, "
        "soften any bruising edges naturally, "
        "do NOT alter body shape contours or proportions at all, "
        "do NOT smooth skin to unrealistic perfection, "
        "preserve all natural skin texture and details, "
        "medical documentation accuracy is paramount"
    ),
    "manos_unas": (
        "Professional hand and nail photography retouching: "
        "even out skin tone on hands and fingers, "
        "clean up cuticle area very subtly, "
        "enhance nail polish color vibrancy and glossy reflection, "
        "soften any visible dry skin around nails gently, "
        "preserve natural hand texture and knuckle detail, "
        "clean bright accurate color rendering"
    ),
    "producto": (
        "Professional product photography color correction: "
        "ensure accurate true-to-life product colors, "
        "clean any dust spots or fingerprints on packaging, "
        "enhance label text readability and sharpness, "
        "boost subtle specular highlights on product surface, "
        "correct any color temperature inconsistencies, "
        "commercial product photography standard"
    ),
    "antes_despues": (
        "Minimal clinical retouching for before-after documentation: "
        "correct white balance to neutral 5500K for consistency, "
        "ensure matching exposure between before and after images, "
        "remove only environmental distractions not related to treatment, "
        "do NOT smooth skin or alter treatment results in any way, "
        "do NOT change skin tone beyond white balance correction, "
        "medical documentation integrity must be preserved completely"
    ),
    "default": (
        "Subtle professional beauty retouching: "
        "gently even out skin tone and reduce visible redness, "
        "correct color cast from artificial lighting to neutral balanced, "
        "soften minor blemishes while preserving natural skin texture completely, "
        "do NOT make skin look plastic or airbrushed, "
        "the result should look like a well-lit natural photo, not an edited one"
    ),
}


# --- LIMPIEZA DE ESCENA ---
# Instrucciones para FLUX Kontext para limpiar el entorno sin
# alterar al sujeto. Un fotografo profesional revisaria cada
# foto y eliminaria manualmente cada distraccion.

LIMPIEZA_ESCENA = {
    "facial": (
        "Remove any distracting background objects, wires, cables, medical "
        "equipment hoses, paper towels, product bottles, and personal items "
        "visible behind or around the subject. "
        "Clean up any visible clinical clutter. "
        "Remove stray hairs that cross over the face unnaturally. "
        "Do NOT alter the subject's face, skin, or any treatment being shown. "
        "Keep the subject exactly as-is, only clean the environment around them."
    ),
    "corporal": (
        "Remove all distracting background elements: cables, equipment cords, "
        "product bottles, towels on the floor, personal belongings, "
        "wall outlets, switches, and any clinical clutter. "
        "Clean up the treatment bed or surface edges. "
        "Do NOT alter the subject's body, skin texture, or treatment area. "
        "Do NOT change body proportions. Only clean the surrounding environment."
    ),
    "producto": (
        "Remove any dust, fingerprints, scratches, and smudges from the "
        "product surface and packaging. Clean the surface the product sits on. "
        "Remove any distracting items around the product. "
        "Straighten the product label if slightly tilted. "
        "Do NOT alter the product design, colors, or branding."
    ),
    "default": (
        "Remove distracting background objects, cables, clutter, personal items, "
        "and any elements that do not contribute to a clean professional composition. "
        "Clean up the environment around the subject. "
        "Do NOT alter the main subject. Only clean the surroundings."
    ),
}


# ============================================================
# PASO 1: LIMPIAR ESCENA
# ============================================================

def _get_fal_key(api_key=None):
    """Obtiene y configura la clave de fal.ai."""
    key = api_key or os.environ.get("FAL_KEY")
    if key:
        os.environ["FAL_KEY"] = key
    return key


def _modo_demo(paso, image_url):
    """Resultado simulado cuando no hay API key."""
    logger.info("[DEMO] Simulando paso: %s", paso)
    return {"url": image_url, "demo": True}


def limpiar_escena(image_url, tipo="default", api_key=None):
    """
    Elimina objetos distractores del fondo y el entorno usando
    FLUX Kontext Pro (edicion por instrucciones, sin mascara).

    Un fotografo profesional revisaria cada foto y eliminaria
    manualmente cables, botes de producto, objetos personales,
    papel, y cualquier elemento que distraiga del sujeto principal.

    Coste: ~$0.03 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("limpiar_escena", image_url)

    prompt = LIMPIEZA_ESCENA.get(tipo, LIMPIEZA_ESCENA["default"])
    logger.info("[Foto] Paso 1/6: Limpiando escena (%s)...", tipo)

    try:
        result = fal_client.subscribe(
            "fal-ai/flux-pro/kontext",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "guidance_scale": 7.5,
                "num_inference_steps": 28,
                "output_format": "png",
            },
            with_logs=False,
        )
        url = result["images"][0]["url"]
        logger.info("[Foto] Escena limpia: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error limpieza: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 2: MEJORAR ROSTRO
# ============================================================

def mejorar_rostro(image_url, fidelity=0.6, api_key=None):
    """
    Restaura y mejora detalles faciales usando CodeFormer.

    El parametro fidelity (0.0 a 1.0) controla cuanto se modifica:
      - 0.0 = maxima restauracion (puede alterar rasgos)
      - 0.5 = equilibrio ideal para belleza
      - 0.6 = valor recomendado para estetica (mejora sutil + fidelidad)
      - 0.8 = muy conservador (casi sin cambios)
      - 1.0 = sin restauracion

    Un retocador profesional de belleza usa frequency separation para
    trabajar textura y tono por separado. CodeFormer logra algo similar
    de forma automatica: suaviza el tono preservando la textura de los poros.

    Regla de oro: la piel debe parecer bien iluminada, no editada.

    Coste: ~$0.01 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("mejorar_rostro", image_url)

    logger.info("[Foto] Paso 2/6: Mejorando rostro (fidelity=%.1f)...", fidelity)

    try:
        result = fal_client.subscribe(
            "fal-ai/codeformer",
            arguments={
                "image_url": image_url,
                "fidelity": fidelity,
                "upscale_factor": 1,      # No agrandar, solo restaurar
                "face_upscale": True,      # Mejorar detalle facial
                "only_center_face": False, # Procesar todos los rostros
            },
            with_logs=False,
        )
        url = result["image"]["url"]
        logger.info("[Foto] Rostro mejorado: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error rostro: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 3: CORREGIR ILUMINACION
# ============================================================

def corregir_iluminacion(image_url, tipo="default", api_key=None):
    """
    Transforma la iluminacion de la foto usando IC-Light V2.

    Este es el paso que mas diferencia visual produce. Las fotos
    amateur de clinicas de estetica sufren tipicamente de:
      - Luz amarilla de fluorescentes (el error mas comun)
      - Flash directo que aplana el rostro y crea brillos
      - Sombras duras bajo nariz y ojos
      - Contraluz de ventanas

    IC-Light V2 reemplaza toda la iluminacion con un esquema de
    estudio profesional, manteniendo la pose y el contenido de la foto.
    El resultado es como si la misma foto se hubiera tomado en un
    estudio con beauty dish, softboxes y reflectores.

    Coste: ~$0.03 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("corregir_iluminacion", image_url)

    prompt = ILUMINACION_PROFESIONAL.get(tipo, ILUMINACION_PROFESIONAL["default"])
    logger.info("[Foto] Paso 3/6: Corrigiendo iluminacion (%s)...", tipo)

    try:
        result = fal_client.subscribe(
            "fal-ai/iclight-v2",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "initial_latent": "Left Light",  # Luz principal desde la izquierda
                "lowres_denoise": 0.95,           # Alta correccion en baja res
                "highres_denoise": 0.50,          # Conservador en alta res (preservar)
                "enable_hr_fix": True,             # Aplicar fix de alta resolucion
                "output_format": "png",
            },
            with_logs=False,
        )
        url = result["images"][0]["url"]
        logger.info("[Foto] Iluminacion corregida: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error iluminacion: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 4: FONDO PROFESIONAL
# ============================================================

def eliminar_fondo(image_url, api_key=None):
    """
    Elimina el fondo usando BiRefNet v2 en modo Heavy.
    Devuelve imagen con fondo transparente (PNG).

    BiRefNet v2 es superior a rembg y comparable a Bria RMBG 2.0
    en precision de bordes. El modo "General Use (Heavy)" es el
    mas preciso para fotos complejas con pelo, telas finas, y
    bordes difusos como los que aparecen en fotos de tratamientos.

    Coste: ~$0.01 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("eliminar_fondo", image_url)

    logger.info("[Foto] Paso 4a/6: Eliminando fondo...")

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
        url = result["image"]["url"]
        logger.info("[Foto] Fondo eliminado: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error eliminacion fondo: %s", e)
        return {"url": image_url, "error": str(e)}


def reemplazar_fondo(image_url, tipo_fondo="clinica_blanco",
                     prompt_personalizado=None, api_key=None):
    """
    Reemplaza el fondo con un entorno profesional usando Bria.

    Los prompts de fondo estan escritos como direcciones de arte
    detalladas, especificando:
      - El espacio fisico (estudio, clinica, spa)
      - El esquema de iluminacion del fondo
      - Los elementos decorativos (orquideas, marmol, velas)
      - La atmosfera emocional (serenidad, lujo, frescura)
      - La profundidad de campo (fondo desenfocado f/2.8)

    Esto asegura que el fondo generado sea coherente con la
    iluminacion y el ambiente que ya se corrigio en el paso 3.

    Coste: ~$0.02 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("reemplazar_fondo", image_url)

    prompt = prompt_personalizado or FONDOS_PROFESIONALES.get(
        tipo_fondo, FONDOS_PROFESIONALES["clinica_blanco"]
    )
    logger.info("[Foto] Paso 4b/6: Reemplazando fondo (%s)...", tipo_fondo)

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
        url = result["images"][0]["url"]
        logger.info("[Foto] Fondo reemplazado: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error reemplazo fondo: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 5: RETOQUE Y COLOR GRADING
# ============================================================

def retocar_y_colorear(image_url, tipo="default", api_key=None):
    """
    Retoque fino de piel y color grading usando FLUX Kontext Pro.

    Este paso replica lo que un retocador profesional hace despues
    de montar la foto: ajustar el balance de blancos, corregir
    cualquier dominante de color restante, igualar tonos de piel,
    y aplicar un color grading sutil que refuerce la atmosfera.

    Reglas profesionales que siguen los prompts:
      1. Los tonos de piel son un ancla a la realidad. Si se empujan
         demasiado, la piel se ve enfermiza o plastica.
      2. Para estetica medica (antes/despues), NUNCA alterar los
         resultados del tratamiento. Solo normalizar luz y color.
      3. El retoque de piel se limita a errores tecnicos (rojeces
         por flash, brillos por luz directa) no a la biologia.
      4. Color grading sutil: tonos calidos para spa/relajacion,
         neutros para clinica, frescos para skincare.

    Coste: ~$0.03 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("retocar_y_colorear", image_url)

    prompt = RETOQUE_PIEL.get(tipo, RETOQUE_PIEL["default"])
    logger.info("[Foto] Paso 5/6: Retocando y color grading (%s)...", tipo)

    try:
        result = fal_client.subscribe(
            "fal-ai/flux-pro/kontext",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "guidance_scale": 5.0,      # Bajo: sutileza, no agresividad
                "num_inference_steps": 28,
                "output_format": "png",
            },
            with_logs=False,
        )
        url = result["images"][0]["url"]
        logger.info("[Foto] Retoque completado: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error retoque: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# PASO 6: CALIDAD FINAL
# ============================================================

def mejorar_calidad(image_url, api_key=None):
    """
    Upscaling inteligente con Clarity Upscaler (basado en difusion).

    A diferencia de Crystal Upscaler (que solo interpola pixeles),
    Clarity usa difusion para "alucinar" detalle real: poros de la
    piel, textura del cabello, detalles de producto, fibras de tela.

    Parametros calibrados para fotografia de belleza:
      - creativity=0.35  : anadir detalle sutil sin inventar contenido
      - resemblance=0.75 : alta fidelidad al original
      - prompt           : guia la mejora hacia texturas de belleza

    La regla del upscaling profesional: se hace SIEMPRE al final,
    despues de todos los demas pasos, porque cada paso previo
    puede introducir artefactos que el upscaler amplificaria.

    Coste: ~$0.02 por imagen.
    """
    key = _get_fal_key(api_key)
    if not key or not FAL_DISPONIBLE:
        return _modo_demo("mejorar_calidad", image_url)

    logger.info("[Foto] Paso 6/6: Mejorando calidad final...")

    try:
        result = fal_client.subscribe(
            "fal-ai/clarity-upscaler",
            arguments={
                "image_url": image_url,
                "scale_factor": 2,
                "creativity": 0.35,
                "resemblance": 0.75,
                "prompt": (
                    "professional beauty photography, sharp skin detail with "
                    "visible natural pores, crisp eyelashes, detailed hair strands, "
                    "clean product label text, premium commercial quality, "
                    "8K ultra high definition, subtle natural film grain"
                ),
                "output_format": "png",
            },
            with_logs=False,
        )
        url = result["images"][0]["url"]
        logger.info("[Foto] Calidad final: %s", url)
        return {"url": url, "demo": False}
    except Exception as e:
        logger.warning("[Foto] Error calidad: %s", e)
        return {"url": image_url, "error": str(e)}


# ============================================================
# MAPEO TIPO TRATAMIENTO -> TIPO FOTO
# ============================================================
# La clienta selecciona un tipo de tratamiento en el UI.
# Este mapeo traduce a la categoria fotografica correcta
# para que cada paso use los prompts adecuados.

TIPO_TRATAMIENTO_A_FOTO = {
    # Tratamientos faciales -> prompts de retrato facial
    "facial": "facial",
    "limpieza_facial": "facial",
    "peeling": "facial",
    "microblading": "facial",
    "micropigmentacion": "facial",
    "botox": "facial",
    "acido_hialuronico": "facial",
    "radiofrecuencia_facial": "facial",
    "mesoterapia": "facial",
    "dermapen": "facial",
    # Tratamientos corporales -> prompts de cuerpo
    "corporal": "corporal",
    "reductor": "corporal",
    "reafirmante": "corporal",
    "radiofrecuencia_corporal": "corporal",
    "cavitacion": "corporal",
    "presoterapia": "corporal",
    "criolipolisis": "corporal",
    "masaje": "corporal",
    "drenante": "corporal",
    # Laser y aparatologia -> prompts clinicos
    "laser": "facial",
    "aparatologia": "facial",
    "ipl": "facial",
    "depilacion_laser": "corporal",
    # Spa y relajacion -> prompts de ambiente
    "spa": "spa_ambiente",
    "relajacion": "spa_ambiente",
    "aromaterapia": "spa_ambiente",
    # Manos y unas -> prompts de detalle
    "unas": "manos_unas",
    "manicura": "manos_unas",
    "pedicura": "manos_unas",
    "nail_art": "manos_unas",
    # Producto -> prompts de producto
    "producto": "producto",
    "cosmetico": "producto",
    # Documentacion -> prompts minimos
    "antes_despues": "antes_despues",
}


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def procesar_foto_tratamiento(image_url, opciones=None, api_key=None):
    """
    Pipeline profesional de mejora de fotos de estetica.

    Replica el flujo de trabajo de un fotografo profesional de belleza:
    limpiar, restaurar, iluminar, ambientar, retocar, perfeccionar.

    Parametros:
        image_url : str
            URL de la foto original subida por la clienta.
        opciones : dict
            - nivel: "rapido" | "profesional" | "premium" (default "profesional")
            - tipo_tratamiento: str (default "default")
            - tipo_fondo: str - clave de FONDOS_PROFESIONALES
            - fondo_personalizado: str - prompt libre para el fondo
            - fidelity_rostro: float 0.0-1.0 (default 0.6)
            - eliminar_fondo: bool (default True) - solo para nivel "rapido"
            - mejorar_calidad: bool (default True)
            Opciones legacy (compatibilidad con API anterior):
            - eliminar_fondo, mejorar_calidad (se mapean a nivel "rapido")
        api_key : str
            Clave de fal.ai (usa FAL_KEY si no se proporciona).

    Retorna:
        dict con URLs intermedias, pasos completados, errores, y url_final.
    """
    if opciones is None:
        opciones = {}

    # --- Determinar nivel y pasos ---
    nivel = opciones.get("nivel", "profesional")
    if nivel not in NIVELES:
        nivel = "profesional"

    pasos_a_ejecutar = list(NIVELES[nivel]["pasos"])

    # --- Determinar tipo fotografico ---
    tipo_tratamiento = opciones.get("tipo_tratamiento", "default")
    tipo_foto = TIPO_TRATAMIENTO_A_FOTO.get(tipo_tratamiento, "default")

    # --- Fondo ---
    tipo_fondo = opciones.get("tipo_fondo") or FONDO_RECOMENDADO.get(
        tipo_tratamiento, FONDO_RECOMENDADO.get(tipo_foto, "clinica_blanco")
    )
    fondo_custom = opciones.get("fondo_personalizado")

    # --- Parametros de retoque ---
    fidelity = opciones.get("fidelity_rostro", 0.6)

    # --- Opciones individuales (pueden desactivar pasos especificos) ---
    if not opciones.get("eliminar_fondo", True) and "fondo" in pasos_a_ejecutar:
        pasos_a_ejecutar.remove("fondo")
    if not opciones.get("mejorar_calidad", True) and "calidad" in pasos_a_ejecutar:
        pasos_a_ejecutar.remove("calidad")

    # --- Inicializar resultado ---
    resultado = {
        "original_url": image_url,
        "nivel": nivel,
        "tipo_foto": tipo_foto,
        "tipo_tratamiento": tipo_tratamiento,
        "pasos_planificados": list(pasos_a_ejecutar),
        "pasos_completados": [],
        "urls_intermedias": {},
        "errores": [],
    }
    url_actual = image_url

    logger.info(
        "[Foto] Iniciando pipeline %s (%d pasos) para tipo '%s'",
        nivel.upper(), len(pasos_a_ejecutar), tipo_foto,
    )

    # ---- PASO 1: LIMPIAR ----
    if "limpiar" in pasos_a_ejecutar:
        paso = limpiar_escena(url_actual, tipo=tipo_foto, api_key=api_key)
        if paso.get("error"):
            resultado["errores"].append(f"Limpieza: {paso['error']}")
        elif not paso.get("demo"):
            url_actual = paso["url"]
            resultado["urls_intermedias"]["limpia"] = url_actual
            resultado["pasos_completados"].append("limpiar")

    # ---- PASO 2: ROSTRO ----
    if "rostro" in pasos_a_ejecutar:
        # Solo aplicar mejora facial si la foto es de tipo facial o default
        if tipo_foto in ("facial", "default", "spa_ambiente"):
            paso = mejorar_rostro(url_actual, fidelity=fidelity, api_key=api_key)
            if paso.get("error"):
                resultado["errores"].append(f"Rostro: {paso['error']}")
            elif not paso.get("demo"):
                url_actual = paso["url"]
                resultado["urls_intermedias"]["rostro"] = url_actual
                resultado["pasos_completados"].append("rostro")
        else:
            logger.info("[Foto] Paso rostro omitido (tipo '%s' no es facial)", tipo_foto)

    # ---- PASO 3: ILUMINACION ----
    if "iluminar" in pasos_a_ejecutar:
        paso = corregir_iluminacion(url_actual, tipo=tipo_foto, api_key=api_key)
        if paso.get("error"):
            resultado["errores"].append(f"Iluminacion: {paso['error']}")
        elif not paso.get("demo"):
            url_actual = paso["url"]
            resultado["urls_intermedias"]["iluminada"] = url_actual
            resultado["pasos_completados"].append("iluminar")

    # ---- PASO 4: FONDO ----
    if "fondo" in pasos_a_ejecutar:
        # 4a: Eliminar fondo
        paso_a = eliminar_fondo(url_actual, api_key=api_key)
        if paso_a.get("error"):
            resultado["errores"].append(f"Eliminar fondo: {paso_a['error']}")
        elif not paso_a.get("demo"):
            url_actual = paso_a["url"]
            resultado["urls_intermedias"]["sin_fondo"] = url_actual

        # 4b: Reemplazar con fondo profesional
        paso_b = reemplazar_fondo(
            url_actual,
            tipo_fondo=tipo_fondo,
            prompt_personalizado=fondo_custom,
            api_key=api_key,
        )
        if paso_b.get("error"):
            resultado["errores"].append(f"Reemplazar fondo: {paso_b['error']}")
        elif not paso_b.get("demo"):
            url_actual = paso_b["url"]
            resultado["urls_intermedias"]["con_fondo"] = url_actual
            resultado["tipo_fondo_usado"] = tipo_fondo
            resultado["pasos_completados"].append("fondo")

    # ---- PASO 5: RETOQUE Y COLOR ----
    if "retocar" in pasos_a_ejecutar:
        paso = retocar_y_colorear(url_actual, tipo=tipo_foto, api_key=api_key)
        if paso.get("error"):
            resultado["errores"].append(f"Retoque: {paso['error']}")
        elif not paso.get("demo"):
            url_actual = paso["url"]
            resultado["urls_intermedias"]["retocada"] = url_actual
            resultado["pasos_completados"].append("retocar")

    # ---- PASO 6: CALIDAD FINAL ----
    if "calidad" in pasos_a_ejecutar:
        paso = mejorar_calidad(url_actual, api_key=api_key)
        if paso.get("error"):
            resultado["errores"].append(f"Calidad: {paso['error']}")
        elif not paso.get("demo"):
            url_actual = paso["url"]
            resultado["urls_intermedias"]["calidad_final"] = url_actual
            resultado["pasos_completados"].append("calidad")

    # ---- RESULTADO FINAL ----
    resultado["url_final"] = url_actual
    resultado["total_pasos"] = len(resultado["pasos_completados"])

    # Compatibilidad con API anterior
    resultado["url_mejorada"] = url_actual
    if "sin_fondo" in resultado["urls_intermedias"]:
        resultado["url_sin_fondo"] = resultado["urls_intermedias"]["sin_fondo"]
    if "con_fondo" in resultado["urls_intermedias"]:
        resultado["url_con_fondo"] = resultado["urls_intermedias"]["con_fondo"]

    logger.info(
        "[Foto] Pipeline %s completo: %d/%d pasos OK%s",
        nivel.upper(),
        resultado["total_pasos"],
        len(pasos_a_ejecutar),
        f" ({len(resultado['errores'])} errores)" if resultado["errores"] else "",
    )

    return resultado


# ============================================================
# UTILIDADES PUBLICAS
# ============================================================

def obtener_fondos_disponibles():
    """Devuelve la lista de fondos con nombre legible para el UI."""
    nombres_ui = {
        "clinica_blanco": "Clinica profesional (blanco)",
        "spa_elegante": "Spa elegante (beige dorado)",
        "neutro_gris": "Estudio neutro (gris)",
        "menta_suave": "Menta fresca (verde suave)",
        "naturaleza_zen": "Naturaleza zen (verde)",
        "negro_lujo": "Negro editorial (lujo)",
        "rosa_suave": "Rosa suave (femenino)",
        "marmol_lujo": "Marmol dorado (premium)",
    }
    return {
        key: {
            "nombre": nombres_ui.get(key, key.replace("_", " ").title()),
            "descripcion": FONDOS_PROFESIONALES[key][:80] + "...",
        }
        for key in FONDOS_PROFESIONALES
    }


def obtener_niveles_disponibles():
    """Devuelve los niveles de procesamiento para el UI."""
    return {
        key: {
            "nombre": info["nombre"],
            "descripcion": info["descripcion"],
            "pasos": info["pasos"],
            "coste": info["coste_aprox"],
        }
        for key, info in NIVELES.items()
    }


def subir_imagen_a_fal(file_bytes, filename="foto.jpg"):
    """
    Sube una imagen a fal.ai storage para procesarla.
    Devuelve la URL publica.
    """
    if not FAL_DISPONIBLE:
        return None
    try:
        content_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
        url = fal_client.upload(file_bytes, content_type=content_type)
        logger.info("[Foto] Imagen subida: %s", url)
        return url
    except Exception as e:
        logger.error("[Foto] Error subida: %s", e)
        return None
