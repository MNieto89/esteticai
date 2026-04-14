"""
GENERADOR DE PACK COMPLETO - RINGANA
======================================
Genera: perfil + calendario + copies + imagenes
Guarda todo en output/ringana/
"""

import os
import sys
import json
from datetime import datetime

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Configurar API keys si no estan en el entorno ---
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("\n[CONFIG] No se detecta ANTHROPIC_API_KEY en el entorno.")
    key = input("  Pega tu API key de Anthropic (sk-ant-...): ").strip()
    if key:
        os.environ["ANTHROPIC_API_KEY"] = key
        print("  [OK] API key configurada para esta sesion.")

if not os.environ.get("FAL_KEY"):
    print("\n[CONFIG] No se detecta FAL_KEY en el entorno.")
    key = input("  Pega tu API key de fal.ai (o pulsa Enter para saltar imagenes): ").strip()
    if key:
        os.environ["FAL_KEY"] = key
        print("  [OK] FAL_KEY configurada para esta sesion.")

from config.ringana_profile import PERFIL_RINGANA
from agents.content_engine import generar_contenido_semanal, generar_copy_individual
from agents.image_engine import generar_imagen_automatica

# Crear directorio de output
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "ringana")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def paso_1_guardar_perfil():
    """Guarda el perfil de marca como JSON"""
    print("\n" + "=" * 60)
    print("  PASO 1: PERFIL DE MARCA RINGANA")
    print("=" * 60)

    ruta = os.path.join(OUTPUT_DIR, "perfil_ringana.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(PERFIL_RINGANA, f, ensure_ascii=False, indent=2)
    print(f"[OK] Perfil guardado en: {ruta}")
    return PERFIL_RINGANA


def paso_2_generar_calendario(perfil):
    """Genera calendario semanal con Claude"""
    print("\n" + "=" * 60)
    print("  PASO 2: CALENDARIO SEMANAL")
    print("=" * 60)

    contexto_ringana = """CONTEXTO DE MARCA ESPECIFICO:
Ringana es una marca austriaca de cosmetica FRESCA. Su gran diferenciador es que los
productos tienen FECHA DE CADUCIDAD (6 meses sin abrir, 10 semanas abiertos), lo que
demuestra que son realmente naturales y sin conservantes artificiales.

PRODUCTOS ESTRELLA para destacar esta semana:
- FRESH skin perfection (89.90 EUR): crema antiedad con ingredientes frescos
- FRESH hydro serum: hidratacion profunda con acido hialuronico natural
- FRESH eye serum (49.70 EUR): contorno de ojos con resultados visibles

MENSAJES CLAVE:
- "Si tu crema no caduca, preguntate que lleva dentro"
- "Frescura que se nota en tu piel"
- "Ciencia austriaca + naturaleza = resultados reales"
- La frescura como prueba de calidad y pureza
- Sostenibilidad y respeto al medio ambiente

TONO: Cercano, educativo, empoderador. Como una amiga que sabe mucho de cosmetica
natural y te recomienda lo mejor. No agresivo ni MLM-style."""

    calendario = generar_contenido_semanal(
        perfil,
        contenido_extra=contexto_ringana
    )

    ruta = os.path.join(OUTPUT_DIR, "calendario_semanal.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(calendario, f, ensure_ascii=False, indent=2)
    print(f"[OK] Calendario guardado en: {ruta}")

    # Mostrar resumen
    if "calendario_semanal" in calendario:
        for pub in calendario["calendario_semanal"]:
            print(f"  {pub.get('dia', '?'):12s} | {pub.get('red_social', '?'):10s} | {pub.get('tipo_contenido', '?')}")

    return calendario


def paso_3_generar_copies(perfil):
    """Genera 3 copies individuales para productos estrella"""
    print("\n" + "=" * 60)
    print("  PASO 3: COPIES INDIVIDUALES")
    print("=" * 60)

    copies_a_generar = [
        ("PRODUCTO", "FRESH skin perfection - crema antiedad fresca con fecha de caducidad, 89.90 EUR. Ingredientes naturales austriacos."),
        ("EDUCATIVO", "Por que la cosmetica fresca es mejor: explicar que si un producto no caduca es porque lleva conservantes quimicos. Ringana pone fecha de caducidad como prueba de pureza."),
        ("TESTIMONIO", "Resultado de usar FRESH hydro serum durante 4 semanas: piel mas hidratada, luminosa y sin tirantez. Producto vegano y sin parabenos."),
    ]

    resultados = []
    for tipo, descripcion in copies_a_generar:
        print(f"\n  Generando copy: {tipo}...")
        copy = generar_copy_individual(perfil, tipo, descripcion)
        resultados.append({"tipo": tipo, "descripcion": descripcion, "resultado": copy})
        if "copy" in copy:
            print(f"  [OK] Copy generado ({len(copy['copy'])} chars)")
        else:
            print(f"  [OK] Copy generado (modo demo)")

    ruta = os.path.join(OUTPUT_DIR, "copies_individuales.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {len(resultados)} copies guardados en: {ruta}")
    return resultados


def paso_4_generar_imagenes(perfil):
    """Genera 3 imagenes para diferentes productos/servicios"""
    print("\n" + "=" * 60)
    print("  PASO 4: IMAGENES PROFESIONALES")
    print("=" * 60)

    imagenes_a_generar = [
        {
            "servicio": "facial",
            "tipo_publicacion": "producto",
            "descripcion": "Producto FRESH skin perfection de Ringana"
        },
        {
            "servicio": "limpieza facial",
            "tipo_publicacion": "post_feed",
            "descripcion": "Rutina de limpieza facial natural"
        },
        {
            "servicio": "corporal",
            "tipo_publicacion": "story",
            "descripcion": "Cuidado corporal con crema natural"
        },
    ]

    resultados = []
    for i, img_config in enumerate(imagenes_a_generar, 1):
        print(f"\n  [{i}/3] Generando imagen: {img_config['descripcion']}...")
        try:
            resultado = generar_imagen_automatica(
                servicio=img_config["servicio"],
                tipo_publicacion=img_config["tipo_publicacion"],
                perfil=perfil
            )
            resultados.append({
                "config": img_config,
                "resultado": resultado
            })
            if resultado.get("url", "").startswith("http"):
                print(f"  [OK] Imagen generada: {resultado['url'][:80]}...")
            else:
                print(f"  [OK] Imagen generada (modo demo)")
        except Exception as e:
            print(f"  [ERROR] {e}")
            resultados.append({"config": img_config, "error": str(e)})

    ruta = os.path.join(OUTPUT_DIR, "imagenes_generadas.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {len(resultados)} imagenes guardadas en: {ruta}")
    return resultados


def paso_5_compilar_pack(perfil, calendario, copies, imagenes):
    """Compila todo en un pack final"""
    print("\n" + "=" * 60)
    print("  PASO 5: PACK COMPLETO")
    print("=" * 60)

    pack = {
        "marca": "Ringana",
        "generado": datetime.now().isoformat(),
        "generado_por": "Esteticai v1.0",
        "perfil": perfil,
        "calendario_semanal": calendario,
        "copies_individuales": copies,
        "imagenes": imagenes,
        "resumen": {
            "total_publicaciones": len(calendario.get("calendario_semanal", [])),
            "total_copies": len(copies),
            "total_imagenes": len(imagenes),
        }
    }

    ruta = os.path.join(OUTPUT_DIR, "pack_completo_ringana.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Pack completo guardado en: {ruta}")
    print(f"\n  Publicaciones en calendario: {pack['resumen']['total_publicaciones']}")
    print(f"  Copies individuales: {pack['resumen']['total_copies']}")
    print(f"  Imagenes generadas: {pack['resumen']['total_imagenes']}")
    print(f"\n  Archivos en {OUTPUT_DIR}/:")
    for f_name in os.listdir(OUTPUT_DIR):
        f_path = os.path.join(OUTPUT_DIR, f_name)
        size = os.path.getsize(f_path)
        print(f"    {f_name} ({size:,} bytes)")

    return pack


def main():
    print("\n" + "#" * 60)
    print("  ESTETICAI - PACK COMPLETO RINGANA")
    print("  Generando ejemplo de marca...")
    print("#" * 60)

    perfil = paso_1_guardar_perfil()
    calendario = paso_2_generar_calendario(perfil)
    copies = paso_3_generar_copies(perfil)
    imagenes = paso_4_generar_imagenes(perfil)
    pack = paso_5_compilar_pack(perfil, calendario, copies, imagenes)

    print("\n" + "#" * 60)
    print("  PACK COMPLETO GENERADO!")
    print("#" * 60)
    return pack


if __name__ == "__main__":
    main()
