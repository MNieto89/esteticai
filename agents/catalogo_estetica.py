"""
ESTETICAI - Catalogo Maestro de Estetica Profesional
=====================================================
Base de datos completa de tratamientos y productos cosmeticos
organizada por categorias para que las clientas solo tengan que
elegir de un menu, sin escribir nada.

Estructura:
  CATALOGO_TRATAMIENTOS = {
      "categoria": {
          "nombre": str,       # Nombre para mostrar en el UI
          "icono": str,        # Emoji/icono para la categoria
          "items": [           # Lista de tratamientos
              {
                  "id": str,   # Identificador unico (snake_case)
                  "nombre": str,  # Nombre tal como lo conoce la clienta
                  "tipo_foto": str,  # Para photo_engine (facial/corporal/...)
              }, ...
          ]
      }
  }

  CATALOGO_PRODUCTOS = { misma estructura }

Uso:
  - Dashboard: genera <optgroup> por categoria con <option> por item
  - image_engine: usa el "id" para buscar en CONOCIMIENTO_SERVICIOS
  - photo_engine: usa "tipo_foto" para elegir iluminacion/retoque/fondo
  - perfil_crear: las clientas marcan checkboxes en vez de escribir

Investigacion basada en: webs de centros de estetica en Espana (Dorsia,
Felicidad Carrera, Sapphira, Treatwell), catalogos de distribuidores
profesionales, y menus de servicios reales de clinicas.
"""


# ============================================================
# TRATAMIENTOS
# ============================================================

CATALOGO_TRATAMIENTOS = {
    "facial": {
        "nombre": "Tratamientos faciales",
        "icono": "facial",
        "items": [
            {"id": "limpieza_facial", "nombre": "Limpieza facial profunda", "tipo_foto": "facial"},
            {"id": "limpieza_facial_basica", "nombre": "Limpieza facial basica", "tipo_foto": "facial"},
            {"id": "hidratacion_facial", "nombre": "Hidratacion facial", "tipo_foto": "facial"},
            {"id": "nutricion_facial", "nombre": "Nutricion facial", "tipo_foto": "facial"},
            {"id": "radiofrecuencia_facial", "nombre": "Radiofrecuencia facial", "tipo_foto": "facial"},
            {"id": "microneedling", "nombre": "Microneedling / Dermapen", "tipo_foto": "facial"},
            {"id": "peeling_quimico", "nombre": "Peeling quimico", "tipo_foto": "facial"},
            {"id": "peeling_ultrasonico", "nombre": "Peeling ultrasonico", "tipo_foto": "facial"},
            {"id": "mesoterapia_facial", "nombre": "Mesoterapia facial", "tipo_foto": "facial"},
            {"id": "hidrafacial", "nombre": "HydraFacial", "tipo_foto": "facial"},
            {"id": "oxigenoterapia", "nombre": "Oxigenoterapia facial", "tipo_foto": "facial"},
            {"id": "electroporacion", "nombre": "Electroporacion", "tipo_foto": "facial"},
            {"id": "fototerapia_led", "nombre": "Fototerapia LED", "tipo_foto": "facial"},
            {"id": "tratamiento_acne", "nombre": "Tratamiento anti-acne", "tipo_foto": "facial"},
            {"id": "tratamiento_manchas", "nombre": "Tratamiento antimanchas", "tipo_foto": "facial"},
            {"id": "tratamiento_rosacea", "nombre": "Tratamiento rosacea / cuperosis", "tipo_foto": "facial"},
            {"id": "contorno_ojos", "nombre": "Tratamiento contorno de ojos", "tipo_foto": "facial"},
            {"id": "lifting_facial", "nombre": "Lifting facial sin cirugia", "tipo_foto": "facial"},
            {"id": "facial_flash", "nombre": "Facial flash / express", "tipo_foto": "facial"},
            {"id": "facial_novias", "nombre": "Facial novias / eventos", "tipo_foto": "facial"},
            {"id": "kobido", "nombre": "Masaje Kobido", "tipo_foto": "facial"},
            {"id": "facial_hombre", "nombre": "Facial masculino", "tipo_foto": "facial"},
            {"id": "dermaplaning", "nombre": "Dermaplaning", "tipo_foto": "facial"},
            {"id": "carbon_peel", "nombre": "Carbon Peel / Hollywood Peel", "tipo_foto": "facial"},
            {"id": "tratamiento_poros", "nombre": "Tratamiento minimizador de poros", "tipo_foto": "facial"},
        ],
    },

    "corporal": {
        "nombre": "Tratamientos corporales",
        "icono": "corporal",
        "items": [
            {"id": "masaje_reductor", "nombre": "Masaje reductor", "tipo_foto": "corporal"},
            {"id": "tratamiento_reafirmante", "nombre": "Tratamiento reafirmante", "tipo_foto": "corporal"},
            {"id": "anticelulitico", "nombre": "Tratamiento anticelulitico", "tipo_foto": "corporal"},
            {"id": "drenaje_linfatico", "nombre": "Drenaje linfatico manual", "tipo_foto": "corporal"},
            {"id": "presoterapia", "nombre": "Presoterapia", "tipo_foto": "corporal"},
            {"id": "cavitacion", "nombre": "Cavitacion ultrasonora", "tipo_foto": "corporal"},
            {"id": "radiofrecuencia_corporal", "nombre": "Radiofrecuencia corporal", "tipo_foto": "corporal"},
            {"id": "criolipolisis", "nombre": "Criolipolisis (frio localizado)", "tipo_foto": "corporal"},
            {"id": "carboxiterapia", "nombre": "Carboxiterapia", "tipo_foto": "corporal"},
            {"id": "mesoterapia_corporal", "nombre": "Mesoterapia corporal", "tipo_foto": "corporal"},
            {"id": "vendas_frias", "nombre": "Vendas frias", "tipo_foto": "corporal"},
            {"id": "vendas_calientes", "nombre": "Vendas calientes", "tipo_foto": "corporal"},
            {"id": "maderoterapia", "nombre": "Maderoterapia", "tipo_foto": "corporal"},
            {"id": "vacumterapia", "nombre": "Vacumterapia", "tipo_foto": "corporal"},
            {"id": "tratamiento_estrias", "nombre": "Tratamiento de estrias", "tipo_foto": "corporal"},
            {"id": "exfoliacion_corporal", "nombre": "Exfoliacion corporal", "tipo_foto": "corporal"},
            {"id": "envoltura_corporal", "nombre": "Envoltura corporal", "tipo_foto": "corporal"},
            {"id": "tratamiento_brazos", "nombre": "Tratamiento reafirmante brazos", "tipo_foto": "corporal"},
            {"id": "tratamiento_gluteos", "nombre": "Tratamiento gluteos", "tipo_foto": "corporal"},
            {"id": "post_parto", "nombre": "Tratamiento post-parto", "tipo_foto": "corporal"},
        ],
    },

    "laser": {
        "nombre": "Laser y aparatologia",
        "icono": "laser",
        "items": [
            {"id": "depilacion_laser_diodo", "nombre": "Depilacion laser diodo", "tipo_foto": "corporal"},
            {"id": "depilacion_laser_alejandrita", "nombre": "Depilacion laser alejandrita", "tipo_foto": "corporal"},
            {"id": "depilacion_ipl", "nombre": "Depilacion IPL (luz pulsada)", "tipo_foto": "corporal"},
            {"id": "rejuvenecimiento_laser", "nombre": "Rejuvenecimiento con laser", "tipo_foto": "facial"},
            {"id": "laser_co2", "nombre": "Laser CO2 fraccionado", "tipo_foto": "facial"},
            {"id": "laser_vascular", "nombre": "Laser vascular (varices, aranitas)", "tipo_foto": "corporal"},
            {"id": "laser_manchas", "nombre": "Laser para manchas", "tipo_foto": "facial"},
            {"id": "hifu", "nombre": "HIFU (ultrasonido focado)", "tipo_foto": "facial"},
            {"id": "indiba", "nombre": "INDIBA (radiofrecuencia profunda)", "tipo_foto": "corporal"},
            {"id": "laser_cicatrices", "nombre": "Laser para cicatrices", "tipo_foto": "corporal"},
        ],
    },

    "depilacion": {
        "nombre": "Depilacion",
        "icono": "depilacion",
        "items": [
            {"id": "depilacion_cera_facial", "nombre": "Depilacion con cera (rostro)", "tipo_foto": "facial"},
            {"id": "depilacion_cera_corporal", "nombre": "Depilacion con cera (cuerpo)", "tipo_foto": "corporal"},
            {"id": "depilacion_hilo", "nombre": "Depilacion con hilo", "tipo_foto": "facial"},
            {"id": "depilacion_sugaring", "nombre": "Sugaring (pasta de azucar)", "tipo_foto": "corporal"},
            {"id": "depilacion_electrica", "nombre": "Electrolisis / depilacion electrica", "tipo_foto": "corporal"},
            {"id": "depilacion_piernas", "nombre": "Depilacion piernas completas", "tipo_foto": "corporal"},
            {"id": "depilacion_ingles", "nombre": "Depilacion ingles / brasilena", "tipo_foto": "corporal"},
            {"id": "depilacion_axilas", "nombre": "Depilacion axilas", "tipo_foto": "corporal"},
            {"id": "depilacion_brazos", "nombre": "Depilacion brazos", "tipo_foto": "corporal"},
            {"id": "depilacion_labio", "nombre": "Depilacion labio superior", "tipo_foto": "facial"},
        ],
    },

    "cejas_pestanas": {
        "nombre": "Cejas y pestanas",
        "icono": "cejas",
        "items": [
            {"id": "diseno_cejas", "nombre": "Diseno de cejas", "tipo_foto": "facial"},
            {"id": "tinte_cejas", "nombre": "Tinte de cejas", "tipo_foto": "facial"},
            {"id": "laminado_cejas", "nombre": "Laminado de cejas (brow lamination)", "tipo_foto": "facial"},
            {"id": "microblading", "nombre": "Microblading", "tipo_foto": "facial"},
            {"id": "micropigmentacion_cejas", "nombre": "Micropigmentacion de cejas", "tipo_foto": "facial"},
            {"id": "micropigmentacion_labios", "nombre": "Micropigmentacion de labios", "tipo_foto": "facial"},
            {"id": "micropigmentacion_ojos", "nombre": "Micropigmentacion de ojos (eyeliner)", "tipo_foto": "facial"},
            {"id": "tinte_pestanas", "nombre": "Tinte de pestanas", "tipo_foto": "facial"},
            {"id": "lifting_pestanas", "nombre": "Lifting de pestanas", "tipo_foto": "facial"},
            {"id": "extensiones_pestanas", "nombre": "Extensiones de pestanas", "tipo_foto": "facial"},
            {"id": "extensiones_pelo_pelo", "nombre": "Extensiones pelo a pelo", "tipo_foto": "facial"},
            {"id": "extensiones_volumen", "nombre": "Extensiones efecto volumen", "tipo_foto": "facial"},
            {"id": "retirada_extensiones", "nombre": "Retirada de extensiones", "tipo_foto": "facial"},
        ],
    },

    "unas": {
        "nombre": "Unas y manos",
        "icono": "unas",
        "items": [
            {"id": "manicura_clasica", "nombre": "Manicura clasica", "tipo_foto": "manos_unas"},
            {"id": "manicura_semipermanente", "nombre": "Manicura semipermanente", "tipo_foto": "manos_unas"},
            {"id": "manicura_gel", "nombre": "Unas de gel", "tipo_foto": "manos_unas"},
            {"id": "manicura_acrilico", "nombre": "Unas de acrilico", "tipo_foto": "manos_unas"},
            {"id": "manicura_japonesa", "nombre": "Manicura japonesa (P-Shine)", "tipo_foto": "manos_unas"},
            {"id": "nail_art", "nombre": "Nail art / decoracion de unas", "tipo_foto": "manos_unas"},
            {"id": "pedicura_clasica", "nombre": "Pedicura clasica", "tipo_foto": "manos_unas"},
            {"id": "pedicura_semipermanente", "nombre": "Pedicura semipermanente", "tipo_foto": "manos_unas"},
            {"id": "pedicura_spa", "nombre": "Pedicura spa", "tipo_foto": "manos_unas"},
            {"id": "parafina_manos", "nombre": "Tratamiento de parafina (manos)", "tipo_foto": "manos_unas"},
            {"id": "parafina_pies", "nombre": "Tratamiento de parafina (pies)", "tipo_foto": "manos_unas"},
            {"id": "retirada_semipermanente", "nombre": "Retirada de semipermanente", "tipo_foto": "manos_unas"},
        ],
    },

    "spa": {
        "nombre": "Spa y bienestar",
        "icono": "spa",
        "items": [
            {"id": "masaje_relajante", "nombre": "Masaje relajante", "tipo_foto": "spa_ambiente"},
            {"id": "masaje_descontracturante", "nombre": "Masaje descontracturante", "tipo_foto": "spa_ambiente"},
            {"id": "masaje_deportivo", "nombre": "Masaje deportivo", "tipo_foto": "corporal"},
            {"id": "masaje_piedras_calientes", "nombre": "Masaje con piedras calientes", "tipo_foto": "spa_ambiente"},
            {"id": "masaje_bambu", "nombre": "Masaje con canas de bambu", "tipo_foto": "spa_ambiente"},
            {"id": "masaje_aromaterapia", "nombre": "Masaje con aromaterapia", "tipo_foto": "spa_ambiente"},
            {"id": "masaje_prenatal", "nombre": "Masaje prenatal", "tipo_foto": "spa_ambiente"},
            {"id": "reflexologia", "nombre": "Reflexologia podal", "tipo_foto": "spa_ambiente"},
            {"id": "circuito_termal", "nombre": "Circuito termal / aguas", "tipo_foto": "spa_ambiente"},
            {"id": "ritual_spa", "nombre": "Ritual spa completo", "tipo_foto": "spa_ambiente"},
            {"id": "sauna", "nombre": "Sauna / bano turco", "tipo_foto": "spa_ambiente"},
            {"id": "flotarium", "nombre": "Flotarium / flotacion", "tipo_foto": "spa_ambiente"},
            {"id": "chocoterapia", "nombre": "Chocoterapia", "tipo_foto": "spa_ambiente"},
            {"id": "vinoterapia", "nombre": "Vinoterapia", "tipo_foto": "spa_ambiente"},
        ],
    },

    "maquillaje": {
        "nombre": "Maquillaje",
        "icono": "maquillaje",
        "items": [
            {"id": "maquillaje_social", "nombre": "Maquillaje social / evento", "tipo_foto": "facial"},
            {"id": "maquillaje_novias", "nombre": "Maquillaje de novia", "tipo_foto": "facial"},
            {"id": "maquillaje_editorial", "nombre": "Maquillaje editorial / moda", "tipo_foto": "facial"},
            {"id": "automaquillaje", "nombre": "Clase de automaquillaje", "tipo_foto": "facial"},
            {"id": "maquillaje_natural", "nombre": "Maquillaje natural / no-makeup", "tipo_foto": "facial"},
            {"id": "maquillaje_fantasia", "nombre": "Maquillaje fantasia / artistico", "tipo_foto": "facial"},
        ],
    },

    "medicina_estetica": {
        "nombre": "Medicina estetica",
        "icono": "medicina",
        "items": [
            {"id": "botox", "nombre": "Toxina botulinica (Botox)", "tipo_foto": "facial"},
            {"id": "acido_hialuronico", "nombre": "Acido hialuronico (rellenos)", "tipo_foto": "facial"},
            {"id": "aumento_labios", "nombre": "Aumento de labios", "tipo_foto": "facial"},
            {"id": "ojeras", "nombre": "Relleno de ojeras", "tipo_foto": "facial"},
            {"id": "hilos_tensores", "nombre": "Hilos tensores", "tipo_foto": "facial"},
            {"id": "plasma_rico", "nombre": "Plasma rico en plaquetas (PRP)", "tipo_foto": "facial"},
            {"id": "bioestimulacion", "nombre": "Bioestimulacion con vitaminas", "tipo_foto": "facial"},
            {"id": "rinomodelacion", "nombre": "Rinomodelacion sin cirugia", "tipo_foto": "facial"},
            {"id": "bichectomia", "nombre": "Bichectomia", "tipo_foto": "facial"},
            {"id": "peeling_medico", "nombre": "Peeling medico profundo", "tipo_foto": "facial"},
            {"id": "escleroterapia", "nombre": "Escleroterapia (varices)", "tipo_foto": "corporal"},
            {"id": "lipolisis", "nombre": "Lipolisis inyectable", "tipo_foto": "corporal"},
        ],
    },
}


# ============================================================
# PRODUCTOS COSMETICOS
# ============================================================

CATALOGO_PRODUCTOS = {
    "limpieza": {
        "nombre": "Limpieza facial",
        "icono": "limpieza",
        "items": [
            {"id": "agua_micelar", "nombre": "Agua micelar", "tipo_foto": "producto"},
            {"id": "gel_limpiador", "nombre": "Gel limpiador", "tipo_foto": "producto"},
            {"id": "leche_limpiadora", "nombre": "Leche limpiadora", "tipo_foto": "producto"},
            {"id": "espuma_limpiadora", "nombre": "Espuma limpiadora", "tipo_foto": "producto"},
            {"id": "aceite_limpiador", "nombre": "Aceite desmaquillante", "tipo_foto": "producto"},
            {"id": "tonico_facial", "nombre": "Tonico facial", "tipo_foto": "producto"},
            {"id": "exfoliante_facial", "nombre": "Exfoliante facial", "tipo_foto": "producto"},
            {"id": "desmaquillante_ojos", "nombre": "Desmaquillante de ojos", "tipo_foto": "producto"},
        ],
    },

    "hidratacion": {
        "nombre": "Hidratacion",
        "icono": "hidratacion",
        "items": [
            {"id": "crema_hidratante", "nombre": "Crema hidratante", "tipo_foto": "producto"},
            {"id": "serum_hidratante", "nombre": "Serum hidratante", "tipo_foto": "producto"},
            {"id": "mascarilla_hidratante", "nombre": "Mascarilla hidratante", "tipo_foto": "producto"},
            {"id": "bruma_facial", "nombre": "Bruma / spray facial", "tipo_foto": "producto"},
            {"id": "crema_nutritiva", "nombre": "Crema nutritiva", "tipo_foto": "producto"},
            {"id": "gel_aloe_vera", "nombre": "Gel de aloe vera", "tipo_foto": "producto"},
            {"id": "aceite_facial", "nombre": "Aceite facial", "tipo_foto": "producto"},
            {"id": "balsamo_labial", "nombre": "Balsamo labial", "tipo_foto": "producto"},
        ],
    },

    "antiedad": {
        "nombre": "Antienvejecimiento",
        "icono": "antiedad",
        "items": [
            {"id": "crema_antiarrugas", "nombre": "Crema antiarrugas", "tipo_foto": "producto"},
            {"id": "serum_retinol", "nombre": "Serum de retinol", "tipo_foto": "producto"},
            {"id": "contorno_ojos_prod", "nombre": "Contorno de ojos", "tipo_foto": "producto"},
            {"id": "serum_colageno", "nombre": "Serum de colageno", "tipo_foto": "producto"},
            {"id": "crema_reafirmante_facial", "nombre": "Crema reafirmante facial", "tipo_foto": "producto"},
            {"id": "serum_vitamina_c", "nombre": "Serum de vitamina C", "tipo_foto": "producto"},
            {"id": "acido_hialuronico_topico", "nombre": "Serum de acido hialuronico", "tipo_foto": "producto"},
            {"id": "mascarilla_antiedad", "nombre": "Mascarilla antiedad", "tipo_foto": "producto"},
            {"id": "crema_cuello_escote", "nombre": "Crema cuello y escote", "tipo_foto": "producto"},
            {"id": "ampollas_flash", "nombre": "Ampollas flash / efecto inmediato", "tipo_foto": "producto"},
        ],
    },

    "proteccion_solar": {
        "nombre": "Proteccion solar",
        "icono": "solar",
        "items": [
            {"id": "protector_solar_facial", "nombre": "Protector solar facial SPF50", "tipo_foto": "producto"},
            {"id": "protector_solar_corporal", "nombre": "Protector solar corporal", "tipo_foto": "producto"},
            {"id": "protector_con_color", "nombre": "Protector solar con color", "tipo_foto": "producto"},
            {"id": "protector_oil_free", "nombre": "Protector solar oil-free", "tipo_foto": "producto"},
            {"id": "after_sun", "nombre": "After sun / post-solar", "tipo_foto": "producto"},
            {"id": "autobronceador", "nombre": "Autobronceador", "tipo_foto": "producto"},
        ],
    },

    "tratamiento_activos": {
        "nombre": "Serums y activos",
        "icono": "activos",
        "items": [
            {"id": "serum_niacinamida", "nombre": "Serum de niacinamida", "tipo_foto": "producto"},
            {"id": "serum_acido_salicilico", "nombre": "Serum de acido salicilico", "tipo_foto": "producto"},
            {"id": "serum_acido_glicolico", "nombre": "Serum de acido glicolico", "tipo_foto": "producto"},
            {"id": "serum_peptidos", "nombre": "Serum de peptidos", "tipo_foto": "producto"},
            {"id": "serum_bakuchiol", "nombre": "Serum de bakuchiol", "tipo_foto": "producto"},
            {"id": "serum_ferulico", "nombre": "Serum ferulico", "tipo_foto": "producto"},
            {"id": "serum_antimanchas", "nombre": "Serum antimanchas", "tipo_foto": "producto"},
            {"id": "serum_calmante", "nombre": "Serum calmante / anti-rojeces", "tipo_foto": "producto"},
            {"id": "peeling_casero", "nombre": "Peeling quimico domiciliario", "tipo_foto": "producto"},
            {"id": "parches_acne", "nombre": "Parches anti-acne", "tipo_foto": "producto"},
        ],
    },

    "corporal_producto": {
        "nombre": "Cuidado corporal",
        "icono": "corporal_prod",
        "items": [
            {"id": "crema_anticelulitica", "nombre": "Crema anticelulitica", "tipo_foto": "producto"},
            {"id": "crema_reductora", "nombre": "Crema reductora", "tipo_foto": "producto"},
            {"id": "crema_reafirmante_corp", "nombre": "Crema reafirmante corporal", "tipo_foto": "producto"},
            {"id": "aceite_corporal", "nombre": "Aceite corporal", "tipo_foto": "producto"},
            {"id": "exfoliante_corporal_prod", "nombre": "Exfoliante corporal", "tipo_foto": "producto"},
            {"id": "crema_manos", "nombre": "Crema de manos", "tipo_foto": "producto"},
            {"id": "crema_pies", "nombre": "Crema de pies", "tipo_foto": "producto"},
            {"id": "gel_piernas_cansadas", "nombre": "Gel piernas cansadas", "tipo_foto": "producto"},
            {"id": "crema_estrias", "nombre": "Crema antiestrias", "tipo_foto": "producto"},
            {"id": "desodorante_natural", "nombre": "Desodorante natural", "tipo_foto": "producto"},
        ],
    },

    "capilar": {
        "nombre": "Cuidado capilar",
        "icono": "capilar",
        "items": [
            {"id": "champu", "nombre": "Champu profesional", "tipo_foto": "producto"},
            {"id": "acondicionador", "nombre": "Acondicionador", "tipo_foto": "producto"},
            {"id": "mascarilla_capilar", "nombre": "Mascarilla capilar", "tipo_foto": "producto"},
            {"id": "serum_capilar", "nombre": "Serum capilar / aceite", "tipo_foto": "producto"},
            {"id": "tratamiento_anticaida", "nombre": "Tratamiento anticaida", "tipo_foto": "producto"},
            {"id": "protector_termico", "nombre": "Protector termico", "tipo_foto": "producto"},
            {"id": "champu_matizador", "nombre": "Champu matizador", "tipo_foto": "producto"},
        ],
    },

    "maquillaje_producto": {
        "nombre": "Maquillaje",
        "icono": "maquillaje_prod",
        "items": [
            {"id": "base_maquillaje", "nombre": "Base de maquillaje", "tipo_foto": "producto"},
            {"id": "corrector", "nombre": "Corrector / concealer", "tipo_foto": "producto"},
            {"id": "polvo_fijador", "nombre": "Polvo fijador", "tipo_foto": "producto"},
            {"id": "iluminador", "nombre": "Iluminador / highlighter", "tipo_foto": "producto"},
            {"id": "colorete", "nombre": "Colorete / blush", "tipo_foto": "producto"},
            {"id": "paleta_sombras", "nombre": "Paleta de sombras", "tipo_foto": "producto"},
            {"id": "mascara_pestanas", "nombre": "Mascara de pestanas", "tipo_foto": "producto"},
            {"id": "labial", "nombre": "Labial / lipstick", "tipo_foto": "producto"},
            {"id": "primer", "nombre": "Primer / prebase", "tipo_foto": "producto"},
            {"id": "spray_fijador", "nombre": "Spray fijador de maquillaje", "tipo_foto": "producto"},
        ],
    },

    "accesorios": {
        "nombre": "Accesorios y herramientas",
        "icono": "accesorios",
        "items": [
            {"id": "rodillo_jade", "nombre": "Rodillo de jade / cuarzo", "tipo_foto": "producto"},
            {"id": "gua_sha", "nombre": "Gua sha", "tipo_foto": "producto"},
            {"id": "cepillo_facial", "nombre": "Cepillo limpiador facial", "tipo_foto": "producto"},
            {"id": "parches_ojos", "nombre": "Parches de ojos", "tipo_foto": "producto"},
            {"id": "mascarilla_tejido", "nombre": "Mascarilla de tejido / sheet mask", "tipo_foto": "producto"},
            {"id": "esponja_maquillaje", "nombre": "Esponja de maquillaje", "tipo_foto": "producto"},
            {"id": "vaporizador_facial", "nombre": "Vaporizador facial", "tipo_foto": "producto"},
            {"id": "lampara_led", "nombre": "Lampara LED portatil", "tipo_foto": "producto"},
        ],
    },
}


# ============================================================
# FUNCIONES DE ACCESO
# ============================================================

def obtener_tratamientos_para_select():
    """
    Devuelve la estructura lista para generar <select> con <optgroup>.
    Formato: [{"grupo": "Tratamientos faciales", "opciones": [{"valor": "id", "texto": "nombre"}, ...]}]
    """
    grupos = []
    for cat_id, cat in CATALOGO_TRATAMIENTOS.items():
        grupo = {
            "grupo": cat["nombre"],
            "cat_id": cat_id,
            "opciones": [
                {"valor": item["id"], "texto": item["nombre"]}
                for item in cat["items"]
            ],
        }
        grupos.append(grupo)
    return grupos


def obtener_productos_para_select():
    """
    Devuelve la estructura lista para generar <select> con <optgroup>.
    """
    grupos = []
    for cat_id, cat in CATALOGO_PRODUCTOS.items():
        grupo = {
            "grupo": cat["nombre"],
            "cat_id": cat_id,
            "opciones": [
                {"valor": item["id"], "texto": item["nombre"]}
                for item in cat["items"]
            ],
        }
        grupos.append(grupo)
    return grupos


def obtener_todo_para_select():
    """
    Devuelve tratamientos + productos en una sola estructura para
    generar un <select> unificado (usado en Generar Imagen, Copy, etc.)
    """
    grupos = []
    # Primero tratamientos
    for cat_id, cat in CATALOGO_TRATAMIENTOS.items():
        grupo = {
            "grupo": cat["nombre"],
            "cat_id": cat_id,
            "tipo": "tratamiento",
            "opciones": [
                {"valor": item["id"], "texto": item["nombre"], "tipo_foto": item["tipo_foto"]}
                for item in cat["items"]
            ],
        }
        grupos.append(grupo)
    # Luego productos
    for cat_id, cat in CATALOGO_PRODUCTOS.items():
        grupo = {
            "grupo": cat["nombre"] + " (producto)",
            "cat_id": cat_id,
            "tipo": "producto",
            "opciones": [
                {"valor": item["id"], "texto": item["nombre"], "tipo_foto": item["tipo_foto"]}
                for item in cat["items"]
            ],
        }
        grupos.append(grupo)
    return grupos


def buscar_item(item_id):
    """
    Busca un item por su ID en todo el catalogo.
    Devuelve el dict del item + su categoria, o None.
    """
    for cat_id, cat in CATALOGO_TRATAMIENTOS.items():
        for item in cat["items"]:
            if item["id"] == item_id:
                return {**item, "categoria": cat_id, "tipo": "tratamiento"}
    for cat_id, cat in CATALOGO_PRODUCTOS.items():
        for item in cat["items"]:
            if item["id"] == item_id:
                return {**item, "categoria": cat_id, "tipo": "producto"}
    return None


def buscar_por_nombre(nombre):
    """
    Busca un item por nombre (coincidencia parcial, case-insensitive).
    Util para compatibilidad con servicios escritos a mano.
    """
    nombre_lower = nombre.strip().lower()
    for catalogo in (CATALOGO_TRATAMIENTOS, CATALOGO_PRODUCTOS):
        for cat_id, cat in catalogo.items():
            for item in cat["items"]:
                if item["nombre"].lower() == nombre_lower:
                    return {**item, "categoria": cat_id}
                if nombre_lower in item["nombre"].lower():
                    return {**item, "categoria": cat_id}
    return None


def obtener_tipo_foto(item_id_o_nombre):
    """
    Dado un ID o nombre de tratamiento/producto, devuelve el tipo_foto
    para usar con photo_engine (facial, corporal, producto, etc.)
    """
    item = buscar_item(item_id_o_nombre)
    if not item:
        item = buscar_por_nombre(item_id_o_nombre)
    if item:
        return item.get("tipo_foto", "default")
    return "default"


# Contadores para verificacion
def _stats():
    """Estadisticas del catalogo."""
    t_items = sum(len(c["items"]) for c in CATALOGO_TRATAMIENTOS.values())
    p_items = sum(len(c["items"]) for c in CATALOGO_PRODUCTOS.values())
    return {
        "categorias_tratamientos": len(CATALOGO_TRATAMIENTOS),
        "categorias_productos": len(CATALOGO_PRODUCTOS),
        "total_tratamientos": t_items,
        "total_productos": p_items,
        "total_items": t_items + p_items,
    }
