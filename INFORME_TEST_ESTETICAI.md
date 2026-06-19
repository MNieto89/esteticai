# Informe de Pruebas - Esteticai

**URL:** https://esteticai.onrender.com
**Fecha:** 19 de junio de 2026
**Entorno:** Chrome (automatizado), Render.com free tier


## Resumen ejecutivo

Se realizaron 17 pruebas funcionales desde Chrome sobre la plataforma desplegada en Render. La aplicacion funciona correctamente en sus flujos principales (registro, login, perfil, dashboard), pero hay 3 problemas criticos que impiden el uso completo de las herramientas de IA, y varios bugs menores que afectan la experiencia de usuario.

**Resultado global:** 12 pruebas OK, 2 parciales, 3 FAIL


## Resultados por prueba

### Flujo de acceso y autenticacion

**TEST 1 - Landing page:** OK. Carga correctamente con todos los elementos (hero, CTA, demo visual, precios, footer). Colores mint aplicados. Banner de cookies funcional.

**TEST 2 - Pagina de login:** OK. Formulario con email/password, enlaces a registro y recuperacion. Estilos coherentes.

**TEST 3 - Login con credenciales incorrectas:** OK. Muestra error claro "Email o contrasena incorrectos" en rojo. Proteccion anti brute-force activa ("Te quedan 2 intentos antes del bloqueo temporal").

**TEST 4 - Login con cuenta previa (demo.ringana@test.com):** FAIL. La cuenta creada previamente se perdio al reiniciarse el contenedor de Render. Error: "Email o contrasena incorrectos" para credenciales que eran validas. Causa raiz: la base de datos SQLite se almacena en el sistema de archivos efimero del contenedor.

**TEST 5 - Dashboard sin autenticacion:** OK. Redirige correctamente a /login. La proteccion de rutas funciona.

**TEST 6 - Registro de nueva cuenta:** OK. Formulario completo (nombre, email, password, nombre de negocio, ciudad, tipo). Validacion funcional. Registro exitoso con redirect al onboarding.

**TEST 7 - Creacion de perfil y acceso al dashboard:** OK. Tras completar el perfil, el dashboard carga con: saludo personalizado, nombre del negocio, panel de uso (TRIAL PRO, 6 dias), 6 tarjetas de herramientas, banner PWA.

**TEST 8 - Logout:** PARCIAL. Navegar directamente a /logout funciona correctamente (cierra sesion y redirige al home). Sin embargo, el boton "Salir" en la cabecera del dashboard no respondia a clics. Causa: el boton estaba dentro de un form POST que no se enviaba correctamente. CORREGIDO: se ha cambiado a un enlace GET (commit 9b842a3).


### Paginas legales y soporte

**TEST 9 - Recuperar contrasena (/recuperar):** OK. Formulario funcional con campo de email y boton de envio. El envio real de emails requiere RESEND_API_KEY configurada.

**TEST 10 - Politica de privacidad (/privacidad):** OK. Contenido completo y bien estructurado.

**TEST 11 - Politica de cookies (/cookies):** OK. Detalla las cookies utilizadas (sesion y CSRF), con bases legales.

**TEST 12 - Aviso legal (/legal):** OK. Informacion legal completa.


### Dashboard y herramientas

**TEST 13 - Ruta /upgrade sin sesion:** OK. Redirige a login (comportamiento esperado).

**TEST 14 - Re-login con cuenta test@esteticai.com:** OK. Login funciona correctamente. Dashboard carga con todos los datos del perfil.

**TEST 15 - Editar perfil (/perfil/editar):** OK. Muestra el formulario con los datos guardados (nombre, ciudad, tipo de negocio, servicios, productos). Los campos se cargan correctamente.

**TEST 16 - Generar Copy (herramienta IA):** FAIL. Al pulsar "Generar", la API responde con error 500. Mensaje mostrado: "No se pudo generar el copy. Intentalo de nuevo." Causa raiz: ANTHROPIC_API_KEY no esta configurada en las variables de entorno de Render.

**TEST 17 - Pagina 404:** PARCIAL. La pagina se muestra correctamente (titulo, mensaje, boton "Volver al inicio"), pero el icono aparecia como texto literal "&#128269;" en vez de renderizar el simbolo de lupa. Causa: Jinja2 escapaba la entidad HTML. CORREGIDO: se ha anadido el filtro |safe (commit 9b842a3).


## Bugs encontrados y estado

### CRITICO - Sin persistencia de datos

**Descripcion:** La base de datos SQLite se pierde cada vez que el contenedor de Render se reinicia (por inactividad, deploy, o reinicio programado). Todos los usuarios registrados, perfiles y contenido generado se borran.

**Causa:** Render free tier no proporciona disco persistente, aunque render.yaml lo declara (disk: esteticai-data, /data, 1GB). El codigo tiene fallback a sistema de archivos efimero.

**Impacto:** Ningun usuario puede mantener su cuenta activa de forma fiable. Esto invalida la plataforma para cualquier uso real o demo.

**Solucion:** Migrar a un plan de Render con disco persistente (Starter: $7/mes), o migrar la base de datos a un servicio externo (PostgreSQL en Render, Supabase, Neon, etc.).

### CRITICO - Herramientas de IA inoperativas

**Descripcion:** Todas las herramientas que usan IA (Generar Copy, Generar Imagen, Crear Video, Calendario Semanal, Mejorar Foto) devuelven error al intentar generar contenido.

**Causa:** Las variables de entorno necesarias no estan configuradas en Render: ANTHROPIC_API_KEY (para copys y calendario), FAL_KEY (para imagenes y video).

**Impacto:** El valor principal de la plataforma (generacion de contenido con IA) no funciona. Un usuario que se registre no podra usar ninguna herramienta.

**Solucion:** Configurar las API keys en Render Dashboard, en la seccion Environment de esteticai.

### CRITICO - Error 500 sin mensaje util

**Descripcion:** Cuando la API key no esta configurada, el servidor responde con HTTP 500 en vez de un error informativo. El usuario ve un mensaje generico.

**Causa:** El endpoint /api/generar/copy (y similares) lanza una excepcion no controlada cuando intenta crear el cliente Anthropic sin API key.

**Impacto:** Mala experiencia de usuario y dificultad para diagnosticar problemas.

**Solucion:** Anadir validacion previa de la API key antes de intentar usarla, y devolver un HTTP 503 con mensaje explicativo ("Servicio temporalmente no disponible").


### MENOR - Boton "Salir" no funcionaba (CORREGIDO)

**Descripcion:** En el dashboard, el boton "Salir" no cerraba sesion al hacer clic.

**Causa:** Usaba un formulario POST con un boton submit, cuyo evento no se disparaba correctamente.

**Estado:** Corregido en commit 9b842a3. Se sustituyo por un enlace GET, consistente con el resto de paginas.


### MENOR - Icono 404 renderizado como texto (CORREGIDO)

**Descripcion:** La pagina de error 404 mostraba "&#128269;" como texto en vez del icono de lupa.

**Causa:** Jinja2 auto-escapa variables HTML. Faltaba el filtro |safe en error.html.

**Estado:** Corregido en commit 9b842a3.


### MENOR - Iconos inconsistentes en tarjetas del dashboard

**Descripcion:** De las 6 tarjetas de herramientas, solo 2 tienen icono visible (Generar Copy y Mejorar Foto Real). Las otras 4 no muestran icono.

**Impacto:** Inconsistencia visual.


### MENOR - Tilde faltante en "Antes y Despues"

**Descripcion:** La tarjeta dice "Antes y Despues" en vez de "Antes y Despues" (con tilde en la u).

**Impacto:** Error ortografico visible en el dashboard.


### MENOR - Anchor #precios no hace scroll

**Descripcion:** El enlace "Precios" en la cabecera de la landing apunta a /#precios, pero la pagina no hace scroll a la seccion de precios. Carga la parte superior de la pagina.

**Causa probable:** No existe un elemento con id="precios" en el HTML, o el scroll suave no esta implementado.


## Correcciones aplicadas

Se ha creado el commit 9b842a3 con las siguientes correcciones:

1. **web/templates/dashboard.html:** El boton "Salir" pasa de form POST con button submit a un simple enlace `<a href="/logout">`, consistente con todas las demas paginas.

2. **web/templates/error.html:** Se anade filtro `|safe` a la variable `{{ icono }}` para que las entidades HTML se rendericen como iconos.

**Nota:** El commit esta en el repositorio local. Necesita un `git push origin main` desde la terminal para que se despliegue en Render.


## Acciones pendientes (por prioridad)

1. Configurar ANTHROPIC_API_KEY en Render (Dashboard > esteticai > Environment)
2. Configurar FAL_KEY en Render para imagenes y video
3. Evaluar migracion a plan con disco persistente o base de datos externa
4. Hacer `git push origin main` para desplegar las correcciones
5. Anadir iconos a las 4 tarjetas que no los tienen
6. Corregir tilde en "Antes y Despues"
7. Verificar anchor #precios en la landing
8. Mejorar manejo de errores cuando faltan API keys (devolver 503 en vez de 500)
