"""
MODULO DE PROMOS Y EVENTOS - Esteticai
Genera contenido para promociones, fechas clave y estrategia mensual.
"""

import json
import os
from datetime import datetime

try:
    from anthropic import Anthropic
    ANTHROPIC_DISPONIBLE = True
except ImportError:
    ANTHROPIC_DISPONIBLE = False

from agents.content_engine import SYSTEM_PROMPT

FECHAS_CLAVE = {
    "enero": ["Ano nuevo - propositos de cuidado personal", "Rebajas de enero"],
    "febrero": ["San Valentin - regala belleza", "Carnaval - maquillaje especial"],
    "marzo": ["Dia de la Mujer (8M)", "Inicio primavera - preparar piel"],
    "abril": ["Semana Santa - tratamientos express", "Preparacion verano empieza"],
    "mayo": ["Dia de la Madre", "Operacion bikini arranca"],
    "junio": ["Operacion bikini fuerte", "Bodas - novias", "Inicio verano"],
    "julio": ["Proteccion solar", "Tratamientos post-sol", "Rebajas verano"],
    "agosto": ["Reparar piel del sol", "Vuelta al cole se acerca"],
    "septiembre": ["Vuelta a la rutina - renueva tu piel"],
    "octubre": ["Halloween - maquillaje", "Otono - hidratacion profunda"],
    "noviembre": ["Black Friday", "Preparacion Navidad"],
    "diciembre": ["Navidad - packs regalo", "Nochevieja - brilla", "Tarjetas regalo"],
}

PROMPT_PROMO = """Genera contenido promocional para redes sociales.

REGLAS ESPECIALES PARA PROMOS:
1. Transmite URGENCIA sin parecer spam ni teletienda.
2. Evita cliches como "oferta irresistible" o "no te lo pierdas".
3. Explica el VALOR del servicio, no solo el descuento.
4. Incluye condiciones claras (fechas, limitaciones).
5. Genera 3 variaciones: feed, stories, y texto para bio.

Responde en JSON:
{
  "post_feed": {
    "copy": "...", "hashtags": ["..."], "cta": "...",
    "formato": "foto/carrusel/reel",
    "nota_visual": "Descripcion de la imagen/video ideal"
  },
  "story": {
    "slide_1": "Gancho",
    "slide_2": "Detalle",
    "slide_3": "CTA",
    "nota_visual": "..."
  },
  "texto_bio": "Texto corto para bio durante la promo",
  "consejo": "Tip para maximizar el resultado de esta promo"
}
Solo JSON."""

PROMPT_ESTRATEGIA_MENSUAL = """Genera estrategia de contenido mensual completa.
Planifica 4 semanas con:
- Un TEMA central por semana
- Tipos de contenido distribuidos estrategicamente
- Progresion: semana 1 educa, semana 2 inspira, semana 3 vende, semana 4 conecta
- Fechas especiales integradas

Responde en JSON:
{
  "mes": "...", "objetivo_del_mes": "...",
  "semanas": [
    {
      "numero": 1, "tema": "...", "objetivo": "educar",
      "publicaciones": [
        {"dia": "Lunes", "tipo_contenido": "EDUCATIVO", "formato": "carrusel",
         "idea": "...", "servicio_relacionado": "..."}
      ],
      "nota_estrategica": "..."
    }
  ],
  "fechas_especiales_del_mes": ["..."],
  "kpis_objetivo": {"seguidores_nuevos": "X-Y", "engagement_rate": "X%", "dms_recibidos": "X-Y"},
  "consejo_del_mes": "..."
}
Solo JSON."""


def generar_promo(perfil, tipo_promo, detalles, api_key=None):
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key or not ANTHROPIC_DISPONIBLE:
        return _demo_promo(perfil, tipo_promo, detalles)

    client = Anthropic(api_key=key)
    prompt = f"""Genera contenido promocional para:
NEGOCIO: {perfil['nombre_negocio']} ({perfil['tipo_negocio']})
TONO: {perfil['tono']}
TIPO DE PROMO: {tipo_promo}
DETALLES: {detalles}
PUBLICO: {perfil['publico']}
INSTAGRAM: {perfil.get('instagram_handle', '')}

{PROMPT_PROMO}"""

    print(f"[Esteticai] Generando promo: {tipo_promo}...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=2000,
        system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error": "No se pudo parsear", "respuesta_cruda": texto}


def generar_estrategia_mensual(perfil, mes=None, contexto_extra=None, api_key=None):
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    meses_lista = ["enero","febrero","marzo","abril","mayo","junio",
                   "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    if mes is None:
        mes = meses_lista[datetime.now().month - 1]
    fechas = FECHAS_CLAVE.get(mes.lower(), [])

    if not key or not ANTHROPIC_DISPONIBLE:
        return _demo_estrategia(perfil, mes, fechas)

    client = Anthropic(api_key=key)
    prompt = f"""Genera la estrategia de contenido mensual para:
NEGOCIO: {perfil['nombre_negocio']} ({perfil['tipo_negocio']})
TONO: {perfil['tono']}
SERVICIOS: {', '.join(perfil['servicios'])}
PRODUCTOS: {', '.join(perfil['productos']) if perfil['productos'] else 'No vende productos'}
PUBLICO: {perfil['publico']}
MES: {mes.capitalize()}
FECHAS CLAVE: {', '.join(fechas) if fechas else 'Ninguna especial'}
"""
    if contexto_extra:
        prompt += f"\nCONTEXTO: {contexto_extra}\n"
    prompt += f"\n{PROMPT_ESTRATEGIA_MENSUAL}"

    print(f"[Esteticai] Generando estrategia de {mes}...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=4000,
        system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error": "No se pudo parsear", "respuesta_cruda": texto}


def sugerir_fechas_clave(mes=None):
    meses_lista = ["enero","febrero","marzo","abril","mayo","junio",
                   "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    if mes is None:
        mes = meses_lista[datetime.now().month - 1]
    return {"mes": mes, "fechas_clave": FECHAS_CLAVE.get(mes.lower(), ["No hay fechas registradas"])}


def _demo_promo(perfil, tipo_promo, detalles):
    nombre = perfil["nombre_negocio"]
    return {
        "post_feed": {
            "copy": f"Esta semana en {nombre} tenemos algo especial.\n\n{detalles}\n\nNo es una promo mas. Queremos que pruebes lo que hacemos y vuelvas porque te encanto.\n\nPlazas limitadas. Reserva antes del domingo.",
            "hashtags": ["#promo", "#estetica", "#cuidadodelapiel", "#ofertalimitada", "#belleza"],
            "cta": "DM con QUIERO para reservar", "formato": "carrusel",
            "nota_visual": "Slide 1: oferta en grande. Slide 2: detalle. Slide 3: como reservar."
        },
        "story": {
            "slide_1": "Tengo algo que contarte...",
            "slide_2": f"{detalles}\nSolo esta semana. Plazas limitadas.",
            "slide_3": "Escribe QUIERO por DM. Corre que vuelan.",
            "nota_visual": "Fondo con color de marca, texto grande."
        },
        "texto_bio": f"PROMO - {detalles.split('.')[0] if '.' in detalles else detalles[:50]} - DM para reservar",
        "consejo": "Publica lunes 19:00, recuerda miercoles en stories, ultimo aviso viernes."
    }

def _demo_estrategia(perfil, mes, fechas):
    nombre = perfil["nombre_negocio"]
    s1 = perfil["servicios"][0] if perfil["servicios"] else "Facial"
    s2 = perfil["servicios"][1] if len(perfil["servicios"]) > 1 else "Corporal"
    return {
        "mes": mes.capitalize(),
        "objetivo_del_mes": f"Posicionar a {nombre} como experta y captar 10 nuevas consultas",
        "semanas": [
            {"numero": 1, "tema": f"La verdad sobre {s1.lower()}", "objetivo": "educar",
             "publicaciones": [
                 {"dia": "Lunes", "tipo_contenido": "EDUCATIVO", "formato": "carrusel", "idea": f"5 mitos sobre {s1.lower()}", "servicio_relacionado": s1},
                 {"dia": "Miercoles", "tipo_contenido": "DETRAS_DE_CAMARAS", "formato": "reel", "idea": "Asi preparamos una sesion", "servicio_relacionado": s1},
                 {"dia": "Viernes", "tipo_contenido": "EDUCATIVO", "formato": "reel", "idea": "Tip de cuidado en casa", "servicio_relacionado": s1},
             ], "nota_estrategica": "Semana educativa para generar autoridad"},
            {"numero": 2, "tema": "Resultados que hablan", "objetivo": "inspirar",
             "publicaciones": [
                 {"dia": "Lunes", "tipo_contenido": "ANTES_DESPUES", "formato": "reel", "idea": "Transformacion real", "servicio_relacionado": s1},
                 {"dia": "Miercoles", "tipo_contenido": "TESTIMONIO", "formato": "carrusel", "idea": "Historia de una clienta", "servicio_relacionado": s2},
                 {"dia": "Viernes", "tipo_contenido": "PERSONAL", "formato": "foto", "idea": "Por que me dedico a esto", "servicio_relacionado": "Marca"},
             ], "nota_estrategica": "Prueba social para generar deseo"},
            {"numero": 3, "tema": "Tu momento es ahora", "objetivo": "vender",
             "publicaciones": [
                 {"dia": "Lunes", "tipo_contenido": "PRODUCTO", "formato": "foto", "idea": "Servicio estrella", "servicio_relacionado": s1},
                 {"dia": "Miercoles", "tipo_contenido": "PROMOCION", "formato": "carrusel", "idea": "Promo de la semana", "servicio_relacionado": s1},
                 {"dia": "Viernes", "tipo_contenido": "TENDENCIA", "formato": "reel", "idea": "Trend + servicio", "servicio_relacionado": s1},
             ], "nota_estrategica": "Semana de conversion"},
            {"numero": 4, "tema": "Nuestra comunidad", "objetivo": "conectar",
             "publicaciones": [
                 {"dia": "Lunes", "tipo_contenido": "DETRAS_DE_CAMARAS", "formato": "reel", "idea": "Tour por la clinica", "servicio_relacionado": "General"},
                 {"dia": "Miercoles", "tipo_contenido": "EDUCATIVO", "formato": "carrusel", "idea": "FAQ respondidas", "servicio_relacionado": "General"},
                 {"dia": "Viernes", "tipo_contenido": "PERSONAL", "formato": "reel", "idea": "Gracias comunidad", "servicio_relacionado": "Marca"},
             ], "nota_estrategica": "Cerrar mes reforzando relacion"},
        ],
        "fechas_especiales_del_mes": fechas,
        "kpis_objetivo": {"seguidores_nuevos": "50-100", "engagement_rate": "4-6%", "dms_recibidos": "15-30"},
        "consejo_del_mes": "Alterna contenido que educa y contenido que emociona. La gente compra como se va a sentir."
    }


def formatear_promo(promo):
    if "error" in promo:
        print(f"\n[ERROR] {promo['error']}")
        return
    print("\n" + "=" * 60)
    print("  CONTENIDO PROMOCIONAL")
    print("=" * 60)
    pf = promo.get("post_feed", {})
    print(f"\n--- POST FEED ({pf.get('formato','')}) ---\n")
    print(pf.get("copy", ""))
    print(f"\nHashtags: {' '.join(pf.get('hashtags', []))}")
    print(f"CTA: {pf.get('cta', '')}")
    print(f"Visual: {pf.get('nota_visual', '')}")
    st = promo.get("story", {})
    print(f"\n--- STORIES ---")
    print(f"  1: {st.get('slide_1', '')}")
    print(f"  2: {st.get('slide_2', '')}")
    print(f"  3: {st.get('slide_3', '')}")
    print(f"\n--- BIO ---\n  {promo.get('texto_bio', '')}")
    print(f"\n--- CONSEJO ---\n  {promo.get('consejo', '')}")


def formatear_estrategia(estrategia):
    if "error" in estrategia:
        print(f"\n[ERROR] {estrategia['error']}")
        return
    print("\n" + "=" * 60)
    print(f"  ESTRATEGIA: {estrategia.get('mes', '').upper()}")
    print("=" * 60)
    print(f"\nObjetivo: {estrategia.get('objetivo_del_mes', '')}")
    fechas = estrategia.get("fechas_especiales_del_mes", [])
    if fechas:
        print(f"Fechas clave: {', '.join(fechas)}")
    for sem in estrategia.get("semanas", []):
        print(f"\n{'~' * 60}")
        print(f"  SEMANA {sem['numero']}: {sem.get('tema', '')} ({sem.get('objetivo', '')})")
        print(f"{'~' * 60}")
        for pub in sem.get("publicaciones", []):
            print(f"  {pub['dia']:12} | {pub['tipo_contenido']:20} | {pub['formato']:10} | {pub.get('idea', '')}")
        if sem.get("nota_estrategica"):
            print(f"  >> {sem['nota_estrategica']}")
    kpis = estrategia.get("kpis_objetivo", {})
    if kpis:
        print(f"\n--- KPIS ---")
        for k, v in kpis.items():
            print(f"  {k}: {v}")
    c = estrategia.get("consejo_del_mes", "")
    if c:
        print(f"\nConsejo: {c}")
