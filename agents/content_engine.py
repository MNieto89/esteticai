"""
MOTOR DE CONTENIDO - Esteticai
================================
Genera contenido profesional de redes sociales para negocios de estetica.
Basado en investigacion real de estrategias de venta en Instagram, TikTok
y Facebook de centros de estetica exitosos (2025-2026).

Fuentes de conocimiento:
- Analisis de engagement rates del sector belleza (Traackr, Dash Social)
- Formulas de copywriting AIDA, PAS, BAB, FAB (Maider Tomasena, Maria Abad)
- Algoritmo Instagram 2026 (Sprout Social, Later, Hootsuite)
- Psicologia de venta: escasez, prueba social, urgencia (Cialdini)
- Estrategia 40-30-20-10 de distribucion de contenido
- Estructura de hooks probada (7 formulas de gancho)
"""

import json
import os
import random
from datetime import datetime, timedelta

try:
    from anthropic import Anthropic
    ANTHROPIC_DISPONIBLE = True
except ImportError:
    ANTHROPIC_DISPONIBLE = False
    print("[INFO] SDK de Anthropic no instalado. Ejecutando en modo demo.")

# ============================================================
# FORMULAS DE COPYWRITING PROFESIONAL
# Estructuras probadas para generar contenido que convierte
# ============================================================

FORMULAS_COPY = {
    "AIDA": {
        "nombre": "Atencion - Interes - Deseo - Accion",
        "estructura": (
            "1. ATENCION: Primera linea que detiene el scroll. Pregunta provocadora, "
            "dato impactante o afirmacion que rompa expectativas.\n"
            "2. INTERES: Desarrolla la idea con informacion relevante que mantenga "
            "la curiosidad. Conecta con un problema o deseo real de la lectora.\n"
            "3. DESEO: Apela a la emocion. Haz que se imagine el resultado, que sienta "
            "como seria su vida/piel/cuerpo despues del tratamiento.\n"
            "4. ACCION: CTA natural y no agresivo. Indica el siguiente paso concreto."
        ),
        "ideal_para": ["PRODUCTO", "PROMOCION", "TESTIMONIO", "TRATAMIENTO"],
    },
    "PAS": {
        "nombre": "Problema - Agitacion - Solucion",
        "estructura": (
            "1. PROBLEMA: Identifica un problema real que tiene tu clienta. "
            "Nombra el dolor de forma especifica (no generica).\n"
            "2. AGITACION: Profundiza en las consecuencias de no actuar. "
            "Que pasa si sigue ignorando el problema. Sin dramatizar, siendo honesta.\n"
            "3. SOLUCION: Presenta tu tratamiento/producto como la respuesta. "
            "Con datos reales, sin promesas imposibles."
        ),
        "ideal_para": ["EDUCATIVO", "PRODUCTO", "ANTES_DESPUES"],
    },
    "BAB": {
        "nombre": "Before - After - Bridge",
        "estructura": (
            "1. ANTES: Describe la situacion actual de la clienta. Su frustracion, "
            "lo que ha probado sin resultado, como se siente.\n"
            "2. DESPUES: Pinta el escenario ideal. Como se sentira, que vera en el espejo, "
            "como cambiara su rutina.\n"
            "3. PUENTE: Tu tratamiento/producto es el camino entre ambos estados. "
            "Explica brevemente como funciona."
        ),
        "ideal_para": ["ANTES_DESPUES", "TESTIMONIO", "PERSONAL"],
    },
    "STORYTELLING": {
        "nombre": "Historia con moraleja",
        "estructura": (
            "1. SITUACION: Presenta a una persona real (clienta, tu misma) en un "
            "momento concreto. Usa detalles sensoriales.\n"
            "2. CONFLICTO: Que problema enfrento. Que habia probado. Por que estaba frustrada.\n"
            "3. RESOLUCION: Como se resolvio. Resultado concreto y medible.\n"
            "4. LECCION: Que puede aprender la lectora de esta historia."
        ),
        "ideal_para": ["PERSONAL", "TESTIMONIO", "DETRAS_DE_CAMARAS"],
    },
}

# ============================================================
# GANCHOS PROBADOS PARA DETENER EL SCROLL
# 7 formulas de hook con ejemplos adaptados a estetica
# ============================================================

GANCHOS_POR_TIPO = {
    "curiosidad": [
        "Sabes cual es el error numero 1 que cometen el 80% de las mujeres con su piel?",
        "Llevo 10 anos como esteticista y hay algo que me sigue sorprendiendo.",
        "Lo que tu piel hace mientras duermes te va a cambiar la rutina.",
        "Por que tu crema de 50 euros no te esta funcionando?",
        "Hay un ingrediente en tu neceser que esta saboteando tu piel.",
    ],
    "revelacion": [
        "Esto NO es filtro. Es {servicio} y tres sesiones de constancia.",
        "Cuando me dijo lo que habia probado antes, entendi por que no le funcionaba.",
        "La diferencia entre estas dos fotos? 6 semanas y un protocolo bien hecho.",
        "Mira lo que pasa cuando dejas de buscar milagros y empiezas un plan real.",
        "No, no retocamos las fotos. Retocamos pieles. Con ciencia.",
    ],
    "narrativo": [
        "Ayer vino una clienta que llevaba dos anos sin mirarse al espejo con ganas.",
        "Empece en este mundo con un curso de fin de semana y una camilla prestada.",
        "Me acuerdo perfectamente de mi primera clienta. Se llamaba Ana.",
        "Hay dias en cabina que me recuerdan por que elegi este trabajo.",
        "La historia de hoy empieza con un 'ya lo he probado todo'.",
    ],
    "lista": [
        "3 senales de que tu piel te esta pidiendo ayuda (y no son las que piensas).",
        "5 cosas que hago cada manana antes de abrir el centro.",
        "Los 4 tratamientos que mas piden mis clientas este mes (y por que).",
        "7 mitos sobre {servicio} que necesitas dejar de creer hoy.",
        "Las 3 preguntas que SIEMPRE hago en una primera consulta.",
    ],
    "contraintuitivo": [
        "La peor hora para ponerse crema solar? Por la manana temprano.",
        "Menos es mas: por que tu rutina de 10 pasos esta empeorando tu piel.",
        "El acido hialuronico no hidrata. Al menos, no como tu crees.",
        "Limpiar tu piel dos veces al dia puede estar resecandola.",
        "Ese serum 'milagroso' de TikTok? Tu esteticista tiene algo que decirte.",
    ],
    "beneficio": [
        "Imagina mirarte al espejo y no necesitar filtro para sentirte bien.",
        "Una piel que no necesita maquillaje para brillar. Eso es lo que buscamos.",
        "Y si te dijera que en 4 sesiones puedes dejar de tapar esas manchas?",
        "Piel luminosa sin cirugia, sin dolor y sin inventos. Existe, y se llama {servicio}.",
        "Tu cara, pero descansada. Tu piel, pero con luz. Eso hacemos aqui.",
    ],
    "urgencia": [
        "Solo quedan {n} huecos esta semana para valoracion gratuita.",
        "Hasta el viernes: primera sesion de {servicio} con valoracion incluida.",
        "Este mes lanzamos algo nuevo. Y las primeras 10 reservas tienen ventaja.",
        "Septiembre es el mes perfecto para empezar. Tu piel lo sabe.",
        "Abrimos agenda para {mes}. Los mejores horarios vuelan.",
    ],
}

# ============================================================
# LLAMADAS A LA ACCION (CTAs) PROFESIONALES
# Naturales, no agresivas, orientadas a conversacion
# ============================================================

CTAS_POR_OBJETIVO = {
    "reservar": [
        "Escribe QUIERO por DM y te cuento todo sin compromiso.",
        "Link en bio para reservar tu hueco.",
        "Primera consulta sin compromiso. DM o link en bio.",
        "Reserva tu valoracion gratuita. El enlace esta en mi perfil.",
        "Escribe tu zona y te digo disponibilidad esta semana.",
    ],
    "educar": [
        "Guarda este post. Tu piel te lo agradecera.",
        "Compartelo con alguien que necesite leer esto.",
        "Dudas? Dejamelas en comentarios. Respondo todas.",
        "Si quieres saber mas, tengo un carrusel completo. Link en bio.",
        "Guardalo y vuelve a leerlo cuando cambies de rutina.",
    ],
    "conectar": [
        "Cuentame: te ha pasado? Te leo en comentarios.",
        "Cual es tu mayor lucha con tu piel? Te leo.",
        "Dale a seguir si quieres mas contenido asi de lunes a sabado.",
        "Comenta si te sientes identificada.",
        "Etiqueta a tu amiga que necesita oir esto.",
    ],
    "vender": [
        "Disponible en cabina y por encargo. Preguntame por DM.",
        "Consulta tu precio personalizado por DM. Cada piel es un mundo.",
        "Escribe PRECIO por DM y te mando toda la info.",
        "Plazas limitadas este mes. Reserva tu hueco antes del viernes.",
        "Escribe INFO por DM y te preparo una propuesta a medida.",
    ],
}

# ============================================================
# HASHTAGS PROFESIONALES POR CATEGORIA
# Organizados en 3 niveles: descubrimiento, nicho, local
# ============================================================

HASHTAGS_BASE = {
    "descubrimiento": [
        "#belleza", "#beauty", "#skincare", "#selfcare", "#cuidadopersonal",
        "#bienestar", "#wellness", "#glowup", "#rutinafacial", "#pielsana",
    ],
    "nicho_facial": [
        "#esteticafacial", "#cuidadodelapiel", "#limpiezafacial",
        "#tratamientofacial", "#antiedad", "#pielluminosa", "#hidratacionfacial",
        "#acnecuidado", "#manchasfaciales", "#rejuvenecimientofacial",
    ],
    "nicho_corporal": [
        "#esteticacorporal", "#tratamientocorporal", "#celulitis",
        "#reafirmante", "#drenaje", "#presoterapia", "#moldearfigura",
        "#cuerposano", "#pielfirme", "#reducirmedidas",
    ],
    "nicho_laser": [
        "#depilacionlaser", "#laserdiodo", "#tecnologiaestetica",
        "#cavitacion", "#radiofrecuencia", "#criolipolisis",
        "#aparatologia", "#esteticaavanzada",
    ],
    "nicho_belleza": [
        "#pestanas", "#cejas", "#manicura", "#unasdecoradas",
        "#liftingpestanas", "#extensionpestanas", "#microblading",
        "#diseno_cejas", "#semipermanente",
    ],
    "nicho_spa": [
        "#spa", "#masaje", "#relajacion", "#ritualdebelleza",
        "#bienestarintegral", "#aromaterapia", "#cuidadoholistico",
    ],
    "nicho_producto": [
        "#cosmeticaprofesional", "#skincareroutine", "#serumfacial",
        "#cosmeticanatural", "#productosdebelleza", "#activos",
        "#acidohialuronico", "#vitaminac", "#retinol",
    ],
    "profesional": [
        "#esteticista", "#centrodeestetica", "#clinicaestetica",
        "#profesionaldelapiel", "#esteticistaprofesional",
        "#formacionestetica", "#vidadeesteticista",
    ],
}

# ============================================================
# HORARIOS OPTIMOS POR RED SOCIAL (Datos 2026)
# Basado en Sprout Social y Later
# ============================================================

HORARIOS_OPTIMOS = {
    "Instagram": {
        "mejores_dias": ["martes", "miercoles", "viernes"],
        "peores_dias": ["sabado", "domingo"],
        "horas_reels": ["18:00", "19:00", "20:00", "21:00"],
        "horas_carrusel": ["11:00", "12:00", "13:00"],
        "horas_foto": ["9:00", "12:00", "19:00"],
        "horas_story": ["8:00", "12:00", "18:00", "21:00"],
    },
    "TikTok": {
        "mejores_dias": ["martes", "jueves", "viernes"],
        "peores_dias": ["lunes"],
        "horas_video": ["12:00", "15:00", "19:00", "21:00"],
    },
    "Facebook": {
        "mejores_dias": ["miercoles", "jueves", "viernes"],
        "peores_dias": ["sabado", "domingo"],
        "horas_post": ["9:00", "11:00", "13:00"],
    },
}

# ============================================================
# DISTRIBUCION DE CONTENIDO (Formula 40-30-20-10)
# ============================================================

DISTRIBUCION_CONTENIDO = {
    "educativo": {
        "porcentaje": 40,
        "tipos": ["EDUCATIVO", "TENDENCIA"],
        "descripcion": "Tips, mitos vs realidad, explicaciones de tratamientos, rutinas",
    },
    "conexion": {
        "porcentaje": 30,
        "tipos": ["DETRAS_DE_CAMARAS", "PERSONAL"],
        "descripcion": "Dia a dia, equipo, historia personal, proceso de tratamientos",
    },
    "prueba_social": {
        "porcentaje": 20,
        "tipos": ["ANTES_DESPUES", "TESTIMONIO"],
        "descripcion": "Resultados reales, testimonios con permiso, transformaciones",
    },
    "conversion": {
        "porcentaje": 10,
        "tipos": ["PRODUCTO", "PROMOCION"],
        "descripcion": "Ofertas, productos, packs, lanzamientos",
    },
}

# ============================================================
# VOCABULARIO PROFESIONAL DE ESTETICA
# Palabras y expresiones que usan los centros exitosos
# ============================================================

VOCABULARIO_PROFESIONAL = {
    "verbos_de_transformacion": [
        "renovar", "despertar", "devolver", "restaurar", "revitalizar",
        "iluminar", "redefinir", "recuperar", "potenciar", "equilibrar",
        "estimular", "nutrir", "proteger", "corregir", "unificar",
    ],
    "adjetivos_sensoriales": [
        "luminosa", "sedosa", "firme", "tersa", "jugosa", "aterciopelada",
        "radiante", "uniforme", "fresca", "hidratada", "suave", "elastica",
        "descansada", "natural", "saludable", "renovada", "vital",
    ],
    "expresiones_profesionales": [
        "protocolo personalizado", "principios activos", "barrera cutanea",
        "microbioma de la piel", "renovacion celular", "dermis profunda",
        "efecto flash", "efecto lifting", "bioestimulacion", "neocolagenesis",
        "cronobiologia cutanea", "capacidad de absorcion", "pH equilibrado",
        "formulacion cosmeceutica", "activos encapsulados",
    ],
    "expresiones_emocionales": [
        "sentirte tu mejor version", "mirarte al espejo y sonreir",
        "tu cara, pero descansada", "piel que habla por ti",
        "la confianza que da una piel cuidada", "ese brillo que no da ningun filtro",
        "volver a sentirte comoda sin maquillaje", "piel que respira confianza",
        "resultados que se ven y se sienten", "tu piel, tus reglas",
    ],
    "frases_credibilidad": [
        "basado en evidencia", "protocolo probado", "resultados medibles",
        "tecnologia de ultima generacion", "formacion continua",
        "mas de X anos de experiencia", "cientos de clientas satisfechas",
        "aprobado dermatologicamente", "sin promesas vacias, solo resultados",
        "cada piel es unica, cada plan tambien",
    ],
}

# ============================================================
# PILARES DE CONTENIDO POR TIPO DE NEGOCIO
# ============================================================

PILARES_POR_TIPO = {
    "Centro de estetica": {
        "pilares": ["tratamientos estrella", "rutinas de cuidado", "tu esteticista de confianza", "resultados reales"],
        "tono_natural": "cercano y profesional, como una amiga que sabe de piel",
    },
    "Clinica de estetica facial y corporal": {
        "pilares": ["ciencia detras de la belleza", "tecnologia avanzada", "casos clinicos", "prevencion y mantenimiento"],
        "tono_natural": "profesional y riguroso, transmitiendo seguridad y conocimiento",
    },
    "Salon de belleza": {
        "pilares": ["transformaciones de imagen", "tendencias", "cuidado integral", "experiencia en salon"],
        "tono_natural": "fresco y cercano, celebrando la belleza en todas sus formas",
    },
    "Spa": {
        "pilares": ["bienestar integral", "rituales de autocuidado", "desconexion", "equilibrio cuerpo-mente"],
        "tono_natural": "sereno y envolvente, invitando al cuidado y la calma",
    },
    "Freelance esteticista": {
        "pilares": ["mi historia", "tu piel mi pasion", "formacion constante", "tratamientos a medida"],
        "tono_natural": "muy personal y directo, como si hablaras tu a tu con cada seguidora",
    },
    "Peluqueria con estetica": {
        "pilares": ["cambio de imagen total", "cuidado capilar", "tendencias de temporada", "equipo creativo"],
        "tono_natural": "creativo y energico, inspirando cambios de look",
    },
    "Distribuidora de cosmetica": {
        "pilares": ["ingredientes que funcionan", "ciencia cosmetica", "novedades del sector", "formacion para profesionales"],
        "tono_natural": "tecnico pero accesible, posicionando como referente del sector",
    },
    "Tienda de cosmetica online": {
        "pilares": ["resenas honestas", "rutinas por tipo de piel", "comparativas de producto", "ofertas exclusivas"],
        "tono_natural": "honesto y practico, como una amiga que ha probado todo",
    },
}

# ============================================================
# BASE DE CONOCIMIENTO DE SERVICIOS (version enriquecida)
# Info tecnica profunda para copywriting de calidad
# ============================================================

SERVICIOS_ESTETICOS = {
    "limpieza facial": {
        "descripcion": "Limpieza profunda profesional con extraccion, vapor y mascarilla personalizada",
        "beneficios": ["Poros limpios y cerrados", "Piel luminosa desde la primera sesion", "Previene brotes e imperfecciones", "Mejora la textura al tacto"],
        "dolor_clienta": "Poros visibles, puntos negros, piel apagada que el maquillaje no tapa",
        "dato_gancho": "Tu piel acumula mas de 200 toxinas al dia solo por vivir en ciudad",
        "resultado_esperable": "Piel visiblemente mas limpia, luminosa y suave desde la primera sesion",
        "frecuencia": "Cada 4-6 semanas",
        "categoria": "facial",
        "palabras_clave_copy": ["renovar", "purificar", "respirar", "detox facial"],
    },
    "hidratacion facial": {
        "descripcion": "Tratamiento intensivo con acido hialuronico y activos hidratantes de penetracion profunda",
        "beneficios": ["Piel jugosa e hidratada en profundidad", "Reduce lineas de expresion finas", "Efecto glow inmediato", "Restaura la barrera cutanea"],
        "dolor_clienta": "Piel tirante, descamada, lineas finas que aparecen de repente, sensacion de sequedad constante",
        "dato_gancho": "La piel pierde un 1% de acido hialuronico natural cada ano a partir de los 25",
        "resultado_esperable": "Efecto 'piel de cristal': hidratacion profunda visible durante 2-3 semanas",
        "frecuencia": "Cada 2-4 semanas",
        "categoria": "facial",
        "palabras_clave_copy": ["glow", "jugosa", "cristal", "barrera cutanea"],
    },
    "radiofrecuencia facial": {
        "descripcion": "Ondas de radiofrecuencia que calientan la dermis profunda para estimular colageno nuevo",
        "beneficios": ["Efecto tensor visible desde la primera sesion", "Estimula la produccion natural de colageno", "Redefine el ovalo facial", "Sin agujas, sin cirugia, sin baja"],
        "dolor_clienta": "Flacidez en mejillas y papada, ovalo facial desdibujado, sensacion de 'cara caida'",
        "dato_gancho": "A partir de los 30 perdemos un 1-2% de colageno al ano. La radiofrecuencia revierte ese reloj",
        "resultado_esperable": "Piel mas firme y definida tras 4-6 sesiones, con mejora progresiva durante meses",
        "frecuencia": "Semanal durante 8-10 sesiones, mantenimiento mensual",
        "categoria": "facial",
        "palabras_clave_copy": ["firme", "definir", "colageno", "tensor sin cirugia"],
    },
    "peeling quimico": {
        "descripcion": "Exfoliacion quimica controlada con acidos (glicolico, salicilico, mandelico) para renovar la piel",
        "beneficios": ["Renueva las capas superficiales", "Reduce manchas y unifica el tono", "Mejora la textura irregular", "Estimula la renovacion celular"],
        "dolor_clienta": "Manchas que no se van con crema, tono desigual, textura rugosa, cicatrices de acne",
        "dato_gancho": "Un peeling bien hecho puede mejorar la textura de tu piel mas que un ano entero de cremas",
        "resultado_esperable": "Piel renovada, tono mas uniforme y textura mejorada en 2-3 sesiones",
        "frecuencia": "Cada 3-4 semanas (protocolo de 4-6 sesiones)",
        "categoria": "facial",
        "palabras_clave_copy": ["renovar", "unificar", "borrar", "nueva piel"],
    },
    "tratamiento antimanchas": {
        "descripcion": "Protocolo despigmentante personalizado con vitamina C, acido kojico, retinol y proteccion solar",
        "beneficios": ["Reduce manchas visiblemente", "Unifica el tono de la piel", "Previene nueva hiperpigmentacion", "Ilumina el rostro"],
        "dolor_clienta": "Manchas del sol, melasma, marcas de acne, tono desigual que el maquillaje no cubre del todo",
        "dato_gancho": "El 90% de las manchas se deben al sol acumulado, no a la edad",
        "resultado_esperable": "Reduccion visible de manchas en 4-8 semanas de protocolo constante",
        "frecuencia": "Semanal o quincenal durante 2-3 meses",
        "categoria": "facial",
        "palabras_clave_copy": ["iluminar", "unificar", "corregir", "tono perfecto"],
    },
    "tratamiento antiacne": {
        "descripcion": "Protocolo especifico para pieles acneicas: limpieza, regulacion seborreica, cicatrizacion y equilibrio del microbioma",
        "beneficios": ["Regula la produccion de sebo", "Reduce brotes activos", "Mejora cicatrices y marcas", "Equilibra el microbioma cutaneo"],
        "dolor_clienta": "Brotes constantes, cicatrices que no se van, autoestima afectada, frustacion con productos de farmacia",
        "dato_gancho": "El acne adulto afecta al 25% de las mujeres entre 25 y 45 anos. No es cosa de adolescentes",
        "resultado_esperable": "Reduccion significativa de brotes en 4-6 semanas, mejora de marcas en 2-3 meses",
        "frecuencia": "Quincenal durante el tratamiento activo",
        "categoria": "facial",
        "palabras_clave_copy": ["equilibrar", "controlar", "restaurar", "piel limpia"],
    },
    "mesoterapia facial": {
        "descripcion": "Microinyecciones de vitaminas, aminoacidos y acido hialuronico directamente en la dermis",
        "beneficios": ["Hidratacion profunda desde dentro", "Luminosidad inmediata", "Estimula colageno y elastina", "Efecto rejuvenecedor natural"],
        "dolor_clienta": "Piel desvitalizada, gris, cansada, que no responde a las cremas habituales",
        "dato_gancho": "La mesoterapia lleva los activos donde las cremas no pueden llegar: la dermis",
        "resultado_esperable": "Efecto 'buena cara' inmediato, resultados acumulativos con cada sesion",
        "frecuencia": "4-6 sesiones quincenales, mantenimiento trimestral",
        "categoria": "facial",
        "palabras_clave_copy": ["revitalizar", "nutrir desde dentro", "luminosidad real", "efecto buena cara"],
    },
    "microneedling": {
        "descripcion": "Microperforaciones controladas con Dermapen para estimular la regeneracion natural de la piel",
        "beneficios": ["Estimula produccion de colageno propio", "Mejora cicatrices y poro dilatado", "Rejuvenece sin quimicos", "Mejora la absorcion de activos"],
        "dolor_clienta": "Cicatrices de acne, poros abiertos, estrias, piel envejecida que necesita un empujon",
        "dato_gancho": "Tu piel tiene una capacidad de regeneracion increible. El microneedling solo la activa",
        "resultado_esperable": "Piel mas firme y con menos poro visible en 3-4 sesiones",
        "frecuencia": "Cada 4-6 semanas, 3-6 sesiones",
        "categoria": "facial",
        "palabras_clave_copy": ["regenerar", "activar", "tu propia piel pero mejor", "colageno natural"],
    },
    "tratamiento reductor": {
        "descripcion": "Protocolo combinado de tecnicas para reducir centimetros, grasa localizada y mejorar el contorno corporal",
        "beneficios": ["Reduce centimetros medibles", "Mejora el contorno corporal", "Activa el metabolismo local", "Drena liquidos retenidos"],
        "dolor_clienta": "Grasa localizada que no se va con dieta ni ejercicio, michelines resistentes, ropa que ya no sienta igual",
        "dato_gancho": "La grasa localizada es resistente a la dieta porque tiene menos receptores de quema. La tecnologia si llega",
        "resultado_esperable": "Reduccion de 2-4 cm por zona en 8-10 sesiones combinadas",
        "frecuencia": "2-3 sesiones semanales durante 8-12 semanas",
        "categoria": "corporal",
        "palabras_clave_copy": ["moldear", "reducir", "contornear", "redefinir tu silueta"],
    },
    "masaje drenante": {
        "descripcion": "Drenaje linfatico manual o mecanico para eliminar retencion de liquidos y toxinas",
        "beneficios": ["Reduce hinchazon visible", "Piernas ligeras desde la primera sesion", "Detoxifica y mejora circulacion", "Alivia la sensacion de pesadez"],
        "dolor_clienta": "Piernas hinchadas al final del dia, retencion de liquidos, sensacion de pesadez constante",
        "dato_gancho": "Tu sistema linfatico no tiene bomba propia. Necesita ayuda manual para drenar correctamente",
        "resultado_esperable": "Piernas mas ligeras y deshinchadas desde la primera sesion",
        "frecuencia": "Semanal o quincenal",
        "categoria": "corporal",
        "palabras_clave_copy": ["drenar", "aligerar", "deshinchar", "piernas ligeras"],
    },
    "depilacion laser": {
        "descripcion": "Eliminacion progresiva y duradera del vello con laser de diodo o alejandrita",
        "beneficios": ["Eliminacion duradera del vello", "Piel suave sin irritaciones", "Olvida la cuchilla para siempre", "Ahorra tiempo y dinero a largo plazo"],
        "dolor_clienta": "Pelos enquistados, irritacion por cuchilla, cera dolorosa cada mes, manchas por depilacion",
        "dato_gancho": "Una mujer se depila con cuchilla una media de 7.718 veces en su vida. El laser lo resuelve en 8",
        "resultado_esperable": "Reduccion del 80-90% del vello en 6-8 sesiones",
        "frecuencia": "Cada 4-8 semanas segun zona, 6-10 sesiones",
        "categoria": "laser",
        "palabras_clave_copy": ["libertad", "sin vello", "piel suave siempre", "adios cuchilla"],
    },
    "extension de pestanas": {
        "descripcion": "Aplicacion pelo a pelo o en abanico de pestanas sinteticas sobre las naturales",
        "beneficios": ["Mirada impactante sin maquillaje", "Efecto natural o dramatico a elegir", "Te levantas lista", "Dura 3-4 semanas"],
        "dolor_clienta": "Pestanas cortas o invisibles, depender del rimmel cada dia, maquillaje que se corre",
        "dato_gancho": "El 70% de las clientas de extensiones dicen que lo mejor es despertarse y ya estar guapa",
        "resultado_esperable": "Mirada transformada al instante. Efecto natural (pelo a pelo) o volumen (abanico)",
        "frecuencia": "Relleno cada 2-3 semanas",
        "categoria": "belleza",
        "palabras_clave_copy": ["mirada", "despertar lista", "sin rimmel", "efecto wow"],
    },
    "manicura semipermanente": {
        "descripcion": "Esmaltado con gel curado con lampara LED que dura 2-3 semanas sin descascarillarse",
        "beneficios": ["Duracion de 2-3 semanas intacta", "Brillo intenso que no pierde", "Secado inmediato", "Protege la una natural"],
        "dolor_clienta": "Esmalte que dura 2 dias, unas que se rompen, manos descuidadas por falta de tiempo",
        "dato_gancho": "Unas cuidadas son la carta de presentacion silenciosa mas potente que existe",
        "resultado_esperable": "Unas perfectas durante 2-3 semanas sin retoques",
        "frecuencia": "Cada 2-3 semanas",
        "categoria": "unas",
        "palabras_clave_copy": ["manos perfectas", "sin retocar", "brillo que dura", "tu carta de presentacion"],
    },
    "masaje relajante": {
        "descripcion": "Masaje manual con aceites esenciales para liberar tension muscular y reducir estres",
        "beneficios": ["Relaja musculatura profunda", "Reduce estres y ansiedad", "Mejora la calidad del sueno", "Bienestar general inmediato"],
        "dolor_clienta": "Estres cronico, contracturas, insomnio, sensacion de no poder desconectar nunca",
        "dato_gancho": "60 minutos de masaje reduce los niveles de cortisol (hormona del estres) un 30%",
        "resultado_esperable": "Sensacion de relajacion profunda y bienestar que dura varios dias",
        "frecuencia": "Semanal o quincenal",
        "categoria": "spa",
        "palabras_clave_copy": ["desconectar", "soltar", "respirar", "tu momento"],
    },
    "microdermoabrasion": {
        "descripcion": "Exfoliacion mecanica con punta de diamante para renovar las capas superficiales",
        "beneficios": ["Piel suave al instante", "Reduce poro visible", "Mejora absorcion de productos", "Sin recuperacion"],
        "dolor_clienta": "Piel apagada, con poro dilatado o textura irregular que no mejora con exfoliantes caseros",
        "dato_gancho": "La microdermoabrasion elimina hasta un 30% mas de celulas muertas que cualquier exfoliante de farmacia",
        "resultado_esperable": "Piel visiblemente mas suave y luminosa desde la primera sesion",
        "frecuencia": "Cada 2-3 semanas",
        "categoria": "facial",
        "palabras_clave_copy": ["renovar", "pulir", "suavizar", "piel nueva"],
    },
    "presoterapia": {
        "descripcion": "Drenaje mecanico con botas de compresion secuencial para piernas y abdomen",
        "beneficios": ["Drena liquidos retenidos", "Mejora circulacion", "Reduce celulitis", "Piernas descansadas"],
        "dolor_clienta": "Piernas pesadas, celulitis visible, hinchazon constante, mala circulacion",
        "dato_gancho": "Una sesion de presoterapia equivale a 20 sesiones de drenaje linfatico manual",
        "resultado_esperable": "Piernas mas ligeras y deshinchadas desde la primera sesion",
        "frecuencia": "1-2 sesiones semanales",
        "categoria": "corporal",
        "palabras_clave_copy": ["drenar", "descansar", "piernas ligeras", "bye celulitis"],
    },
    "tratamiento reafirmante": {
        "descripcion": "Protocolo para mejorar la firmeza y elasticidad de la piel corporal con radiofrecuencia y activos",
        "beneficios": ["Piel mas firme", "Reduce flacidez visible", "Estimula colageno corporal", "Mejora textura"],
        "dolor_clienta": "Flacidez tras perdida de peso o post-parto, piel que ha perdido elasticidad, brazos o abdomen 'caidos'",
        "dato_gancho": "Despues de perder 10 kg, la piel tarda hasta 2 anos en adaptarse sola. Con tecnologia, semanas",
        "resultado_esperable": "Piel visiblemente mas firme y tonificada en 6-8 sesiones",
        "frecuencia": "Semanal durante 10-12 sesiones",
        "categoria": "corporal",
        "palabras_clave_copy": ["reafirmar", "tonificar", "recuperar firmeza", "piel elastica"],
    },
    "tratamiento anticelulitis": {
        "descripcion": "Protocolo combinado con ultrasonidos, masaje y activos para reducir celulitis",
        "beneficios": ["Reduce piel de naranja", "Mejora textura de la piel", "Activa circulacion local", "Reafirma"],
        "dolor_clienta": "Celulitis visible en muslos y gluteos, piel de naranja que no mejora con ejercicio, inseguridad en verano",
        "dato_gancho": "El 90% de las mujeres tienen celulitis. Es normal. Pero si te molesta, tiene solucion profesional",
        "resultado_esperable": "Mejora visible de la textura en 8-10 sesiones de protocolo combinado",
        "frecuencia": "2 sesiones semanales durante 10-12 semanas",
        "categoria": "corporal",
        "palabras_clave_copy": ["suavizar", "textura", "piel lisa", "sin complejos"],
    },
}


def buscar_servicio(nombre):
    """Busca un servicio en la base de conocimiento por coincidencia parcial."""
    nombre_lower = nombre.lower().strip()
    if nombre_lower in SERVICIOS_ESTETICOS:
        return SERVICIOS_ESTETICOS[nombre_lower]
    for key, valor in SERVICIOS_ESTETICOS.items():
        if nombre_lower in key or key in nombre_lower:
            return valor
    return None


# ============================================================
# SYSTEM PROMPT PROFESIONAL
# ============================================================

SYSTEM_PROMPT = """Eres el motor de contenido de Esteticai, un agente de IA que genera contenido \
de redes sociales para profesionales de la estetica como si fuera una community manager senior \
con 8 anos de experiencia en el sector belleza.

TU PERSONALIDAD COMO CREADORA DE CONTENIDO:
Eres una profesional que entiende tanto de estetica como de redes sociales. Sabes que detras \
de cada tratamiento hay una mujer que quiere sentirse mejor consigo misma. No vendes \
tratamientos: vendes confianza, resultados reales y el placer de cuidarse. Escribes como \
una persona real, no como un anuncio. Cada palabra tiene intencion.

REGLAS INQUEBRANTABLES DE CONTENIDO:

1. PRIMER RENGLON = GANCHO. Es la linea mas importante de todo el copy. Debe detener el \
scroll en menos de 2 segundos. Usa una de estas 7 formulas de gancho:
   - CURIOSIDAD: pregunta provocadora o dato que rompa expectativas
   - REVELACION: adelanta un resultado sorprendente sin desvelarlo todo
   - NARRATIVO: empieza con una historia real en primera persona
   - LISTA: numero concreto + beneficio ("3 senales de que tu piel necesita ayuda")
   - CONTRAINTUITIVO: contradice una creencia popular ("Limpiar tu piel dos veces al dia puede estar danandola")
   - BENEFICIO: describe el resultado final que la clienta desea
   - URGENCIA: escasez o tiempo limitado (solo cuando sea real, nunca inventar urgencia falsa)

2. ESTRUCTURA DE CADA COPY (framework probado):
   - GANCHO (1-2 lineas): Detener el scroll
   - CUERPO (3-6 lineas): Aportar valor real. Usar una formula de copy:
     * AIDA (Atencion-Interes-Deseo-Accion) para productos y promos
     * PAS (Problema-Agitacion-Solucion) para educativo y tratamientos
     * BAB (Before-After-Bridge) para testimonios y antes/despues
     * STORYTELLING para personal y detras de camaras
   - CTA (1 linea): Llamada a la accion natural y no agresiva

3. LENGUAJE Y TONO:
   - NO uses lenguaje generico de marketing ("descubre el secreto", "no te lo pierdas", \
     "la mejor opcion del mercado")
   - NO uses emojis ni emoticonos de ningun tipo. CERO. Texto limpio, elegante, editorial.
   - SI usa lenguaje sensorial: texturas, sensaciones, imagenes mentales
   - SI usa vocabulario tecnico de estetica cuando aporte credibilidad (principios activos, \
     protocolo, dermis, barrera cutanea) pero siempre explicandolo
   - SI mezcla cercania con autoridad: "soy tu esteticista, no tu vendedora"
   - Varia la longitud: no todos los posts deben ser largos. Un copy corto y contundente \
     puede funcionar mejor que uno largo y generico
   - Usa saltos de linea para que sea facil de leer en el movil. Parrafos de 1-2 lineas max.

4. REGLA 80-20:
   - 80% del contenido debe aportar VALOR (educar, inspirar, conectar)
   - 20% puede ser PROMOCIONAL (vender, ofertar)
   - Incluso el contenido promocional debe aportar informacion util

5. PRUEBA SOCIAL Y CREDIBILIDAD:
   - Cita datos reales cuando sea posible (porcentajes, estudios, numeros de clientas)
   - Referencia la experiencia de la profesional (anos, formaciones, casos)
   - Usa testimonios en tercera persona con detalles concretos (nombre, problema, resultado)
   - NUNCA inventes testimonios. Si no hay datos reales, usa "muchas de mis clientas me dicen..."
   - NUNCA prometas resultados garantizados. Usa "resultados visibles", "mejora significativa"

6. PSICOLOGIA DE VENTA ETICA:
   - ESCASEZ: solo cuando sea real ("quedan 3 huecos esta semana" si es verdad)
   - URGENCIA: solo con fecha real ("hasta el viernes" si hay fecha limite real)
   - PRUEBA SOCIAL: testimonios reales, numeros de clientas, anos de experiencia
   - RECIPROCIDAD: da valor gratis primero (tips, rutinas, educacion) antes de pedir
   - AUTORIDAD: demuestra conocimiento tecnico, formaciones, certificaciones
   - NO uses tacticas manipulativas ni crees urgencia falsa. La confianza se construye a largo plazo.

7. HASHTAGS (formula de 3 niveles):
   - 3-4 de DESCUBRIMIENTO (alto volumen): #skincare, #belleza, #beauty, #selfcare
   - 4-5 de NICHO ESPECIFICO (medio volumen): #esteticafacial, #cuidadodelapiel, #tratamientofacial
   - 2-3 LOCALES o DE MARCA (bajo volumen): #estetica[ciudad], #[nombremarca]
   - Total: 10-12 hashtags. NI MAS NI MENOS.
   - Adapta los hashtags de nicho al servicio concreto del post

8. TIPOS DE CONTENIDO Y SU OBJETIVO:
   - EDUCATIVO: Posicionar como experta. Tips, mitos, explicaciones. Formula PAS.
   - TRATAMIENTO: Explicar un servicio concreto (como funciona, para quien, que esperar). Formula AIDA.
   - ANTES_DESPUES: Prueba social visual. Formula BAB. Con permiso y datos reales.
   - TESTIMONIO: Confianza. Historia real de clienta. Formula STORYTELLING.
   - PRODUCTO: Vender sin vender. Beneficios > caracteristicas. Formula AIDA. Solo para productos (cremas, serums, etc.), NO para tratamientos.
   - DETRAS_DE_CAMARAS: Humanizar. Dia a dia, preparacion, equipo. Formula STORYTELLING.
   - TENDENCIA: Relevancia. Contenido actual adaptado al nicho. Gancho CONTRAINTUITIVO.
   - PROMOCION: Convertir. Oferta concreta con fecha limite. Formula AIDA + URGENCIA.
   - PERSONAL: Conectar. La historia de la profesional, su vocacion. Formula STORYTELLING.

9. FORMATOS Y CUANDO USARLOS:
   - REEL (15-45 seg): Transformaciones, tutoriales rapidos, tendencias. Maximo alcance.
   - CARRUSEL (5-9 slides): Educativo, paso a paso, mitos. Maximo guardados y compartidos.
   - FOTO: Productos, testimonios, frases con imagen de fondo. Engagement medio.
   - STORY: Dia a dia, encuestas, preguntas, ofertas flash. Mantenimiento de comunidad.

10. HORARIOS RECOMENDADOS (datos 2026):
    - Instagram Reels: 18:00-21:00, mejor miercoles y jueves
    - Instagram Carrusel: 11:00-13:00, mejor martes y miercoles
    - TikTok: 12:00, 15:00, 19:00-21:00
    - Facebook: 9:00-13:00
    - Peores dias: sabado y domingo (menor engagement en estetica)

FORMATO DE RESPUESTA:
Responde SIEMPRE en formato JSON valido con esta estructura exacta:
{
  "calendario_semanal": [
    {
      "dia": "Lunes",
      "fecha": "2026-06-22",
      "hora_publicacion": "19:00",
      "red_social": "instagram",
      "tipo_contenido": "EDUCATIVO",
      "formato": "carrusel",
      "formula_copy": "PAS",
      "copy": "El texto completo de la publicacion listo para copiar y pegar...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "cta": "La llamada a la accion",
      "nota_para_la_clienta": "Instruccion practica sobre que foto/video usar y como grabarlo",
      "objetivo": "educar"
    }
  ],
  "estrategia_semanal": "Explicacion de la estrategia de esta semana concreta",
  "metricas_objetivo": "Que metricas observar y que numeros esperar",
  "consejo_de_la_semana": "Un tip concreto y accionable para mejorar sus redes"
}"""


def construir_prompt_usuario(perfil, semana_inicio=None, contenido_extra=None):
    """Construye el prompt de usuario con toda la informacion del perfil y contexto."""
    if semana_inicio is None:
        semana_inicio = datetime.now()

    # Obtener info de pilares segun tipo de negocio
    tipo = perfil.get("tipo_negocio", "Centro de estetica")
    info_pilares = PILARES_POR_TIPO.get(tipo, PILARES_POR_TIPO["Centro de estetica"])

    # Construir contexto de servicios con info tecnica
    servicios_con_contexto = []
    for serv in perfil.get("servicios", []):
        info = buscar_servicio(serv)
        if info:
            servicios_con_contexto.append(
                f"- {serv}: {info.get('descripcion', '')}. "
                f"Dolor de clienta: {info.get('dolor_clienta', '')}. "
                f"Dato gancho: {info.get('dato_gancho', '')}"
            )
        else:
            servicios_con_contexto.append(f"- {serv}")

    servicios_texto = "\n".join(servicios_con_contexto) if servicios_con_contexto else "No especificados"

    # Calcular fechas de la semana
    fechas_semana = []
    dias_nombre = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
    inicio = semana_inicio
    if inicio.weekday() != 0:
        inicio = inicio + timedelta(days=(7 - inicio.weekday()))
    for i in range(6):
        fecha = inicio + timedelta(days=i)
        fechas_semana.append(f"{dias_nombre[i]} {fecha.strftime('%d/%m/%Y')}")

    prompt = f"""Genera el calendario de contenido semanal para este negocio.

PERFIL COMPLETO:
- Negocio: {perfil['nombre_negocio']}
- Propietaria: {perfil.get('propietaria', '')}
- Ciudad: {perfil.get('ciudad', '')}
- Tipo: {tipo}
- Tono: {perfil.get('tono', 'cercano')}
- Valores: {', '.join(perfil.get('valores', [])) or 'No especificados'}
- Publico objetivo: {perfil.get('publico', '') or 'Mujeres interesadas en estetica y cuidado personal'}
- Redes activas: {', '.join(perfil.get('redes', ['Instagram']))}
- Instagram: {perfil.get('instagram_handle', 'No especificado')}
- Pilares de contenido recomendados: {', '.join(info_pilares['pilares'])}

SERVICIOS CON CONTEXTO TECNICO:
{servicios_texto}

PRODUCTOS QUE VENDE: {', '.join(perfil['productos']) if perfil.get('productos') else 'No vende productos'}

SEMANA: {' | '.join(fechas_semana)}
Genera 6 publicaciones (lunes a sabado). Domingo NO se publica.

DISTRIBUCION OBLIGATORIA DE ESTA SEMANA (formula 40-30-20-10):
- 2-3 posts EDUCATIVOS (40%): tips, mitos, explicaciones de tratamientos
- 1-2 posts de CONEXION (30%): detras de camaras, historia personal, equipo
- 1 post de PRUEBA SOCIAL (20%): antes/despues o testimonio
- 0-1 post de CONVERSION (10%): producto o promocion

REGLAS PARA ESTA SEMANA:
- Alterna formatos: minimo 1 reel, 1 carrusel y 1 foto. El resto varia.
- Alterna redes si la clienta tiene mas de una activa
- NO repitas el mismo tipo de contenido dos dias seguidos
- Cada copy debe usar una formula diferente (AIDA, PAS, BAB, STORYTELLING)
- El primer renglon de CADA copy debe ser un gancho que detenga el scroll
- Adapta los horarios segun la red y el formato (reels por la tarde, carruseles al mediodia)
- Los hashtags deben seguir la formula de 3 niveles (descubrimiento + nicho + local)
- El CTA debe ser natural, conversacional, no agresivo
- Incluye nota practica para la clienta: que foto usar, como grabarla, que mostrar"""

    if contenido_extra:
        prompt += f"\n\nCONTEXTO ADICIONAL DE LA CLIENTA:\n{contenido_extra}\n"

    prompt += "\n\nResponde SOLO con el JSON. Sin texto adicional, sin markdown, sin ```."
    return prompt


def generar_contenido_semanal(perfil, api_key=None, contenido_extra=None):
    """Genera el calendario semanal completo."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key or not ANTHROPIC_DISPONIBLE:
        return _generar_demo(perfil)

    client = Anthropic(api_key=key)
    prompt_usuario = construir_prompt_usuario(perfil, contenido_extra=contenido_extra)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4500,
        temperature=0.85,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt_usuario}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        calendario = json.loads(texto)
        return calendario
    except json.JSONDecodeError as e:
        return {"error": str(e), "respuesta_cruda": texto}


def generar_copy_individual(perfil, tipo_contenido, servicio_o_producto,
                            descripcion_foto=None, api_key=None):
    """Genera un copy individual con todo el conocimiento profesional."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key or not ANTHROPIC_DISPONIBLE:
        return _generar_copy_demo(perfil, tipo_contenido, servicio_o_producto)

    client = Anthropic(api_key=key)

    # Obtener info tecnica del servicio
    info_servicio = buscar_servicio(servicio_o_producto)
    contexto_servicio = ""
    if info_servicio:
        contexto_servicio = f"""
INFORMACION TECNICA DEL SERVICIO (usa esto para dar credibilidad y profundidad):
- Descripcion profesional: {info_servicio.get('descripcion', '')}
- Beneficios clave: {', '.join(info_servicio.get('beneficios', []))}
- Dolor de la clienta: {info_servicio.get('dolor_clienta', '')}
- Dato gancho para el hook: {info_servicio.get('dato_gancho', '')}
- Resultado esperable (realista): {info_servicio.get('resultado_esperable', '')}
- Frecuencia recomendada: {info_servicio.get('frecuencia', '')}
- Palabras clave para el copy: {', '.join(info_servicio.get('palabras_clave_copy', []))}
"""

    # Seleccionar formula de copy segun tipo de contenido
    formula_recomendada = "PAS"
    for nombre_formula, datos in FORMULAS_COPY.items():
        if tipo_contenido in datos["ideal_para"]:
            formula_recomendada = nombre_formula
            break

    info_formula = FORMULAS_COPY[formula_recomendada]

    # Seleccionar hashtags relevantes segun categoria del servicio
    categoria = info_servicio.get("categoria", "facial") if info_servicio else "facial"
    hashtags_sugeridos = HASHTAGS_BASE.get(f"nicho_{categoria}", HASHTAGS_BASE["nicho_facial"])

    # Info de pilares
    tipo_negocio = perfil.get("tipo_negocio", "Centro de estetica")
    info_pilares = PILARES_POR_TIPO.get(tipo_negocio, PILARES_POR_TIPO["Centro de estetica"])

    prompt = f"""Genera UN SOLO copy de tipo {tipo_contenido} para redes sociales.

PERFIL DEL NEGOCIO:
- Negocio: {perfil['nombre_negocio']} ({perfil.get('tipo_negocio', '')})
- Propietaria: {perfil.get('propietaria', '')}
- Ciudad: {perfil.get('ciudad', '')}
- Tono: {perfil.get('tono', 'cercano')}
- Valores: {', '.join(perfil.get('valores', [])) or 'No especificados'}
- Publico: {perfil.get('publico', '') or 'Mujeres interesadas en estetica'}
- Redes: {', '.join(perfil.get('redes', ['Instagram']))}
- Instagram: {perfil.get('instagram_handle', '')}
- Tono natural del negocio: {info_pilares['tono_natural']}
- Todos sus servicios: {', '.join(perfil.get('servicios', []))}

SERVICIO/PRODUCTO PARA ESTE COPY: {servicio_o_producto}
{contexto_servicio}

TIPO DE CONTENIDO: {tipo_contenido}

FORMULA DE COPY A USAR: {formula_recomendada} ({info_formula['nombre']})
{info_formula['estructura']}

INSTRUCCIONES ESPECIFICAS:
1. El PRIMER RENGLON debe ser un gancho que detenga el scroll.
   Elige entre: curiosidad, revelacion, narrativo, lista, contraintuitivo, beneficio o urgencia.
   El gancho debe estar relacionado con el dolor o deseo de la clienta, NO ser generico.

2. Escribe el copy como si fueras {perfil.get('propietaria', 'la propietaria')} hablando \
a sus seguidoras. Tono {perfil.get('tono', 'cercano')}.

3. Usa lenguaje sensorial: que la lectora pueda SENTIR el resultado (texturas, sensaciones, \
imagenes mentales). No describas, haz que lo viva.

4. Maximo 2200 caracteres. Ideal: 800-1200 para Instagram, 300-500 para TikTok.

5. NO uses emojis ni emoticonos. CERO. Texto limpio y elegante, estilo editorial.

6. Saltos de linea cada 1-2 frases para legibilidad movil.

7. El CTA debe ser conversacional, no comercial.
   BIEN: "Escribe QUIERO por DM y te cuento mas"
   MAL: "RESERVA YA!!!" o "COMPRA AHORA"

8. Incluye datos o numeros reales cuando sea posible para dar credibilidad.

9. Si es TESTIMONIO: cuenta la historia en tercera persona con detalles concretos.
   Si es EDUCATIVO: aporta un tip que la seguidora pueda aplicar HOY.
   Si es TRATAMIENTO: explica el tratamiento como profesional (que es, como funciona, para quien, \
que esperar). Usa datos tecnicos con lenguaje accesible. NO es lo mismo que PRODUCTO.
   Si es DETRAS_DE_CAMARAS: muestra el lado humano, no el corporativo.
   Si es PRODUCTO: beneficios > caracteristicas. Que sentira la clienta, no que contiene. \
IMPORTANTE: Solo para productos fisicos (cremas, serums, cosmeticos), NO para tratamientos.
   Si es ANTES_DESPUES: describe el proceso y el cambio con respeto y honestidad.
   Si es PROMOCION: justifica la oferta (por que ahora, que incluye, cuanto vale normalmente).

10. HASHTAGS: 3-4 de descubrimiento + 4-5 de nicho ({', '.join(hashtags_sugeridos[:5])}) \
+ 2-3 locales. Total 10-12.
"""
    if descripcion_foto:
        prompt += f"\nFOTO/VIDEO QUE ACOMPANA: {descripcion_foto}\nAdapta el copy a lo que se ve en la imagen/video.\n"

    prompt += """
Responde SOLO con JSON valido (sin markdown, sin ```):
{
  "copy": "El texto completo listo para copiar y pegar",
  "hashtags": ["#hashtag1", "#hashtag2", ...],
  "cta": "La llamada a la accion",
  "formula_usada": "AIDA|PAS|BAB|STORYTELLING",
  "tipo_gancho": "curiosidad|revelacion|narrativo|lista|contraintuitivo|beneficio|urgencia",
  "formato_recomendado": "reel|carrusel|foto|story",
  "hora_recomendada": "19:00",
  "red_social_ideal": "Instagram|TikTok|Facebook",
  "nota_para_la_clienta": "Instruccion practica: que foto/video usar, como grabarlo, que mostrar"
}"""

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2000, temperature=0.85,
        system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}],
    )
    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0].strip()
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
        if "copy" not in resultado or not resultado["copy"]:
            return {"error": "El copy generado esta vacio"}
        if isinstance(resultado.get("hashtags"), str):
            resultado["hashtags"] = [h.strip() for h in resultado["hashtags"].split() if h.startswith("#")]
        return resultado
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"error": "No se pudo parsear la respuesta", "respuesta_cruda": texto[:500]}


# ============================================================
# CONTENIDO DEMO (cuando no hay API key)
# Escrito con calidad profesional real
# ============================================================

def _generar_demo(perfil):
    """Genera calendario demo con calidad profesional."""
    nombre = perfil["nombre_negocio"]
    propietaria = perfil.get("propietaria", "la propietaria")
    ciudad = perfil.get("ciudad", "tu ciudad")
    s1 = perfil["servicios"][0] if perfil.get("servicios") else "Limpieza facial"
    s2 = perfil["servicios"][1] if len(perfil.get("servicios", [])) > 1 else "Hidratacion facial"
    s3 = perfil["servicios"][2] if len(perfil.get("servicios", [])) > 2 else "Radiofrecuencia facial"
    prod = perfil["productos"][0] if perfil.get("productos") else "Serum de vitamina C"
    handle = perfil.get("instagram_handle", "@tunegocio")

    ciudad_tag = ciudad.lower().replace(" ", "") if ciudad and ciudad != "tu ciudad" else "esteticaprofesional"
    nombre_tag = nombre.lower().replace(" ", "") if nombre else "centroestetica"

    return {
        "calendario_semanal": [
            {
                "dia": "Lunes",
                "fecha": "2026-06-22",
                "hora_publicacion": "12:00",
                "red_social": "instagram",
                "tipo_contenido": "EDUCATIVO",
                "formato": "carrusel",
                "formula_copy": "PAS",
                "copy": (
                    f"Tu piel acumula mas de 200 toxinas al dia solo por vivir en ciudad.\n\n"
                    f"No, no es por falta de cremas. Es por falta de limpieza profesional.\n\n"
                    f"Lo que pasa cuando no limpias tu piel en profundidad cada mes:\n"
                    f"Los poros se saturan. La piel se apaga. Los productos que te aplicas "
                    f"no penetran. Y ese brillo que buscas? Queda enterrado bajo capas de "
                    f"contaminacion, maquillaje residual y celulas muertas.\n\n"
                    f"Una {s1.lower()} profesional no es un capricho.\n"
                    f"Es el primer paso de cualquier rutina que funcione.\n\n"
                    f"En {nombre} la hacemos adaptada a tu tipo de piel. "
                    f"Porque una piel seca no se limpia igual que una grasa. "
                    f"Y eso marca toda la diferencia.\n\n"
                    f"Guarda este post y revisalo antes de tu proxima cita."
                ),
                "hashtags": [
                    "#cuidadodelapiel", "#esteticafacial", "#limpiezafacial",
                    "#pielsana", "#skincareroutine", "#cuidadofacial",
                    "#esteticista", "#pielluminosa", "#bellezanatural",
                    f"#estetica{ciudad_tag}",
                ],
                "cta": "Guarda este post. Tu piel te lo agradecera.",
                "nota_para_la_clienta": (
                    "Carrusel de 5-6 slides: portada con frase gancho, 1 slide por consecuencia "
                    "de no limpiar (con iconos simples), slide final con tu contacto. "
                    "Fondo claro, tipografia limpia."
                ),
                "objetivo": "educar",
            },
            {
                "dia": "Martes",
                "fecha": "2026-06-23",
                "hora_publicacion": "19:00",
                "red_social": "instagram",
                "tipo_contenido": "ANTES_DESPUES",
                "formato": "reel",
                "formula_copy": "BAB",
                "copy": (
                    f"Cuando me dijo 'ya he probado de todo', supe que venia al sitio correcto.\n\n"
                    f"ANTES: Manchas en pomulos y frente que llevaban tres anos ahi. "
                    f"Base de maquillaje cada dia para taparlas. Cremas despigmentantes de "
                    f"farmacia que no hacian nada. "
                    f"Y la frustracion de sentir que su cara no era la de antes.\n\n"
                    f"DESPUES (8 semanas de protocolo): Tono uniforme. Luminosidad natural. "
                    f"Y la frase que me dijo en su ultima sesion: "
                    f"'Ya no necesito el corrector'.\n\n"
                    f"No fue magia. Fue un plan personalizado, constancia, y dejar de probar "
                    f"cosas al azar.\n\n"
                    f"Cada piel es diferente. Lo que funciono para ella puede no ser lo tuyo. "
                    f"Por eso siempre empezamos con una valoracion."
                ),
                "hashtags": [
                    "#antesydespues", "#resultadosreales", "#manchasfaciales",
                    "#tratamientoantimanchas", "#pielluminosa", "#esteticafacial",
                    "#skincare", "#cuidadodelapiel", "#bellezareal",
                    f"#estetica{ciudad_tag}",
                ],
                "cta": "Primera valoracion sin compromiso. Escribe VALORACION por DM.",
                "nota_para_la_clienta": (
                    "Reel de 15-30 seg: transicion antes/despues con musica suave. "
                    "Misma luz, mismo angulo, mismo fondo. Pide permiso escrito a la clienta. "
                    "Si no tienes fotos reales aun, usa este copy como plantilla para cuando las tengas."
                ),
                "objetivo": "inspirar",
            },
            {
                "dia": "Miercoles",
                "fecha": "2026-06-24",
                "hora_publicacion": "20:00",
                "red_social": "tiktok" if "TikTok" in perfil.get("redes", []) else "instagram",
                "tipo_contenido": "DETRAS_DE_CAMARAS",
                "formato": "reel",
                "formula_copy": "STORYTELLING",
                "copy": (
                    f"Hay dias en cabina que me recuerdan por que elegi este trabajo.\n\n"
                    f"Hoy fue uno de esos.\n\n"
                    f"8:30 - Llego al centro. Enciendo la musica suave, preparo las cabinas, "
                    f"repaso la agenda. Es mi momento zen antes de que empiece todo.\n\n"
                    f"9:00 - Primera clienta. Una {s1.lower()} que teniamos pendiente. "
                    f"Le noto la piel tirante del verano. Ajusto el protocolo sobre la marcha.\n\n"
                    f"11:30 - Consulta nueva. Viene nerviosa. Le explico todo con calma. "
                    f"Se va con un plan y una sonrisa.\n\n"
                    f"14:00 - Cafe, DMs, pedidos de producto. El trabajo invisible que nadie ve.\n\n"
                    f"16:00 - Tarde de {s3.lower()}. Mi favorito. Ver como la piel responde "
                    f"sesion a sesion es lo que me engancho a esto.\n\n"
                    f"19:30 - Cierro. Limpio. Organizo manana. Y pienso: "
                    f"mola tener un trabajo donde cada dia ayudas a alguien a sentirse mejor."
                ),
                "hashtags": [
                    "#detrasdelascamaras", "#diaenelcentro", "#esteticista",
                    "#vidadeesteticista", "#behindthescenes", "#emprendedora",
                    "#centrodeestetica", "#cuidadodelapiel", "#trabajoconamor",
                    f"#{nombre_tag}",
                ],
                "cta": "Dale a seguir si quieres ver mas de mi dia a dia en cabina.",
                "nota_para_la_clienta": (
                    "Clips cortos del dia: preparando cabina, producto en manos, cafe, "
                    "cerrando el centro. 30-45 seg total. Audio trending o musica suave. "
                    "No necesitas que sea perfecto, la autenticidad vende mas."
                ),
                "objetivo": "conectar",
            },
            {
                "dia": "Jueves",
                "fecha": "2026-06-25",
                "hora_publicacion": "19:00",
                "red_social": "instagram",
                "tipo_contenido": "PRODUCTO",
                "formato": "foto",
                "formula_copy": "AIDA",
                "copy": (
                    f"Sabias que el 80% de los serums de vitamina C que se venden "
                    f"ya estan oxidados cuando los abres?\n\n"
                    f"Es lo primero que miro cuando una clienta me dice "
                    f"'uso vitamina C pero no noto nada'.\n\n"
                    f"Un buen serum de vitamina C deberia:\n"
                    f"- Tener un color claro (si es naranja oscuro, esta oxidado)\n"
                    f"- Venir en envase opaco (la luz lo degrada)\n"
                    f"- Contener al menos un 10% de acido L-ascorbico\n"
                    f"- Combinarse con vitamina E y acido ferulico para mayor eficacia\n\n"
                    f"El que uso en cabina y recomiendo a mis clientas cumple todo esto.\n"
                    f"Y la diferencia en luminosidad se nota desde la primera semana.\n\n"
                    f"Disponible en {nombre}."
                ),
                "hashtags": [
                    "#vitaminac", "#serum", "#cuidadofacial", "#skincare",
                    "#pielluminosa", "#cosmeticaprofesional", "#antiedad",
                    "#rutinafacial", "#activos", "#acidoascorbico",
                    f"#{nombre_tag}",
                ],
                "cta": "Dudas sobre tu serum? Preguntame por DM. Te digo si el tuyo esta bien.",
                "nota_para_la_clienta": (
                    "Foto del producto con luz natural lateral, fondo neutro (blanco o beige). "
                    "Si puedes, pon una gota del serum sobre la mano para mostrar la textura. "
                    "Nada de composiciones recargadas, menos es mas."
                ),
                "objetivo": "vender",
            },
            {
                "dia": "Viernes",
                "fecha": "2026-06-26",
                "hora_publicacion": "13:00",
                "red_social": "instagram",
                "tipo_contenido": "TESTIMONIO",
                "formato": "carrusel",
                "formula_copy": "STORYTELLING",
                "copy": (
                    f"'Llevo toda la vida con la piel grasa y ya me habia resignado.'\n\n"
                    f"Eso me dijo Laura en su primera consulta hace 4 meses.\n\n"
                    f"Habia probado de todo: cremas 'oil-free' que le resecaban la piel, "
                    f"limpiezas agresivas que la dejaban tirante dos dias y luego vuelta a brillar, "
                    f"y productos de farmacia recomendados por internet que le irritaban.\n\n"
                    f"Lo que nadie le habia dicho es que su piel era grasa Y deshidratada a la vez. "
                    f"Parece contradictorio, pero es mucho mas comun de lo que se piensa.\n\n"
                    f"Le disenamos un protocolo que combinaba {s1.lower()} mensual "
                    f"con una rutina en casa de 3 pasos (solo 3, nada mas).\n\n"
                    f"Hoy su piel esta equilibrada. Sigue teniendo tendencia grasa porque eso "
                    f"no se cambia, pero ya no brilla, no tiene brotes, y ha dejado de esconderse "
                    f"detras del maquillaje.\n\n"
                    f"Lo que me dijo la ultima vez: 'Ojala hubiera venido antes'.\n\n"
                    f"Cada piel tiene solucion. A veces solo necesita que alguien la entienda."
                ),
                "hashtags": [
                    "#testimonio", "#clientasatisfecha", "#pielgrasa",
                    "#resultadosreales", "#esteticafacial", "#cuidadodelapiel",
                    "#skincare", "#pielsana", "#bellezareal",
                    f"#estetica{ciudad_tag}",
                    f"#{nombre_tag}",
                ],
                "cta": "Te sientes identificada? Cuentame tu caso por DM. Sin compromiso.",
                "nota_para_la_clienta": (
                    "Carrusel de 4-5 slides: frase destacada de la clienta (con comillas), "
                    "foto del resultado (con permiso), detalle del protocolo simplificado, "
                    "slide final con 'tu piel tambien puede' + contacto. "
                    "Si no tienes testimonio real, adapta con una situacion frecuente de tus clientas."
                ),
                "objetivo": "inspirar",
            },
            {
                "dia": "Sabado",
                "fecha": "2026-06-27",
                "hora_publicacion": "11:00",
                "red_social": "tiktok" if "TikTok" in perfil.get("redes", []) else "instagram",
                "tipo_contenido": "TENDENCIA",
                "formato": "reel",
                "formula_copy": "PAS",
                "copy": (
                    f"Ese serum 'milagroso' de TikTok? Tu esteticista tiene algo que decirte.\n\n"
                    f"Se que es tentador. Un video viral con una piel perfecta y un producto "
                    f"de 12 euros que 'lo cambia todo'. Lo veo cada semana.\n\n"
                    f"El problema no es el producto. Es que no sabes si es para TU piel.\n\n"
                    f"Un acido glicolico al 30% en una piel sensible? Desastre.\n"
                    f"Retinol sin fotoproteccion? Manchas.\n"
                    f"Vitamina C oxidada? Tiraste el dinero.\n\n"
                    f"Antes de comprar lo que sale en tu 'para ti', pregunta a una profesional.\n"
                    f"No porque yo sepa mas que TikTok (bueno, si), sino porque tu piel es unica "
                    f"y lo que le va bien a una influencer con filtro no tiene por que irte bien a ti.\n\n"
                    f"Prueba esto: foto de tu piel sin filtro + DM. "
                    f"Te digo gratis si ese producto es para ti o no."
                ),
                "hashtags": [
                    "#skincaretips", "#tiktokviral", "#consejodeesteticista",
                    "#mitosypiel", "#cuidadodelapiel", "#skincareaddict",
                    "#esteticista", "#bellezareal", "#pielsana",
                    f"#{handle.replace('@', '')}" if handle and handle != "@tunegocio" else f"#{nombre_tag}",
                ],
                "cta": "Comenta con el nombre del producto viral que quieres probar. Te doy mi opinion honesta.",
                "nota_para_la_clienta": (
                    "Reel informal, 20-30 seg. Tu hablando a camara con gesto de 'tengo que decirte algo'. "
                    "Texto superpuesto con los puntos clave. Audio trending si encaja. "
                    "Este tipo de contenido genera mucha conversacion en comentarios."
                ),
                "objetivo": "educar",
            },
        ],
        "estrategia_semanal": (
            f"Semana equilibrada siguiendo la formula 40-30-20-10. Dos posts educativos "
            f"(lunes y sabado) que posicionan a {nombre} como referente. Un antes/despues "
            f"(martes) como prueba social. Un detras de camaras (miercoles) para humanizar. "
            f"Un producto (jueves) como unica pieza de venta directa. Y un testimonio (viernes) "
            f"para cerrar la semana con credibilidad. Los formatos alternan entre carrusel "
            f"(guardados), reel (alcance) y foto (engagement directo)."
        ),
        "metricas_objetivo": (
            "Esta semana observa: tasa de guardados en carruseles (objetivo: >2% de alcance), "
            "DMs recibidos tras CTAs (objetivo: 3-5 por post de conversion), "
            "y compartidos en el reel del sabado (indicador de contenido viral). "
            "Si un tipo de contenido funciona mejor, la proxima semana duplicalo."
        ),
        "consejo_de_la_semana": (
            "Responde TODOS los comentarios en menos de 1 hora. El algoritmo de Instagram "
            "en 2026 premia la velocidad de respuesta: cuanto antes respondas, mas muestra "
            "tu post a nuevos usuarios. Y cada respuesta debe terminar con una pregunta "
            "para generar un segundo comentario. Asi duplicas la conversacion."
        ),
    }


def _generar_copy_demo(perfil, tipo_contenido, servicio_o_producto):
    """Genera un copy demo individual con calidad profesional."""
    nombre = perfil["nombre_negocio"]
    info = buscar_servicio(servicio_o_producto)

    if tipo_contenido == "EDUCATIVO":
        dato = info.get("dato_gancho", "Tu piel te habla cada dia. Solo hay que saber escucharla") if info else "Tu piel te habla cada dia"
        dolor = info.get("dolor_clienta", "problemas de piel que no se resuelven con cremas genericas") if info else "problemas de piel"
        return {
            "copy": (
                f"{dato}.\n\n"
                f"Cada semana recibo clientas con el mismo problema: {dolor}.\n\n"
                f"Y casi siempre el problema es el mismo: estan usando productos "
                f"que no son para su tipo de piel, o los estan usando mal.\n\n"
                f"Aqui van 3 cosas que puedes hacer HOY para mejorar:\n\n"
                f"1. Deja de usar toallitas para desmaquillarte. Doble limpieza: "
                f"primero aceite, despues espuma.\n"
                f"2. No te saltes la proteccion solar. Ni en invierno. Ni en casa.\n"
                f"3. Menos productos, mejor elegidos. Tu piel no necesita 10 pasos, "
                f"necesita los correctos.\n\n"
                f"Si quieres saber cuales son los correctos para ti, preguntame.\n"
                f"En {nombre} siempre empezamos por escuchar a tu piel."
            ),
            "hashtags": [
                "#cuidadodelapiel", "#esteticafacial", "#skincaretips",
                "#pielsana", "#rutinafacial", "#bellezanatural",
                "#esteticista", "#consejodepiel", "#cuidadofacial",
                "#skincare",
            ],
            "cta": "Guarda este post y compartelo con alguien que lo necesite.",
            "formula_usada": "PAS",
            "tipo_gancho": "curiosidad",
            "formato_recomendado": "carrusel",
            "hora_recomendada": "12:00",
            "red_social_ideal": "Instagram",
            "nota_para_la_clienta": (
                "Carrusel de 5 slides: portada con la frase gancho, 1 slide por tip, "
                "slide final con tu contacto. Diseno limpio, colores de tu marca."
            ),
        }

    elif tipo_contenido == "TRATAMIENTO":
        desc = info.get("descripcion", servicio_o_producto) if info else servicio_o_producto
        beneficios = info.get("beneficios", []) if info else []
        resultado = info.get("resultado_esperable", "Resultados visibles desde las primeras sesiones") if info else "Resultados visibles"
        frecuencia = info.get("frecuencia", "") if info else ""
        dolor = info.get("dolor_clienta", "problemas que afectan a tu confianza") if info else "problemas de piel"
        ben_texto = ""
        if beneficios:
            ben_texto = "\n".join(f"- {b}" for b in beneficios[:4])
        return {
            "copy": (
                f"Sabes esa sensacion de '{dolor}'?\n\n"
                f"Es una de las consultas mas frecuentes que recibo. Y tiene solucion.\n\n"
                f"La {servicio_o_producto.lower()} es un {desc.lower()}.\n\n"
                f"Lo que puedes esperar:\n{ben_texto}\n\n"
                f"El resultado: {resultado.lower()}.\n\n"
                f"{'Se recomienda ' + frecuencia.lower() + '.' if frecuencia else ''}\n\n"
                f"En {nombre} cada protocolo es personalizado porque no hay dos pieles iguales.\n\n"
                f"Si tienes dudas sobre si este tratamiento es para ti, escribeme."
            ),
            "hashtags": [
                "#esteticafacial", "#cuidadodelapiel", "#tratamientofacial",
                "#pielsana", "#skincare", "#esteticista",
                "#resultadosreales", "#cuidadopersonal", "#bellezanatural",
                "#esteticaprofesional",
            ],
            "cta": "Primera consulta sin compromiso. Escribe CONSULTA por DM.",
            "formula_usada": "AIDA",
            "tipo_gancho": "curiosidad",
            "formato_recomendado": "carrusel",
            "hora_recomendada": "12:00",
            "red_social_ideal": "Instagram",
            "nota_para_la_clienta": (
                "Carrusel de 5-6 slides: portada con pregunta gancho, 1 slide explicando "
                "el tratamiento, 1-2 slides con beneficios, slide con resultado esperable, "
                "slide final con tu contacto."
            ),
        }

    elif tipo_contenido == "ANTES_DESPUES":
        return {
            "copy": (
                f"Esta foto no tiene filtro. Tiene {servicio_o_producto.lower()} y 6 semanas de constancia.\n\n"
                f"Cuando llego, su principal preocupacion era que ya nada le funcionaba. "
                f"Habia probado cremas, remedios caseros, productos de internet. "
                f"Nada.\n\n"
                f"Lo primero que hice fue escucharla. Despues, analizar su piel "
                f"(no la piel de las revistas, LA SUYA). Y disenamos un plan juntas.\n\n"
                f"No fue un milagro. Fue ciencia, constancia y alguien que supo ver "
                f"lo que su piel necesitaba.\n\n"
                f"El resultado habla solo."
            ),
            "hashtags": [
                "#antesydespues", "#resultadosreales", "#esteticafacial",
                "#cuidadodelapiel", "#skincare", "#pielsana",
                "#bellezareal", "#tratamientofacial", "#cambioreal",
                "#esteticista",
            ],
            "cta": "Quieres saber si este tratamiento es para ti? Escribe QUIERO por DM.",
            "formula_usada": "BAB",
            "tipo_gancho": "revelacion",
            "formato_recomendado": "reel",
            "hora_recomendada": "19:00",
            "red_social_ideal": "Instagram",
            "nota_para_la_clienta": (
                "Reel con transicion antes/despues. Misma luz, mismo angulo, mismo fondo. "
                "15-30 seg. Pide consentimiento escrito a la clienta."
            ),
        }

    else:
        return {
            "copy": (
                f"Hay algo que no te han contado sobre {servicio_o_producto.lower()}.\n\n"
                f"No es solo un tratamiento. Es un plan pensado para TU piel.\n\n"
                f"Lo que hacemos en {nombre} es diferente: primero escuchamos, "
                f"despues analizamos, y solo entonces proponemos. "
                f"Sin promesas vacias. Sin tratamientos genericos.\n\n"
                f"Porque tu piel no es como la de nadie. "
                f"Y tu plan tampoco deberia serlo.\n\n"
                f"Si quieres saber que necesita tu piel de verdad, hablemos."
            ),
            "hashtags": [
                "#esteticafacial", "#cuidadodelapiel", "#skincare",
                "#bellezanatural", "#pielsana", "#esteticista",
                "#tratamientopersonalizado", "#cuidadofacial",
                "#bellezareal", "#esteticaprofesional",
            ],
            "cta": "Escribe INFO por DM y te cuento sin compromiso.",
            "formula_usada": "AIDA",
            "tipo_gancho": "curiosidad",
            "formato_recomendado": "carrusel",
            "hora_recomendada": "19:00",
            "red_social_ideal": "Instagram",
            "nota_para_la_clienta": (
                "Foto de calidad del tratamiento o del espacio. "
                "Luz natural, fondo limpio. Menos es mas."
            ),
        }


def formatear_para_consola(calendario):
    """Formatea el calendario para visualizacion en consola."""
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
        dia_info = f"  {pub['dia'].upper()} | {pub.get('hora_publicacion', '')} | {pub.get('red_social', '')}"
        print(dia_info)
        tipo_info = f"  Tipo: {pub.get('tipo_contenido', '')} | Formato: {pub.get('formato', '')}"
        if pub.get("formula_copy"):
            tipo_info += f" | Formula: {pub['formula_copy']}"
        print(tipo_info)
        print(f"{'~' * 60}")
        print(f"\n{pub.get('copy', '')}")
        print(f"\nHashtags: {' '.join(pub.get('hashtags', []))}")
        print(f"CTA: {pub.get('cta', '')}")
        if pub.get("nota_para_la_clienta"):
            print(f"Nota: {pub['nota_para_la_clienta']}")
    if "metricas_objetivo" in calendario:
        print(f"\n{'=' * 60}")
        print(f"  METRICAS: {calendario['metricas_objetivo']}")
    if "consejo_de_la_semana" in calendario:
        print(f"\n  CONSEJO: {calendario['consejo_de_la_semana']}")
        print(f"{'=' * 60}")


def exportar_a_json(calendario, ruta_archivo):
    """Exporta el calendario a archivo JSON."""
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(calendario, f, ensure_ascii=False, indent=2)
    print(f"\n[Esteticai] Exportado a: {ruta_archivo}")


# ============================================================
# FUNCIONES AUXILIARES PARA OTROS MODULOS
# ============================================================

def obtener_ganchos(tipo="curiosidad", servicio=None):
    """Devuelve ganchos aleatorios para usar en otros modulos."""
    ganchos = GANCHOS_POR_TIPO.get(tipo, GANCHOS_POR_TIPO["curiosidad"])
    gancho = random.choice(ganchos)
    if servicio and "{servicio}" in gancho:
        gancho = gancho.replace("{servicio}", servicio)
    return gancho


def obtener_ctas(objetivo="educar"):
    """Devuelve CTAs aleatorios para usar en otros modulos."""
    ctas = CTAS_POR_OBJETIVO.get(objetivo, CTAS_POR_OBJETIVO["educar"])
    return random.choice(ctas)


def obtener_hashtags(categoria="facial", ciudad=None, marca=None):
    """Construye un set de hashtags para una categoria."""
    resultado = []
    resultado.extend(random.sample(HASHTAGS_BASE["descubrimiento"], min(4, len(HASHTAGS_BASE["descubrimiento"]))))
    nicho_key = f"nicho_{categoria}"
    if nicho_key in HASHTAGS_BASE:
        resultado.extend(random.sample(HASHTAGS_BASE[nicho_key], min(5, len(HASHTAGS_BASE[nicho_key]))))
    else:
        resultado.extend(random.sample(HASHTAGS_BASE["nicho_facial"], 4))
    if ciudad:
        resultado.append(f"#estetica{ciudad.lower().replace(' ', '')}")
    if marca:
        resultado.append(f"#{marca.lower().replace(' ', '')}")
    resultado.extend(random.sample(HASHTAGS_BASE["profesional"], 2))
    return resultado[:12]
