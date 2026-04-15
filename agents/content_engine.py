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

# ============================================================
# BASE DE CONOCIMIENTO DE SERVICIOS ESTETICOS
# Informacion tecnica real para generar contenido creible
# ============================================================

SERVICIOS_ESTETICOS = {
    # --- FACIALES ---
    "limpieza facial": {
        "descripcion": "Limpieza profunda profesional con extraccion, vapor y mascarilla personalizada",
        "beneficios": ["Poros limpios", "Piel luminosa", "Previene imperfecciones", "Mejora textura"],
        "publico_ideal": "Todo tipo de pieles, desde los 16 anos",
        "frecuencia": "Cada 4-6 semanas",
        "categoria": "facial",
    },
    "hidratacion facial": {
        "descripcion": "Tratamiento intensivo de hidratacion con acido hialuronico y activos hidratantes",
        "beneficios": ["Piel jugosa", "Reduce lineas finas", "Efecto glow inmediato", "Restaura barrera cutanea"],
        "publico_ideal": "Pieles deshidratadas, maduras o danadas por el sol",
        "frecuencia": "Cada 2-4 semanas",
        "categoria": "facial",
    },
    "peeling quimico": {
        "descripcion": "Exfoliacion quimica con acidos (glicolico, salicilico, mandelico) para renovar la piel",
        "beneficios": ["Renueva la piel", "Reduce manchas", "Mejora textura", "Estimula colageno"],
        "publico_ideal": "Pieles con manchas, cicatrices de acne, envejecimiento",
        "frecuencia": "Cada 3-4 semanas (protocolo de 4-6 sesiones)",
        "categoria": "facial",
    },
    "microdermoabrasion": {
        "descripcion": "Exfoliacion mecanica con punta de diamante para renovar las capas superficiales",
        "beneficios": ["Piel suave", "Reduce poro", "Mejora absorcion de productos", "Sin recuperacion"],
        "publico_ideal": "Pieles apagadas, con poro dilatado o textura irregular",
        "frecuencia": "Cada 2-3 semanas",
        "categoria": "facial",
    },
    "radiofrecuencia facial": {
        "descripcion": "Tratamiento con ondas de radiofrecuencia para estimular colageno y tensar la piel",
        "beneficios": ["Efecto tensor", "Estimula colageno", "Redefine ovalo facial", "No invasivo"],
        "publico_ideal": "A partir de 35 anos, pieles con flacidez leve a moderada",
        "frecuencia": "Semanal durante 8-10 sesiones, mantenimiento mensual",
        "categoria": "facial",
    },
    "tratamiento antimanchas": {
        "descripcion": "Protocolo despigmentante con activos como vitamina C, acido kojico y retinol",
        "beneficios": ["Reduce manchas", "Unifica tono", "Previene hiperpigmentacion", "Ilumina"],
        "publico_ideal": "Pieles con manchas solares, melasma o hiperpigmentacion postinflamatoria",
        "frecuencia": "Semanal o quincenal durante 2-3 meses",
        "categoria": "facial",
    },
    "tratamiento antiacne": {
        "descripcion": "Protocolo especifico para pieles acneicas con limpieza, regulacion seborreica y cicatrizacion",
        "beneficios": ["Regula sebo", "Reduce brotes", "Mejora cicatrices", "Equilibra microbioma"],
        "publico_ideal": "Adolescentes y adultos con acne activo o cicatrices",
        "frecuencia": "Quincenal durante el tratamiento activo",
        "categoria": "facial",
    },
    "mesoterapia facial": {
        "descripcion": "Microinyecciones de vitaminas, aminoacidos y acido hialuronico en la dermis",
        "beneficios": ["Hidratacion profunda", "Luminosidad", "Estimula colageno", "Efecto rejuvenecedor"],
        "publico_ideal": "A partir de 30 anos, pieles desvitalizadas o con primeros signos de envejecimiento",
        "frecuencia": "4-6 sesiones quincenales, mantenimiento trimestral",
        "categoria": "facial",
    },
    "microneedling": {
        "descripcion": "Microperforaciones controladas con dermapen para estimular la regeneracion natural",
        "beneficios": ["Estimula colageno", "Mejora cicatrices", "Reduce poro", "Rejuvenece"],
        "publico_ideal": "Cicatrices de acne, estrias, piel envejecida",
        "frecuencia": "Cada 4-6 semanas, 3-6 sesiones",
        "categoria": "facial",
    },
    # --- CORPORALES ---
    "tratamiento reductor": {
        "descripcion": "Combinacion de tecnicas para reducir grasa localizada y contorno corporal",
        "beneficios": ["Reduce centimetros", "Mejora contorno", "Activa metabolismo local", "Drena liquidos"],
        "publico_ideal": "Personas con grasa localizada resistente a dieta y ejercicio",
        "frecuencia": "2-3 sesiones semanales durante 8-12 semanas",
        "categoria": "corporal",
    },
    "tratamiento reafirmante": {
        "descripcion": "Protocolo para mejorar la firmeza y elasticidad de la piel corporal",
        "beneficios": ["Piel mas firme", "Reduce flacidez", "Estimula colageno", "Mejora textura"],
        "publico_ideal": "Post-parto, perdida de peso, o envejecimiento cutaneo",
        "frecuencia": "Semanal durante 10-12 sesiones",
        "categoria": "corporal",
    },
    "masaje drenante": {
        "descripcion": "Drenaje linfatico manual o mecanico para eliminar retencion de liquidos",
        "beneficios": ["Reduce hinchazon", "Piernas ligeras", "Detoxifica", "Mejora circulacion"],
        "publico_ideal": "Retencion de liquidos, piernas cansadas, post-operatorio",
        "frecuencia": "Semanal o quincenal",
        "categoria": "corporal",
    },
    "presoterapia": {
        "descripcion": "Drenaje mecanico con botas de compresion secuencial",
        "beneficios": ["Drena liquidos", "Mejora circulacion", "Reduce celulitis", "Piernas descansadas"],
        "publico_ideal": "Retencion de liquidos, celulitis, piernas pesadas",
        "frecuencia": "1-2 sesiones semanales",
        "categoria": "corporal",
    },
    "tratamiento anticelulitis": {
        "descripcion": "Protocolo combinado para reducir celulitis con ultrasonidos, masaje y activos",
        "beneficios": ["Reduce piel de naranja", "Mejora textura", "Activa circulacion", "Reafirma"],
        "publico_ideal": "Mujeres con celulitis en grados I a III",
        "frecuencia": "2 sesiones semanales durante 10-12 semanas",
        "categoria": "corporal",
    },
    "envoltura corporal": {
        "descripcion": "Tratamiento con principios activos envueltos en film o vendas para potenciar absorcion",
        "beneficios": ["Hidrata en profundidad", "Desintoxica", "Reduce centimetros", "Piel suave"],
        "publico_ideal": "Todo tipo de pieles, ideal para preparar la piel en verano",
        "frecuencia": "Semanal o quincenal",
        "categoria": "corporal",
    },
    # --- LASER Y APARATOLOGIA ---
    "depilacion laser": {
        "descripcion": "Eliminacion del vello con laser de diodo o alejandrita, progresiva y duradera",
        "beneficios": ["Eliminacion permanente", "Piel suave", "Sin irritaciones", "Ahorra tiempo"],
        "publico_ideal": "Hombres y mujeres a partir de 16 anos con vello oscuro",
        "frecuencia": "Cada 4-8 semanas segun zona, 6-10 sesiones",
        "categoria": "laser",
    },
    "fotorejuvenecimiento ipl": {
        "descripcion": "Luz pulsada intensa para tratar manchas, rojeces y mejorar textura de la piel",
        "beneficios": ["Reduce manchas", "Mejora rojeces", "Unifica tono", "Estimula colageno"],
        "publico_ideal": "Pieles con dano solar, rosácea leve, manchas superficiales",
        "frecuencia": "Cada 3-4 semanas, 4-6 sesiones",
        "categoria": "laser",
    },
    "cavitacion": {
        "descripcion": "Ultrasonidos de baja frecuencia para romper adipocitos y reducir grasa localizada",
        "beneficios": ["Reduce grasa localizada", "No invasivo", "Sin recuperacion", "Resultados medibles"],
        "publico_ideal": "Grasa localizada resistente, sin obesidad general",
        "frecuencia": "Semanal, 8-12 sesiones",
        "categoria": "laser",
    },
    "criolipólisis": {
        "descripcion": "Congelacion controlada de celulas grasas para su eliminacion natural",
        "beneficios": ["Reduce hasta 25% grasa local", "Una sola sesion", "Sin cirugia", "Resultados permanentes"],
        "publico_ideal": "Personas con bolsas de grasa localizada que no responden a dieta",
        "frecuencia": "1-2 sesiones por zona, resultados en 2-3 meses",
        "categoria": "laser",
    },
    # --- SPA Y BIENESTAR ---
    "masaje relajante": {
        "descripcion": "Masaje manual con aceites esenciales para aliviar tension y estres",
        "beneficios": ["Relaja musculatura", "Reduce estres", "Mejora sueno", "Bienestar general"],
        "publico_ideal": "Cualquier persona que necesite desconectar y relajarse",
        "frecuencia": "Semanal o quincenal",
        "categoria": "spa",
    },
    "ritual spa": {
        "descripcion": "Experiencia completa de bienestar: exfoliacion, envoltura, masaje y aromaterapia",
        "beneficios": ["Experiencia sensorial completa", "Piel renovada", "Relajacion profunda", "Desconexion total"],
        "publico_ideal": "Regalos, ocasiones especiales, autocuidado",
        "frecuencia": "Mensual o puntual",
        "categoria": "spa",
    },
    "aromaterapia": {
        "descripcion": "Tratamiento con aceites esenciales puros aplicados mediante masaje, inhalacion o bano",
        "beneficios": ["Equilibrio emocional", "Reduce ansiedad", "Mejora sueno", "Bienestar holistico"],
        "publico_ideal": "Personas con estres, ansiedad o necesidad de equilibrio emocional",
        "frecuencia": "Semanal o quincenal",
        "categoria": "spa",
    },
    # --- UNAS Y BELLEZA ---
    "manicura semipermanente": {
        "descripcion": "Esmaltado con gel que dura 2-3 semanas sin descascarillarse",
        "beneficios": ["Duracion 2-3 semanas", "Brillo intenso", "Secado inmediato", "Protege la una"],
        "publico_ideal": "Mujeres que quieren unas perfectas sin retocar frecuentemente",
        "frecuencia": "Cada 2-3 semanas",
        "categoria": "unas",
    },
    "extension de pestanas": {
        "descripcion": "Aplicacion pelo a pelo o en abanico de pestanas sinteticas sobre las naturales",
        "beneficios": ["Mirada impactante", "Sin maquillaje diario", "Efecto natural o dramatico", "Duracion 3-4 semanas"],
        "publico_ideal": "Mujeres que quieren resaltar su mirada sin maquillarse a diario",
        "frecuencia": "Relleno cada 2-3 semanas",
        "categoria": "belleza",
    },
    "lifting de pestanas": {
        "descripcion": "Curvado y tinte de pestanas naturales para un efecto de ojos abiertos",
        "beneficios": ["Efecto natural", "Sin mantenimiento", "Ojos mas abiertos", "Dura 6-8 semanas"],
        "publico_ideal": "Pestanas rectas o caidas, quien busca efecto natural",
        "frecuencia": "Cada 6-8 semanas",
        "categoria": "belleza",
    },
    "diseno de cejas": {
        "descripcion": "Perfilado y tinte de cejas para enmarcar el rostro",
        "beneficios": ["Enmarca el rostro", "Mirada definida", "Reduce maquillaje diario", "Simetria facial"],
        "publico_ideal": "Cualquier persona que quiera cejas definidas y con forma",
        "frecuencia": "Cada 3-4 semanas",
        "categoria": "belleza",
    },
}

# Funcion para buscar servicio por coincidencia parcial
def buscar_servicio(nombre):
    """Busca un servicio en la base de conocimiento por coincidencia parcial."""
    nombre_lower = nombre.lower().strip()
    # Busqueda exacta
    if nombre_lower in SERVICIOS_ESTETICOS:
        return SERVICIOS_ESTETICOS[nombre_lower]
    # Busqueda parcial
    for key, valor in SERVICIOS_ESTETICOS.items():
        if nombre_lower in key or key in nombre_lower:
            return valor
    return None


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
- Tono de comunicacion: {perfil.get('tono', 'cercano')}
- Valores de marca: {', '.join(perfil.get('valores', [])) or 'No especificados'}
- Publico objetivo: {perfil.get('publico', '') or 'Mujeres interesadas en estetica y cuidado personal'}
- Redes sociales: {', '.join(perfil.get('redes', ['Instagram']))}
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

    # Construir contexto rico de marca
    valores_str = ', '.join(perfil.get('valores', [])) or 'No especificados'
    publico_str = perfil.get('publico', '') or 'Mujeres interesadas en estetica y cuidado personal'
    redes_str = ', '.join(perfil.get('redes', ['Instagram']))
    servicios_str = ', '.join(perfil.get('servicios', []))

    # Obtener info del servicio si existe en la base de conocimiento
    info_servicio = buscar_servicio(servicio_o_producto)
    contexto_servicio = ""
    if info_servicio:
        contexto_servicio = f"""
INFORMACION DEL SERVICIO (usa esto para hacer el copy mas tecnico y creible):
- Descripcion: {info_servicio.get('descripcion', '')}
- Beneficios clave: {', '.join(info_servicio.get('beneficios', []))}
- Publico ideal: {info_servicio.get('publico_ideal', '')}
- Frecuencia recomendada: {info_servicio.get('frecuencia', '')}
"""

    prompt = f"""Genera UN SOLO copy de tipo {tipo_contenido} para publicar en redes sociales.

PERFIL COMPLETO DEL NEGOCIO:
- Negocio: {perfil['nombre_negocio']} ({perfil['tipo_negocio']})
- Propietaria: {perfil.get('propietaria', '')}
- Ciudad: {perfil.get('ciudad', '')}
- Tono de comunicacion: {perfil.get('tono', 'cercano')}
- Valores de marca: {valores_str}
- Publico objetivo: {publico_str}
- Redes sociales activas: {redes_str}
- Todos sus servicios: {servicios_str}
- Instagram: {perfil.get('instagram_handle', '')}

SERVICIO/PRODUCTO PARA ESTE COPY: {servicio_o_producto}
{contexto_servicio}

TIPO DE CONTENIDO: {tipo_contenido}

REGLAS PARA ESTE COPY:
1. El PRIMER RENGLON debe ser un gancho que detenga el scroll (pregunta, dato impactante, o frase que genere curiosidad)
2. El copy debe sentirse escrito por la propietaria, NO por una IA. Usa su tono ({perfil.get('tono', 'cercano')}).
3. Maximo 2200 caracteres (limite de Instagram). Ideal: 800-1200.
4. Incluye saltos de linea para que sea facil de leer en el movil.
5. Maximo 3-4 emojis, usados con gusto.
6. Los hashtags deben ser: 3 de nicho especifico, 3 de alcance medio, 2 generales. Total 8 hashtags.
7. El CTA debe ser natural, no agresivo. Ejemplo: "Escribe QUIERO por DM" mejor que "COMPRA YA".
8. Incluye una nota practica para la clienta sobre que imagen o video acompanar.
"""
    if descripcion_foto:
        prompt += f"\nFOTO/VIDEO QUE ACOMPANA: {descripcion_foto}\nAdapta el copy a lo que se ve en la imagen/video.\n"

    prompt += """
Responde SOLO con JSON valido (sin markdown, sin ```):
{
  "copy": "El texto completo listo para copiar y pegar",
  "hashtags": ["#hashtag1", "#hashtag2", ...],
  "cta": "La llamada a la accion",
  "formato_recomendado": "reel|carrusel|foto|story",
  "hora_recomendada": "19:00",
  "red_social_ideal": "Instagram|TikTok|Facebook",
  "nota_para_la_clienta": "Instruccion sobre que foto/video usar"
}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=2000,
        system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}],
    )
    texto = response.content[0].text.strip()
    # Limpiar posibles wrappers markdown
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    # Intentar extraer JSON si hay texto extra
    if not texto.startswith("{"):
        inicio = texto.find("{")
        if inicio != -1:
            texto = texto[inicio:]
    if not texto.endswith("}"):
        fin = texto.rfind("}")
        if fin != -1:
            texto = texto[:fin + 1]
    try:
        resultado = json.loads(texto)
        # Validar campos minimos
        if "copy" not in resultado or not resultado["copy"]:
            return {"error": "El copy generado esta vacio"}
        # Asegurar que hashtags es una lista
        if isinstance(resultado.get("hashtags"), str):
            resultado["hashtags"] = [h.strip() for h in resultado["hashtags"].split() if h.startswith("#")]
        return resultado
    except json.JSONDecodeError:
        # Ultimo intento: buscar el JSON dentro del texto
        import re
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"error": "No se pudo parsear la respuesta", "respuesta_cruda": texto[:500]}


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
