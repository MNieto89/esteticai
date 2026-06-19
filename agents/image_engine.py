"""
MOTOR DE IMAGENES - Esteticai v2.0
====================================
Genera y transforma imagenes para redes sociales usando:
- fal.ai (Flux) para generar imagenes desde cero
- Photoroom para quitar/cambiar fondos de fotos reales
- Sistema de prompts automaticos inteligentes

REQUISITOS:
  pip3 install fal-client requests
  API keys:
    - fal.ai: https://fal.ai/dashboard/keys
    - Photoroom (opcional): https://www.photoroom.com/api
"""

import os
import json
import requests
from datetime import datetime

try:
    import fal_client
    FAL_DISPONIBLE = True
except ImportError:
    FAL_DISPONIBLE = False
    print("[INFO] fal-client no instalado. pip3 install fal-client")


# ============================================================
# BASE DE CONOCIMIENTO DE ESTETICA
# Cada tratamiento describe la ESCENA REAL: como se ve en cabina,
# que equipo se usa, que hace la esteticista, que ve la clienta.
# El agente genera prompts fieles a la realidad, sin inventar nada.
# ============================================================

CONOCIMIENTO_SERVICIOS = {
    # ── FACIAL: CUIDADO Y LIMPIEZA ─────────────────────────────
    "limpieza facial": {
        "categoria": "facial",
        "escena": "client lying on adjustable treatment bed with eyes closed, white headband holding hair back, aesthetician in white coat gently applying cleanser with circular motions using a cotton pad, professional facial steamer positioned nearby emitting soft vapor toward the face",
        "equipo": "facial steamer on wheeled stand, LED magnifying lamp on adjustable arm, small stainless steel tray with extraction loop and lancet, stack of cotton pads, pump bottles of professional micellar cleanser and toner",
        "angulo": "slightly elevated angle showing client face and aesthetician hands working, treatment bed visible, side cart with products in soft focus background",
        "resultado": "clean fresh glowing skin, minimized pores, smooth even complexion, healthy natural radiance without filters",
        "no_incluir": "no blood, no extractions close-up, no redness, no acne, no pimples, no text on image, no watermarks",
        "productos_tipicos": "micellar water, enzyme peel, purifying mask, toner",
        "colores": "white, soft blue, mint green",
    },
    "hidratacion facial": {
        "categoria": "facial",
        "escena": "client on treatment bed with a translucent hydrating gel mask on her face, aesthetician applying extra serum drops on top of the mask with a glass dropper, small glass bowls with cream on the side cart, client expression peaceful and pampered",
        "equipo": "translucent gel sheet mask, glass serum dropper bottles, professional skincare jars with pump dispensers, soft fan brush, warm towel rolled nearby",
        "angulo": "close-up to medium shot of face showing mask and serum application, warm soft tones, intimate and luxurious feel",
        "resultado": "deeply hydrated dewy skin, plump luminous complexion, no dry patches, youthful supple glow",
        "no_incluir": "no dry or flaky skin, no redness, no needles, no machinery, no text",
        "productos_tipicos": "hyaluronic serum, sheet mask, moisturizer, eye cream",
        "colores": "soft mint, white, translucent",
    },
    "peeling quimico": {
        "categoria": "facial",
        "escena": "client lying still on treatment bed, aesthetician wearing nitrile gloves carefully applying a clear gel solution to the face with a wide fan brush, precise and methodical brush strokes across the forehead and cheeks, small timer on the side table",
        "equipo": "wide fan brush, small glass bowl with peeling solution, digital timer, post-treatment calming cream jar, broad-spectrum SPF bottle nearby, sterile gauze pads",
        "angulo": "medium close-up of face during brush application, showing precise technique, gloved hands and brush in frame, clinical yet elegant setting",
        "resultado": "refined smooth skin texture, diminished fine lines, brighter even skin tone, reduced acne scars, renewed fresh complexion",
        "no_incluir": "no peeling or flaking skin, no redness or irritation, no burns, no raw skin, no text",
        "productos_tipicos": "glycolic acid peel, salicylic peel, calming cream, SPF",
        "colores": "clinical white, soft grey, transparent",
    },
    "tratamiento antiedad": {
        "categoria": "facial",
        "escena": "elegant woman on treatment bed receiving anti-aging facial, aesthetician applying rich golden serum with gentle upward lifting strokes along the jawline and cheeks, premium professional skincare products arranged on glass shelf nearby, serene pampering atmosphere",
        "equipo": "gold-tinted anti-aging serum in glass dropper bottle, collagen cream in elegant jar, facial roller (jade or rose quartz), LED light device nearby, premium professional skincare line on display",
        "angulo": "three-quarter portrait showing woman face receiving upward massage strokes, aesthetician hands in frame, warm flattering light, aspirational and luxurious",
        "resultado": "firmer smoother skin, softened wrinkles and fine lines, restored volume and elasticity, luminous youthful complexion",
        "no_incluir": "no exaggerated wrinkles, no unflattering angles, no harsh aging signs, no needles, no text",
        "productos_tipicos": "retinol serum, collagen cream, eye contour, peptide complex",
        "colores": "warm gold, cream, soft white",
    },
    "antimanchas": {
        "categoria": "facial",
        "escena": "client on treatment bed, aesthetician using a fine precision brush to apply depigmenting solution on specific areas of the cheek, magnifying lamp illuminating the treatment zone, protective eye patches on the client, clinical precision and care",
        "equipo": "precision detail brush, depigmenting solution in medical dropper bottle, magnifying lamp, protective eye patches, SPF cream, clinical treatment tray",
        "angulo": "close-up of face showing precise application on specific spots, magnifying lamp glow visible, gloved hands steady, professional clinical atmosphere",
        "resultado": "even uniform skin tone, faded dark spots, bright luminous complexion, clear radiant skin without discoloration",
        "no_incluir": "no visible dark spots or melasma in the final image, no blotchy skin, no harsh contrast, no text",
        "productos_tipicos": "vitamin C serum, niacinamide, kojic acid cream, SPF",
        "colores": "white, soft mint, warm neutral",
    },
    # ── FACIAL: TECNOLOGIA AVANZADA ─────────────────────────────
    "radiofrecuencia": {
        "categoria": "facial_tech",
        "escena": "client lying comfortably on treatment bed, aesthetician holding a sleek radiofrequency handpiece with rounded metal tip against the client jawline, moving in slow circular motions, conductive gel glistening on the treated skin area, modern RF device on a wheeled stand showing digital temperature display in the background",
        "equipo": "professional radiofrequency device (large standing unit with articulated arm and digital screen), round metallic handpiece, tube of conductive contact gel, clean white towels, treatment bed",
        "angulo": "profile or three-quarter view showing handpiece gliding along the jawline, device screen glowing in soft focus behind, client expression relaxed, high-tech yet comfortable atmosphere",
        "resultado": "visibly firmer tighter skin, defined jawline and contours, reduced nasolabial folds, lifted cheekbones, smooth taut skin",
        "no_incluir": "no burns, no redness marks, no pain expression, no cheap handheld devices, no home-use gadgets, no text",
        "productos_tipicos": "conductive gel, firming cream, collagen booster serum",
        "colores": "white, mint, silver, subtle blue LED",
    },
    "microneedling": {
        "categoria": "facial_tech",
        "escena": "aesthetician wearing medical gloves holding a professional dermapen device (metallic pen-shaped tool with cartridge tip) against the client forehead, client lying on treatment bed with a thin layer of hyaluronic serum on the skin, the pen making controlled passes across the skin surface",
        "equipo": "electric dermapen device (pen-shaped, metallic silver body with disposable cartridge tip), hyaluronic acid serum vial, numbing cream tube, sterile cartridge packages, treatment bed",
        "angulo": "close-up showing the dermapen on the forehead or cheek, gloved hands steady and precise, sterile professional setting, clinical detail visible",
        "resultado": "improved skin texture, reduced acne scars, smaller pores, firmer even skin, natural collagen boost visible as plumper healthier skin",
        "no_incluir": "no blood, no visible puncture marks, no redness, no pain expression, no manual dermarollers, no text",
        "productos_tipicos": "hyaluronic serum, growth factor serum, numbing cream",
        "colores": "clinical white, silver, cool grey",
    },
    "led terapia": {
        "categoria": "facial_tech",
        "escena": "client lying on treatment bed wearing opaque protective eye goggles, a large professional LED panel positioned directly above the face emitting therapeutic colored light (red or blue or combination), the face bathed in the glowing colored light, creating a dramatic futuristic look",
        "equipo": "professional LED light therapy panel on adjustable mechanical arm, protective opaque eye goggles, treatment bed, dimmed room lighting to enhance LED effect",
        "angulo": "slightly above or side angle showing the LED panel glowing over the client face, goggles visible, colored light casting on the skin, dramatic cinematic quality",
        "resultado": "calmed clear skin, reduced inflammation and redness, improved acne, stimulated collagen, even radiant tone",
        "no_incluir": "no UV tanning bed look, no sunbed association, no harsh medical equipment, no text",
        "productos_tipicos": "calming serum, post-treatment moisturizer",
        "colores": "red or blue LED glow, dark background, white treatment bed",
    },
    "mesoterapia facial": {
        "categoria": "facial_tech",
        "escena": "medical aesthetic professional in white coat performing mesotherapy on client face, using a mesotherapy pistol (small pneumatic gun device) making precise micro-injections along the cheekbone line, small transparent vials of vitamin cocktails visible on a sterile stainless steel tray",
        "equipo": "mesotherapy pistol or mesogun (small metallic pneumatic device), transparent glass vials with vitamin cocktail solutions, sterile stainless steel instrument tray, alcohol swabs, treatment bed",
        "angulo": "medium shot showing the professional hand holding the mesogun near the face, vitamin vials visible on tray, clinical and precise atmosphere, professional and trustworthy",
        "resultado": "deeply nourished luminous skin, improved hydration from within, healthy radiant glow, firmer plumper texture",
        "no_incluir": "no large needles, no blood, no bruising, no pain expression, no graphic injection close-ups, no text",
        "productos_tipicos": "hyaluronic acid vials, vitamin cocktails, amino acid solutions",
        "colores": "clinical white, silver, clear glass",
    },
    "ultrasonidos facial": {
        "categoria": "facial_tech",
        "escena": "aesthetician holding a flat ultrasound spatula device against the client forehead at a shallow angle, transparent gel on the skin, the metal spatula tip gliding smoothly, modern ultrasonic machine with digital display on the side",
        "equipo": "ultrasonic skin scrubber spatula (flat metal paddle device), clear contact gel, modern digital ultrasound unit, treatment bed",
        "angulo": "close-up of the spatula on the forehead showing the exfoliation technique, gel glistening, clean clinical background",
        "resultado": "deeply cleansed exfoliated skin, unclogged pores, brighter smoother complexion, enhanced product absorption",
        "no_incluir": "no debris or dirt on skin, no blackheads, no harsh imagery, no text",
        "productos_tipicos": "contact gel, calming toner, hydrating serum",
        "colores": "silver, white, translucent",
    },
    # ── MEDICINA ESTETICA ───────────────────────────────────────
    "acido hialuronico": {
        "categoria": "medicina_estetica",
        "escena": "qualified aesthetic doctor in white medical coat holding a fine pre-filled syringe near the client lip border or nasolabial fold area, client reclining on medical treatment chair with white marking pencil dots on the face indicating injection points, sterile gloves, precise and steady hands",
        "equipo": "pre-filled hyaluronic acid syringe (thin 1ml syringe with fine needle), white dermatographic marking pencil, sterile medical gloves, numbing cream tube, antiseptic swabs, medical reclining chair",
        "angulo": "profile or three-quarter view showing precise hand positioning near the lip or cheek, doctor face partially visible showing concentration, medical certificates in soft focus on wall behind",
        "resultado": "natural-looking volume restoration, smooth plump lips, softened nasolabial folds, hydrated youthful appearance, subtle and elegant enhancement that looks natural",
        "no_incluir": "no bruising, no swelling, no exaggerated duck lips, no blood, no overfilled unnatural proportions, no visible needle punctures, no text",
        "productos_tipicos": "HA filler syringes, numbing cream, aftercare products",
        "colores": "white, silver, clinical blue",
    },
    "botox": {
        "categoria": "medicina_estetica",
        "escena": "aesthetic doctor performing botulinum toxin injection on client upper forehead, using a very fine insulin-type syringe, tiny white pencil marks indicating precise injection points on the forehead, client reclining with eyes open looking calm, doctor wearing magnifying loupes for precision",
        "equipo": "very fine insulin-type syringe with tiny needle, white dermatographic pencil marks on forehead, magnifying surgical loupes, sterile medical gloves, antiseptic solution, medical chair",
        "angulo": "front view or slight three-quarter showing forehead treatment zone, doctor hands precise and steady, clinical professional atmosphere, luxury medical office",
        "resultado": "smooth relaxed forehead, softened frown lines, natural expression preserved, refreshed youthful appearance without frozen or stiff look",
        "no_incluir": "no frozen expression, no visible needle marks, no bruising, no unnatural stiffness, no large syringes, no text",
        "productos_tipicos": "botulinum toxin vial, insulin syringes, numbing cream",
        "colores": "white, silver, medical blue",
    },
    "hilos tensores": {
        "categoria": "medicina_estetica",
        "escena": "aesthetic doctor performing thread lift procedure, holding a long thin cannula near the client jawline area, white pencil lines drawn on the face mapping the thread trajectory, client reclining on medical chair, sterile surgical draping around the treatment area",
        "equipo": "long thin insertion cannula, PDO thread packages on sterile tray, white marking pencil, sterile surgical drapes, local anesthetic syringe, medical reclining chair",
        "angulo": "profile view showing the jawline and cheek area, doctor hands positioning the cannula along the pencil guidelines, medical precision and expertise visible",
        "resultado": "lifted tightened jawline, restored cheek volume, reduced jowls, natural V-shape face contour, rejuvenated profile",
        "no_incluir": "no visible threads under skin, no bruising, no swelling, no blood, no graphic surgical imagery, no text",
        "productos_tipicos": "PDO threads, local anesthetic, marking pencil",
        "colores": "white, surgical blue, silver",
    },
    # ── CORPORAL ────────────────────────────────────────────────
    "cavitacion": {
        "categoria": "corporal",
        "escena": "client lying on treatment bed wearing disposable underwear covered with towel, aesthetician applying a round ultrasonic cavitation handpiece on the abdomen area with conductive gel, slow circular motions on the skin, the cavitation machine on a wheeled stand showing frequency settings on its digital screen",
        "equipo": "ultrasonic cavitation machine (wheeled unit with digital display), round smooth cavitation handpiece, tube of conductive gel, measuring tape on side table, treatment bed with disposable cover",
        "angulo": "medium shot from the side showing the handpiece on the abdomen, aesthetician in frame, machine visible in background, professional and tasteful, body covered modestly with towels",
        "resultado": "reduced localized fat, smoother body contour, tighter skin in treated area, visibly slimmer waistline",
        "no_incluir": "no nudity, no cellulite close-ups, no unflattering body angles, no stretch marks, no text",
        "productos_tipicos": "conductive gel, firming body cream, measuring tape",
        "colores": "white, neutral, clinical blue",
    },
    "presoterapia": {
        "categoria": "corporal",
        "escena": "client lying on treatment bed wearing full-leg pressotherapy compression boots that cover from feet to upper thighs, the pneumatic chambers visibly inflated in sequence, client looking relaxed with arms resting at sides, pressotherapy machine unit nearby with pressure controls",
        "equipo": "pressotherapy machine (control unit with hoses), full-leg pneumatic compression boots (large inflatable sectioned cuffs covering feet to thighs), treatment bed, optional abdominal band",
        "angulo": "full body or lower body shot showing both legs in the compression boots fully inflated, client relaxed and comfortable, machine unit visible, clean treatment room",
        "resultado": "reduced leg swelling and heaviness, improved blood circulation, lighter feeling legs, reduced water retention, smoother leg contour",
        "no_incluir": "no varicose veins, no swollen legs shown before, no hospital or medical ward look, no text",
        "productos_tipicos": "drainage cream, compression garments",
        "colores": "white, soft blue, neutral",
    },
    "radiofrecuencia corporal": {
        "categoria": "corporal",
        "escena": "aesthetician applying a large radiofrequency body handpiece on the client thigh area with conductive gel, the handpiece larger than the facial version with a wider treatment head, client lying on treatment bed covered modestly, RF body machine showing power settings",
        "equipo": "body radiofrequency machine (larger unit than facial version), wide-head body handpiece, conductive body gel, measuring tape, treatment bed",
        "angulo": "medium shot showing handpiece on thigh or abdomen area, professional and modest framing, machine visible, clinical body treatment atmosphere",
        "resultado": "firmer tighter body skin, reduced cellulite appearance, smoother contours, improved skin elasticity",
        "no_incluir": "no cellulite close-ups, no unflattering angles, no nudity, no text",
        "productos_tipicos": "conductive gel, firming body cream, collagen body lotion",
        "colores": "white, silver, neutral",
    },
    # ── DEPILACION ──────────────────────────────────────────────
    "depilacion laser": {
        "categoria": "depilacion",
        "escena": "laser technician holding a professional diode laser handpiece with integrated cooling tip against the client lower leg shin area, both technician and client wearing dark protective laser goggles, the large standing laser machine visible behind with its articulated arm, small area of cooling gel on the skin",
        "equipo": "professional diode laser machine (large standing unit with articulated arm and digital touchscreen), laser handpiece with sapphire cooling contact tip, dark protective goggles for client and technician, aloe vera gel bottle",
        "angulo": "medium shot showing the handpiece touching the leg, both people wearing protective goggles, the large laser machine visible in background, safe and professional atmosphere",
        "resultado": "smooth completely hairless skin, no stubble, no ingrown hairs, silky clean skin surface",
        "no_incluir": "no burns, no redness, no visible hair, no pain expression, no cheap IPL home devices, no text",
        "productos_tipicos": "aloe vera gel, cooling spray, post-treatment cream",
        "colores": "white, ice blue, silver",
    },
    # ── SEMIPERMANENTE ──────────────────────────────────────────
    "microblading": {
        "categoria": "semipermanente",
        "escena": "microblading artist wearing gloves and magnifying visor performing eyebrow hair-stroke technique, holding a manual microblading pen with fine blade against the client brow area, client lying with eyes closed on treatment bed, one completed eyebrow visible showing natural-looking hair-stroke pattern, pigment palette with brown shades on side table",
        "equipo": "manual microblading pen with disposable fine blade, pigment palette with earth-tone brown shades in small cups, eyebrow mapping thread and white pencil markings around the brows, numbing cream, magnifying headband visor",
        "angulo": "extreme close-up of eyebrow area showing precise individual hair-stroke lines, artist gloved hand and blade visible, the fine detail of the work clearly visible, intimate precision workspace",
        "resultado": "perfectly shaped natural-looking eyebrows with individual hair strokes visible, defined but not drawn-on appearance, symmetrical natural arch, color matching the client natural hair",
        "no_incluir": "no block-filled brows, no tattoo appearance, no redness or swelling, no unnatural shapes, no heavy makeup look, no text",
        "productos_tipicos": "numbing cream, pigment palette, aftercare balm",
        "colores": "warm brown, nude, soft neutral",
    },
    "lifting pestanas": {
        "categoria": "semipermanente",
        "escena": "lash technician using a thin wooden applicator stick to carefully position the client upper eyelashes over a small silicone curling shield adhered to the eyelid, client lying with eyes closed, one eye completed showing beautifully curled lashes, the other in process with lashes being arranged on the shield",
        "equipo": "silicone lash lifting shields in various curve sizes, lash lifting perm solution, setting solution, thin wooden or metal applicator sticks, under-eye hydrogel pads, lash tint in small mixing dish",
        "angulo": "extreme close-up of the eye area showing lashes arranged on the silicone shield, technician careful hands with applicator stick, intimate precision work, soft focused background",
        "resultado": "beautifully curled uplifted natural lashes, wide open eye effect, defined dramatic lashes without extensions, mascara-free natural beauty look",
        "no_incluir": "no glue blobs, no messy application, no chemical drips, no irritation or redness, no text",
        "productos_tipicos": "lash lift solution, setting solution, lash tint, nourishing oil",
        "colores": "soft pink, white, natural skin tones",
    },
    "micropigmentacion labios": {
        "categoria": "semipermanente",
        "escena": "micropigmentation artist holding a professional PMU machine pen against the client lip border, adding soft color to define and enhance the lip shape, client lying on treatment bed with numbing cream residue around the mouth area, one lip completed showing a soft natural pink tone enhancement",
        "equipo": "PMU (permanent makeup) digital machine pen with fine needle cartridge, pigment color palette with pink and nude shades, numbing cream, white lip liner pencil marks showing planned shape, sterile disposable needles",
        "angulo": "close-up of the lips showing the PMU pen working on the lip contour, steady gloved hands, precise color work, clean professional setting",
        "resultado": "beautifully defined lip contour, soft natural pink tone, enhanced lip shape without looking artificial, fresh and youthful lip color",
        "no_incluir": "no harsh unnatural lip color, no swelling, no blood, no dark or heavy tattoo look, no text",
        "productos_tipicos": "PMU pigments, numbing cream, aftercare lip balm",
        "colores": "soft pink, nude, warm rose",
    },
    # ── BIENESTAR ───────────────────────────────────────────────
    "masaje drenante": {
        "categoria": "bienestar",
        "escena": "massage therapist performing manual lymphatic drainage on client legs, gentle rhythmic upward strokes with both hands on the calf, client lying face up on massage table draped modestly with white cotton sheet, warm spa atmosphere with essential oil diffuser visible, soft towels rolled nearby",
        "equipo": "professional massage table with clean white linen, body massage oil in pump bottle, warm rolled cotton towels, essential oil diffuser with soft steam, optional wooden lymphatic drainage paddle",
        "angulo": "medium shot showing therapist hands performing upward massage strokes on the leg, client covered modestly, warm ambient spa lighting, peaceful and therapeutic atmosphere",
        "resultado": "reduced swelling and puffiness, lighter feeling limbs, improved circulation, detoxified body, deep physical relaxation",
        "no_incluir": "no varicose veins, no cellulite, no bruising, no medical or hospital atmosphere, no nudity, no text",
        "productos_tipicos": "drainage oil, body brush, aromatherapy oils",
        "colores": "warm earth tones, beige, soft green, warm white",
    },
    "masaje relajante": {
        "categoria": "bienestar",
        "escena": "massage therapist applying flowing relaxation massage strokes on client back and shoulders, client lying face down on massage table with face in headrest, warm oil glistening on the skin, ambient candles and stacked hot stones visible on a side table, serene spa environment",
        "equipo": "professional massage table with face rest, warm massage oil, lit candles in glass holders, stacked smooth hot stones on wooden tray, rolled white and natural-colored towels",
        "angulo": "medium shot showing flowing hand movements on the back, warm golden candlelight atmosphere, spa elements visible, deeply relaxing and aspirational",
        "resultado": "complete muscle relaxation, stress relief, deep physical and mental calm, renewed energy, wellness and balance",
        "no_incluir": "no clinical atmosphere, no medical equipment, no harsh lighting, no nudity, no text",
        "productos_tipicos": "massage oil, essential oils, hot stones, warm towels",
        "colores": "warm amber, soft cream, earth tones, candlelight gold",
    },
    # ── FALLBACKS POR CATEGORIA ─────────────────────────────────
    "facial": {
        "categoria": "facial",
        "escena": "client lying on treatment bed receiving a professional facial treatment, aesthetician in white coat applying serum to the face with gentle movements, the client expression serene and relaxed, professional skincare products on a glass shelf nearby",
        "equipo": "professional treatment bed, skincare products on side cart, facial steamer, magnifying lamp, cotton pads, glass serum bottles",
        "angulo": "medium shot showing client face and aesthetician working, warm yet professional clinical setting",
        "resultado": "glowing hydrated skin, relaxed expression, visibly refreshed and rejuvenated complexion",
        "no_incluir": "no harsh chemicals, no needles, no redness, no text",
        "productos_tipicos": "serum, moisturizer, mask, toner, eye cream",
        "colores": "soft mint, white, cool grey",
    },
    "corporal": {
        "categoria": "corporal",
        "escena": "client on treatment bed receiving professional body treatment, aesthetician using a body contouring device or performing manual body care, client covered modestly with towels, modern body treatment equipment visible",
        "equipo": "body treatment machine, conductive gel, measuring tape, treatment bed with disposable cover, body care products",
        "angulo": "medium shot, tasteful and professional framing, machine or hands visible, body covered modestly",
        "resultado": "toned contoured body, smooth skin, improved silhouette, firmer skin texture",
        "no_incluir": "no nudity, no cellulite, no unflattering angles, no text",
        "productos_tipicos": "body cream, conductive gel, firming lotion, body oil",
        "colores": "nude, soft bronze, warm white, neutral",
    },
}

# Alias para que variaciones comunes encuentren el tratamiento correcto
ALIASES_SERVICIOS = {
    "limpieza": "limpieza facial",
    "limpieza profunda": "limpieza facial",
    "limpieza facial profunda": "limpieza facial",
    "deep cleansing": "limpieza facial",
    "higiene facial": "limpieza facial",
    "hidratacion": "hidratacion facial",
    "facial hidratante": "hidratacion facial",
    "hidratante": "hidratacion facial",
    "peeling": "peeling quimico",
    "peeling facial": "peeling quimico",
    "exfoliacion": "peeling quimico",
    "exfoliacion quimica": "peeling quimico",
    "antiedad": "tratamiento antiedad",
    "rejuvenecimiento": "tratamiento antiedad",
    "rejuvenecimiento facial": "tratamiento antiedad",
    "anti-aging": "tratamiento antiedad",
    "antiaging": "tratamiento antiedad",
    "antiarrugas": "tratamiento antiedad",
    "despigmentante": "antimanchas",
    "manchas": "antimanchas",
    "tratamiento antimanchas": "antimanchas",
    "manchas oscuras": "antimanchas",
    "melasma": "antimanchas",
    "radiofrecuencia facial": "radiofrecuencia",
    "rf facial": "radiofrecuencia",
    "indiba": "radiofrecuencia",
    "dermapen": "microneedling",
    "micro needling": "microneedling",
    "micropuncion": "microneedling",
    "needling": "microneedling",
    "led": "led terapia",
    "fototerapia": "led terapia",
    "terapia led": "led terapia",
    "luz led": "led terapia",
    "mesoterapia": "mesoterapia facial",
    "meso facial": "mesoterapia facial",
    "vitaminas facial": "mesoterapia facial",
    "ultrasonidos": "ultrasonidos facial",
    "pala ultrasonidos": "ultrasonidos facial",
    "skin scrubber": "ultrasonidos facial",
    "hialuronico": "acido hialuronico",
    "rellenos": "acido hialuronico",
    "fillers": "acido hialuronico",
    "filler": "acido hialuronico",
    "labios": "acido hialuronico",
    "aumento labios": "acido hialuronico",
    "toxina botulinica": "botox",
    "botoxx": "botox",
    "arrugas frente": "botox",
    "hilos": "hilos tensores",
    "tensor": "hilos tensores",
    "hilo tensor": "hilos tensores",
    "thread lift": "hilos tensores",
    "cavitacion corporal": "cavitacion",
    "ultracavitacion": "cavitacion",
    "lipo sin cirugia": "cavitacion",
    "presoterapia piernas": "presoterapia",
    "botas de presoterapia": "presoterapia",
    "compresion neumatica": "presoterapia",
    "rf corporal": "radiofrecuencia corporal",
    "radiofrecuencia cuerpo": "radiofrecuencia corporal",
    "laser": "depilacion laser",
    "depilacion": "depilacion laser",
    "laser diodo": "depilacion laser",
    "alejandrita": "depilacion laser",
    "ipl": "depilacion laser",
    "cejas": "microblading",
    "microblading cejas": "microblading",
    "hair stroke": "microblading",
    "micropigmentacion cejas": "microblading",
    "lash lift": "lifting pestanas",
    "lifting de pestanas": "lifting pestanas",
    "laminado": "lifting pestanas",
    "permanente pestanas": "lifting pestanas",
    "micropigmentacion": "micropigmentacion labios",
    "labios permanente": "micropigmentacion labios",
    "pmu labios": "micropigmentacion labios",
    "drenaje": "masaje drenante",
    "drenaje linfatico": "masaje drenante",
    "linfatico": "masaje drenante",
    "masaje linfatico": "masaje drenante",
    "masaje": "masaje relajante",
    "relajante": "masaje relajante",
    "masaje corporal": "masaje relajante",
    "masaje descontracturante": "masaje relajante",
    "aromaterapia": "masaje relajante",
}

# Tipos de publicacion con sus estilos fotograficos
ESTILOS_PUBLICACION = {
    "post_feed": {
        "formato": "square",
        "estilo": "polished editorial photography, Instagram-worthy, high contrast, vibrant",
        "composicion": "centered subject, clean background, rule of thirds",
    },
    "story": {
        "formato": "story",
        "estilo": "casual authentic feel, behind-the-scenes vibe, warm tones",
        "composicion": "vertical framing, close-up details, space for text overlay at top and bottom",
    },
    "reel_portada": {
        "formato": "vertical",
        "estilo": "eye-catching thumbnail, bold and dynamic, high energy",
        "composicion": "vertical portrait, strong focal point, dramatic lighting",
    },
    "carrusel": {
        "formato": "square",
        "estilo": "consistent clean aesthetic, educational layout feel, minimal and modern",
        "composicion": "clean background with space for text, consistent color palette across slides",
    },
    "antes_despues": {
        "formato": "square",
        "estilo": "clinical comparison, consistent lighting both sides, professional medical aesthetic",
        "composicion": "split screen or side by side, same angle and lighting, clear difference visible",
    },
    "producto": {
        "formato": "square",
        "estilo": "luxury product photography, commercial quality, beauty magazine aesthetic",
        "composicion": "product centered, complementary props, soft shadows, lifestyle context",
    },
}

# Paletas de color segun tono de marca
PALETAS_TONO = {
    "cercano": {
        "principal": "soft mint green and seafoam",
        "secundario": "clean white and light grey accents",
        "ambiente": "fresh, elegant, approachable",
    },
    "profesional": {
        "principal": "deep black and mint green",
        "secundario": "silver and cool grey accents",
        "ambiente": "clinical, trustworthy, premium",
    },
    "divertido": {
        "principal": "bright teal and mint",
        "secundario": "crisp white and charcoal accents",
        "ambiente": "energetic, fresh, modern",
    },
}


def encontrar_servicio(nombre_servicio):
    """
    Busca en la base de conocimiento el servicio mas parecido.
    Usa aliases, busqueda parcial y fallback por categoria.
    """
    nombre = nombre_servicio.lower().strip()

    # 1. Busqueda exacta en el diccionario principal
    if nombre in CONOCIMIENTO_SERVICIOS:
        return CONOCIMIENTO_SERVICIOS[nombre]

    # 2. Busqueda en aliases
    if nombre in ALIASES_SERVICIOS:
        clave = ALIASES_SERVICIOS[nombre]
        return CONOCIMIENTO_SERVICIOS[clave]

    # 3. Busqueda parcial en aliases (el input contiene un alias)
    for alias, clave in ALIASES_SERVICIOS.items():
        if alias in nombre or nombre in alias:
            return CONOCIMIENTO_SERVICIOS[clave]

    # 4. Busqueda parcial en claves principales
    for clave, datos in CONOCIMIENTO_SERVICIOS.items():
        if clave in nombre or nombre in clave:
            return datos

    # 5. Busqueda por palabras clave (palabras de >3 letras)
    palabras = nombre.split()
    mejor_match = None
    mejor_score = 0
    for clave, datos in CONOCIMIENTO_SERVICIOS.items():
        score = 0
        for palabra in palabras:
            if len(palabra) > 3 and palabra in clave:
                score += 1
        if score > mejor_score:
            mejor_score = score
            mejor_match = datos
    if mejor_match and mejor_score > 0:
        return mejor_match

    # 6. Fallback inteligente por tipo de palabra clave
    palabras_corporales = ["corporal", "cuerpo", "piernas", "abdomen",
                           "gluteos", "brazos", "muslos", "celulitis",
                           "grasa", "reducir", "adelgazar", "moldear"]
    palabras_bienestar = ["masaje", "relajar", "relax", "spa",
                          "bienestar", "wellness", "descontracturante"]
    for p in palabras:
        if p in palabras_corporales:
            return CONOCIMIENTO_SERVICIOS["corporal"]
        if p in palabras_bienestar:
            return CONOCIMIENTO_SERVICIOS["masaje relajante"]

    # 7. Fallback final: facial generico
    return CONOCIMIENTO_SERVICIOS["facial"]


# ============================================================
# CATALOGO VISUAL DE PRODUCTOS (marcas conocidas)
# Descripciones fisicas detalladas para prompts realistas
# ============================================================

CATALOGO_PRODUCTOS = {
    # --- RINGANA FRESH (cosmetica) ---
    "ringana hydro serum": {
        "marca": "Ringana",
        "envase": "tall cylindrical clear glass bottle, approximately 15cm height",
        "material": "transparent glass, pharmaceutical luxe finish",
        "cierre": "silver metallic airless pump dispenser mechanism",
        "color_cuerpo": "transparent, showing pale golden liquid serum inside",
        "etiqueta": "minimalist white paper label, small grey sans-serif lowercase text, tiny green leaf icon",
        "producto_visible": "pale golden translucent liquid serum",
        "estetica": "eco-minimalist luxury, similar to Aesop, Scandinavian bathroom aesthetic",
        "iluminacion_ideal": "subtle backlight making glass glow and serum shimmer",
        "props_ideales": "fresh eucalyptus sprig, light natural stone surface",
    },
    "ringana cleanser": {
        "marca": "Ringana",
        "envase": "cylindrical clear glass bottle, approximately 12cm height, 150ml",
        "material": "transparent glass showing product inside",
        "cierre": "silver metallic airless pump dispenser",
        "color_cuerpo": "transparent, showing slightly green-tinted cleansing milk inside (chlorophyll tint)",
        "etiqueta": "minimalist white label, 'FRESH' in small caps, product name in light grey sans-serif",
        "producto_visible": "slightly green-tinted milky liquid",
        "estetica": "clean pharmaceutical aesthetic, no decorative elements",
        "iluminacion_ideal": "soft diffused light with backlight accent on glass",
        "props_ideales": "white marble surface, single green leaf",
    },
    "ringana cream": {
        "marca": "Ringana",
        "envase": "small cylindrical glass jar, approximately 6cm height, 50ml, flat screw-top lid",
        "material": "clear or slightly frosted glass showing cream inside",
        "cierre": "flat screw-on glass or metal lid",
        "color_cuerpo": "transparent glass with cream-colored product visible",
        "etiqueta": "minimal white label, 'FRESH' and 'cream' in grey sans-serif lowercase",
        "producto_visible": "rich white cream visible through glass",
        "estetica": "rounded proportions, clean and simple, premium eco",
        "iluminacion_ideal": "warm soft light, gentle shadows",
        "props_ideales": "cotton pad nearby, clean white towel, botanical element",
    },
    "ringana eye cream": {
        "marca": "Ringana",
        "envase": "very small cylindrical glass jar, approximately 4cm height, 15ml",
        "material": "clear glass, delicate proportions",
        "cierre": "small flat screw-on lid",
        "color_cuerpo": "transparent glass with light cream visible inside",
        "etiqueta": "tiny minimalist white label, grey sans-serif text, very reduced branding",
        "producto_visible": "light delicate cream",
        "estetica": "precious and compact, eco luxury",
        "iluminacion_ideal": "intimate soft lighting, close-up macro style",
        "props_ideales": "smooth river stone, single flower petal",
    },
    "ringana tonic": {
        "marca": "Ringana",
        "envase": "tall cylindrical clear glass bottle, 15cm height, slender proportions",
        "material": "transparent glass",
        "cierre": "silver metallic spray nozzle or pump dispenser",
        "color_cuerpo": "transparent, showing clear liquid with very slight color tint",
        "etiqueta": "white minimalist label, 'FRESH' and 'tonic' in grey lowercase sans-serif",
        "producto_visible": "clear transparent liquid, possibly light hint of color",
        "estetica": "tall and elegant, pharmaceutical luxury",
        "iluminacion_ideal": "backlight for transparency effect, light refracting through liquid",
        "props_ideales": "light stone surface, minimalist setting",
    },
    # --- RINGANA CAPS (suplementos) ---
    "ringana caps beauty": {
        "marca": "Ringana",
        "envase": "cylindrical cardboard tube, approximately 12cm height, matte finish",
        "material": "sustainable cardboard, matte texture, eco packaging",
        "cierre": "flat screw-off cardboard lid, same color as body",
        "color_cuerpo": "warm rose-pink solid color, matte finish",
        "etiqueta": "product name 'beauty' in white lowercase sans-serif, minimal RINGANA branding",
        "producto_visible": "not visible (opaque cardboard)",
        "estetica": "bold single color, sustainable material, modern eco supplement brand",
        "iluminacion_ideal": "soft even lighting, matte surface without harsh reflections",
        "props_ideales": "natural wood surface, scattered dried flower petals, linen cloth",
    },
    "ringana caps protec": {
        "marca": "Ringana",
        "envase": "cylindrical cardboard tube, approximately 12cm height, matte finish",
        "material": "sustainable cardboard, eco packaging",
        "cierre": "flat screw-off lid, same color as body",
        "color_cuerpo": "deep forest green solid color, matte finish",
        "etiqueta": "product name 'protec' in white lowercase sans-serif",
        "producto_visible": "not visible (opaque cardboard)",
        "estetica": "bold single color, natural health aesthetic",
        "iluminacion_ideal": "natural soft light",
        "props_ideales": "wooden surface, green leaves, natural setting",
    },
    "ringana caps immu": {
        "marca": "Ringana",
        "envase": "cylindrical cardboard tube, approximately 12cm height, matte finish",
        "material": "sustainable cardboard",
        "cierre": "flat screw-off lid, same color as body",
        "color_cuerpo": "warm amber/orange solid color, matte finish",
        "etiqueta": "product name 'immu' in white lowercase sans-serif",
        "producto_visible": "not visible (opaque cardboard)",
        "estetica": "bold warm color, vitality and health",
        "iluminacion_ideal": "warm natural light",
        "props_ideales": "citrus slices nearby, wooden surface",
    },
}


def buscar_producto_en_catalogo(nombre_producto):
    """
    Busca un producto en el catalogo de marcas conocidas.
    Devuelve los datos visuales si lo encuentra, None si no.
    """
    nombre = nombre_producto.lower().strip()

    # Busqueda exacta
    if nombre in CATALOGO_PRODUCTOS:
        return CATALOGO_PRODUCTOS[nombre]

    # Busqueda parcial: coincidencia de palabras clave
    palabras = nombre.split()
    mejor_match = None
    mejor_score = 0

    for clave, datos in CATALOGO_PRODUCTOS.items():
        score = 0
        for palabra in palabras:
            if len(palabra) > 2 and palabra in clave:
                score += 1
        # Bonus si la marca coincide
        if datos.get("marca", "").lower() in nombre:
            score += 2
        if score > mejor_score:
            mejor_score = score
            mejor_match = datos

    if mejor_score >= 2:
        return mejor_match

    return None


def generar_prompt_producto_detallado(servicio, tipo_publicacion, perfil,
                                      descripcion_producto=None,
                                      datos_busqueda_web=None):
    """
    GENERADOR DE PROMPT DE PRODUCTO DE 5 BLOQUES
    Construye un prompt ultradetallado para fotografia de producto realista.

    Fuentes de informacion (en orden de prioridad):
    1. Catalogo interno de marcas conocidas
    2. Descripcion libre de la clienta
    3. Datos de busqueda web
    4. Conocimiento generico del servicio
    """
    estilo_pub = ESTILOS_PUBLICACION.get(tipo_publicacion, ESTILOS_PUBLICACION["producto"])
    tono = perfil.get("tono", "cercano")
    paleta = PALETAS_TONO.get(tono, PALETAS_TONO["cercano"])

    # Intentar encontrar producto en catalogo
    catalogo = buscar_producto_en_catalogo(servicio)

    if catalogo:
        # RUTA 1: Producto conocido en el catalogo
        prompt = _prompt_desde_catalogo(catalogo, tipo_publicacion, paleta)
    elif descripcion_producto:
        # RUTA 2: Descripcion proporcionada por la clienta
        prompt = _prompt_desde_descripcion(descripcion_producto, servicio,
                                           tipo_publicacion, paleta)
    elif datos_busqueda_web:
        # RUTA 3: Datos extraidos de busqueda web
        prompt = _prompt_desde_busqueda_web(datos_busqueda_web, servicio,
                                            tipo_publicacion, paleta)
    else:
        # RUTA 4: Solo el nombre del producto, prompt generico mejorado
        conocimiento = encontrar_servicio(servicio)
        prompt = _prompt_producto_generico(conocimiento, servicio,
                                          tipo_publicacion, paleta)

    return {
        "prompt": prompt,
        "tamano": estilo_pub["formato"],
        "servicio": servicio,
        "tipo_publicacion": tipo_publicacion,
        "modo": "producto",
        "fuente": "catalogo" if catalogo else "descripcion" if descripcion_producto else "web" if datos_busqueda_web else "generico",
    }


def _prompt_desde_catalogo(catalogo, tipo_publicacion, paleta):
    """Construye prompt de 5 bloques a partir de datos del catalogo."""
    bloque1 = "Commercial beauty product photography of a single product, centered composition"

    bloque2 = (
        f"{catalogo['envase']}. "
        f"{catalogo['material']}. "
        f"{catalogo['cierre']} on top. "
        f"Body: {catalogo['color_cuerpo']}. "
        f"{catalogo['etiqueta']}."
    )
    if catalogo.get("producto_visible") and catalogo["producto_visible"] != "not visible (opaque cardboard)":
        bloque2 += f" Product inside: {catalogo['producto_visible']}."

    bloque3 = (
        f"Hero angle from slightly above. "
        f"{catalogo.get('iluminacion_ideal', 'Soft diffused studio lighting')}. "
        f"Shallow depth of field, sharp focus on product."
    )

    bloque4 = f"On {catalogo.get('props_ideales', 'clean neutral surface')}, clean background."

    bloque5 = (
        f"4K commercial quality, photorealistic, "
        f"{catalogo.get('estetica', 'premium beauty brand aesthetic')}."
    )

    return f"{bloque1}. {bloque2} {bloque3} {bloque4} {bloque5}"


def _prompt_desde_descripcion(descripcion, servicio, tipo_publicacion, paleta):
    """Construye prompt a partir de la descripcion libre de la clienta."""
    servicio_en = _traducir_servicio(servicio)

    bloque1 = "Commercial beauty product photography of a single product, centered composition"

    bloque2 = f"{descripcion}."

    bloque3 = (
        f"Hero angle from slightly above. "
        f"Soft diffused studio lighting with subtle highlights. "
        f"Shallow depth of field, sharp focus on product."
    )

    bloque4 = (
        f"On elegant neutral surface, clean background, "
        f"{paleta['ambiente']} mood, {paleta['principal']} color accents."
    )

    bloque5 = "4K commercial quality, photorealistic, beauty magazine editorial style."

    return f"{bloque1}. {bloque2} {bloque3} {bloque4} {bloque5}"


def _prompt_desde_busqueda_web(datos_web, servicio, tipo_publicacion, paleta):
    """Construye prompt a partir de datos extraidos de busqueda web."""
    servicio_en = _traducir_servicio(servicio)

    bloque1 = "Commercial beauty product photography of a single product, centered composition"

    # Extraer lo que tengamos de la busqueda web
    envase = datos_web.get("envase", "elegant beauty product container")
    material = datos_web.get("material", "premium finish")
    color = datos_web.get("color_cuerpo", "neutral tones")
    cierre = datos_web.get("cierre", "")
    etiqueta = datos_web.get("etiqueta", "minimalist label with brand text")

    bloque2 = f"{envase}, {material}, {color}"
    if cierre:
        bloque2 += f", {cierre}"
    bloque2 += f". {etiqueta}."

    bloque3 = (
        f"Hero angle from slightly above. "
        f"Soft diffused studio lighting. "
        f"Shallow depth of field."
    )

    bloque4 = (
        f"On clean surface, neutral background, "
        f"{paleta['ambiente']} mood."
    )

    bloque5 = "4K commercial quality, photorealistic, beauty magazine editorial style."

    return f"{bloque1}. {bloque2} {bloque3} {bloque4} {bloque5}"


def _prompt_producto_generico(conocimiento, servicio, tipo_publicacion, paleta):
    """Prompt mejorado para productos sin datos especificos."""
    servicio_en = _traducir_servicio(servicio)

    bloque1 = "Commercial beauty product photography of a single product"

    bloque2 = (
        f"Elegant beauty product for {servicio_en}: {conocimiento['productos_tipicos']}. "
        f"In premium container with {conocimiento['colores']} color scheme, "
        f"minimalist label design, professional packaging."
    )

    bloque3 = (
        f"Hero angle from slightly above. "
        f"Soft natural light, shallow depth of field."
    )

    bloque4 = (
        f"On elegant marble surface, {paleta['ambiente']} mood, "
        f"complementary botanical elements nearby."
    )

    bloque5 = "4K commercial quality, photorealistic, luxury beauty brand aesthetic."

    return f"{bloque1}. {bloque2} {bloque3} {bloque4} {bloque5}"


TRADUCCION_SERVICIOS = {
    # Facial: cuidado
    "limpieza facial": "professional deep facial cleansing",
    "limpieza facial profunda": "professional deep facial cleansing",
    "hidratacion facial": "deep hydration facial treatment",
    "peeling quimico": "chemical peel facial treatment",
    "tratamiento antiedad": "professional anti-aging facial treatment",
    "rejuvenecimiento facial": "facial rejuvenation treatment",
    "antimanchas": "dark spot depigmentation treatment",
    "tratamiento antimanchas": "dark spot depigmentation treatment",
    "tratamiento despigmentante": "skin brightening depigmentation treatment",
    # Facial: tecnologia
    "radiofrecuencia": "radiofrequency skin tightening treatment",
    "radiofrecuencia facial": "facial radiofrequency lifting treatment",
    "microneedling": "professional microneedling dermapen treatment",
    "dermapen": "professional dermapen microneedling treatment",
    "led terapia": "LED light therapy facial treatment",
    "fototerapia": "phototherapy LED facial treatment",
    "mesoterapia facial": "facial mesotherapy vitamin injection treatment",
    "mesoterapia": "mesotherapy vitamin cocktail treatment",
    "ultrasonidos facial": "ultrasonic facial spatula exfoliation treatment",
    # Medicina estetica
    "acido hialuronico": "hyaluronic acid filler injection treatment",
    "botox": "botulinum toxin wrinkle relaxation treatment",
    "toxina botulinica": "botulinum toxin injection treatment",
    "hilos tensores": "PDO thread lift facial contouring treatment",
    # Corporal
    "cavitacion": "ultrasonic body cavitation fat reduction treatment",
    "presoterapia": "pressotherapy lymphatic compression treatment",
    "radiofrecuencia corporal": "body radiofrequency skin tightening treatment",
    # Depilacion
    "depilacion laser": "professional diode laser hair removal",
    "depilacion": "professional laser hair removal",
    # Semipermanente
    "microblading": "eyebrow microblading hair-stroke technique",
    "microblading de cejas": "eyebrow microblading hair-stroke technique",
    "lifting pestanas": "eyelash lift and tint treatment",
    "micropigmentacion labios": "lip micropigmentation permanent makeup",
    # Bienestar
    "masaje drenante": "manual lymphatic drainage massage",
    "masaje drenante linfatico": "lymphatic drainage massage",
    "drenaje linfatico": "lymphatic drainage massage",
    "masaje relajante": "relaxation full-body massage",
    "masaje descontracturante": "deep tissue therapeutic massage",
    # Productos
    "serum vitamina c": "vitamin C brightening serum",
    "crema hidratante facial": "professional facial moisturizing cream",
    "contorno de ojos antiojeras": "under-eye dark circle correcting cream",
}


def _traducir_servicio(nombre):
    """Traduce nombre de servicio al ingles para mejores prompts."""
    nombre_lower = nombre.lower().strip()
    if nombre_lower in TRADUCCION_SERVICIOS:
        return TRADUCCION_SERVICIOS[nombre_lower]
    # Busqueda parcial
    for es, en in TRADUCCION_SERVICIOS.items():
        if es in nombre_lower or nombre_lower in es:
            return en
    # Si no encuentra traduccion, devolver nombre limpio
    return f"beauty {nombre}"


def generar_prompt_automatico(servicio, tipo_publicacion, perfil, modo="servicio"):
    """
    GENERADOR INTELIGENTE DE PROMPTS v3.0
    Genera prompts REALISTAS basados en como se ven los tratamientos
    EN LA REALIDAD. No inventa equipo ni escenas que no existen.
    Cada tipo de publicacion produce una composicion distinta.
    """
    conocimiento = encontrar_servicio(servicio)
    estilo_pub = ESTILOS_PUBLICACION.get(tipo_publicacion, ESTILOS_PUBLICACION["post_feed"])
    tono = perfil.get("tono", "cercano")
    paleta = PALETAS_TONO.get(tono, PALETAS_TONO["cercano"])
    servicio_en = _traducir_servicio(servicio)
    categoria = conocimiento.get("categoria", "facial")

    # Campos del nuevo formato de conocimiento
    escena = conocimiento.get("escena", "")
    equipo = conocimiento.get("equipo", "")
    angulo = conocimiento.get("angulo", "")
    resultado = conocimiento.get("resultado", "")
    no_incluir = conocimiento.get("no_incluir", "no text, no watermarks")

    # --- MODO PRODUCTO: usa el generador detallado de 5 bloques ---
    if modo == "producto":
        datos_producto = generar_prompt_producto_detallado(
            servicio, tipo_publicacion, perfil,
            descripcion_producto=perfil.get("descripcion_producto"),
        )
        prompt = datos_producto["prompt"]

    # --- ANTES/DESPUES: comparativa clinica ---
    elif tipo_publicacion == "antes_despues":
        prompt = (
            f"Professional clinical before-and-after comparison photograph for {servicio_en}. "
            f"Clean side-by-side split composition with identical lighting, angle and background on both halves. "
            f"Left half labeled BEFORE: realistic skin with minor imperfections, slightly muted warm tones, natural unedited look. "
            f"Right half labeled AFTER: the same face or area showing {resultado}, brighter and clearer skin, natural improvement not exaggerated. "
            f"Both sides show the same person, same position, same neutral background. "
            f"Clinical aesthetic, {paleta['principal']} subtle color accents, consistent professional lighting, 4K quality. "
            f"{no_incluir}, no extreme transformations, no unrealistic changes."
        )

    # --- STORY: escena vertical del tratamiento ---
    elif tipo_publicacion == "story":
        if categoria in ("bienestar",):
            # Bienestar: ambience shot with space for text
            prompt = (
                f"Vertical Instagram story photograph of a {servicio_en} spa moment. "
                f"Atmospheric close-up detail shot: {equipo}. "
                f"Warm ambient lighting, soft bokeh in background, shallow depth of field. "
                f"Vertical 9:16 composition with generous negative space in upper and lower thirds for text overlay. "
                f"Intimate and aspirational, authentic spa atmosphere, {paleta['principal']} accents. "
                f"Photorealistic, 4K vertical. {no_incluir}."
            )
        else:
            # Clinico/tech: behind-the-scenes treatment moment
            prompt = (
                f"Vertical Instagram story photograph captured during a real {servicio_en} session. "
                f"Behind-the-scenes authentic moment: {escena}. "
                f"Vertical 9:16 composition, close-up detail with shallow depth of field, "
                f"generous negative space in upper and lower thirds for text overlay. "
                f"Authentic clinic atmosphere, {paleta['principal']} accents, warm natural tones. "
                f"Photorealistic candid feel, 4K vertical. {no_incluir}."
            )

    # --- CARRUSEL: fondo educativo con imagen tratamiento ---
    elif tipo_publicacion == "carrusel":
        prompt = (
            f"Clean educational beauty carousel slide about {servicio_en}. "
            f"Soft blurred background photograph showing {equipo} in a {categoria} treatment setting, "
            f"extremely shallow depth of field creating a dreamy soft-focus backdrop. "
            f"Large clean area for text overlay, {paleta['principal']} tones, {paleta['secundario']}. "
            f"Consistent minimal aesthetic, modern beauty brand visual style, 4K square format. "
            f"{no_incluir}."
        )

    # --- REEL PORTADA: vertical impactante y dinamica ---
    elif tipo_publicacion == "reel_portada":
        prompt = (
            f"Eye-catching vertical thumbnail for beauty reel about {servicio_en}. "
            f"Dramatic close-up detail shot: {_detalle_reel(conocimiento)}. "
            f"Bold cinematic lighting with contrast, strong single focal point, "
            f"shallow depth of field with creamy bokeh background. "
            f"{paleta['principal']} tones with bright highlights, dynamic energy, 4K vertical. "
            f"{no_incluir}."
        )

    # --- PRODUCTO (tipo publicacion): productos del tratamiento ---
    elif tipo_publicacion == "producto":
        productos = conocimiento.get("productos_tipicos", "professional skincare products")
        colores = conocimiento.get("colores", "white, neutral")
        prompt = (
            f"High-end flat lay product photography for {servicio_en} treatment products. "
            f"{productos} arranged in editorial flat lay composition on elegant surface. "
            f"Complementary natural props (fresh eucalyptus sprig, cotton rounds, natural stone). "
            f"Soft natural window light from the side, {colores} color palette, subtle shadows. "
            f"Beauty magazine editorial quality, shallow depth of field on hero product, 4K. "
            f"{no_incluir}."
        )

    # --- POST FEED: foto profesional del tratamiento real ---
    else:
        prompt = _prompt_post_feed(conocimiento, servicio_en, paleta, categoria, no_incluir)

    return {
        "prompt": prompt,
        "tamano": estilo_pub["formato"],
        "servicio": servicio,
        "tipo_publicacion": tipo_publicacion,
        "modo": modo,
    }


def _prompt_post_feed(conocimiento, servicio_en, paleta, categoria, no_incluir):
    """
    Genera el prompt principal para post de feed.
    Diferencia por categoria para que cada tipo de tratamiento
    tenga una composicion y atmosfera apropiada.
    """
    escena = conocimiento.get("escena", "")
    equipo = conocimiento.get("equipo", "")
    angulo = conocimiento.get("angulo", "")

    if categoria in ("medicina_estetica",):
        # Medicina estetica: precision clinica, confianza, profesionalidad
        prompt = (
            f"Professional medical aesthetic clinic photography: {servicio_en}. "
            f"{escena}. "
            f"Visible equipment: {equipo}. "
            f"Luxury medical setting, clinical precision, trustworthy professional atmosphere. "
            f"{angulo}. "
            f"Photorealistic, sharp focus, 4K commercial quality, {paleta['principal']} subtle accents. "
            f"{no_incluir}."
        )
    elif categoria in ("facial_tech",):
        # Tecnologia facial: high-tech, moderno, innovacion
        prompt = (
            f"Modern aesthetic technology photography: {servicio_en}. "
            f"{escena}. "
            f"Equipment detail: {equipo}. "
            f"High-tech clinical environment with contemporary design, advanced skincare technology feel. "
            f"{angulo}. "
            f"Photorealistic, sharp detail, 4K quality, {paleta['principal']} accents with cool tech tones. "
            f"{no_incluir}."
        )
    elif categoria in ("bienestar",):
        # Bienestar/spa: calido, relajante, aspiracional
        prompt = (
            f"Luxurious spa and wellness photography: {servicio_en}. "
            f"{escena}. "
            f"Spa elements: {equipo}. "
            f"Warm inviting atmosphere, soft ambient lighting, relaxation and self-care mood. "
            f"{angulo}. "
            f"Photorealistic, warm tones, 4K quality, {paleta['principal']} natural accents. "
            f"{no_incluir}."
        )
    elif categoria in ("corporal",):
        # Corporal: profesional, discreto, resultados
        prompt = (
            f"Professional body contouring photography: {servicio_en}. "
            f"{escena}. "
            f"Equipment: {equipo}. "
            f"Clean modern treatment room, professional and modest presentation. "
            f"{angulo}. "
            f"Photorealistic, 4K quality, {paleta['principal']} accents, tasteful clinical aesthetic. "
            f"{no_incluir}."
        )
    elif categoria in ("depilacion",):
        # Depilacion: seguridad, tecnologia, resultado limpio
        prompt = (
            f"Professional laser clinic photography: {servicio_en}. "
            f"{escena}. "
            f"Equipment: {equipo}. "
            f"Safe professional environment, modern laser technology, clean clinical setting. "
            f"{angulo}. "
            f"Photorealistic, 4K quality, {paleta['principal']} accents, cool clinical tones. "
            f"{no_incluir}."
        )
    elif categoria in ("semipermanente",):
        # Semipermanente: precision artistica, detalle, resultado natural
        prompt = (
            f"Precision beauty artistry photography: {servicio_en}. "
            f"{escena}. "
            f"Artist tools: {equipo}. "
            f"Intimate precise workspace, artistic detail and skill visible. "
            f"{angulo}. "
            f"Photorealistic, macro detail, 4K quality, {paleta['principal']} accents, natural beauty tones. "
            f"{no_incluir}."
        )
    else:
        # Facial generico: cuidado, profesionalidad, relajacion
        prompt = (
            f"Professional beauty clinic photography: {servicio_en}. "
            f"{escena}. "
            f"Treatment setup: {equipo}. "
            f"Clean elegant treatment room, professional skincare atmosphere. "
            f"{angulo}. "
            f"Photorealistic, 4K commercial quality, {paleta['principal']} accents. "
            f"{no_incluir}."
        )

    return prompt


def _detalle_reel(conocimiento):
    """Extrae un detalle visual impactante para portada de reel."""
    equipo = conocimiento.get("equipo", "")
    # Tomar el primer elemento del equipo como focal point
    if equipo:
        elementos = [e.strip() for e in equipo.split(",")]
        focal = elementos[0] if elementos else "beauty treatment detail"
    else:
        focal = "beauty treatment close-up detail"
    return f"extreme close-up of {focal}, dramatic angle, sharp detail"


# ============================================================
# PRESETS MANUALES (se mantienen para uso avanzado)
# ============================================================

PROMPTS_ESTETICA = {
    "producto_fondo_blanco": (
        "Professional product photography of {producto}, centered on a clean white background, "
        "soft studio lighting, high-end cosmetic advertisement style, sharp focus, "
        "subtle shadow underneath, 4K quality, commercial photography"
    ),
    "producto_lifestyle": (
        "Elegant lifestyle product photography of {producto}, placed on a marble surface "
        "with green eucalyptus leaves and soft natural light from a window, "
        "beauty magazine aesthetic, warm tones, shallow depth of field, luxurious feel"
    ),
    "producto_natural": (
        "Natural beauty product photography of {producto}, surrounded by fresh flowers "
        "and natural ingredients, soft morning light, organic aesthetic, "
        "clean and minimal composition, pastel tones, spa atmosphere"
    ),
    "tratamiento_ambiente": (
        "Professional aesthetic clinic interior, treatment room with {tratamiento} equipment, "
        "clean modern design, soft ambient lighting, calming atmosphere, "
        "white and light wood tones, medical spa aesthetic, welcoming and luxurious"
    ),
    "antes_despues_plantilla": (
        "Clean split-screen template design for before and after comparison, "
        "minimal design, left side slightly darker, right side brighter and glowing, "
        "beauty clinic aesthetic, text area at top saying 'ANTES | DESPUES', "
        "professional medical aesthetic style"
    ),
    "fondo_stories": (
        "Elegant gradient background for Instagram stories, {color_scheme} color palette, "
        "subtle texture, modern and clean, beauty brand aesthetic, "
        "space for text overlay, soft and luxurious feel"
    ),
    "carrusel_fondo": (
        "Clean minimal background for Instagram carousel slide about {tema}, "
        "soft {color_scheme} gradient, subtle geometric patterns, "
        "professional beauty brand design, space for text, modern aesthetic"
    ),
}


# ============================================================
# FUNCIONES DE GENERACION DE IMAGENES
# ============================================================

def generar_imagen(prompt_personalizado=None, tipo_preset=None,
                   variables=None, tamano="square", api_key=None):
    """Genera una imagen usando fal.ai con modelos Flux."""
    key = api_key or os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        print(f"[WARN] Modo demo en generar_imagen: FAL_KEY={'SI' if key else 'NO'}, FAL_DISPONIBLE={FAL_DISPONIBLE}")
        return _demo_imagen(tipo_preset or "producto_lifestyle", variables or {},
                            prompt_override=prompt_personalizado)
    if prompt_personalizado:
        prompt = prompt_personalizado
    elif tipo_preset and tipo_preset in PROMPTS_ESTETICA:
        prompt = PROMPTS_ESTETICA[tipo_preset].format(**(variables or {}))
    else:
        prompt = "Professional beauty product photography, clean white background, studio lighting"
    tamanos = {
        "square": "square",
        "vertical": "portrait_4_3",
        "horizontal": "landscape_4_3",
        "story": "portrait_16_9",
        "reel": "portrait_16_9",
    }
    image_size = tamanos.get(tamano, "square")
    print(f"[Esteticai] Generando imagen con Flux...")
    print(f"[Esteticai] Prompt: {prompt[:100]}...")
    os.environ["FAL_KEY"] = key
    try:
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": 1,
                "safety_tolerance": "5",
            },
            with_logs=False,
        )
        image_url = result["images"][0]["url"]
        print(f"[Esteticai] Imagen generada: {image_url}")
        return {
            "url": image_url,
            "prompt": prompt,
            "tamano": tamano,
            "modelo": "flux-pro-1.1",
        }
    except Exception as e:
        print(f"[ERROR] Fallo al generar imagen: {e}")
        return {"error": str(e)}


def generar_imagen_automatica(servicio, tipo_publicacion, perfil, modo="servicio"):
    """
    FUNCION PRINCIPAL - Generacion automatica sin prompts manuales.
    La clienta elige servicio + tipo de post y listo.
    """
    datos = generar_prompt_automatico(servicio, tipo_publicacion, perfil, modo)
    print(f"\n[Esteticai] Generacion automatica")
    print(f"[Esteticai] Servicio: {servicio}")
    print(f"[Esteticai] Tipo: {tipo_publicacion} | Modo: {modo}")

    key = os.environ.get("FAL_KEY")
    if not key or not FAL_DISPONIBLE:
        razon = []
        if not key:
            razon.append("FAL_KEY no configurada")
        if not FAL_DISPONIBLE:
            razon.append("fal-client no se pudo importar")
        print(f"[WARN] Modo demo en generar_imagen_automatica: {', '.join(razon)}")
        # Generar placeholder visual en vez de error
        placeholder_url = _generar_placeholder(servicio, datos["tamano"])
        return {
            "url": placeholder_url or "",
            "prompt": datos["prompt"],
            "tamano": datos["tamano"],
            "modelo": "demo",
            "es_demo": True,
            "servicio": servicio,
            "tipo_publicacion": tipo_publicacion,
            "modo": modo,
            "nota": f"Vista previa ({', '.join(razon)}). Conecta fal.ai para imagenes reales.",
        }

    resultado = generar_imagen(
        prompt_personalizado=datos["prompt"],
        tamano=datos["tamano"],
    )
    resultado["servicio"] = servicio
    resultado["tipo_publicacion"] = tipo_publicacion
    resultado["modo"] = modo
    return resultado


def generar_pack_automatico(perfil, servicio, tipo_publicacion="post_feed"):
    """
    Genera un pack completo de imagenes para una publicacion.
    Todo automatico basado en el servicio y tipo de post.
    """
    packs_config = {
        "post_feed": [
            {"tipo_pub": "post_feed", "modo": "servicio", "desc": "Foto principal del post"},
        ],
        "carrusel": [
            {"tipo_pub": "carrusel", "modo": "servicio", "desc": "Portada del carrusel"},
            {"tipo_pub": "carrusel", "modo": "producto", "desc": "Slide de productos"},
            {"tipo_pub": "post_feed", "modo": "servicio", "desc": "Slide final con resultado"},
        ],
        "story": [
            {"tipo_pub": "story", "modo": "servicio", "desc": "Fondo para story"},
        ],
        "reel_portada": [
            {"tipo_pub": "reel_portada", "modo": "servicio", "desc": "Portada del reel"},
        ],
        "antes_despues": [
            {"tipo_pub": "antes_despues", "modo": "servicio", "desc": "Plantilla antes/despues"},
        ],
        "producto": [
            {"tipo_pub": "producto", "modo": "producto", "desc": "Foto de producto"},
        ],
    }
    pack = packs_config.get(tipo_publicacion, packs_config["post_feed"])
    print(f"\n[Esteticai] Pack automatico para: {servicio}")
    print(f"[Esteticai] Tipo: {tipo_publicacion} ({len(pack)} imagenes)")
    resultados = []
    for i, item in enumerate(pack, 1):
        print(f"\n--- Imagen {i}/{len(pack)}: {item['desc']} ---")
        resultado = generar_imagen_automatica(
            servicio=servicio,
            tipo_publicacion=item["tipo_pub"],
            perfil=perfil,
            modo=item["modo"],
        )
        resultado["descripcion"] = item["desc"]
        resultados.append(resultado)
        if "url" in resultado and "error" not in resultado:
            nombre = f"pack_{tipo_publicacion}_{i}.png"
            descargar_imagen(resultado["url"], nombre)
    return resultados


def descargar_imagen(url, nombre_archivo=None, carpeta="output"):
    """Descarga una imagen generada y la guarda en disco."""
    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"esteticai_{timestamp}.png"
    ruta = os.path.join(carpeta, nombre_archivo)
    os.makedirs(carpeta, exist_ok=True)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(response.content)
        print(f"[Esteticai] Imagen guardada en: {ruta}")
        return ruta
    except Exception as e:
        print(f"[ERROR] No se pudo descargar: {e}")
        return None


def quitar_fondo(ruta_imagen, api_key=None):
    """Quita el fondo de una foto usando Photoroom API."""
    key = api_key or os.environ.get("PHOTOROOM_API_KEY")
    if not key:
        print("[MODO DEMO] No hay API key de Photoroom.")
        print("[INFO] Para usar: registrate en https://www.photoroom.com/api")
        return _demo_fondo(ruta_imagen)
    print(f"[Esteticai] Quitando fondo de: {ruta_imagen}")
    try:
        with open(ruta_imagen, "rb") as f:
            response = requests.post(
                "https://sdk.photoroom.com/v1/segment",
                headers={"x-api-key": key},
                files={"image_file": f},
            )
        if response.status_code == 200:
            nombre = os.path.splitext(os.path.basename(ruta_imagen))[0]
            ruta_salida = f"output/{nombre}_sin_fondo.png"
            os.makedirs("output", exist_ok=True)
            with open(ruta_salida, "wb") as f:
                f.write(response.content)
            print(f"[Esteticai] Imagen sin fondo: {ruta_salida}")
            return ruta_salida
        else:
            print(f"[ERROR] Photoroom respondio: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# ============================================================
# MODO DEMO
# ============================================================

def _generar_placeholder(servicio="Tratamiento", tipo_pub="post_feed"):
    """Genera una imagen placeholder profesional con Pillow cuando no hay API."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io, base64

        # Tamanos segun tipo
        tamanos = {
            "post_feed": (1080, 1080), "square": (1080, 1080),
            "story": (1080, 1920), "reel_portada": (1080, 1920),
            "vertical": (1080, 1440), "carrusel": (1080, 1080),
            "antes_despues": (1080, 1080), "producto": (1080, 1080),
        }
        ancho, alto = tamanos.get(tipo_pub, (1080, 1080))

        # Crear imagen con gradiente mint suave
        img = Image.new("RGB", (ancho, alto), (235, 248, 245))
        draw = ImageDraw.Draw(img)

        # Gradiente diagonal
        for y in range(alto):
            r = int(235 - (y / alto) * 30)
            g = int(248 - (y / alto) * 20)
            b = int(245 - (y / alto) * 25)
            draw.line([(0, y), (ancho, y)], fill=(r, g, b))

        # Icono central
        try:
            fuente_grande = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            fuente_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            fuente_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except (OSError, IOError):
            fuente_grande = ImageFont.load_default()
            fuente_med = fuente_grande
            fuente_small = fuente_grande

        # Circulo decorativo central
        cx, cy = ancho // 2, alto // 2 - 40
        radio = 80
        draw.ellipse([(cx - radio, cy - radio), (cx + radio, cy + radio)],
                     fill=(98, 201, 184), outline=(77, 184, 167), width=3)

        # Icono de camara
        icon_text = "AI"
        bbox = draw.textbbox((0, 0), icon_text, font=fuente_grande)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2), icon_text, font=fuente_grande, fill=(255, 255, 255))

        # Texto del servicio
        texto = servicio[:40] if len(servicio) > 40 else servicio
        bbox = draw.textbbox((0, 0), texto, font=fuente_med)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, cy + radio + 30), texto, font=fuente_med, fill=(56, 158, 142))

        # Texto demo
        demo_text = "Vista previa - Imagen generada con IA"
        bbox = draw.textbbox((0, 0), demo_text, font=fuente_small)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, cy + radio + 75), demo_text, font=fuente_small, fill=(180, 160, 170))

        # Marca
        marca = "Esteticai"
        bbox = draw.textbbox((0, 0), marca, font=fuente_med)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, alto - 60), marca, font=fuente_med, fill=(199, 121, 135, 120))

        # Convertir a base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        print(f"[WARN] No se pudo generar placeholder: {e}")
        return None


def _demo_imagen(tipo_preset, variables, prompt_override=None):
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = PROMPTS_ESTETICA.get(tipo_preset, "Professional beauty photography")
        try:
            prompt = prompt.format(**variables)
        except KeyError:
            pass

    # Extraer servicio del prompt para el placeholder
    servicio = variables.get("tratamiento", variables.get("producto", "Tratamiento"))
    placeholder_url = _generar_placeholder(servicio, "post_feed")

    return {
        "url": placeholder_url or "",
        "prompt": prompt,
        "tamano": "square",
        "modelo": "demo",
        "es_demo": True,
        "nota": "Esta es una vista previa. Conecta tu API key de fal.ai para generar imagenes reales con IA."
    }

def _demo_fondo(ruta_imagen):
    print("[DEMO] Simulando eliminacion de fondo")
    return None


def listar_presets():
    """Muestra todos los presets de imagen disponibles."""
    print("\n--- Presets de imagen disponibles ---\n")
    for nombre, plantilla in PROMPTS_ESTETICA.items():
        import re
        vars_found = re.findall(r'\{(\w+)\}', plantilla)
        vars_str = ", ".join(vars_found) if vars_found else "ninguna"
        print(f"  {nombre}")
        print(f"    Variables: {vars_str}")
        print(f"    Prompt: {plantilla[:70]}...")
        print()


def listar_servicios_conocidos():
    """Muestra todos los servicios que el agente conoce."""
    print("\n--- Servicios con conocimiento integrado ---\n")
    for nombre in CONOCIMIENTO_SERVICIOS:
        datos = CONOCIMIENTO_SERVICIOS[nombre]
        print(f"  {nombre.title()}")
        print(f"    Productos tipicos: {datos['productos_tipicos'][:60]}...")
        print(f"    Resultado: {datos['resultado'][:60]}...")
        print()


def listar_tipos_publicacion():
    """Muestra todos los tipos de publicacion disponibles."""
    print("\n--- Tipos de publicacion ---\n")
    tipos = list(ESTILOS_PUBLICACION.keys())
    for i, tipo in enumerate(tipos, 1):
        datos = ESTILOS_PUBLICACION[tipo]
        print(f"  {i}. {tipo}")
        print(f"     Formato: {datos['formato']} | Estilo: {datos['estilo'][:50]}...")
        print()
    return tipos
