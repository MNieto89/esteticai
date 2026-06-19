# Analisis: Prompt Optimo para Fotografia de Producto con IA

## El problema actual

La funcion `generar_prompt_automatico` tiene una unica rama para productos:

```
"Luxury beauty product photo: {productos_tipicos}.
On elegant marble surface, {colores} tones,
soft natural light, shallow depth of field, 4K commercial quality."
```

Este prompt genera imagenes genericas porque no describe el envase real. Dice QUE productos fotografiar, pero no COMO son esos productos fisicamente. fal.ai no puede adivinar que un "serum de vitamina C" viene en un frasco cuentagotas de vidrio ambar de 30ml con etiqueta blanca minimalista.


## Taxonomia completa de variables para producto

### 1. Forma del envase

El envase es la variable con mas impacto visual. Un mismo producto ("crema hidratante") puede venir en formatos radicalmente distintos.

**Tipo de contenedor:** botella, tarro/bote, tubo, frasco con bomba/pump, cuentagotas/dropper, spray, ampolla, stick, sobre/sachet, caja, tubo de carton (como los CAPS de Ringana).

**Forma geometrica:** cilindrico, rectangular, cuadrado, conico, esferico, ovalado, estrechado en la cintura, forma ergonomica. Ejemplo Ringana: siempre cilindrico, proporciones esbeltas.

**Proporciones:** alto y estrecho vs bajo y ancho. Un serum suele ser alto-estrecho; una crema, bajo-ancha. Esto cambia completamente la silueta del producto en la foto.

**Tamano relativo:** indicar altura aproximada o volumen ayuda a la IA a escalar correctamente ("15cm tall", "50ml jar", "travel size").


### 2. Material y acabado

**Material:** vidrio transparente, vidrio esmerilado, vidrio coloreado, plastico mate, plastico brillante, ceramica, metal (aluminio, acero), carton, bambu. Ringana usa exclusivamente vidrio transparente para cosmetica.

**Transparencia:** transparente (se ve el producto dentro), translucido (se intuye), opaco (no se ve nada). La transparencia de Ringana es su senal de identidad: "nada que esconder".

**Acabado superficial:** mate, brillante/glossy, satinado, metalizado, holografico, texturizado, grabado en relieve.


### 3. Esquema de color

Esta es la variable que mas diferencia una marca de otra.

**Color del cuerpo:** el color dominante del envase.
**Color del cierre/tapa:** frecuentemente distinto al cuerpo.
**Color de la etiqueta:** fondo de la etiqueta.
**Color del texto:** tipicamente negro, blanco, gris o metalizado.
**Acentos:** detalles decorativos, lineas, bordes.

Ejemplo Ringana FRESH: cuerpo transparente (vidrio), pump plateado/metalico, etiqueta blanca minimalista, texto gris sans-serif, sin acentos de color.

Ejemplo Ringana CAPS: cuerpo de color solido (cada variante un color distinto), texto blanco, tapa del mismo color, acabado mate.


### 4. Cierre/tapa

**Tipo:** bomba/pump (dispensador), tapa rosca, cuentagotas, pulverizador spray, flip-top, presion, push-button, tapa plana.

**Material del cierre:** plastico, metal, bambu.

**Color del cierre:** blanco, negro, plateado, dorado, transparente, mismo color que el cuerpo.

El tipo de cierre cambia significativamente la silueta del producto y su posicionamiento (un pump sugiere serum/limpiador; una tapa rosca sugiere crema/balsamo).


### 5. Etiqueta y branding

**Tipo de etiqueta:** impresa directamente sobre el envase, etiqueta de papel pegada, pegatina transparente, grabado/embossing, sin etiqueta (solo serigrafía).

**Colocacion:** centro-frontal, envolvente (wrap-around), tercio inferior, cobertura completa.

**Tipografia:** sans-serif (moderno, limpio), serif (clasico, premium), script (artesanal), handwritten (natural). Ringana: siempre sans-serif, lowercase o small caps.

**Jerarquia de texto:**
- Nombre de marca: posicion y tamano
- Nombre de producto: estilo (una palabra, descriptivo, codificado)
- Subtexto: ingredientes clave, volumen, claims

**Estilo del logo:** minimalista, geometrico, organico, emblema. Ringana: hoja verde pequena, muy discreto.


### 6. Producto visible

Cuando el envase es transparente o semi-transparente, el producto de dentro es un elemento visual fundamental.

**Color del producto:** crema blanca, liquido transparente, aceite dorado, gel rosado, liquido verde, polvo blanco.

**Textura visible:** crema espesa, liquido fino, gel, aceite, espuma, polvo, capsulas.

Ejemplo: el cleanser de Ringana muestra un liquido ligeramente verdoso (clorofila) a traves del vidrio transparente. Esto es un detalle que transforma la foto.


### 7. Configuracion fotografica

**Angulo de camara:**
- Hero shot (45 grados desde arriba): el mas versatil y comercial
- Eye level (recto): dramatico, editorial
- Top-down (cenital): flat lay, lifestyle
- 3/4 frontal: muestra volumen y profundidad

**Iluminacion:**
- Difusa suave: estandar comercial, sin sombras duras
- Lateral dramatica: crea volumen y textura
- Contraluz (backlit): hace brillar productos transparentes -- ideal para Ringana
- Natural de ventana: lifestyle, calido

**Fondo:**
- Blanco infinito: catalogo, e-commerce
- Marmol: lujo
- Madera: natural, eco
- Botanico: con plantas, hojas, ingredientes
- Gradiente suave: moderno, redes sociales
- Contextual: bano, tocador, spa

**Props/atrezo:**
- Ingredientes (hojas, flores, frutas, semillas)
- Texturas (tela de lino, piedra, arena)
- Gotas de agua (frescura)
- Otro producto de la misma linea (coherencia de marca)
- Manos de modelo (uso del producto)

**Profundidad de campo:**
- Superficial (producto nitido, fondo difuso): el estandar para producto
- Profunda (todo nitido): catalogo, e-commerce


### 8. Posicionamiento de marca

**Estetica general:**
- Lujo (La Mer, Chanel Beauty): fondos oscuros, iluminacion dramatica, dorados
- Eco/natural (Ringana, Lush, Aesop): materiales naturales, luz natural, vegetacion
- Clinico/farmaceutico (La Roche-Posay, CeraVe): fondo blanco, limpio, cientifico
- Artesanal (marcas indie): texturas rusticas, packaging craft
- Minimalista premium (Glossier, The Ordinary): tipografia limpia, fondo blanco, sin ruido


## Arquitectura de prompt propuesta

### Estructura del prompt en 5 bloques

```
[TIPO DE FOTO] + [DESCRIPCION FISICA DEL ENVASE] + [SETUP FOTOGRAFICO] + [AMBIENTE Y PROPS] + [CALIDAD TECNICA]
```

**Bloque 1 - Tipo de foto:**
"Commercial product photography of a single beauty product"

**Bloque 2 - Descripcion fisica (el mas importante):**
"Tall cylindrical clear glass bottle, approximately 15cm height,
transparent body showing pale golden serum inside,
silver metallic airless pump dispenser,
minimalist white label with small grey sans-serif lowercase text,
small green leaf logo near bottom"

**Bloque 3 - Setup fotografico:**
"Hero angle from slightly above, soft diffused studio lighting,
subtle backlight making the glass glow, shallow depth of field"

**Bloque 4 - Ambiente y props:**
"On light marble surface, single eucalyptus branch nearby,
clean neutral background with soft gradient"

**Bloque 5 - Calidad tecnica:**
"4K commercial quality, beauty magazine editorial style,
photorealistic, sharp focus on product"


### Prompt ejemplo completo para Ringana FRESH hydro serum

```
Commercial beauty product photography of a single skincare bottle.
Tall cylindrical clear glass bottle approximately 15cm height,
transparent body showing pale golden liquid serum inside,
silver metallic airless pump dispenser mechanism on top,
minimalist white paper label with small grey sans-serif lowercase text
reading product name, tiny green leaf icon near the bottom of the label,
pharmaceutical-luxe minimalist aesthetic.
Hero angle from slightly above and to the right,
soft diffused studio lighting with subtle backlight making the glass glow
and the serum inside shimmer, shallow depth of field.
Placed on light natural stone surface, single fresh eucalyptus sprig nearby,
clean warm neutral background with soft gradient.
4K commercial quality, beauty magazine editorial style, photorealistic,
premium eco-luxury brand aesthetic similar to Aesop.
```


## Flujo de implementacion propuesto

### Paso 1: Busqueda web del producto
Cuando la clienta escribe "crema hidratante Ringana" o "serum vitamina C de [marca]", el sistema busca en internet informacion visual del producto.

### Paso 2: Extraccion de caracteristicas visuales
Claude (el agente de texto de Esteticai) analiza los resultados de busqueda y extrae las caracteristicas fisicas del producto en formato estructurado:
- tipo_envase, forma, material, transparencia
- color_cuerpo, color_tapa, color_etiqueta
- tipo_cierre, tipo_etiqueta, tipografia
- producto_visible, color_producto
- estetica_marca

### Paso 3: Construccion del prompt
Con las caracteristicas estructuradas, la funcion construye un prompt de 5 bloques optimizado para generar una imagen lo mas fiel posible al producto real.

### Paso 4: Generacion
Se envia a fal.ai y se obtiene una imagen realista del producto descrito.


## Variables que mas impacto tienen (por orden)

1. Tipo y forma del envase (define la silueta)
2. Material y transparencia (define la textura visual)
3. Esquema de colores (define la identidad de marca)
4. Tipo de cierre (define la parte superior, muy visible)
5. Iluminacion (contraluz para vidrio transparente, difusa para mate)
6. Producto visible dentro del envase (da realismo y color)
7. Estilo de etiqueta y tipografia (identidad de marca)
8. Props y fondo (contexto y atmosfera)


## Consideraciones tecnicas

### Limitaciones de fal.ai / Flux
- Flux no genera texto legible de forma consistente. Las etiquetas con texto real suelen salir distorsionadas. Es mejor pedir "label with small text" sin especificar palabras exactas.
- Los reflejos en vidrio son un punto fuerte de Flux Pro 1.1.
- Los prompts mas largos y descriptivos dan mejores resultados que los cortos y ambiguos.
- Especificar "single product" evita que genere multiples botellas.

### Texto en etiquetas
Como Flux no genera texto fiable, la estrategia es:
- Describir el ESTILO del texto ("grey sans-serif lowercase") sin pedir texto especifico
- Pedir "minimal label with subtle text" en vez de "label that says RINGANA"
- Si la clienta necesita texto exacto, se puede anadir en post-produccion (Canva, etc.)
