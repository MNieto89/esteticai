# PROMPT DE PRODUCCION: Video Demo Esteticai x Ringana

## Contexto estrategico

Este documento contiene los prompts de ingenieria para generar un video demo profesional de 60-90 segundos que simule el funcionamiento de Esteticai adaptado a Ringana. El video es parte de la POC comercial dirigida a una cliente que trabaja para Ringana, una empresa austriaca de cosmetica fresca natural con +100.000 Partners independientes en 38 paises.

El objetivo del video es provocar una reaccion de "necesito esto YA" en la cliente, mostrando como un Partner Ringana real usaria Esteticai en su dia a dia para generar contenido de redes sociales que respete las directrices de marca.

---

## Eleccion de herramienta

### Recomendacion principal: Runway Gen-4.5 (Director Mode)

- Acepta hasta 1.000 caracteres por escena
- Consistencia de personaje del 90% con imagenes de referencia
- Hasta 60 segundos por generacion nativa
- Director Mode 2.0 permite control de camara, planos y composicion
- Calidad cinematografica sin avatares artificiales
- Se complementa con ElevenLabs para voz en off en espanol

### Alternativa A: Veo 3.1 (Google)

- Fotorrealismo del 95% en benchmarks
- Acepta ~1.024 tokens por prompt
- Audio nativo integrado (puede generar ambiente sonoro)
- Clips de 7s extensibles hasta 20 veces
- Ideal si se busca el maximo realismo visual

### Alternativa B: Synthesia + grabacion de pantalla

- Para una demo mas literal con UI real del producto
- Avatar presentador + capturas de pantalla reales de Esteticai
- Script sin limite de longitud
- El script de Synthesia esta al final de este documento (Seccion 4)

### Alternativa C: Kling 3.0 via fal.ai

- Ya integrado en Esteticai (coste cero de setup)
- Hasta 3 minutos de duracion
- Ideal para prototipar rapido antes de invertir en Runway/Veo
- Prompt optimizado para Kling en la Seccion 3

---

## SECCION 1: MASTER PROMPT — Runway Gen-4.5

### Nota de ingenieria

Runway Gen-4.5 rinde mejor con prompts entre 200-400 palabras por escena. El Director Mode permite definir camara, sujeto, ambiente y accion por separado. Para mantener consistencia del personaje principal (la Partner Ringana), se debe usar una imagen de referencia generada previamente con Flux o similar: mujer de 30-35 anos, cabello castano ondulado, maquillaje natural, ropa casual-elegante en tonos neutros/verdes.

El video se compone de 6 escenas de 10-15 segundos cada una, editadas en secuencia con transiciones suaves. Total: ~75 segundos.

---

### ESCENA 1 — El problema (15s)

**Titulo interno:** "La Partner abrumada"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: A woman in her early 30s with wavy brown hair, minimal natural makeup, wearing a sage green linen blouse. She is sitting at a modern white desk in a bright, airy home office. Natural plants on shelves. Soft morning light from a large window.

ACTION: She stares at her laptop screen with a look of creative frustration. Her phone shows Instagram open with zero new posts drafted. She sighs, rubs her temples, picks up a Ringana skincare bottle from the desk and looks at it, then back at the empty screen. She types a few words, then deletes them. Her expression shows she's stuck.

CAMERA: Start with a medium shot from a 45-degree angle showing both her and the desk. Slowly dolly in to a close-up of her face as frustration builds. End on an extreme close-up of the blank content creation screen on her laptop.

MOOD: Warm natural lighting, slightly desaturated colors with green and cream tones. The aesthetic should feel authentic and relatable — not staged or corporate. Think lifestyle documentary.

DETAILS ON DESK: A green Ringana product bottle, a small potted succulent, a notebook with handwritten ideas crossed out, a coffee mug. The desk is slightly cluttered — real, not perfect.
```

**Texto superpuesto (post-produccion):**
> "Cada dia, 100.000 Partners necesitan crear contenido."
> "La inspiracion no siempre llega."

**Audio:** Sonido ambiente suave de oficina en casa. Tecleo esporadico. Un suspiro.

---

### ESCENA 2 — El descubrimiento (10s)

**Titulo interno:** "Esteticai aparece"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: Same woman from Scene 1 (use reference image for consistency). Same sage green blouse, same desk, same setting. Her expression shifts from frustration to curiosity, then to excitement.

ACTION: She opens a new tab on her laptop. The screen glows with a warm pink-and-white interface (Esteticai). Her eyes light up. She leans forward with interest, a slight smile forming. She clicks something on the screen confidently. The Ringana bottle on her desk catches the screen's warm glow.

CAMERA: Over-the-shoulder shot showing the laptop screen (slightly blurred/bokeh) and her profile. Rack focus from the screen to her face as she smiles. The camera is steady, intimate.

MOOD: The lighting subtly warms up compared to Scene 1 — the room feels brighter, more hopeful. The pink glow from the screen adds a gentle color cast to her face.

ENVIRONMENT: Same home office but the atmosphere has shifted. Morning light is now fuller, streaming in more strongly through the window. The plants look greener.
```

**Texto superpuesto:**
> "Hasta que descubres Esteticai."
> "IA especializada en belleza y cosmetica."

**Audio:** Un sutil tono de notificacion positivo. Musica ambiental suave comienza (piano minimalista + pads).

---

### ESCENA 3 — Generacion de contenido (15s)

**Titulo interno:** "La magia en accion"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: Close-up of the woman's hands on the laptop keyboard. Her nails have a natural, clean manicure. She wears a delicate gold bracelet. The laptop screen shows abstract UI elements — text appearing, loading animations, content materializing.

ACTION: Her fingers type a few keystrokes confidently. On screen, text appears rapidly — professional-looking paragraphs with hashtags materialize as if being generated in real time. She pauses, reads, smiles broadly. She clicks a button and a beautiful product image appears on screen. She reacts with genuine delight — mouth slightly open, then a wide smile. She picks up her phone and starts composing an Instagram post.

CAMERA: Start with an extreme close-up of fingers on keyboard. Smooth tilt up to reveal her face showing delight. Then pull back to a medium shot showing her holding her phone next to the laptop, comparing the generated content.

MOOD: Energetic but controlled. The pace quickens slightly compared to previous scenes. Colors are warmer, more vibrant — the pinks and greens from the brand palette are subtly present in the environment (the screen glow, the plants, the product packaging).

CRITICAL DETAIL: The laptop screen should NOT show readable text — keep it slightly out of focus or at an angle that makes specific text illegible while clearly showing the structure of a content generation interface (text blocks, image thumbnails, colored buttons, loading bars).
```

**Texto superpuesto:**
> "Copys profesionales en 5 segundos."
> "Imagenes, videos, calendarios."
> "Todo adaptado a tu marca."

**Audio:** Sonido satisfactorio de "content generated" — un suave chime. Musica sube ligeramente de intensidad.

---

### ESCENA 4 — El contenido cobra vida (15s)

**Titulo interno:** "Resultados profesionales"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: A flat-lay composition on a marble surface. Center: a smartphone showing a beautifully designed Instagram post with a Ringana product photo (green and white aesthetic, natural background). Around the phone: fresh green leaves, a small glass bottle of serum with golden liquid, white flowers, a cotton towel, and scattered natural ingredients (avocado, aloe vera leaf). The overall aesthetic is fresh, natural, premium.

ACTION: The composition is initially static. Then a hand reaches in from the right side and picks up the phone. The camera follows the phone as it's lifted, revealing the Instagram feed with multiple professional-looking posts — each one different, each one on-brand for Ringana. The hand swipes through 3-4 posts. The feed looks cohesive, professional, as if managed by an expert social media team.

CAMERA: Start with a top-down flat-lay shot (directly overhead). As the hand picks up the phone, transition to a 45-degree angle following the phone upward. End with a close-up of the phone screen showing the Instagram grid — all posts looking cohesive and professional.

MOOD: Fresh, vibrant, aspirational. The color palette is dominated by Ringana's green and white with touches of gold and natural textures. Everything feels organic, premium, intentional. This is the "after" — the result of using Esteticai.

LIGHTING: Bright, even, editorial-style lighting. No harsh shadows. The kind of lighting you'd see in a high-end beauty magazine editorial.
```

**Texto superpuesto:**
> "Un feed profesional."
> "Sin community manager."
> "Desde 59 euros al mes."

**Audio:** Musica alcanza su punto mas positivo. Sonidos sutiles de swipe al pasar los posts.

---

### ESCENA 5 — La escala (10s)

**Titulo interno:** "De uno a cien mil"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: Multiple smartphones arranged in a dynamic, cascading composition against a dark forest green background. Each phone shows a different Instagram profile — different Partners, different content, but all with the same cohesive Ringana aesthetic (green, white, natural). The phones are at various angles, some overlapping, creating depth.

ACTION: The phones appear one by one in a cascading effect, each lighting up with a different post. Numbers float subtly in the background: "38 paises", "100K+ Partners", "6 redes sociales". The phones multiply, suggesting infinite scale. Small notification badges (hearts, comments, shares) pop up on each phone, showing engagement.

CAMERA: Start tight on a single phone, then pull back progressively as more phones appear. The camera dollies out smoothly, revealing the full cascade. End with a wide shot showing dozens of phones, all glowing with professional content.

MOOD: Powerful, expansive, slightly dramatic. The dark green background gives premium weight. The glow from the phone screens creates a beautiful array of light. This scene communicates scale and reach.

BACKGROUND: Deep forest green (Ringana brand color #2C5F2D) with subtle organic texture — like a macro shot of a leaf vein pattern, very dark and abstract.
```

**Texto superpuesto:**
> "Escala a toda tu red."
> "100.000 Partners."
> "38 paises."
> "Una sola plataforma."

**Audio:** Musica con mas cuerpo — se anaden cuerdas suaves. Efecto de "whoosh" sutil cada vez que aparece un nuevo telefono.

---

### ESCENA 6 — Cierre con CTA (10s)

**Titulo interno:** "Hagamos que brillen"

```
PROMPT (Runway Gen-4.5 Director Mode):

SUBJECT: Back to the same woman from Scenes 1-3 (reference image for consistency). She is now standing, holding her phone with a confident smile. Behind her, a large window shows a beautiful green garden — nature, freshness, the Ringana ethos. She's added a light cardigan. She looks directly at the camera with warmth and confidence.

ACTION: She looks at her phone one last time, smiles at something she sees (satisfaction with her published content), then looks up directly into the camera. She gives a subtle, knowing nod — as if sharing a secret with the viewer. She raises her phone slightly, showing the screen (blurred, but the green and white Ringana aesthetic is visible). The scene holds on her confident expression.

CAMERA: Medium shot, slightly below eye level (makes the subject look empowered). Very gentle, almost imperceptible slow zoom in toward her face. The background is slightly blurred (f/2.8 depth of field). Hold the final frame for 3 seconds.

MOOD: Warm, empowering, conclusive. The lighting is golden hour — warm, flattering, cinematic. This is the "hero shot" — the Partner Ringana empowered by Esteticai.

ENVIRONMENT: The home office is still visible but the dominant background element is now nature through the window — connecting back to Ringana's brand values of freshness and natural beauty.
```

**Texto superpuesto (motion graphics en post):**
> Logo ESTETICAI x RINGANA
> "Contenido profesional. En segundos. Con IA."
> "Solicita tu demo en vivo → esteticai.com"

**Audio:** Musica resuelve en un acorde final calido. Silencio de 1 segundo. Entonces, un tono suave de "notificacion" — como si un nuevo contenido acabara de generarse.

---

## SECCION 2: PROMPT UNIFICADO PARA VEO 3.1

Veo 3.1 funciona mejor con un unico prompt narrativo de hasta 1.024 tokens. Este prompt condensa las 6 escenas en una narrativa continua.

```
A cinematic mini-film in warm, natural tones with a green and cream color palette. The video follows a woman in her early 30s with wavy brown hair and a sage green linen blouse in her bright, plant-filled home office.

The story arc has three acts:

ACT 1 — FRUSTRATION (0-15s): She sits at her white desk staring at a blank laptop screen. On the desk: a green Ringana skincare bottle, a crossed-out notebook, a coffee mug. She's trying to write an Instagram post but can't find the words. She types, deletes, sighs, rubs her temples. The camera starts at a medium 45-degree angle and slowly dollies into a close-up of her frustrated face. Morning light streams through a large window. The mood is warm but stagnant.

ACT 2 — DISCOVERY AND CREATION (15-45s): She opens a new tab — her face glows with warm pink light from the screen. Her expression shifts from curiosity to genuine excitement. Cut to: extreme close-up of her hands typing confidently on the keyboard. On screen (slightly out of focus), professional text content and beautiful images materialize rapidly. She smiles broadly, picks up her phone and starts comparing content. Cut to: a stunning flat-lay on marble — her phone showing a perfect Instagram post with Ringana products, surrounded by fresh green leaves, serum bottles, white flowers, and natural ingredients. Her hand picks up the phone and swipes through 4 cohesive, professional posts. The camera lifts from top-down to 45-degrees following the phone. The mood is energetic, vibrant — pinks and greens dominate. Editorial beauty lighting.

ACT 3 — EMPOWERMENT (45-60s): Multiple smartphones cascade against a dark forest green background, each showing different but cohesive Ringana content — representing 100,000 Partners worldwide. Phones multiply with engagement notifications popping up. Final shot: the woman stands by the window, golden hour light on her face, looking directly at camera with a warm, confident smile. She holds her phone showing green-and-white content. Slight slow zoom. The mood is empowering and conclusive.

Style: documentary-meets-commercial. Think Apple product launch meets clean beauty brand film. Natural lighting throughout. No harsh edits — smooth, organic transitions. Skin tones warm and natural. The overall feeling is: technology serving humanity's creativity, not replacing it. Aspect ratio 16:9. Cinematic depth of field throughout.
```

---

## SECCION 3: PROMPT OPTIMIZADO PARA KLING 3.0

Kling rinde mejor con prompts de 60-100 palabras y funciona via fal.ai (ya integrado en Esteticai). Para usarlo, se generarian 6 clips cortos de 5-10 segundos y se editarian en secuencia.

### Clip 1 — Frustracion (5s)
```
A woman with wavy brown hair in a sage green blouse sits at a white desk in a bright home office with plants. She stares at a blank laptop screen, looking frustrated and creatively blocked. She sighs and rubs her temples. A green skincare bottle sits on the desk beside a crossed-out notebook. Warm natural morning light from a window. Documentary style, shallow depth of field, slow dolly in.
```

### Clip 2 — Descubrimiento (5s)
```
Same woman at same desk. Her face lights up with curiosity as warm pink light from the laptop screen illuminates her features. She leans forward with a growing smile, her eyes widening with excitement. She clicks something confidently. The room feels warmer and brighter. Over-the-shoulder shot with soft bokeh on the screen. Natural lighting, cinematic.
```

### Clip 3 — Generacion (10s)
```
Extreme close-up of feminine hands with natural manicure and gold bracelet typing on a laptop keyboard. Text and images appear rapidly on the slightly blurred screen — content being generated by AI. The hands pause, the woman's face enters frame as she smiles with genuine delight at what she sees. She picks up her phone. Warm cinematic lighting, shallow focus.
```

### Clip 4 — Resultados (10s)
```
Top-down flat-lay on white marble surface. Center: a smartphone displaying a beautiful Instagram post with green and white skincare product photography. Surrounding the phone: fresh green leaves, a glass serum bottle with golden liquid, white flowers, an aloe vera leaf, a cotton towel. A hand reaches in and picks up the phone, swiping through professional posts. Editorial beauty lighting, bright and even, no harsh shadows.
```

### Clip 5 — Escala (5s)
```
Multiple glowing smartphones arranged in a cascading diagonal pattern against a deep forest green background. Each phone shows a different but cohesive Instagram profile with green-and-white beauty content. Small notification badges with hearts and comments pop up. The phones seem to multiply, suggesting massive scale. Premium, slightly dramatic mood. The green background has subtle organic leaf vein texture.
```

### Clip 6 — Cierre (5s)
```
The same woman with wavy brown hair stands by a large window, golden hour light on her face. Behind her: a lush green garden. She looks at her phone with satisfaction, then looks directly into camera with a warm, confident, knowing smile. Slow, almost imperceptible zoom in. Empowering, cinematic, beautiful. Shallow depth of field, warm color grade.
```

---

## SECCION 4: GUION COMPLETO PARA SYNTHESIA / HEYGEN

Para una demo mas literal con avatar presentador y grabacion de pantalla real del producto.

### Configuracion del avatar

- **Aspecto:** Mujer, 30-35 anos, cabello castano, maquillaje natural
- **Vestimenta:** Blusa verde salvia o blanca (tonos Ringana)
- **Fondo:** Oficina luminosa con plantas o fondo abstracto verde/blanco
- **Tono de voz:** Cercano, profesional, entusiasmado pero no sobreactuado
- **Idioma:** Espanol neutro (o con acento espanol si la cliente es de Espana)

### Guion con timestamps

```
[00:00 - 00:08] ESCENA 1: PRESENTACION DEL PROBLEMA
Avatar en pantalla, medio plano.

AVATAR: "Si eres Partner de Ringana, sabes lo dificil que es mantener
un feed profesional dia tras dia. Pensar que publicar, crear las imagenes,
escribir los textos... todo eso lleva horas. Y necesitas hacerlo cada dia."

Transicion: corte suave a pantalla dividida (avatar izquierda, estadisticas derecha)

[00:08 - 00:15] ESCENA 2: DATOS QUE DUELEN
Avatar en lado izquierdo, infografia animada en lado derecho.

AVATAR: "Ringana tiene mas de cien mil Partners en treinta y ocho paises.
Todos necesitan contenido para redes sociales. Pero la mayoria no son
profesionales de marketing."

Graficos animados: "100K+ Partners" / "38 paises" / "6 redes por semana"

[00:15 - 00:25] ESCENA 3: LA SOLUCION
Pantalla completa del avatar con entusiasmo contenido.

AVATAR: "Por eso creamos Esteticai. Una plataforma de inteligencia artificial
disenada exclusivamente para profesionales de la belleza y la cosmetica natural.
En menos de treinta segundos, genera contenido profesional listo para publicar."

Transicion: el avatar se reduce a esquina inferior derecha, la pantalla muestra
grabacion del dashboard de Esteticai.

[00:25 - 00:40] ESCENA 4: DEMO EN VIVO — GENERANDO UN COPY
Grabacion de pantalla de Esteticai + avatar en esquina.

AVATAR: "Mira. Selecciono mi servicio — por ejemplo, 'cosmetica fresca natural'.
Elijo el tipo de contenido: educativo. Y pulso generar."

(La pantalla muestra el flujo real: seleccionar servicio, tipo, generar.
El skeleton loader aparece. El copy se genera con hashtags, CTA, hora optima.)

AVATAR: "En cinco segundos tengo un copy profesional con hashtags,
llamada a la accion, y la mejor hora para publicarlo. Todo adaptado
al tono de Ringana: natural, fresco, transparente."

[00:40 - 00:52] ESCENA 5: DEMO EN VIVO — IMAGEN + VIDEO
Grabacion de pantalla continua + avatar en esquina.

AVATAR: "Pero no se queda ahi. Puedo generar una imagen profesional
de producto con inteligencia artificial..."

(La pantalla muestra la generacion de imagen: seleccionar formato,
servicio, generar. Una imagen profesional de producto Ringana aparece.)

AVATAR: "...y convertirla en un video para Reels o TikTok con un solo clic.
Siete tipos de movimiento: zoom suave, panoramica, revelacion dramatica..."

(La pantalla muestra el boton "Crear video", la seleccion de movimiento,
el video generandose.)

[00:52 - 01:02] ESCENA 6: DEMO EN VIVO — CALENDARIO SEMANAL
Grabacion de pantalla + avatar en esquina.

AVATAR: "Y mi favorita: el calendario semanal. Un plan completo de siete dias
con que publicar, donde, a que hora, y por que. Exportable a PDF profesional."

(La pantalla muestra el calendario generado: 7 dias con iconos de red social,
tipos de contenido, y el boton de exportar a PDF.)

AVATAR: "Una semana entera de contenido. Generada en diez segundos."

[01:02 - 01:12] ESCENA 7: PROPUESTA DE VALOR
Avatar en pantalla completa, tono conclusivo.

AVATAR: "Imagina esto para toda la red de Partners de Ringana.
Cien mil personas creando contenido profesional cada dia.
Coherente con la marca. Adaptado a su mercado local.
Sin necesidad de un community manager por cada Partner."

Graficos animados: "85% menos tiempo" / "59 euros al mes" / "Contenido ilimitado"

[01:12 - 01:20] ESCENA 8: CIERRE Y CTA
Avatar en pantalla completa con fondo verde Ringana.

AVATAR: "Esteticai y Ringana. Hagamos que cada Partner brille en redes.
Solicita tu demo personalizada en esteticai punto com."

Logo ESTETICAI x RINGANA aparece.
Boton animado: "Solicitar Demo"
```

---

## SECCION 5: NOTAS DE POST-PRODUCCION

### Musica

- **Estilo:** Piano minimalista + pads ambientales. Similar a la musica de anuncios de Apple o de marcas de cosmetica premium (Aesop, Glossier).
- **Progresion:** Comienza suave y contenida (escena 1). Crece gradualmente. Alcanza el pico en escena 4-5. Resuelve con calidez en escena 6.
- **Fuentes:** Epidemic Sound (buscar "minimal piano corporate" o "organic beauty brand"), Artlist, o generar con Udio/Suno con prompt: "Minimal piano ambient track for a clean beauty brand commercial. Warm, hopeful, building gradually. 75 seconds. No vocals."

### Tipografia para overlays

- **Titulos:** Georgia Bold, 48-64pt, blanco con sombra suave
- **Subtitulos:** Calibri Light, 24-32pt, blanco al 90% opacidad
- **Datos/stats:** Georgia Bold, 72-96pt, verde Ringana (#2C5F2D) o rosa Esteticai (#C4748E)
- **CTA final:** Calibri Bold, 36pt, blanco sobre fondo verde Ringana

### Paleta de color para graficos

| Elemento | Color | Hex |
|----------|-------|-----|
| Fondo oscuro | Navy profundo | #1E2761 |
| Acento principal | Verde Ringana | #2C5F2D |
| Acento secundario | Verde moss | #97BC62 |
| Highlight | Rosa Esteticai | #C4748E |
| Textos claros | Blanco | #FFFFFF |
| Textos sobre claro | Negro suave | #1A1A1A |

### Transiciones recomendadas

- Entre escenas: Cross dissolve de 0.5s (nunca corte seco salvo intencion dramatica)
- Para stats/datos: Fade in con ligero scale-up (105% a 100%)
- Para mockups de telefono: Slide-in lateral suave
- Final: Fade to white (0.8s) antes del logo

### Formato de exportacion

- **Resolucion:** 1920x1080 (16:9) como master. Exportar tambien 1080x1920 (9:16) para Stories/Reels y 1080x1080 (1:1) para feed.
- **Codec:** H.264, bitrate 15-20 Mbps
- **Frame rate:** 24fps (look cinematografico) o 30fps (look digital limpio)
- **Subtitulos:** Incrustados (burned-in) en la version 9:16 para consumo en movil sin audio

---

## SECCION 6: PROMPT PARA GENERAR LA IMAGEN DE REFERENCIA DEL PERSONAJE

Para mantener consistencia del personaje principal en Runway Gen-4.5, primero hay que generar una imagen de referencia con Flux (ya integrado en Esteticai via fal.ai).

```
PROMPT PARA FLUX (imagen de referencia):

A professional portrait photograph of a woman in her early 30s. She has
wavy medium-length brown hair, warm brown eyes, light olive skin with a
natural healthy glow, and minimal makeup — just a touch of mascara and
lip tint. She wears a sage green linen blouse with rolled-up sleeves.

She has a warm, approachable smile. The lighting is soft and natural,
coming from a large window to her left. The background is a bright,
modern home office with green plants on white shelves, slightly out of focus.

Style: editorial portrait photography, Canon EOS R5, 85mm f/1.8,
natural lighting, warm tones. The overall feeling is professional yet
approachable — like a successful entrepreneur who values natural beauty
and sustainability.

Do NOT include: heavy makeup, corporate suit, studio backdrop, artificial
lighting, filters, or any text/logos.
```

### Prompt para variaciones de angulo (necesarias para Runway):

```
VARIACION FRONTAL: Same woman, same green blouse, same setting.
Direct eye contact with camera. Slight smile. Shoulders squared.
Shot from chest up. Same natural window lighting.

VARIACION 3/4: Same woman, same outfit. Turned 45 degrees to the right.
Looking at a laptop screen (not visible). Profile showing from left ear
to nose. Same lighting, same setting.

VARIACION MANOS: Close-up of feminine hands with clean, natural manicure
and a thin gold bracelet. The hands are positioned on a laptop keyboard
as if mid-typing. Skin tone matches the woman from the portraits. Same
warm lighting.
```

---

## SECCION 7: CHECKLIST DE PRODUCCION

### Pre-produccion
- [ ] Generar imagen de referencia del personaje con Flux (3 angulos)
- [ ] Seleccionar herramienta principal (Runway / Veo / Synthesia)
- [ ] Preparar capturas de pantalla del dashboard de Esteticai (si se usa Synthesia)
- [ ] Configurar perfil Ringana en Esteticai para las capturas
- [ ] Generar contenido real de Ringana con Esteticai (copys, imagenes) para mostrar en la demo
- [ ] Seleccionar pista musical (Epidemic Sound / Artlist / generar con Suno)

### Produccion
- [ ] Generar los 6 clips con la herramienta elegida
- [ ] Revisar consistencia del personaje entre clips
- [ ] Regenerar clips con problemas de coherencia o calidad
- [ ] Grabar pantalla del dashboard (si se usa enfoque hibrido)
- [ ] Generar voz en off con ElevenLabs (si no se usa Synthesia)

### Post-produccion
- [ ] Editar secuencia en CapCut / Premiere / DaVinci
- [ ] Anadir textos superpuestos segun las indicaciones por escena
- [ ] Anadir musica y sincronizar con cambios de escena
- [ ] Color grading: calidez +10%, saturacion verdes +15%, highlights suaves
- [ ] Exportar en 3 formatos: 16:9, 9:16, 1:1
- [ ] Anadir subtitulos burned-in a la version 9:16
- [ ] Revision final: comprobar que no hay texto de IA visible, que los colores de marca son correctos, que el flow narrativo funciona

### Control de calidad
- [ ] Ver el video SIN audio — la narrativa visual funciona sola?
- [ ] Ver el video SOLO con audio — el audio cuenta la historia?
- [ ] Ensenarlo a alguien que NO conozca Esteticai — entiende que hace el producto?
- [ ] Verificar que ningun frame muestra texto ilegible o artefactos de IA
- [ ] Confirmar que la duracion total esta entre 60-90 segundos
