"""
MOTOR DE VIDEO - Esteticai v1.0
=================================
Convierte imagenes generadas en videos para Reels/TikTok usando:
- Kling 3.0 via fal.ai (imagen a video)
- Misma API key de fal.ai que usas para imagenes

REQUISITOS:
  pip3 install fal-client requests
  API key: FAL_KEY (la misma que ya tienes)
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
# PROMPTS DE MOVIMIENTO PARA VIDEOS DE ESTETICA
# Describen QUE MOVIMIENTO hacer con la imagen
# ============================================================

MOVIMIENTOS_VIDEO = {
    "zoom_suave": {
        "prompt": "Slow smooth zoom in, subtle movement, professional cinematic feel, steady camera",
        "descripcion": "Zoom lento y elegante (ideal para productos)",
    },
    "panoramica": {
        "prompt": "Slow panoramic camera pan from left to right, revealing the scene, smooth cinematic movement",
        "descripcion": "Movimiento panoramico lateral (ideal para clinicas)",
    },
    "reveal_dramatico": {
        "prompt": "Dramatic slow reveal with soft focus becoming sharp, cinematic lighting transition, elegant unveiling",
        "descripcion": "Revelacion dramatica (ideal para antes/despues)",
    },
    "ambiente_relajante": {
        "prompt": "Gentle subtle movement, soft particles floating, calming spa atmosphere, peaceful and serene",
        "descripcion": "Ambiente relajante con particulas (ideal para spa)",
    },
    "producto_360": {
        "prompt": "Slow elegant rotation revealing product details, luxury commercial feel, smooth 3D rotation",
        "descripcion": "Rotacion elegante de producto (ideal para productos)",
    },
    "clinica_tour": {
        "prompt": "Smooth walking camera movement through the space, professional interior reveal, warm inviting atmosphere",
        "descripcion": "Recorrido por la clinica (ideal para stories)",
    },
    "close_up": {
        "prompt": "Extreme close-up with shallow depth of field, intimate detail shot, beauty macro photography feel",
        "descripcion": "Primer plano con detalle (ideal para tratamientos)",
    },
}

# Movimientos recomendados segun tipo de publicacion
MOVIMIENTO_RECOMENDADO = {
    "post_feed": "zoom_suave",
    "story": "ambiente_relajante",
    "reel_portada": "reveal_dramatico",
    "carrusel": "zoom_suave",
    "antes_despues": "reveal_dramatico",
    "producto": "producto_360",
}

# Duraciones recomendadas
DURACIONES = {
    "corto": 5,     # Stories, previews
    "medio": 10,    # Posts, reels cortos
    "largo": 15,    # Reels completos
}


def generar_video_desde_imagen(url_imagen, prompt_movimiento=None,
                                tipo_movimiento=None, duracion=5,
                                api_key=None):
    """
    Convierte una imagen generada en un video animado.

    Args:
        url_imagen: URL de la imagen (de fal.ai) o ruta local
        prompt_movimiento: Prompt libre describiendo el movimiento
        tipo_movimiento: Clave de MOVIMIENTOS_VIDEO
        duracion: Duracion en segundos (5, 10, o 15)
        api_key: API key de fal.ai

    Returns:
        dict con url del video y metadata
    """
    key = api_key or os.environ.get("FAL_KEY")

    if not key or not FAL_DISPONIBLE:
        return _demo_video(url_imagen, tipo_movimiento or "zoom_suave")

    # Construir prompt de movimiento
    if prompt_movimiento:
        prompt = prompt_movimiento
    elif tipo_movimiento and tipo_movimiento in MOVIMIENTOS_VIDEO:
        prompt = MOVIMIENTOS_VIDEO[tipo_movimiento]["prompt"]
    else:
        prompt = MOVIMIENTOS_VIDEO["zoom_suave"]["prompt"]

    # Si la imagen es local, no podemos usarla directamente
    if not url_imagen.startswith("http"):
        print(f"[ERROR] Necesito una URL de imagen, no una ruta local.")
        print(f"[INFO] Genera primero la imagen con la opcion 5 y usa la URL.")
        return {"error": "Se necesita URL de imagen, no ruta local"}

    # Limitar duracion
    duracion = min(max(duracion, 5), 15)

    print(f"[Esteticai] Generando video de {duracion}s...")
    print(f"[Esteticai] Movimiento: {prompt[:60]}...")
    print(f"[Esteticai] Esto tarda 1-3 minutos, paciencia...")

    os.environ["FAL_KEY"] = key

    try:
        result = fal_client.subscribe(
            "fal-ai/kling-video/v2/master/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": url_imagen,
                "duration": str(duracion),
                "aspect_ratio": "9:16",
            },
            with_logs=True,
        )

        video_url = result.get("video", {}).get("url", "")
        if not video_url and "video_url" in result:
            video_url = result["video_url"]
        if not video_url:
            # Buscar URL en la respuesta
            for key_name in result:
                val = result[key_name]
                if isinstance(val, str) and val.startswith("http") and (".mp4" in val or "video" in val):
                    video_url = val
                    break
                if isinstance(val, dict):
                    for subkey in val:
                        subval = val[subkey]
                        if isinstance(subval, str) and subval.startswith("http"):
                            video_url = subval
                            break

        if video_url:
            print(f"[Esteticai] Video generado: {video_url}")
        else:
            print(f"[Esteticai] Respuesta de la API: {json.dumps(result, indent=2)[:300]}")

        return {
            "url": video_url or "[No se pudo extraer URL]",
            "prompt_movimiento": prompt,
            "duracion": duracion,
            "imagen_origen": url_imagen,
            "modelo": "kling-v2-master",
            "raw_response": result,
        }

    except Exception as e:
        print(f"[ERROR] Fallo al generar video: {e}")
        return {"error": str(e)}


def generar_video_automatico(servicio, tipo_publicacion, perfil, url_imagen):
    """
    Genera un video automaticamente eligiendo el mejor movimiento
    segun el tipo de publicacion.
    """
    # Elegir movimiento recomendado
    tipo_mov = MOVIMIENTO_RECOMENDADO.get(tipo_publicacion, "zoom_suave")

    # Elegir duracion segun tipo
    duraciones_tipo = {
        "story": 5,
        "post_feed": 5,
        "reel_portada": 5,
        "carrusel": 5,
        "antes_despues": 10,
        "producto": 10,
    }
    duracion = duraciones_tipo.get(tipo_publicacion, 5)

    print(f"\n[Esteticai] Video automatico")
    print(f"[Esteticai] Servicio: {servicio}")
    print(f"[Esteticai] Movimiento: {tipo_mov} ({MOVIMIENTOS_VIDEO[tipo_mov]['descripcion']})")
    print(f"[Esteticai] Duracion: {duracion}s")

    resultado = generar_video_desde_imagen(
        url_imagen=url_imagen,
        tipo_movimiento=tipo_mov,
        duracion=duracion,
    )
    resultado["servicio"] = servicio
    resultado["tipo_publicacion"] = tipo_publicacion
    resultado["tipo_movimiento"] = tipo_mov

    return resultado


def descargar_video(url, nombre_archivo=None, carpeta="output"):
    """Descarga un video generado y lo guarda en disco."""
    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"esteticai_video_{timestamp}.mp4"

    ruta = os.path.join(carpeta, nombre_archivo)
    os.makedirs(carpeta, exist_ok=True)

    try:
        print(f"[Esteticai] Descargando video...")
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(response.content)
        tamano_mb = len(response.content) / (1024 * 1024)
        print(f"[Esteticai] Video guardado en: {ruta} ({tamano_mb:.1f} MB)")
        return ruta
    except Exception as e:
        print(f"[ERROR] No se pudo descargar el video: {e}")
        return None


# ============================================================
# MODO DEMO
# ============================================================

def _demo_video(url_imagen, tipo_movimiento):
    mov = MOVIMIENTOS_VIDEO.get(tipo_movimiento, MOVIMIENTOS_VIDEO["zoom_suave"])
    return {
        "url": "[DEMO] Video no generado - necesitas FAL_KEY con saldo",
        "prompt_movimiento": mov["prompt"],
        "duracion": 5,
        "imagen_origen": url_imagen,
        "modelo": "demo",
        "nota": "Para generar videos reales necesitas saldo en fal.ai"
    }


def listar_movimientos():
    """Muestra todos los movimientos de video disponibles."""
    print("\n--- Movimientos de video disponibles ---\n")
    for nombre, datos in MOVIMIENTOS_VIDEO.items():
        print(f"  {nombre}")
        print(f"    {datos['descripcion']}")
        print()


def listar_duraciones():
    """Muestra las duraciones disponibles."""
    print("\n--- Duraciones ---")
    print("  5s  - Stories, previews rapidos")
    print("  10s - Posts animados, reels cortos")
    print("  15s - Reels completos")
    print()
