"""
MOTOR DE IMAGENES - Esteticai v2.0
====================================
Genera y transforma imagenes para redes sociales usando:
- fal.ai (Flux) para generar imagenes desde cero
- Photoroom para quitar/cambiar fondos de fotos reales
- Sistema de prompts automaticos inteligentes

REQUISITOS:
  pip3 install fal-client requests
  API keys:
    - fal.ai: https://fal.ai/dashboard/keys
    - Photoroom (opcional): https://www.photoroom.com/api
"""

import os
import json
import requests
from datetime import datetime

try:
    import fal_client
    FAL_DISPONIBLE = True
except ImportError:
    FAL_DISPONIBLE = False
    print("[INFO] fal-client no instalado. pip3 install fal-client")


# ============================================================
# BASE DE CONOCIMIENTO DE ESTETICA
# El agente usa esto para generar prompts inteligentes
# sin que la clienta tenga que describir nada
# ============================================================

CONOCIMIENTO_SERVICIOS = {
    "limpieza facial": {
        "elementos_visuales": "clean glowing skin, facial steamer, extraction tools, cotton pads, magnifying lamp",
        "ambiente": "bright clinical room with soft lighting, clean white towels",
        "productos_tipicos": "micellar water, enzyme peel, purifying mask, toner",
        "colores": "white, soft blue, mint green",
        "resultado": "clear radiant skin, minimized pores, healthy glow",
    },
    "antimanchas": {
        "elementos_visuales": "vitamin C serum, brightening cream, IPL device, derma pen",
        "ambiente": "modern treatment room, soft warm lighting",
        "productos_tipicos": "vitamin C serum, niacinamide, kojic acid cream, SPF",
        "colores": "golden, amber, warm white",
        "resultado": "even skin tone, bright complexion, faded dark spots",
    },
    "radiofrecuencia": {
        "elementos_visuales": "radiofrequency handpiece, conductive gel, modern RF device with LED screen",
        "ambiente": "high-tech aesthetic clinic, sleek modern equipment",
        "productos_tipicos": "conductive gel, firming cream, collagen booster serum",
        "colores": "gold, white, rose gold",
        "resultado": "firm lifted skin, defined jawline, reduced wrinkles",
    },
    "mesoterapia": {
        "elementos_visuales": "mesotherapy gun, vitamin cocktail vials, fine needles, treatment bed",
        "ambiente": "clinical setting, sterile and professional",
        "productos_tipicos": "hyaluronic acid vials, vitamin cocktails, amino acid solutions",
        "colores": "clinical blue, white, silver",
        "resultado": "hydrated plump skin, reduced cellulite, body contouring",
    },
    "depilacion laser": {
        "elementos_visuales": "laser handpiece, protective goggles, cooling gel, modern laser machine",
        "ambiente": "clean modern room, professional clinical setting",
        "productos_tipicos": "aloe vera gel, cooling spray, post-treatment cream",
        "colores": "white, ice blue, silver",
        "resultado": "smooth hairless skin, no irritation, clean results",
    },
    "microblading": {
        "elementos_visuales": "microblading pen, pigment cups, eyebrow mapping tools, fine blade",
        "ambiente": "intimate well-lit workspace, precision tools laid out",
        "productos_tipicos": "numbing cream, pigment palette, aftercare balm",
        "colores": "warm brown, nude, rose",
        "resultado": "perfectly shaped natural-looking eyebrows, hair-stroke detail",
    },
    "acido hialuronico": {
        "elementos_visuales": "hyaluronic acid syringe, filler vials, cannula, sterile tray",
        "ambiente": "luxury medical aesthetic clinic, professional and elegant",
        "productos_tipicos": "HA filler syringes, numbing cream, aftercare products",
        "colores": "white, gold, crystal clear",
        "resultado": "plump hydrated skin, restored volume, smooth fine lines",
    },
    "masaje drenante": {
        "elementos_visuales": "massage table, essential oils, wooden massage tools, candles",
        "ambiente": "spa atmosphere, warm dim lighting, relaxing setting",
        "productos_tipicos": "drainage oil, body brush, aromatherapy oils",
        "colores": "warm earth tones, beige, soft green",
        "resultado": "reduced swelling, lighter legs, detoxified body, relaxed feeling",
    },
    "facial": {
        "elementos_visuales": "facial mask, serum dropper, jade roller, treatment bed",
        "ambiente": "spa-like room, soft lighting, calming atmosphere",
        "productos_tipicos": "sheet mask, serum, moisturizer, eye cream",
        "colores": "soft pink, white, lavender",
        "resultado": "glowing hydrated skin, relaxed expression, youthful appearance",
    },
    "corporal": {
        "elementos_visuales": "body wrap, sculpting machine, measuring tape, treatment bed",
        "ambiente": "spacious treatment room, body contouring equipment",
        "productos_tipicos": "slimming cream, firming lotion, body oil",
        "colores": "nude, bronze, warm white",
        "resultado": "toned contoured body, smooth skin, reduced measurements",
    },
}

# Tipos de publicacion con sus estilos fotograficos
ESTILOS_PUBLICACION = {
    "post_feed": {
        "formato": "square",
        "estilo": "polished editorial photography, Instagram-worthy, high contrast, vibrant",
        "composicion": "centered subject, clean background, rule of thirds",
    },
    "story": {
        "formato": "story",
        "estilo": "casual authentic feel, behind-the-scenes vibe, warm tones",
        "composicion": "vertical framing, close-up details, space for text overlay at top and bottom",
    },
    "reel_portada": {
        "formato": "vertical",
        "estilo": "eye-catching thumbnail, bold and dynamic, high energy",
        "composicion": "vertical portrait, strong focal point, dramatic lighting",
    },
    "carrusel": {
        "formato": "square",
        "estilo": "consistent clean aesthetic, educational layout feel, minimal and modern",
        "composicion": "clean background with space for text, consistent color palette across slides",
    },
    "antes_despues": {
        "formato": "square",
        "estilo": "clinical comparison, consistent lighting both sides, professional medical aesthetic",
        "composicion": "split screen or side by side, same angle and lighting, clear difference visible",
    },
    "producto": {
        "formato": "square",
        "estilo": "luxury product photography, commercial quality, beauty magazine aesthetic",
        "composicion": "product centered, complementary props, soft shadows, lifestyle context",
    },
}

# Paletas de color segun tono de marca
PALETAS_TONO = {
    "cercano": {
        "principal": "warm pink and peach",
        "secundario": "soft gold accents",
        "ambiente": "warm, inviting, friendly",
    },
    "profesional": {
        "principal": "clean white and navy blue",
        "secundario": "silver and grey accents",
        "ambiente": "clinical, trustworthy, premium",
    },
    "divertido": {
        "principal": "bright coral and lavender",
        "secundario": "playful mint green accents",
        "ambiente": "energetic, youthful, fresh",
    },
}


def encontrar_servicio(nombre_servicio):
    """Busca en la base de conocimiento el servicio mas parecido."""
    nombre = nombre_servicio.lower().strip()
    # Busqueda exacta
    if nombre in CONOCIMIENTO_SERVICIOS:
        return CONOCIMIENTO_SERVICIOS[nombre]
    # Busqueda parcial
    for clave, datos in CONOCIMIENTO_SERVICIOS.items():
        if clave in nombre or nombre in clave:
            return datos
    # Busqueda por palabras clave
    palabras = nombre.split()
    for palabra in palabras:
        if len(palabra) > 3:
            for clave, datos in CONOCIMIENTO_SERVICIOS.items():
                if palabra in clave:
                    return datos
    # Si no encuentra, devuelve datos genericos de facial
    return CONOCIMIENTO_SERVICIOS["facial"]


TRADUCCION_SERVICIOS = {
    "limpieza facial profunda": "deep facial cleansing",
    "tratamiento antimanchas": "dark spot removal treatment",
    "radiofrecuencia facial": "facial radiofrequency treatment",
    "mesoterapia corporal": "body mesotherapy",
    "depilacion laser": "laser hair removal",
    "microblading de cejas": "eyebrow microblading",
    "tratamiento antiedad con acido hialuronico": "hyaluronic acid anti-aging treatment",
    "masaje drenante linfatico": "lymphatic drainage massage",
    "serum vitamina c": "vitamin C serum",
    "crema hidratante facial": "facial moisturizing cream",
    "contorno de ojos antiojeras": "under-eye dark circle cream",
}


def _traducir_servicio(nombre):
    """Traduce nombre de servicio al ingles para mejores prompts."""
    nombre_lower = nombre.lower().strip()
    if nombre_lower in TRADUCCION_SERVICIOS:
        return TRADUCCION_SERVICIOS[nombre_lower]
    # Busqueda parcial
    for es, en in TRADUCCION_SERVICIOS.items():
        if es in nombre_lower or nombre_lower in es:
            return en
    # Si no encuentra traduccion, devolver en ingles generico
    return f"beauty {nombre} treatment"


def generar_prompt_automatico(servicio, tipo_publicacion, perfil, modo="servicio"):
    """
    GENERADOR INTELIGENTE DE PROMPTS
    La clienta solo elige servicio + tipo de post.
    El agente genera el prompt perfecto automaticamente.
    Prompts cortos y 100% en ingles para mejor calidad.
    """
    conocimiento = encontrar_servicio(servicio)
    estilo_pub = ESTILOS_PUBLICACION.get(tipo_publicacion, ESTILOS_PUBLICACION["post_feed"])
    tono = perfil.get("tono", "cercano")
    paleta = PALETAS_TONO.get(tono, PALETAS_TONO["cercano"])
    servicio_en = _traducir_servicio(servicio)

    if modo == "producto":
        prompt = (
            f"Luxury beauty product photo: {conocimiento['productos_tipicos']}. "
            f"On elegant marble surface, {conocimiento['colores']} tones, "
            f"soft natural light, shallow depth of field, 4K commercial quality."
        )
    elif tipo_publicacion == "antes_despues":
        prompt = (
            f"Before and after split-screen for {servicio_en}. "
            f"Left side: muted skin with visible concerns. "
            f"Right side: glowing skin showing {conocimiento['resultado']}. "
            f"{paleta['principal']} color scheme, clean medical aesthetic."
        )
    elif tipo_publicacion in ("story", "carrusel"):
        prompt = (
            f"Elegant social media background for {servicio_en}. "
            f"{paleta['principal']} gradient, {paleta['secundario']}, "
            f"modern beauty brand aesthetic, space for text overlay, 4K."
        )
    else:
        prompt = (
            f"Professional photo: {servicio_en} in beauty clinic. "
            f"Showing {conocimiento['elementos_visuales']}. "
            f"{conocimiento['ambiente']}. "
            f"{paleta['principal']} palette, 4K, {estilo_pub['estilo'][:40]}."
        )

    return {
        "prompt": prompt,
        "tamano": estilo_pub["formato"],
        "servicio": servicio,
        "tipo_publicacion": tipo_publicacion,
        "modo": modo,
    }


# ============================================================
# PRESETS MANUALES (se mantienen para uso avanzado)
# ============================================================

PROMPTS_ESTETICA = {
    "producto_fondo_blanco": (
        "Professional product photography of {producto}, centered on a clean white background, "
        "soft studio lighting, high-end cosmetic advertisement style, sharp focus, "
        "subtle shadow underneath, 4K quality, commercial photography"
    ),
    "producto_lifestyle": (
        "Elegant lifestyle product photography of {producto}, placed on a marble surface "
        "with green eucalyptus leaves and soft natural light from a window, "
        "beauty magazine aesthetic, warm tones, shallow depth of field, luxurious feel"
    ),
    "producto_natural": (
        "Natural beauty product photography of {producto}, surrounded by fresh flowers "
        "and natural ingredients, soft morning light, organic aesthetic, "
        "clean and minimal composition, pastel tones, spa atmosphere"
    ),
    "tratamiento_ambiente": (
        "Professional aesthetic clinic interior, treatment room with {tratamiento} equipment, "
        "clean modern design, soft ambient lighting, calming atmosphere, "
        "white and light wood tones, medical spa aesthetic, welcoming and luxurious"
    ),
    "antes_despues_plantilla": (
        "Clean split-screen template design for before and after comparison, "
        "minimal design, left side slightly darker, right side brighter and glowing, "
        "beauty clinic aesthetic, text area at top saying 'ANTES | DESPUES', "
        "professional medical aesthetic style"
    ),
    "fondo_stories": (
        "Elegant gradient background for Instagram stories, {color_scheme} color palette, "
        "subtle texture, modern and clean, beauty brand aesthetic, "
        "space for text overlay, soft and luxurious feel"
    ),
    "carrusel_fondo": (
        "Clean minimal background for Instagram carousel slide about {tema}, "
        "soft {color_scheme} gradient, subtle geometric patterns, "
        "professional beauty brand design, space for text, modern aesthetic"
    ),
}


# ============================================================
# FUNCIONES DE GENERACION DE IMAGENES
# ============================================================

def generar_imagen(prompt_personalizado=None, tipo_preset=None,
                   variables=None, tamano="square", api_key=None):
    """Genera una imagen usando fal.ai con modelos Flux."""
    key = api_key or os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        return _demo_imagen(tipo_preset or "producto_lifestyle", variables or {},
                            prompt_override=prompt_personalizado)
    if prompt_personalizado:
        prompt = prompt_personalizado
    elif tipo_preset and tipo_preset in PROMPTS_ESTETICA:
        prompt = PROMPTS_ESTETICA[tipo_preset].format(**(variables or {}))
    else:
        prompt = "Professional beauty product photography, clean white background, studio lighting"
    tamanos = {
        "square": "square",
        "vertical": "portrait_4_3",
        "horizontal": "landscape_4_3",
        "story": "portrait_16_9",
        "reel": "portrait_16_9",
    }
    image_size = tamanos.get(tamano, "square")
    print(f"[Esteticai] Generando imagen con Flux...")
    print(f"[Esteticai] Prompt: {prompt[:100]}...")
    os.environ["FAL_KEY"] = key
    try:
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": 1,
                "safety_tolerance": "5",
            },
            with_logs=False,
        )
        image_url = result["images"][0]["url"]
        print(f"[Esteticai] Imagen generada: {image_url}")
        return {
            "url": image_url,
            "prompt": prompt,
            "tamano": tamano,
            "modelo": "flux-pro-1.1",
        }
    except Exception as e:
        print(f"[ERROR] Fallo al generar imagen: {e}")
        return {"error": str(e)}


def generar_imagen_automatica(servicio, tipo_publicacion, perfil, modo="servicio"):
    """
    FUNCION PRINCIPAL - Generacion automatica sin prompts manuales.
    La clienta elige servicio + tipo de post y listo.
    """
    datos = generar_prompt_automatico(servicio, tipo_publicacion, perfil, modo)
    print(f"\n[Esteticai] Generacion automatica")
    print(f"[Esteticai] Servicio: {servicio}")
    print(f"[Esteticai] Tipo: {tipo_publicacion} | Modo: {modo}")
    resultado = generar_imagen(
        prompt_personalizado=datos["prompt"],
        tamano=datos["tamano"],
    )
    resultado["servicio"] = servicio
    resultado["tipo_publicacion"] = tipo_publicacion
    resultado["modo"] = modo
    return resultado


def generar_pack_automatico(perfil, servicio, tipo_publicacion="post_feed"):
    """
    Genera un pack completo de imagenes para una publicacion.
    Todo automatico basado en el servicio y tipo de post.
    """
    packs_config = {
        "post_feed": [
            {"tipo_pub": "post_feed", "modo": "servicio", "desc": "Foto principal del post"},
        ],
        "carrusel": [
            {"tipo_pub": "carrusel", "modo": "servicio", "desc": "Portada del carrusel"},
            {"tipo_pub": "carrusel", "modo": "producto", "desc": "Slide de productos"},
            {"tipo_pub": "post_feed", "modo": "servicio", "desc": "Slide final con resultado"},
        ],
        "story": [
            {"tipo_pub": "story", "modo": "servicio", "desc": "Fondo para story"},
        ],
        "reel_portada": [
            {"tipo_pub": "reel_portada", "modo": "servicio", "desc": "Portada del reel"},
        ],
        "antes_despues": [
            {"tipo_pub": "antes_despues", "modo": "servicio", "desc": "Plantilla antes/despues"},
        ],
        "producto": [
            {"tipo_pub": "producto", "modo": "producto", "desc": "Foto de producto"},
        ],
    }
    pack = packs_config.get(tipo_publicacion, packs_config["post_feed"])
    print(f"\n[Esteticai] Pack automatico para: {servicio}")
    print(f"[Esteticai] Tipo: {tipo_publicacion} ({len(pack)} imagenes)")
    resultados = []
    for i, item in enumerate(pack, 1):
        print(f"\n--- Imagen {i}/{len(pack)}: {item['desc']} ---")
        resultado = generar_imagen_automatica(
            servicio=servicio,
            tipo_publicacion=item["tipo_pub"],
            perfil=perfil,
            modo=item["modo"],
        )
        resultado["descripcion"] = item["desc"]
        resultados.append(resultado)
        if "url" in resultado and "error" not in resultado:
            nombre = f"pack_{tipo_publicacion}_{i}.png"
            descargar_imagen(resultado["url"], nombre)
    return resultados


def descargar_imagen(url, nombre_archivo=None, carpeta="output"):
    """Descarga una imagen generada y la guarda en disco."""
    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"esteticai_{timestamp}.png"
    ruta = os.path.join(carpeta, nombre_archivo)
    os.makedirs(carpeta, exist_ok=True)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(response.content)
        print(f"[Esteticai] Imagen guardada en: {ruta}")
        return ruta
    except Exception as e:
        print(f"[ERROR] No se pudo descargar: {e}")
        return None


def quitar_fondo(ruta_imagen, api_key=None):
    """Quita el fondo de una foto usando Photoroom API."""
    key = api_key or os.environ.get("PHOTOROOM_API_KEY")
    if not key:
        print("[MODO DEMO] No hay API key de Photoroom.")
        print("[INFO] Para usar: registrate en https://www.photoroom.com/api")
        return _demo_fondo(ruta_imagen)
    print(f"[Esteticai] Quitando fondo de: {ruta_imagen}")
    try:
        with open(ruta_imagen, "rb") as f:
            response = requests.post(
                "https://sdk.photoroom.com/v1/segment",
                headers={"x-api-key": key},
                files={"image_file": f},
            )
        if response.status_code == 200:
            nombre = os.path.splitext(os.path.basename(ruta_imagen))[0]
            ruta_salida = f"output/{nombre}_sin_fondo.png"
            os.makedirs("output", exist_ok=True)
            with open(ruta_salida, "wb") as f:
                f.write(response.content)
            print(f"[Esteticai] Imagen sin fondo: {ruta_salida}")
            return ruta_salida
        else:
            print(f"[ERROR] Photoroom respondio: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# ============================================================
# MODO DEMO
# ============================================================

def _demo_imagen(tipo_preset, variables, prompt_override=None):
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = PROMPTS_ESTETICA.get(tipo_preset, "Professional beauty photography")
        try:
            prompt = prompt.format(**variables)
        except KeyError:
            pass
    return {
        "url": "[DEMO] Imagen no generada - necesitas FAL_KEY",
        "prompt": prompt,
        "tamano": "square",
        "modelo": "demo",
        "nota": "Para generar imagenes reales: export FAL_KEY=tu-clave (de fal.ai/dashboard/keys)"
    }

def _demo_fondo(ruta_imagen):
    print("[DEMO] Simulando eliminacion de fondo")
    return None


def listar_presets():
    """Muestra todos los presets de imagen disponibles."""
    print("\n--- Presets de imagen disponibles ---\n")
    for nombre, plantilla in PROMPTS_ESTETICA.items():
        import re
        vars_found = re.findall(r'\{(\w+)\}', plantilla)
        vars_str = ", ".join(vars_found) if vars_found else "ninguna"
        print(f"  {nombre}")
        print(f"    Variables: {vars_str}")
        print(f"    Prompt: {plantilla[:70]}...")
        print()


def listar_servicios_conocidos():
    """Muestra todos los servicios que el agente conoce."""
    print("\n--- Servicios con conocimiento integrado ---\n")
    for nombre in CONOCIMIENTO_SERVICIOS:
        datos = CONOCIMIENTO_SERVICIOS[nombre]
        print(f"  {nombre.title()}")
        print(f"    Productos tipicos: {datos['productos_tipicos'][:60]}...")
        print(f"    Resultado: {datos['resultado'][:60]}...")
        print()


def listar_tipos_publicacion():
    """Muestra todos los tipos de publicacion disponibles."""
    print("\n--- Tipos de publicacion ---\n")
    tipos = list(ESTILOS_PUBLICACION.keys())
    for i, tipo in enumerate(tipos, 1):
        datos = ESTILOS_PUBLICACION[tipo]
        print(f"  {i}. {tipo}")
        print(f"     Formato: {datos['formato']} | Estilo: {datos['estilo'][:50]}...")
        print()
    return tipos
