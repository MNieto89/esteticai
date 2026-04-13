"""
MOTOR DE CONTENIDO - Esteticai
================================
El cerebro del agente. Usa Claude API para generar contenido
de redes sociales especializado en estetica.
"""

import json
import os
from datetime import datetime, timedelta

try:
    from anthropic import Anthropic
    ANTHROPIC_DISPONIBLE = True
except ImportError:
    ANTHROPIC_DISPONIBLE = False
    print("[INFO] SDK de Anthropic no instalado. Ejecutando en modo demo.")
    print("[INFO] Para usar la API real: pip3 install anthropic")

SYSTEM_PROMPT = """Eres el motor de contenido de Esteticai, un agente de inteligencia artificial \
especializado en crear contenido de redes sociales para profesionales de la estetica \
(clinicas de belleza, centros de estetica, esteticistas autonomas).

TU MISION: Generar contenido que parezca creado por una community manager experta en el \
sector belleza, no por una IA. El contenido debe ser autentico, cercano y orientado a \
generar engagement y atraer clientas nuevas.

REGLAS DE CONTENIDO:
1. NUNCA uses lenguaje generico de marketing. Habla como habla una profesional de estetica \
   a sus seguidoras: cercana, experta pero accesible, apasionada por su trabajo.
2. Cada publicacion debe tener UN objetivo claro: educar, inspirar, vender o conectar.
3. Los copies deben ser concisos pero con gancho. El primer renglon es critico: debe \
   detener el scroll.
4. Usa emojis con moderacion y buen gusto (maximo 3-4 por copy). Nada de parecer spam.
5. Los hashtags deben mezclar: 3-4 de nicho (#esteticafacial, #cuidadodelapiel), \
   2-3 de alcance medio (#bellezanatural, #skincareroutine), y 1-2 generales (#beauty).
6. Adapta el tono al perfil de la marca (profesional, cercano o divertido).
7. SIEMPRE incluye una llamada a la accion clara pero no agresiva.
8. Varia los tipos de contenido: no repitas dos del mismo tipo seguidos.

TIPOS DE CONTENIDO QUE PUEDES GENERAR:
- EDUCATIVO: Tips de cuidado, mitos vs realidad, explicacion de tratamientos
- ANTES/DESPUES: Copy para acompanar fotos/videos de resultados
- TESTIMONIO: Texto para acompanar resenas de clientas
- PRODUCTO: Presentacion de un producto o servicio
- DETRAS_DE_CAMARAS: Dia a dia en la clinica, proceso de un tratamiento
- TENDENCIA: Contenido que sigue tendencias actuales de redes sociales
- PROMOCION: Ofertas, descuentos, packs especiales
- PERSONAL: La profesional habla de si misma, su vocacion, su historia

FORMATO DE RESPUESTA:
Responde SIEMPRE en formato JSON valido con esta estructura exacta:
{
  "calendario_semanal": [
    {
      "dia": "Lunes",
      "fecha": "2026-04-13",
      "hora_publicacion": "19:00",
      "red_social": "instagram",
      "tipo_contenido": "EDUCATIVO",
      "formato": "carrusel",
      "copy": "El texto completo de la publicacion...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "cta": "La llamada a la accion",
      "nota_para_la_clienta": "Instruccion sobre que foto/video usar",
      "objetivo": "educar"
    }
  ],
  "estrategia_semanal": "Un parrafo explicando la estrategia de la semana",
  "consejo_de_la_semana": "Un tip extra para la clienta sobre sus redes"
}

FORMATOS DISPONIBLES:
- "reel": Video corto vertical (ideal para tutoriales, antes/despues)
- "carrusel": Varias imagenes/slides (ideal para educativo, tips)
- "foto": Imagen unica con copy (ideal para producto, testimonio)
- "story": Contenido efimero (ideal para detras de camaras, encuestas)

Genera contenido REALISTA que una esteticista real publicaria. Nada de frases como \
"descubre el secreto" o "no te lo vas a creer". Habla como una profesional, no como un \
anuncio de teletienda."""


def construir_prompt_usuario(perfil, semana_inicio=None, contenido_extra=None):
    if semana_inicio is None:
        semana_inicio = datetime.now()
    prompt = f"""Genera el calendario de contenido semanal para este negocio:

PERFIL DE LA CLIENTA:
- Negocio: {perfil['nombre_negocio']}
- Propietaria: {perfil['propietaria']}
- Ciudad: {perfil['ciudad']}
- Tipo: {perfil['tipo_negocio']}
- Servicios: {', '.join(perfil['servicios'])}
- Productos: {', '.join(perfil['productos']) if perfil['productos'] else 'No vende productos'}
- Tono de comunicacion: {perfil['tono']}
- Valores de marca: {', '.join(perfil['valores'])}
- Publico objetivo: {perfil['publico']}
- Redes sociales: {', '.join(perfil['redes'])}
- Instagram: {perfil.get('instagram_handle', 'No especificado')}

SEMANA A PLANIFICAR:
Genera contenido para 6 dias (lunes a sabado). Domingo no se publica.
1 publicacion por dia = 6 publicaciones en total.
Alterna entre las redes sociales de la clienta.

HORARIOS OPTIMOS:
{json.dumps(perfil.get('mejores_horarios', {}), indent=2, ensure_ascii=False)}
"""
    if contenido_extra:
        prompt += f"\nCONTEXTO ADICIONAL:\n{contenido_extra}\n"
    prompt += """
IMPORTANTE:
- Varia los tipos de contenido (no repitas el mismo tipo dos dias seguidos)
- Incluye al menos 1 reel y 1 carrusel educativo
- Al menos 1 publicacion debe promocionar un servicio concreto
- El copy debe estar listo para copiar y pegar
- Adapta el tono al perfil de la marca
Responde SOLO con el JSON."""
    return prompt


def generar_contenido_semanal(perfil, api_key=None, contenido_extra=None):
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key or not ANTHROPIC_DISPONIBLE:
        print("[MODO DEMO] Generando contenido de ejemplo.")
        return _generar_demo(perfil)

    client = Anthropic(api_key=key)
    prompt_usuario = construir_prompt_usuario(perfil, contenido_extra=contenido_extra)
    print(f"[Esteticai] Generando contenido para {perfil['nombre_negocio']}...")
    print(f"[Esteticai] Conectando con Claude... (10-20 segundos)")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt_usuario}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        calendario = json.loads(texto)
        print(f"[Esteticai] Listo: {len(calendario.get('calendario_semanal', []))} publicaciones")
        return calendario
    except json.JSONDecodeError as e:
        print(f"[Esteticai] Error: {e}")
        return {"error": str(e), "respuesta_cruda": texto}


def generar_copy_individual(perfil, tipo_contenido, servicio_o_producto,
                            descripcion_foto=None, api_key=None):
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key or not ANTHROPIC_DISPONIBLE:
        return _generar_copy_demo(perfil, tipo_contenido, servicio_o_producto)

    client = Anthropic(api_key=key)
    prompt = f"""Genera UN SOLO copy de tipo {tipo_contenido} para:
NEGOCIO: {perfil['nombre_negocio']} ({perfil['tipo_negocio']})
TONO: {perfil['tono']}
SERVICIO/PRODUCTO: {servicio_o_producto}
"""
    if descripcion_foto:
        prompt += f"\nFOTO/VIDEO: {descripcion_foto}\nAdapta el copy a lo que se ve.\n"
    prompt += """
Responde en JSON: {"copy": "...", "hashtags": [...], "cta": "...",
"formato_recomendado": "...", "hora_recomendada": "...", "nota_para_la_clienta": "..."}
Solo JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=1500,
        system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error": "No se pudo parsear", "respuesta_cruda": texto}


def _generar_demo(perfil):
    nombre = perfil["nombre_negocio"]
    s1 = perfil["servicios"][0] if perfil["servicios"] else "Tratamiento facial"
    s2 = perfil["servicios"][1] if len(perfil["servicios"]) > 1 else "Tratamiento corporal"
    s3 = perfil["servicios"][2] if len(perfil["servicios"]) > 2 else "Tratamiento premium"
    prod = perfil["productos"][0] if perfil["productos"] else "Nuestros productos"
    handle = perfil.get("instagram_handle", "")

    return {
        "calendario_semanal": [
            {"dia": "Lunes", "fecha": "2026-04-13", "hora_publicacion": "19:00",
             "red_social": "instagram", "tipo_contenido": "EDUCATIVO", "formato": "carrusel",
             "copy": f"Tu piel te habla, pero no siempre la escuchamos.\n\nEstos son los 5 signos de que tu piel necesita una {s1.lower()} YA:\n\n1. Poros visibles en nariz y mejillas\n2. Textura irregular al tacto\n3. Tono apagado aunque duermas bien\n4. Granitos que aparecen sin motivo\n5. Maquillaje que no se fija como antes\n\nSi marcas 3 o mas... es momento de actuar.\n\nEn {nombre} hacemos {s1.lower()} adaptadas a cada tipo de piel.\n\nGuarda este post y compartelo con alguien que lo necesite.",
             "hashtags": ["#cuidadodelapiel", "#esteticafacial", "#limpiezafacial", "#skincare", "#pielsana", "#bellezanatural"],
             "cta": "Escribe INFO por DM y te contamos como es el proceso",
             "nota_para_la_clienta": "5 slides: portada + 1 por signo + slide final con contacto.", "objetivo": "educar"},
            {"dia": "Martes", "fecha": "2026-04-14", "hora_publicacion": "12:30",
             "red_social": "instagram", "tipo_contenido": "ANTES_DESPUES", "formato": "reel",
             "copy": f"No, no es filtro. Es {s3.lower()}.\n\nResultado de 3 sesiones en nuestra clienta Maria (con su permiso).\n\nLo que nos dijo: 'Me miro al espejo y me reconozco, pero mejorada'.\n\nEso buscamos en {nombre}. Resultados reales que te hagan sentir tu mejor version.\n\nValoracion gratuita. Enlace en bio.",
             "hashtags": ["#antesydespues", "#resultadosreales", "#esteticaavanzada", "#bellezareal"],
             "cta": "Reserva tu valoracion gratuita. Link en bio.",
             "nota_para_la_clienta": "Video antes/despues con transicion. Asegurate de tener permiso.", "objetivo": "inspirar"},
            {"dia": "Miercoles", "fecha": "2026-04-15", "hora_publicacion": "20:00",
             "red_social": "tiktok", "tipo_contenido": "DETRAS_DE_CAMARAS", "formato": "reel",
             "copy": f"Un dia normal en {nombre} (spoiler: no existe un dia normal).\n\n8:30 - Preparo cabina. Mi momento zen.\n9:00 - Primera clienta: {s1.lower()}.\n11:00 - Cafe (sagrado e innegociable).\n11:30 - {s2} + consulta nueva clienta.\n14:00 - Comer y responder DMs.\n16:00 - Tarde de {s3.lower()}. Mi favorito.\n19:00 - Cierro y organizo manana.\n\nMucho amor y mucha ciencia.",
             "hashtags": ["#diaenlaClinica", "#esteticista", "#behindthescenes", "#emprendedora"],
             "cta": "Dale a seguir para mas dia a dia",
             "nota_para_la_clienta": "Clips cortos del dia: preparando, trabajando, cafe, cerrando. 30-45 seg.", "objetivo": "conectar"},
            {"dia": "Jueves", "fecha": "2026-04-16", "hora_publicacion": "20:00",
             "red_social": "instagram", "tipo_contenido": "PRODUCTO", "formato": "foto",
             "copy": f"Te presento a mi aliado numero 1: {prod}.\n\nBuscaba un producto que funcionara DE VERDAD, no irritara pieles sensibles, y mis clientas notaran diferencia desde la primera semana.\n\nEste lo cumple todo.\n\nNo es magia. Es ciencia bien aplicada.\n\nDisponible en cabina.",
             "hashtags": ["#skincare", "#cosmeticaprofesional", "#cuidadofacial", "#pielluminosa", "#beauty"],
             "cta": "DM para saber si es adecuado para tu piel",
             "nota_para_la_clienta": "Foto del producto con luz natural, fondo claro.", "objetivo": "vender"},
            {"dia": "Viernes", "fecha": "2026-04-17", "hora_publicacion": "13:00",
             "red_social": "instagram", "tipo_contenido": "TESTIMONIO", "formato": "carrusel",
             "copy": f"Cuando una clienta te dice esto, todo merece la pena.\n\n'Llevo anos con manchas. Habia probado de todo. En {nombre} me hicieron un plan personalizado. En 2 meses las manchas se redujeron un 80%.' - Ana R.\n\nGracias Ana por confiar.\n\nCada piel es diferente. Primero escuchamos, despues proponemos.",
             "hashtags": ["#testimonios", "#clientasfelices", "#resultadosreales", "#esteticafacial"],
             "cta": "Primera consulta sin compromiso.",
             "nota_para_la_clienta": "Slide 1: frase destacada. Slide 2-3: fotos. Slide 4: contacto.", "objetivo": "inspirar"},
            {"dia": "Sabado", "fecha": "2026-04-18", "hora_publicacion": "11:00",
             "red_social": "tiktok", "tipo_contenido": "TENDENCIA", "formato": "reel",
             "copy": f"POV: Le dices a tu esteticista que te cuidas la piel con toallitas.\n\n(cara de horror)\n\nLas toallitas no son el demonio, pero NO sustituyen una limpieza en condiciones.\n\nTip: doble limpieza. Primero aceite, despues limpiador.\n\nTu piel te lo agradecera.\n\n{handle}",
             "hashtags": ["#skincaretips", "#consejodeesteticista", "#limpiezafacial", "#bellezatiktok"],
             "cta": "Comenta con que te desmaquillas",
             "nota_para_la_clienta": "Vertical, mirando a camara, 20-30 seg. Audio trending si encuentras.", "objetivo": "educar"},
        ],
        "estrategia_semanal": f"Semana enfocada en posicionar a {nombre} como referente. Alternamos educativo (lun, sab), prueba social (mar, vie), conexion (mie) y producto (jue).",
        "consejo_de_la_semana": "Responde TODOS los comentarios y DMs en menos de 2 horas. El algoritmo premia la conversacion rapida."
    }


def _generar_copy_demo(perfil, tipo_contenido, servicio_o_producto):
    nombre = perfil["nombre_negocio"]
    return {
        "copy": f"Mito vs Realidad: {servicio_o_producto}\n\nMITO: 'Es doloroso'\nREALIDAD: Practicamente indoloro con tecnologia actual.\n\nMITO: 'Solo para gente mayor'\nREALIDAD: La prevencion empieza a los 30.\n\nMITO: 'Resultados artificiales'\nREALIDAD: TU cara, pero descansada y luminosa.\n\nEn {nombre} resolvemos tus dudas. Sin presion.",
        "hashtags": ["#mitosyrealidades", "#esteticafacial", "#cuidadodelapiel", "#bellezanatural"],
        "cta": "Dudas? Dejala en comentarios.",
        "formato_recomendado": "carrusel",
        "hora_recomendada": "19:00",
        "nota_para_la_clienta": "Carrusel con cada mito/realidad en una slide."
    }


def formatear_para_consola(calendario):
    if "error" in calendario:
        print(f"\n[ERROR] {calendario['error']}")
        return
    print("\n" + "=" * 60)
    print("  CALENDARIO SEMANAL - ESTETICAI")
    print("=" * 60)
    if "estrategia_semanal" in calendario:
        print(f"\nESTRATEGIA: {calendario['estrategia_semanal']}")
    for pub in calendario.get("calendario_semanal", []):
        print(f"\n{'~' * 60}")
        print(f"  {pub['dia'].upper()} | {pub.get('hora_publicacion', '')} | {pub.get('red_social', '')}")
        print(f"  Tipo: {pub.get('tipo_contenido', '')} | Formato: {pub.get('formato', '')}")
        print(f"{'~' * 60}")
        print(f"\n{pub.get('copy', '')}")
        print(f"\nHashtags: {' '.join(pub.get('hashtags', []))}")
        print(f"CTA: {pub.get('cta', '')}")
        if pub.get("nota_para_la_clienta"):
            print(f"Nota: {pub['nota_para_la_clienta']}")
    if "consejo_de_la_semana" in calendario:
        print(f"\n{'=' * 60}")
        print(f"  CONSEJO: {calendario['consejo_de_la_semana']}")
        print(f"{'=' * 60}")


def exportar_a_json(calendario, ruta_archivo):
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(calendario, f, ensure_ascii=False, indent=2)
    print(f"\n[Esteticai] Exportado a: {ruta_archivo}")
