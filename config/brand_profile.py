"""
PERFIL DE MARCA - Esteticai
============================
Cada clienta tiene su propio perfil de marca.
Modifica PERFIL_DEMO con los datos de tu clienta real.
"""

PERFIL_DEMO = {
    "nombre_negocio": "Clinica Bella Piel",
    "propietaria": "Laura Martinez",
    "ciudad": "Madrid",
    "tipo_negocio": "Clinica de estetica facial y corporal",
    "servicios": [
        "Limpieza facial profunda",
        "Tratamiento antimanchas",
        "Radiofrecuencia facial",
        "Mesoterapia corporal",
        "Depilacion laser",
        "Microblading de cejas",
        "Tratamiento antiedad con acido hialuronico",
        "Masaje drenante linfatico",
    ],
    "productos": [
        "Serum vitamina C propio",
        "Crema hidratante facial",
        "Contorno de ojos antiojeras",
    ],
    "tono": "cercano",
    "valores": [
        "Resultados reales sin cirugia",
        "Tecnologia de vanguardia",
        "Trato personalizado",
        "Belleza natural",
    ],
    "publico": "Mujeres de 30-55 anos preocupadas por el envejecimiento y el cuidado de la piel",
    "redes": ["instagram", "tiktok"],
    "instagram_handle": "@clinicabellapiel",
    "mejores_horarios": {
        "instagram": {"lunes": "19:00", "martes": "12:30", "miercoles": "19:00",
                       "jueves": "20:00", "viernes": "13:00", "sabado": "11:00"},
        "tiktok":    {"lunes": "20:00", "martes": "18:00", "miercoles": "20:00",
                       "jueves": "19:00", "viernes": "17:00", "sabado": "10:00"},
    },
}


def crear_perfil(nombre_negocio, propietaria, ciudad, tipo_negocio, servicios,
                 tono="cercano", productos=None, valores=None, publico=None,
                 redes=None, instagram_handle=None):
    return {
        "nombre_negocio": nombre_negocio,
        "propietaria": propietaria,
        "ciudad": ciudad,
        "tipo_negocio": tipo_negocio,
        "servicios": servicios,
        "productos": productos or [],
        "tono": tono,
        "valores": valores or [],
        "publico": publico or "Mujeres interesadas en estetica y cuidado personal",
        "redes": redes or ["instagram"],
        "instagram_handle": instagram_handle or "",
        "mejores_horarios": {
            "instagram": {"lunes": "19:00", "martes": "12:30", "miercoles": "19:00",
                           "jueves": "20:00", "viernes": "13:00", "sabado": "11:00"},
        },
    }
