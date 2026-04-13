#!/usr/bin/env python3
"""
DEMO DE ESTETICAI
==================
MODO DEMO:  python3 demo.py
MODO REAL:  ANTHROPIC_API_KEY=sk-ant-tu-clave python3 demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.brand_profile import PERFIL_DEMO
from agents.content_engine import (
    generar_contenido_semanal, generar_copy_individual,
    formatear_para_consola, exportar_a_json,
)

def main():
    print("\n" + "#" * 60)
    print("#  ESTETICAI - Agente IA para Redes Sociales             #")
    print("#  Especializado en profesionales de la estetica         #")
    print("#" * 60)

    # --- Calendario semanal ---
    print("\n" + "=" * 60)
    print(f"  Generando calendario para: {PERFIL_DEMO['nombre_negocio']}")
    print("=" * 60)

    calendario = generar_contenido_semanal(
        perfil=PERFIL_DEMO,
        contenido_extra=None,  # Pon contexto: "Esta semana promo 2x1 en faciales"
    )
    formatear_para_consola(calendario)
    exportar_a_json(calendario, "output/calendario_semanal.json")

    # --- Copy individual ---
    print("\n" + "=" * 60)
    print("  Copy individual de ejemplo")
    print("=" * 60)

    copy = generar_copy_individual(
        perfil=PERFIL_DEMO,
        tipo_contenido="EDUCATIVO",
        servicio_o_producto="Radiofrecuencia facial",
    )
    print(f"\n{copy.get('copy', '')}")
    print(f"\nHashtags: {' '.join(copy.get('hashtags', []))}")
    print(f"CTA: {copy.get('cta', '')}")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n" + "=" * 60)
        print("  MODO DEMO - Para contenido real con Claude:")
        print("  ANTHROPIC_API_KEY=tu-clave python3 demo.py")
        print("=" * 60)

if __name__ == "__main__":
    main()
