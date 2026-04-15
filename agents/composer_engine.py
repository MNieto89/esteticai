"""
ESTETICAI - Motor de Composicion Antes/Despues
================================================
Crea imagenes profesionales combinando fotos de antes y despues
para publicar directamente en redes sociales.

Plantillas disponibles:
1. side_by_side  - Clasico lado a lado (1080x1080 feed)
2. story         - Vertical apilado (1080x1920 stories)
3. premium       - Con marco editorial y datos del tratamiento
4. diagonal      - Corte diagonal moderno

Todo renderizado con Pillow, coste cero, <1 segundo.
"""

import io
import os
import base64
import requests
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# CONFIGURACION
# ============================================================

# Dimensiones por formato
FORMATOS = {
    "side_by_side": (1080, 1080),
    "story": (1080, 1920),
    "premium": (1080, 1350),
    "diagonal": (1080, 1080),
}

PLANTILLA_INFO = {
    "side_by_side": {
        "nombre": "Clasico lado a lado",
        "descripcion": "Las dos fotos a 50/50, ideal para feed de Instagram",
        "formato_red": "Feed Instagram (1:1)",
    },
    "story": {
        "nombre": "Formato Story",
        "descripcion": "Fotos apiladas arriba/abajo, ideal para Stories y Reels",
        "formato_red": "Story/Reel (9:16)",
    },
    "premium": {
        "nombre": "Marco Premium",
        "descripcion": "Composicion editorial con datos del tratamiento",
        "formato_red": "Feed Instagram (4:5)",
    },
    "diagonal": {
        "nombre": "Corte Diagonal",
        "descripcion": "Division diagonal moderna y llamativa",
        "formato_red": "Feed Instagram (1:1)",
    },
}

# Colores base (se sobreescriben con colores de marca si existen)
COLORES = {
    "rosa": (199, 121, 135),
    "rosa_claro": (253, 241, 243),
    "blanco": (255, 255, 255),
    "negro": (30, 30, 30),
    "gris": (120, 120, 120),
    "gris_claro": (245, 245, 245),
    "dorado": (191, 155, 103),
}


# ============================================================
# UTILIDADES DE IMAGEN
# ============================================================

def descargar_imagen(url):
    """Descarga una imagen desde URL y la devuelve como PIL Image."""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        print(f"[ERROR] No se pudo descargar imagen: {e}")
        return None


def cargar_imagen_bytes(file_bytes):
    """Carga una imagen desde bytes."""
    try:
        return Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        print(f"[ERROR] No se pudo cargar imagen: {e}")
        return None


def ajustar_imagen(img, ancho, alto):
    """Recorta y redimensiona una imagen para que llene exactamente el area dada (crop center)."""
    ratio_destino = ancho / alto
    ratio_original = img.width / img.height

    if ratio_original > ratio_destino:
        # Imagen mas ancha: recortar lados
        nuevo_ancho = int(img.height * ratio_destino)
        offset = (img.width - nuevo_ancho) // 2
        img = img.crop((offset, 0, offset + nuevo_ancho, img.height))
    else:
        # Imagen mas alta: recortar arriba/abajo
        nuevo_alto = int(img.width / ratio_destino)
        offset = (img.height - nuevo_alto) // 2
        img = img.crop((0, offset, img.width, offset + nuevo_alto))

    return img.resize((ancho, alto), Image.LANCZOS)


def obtener_fuente(tamano, bold=False):
    """Intenta cargar una fuente del sistema o usa la default."""
    fuentes_posibles = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
    ]
    for ruta in fuentes_posibles:
        try:
            return ImageFont.truetype(ruta, tamano)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def texto_centrado(draw, texto, x_centro, y, fuente, color):
    """Dibuja texto centrado horizontalmente en una posicion."""
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    ancho_texto = bbox[2] - bbox[0]
    draw.text((x_centro - ancho_texto // 2, y), texto, font=fuente, fill=color)


def imagen_a_bytes(img, formato="JPEG", calidad=92):
    """Convierte PIL Image a bytes."""
    buffer = io.BytesIO()
    if formato == "JPEG":
        img = img.convert("RGB")
    img.save(buffer, format=formato, quality=calidad, optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def imagen_a_base64(img, formato="JPEG"):
    """Convierte PIL Image a base64 data URL."""
    img_bytes = imagen_a_bytes(img, formato)
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    mime = "image/jpeg" if formato == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


# ============================================================
# PLANTILLA 1: SIDE BY SIDE (1080x1080)
# ============================================================

def componer_side_by_side(img_antes, img_despues, config=None):
    """
    Composicion clasica: antes a la izquierda, despues a la derecha.
    Barra superior con titulo, barra inferior con nombre del negocio.
    """
    config = config or {}
    ancho, alto = 1080, 1080

    barra_superior = 80
    barra_inferior = 60
    gap = 6  # Linea divisoria
    zona_fotos_alto = alto - barra_superior - barra_inferior

    # Cada foto ocupa la mitad del ancho
    foto_ancho = (ancho - gap) // 2

    # Ajustar imagenes
    antes = ajustar_imagen(img_antes, foto_ancho, zona_fotos_alto)
    despues = ajustar_imagen(img_despues, foto_ancho, zona_fotos_alto)

    # Crear lienzo
    canvas = Image.new("RGB", (ancho, alto), COLORES["blanco"])

    # Pegar fotos
    canvas.paste(antes, (0, barra_superior))
    canvas.paste(despues, (foto_ancho + gap, barra_superior))

    # Dibujar elementos
    draw = ImageDraw.Draw(canvas)

    # Barra superior - fondo rosa
    color_marca = config.get("color_marca", COLORES["rosa"])
    draw.rectangle([(0, 0), (ancho, barra_superior)], fill=color_marca)

    # Titulo
    tratamiento = config.get("tratamiento", "Resultados reales")
    fuente_titulo = obtener_fuente(28, bold=True)
    texto_centrado(draw, tratamiento.upper(), ancho // 2, 24, fuente_titulo, COLORES["blanco"])

    # Linea divisoria central
    x_linea = foto_ancho
    draw.rectangle([(x_linea, barra_superior), (x_linea + gap, barra_superior + zona_fotos_alto)], fill=COLORES["blanco"])

    # Etiquetas ANTES / DESPUES sobre las fotos
    fuente_label = obtener_fuente(22, bold=True)

    # Fondo semitransparente para etiquetas
    for (texto_label, x_pos) in [("ANTES", foto_ancho // 2), ("DESPUES", foto_ancho + gap + foto_ancho // 2)]:
        bbox = draw.textbbox((0, 0), texto_label, font=fuente_label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad = 12
        lx = x_pos - tw // 2 - pad
        ly = barra_superior + zona_fotos_alto - th - pad * 3
        # Rectangulo con fondo oscuro semitransparente
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [(lx, ly), (lx + tw + pad * 2, ly + th + pad * 2)],
            radius=6, fill=(0, 0, 0, 160)
        )
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(canvas)
        draw.text((lx + pad, ly + pad), texto_label, font=fuente_label, fill=COLORES["blanco"])

    # Barra inferior con nombre del negocio
    draw.rectangle([(0, alto - barra_inferior), (ancho, alto)], fill=COLORES["gris_claro"])
    nombre = config.get("nombre_negocio", "")
    if nombre:
        fuente_marca = obtener_fuente(18, bold=True)
        texto_centrado(draw, nombre, ancho // 2, alto - barra_inferior + 18, fuente_marca, color_marca)

    return canvas


# ============================================================
# PLANTILLA 2: STORY / VERTICAL (1080x1920)
# ============================================================

def componer_story(img_antes, img_despues, config=None):
    """
    Formato vertical para Stories: antes arriba, despues abajo.
    """
    config = config or {}
    ancho, alto = 1080, 1920

    barra_superior = 120
    barra_medio = 80
    barra_inferior = 100
    zona_foto_alto = (alto - barra_superior - barra_medio - barra_inferior) // 2

    antes = ajustar_imagen(img_antes, ancho, zona_foto_alto)
    despues = ajustar_imagen(img_despues, ancho, zona_foto_alto)

    canvas = Image.new("RGB", (ancho, alto), COLORES["blanco"])
    draw = ImageDraw.Draw(canvas)

    color_marca = config.get("color_marca", COLORES["rosa"])

    # Barra superior
    draw.rectangle([(0, 0), (ancho, barra_superior)], fill=color_marca)
    tratamiento = config.get("tratamiento", "Resultados reales")
    fuente_titulo = obtener_fuente(34, bold=True)
    texto_centrado(draw, tratamiento.upper(), ancho // 2, 35, fuente_titulo, COLORES["blanco"])

    # Subtitulo
    sesiones = config.get("sesiones", "")
    if sesiones:
        fuente_sub = obtener_fuente(22)
        texto_centrado(draw, sesiones, ancho // 2, 78, fuente_sub, (255, 255, 255, 200))

    # Foto ANTES
    y_antes = barra_superior
    canvas.paste(antes, (0, y_antes))

    # Barra central con etiqueta
    y_medio = y_antes + zona_foto_alto
    draw.rectangle([(0, y_medio), (ancho, y_medio + barra_medio)], fill=COLORES["blanco"])

    fuente_label = obtener_fuente(26, bold=True)

    # Flecha o indicador
    flecha_texto = "ANTES                                                    DESPUES"
    texto_centrado(draw, flecha_texto, ancho // 2, y_medio + 24, fuente_label, color_marca)

    # Linea decorativa
    draw.line([(100, y_medio + 60), (980, y_medio + 60)], fill=color_marca, width=2)

    # Foto DESPUES
    y_despues = y_medio + barra_medio
    canvas.paste(despues, (0, y_despues))

    # Barra inferior
    y_bottom = y_despues + zona_foto_alto
    draw.rectangle([(0, y_bottom), (ancho, alto)], fill=color_marca)
    nombre = config.get("nombre_negocio", "")
    if nombre:
        fuente_marca = obtener_fuente(24, bold=True)
        texto_centrado(draw, nombre, ancho // 2, y_bottom + 20, fuente_marca, COLORES["blanco"])
    cta = config.get("cta", "Reserva tu cita")
    fuente_cta = obtener_fuente(20)
    texto_centrado(draw, cta, ancho // 2, y_bottom + 55, fuente_cta, (255, 230, 235))

    return canvas


# ============================================================
# PLANTILLA 3: PREMIUM / EDITORIAL (1080x1350)
# ============================================================

def componer_premium(img_antes, img_despues, config=None):
    """
    Marco editorial premium con datos del tratamiento.
    Formato 4:5 (ideal para Instagram feed con mas espacio).
    """
    config = config or {}
    ancho, alto = 1080, 1350

    margen = 40
    barra_superior = 140
    barra_inferior = 160
    gap = 8
    zona_fotos_alto = alto - barra_superior - barra_inferior
    foto_ancho = (ancho - margen * 2 - gap) // 2

    antes = ajustar_imagen(img_antes, foto_ancho, zona_fotos_alto)
    despues = ajustar_imagen(img_despues, foto_ancho, zona_fotos_alto)

    canvas = Image.new("RGB", (ancho, alto), COLORES["blanco"])
    draw = ImageDraw.Draw(canvas)

    color_marca = config.get("color_marca", COLORES["rosa"])

    # Fondo sutil
    draw.rectangle([(0, 0), (ancho, alto)], fill=COLORES["gris_claro"])

    # Marco blanco interior
    draw.rounded_rectangle(
        [(20, 20), (ancho - 20, alto - 20)],
        radius=16, fill=COLORES["blanco"]
    )

    # Titulo y subtitulo
    tratamiento = config.get("tratamiento", "Resultados reales")
    fuente_titulo = obtener_fuente(32, bold=True)
    texto_centrado(draw, tratamiento.upper(), ancho // 2, 45, fuente_titulo, COLORES["negro"])

    # Linea decorativa
    linea_y = 90
    draw.line([(ancho // 2 - 60, linea_y), (ancho // 2 + 60, linea_y)], fill=color_marca, width=3)

    # Sesiones / info extra
    sesiones = config.get("sesiones", "")
    if sesiones:
        fuente_info = obtener_fuente(20)
        texto_centrado(draw, sesiones, ancho // 2, 102, fuente_info, COLORES["gris"])

    # Pegar fotos
    x_antes = margen
    x_despues = margen + foto_ancho + gap
    y_fotos = barra_superior

    canvas.paste(antes, (x_antes, y_fotos))
    canvas.paste(despues, (x_despues, y_fotos))

    # Etiquetas debajo de las fotos
    fuente_label = obtener_fuente(20, bold=True)
    y_label = y_fotos + zona_fotos_alto + 15

    texto_centrado(draw, "ANTES", x_antes + foto_ancho // 2, y_label, fuente_label, COLORES["gris"])
    texto_centrado(draw, "DESPUES", x_despues + foto_ancho // 2, y_label, fuente_label, color_marca)

    # Zona inferior: nombre + CTA
    y_bottom = alto - 90
    nombre = config.get("nombre_negocio", "")
    if nombre:
        fuente_marca = obtener_fuente(22, bold=True)
        texto_centrado(draw, nombre, ancho // 2, y_bottom, fuente_marca, color_marca)

    cta = config.get("cta", "Reserva tu valoracion gratuita")
    fuente_cta = obtener_fuente(18)
    texto_centrado(draw, cta, ancho // 2, y_bottom + 35, fuente_cta, COLORES["gris"])

    return canvas


# ============================================================
# PLANTILLA 4: DIAGONAL (1080x1080)
# ============================================================

def componer_diagonal(img_antes, img_despues, config=None):
    """
    Corte diagonal moderno: antes a la izquierda, despues a la derecha,
    separados por una linea diagonal.
    """
    config = config or {}
    ancho, alto = 1080, 1080

    barra_inferior = 70

    # Ajustar ambas imagenes al tamano completo
    antes = ajustar_imagen(img_antes, ancho, alto - barra_inferior)
    despues = ajustar_imagen(img_despues, ancho, alto - barra_inferior)

    # Crear mascara diagonal para la imagen "despues"
    mask = Image.new("L", (ancho, alto - barra_inferior), 0)
    mask_draw = ImageDraw.Draw(mask)

    # Poligono diagonal: desde el centro-arriba hasta el centro-abajo con inclinacion
    offset_diagonal = 80  # cuanto se inclina
    puntos = [
        (ancho // 2 - offset_diagonal, 0),
        (ancho, 0),
        (ancho, alto - barra_inferior),
        (ancho // 2 + offset_diagonal, alto - barra_inferior),
    ]
    mask_draw.polygon(puntos, fill=255)

    # Componer
    canvas = antes.copy()
    canvas.paste(despues, (0, 0), mask)

    # Expandir para barra inferior
    canvas_final = Image.new("RGB", (ancho, alto), COLORES["blanco"])
    canvas_final.paste(canvas, (0, 0))

    draw = ImageDraw.Draw(canvas_final)

    # Linea diagonal decorativa
    color_marca = config.get("color_marca", COLORES["rosa"])
    grosor_linea = 5
    for i in range(-grosor_linea // 2, grosor_linea // 2 + 1):
        draw.line(
            [(ancho // 2 - offset_diagonal + i, 0),
             (ancho // 2 + offset_diagonal + i, alto - barra_inferior)],
            fill=COLORES["blanco"], width=1
        )

    # Etiquetas ANTES / DESPUES
    fuente_label = obtener_fuente(24, bold=True)

    # Crear overlay para etiquetas semitransparentes
    overlay = Image.new("RGBA", canvas_final.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    for (texto_label, x_pos) in [("ANTES", ancho // 4 - 40), ("DESPUES", ancho * 3 // 4 - 20)]:
        bbox = overlay_draw.textbbox((0, 0), texto_label, font=fuente_label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad = 10
        lx = x_pos - tw // 2 - pad
        ly = alto - barra_inferior - th - pad * 4
        overlay_draw.rounded_rectangle(
            [(lx, ly), (lx + tw + pad * 2, ly + th + pad * 2)],
            radius=6, fill=(0, 0, 0, 150)
        )
    canvas_final = Image.alpha_composite(canvas_final.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas_final)

    for (texto_label, x_pos) in [("ANTES", ancho // 4 - 40), ("DESPUES", ancho * 3 // 4 - 20)]:
        bbox = draw.textbbox((0, 0), texto_label, font=fuente_label)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad = 10
        draw.text((x_pos - tw // 2, alto - barra_inferior - th - pad * 3), texto_label, font=fuente_label, fill=COLORES["blanco"])

    # Barra inferior
    draw.rectangle([(0, alto - barra_inferior), (ancho, alto)], fill=color_marca)

    tratamiento = config.get("tratamiento", "")
    nombre = config.get("nombre_negocio", "")
    texto_inferior = f"{tratamiento}  |  {nombre}" if tratamiento and nombre else tratamiento or nombre
    if texto_inferior:
        fuente_bottom = obtener_fuente(20, bold=True)
        texto_centrado(draw, texto_inferior, ancho // 2, alto - barra_inferior + 22, fuente_bottom, COLORES["blanco"])

    return canvas_final


# ============================================================
# FUNCION PRINCIPAL
# ============================================================

PLANTILLAS = {
    "side_by_side": componer_side_by_side,
    "story": componer_story,
    "premium": componer_premium,
    "diagonal": componer_diagonal,
}


def componer_antes_despues(img_antes_bytes, img_despues_bytes, plantilla="side_by_side", config=None):
    """
    Funcion principal: recibe los bytes de las dos fotos, genera la composicion.

    Parametros:
        img_antes_bytes: bytes de la imagen "antes"
        img_despues_bytes: bytes de la imagen "despues"
        plantilla: str - clave de PLANTILLAS
        config: dict con opciones de personalizacion:
            - tratamiento: str - nombre del tratamiento
            - nombre_negocio: str - nombre del negocio
            - sesiones: str - ej "Resultado de 6 sesiones"
            - cta: str - llamada a la accion
            - color_marca: tuple (R, G, B)

    Retorna dict con:
        - image_base64: str - imagen en base64 data URL
        - image_bytes: bytes - la imagen en JPEG
        - ancho, alto: dimensiones
        - plantilla: nombre de plantilla usada
    """
    config = config or {}

    # Cargar imagenes
    img_antes = cargar_imagen_bytes(img_antes_bytes)
    img_despues = cargar_imagen_bytes(img_despues_bytes)

    if not img_antes:
        return {"error": "No se pudo cargar la foto del ANTES"}
    if not img_despues:
        return {"error": "No se pudo cargar la foto del DESPUES"}

    # Seleccionar plantilla
    func = PLANTILLAS.get(plantilla, componer_side_by_side)
    ancho, alto = FORMATOS.get(plantilla, (1080, 1080))

    print(f"[Esteticai] Componiendo antes/despues con plantilla '{plantilla}' ({ancho}x{alto})...")

    try:
        resultado = func(img_antes, img_despues, config)

        # Generar output
        img_bytes = imagen_a_bytes(resultado, formato="JPEG", calidad=92)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        print(f"[Esteticai] Composicion lista: {len(img_bytes) / 1024:.0f} KB")

        return {
            "image_base64": f"data:image/jpeg;base64,{img_b64}",
            "image_bytes": img_bytes,
            "ancho": ancho,
            "alto": alto,
            "plantilla": plantilla,
            "plantilla_nombre": PLANTILLA_INFO.get(plantilla, {}).get("nombre", plantilla),
            "tamano_kb": round(len(img_bytes) / 1024),
        }
    except Exception as e:
        print(f"[ERROR] Fallo en composicion: {e}")
        return {"error": f"Error al componer la imagen: {str(e)}"}


def obtener_plantillas_disponibles():
    """Devuelve la info de todas las plantillas disponibles."""
    return PLANTILLA_INFO
