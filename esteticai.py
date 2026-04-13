#!/usr/bin/env python3
"""
ESTETICAI - Menu Principal v5.0
Contenido + Imagenes automaticas + Video para Reels/TikTok
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.brand_profile import PERFIL_DEMO, crear_perfil
from agents.content_engine import (
    generar_contenido_semanal, generar_copy_individual,
    formatear_para_consola, exportar_a_json,
)
from agents.promos import (
    generar_promo, generar_estrategia_mensual, sugerir_fechas_clave,
    formatear_promo, formatear_estrategia,
)
from agents.image_engine import (
    generar_imagen, generar_imagen_automatica, generar_pack_automatico,
    descargar_imagen, quitar_fondo, listar_presets, listar_tipos_publicacion,
    listar_servicios_conocidos, PROMPTS_ESTETICA, ESTILOS_PUBLICACION,
)
from agents.video_engine import (
    generar_video_desde_imagen, generar_video_automatico,
    descargar_video, listar_movimientos, listar_duraciones,
    MOVIMIENTOS_VIDEO, MOVIMIENTO_RECOMENDADO,
)

# Variable global para recordar la ultima imagen generada
ultima_imagen_url = None

perfil_activo = PERFIL_DEMO

def mostrar_menu():
    global ultima_imagen_url
    print()
    print("=" * 60)
    print(f"  ESTETICAI v5.0 - Contenido + Imagenes + Video")
    print(f"  Clienta: {perfil_activo['nombre_negocio']}")
    print("=" * 60)
    print()
    print("  --- CONTENIDO ---")
    print("  1. Generar calendario semanal")
    print("  2. Generar copy individual")
    print("  3. Generar contenido para promo")
    print("  4. Generar estrategia mensual")
    print()
    print("  --- IMAGENES (automatico) ---")
    print("  5. Generar imagen para publicacion")
    print("  6. Generar pack visual completo")
    print("  7. Foto de producto")
    print()
    print("  --- VIDEO (Reels / TikTok) ---")
    if ultima_imagen_url:
        print("  8. Convertir ultima imagen en video")
    else:
        print("  8. Convertir imagen en video (genera imagen primero)")
    print("  9. Video desde URL de imagen")
    print("  10. Ver movimientos de video disponibles")
    print()
    print("  --- MAS ---")
    print("  11. Quitar fondo a foto real")
    print("  12. Imagen con prompt manual")
    print("  13. Crear nueva clienta / cambiar perfil")
    print("  0. Salir")
    print()


# ============================================================
# OPCIONES DE CONTENIDO (sin cambios)
# ============================================================

def opcion_calendario():
    ctx = input("\nContexto extra (Enter para saltar): ").strip()
    cal = generar_contenido_semanal(perfil=perfil_activo, contenido_extra=ctx if ctx else None)
    formatear_para_consola(cal)
    exportar_a_json(cal, "output/calendario_semanal.json")

def opcion_copy():
    tipos = ["EDUCATIVO", "ANTES_DESPUES", "TESTIMONIO", "PRODUCTO",
             "DETRAS_DE_CAMARAS", "TENDENCIA", "PROMOCION", "PERSONAL"]
    print("\nTipos:")
    for i, t in enumerate(tipos, 1):
        print(f"  {i}. {t}")
    try:
        tipo = tipos[int(input("Tipo: ")) - 1]
    except (ValueError, IndexError):
        tipo = "EDUCATIVO"
    print(f"\nServicios:")
    for i, s in enumerate(perfil_activo['servicios'], 1):
        print(f"  {i}. {s}")
    srv = input("Servicio: ").strip()
    try:
        srv = perfil_activo['servicios'][int(srv) - 1]
    except (ValueError, IndexError):
        pass
    foto = input("Describe foto/video (Enter saltar): ").strip()
    copy = generar_copy_individual(perfil=perfil_activo, tipo_contenido=tipo,
        servicio_o_producto=srv, descripcion_foto=foto if foto else None)
    print(f"\n{'~' * 60}\n{copy.get('copy', '')}\n{'~' * 60}")
    print(f"Hashtags: {' '.join(copy.get('hashtags', []))}")
    print(f"CTA: {copy.get('cta', '')}")

def opcion_promo():
    tipos = ["descuento", "pack", "evento", "fecha_especial", "lanzamiento"]
    print("\n  1.Descuento  2.Pack  3.Evento  4.Fecha especial  5.Lanzamiento")
    try:
        tipo = tipos[int(input("Tipo: ")) - 1]
    except (ValueError, IndexError):
        tipo = "descuento"
    detalles = input("Describe la promo: ").strip() or "20% en faciales esta semana"
    promo = generar_promo(perfil=perfil_activo, tipo_promo=tipo, detalles=detalles)
    formatear_promo(promo)

def opcion_estrategia():
    meses = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    for i, m in enumerate(meses, 1):
        print(f"  {i:2}. {m.capitalize()}")
    try:
        idx = int(input("Mes (Enter=actual): ").strip() or "0") - 1
        mes = meses[idx] if 0 <= idx < 12 else None
    except (ValueError, IndexError):
        mes = None
    ctx = input("Contexto (Enter saltar): ").strip()
    est = generar_estrategia_mensual(perfil=perfil_activo, mes=mes,
        contexto_extra=ctx if ctx else None)
    formatear_estrategia(est)


# ============================================================
# OPCIONES DE IMAGENES - MODO AUTOMATICO
# ============================================================

def _elegir_servicio():
    """Muestra servicios de la clienta y deja elegir."""
    servicios = perfil_activo.get('servicios', [])
    productos = perfil_activo.get('productos', [])
    todos = servicios + productos

    print(f"\nServicios y productos de {perfil_activo['nombre_negocio']}:")
    for i, s in enumerate(todos, 1):
        print(f"  {i}. {s}")

    eleccion = input("\nElige (numero o nombre): ").strip()
    try:
        return todos[int(eleccion) - 1]
    except (ValueError, IndexError):
        return eleccion if eleccion else todos[0]


def _elegir_tipo_publicacion():
    """Muestra tipos de publicacion y deja elegir."""
    tipos = list(ESTILOS_PUBLICACION.keys())
    print("\nTipo de publicacion:")
    nombres_bonitos = {
        "post_feed": "Post para feed (cuadrado)",
        "story": "Story de Instagram/TikTok",
        "reel_portada": "Portada de Reel",
        "carrusel": "Carrusel educativo",
        "antes_despues": "Antes y despues",
        "producto": "Foto de producto",
    }
    for i, tipo in enumerate(tipos, 1):
        nombre = nombres_bonitos.get(tipo, tipo)
        print(f"  {i}. {nombre}")

    try:
        return tipos[int(input("\nTipo: ")) - 1]
    except (ValueError, IndexError):
        return "post_feed"


def opcion_imagen_automatica():
    """Genera imagen automaticamente: elige servicio + tipo y listo."""
    global ultima_imagen_url
    print("\n" + "=" * 50)
    print("  GENERAR IMAGEN AUTOMATICA")
    print("  Solo elige servicio y tipo de post")
    print("=" * 50)

    servicio = _elegir_servicio()
    tipo = _elegir_tipo_publicacion()

    print(f"\n[Esteticai] Generando imagen para: {servicio}")
    print(f"[Esteticai] Tipo de publicacion: {tipo}")
    print(f"[Esteticai] El prompt se genera automaticamente...\n")

    resultado = generar_imagen_automatica(
        servicio=servicio,
        tipo_publicacion=tipo,
        perfil=perfil_activo,
        modo="servicio",
    )

    # Guardar URL para poder convertir a video
    url = resultado.get("url", "")
    if url.startswith("http"):
        ultima_imagen_url = url

    _mostrar_resultado(resultado)

    # Ofrecer convertir a video
    if url.startswith("http"):
        convertir = input("\n  Convertir esta imagen en video para Reels? (s/n): ").strip().lower()
        if convertir == "s":
            _convertir_a_video(url, servicio, tipo)


def opcion_pack_automatico():
    """Genera pack completo de imagenes para una publicacion."""
    print("\n" + "=" * 50)
    print("  PACK VISUAL COMPLETO")
    print("  Genera todas las imagenes para un post")
    print("=" * 50)

    servicio = _elegir_servicio()
    tipo = _elegir_tipo_publicacion()

    resultados = generar_pack_automatico(
        perfil=perfil_activo,
        servicio=servicio,
        tipo_publicacion=tipo,
    )

    print(f"\n{'=' * 50}")
    print(f"  PACK GENERADO: {len(resultados)} imagenes")
    print(f"{'=' * 50}")
    for r in resultados:
        desc = r.get('descripcion', '')
        url = r.get('url', 'N/A')
        if url.startswith("http"):
            print(f"  OK  {desc}")
            print(f"       {url[:70]}")
        else:
            print(f"  --  {desc}: {url[:50]}")


def opcion_foto_producto():
    """Genera foto profesional de un producto especifico."""
    print("\n" + "=" * 50)
    print("  FOTO DE PRODUCTO")
    print("  Genera foto profesional de tus productos")
    print("=" * 50)

    productos = perfil_activo.get('productos', [])
    servicios = perfil_activo.get('servicios', [])

    if productos:
        print(f"\nProductos de {perfil_activo['nombre_negocio']}:")
        for i, p in enumerate(productos, 1):
            print(f"  {i}. {p}")
        print(f"\n  O escribe el nombre de cualquier producto")
        eleccion = input("\nProducto: ").strip()
        try:
            producto = productos[int(eleccion) - 1]
        except (ValueError, IndexError):
            producto = eleccion if eleccion else productos[0]
    else:
        producto = input("\nNombre del producto: ").strip()
        if not producto:
            producto = "crema facial hidratante"

    print(f"\n[Esteticai] Generando foto de producto: {producto}\n")

    resultado = generar_imagen_automatica(
        servicio=producto,
        tipo_publicacion="producto",
        perfil=perfil_activo,
        modo="producto",
    )

    url = resultado.get("url", "")
    if url.startswith("http"):
        global ultima_imagen_url
        ultima_imagen_url = url

    _mostrar_resultado(resultado)

    if url.startswith("http"):
        convertir = input("\n  Convertir en video de producto? (s/n): ").strip().lower()
        if convertir == "s":
            _convertir_a_video(url, producto, "producto")


def _convertir_a_video(url_imagen, servicio, tipo_publicacion):
    """Funcion auxiliar para convertir imagen a video."""
    print(f"\n" + "=" * 50)
    print(f"  CONVIRTIENDO IMAGEN A VIDEO")
    print(f"=" * 50)

    # Elegir movimiento
    mov_recomendado = MOVIMIENTO_RECOMENDADO.get(tipo_publicacion, "zoom_suave")
    mov_desc = MOVIMIENTOS_VIDEO[mov_recomendado]["descripcion"]

    print(f"\n  Movimiento recomendado: {mov_recomendado}")
    print(f"  ({mov_desc})")
    print(f"\n  1. Usar movimiento recomendado")
    print(f"  2. Elegir otro movimiento")

    opcion = input("\n  Elige: ").strip()

    if opcion == "2":
        movs = list(MOVIMIENTOS_VIDEO.keys())
        print()
        for i, m in enumerate(movs, 1):
            print(f"  {i}. {m} - {MOVIMIENTOS_VIDEO[m]['descripcion']}")
        try:
            mov_elegido = movs[int(input("\n  Movimiento: ")) - 1]
        except (ValueError, IndexError):
            mov_elegido = mov_recomendado
    else:
        mov_elegido = mov_recomendado

    # Elegir duracion
    print(f"\n  Duracion:")
    print(f"  1. 5 segundos (story, preview)")
    print(f"  2. 10 segundos (reel corto)")
    try:
        dur_opcion = input("  Elige (Enter=5s): ").strip()
        duracion = 10 if dur_opcion == "2" else 5
    except (ValueError, IndexError):
        duracion = 5

    resultado = generar_video_desde_imagen(
        url_imagen=url_imagen,
        tipo_movimiento=mov_elegido,
        duracion=duracion,
    )

    _mostrar_resultado_video(resultado)


def _mostrar_resultado_video(resultado):
    """Muestra el resultado de una generacion de video."""
    print(f"\n{'=' * 50}")
    if "error" in resultado:
        print(f"  Error: {resultado['error']}")
    else:
        url = resultado.get('url', 'N/A')
        print(f"  Video generado!")
        print(f"  URL: {url}")
        print(f"  Duracion: {resultado.get('duracion', '?')}s")
        print(f"  Movimiento: {resultado.get('prompt_movimiento', '')[:60]}...")
        if url.startswith("http"):
            guardar = input("\n  Descargar video? (s/n): ").strip().lower()
            if guardar == "s":
                descargar_video(url)
    print(f"{'=' * 50}")


def opcion_video_ultima_imagen():
    """Convierte la ultima imagen generada en video."""
    global ultima_imagen_url
    if not ultima_imagen_url:
        print("\n[ERROR] No hay imagen reciente. Genera una imagen primero (opcion 5 o 7).")
        return
    print(f"\n  Imagen a convertir: {ultima_imagen_url[:70]}...")
    _convertir_a_video(ultima_imagen_url, "servicio", "post_feed")


def opcion_video_desde_url():
    """Convierte una imagen desde URL en video."""
    print("\n" + "=" * 50)
    print("  VIDEO DESDE URL DE IMAGEN")
    print("=" * 50)
    url = input("\n  Pega la URL de la imagen: ").strip()
    if not url.startswith("http"):
        print("[ERROR] Necesito una URL que empiece por http")
        return
    _convertir_a_video(url, "personalizado", "post_feed")


def opcion_quitar_fondo():
    print("\n--- Quitar fondo de foto ---")
    print("Arrastra el archivo de imagen a esta ventana:")
    ruta = input("Ruta: ").strip().strip("'\"")
    if not os.path.exists(ruta):
        print(f"[ERROR] No encuentro el archivo: {ruta}")
        return
    quitar_fondo(ruta)


def opcion_imagen_manual():
    """Modo avanzado: imagen con preset manual o prompt libre."""
    print("\n--- Modo avanzado ---")
    print("\n  1. Usar preset de estetica")
    print("  2. Escribir prompt libre")
    modo = input("\nElige: ").strip()

    if modo == "2":
        prompt = input("\nDescribe la imagen que quieres generar:\n> ").strip()
        if not prompt:
            print("[ERROR] Necesito una descripcion.")
            return
        tamano = input("Tamano (square/vertical/story): ").strip() or "square"
        resultado = generar_imagen(prompt_personalizado=prompt, tamano=tamano)
    else:
        listar_presets()
        presets = list(PROMPTS_ESTETICA.keys())
        for i, p in enumerate(presets, 1):
            print(f"  {i}. {p}")
        try:
            preset = presets[int(input("\nPreset: ")) - 1]
        except (ValueError, IndexError):
            preset = "producto_lifestyle"
        import re
        plantilla = PROMPTS_ESTETICA[preset]
        vars_needed = re.findall(r'\{(\w+)\}', plantilla)
        variables = {}
        for v in vars_needed:
            valor = input(f"  {v}: ").strip()
            variables[v] = valor if valor else "beauty treatment"
        tamano = input("Tamano (square/vertical/story): ").strip() or "square"
        resultado = generar_imagen(tipo_preset=preset, variables=variables, tamano=tamano)

    _mostrar_resultado(resultado)


def _mostrar_resultado(resultado):
    """Muestra el resultado de una generacion de imagen."""
    print(f"\n{'=' * 50}")
    if "error" in resultado:
        print(f"  Error: {resultado['error']}")
    else:
        print(f"  Imagen generada!")
        url = resultado.get('url', 'N/A')
        print(f"  URL: {url}")
        if resultado.get("prompt"):
            print(f"  Prompt usado: {resultado['prompt'][:80]}...")
        if url.startswith("http"):
            guardar = input("\n  Descargar imagen? (s/n): ").strip().lower()
            if guardar == "s":
                descargar_imagen(url)
    print(f"{'=' * 50}")


# ============================================================
# CONFIGURACION
# ============================================================

def opcion_nueva_clienta():
    global perfil_activo
    print("\n--- Nueva clienta ---\n")
    nombre = input("Nombre del negocio: ").strip()
    if not nombre:
        print("[ERROR] Nombre obligatorio.")
        return
    propietaria = input("Propietaria: ").strip() or "No especificado"
    ciudad = input("Ciudad: ").strip() or "No especificada"
    tipo = input("Tipo de negocio: ").strip() or "Centro de estetica"

    print("\nServicios (uno por linea, vacia para terminar):")
    servicios = []
    while True:
        s = input("  > ").strip()
        if not s: break
        servicios.append(s)
    if not servicios:
        servicios = ["Tratamiento facial", "Tratamiento corporal"]

    print("\nProductos que vendes (uno por linea, vacia para saltar):")
    productos = []
    while True:
        p = input("  > ").strip()
        if not p: break
        productos.append(p)

    print("\nTono de comunicacion:")
    print("  1. Cercano (como una amiga)")
    print("  2. Profesional (clinica medica)")
    print("  3. Divertido (joven y fresco)")
    tonos = {"1": "cercano", "2": "profesional", "3": "divertido"}
    tono = tonos.get(input("Elige: ").strip(), "cercano")
    handle = input("Instagram (@...): ").strip() or ""

    perfil_activo = crear_perfil(
        nombre_negocio=nombre, propietaria=propietaria,
        ciudad=ciudad, tipo_negocio=tipo, servicios=servicios, tono=tono,
        productos=productos, instagram_handle=handle,
    )
    os.makedirs("config", exist_ok=True)
    fname = f"config/perfil_{nombre.lower().replace(' ', '_')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(perfil_activo, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Clienta: {nombre} | Guardado en {fname}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "#" * 60)
    print("#  ESTETICAI v5.0                                         #")
    print("#  Contenido + Imagenes + Video con IA                    #")
    print("#  Especializado en profesionales de la estetica          #")
    print("#" * 60)

    api_claude = os.environ.get("ANTHROPIC_API_KEY")
    api_fal = os.environ.get("FAL_KEY")
    api_photo = os.environ.get("PHOTOROOM_API_KEY")

    print(f"\n  Claude API:    {'OK' if api_claude else 'NO CONFIGURADA'}")
    print(f"  fal.ai (imgs): {'OK' if api_fal else 'NO CONFIGURADA'}")
    print(f"  Photoroom:     {'OK' if api_photo else 'NO CONFIGURADA (opcional)'}")

    if not api_claude and not api_fal:
        print(f"\n  Para activar todo:")
        print(f"  ANTHROPIC_API_KEY=x FAL_KEY=y python3 esteticai.py")

    while True:
        mostrar_menu()
        op = input("  Opcion: ").strip()
        if op == "1": opcion_calendario()
        elif op == "2": opcion_copy()
        elif op == "3": opcion_promo()
        elif op == "4": opcion_estrategia()
        elif op == "5": opcion_imagen_automatica()
        elif op == "6": opcion_pack_automatico()
        elif op == "7": opcion_foto_producto()
        elif op == "8": opcion_video_ultima_imagen()
        elif op == "9": opcion_video_desde_url()
        elif op == "10": listar_movimientos()
        elif op == "11": opcion_quitar_fondo()
        elif op == "12": opcion_imagen_manual()
        elif op == "13": opcion_nueva_clienta()
        elif op == "0":
            print("\nHasta pronto! Que tus clientas brillen.\n")
            break
        else:
            print("\nOpcion no valida.")
        input("\nEnter para volver al menu...")

if __name__ == "__main__":
    main()
