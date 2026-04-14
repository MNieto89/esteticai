"""
PERFIL DE MARCA - RINGANA
==========================
Ejemplo completo con productos REALES de Ringana.
Cosmetica natural fresca austriaca + suplementos.
Datos actualizados con catalogo real.
"""

PERFIL_RINGANA = {
    "nombre_negocio": "Ringana - Cosmetica Fresca Natural",
    "propietaria": "Partner Ringana",
    "ciudad": "Madrid",
    "tipo_negocio": "Distribucion de cosmetica natural fresca y suplementos veganos",

    # =========================================================
    # PRODUCTOS REALES - LINEA FRESH (Cosmetica)
    # =========================================================
    "productos_fresh": [
        # --- Limpieza ---
        {
            "nombre": "FRESH cleanser",
            "categoria": "limpieza",
            "descripcion": "Leche limpiadora facial suave que limpia en profundidad, hidrata y unifica el tono de la piel",
            "uso": "Limpieza diaria manana y noche",
        },
        {
            "nombre": "FRESH tonic pure",
            "categoria": "limpieza",
            "descripcion": "Tonico facial purificante para equilibrar el pH de la piel tras la limpieza",
            "uso": "Despues del cleanser, manana y noche",
        },
        {
            "nombre": "FRESH tonic calm",
            "categoria": "limpieza",
            "descripcion": "Tonico facial calmante para pieles sensibles o reactivas",
            "uso": "Despues del cleanser, manana y noche",
        },
        # --- Tratamiento facial ---
        {
            "nombre": "FRESH hydro serum",
            "categoria": "tratamiento",
            "descripcion": "Serum hidratante con acido hialuronico natural. Textura ligera como agua pero potentemente hidratante, se absorbe al instante",
            "uso": "Antes de la crema, manana y noche",
        },
        {
            "nombre": "FRESH eye serum",
            "categoria": "tratamiento",
            "precio": "49.70 EUR",
            "descripcion": "Serum para contorno de ojos con efecto refrescante, descongestivo y reafirmante",
            "uso": "Aplicar con suaves toques alrededor del ojo",
        },
        {
            "nombre": "FRESH skin perfection",
            "categoria": "tratamiento",
            "precio": "89.90 EUR",
            "descripcion": "Tratamiento antiedad premium. Cierra poros y unifica el tono sin quimicos agresivos. El producto estrella de Ringana",
            "uso": "Como mascarilla o tratamiento intensivo",
        },
        {
            "nombre": "FRESH overnight face treatment",
            "categoria": "tratamiento",
            "precio": "81.40 EUR",
            "descripcion": "Tratamiento facial nocturno de alta gama. Regenera la piel mientras duermes",
            "uso": "Aplicar por la noche como ultimo paso de la rutina",
        },
        # --- Cremas faciales ---
        {
            "nombre": "FRESH cream light",
            "categoria": "crema facial",
            "descripcion": "Crema hidratante ligera ideal para pieles mixtas o grasas y dias calurosos. Textura fresca y no comedogenica",
            "uso": "Hidratacion diaria para piel mixta/grasa",
        },
        {
            "nombre": "FRESH cream medium",
            "categoria": "crema facial",
            "descripcion": "Crema hidratante equilibrada, ni grasa ni ligera. La mas versatil, ideal para pieles normales o mixtas",
            "uso": "Hidratacion diaria todo-terreno",
        },
        {
            "nombre": "FRESH cream rich",
            "categoria": "crema facial",
            "descripcion": "Crema nutritiva y densa para pieles secas. Ideal en invierno, con calefaccion o tras viajes",
            "uso": "Hidratacion diaria para piel seca",
        },
        # --- Proteccion solar y color ---
        {
            "nombre": "FRESH tinted moisturiser SPF 15",
            "categoria": "color y proteccion",
            "descripcion": "Hidratante con color y proteccion solar. Unifica el tono con pigmentos minerales. Alternativa ligera al maquillaje. Disponible en varias tonalidades",
            "uso": "Hidratacion diaria con color y proteccion",
        },
        {
            "nombre": "FRESH sunscreen",
            "categoria": "proteccion solar",
            "descripcion": "Protector solar natural con filtros minerales",
            "uso": "Proteccion solar diaria",
        },
        # --- Cuidado especial ---
        {
            "nombre": "FRESH enzyme peeling",
            "categoria": "exfoliacion",
            "descripcion": "Peeling enzimatico suave para renovar la piel sin agresion mecanica",
            "uso": "1-2 veces por semana",
        },
        {
            "nombre": "FRESH lip balm",
            "categoria": "labios",
            "descripcion": "Balsamo labial nutritivo con ingredientes naturales",
            "uso": "Hidratacion labial diaria",
        },
        {
            "nombre": "FRESH tooth oil",
            "categoria": "higiene bucal",
            "descripcion": "Aceite dental natural para una higiene bucal completa. Innovacion de Ringana en cuidado oral",
            "uso": "Higiene bucal diaria",
        },
        # --- Cuidado corporal ---
        {
            "nombre": "FRESH body cream",
            "categoria": "corporal",
            "descripcion": "Crema corporal nutritiva con ingredientes frescos y naturales",
            "uso": "Hidratacion corporal tras la ducha",
        },
        {
            "nombre": "FRESH hand serum",
            "categoria": "corporal",
            "descripcion": "Serum para manos con textura ligera y absorcion rapida",
            "uso": "Cuidado de manos diario",
        },
        {
            "nombre": "FRESH shower gel",
            "categoria": "corporal",
            "descripcion": "Gel de ducha natural con ingredientes frescos",
            "uso": "Limpieza corporal diaria",
        },
        {
            "nombre": "FRESH deodorant",
            "categoria": "corporal",
            "descripcion": "Desodorante natural sin aluminio ni quimicos agresivos",
            "uso": "Proteccion diaria",
        },
    ],

    # =========================================================
    # PRODUCTOS REALES - LINEA CAPS (Suplementos)
    # =========================================================
    "productos_caps": [
        {
            "nombre": "CAPS beauty & hair",
            "descripcion": "Fortalece piel, cabello, unas y tejido conectivo desde dentro. Con acido hialuronico, biotina, zinc, SOD y extracto de manzana",
        },
        {
            "nombre": "CAPS immu",
            "descripcion": "Setas medicinales y micronutrientes naturales que refuerzan el sistema inmunitario en epocas de estres",
        },
        {
            "nombre": "CAPS fem",
            "descripcion": "Formulado para la salud femenina en distintas etapas. Con extracto de Shatavari para equilibrio hormonal durante menstruacion y menopausia",
        },
        {
            "nombre": "CAPS mascu",
            "descripcion": "Suplemento especifico para la salud masculina",
        },
        {
            "nombre": "CAPS move",
            "descripcion": "Para mejorar la movilidad y salud articular. Ideal para personas activas",
        },
        {
            "nombre": "CAPS moodoo",
            "descripcion": "Promueve el equilibrio emocional, reduce el cansancio y mejora el bienestar diario. Vegano y sin gluten ni alergenos",
        },
        {
            "nombre": "CAPS push",
            "descripcion": "Energia y concentracion mental para jornadas intensas de trabajo",
        },
        {
            "nombre": "CAPS protect",
            "descripcion": "Proteccion celular con antioxidantes naturales",
        },
        {
            "nombre": "CAPS d-gest",
            "descripcion": "Apoyo para la digestion y salud intestinal",
        },
        {
            "nombre": "CAPS hydro",
            "descripcion": "Hidratacion desde dentro para piel y organismo",
        },
        {
            "nombre": "CAPS cerebro",
            "descripcion": "Apoyo para la funcion cognitiva y concentracion",
        },
        {
            "nombre": "CAPS pump",
            "descripcion": "Suplemento para el sistema cardiovascular",
        },
        {
            "nombre": "BEYOND omega",
            "descripcion": "Omega-3 vegano de alta calidad con enfoque holistico y sostenible",
        },
        {
            "nombre": "BEYOND biotic",
            "descripcion": "Probioticos para la salud de la flora intestinal",
        },
        {
            "nombre": "BEYOND spermidine",
            "descripcion": "Espermidina natural para el rejuvenecimiento celular",
        },
        {
            "nombre": "PACK antiox",
            "descripcion": "Pack antioxidante completo con metabolitos secundarios, vitaminas y minerales para proteger las celulas del estres oxidativo",
        },
    ],

    # =========================================================
    # PRODUCTOS LEGACY (formato simplificado para el motor de contenido)
    # =========================================================
    "productos": [
        "FRESH skin perfection (tratamiento antiedad premium, 89.90 EUR)",
        "FRESH hydro serum (serum hidratante con acido hialuronico natural)",
        "FRESH eye serum (contorno de ojos reafirmante, 49.70 EUR)",
        "FRESH overnight face treatment (regeneracion nocturna, 81.40 EUR)",
        "FRESH cream light / medium / rich (cremas faciales para cada tipo de piel)",
        "FRESH cleanser (leche limpiadora suave)",
        "FRESH tinted moisturiser SPF 15 (hidratante con color)",
        "CAPS beauty & hair (suplemento para piel, cabello y unas)",
        "CAPS immu (refuerzo del sistema inmunitario)",
        "CAPS fem (equilibrio hormonal femenino)",
        "CAPS moodoo (equilibrio emocional y bienestar)",
        "BEYOND omega (omega-3 vegano)",
    ],

    "servicios": [
        "Consultoria personalizada de skincare natural",
        "Rutinas de cuidado facial con productos frescos",
        "Tratamientos antiedad con ingredientes naturales",
        "Cuidado corporal con cosmetica vegana",
        "Suplementacion natural con CAPS y BEYOND",
        "Asesoramiento de belleza sostenible",
    ],

    "tono": "cercano",

    "valores": [
        "Frescura real: productos con fecha de caducidad (cosmetica 6 meses sin abrir, 10 semanas abierto; suplementos 12 meses)",
        "100% vegano y cruelty-free",
        "Sin conservantes anadidos, parabenos, siliconas ni microplasticos",
        "Ingredientes naturales de alta calidad",
        "Sostenibilidad: packaging reciclable y envases retornables (economia circular)",
        "Ciencia austriaca combinada con naturaleza",
    ],

    "publico": "Mujeres de 25-50 anos interesadas en cosmetica natural, sostenibilidad y bienestar. Conscientes del medio ambiente, buscan productos que funcionen sin quimicos agresivos. Tambien hombres interesados en suplementacion natural.",

    "redes": ["instagram", "tiktok"],
    "instagram_handle": "@ringana.partner",

    "diferenciadores": [
        "Unica marca que pone fecha de caducidad a sus cosmeticos como prueba de frescura",
        "Fabricacion en Austria con ingredientes frescos de origen natural",
        "Sin conservantes artificiales: si tu crema no caduca, preguntate que lleva dentro",
        "Fundada en 1996 por Andreas Wilfinger en Hartberg, Austria",
        "Economia circular: envases retornables y packaging sostenible",
        "Mas de 1.000 ingredientes activos naturales en su catalogo",
    ],

    "mensajes_clave": [
        "Si tu crema no caduca, preguntate que lleva dentro",
        "Frescura que se nota en tu piel",
        "Ciencia austriaca + naturaleza = resultados reales",
        "No es magia, es frescura real con fecha de caducidad",
        "Tu piel merece ingredientes que esten vivos",
    ],

    "mejores_horarios": {
        "instagram": {
            "lunes": "19:00", "martes": "12:30", "miercoles": "19:00",
            "jueves": "20:00", "viernes": "13:00", "sabado": "11:00",
        },
        "tiktok": {
            "lunes": "20:00", "martes": "18:00", "miercoles": "20:00",
            "jueves": "19:00", "viernes": "17:00", "sabado": "10:00",
        },
    },
}
