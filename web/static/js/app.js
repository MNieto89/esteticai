/* ============================================================
   ESTETICAI - Frontend v1.0
   ============================================================ */

let ultimaImagenUrl = null;


// ============================================================
// SANITIZACIÓN HTML (prevenir XSS en contenido generado por IA)
// ============================================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function skeletonLoader(msg) {
    return `<div class="gen-skeleton">
        <div class="gen-skeleton-line"></div>
        <div class="gen-skeleton-line"></div>
        <div class="gen-skeleton-line"></div>
        <div class="gen-skeleton-line"></div>
        <div class="gen-skeleton-msg">${escapeHtml(msg)}</div>
    </div>`;
}


// ============================================================
// ONBOARDING / TUTORIAL PRIMERA VEZ
// ============================================================

const ONBOARDING_PASOS = [
    {
        titulo: "Bienvenida a Esteticai",
        texto: "Tu asistente de contenido para redes sociales. Te voy a ense&ntilde;ar las herramientas que tienes disponibles.",
        target: null,
    },
    {
        titulo: "Generar Copy",
        texto: "Crea textos profesionales con hashtags, CTA y estrategia para cada publicaci&oacute;n. Solo elige el tipo de post y el servicio.",
        target: "card-copy",
    },
    {
        titulo: "Generar Imagen",
        texto: "Genera im&aacute;genes profesionales con IA para tus posts. Elige servicio y formato, y la IA crea la imagen perfecta.",
        target: "card-imagen",
    },
    {
        titulo: "Crear Video",
        texto: "Convierte tus im&aacute;genes en videos animados para Reels y TikTok. Varios estilos de movimiento disponibles.",
        target: "card-video",
    },
    {
        titulo: "Antes y Despu&eacute;s",
        texto: "Sube la foto del antes y la del despu&eacute;s, y creamos una composici&oacute;n profesional lista para publicar.",
        target: "card-antes-despues",
    },
    {
        titulo: "Mejorar Foto Real",
        texto: "Sube una foto de tu cl&iacute;nica o tratamiento y la mejoramos: cambio de fondo, mejor calidad y aspecto profesional.",
        target: "card-foto",
    },
    {
        titulo: "Calendario Semanal",
        texto: "Genera un plan completo de contenido para toda la semana con estrategia, copys y horarios recomendados.",
        target: "card-calendario",
    },
    {
        titulo: "&iexcl;Todo listo!",
        texto: "Ya conoces todas las herramientas. Pulsa en cualquier tarjeta para empezar a crear contenido para tu negocio.",
        target: null,
    },
];

let onboardingPasoActual = 0;

function iniciarOnboarding() {
    if (localStorage.getItem('esteticai_onboarding_visto')) return;
    if (!document.querySelector('.generators')) return;
    onboardingPasoActual = 0;
    mostrarPasoOnboarding();
}

function mostrarPasoOnboarding() {
    // Limpiar overlay anterior
    const existente = document.getElementById('onboarding-overlay');
    if (existente) existente.remove();
    document.querySelectorAll('.onboarding-highlight').forEach(el => el.classList.remove('onboarding-highlight'));

    if (onboardingPasoActual >= ONBOARDING_PASOS.length) {
        localStorage.setItem('esteticai_onboarding_visto', '1');
        return;
    }

    const paso = ONBOARDING_PASOS[onboardingPasoActual];
    const esUltimo = onboardingPasoActual === ONBOARDING_PASOS.length - 1;
    const esPrimero = onboardingPasoActual === 0;

    // Crear overlay
    const overlay = document.createElement('div');
    overlay.id = 'onboarding-overlay';
    overlay.innerHTML = `
        <div class="onboarding-card">
            <div class="onboarding-step">${onboardingPasoActual + 1} / ${ONBOARDING_PASOS.length}</div>
            <h3 class="onboarding-titulo">${paso.titulo}</h3>
            <p class="onboarding-texto">${paso.texto}</p>
            <div class="onboarding-actions">
                <button class="btn btn-secondary onboarding-btn-skip" onclick="cerrarOnboarding()">Saltar</button>
                <button class="btn btn-primary onboarding-btn-next" onclick="siguientePasoOnboarding()">
                    ${esUltimo ? 'Empezar' : 'Siguiente'}
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    // Highlight target
    if (paso.target) {
        const targetEl = document.getElementById(paso.target);
        if (targetEl) {
            targetEl.classList.add('onboarding-highlight');
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

function siguientePasoOnboarding() {
    onboardingPasoActual++;
    mostrarPasoOnboarding();
}

function cerrarOnboarding() {
    const overlay = document.getElementById('onboarding-overlay');
    if (overlay) overlay.remove();
    document.querySelectorAll('.onboarding-highlight').forEach(el => el.classList.remove('onboarding-highlight'));
    localStorage.setItem('esteticai_onboarding_visto', '1');
}

// Iniciar onboarding al cargar + lazy load de imágenes
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(iniciarOnboarding, 500);
    // Cookie banner
    if (!localStorage.getItem('esteticai_cookies_aceptadas')) {
        const banner = document.getElementById('cookie-banner');
        if (banner) banner.style.display = '';
    }
    // Marcar imágenes del historial como loaded cuando terminan de cargar
    document.querySelectorAll('.historial-img').forEach(img => {
        if (img.complete) { img.classList.add('loaded'); }
        else { img.addEventListener('load', () => img.classList.add('loaded')); }
        img.addEventListener('error', () => img.classList.add('loaded'));  // Quitar shimmer en error también
    });
});

function aceptarCookies() {
    localStorage.setItem('esteticai_cookies_aceptadas', '1');
    const banner = document.getElementById('cookie-banner');
    if (banner) banner.style.display = 'none';
}

// Toggle cards
document.querySelectorAll('.gen-card').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT' ||
            e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
            e.target.tagName === 'LABEL' || e.target.tagName === 'IMG' ||
            e.target.closest('.upload-area') || e.target.closest('.foto-opciones') ||
            e.target.closest('.foto-comparacion') || e.target.closest('.foto-actions') ||
            e.target.closest('.ad-uploads') || e.target.closest('.ad-actions') ||
            e.target.closest('.ad-resultado') || e.target.closest('.gen-result')) return;
        const form = this.querySelector('.gen-form');
        if (form) {
            const isVisible = form.style.display !== 'none';
            // Cerrar todos
            document.querySelectorAll('.gen-form').forEach(f => f.style.display = 'none');
            document.querySelectorAll('.gen-card').forEach(c => c.classList.remove('active'));
            // Abrir este
            if (!isVisible) {
                form.style.display = 'flex';
                this.classList.add('active');
            }
        }
    });
});


// ============================================================
// SISTEMA DE NOTIFICACIONES TOAST
// ============================================================

function mostrarToast(mensaje, tipo = 'info', duracion = 4000) {
    const container = document.getElementById('toast-container') || crearToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensaje;
    container.appendChild(toast);
    // Trigger animation
    requestAnimationFrame(() => toast.classList.add('toast-visible'));
    setTimeout(() => {
        toast.classList.remove('toast-visible');
        setTimeout(() => toast.remove(), 300);
    }, duracion);
}

function crearToastContainer() {
    const c = document.createElement('div');
    c.id = 'toast-container';
    c.setAttribute('role', 'status');
    c.setAttribute('aria-live', 'polite');
    c.setAttribute('aria-label', 'Notificaciones');
    document.body.appendChild(c);
    return c;
}


// ============================================================
// API CALL CON MANEJO DE ERRORES
// ============================================================

async function apiCall(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok && json.error) {
        if (res.status === 429) {
            mostrarToast(json.error, 'warning', 6000);
        } else if (res.status === 401) {
            mostrarSesionExpirada();
        } else if (res.status >= 500) {
            mostrarToast(json.error || 'Error del servidor. Intentalo de nuevo.', 'error', 5000);
        }
    }
    return json;
}

function mostrarSesionExpirada() {
    // Evitar mostrar el overlay multiples veces
    if (document.getElementById('sesion-expirada-overlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'sesion-expirada-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
    overlay.innerHTML = `
        <div style="background:white;border-radius:16px;padding:32px;text-align:center;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.2);">
            <div style="font-size:40px;margin-bottom:12px;">&#128274;</div>
            <h3 style="margin:0 0 8px;font-size:18px;">Sesi\u00f3n expirada</h3>
            <p style="color:#888;font-size:14px;margin:0 0 20px;">Tu sesi\u00f3n ha caducado por seguridad. Inicia sesi\u00f3n de nuevo para continuar.</p>
            <a href="/login" class="btn btn-primary" style="display:inline-block;padding:10px 32px;">Iniciar sesi\u00f3n</a>
        </div>
    `;
    document.body.appendChild(overlay);
}


// ============================================================
// PROTECCION ANTI-DOBLE-CLICK
// ============================================================

const _generando = {};

function bloquearBoton(key, btn) {
    if (_generando[key]) return false;
    _generando[key] = true;
    if (btn) { btn.disabled = true; btn._textoOriginal = btn.textContent; btn.textContent = 'Generando...'; }
    return true;
}

function desbloquearBoton(key, btn) {
    _generando[key] = false;
    if (btn) { btn.disabled = false; btn.textContent = btn._textoOriginal || 'Generar'; }
}


// ============================================================
// GENERAR COPY
// ============================================================

async function generarCopy() {
    const btn = document.querySelector('#form-copy .btn-primary');
    if (!bloquearBoton('copy', btn)) return;

    const tipo = document.getElementById('copy-tipo').value;
    const servicio = document.getElementById('copy-servicio').value;
    const resultDiv = document.getElementById('result-copy');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Generando copy profesional para tu negocio...');

    try {
        const data = await apiCall('/api/generar/copy', { tipo, servicio });
        if (data.ok) {
            const copy = data.copy;
            if (copy.error) {
                resultDiv.innerHTML = `<div>Error: ${escapeHtml(copy.error)}</div>`;
                return;
            }
            let html = '';

            // Copy principal (preservar saltos de linea, escapar HTML)
            const copyText = escapeHtml(copy.copy).replace(/\n/g, '<br>');
            html += `<div class="copy-texto">${copyText}</div>`;

            // Hashtags
            if (copy.hashtags && copy.hashtags.length > 0) {
                html += `<div class="copy-hashtags">${copy.hashtags.map(h => escapeHtml(h)).join(' ')}</div>`;
            }

            // Meta info
            html += `<div class="copy-meta">`;
            if (copy.formato_recomendado) html += `<span class="copy-tag">${escapeHtml(copy.formato_recomendado)}</span>`;
            if (copy.red_social_ideal) html += `<span class="copy-tag">${escapeHtml(copy.red_social_ideal)}</span>`;
            if (copy.hora_recomendada) html += `<span class="copy-tag">${escapeHtml(copy.hora_recomendada)}</span>`;
            html += `</div>`;

            // CTA
            if (copy.cta) html += `<div class="copy-cta">${escapeHtml(copy.cta)}</div>`;

            // Nota para la clienta
            if (copy.nota_para_la_clienta) {
                html += `<div class="copy-nota">${escapeHtml(copy.nota_para_la_clienta)}</div>`;
            }

            // Botones copiar y regenerar
            html += `<div class="copy-actions">`;
            html += `<button class="btn btn-secondary" onclick="copiarTexto(this)" data-copy="${encodeURIComponent(copy.copy || '')}">Copiar copy</button>`;
            html += `<button class="btn btn-secondary" onclick="generarCopy()">Regenerar</button>`;
            html += `</div>`;

            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<div>Error: ${escapeHtml(data.error)}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error de conexion: ${escapeHtml(e.message)}</div>`;
    } finally {
        desbloquearBoton('copy', btn);
    }
}


// ============================================================
// GENERAR IMAGEN
// ============================================================

async function generarImagen() {
    const btn = document.querySelector('#form-imagen .btn-primary');
    if (!bloquearBoton('imagen', btn)) return;

    const servicio = document.getElementById('img-servicio').value;
    const tipo = document.getElementById('img-tipo').value;
    const resultDiv = document.getElementById('result-imagen');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Generando imagen profesional con IA...');

    try {
        const data = await apiCall('/api/generar/imagen', {
            servicio, tipo_publicacion: tipo, modo: 'servicio'
        });
        if (data.ok && data.imagen) {
            const img = data.imagen;
            const tieneUrl = img.url && (img.url.startsWith('http') || img.url.startsWith('data:'));
            if (tieneUrl) {
                let html = `<img src="${img.url}" alt="Imagen generada">`;

                if (img.es_demo) {
                    html += `<div class="demo-aviso">
                        <strong>Vista previa</strong> &mdash; Esta es una imagen de ejemplo.
                        Con la API de fal.ai conectada, se generar&aacute; una imagen real con IA.
                    </div>`;
                } else {
                    ultimaImagenUrl = img.url;
                    html += `<div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
                        <button class="btn btn-primary" onclick="descargarImagen('${img.url}', 'esteticai_imagen')">
                            Descargar imagen
                        </button>
                        <button class="btn btn-secondary" onclick="prepararVideo()">
                            Convertir en video
                        </button>
                        <button class="btn btn-secondary" onclick="generarImagen()">
                            Regenerar
                        </button>
                    </div>`;
                    document.getElementById('video-url').value = img.url;
                    document.getElementById('btn-video').disabled = false;
                    document.getElementById('btn-video').textContent = 'Crear video';
                }
                resultDiv.innerHTML = html;
            } else {
                resultDiv.innerHTML = `<div class="demo-aviso">
                    <strong>Modo demo</strong> &mdash; La generaci&oacute;n de im&aacute;genes requiere una API key de fal.ai.
                </div>`;
            }
        } else {
            resultDiv.innerHTML = `<div class="error-msg">No se pudo generar la imagen. ${escapeHtml(data.error || '')}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
    } finally {
        desbloquearBoton('imagen', btn);
    }
}


function prepararVideo() {
    if (!ultimaImagenUrl) return;
    // Scroll a la tarjeta de video
    const cardVideo = document.getElementById('card-video');
    const formVideo = document.getElementById('form-video');
    document.querySelectorAll('.gen-form').forEach(f => f.style.display = 'none');
    document.querySelectorAll('.gen-card').forEach(c => c.classList.remove('active'));
    formVideo.style.display = 'flex';
    cardVideo.classList.add('active');
    document.getElementById('video-url').value = ultimaImagenUrl;
    document.getElementById('btn-video').disabled = false;
    document.getElementById('btn-video').textContent = 'Crear video';
    cardVideo.scrollIntoView({ behavior: 'smooth' });
}


// ============================================================
// GENERAR VIDEO
// ============================================================

async function generarVideo() {
    const btn = document.getElementById('btn-video');
    if (!bloquearBoton('video', btn)) return;

    const urlImagen = document.getElementById('video-url').value;
    const movimiento = document.getElementById('video-movimiento').value;
    const duracion = parseInt(document.getElementById('video-duracion').value);
    const resultDiv = document.getElementById('result-video');

    if (!urlImagen.startsWith('http')) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>Genera una imagen primero</div>';
        desbloquearBoton('video', btn);
        return;
    }

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Creando video para Reels (1-3 minutos)...');

    try {
        const data = await apiCall('/api/generar/video', {
            url_imagen: urlImagen,
            tipo_movimiento: movimiento,
            duracion: duracion,
        });
        if (data.ok && data.video) {
            const video = data.video;
            if (video.es_demo) {
                resultDiv.innerHTML = `<div class="demo-aviso">
                    <strong>Modo demo</strong> &mdash; ${video.nota || 'La generaci&oacute;n de video requiere una API key de fal.ai con saldo.'}
                </div>`;
            } else if (video.url && video.url.startsWith('http')) {
                resultDiv.innerHTML = `
                    <video controls autoplay muted loop style="max-width:100%;border-radius:8px;">
                        <source src="${video.url}" type="video/mp4">
                    </video>
                    <div style="margin-top:8px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
                        <a href="${video.url}" download class="btn btn-primary" target="_blank" rel="noopener noreferrer">
                            Descargar video
                        </a>
                        <button class="btn btn-secondary" onclick="generarVideo()">
                            Regenerar
                        </button>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div class="demo-aviso">
                    <strong>Modo demo</strong> &mdash; No se pudo generar el video. Verifica tu API key de fal.ai.
                </div>`;
            }
        } else {
            resultDiv.innerHTML = `<div class="error-msg">No se pudo generar el video. ${escapeHtml(data.error || '')}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
    } finally {
        desbloquearBoton('video', btn);
    }
}


// ============================================================
// GENERAR CALENDARIO
// ============================================================

async function generarCalendario() {
    const btn = document.querySelector('#form-calendario .btn-primary');
    if (!bloquearBoton('calendario', btn)) return;

    const contexto = document.getElementById('cal-contexto').value;
    const resultDiv = document.getElementById('result-calendario');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Generando calendario semanal con estrategia...');

    try {
        const data = await apiCall('/api/generar/calendario', {
            contexto: contexto || null
        });
        if (data.ok && data.calendario) {
            const cal = data.calendario;
            let html = '';

            // Estrategia semanal
            const estrategia = cal.estrategia_semanal || cal.estrategia || '';
            if (estrategia) {
                html += `<div class="cal-estrategia"><strong>Estrategia de la semana:</strong> ${escapeHtml(estrategia)}</div>`;
            }

            // Publicaciones (soporta ambos formatos)
            const pubs = cal.calendario_semanal || cal.publicaciones || [];
            if (pubs.length > 0) {
                pubs.forEach(pub => {
                    const hora = escapeHtml(pub.hora_publicacion || pub.hora || '');
                    const red = escapeHtml(pub.red_social || '');
                    const tipo = escapeHtml(pub.tipo_contenido || pub.tipo || '');
                    const formato = escapeHtml(pub.formato || '');

                    html += `<div class="cal-dia">`;
                    html += `<div class="cal-dia-header">`;
                    html += `<strong>${escapeHtml(pub.dia || '')}</strong>`;
                    html += `<span class="cal-meta">${hora} · ${red} · ${formato}</span>`;
                    html += `</div>`;
                    if (tipo) html += `<span class="cal-tipo">${tipo}</span>`;
                    html += `<div class="cal-copy">${escapeHtml(pub.copy || '')}</div>`;
                    if (pub.hashtags) {
                        const tags = Array.isArray(pub.hashtags) ? pub.hashtags.map(h => escapeHtml(h)).join(' ') : escapeHtml(pub.hashtags);
                        html += `<div class="hashtags">${tags}</div>`;
                    }
                    if (pub.cta) html += `<div class="cal-cta">${escapeHtml(pub.cta)}</div>`;
                    if (pub.nota_para_la_clienta) {
                        html += `<div class="cal-nota">${escapeHtml(pub.nota_para_la_clienta)}</div>`;
                    }
                    html += `</div>`;
                });
            }

            // Consejo de la semana
            const consejo = cal.consejo_de_la_semana || cal.consejo || '';
            if (consejo) {
                html += `<div class="cal-consejo"><strong>Consejo de la semana:</strong> ${escapeHtml(consejo)}</div>`;
            }

            // Botones regenerar y exportar PDF
            html += `<div style="margin-top:16px; text-align:center; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="exportarCalendarioPDF()">Exportar a PDF</button>
                <button class="btn btn-secondary" onclick="generarCalendario()">Regenerar calendario</button>
            </div>`;

            // Guardar calendario para exportar
            window._ultimoCalendario = cal;

            resultDiv.innerHTML = html || '<div>Calendario generado (revisa la consola para detalles)</div>';
        } else {
            resultDiv.innerHTML = `<div>Error: ${escapeHtml(data.error || 'Error desconocido')}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
    } finally {
        desbloquearBoton('calendario', btn);
    }
}


// ============================================================
// MEJORAR FOTO REAL
// ============================================================

let fotoSeleccionada = null;

function previewFoto(input) {
    if (input.files && input.files[0]) {
        fotoSeleccionada = input.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('foto-preview');
            const placeholder = document.getElementById('upload-placeholder');
            preview.src = e.target.result;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
            document.getElementById('btn-foto').disabled = false;
            document.getElementById('btn-foto').textContent = 'Mejorar foto';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function mejorarFoto() {
    if (!fotoSeleccionada) return;

    // Validar archivo
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

    if (fotoSeleccionada.size > maxSize) {
        mostrarToast('La foto es demasiado grande. Maximo 10MB.', 'error');
        return;
    }
    if (!allowedTypes.includes(fotoSeleccionada.type)) {
        mostrarToast('Formato no soportado. Usa JPG, PNG o WebP.', 'error');
        return;
    }

    const tipoTratamiento = document.getElementById('foto-tipo-tratamiento').value;
    const tipoFondo = document.getElementById('foto-fondo').value;
    const quitarFondo = document.getElementById('foto-quitar-fondo').checked;
    const mejorarCalidad = document.getElementById('foto-mejorar').checked;
    const resultDiv = document.getElementById('result-foto');
    const btn = document.getElementById('btn-foto');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Mejorando tu foto profesionalmente...');
    btn.disabled = true;
    btn.textContent = 'Procesando...';

    const formData = new FormData();
    formData.append('foto', fotoSeleccionada);
    formData.append('tipo_tratamiento', tipoTratamiento);
    formData.append('tipo_fondo', tipoFondo);
    formData.append('eliminar_fondo', quitarFondo.toString());
    formData.append('mejorar_calidad', mejorarCalidad.toString());

    try {
        const res = await fetch('/api/mejorar-foto', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        if (data.ok && data.resultado) {
            const r = data.resultado;
            let html = '';

            if (r.url_final && r.url_final.startsWith('http')) {
                html += `<div class="foto-comparacion">`;
                html += `<div class="foto-antes">`;
                html += `<span class="foto-label">Original</span>`;
                html += `<img src="${r.original_url}" alt="Original">`;
                html += `</div>`;
                html += `<div class="foto-despues">`;
                html += `<span class="foto-label">Mejorada</span>`;
                html += `<img src="${r.url_final}" alt="Mejorada">`;
                html += `</div>`;
                html += `</div>`;

                html += `<div class="foto-info"><span>${r.total_pasos} mejoras aplicadas</span></div>`;

                html += `<div class="foto-actions">`;
                html += `<button class="btn btn-primary" onclick="descargarImagen('${r.url_final}', 'esteticai_foto_mejorada')">Descargar imagen</button>`;
                html += `<button class="btn btn-secondary" onclick="usarParaVideo('${r.url_final}')">Crear video</button>`;
                html += `<button class="btn btn-secondary" onclick="mejorarFoto()">Regenerar</button>`;
                html += `</div>`;

                ultimaImagenUrl = r.url_final;
                document.getElementById('video-url').value = r.url_final;
                document.getElementById('btn-video').disabled = false;
                document.getElementById('btn-video').textContent = 'Crear video';
            } else {
                html = '<div>Foto procesada en modo demo (configura FAL_KEY para resultados reales)</div>';
            }

            if (r.errores && r.errores.length > 0) {
                html += `<div class="foto-errores">Avisos: ${r.errores.join(', ')}</div>`;
            }

            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<div>Error: ${escapeHtml(data.error || 'Error desconocido')}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error de conexion: ${escapeHtml(e.message)}</div>`;
    }

    btn.disabled = false;
    btn.textContent = 'Mejorar otra foto';
}

function usarParaVideo(url) {
    const cardVideo = document.getElementById('card-video');
    const formVideo = document.getElementById('form-video');
    document.querySelectorAll('.gen-form').forEach(f => f.style.display = 'none');
    document.querySelectorAll('.gen-card').forEach(c => c.classList.remove('active'));
    formVideo.style.display = 'flex';
    cardVideo.classList.add('active');
    document.getElementById('video-url').value = url;
    document.getElementById('btn-video').disabled = false;
    document.getElementById('btn-video').textContent = 'Crear video';
    cardVideo.scrollIntoView({ behavior: 'smooth' });
}


// ============================================================
// ANTES / DESPUES
// ============================================================

let adFotoAntes = null;
let adFotoDespues = null;

function previewAD(input, tipo) {
    const file = input.files[0];
    if (!file) return;

    const maxSize = 10 * 1024 * 1024;
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

    if (file.size > maxSize) {
        mostrarToast('La foto es demasiado grande. Maximo 10MB.', 'error');
        input.value = '';
        return;
    }
    if (!allowedTypes.includes(file.type)) {
        mostrarToast('Formato no soportado. Usa JPG, PNG o WebP.', 'error');
        input.value = '';
        return;
    }

    if (tipo === 'antes') {
        adFotoAntes = file;
    } else {
        adFotoDespues = file;
    }

    // Preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('ad-preview-' + tipo);
        const placeholder = document.getElementById('ad-placeholder-' + tipo);
        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Activar boton si las dos fotos estan subidas
    const btn = document.getElementById('btn-ad');
    if (adFotoAntes && adFotoDespues) {
        btn.disabled = false;
        btn.textContent = 'Crear composicion';
    }
}

async function componerAntesDespues() {
    if (!adFotoAntes || !adFotoDespues) return;

    const plantilla = document.getElementById('ad-plantilla').value;
    const tratamiento = document.getElementById('ad-tratamiento').value;
    const sesiones = document.getElementById('ad-sesiones').value;
    const resultDiv = document.getElementById('result-antes-despues');
    const btn = document.getElementById('btn-ad');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = skeletonLoader('Creando composición antes/después...');
    btn.disabled = true;
    btn.textContent = 'Creando...';

    const formData = new FormData();
    formData.append('foto_antes', adFotoAntes);
    formData.append('foto_despues', adFotoDespues);
    formData.append('plantilla', plantilla);
    formData.append('tratamiento', tratamiento);
    formData.append('sesiones', sesiones);

    try {
        const resp = await fetch('/api/componer-antes-despues', {
            method: 'POST',
            body: formData,
        });
        const data = await resp.json();

        if (data.ok) {
            const r = data.resultado;
            let html = '';
            html += `<div class="ad-resultado">`;
            html += `<img src="${r.image_base64}" class="ad-imagen-resultado" alt="Composicion antes/despues">`;
            html += `<div class="ad-info">`;
            html += `<span class="copy-tag">${r.plantilla_nombre}</span>`;
            html += `<span class="copy-tag">${r.ancho}x${r.alto}</span>`;
            html += `<span class="copy-tag">${r.tamano_kb} KB</span>`;
            html += `</div>`;
            html += `<div class="ad-actions">`;
            html += `<button class="btn btn-primary" onclick="descargarImagen('${r.image_base64}', 'esteticai_antes_despues_${plantilla}')">Descargar imagen</button>`;
            html += `<button class="btn btn-secondary" onclick="resetAntesDespues()">Crear otra</button>`;
            html += `</div>`;
            html += `</div>`;
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<div>Error: ${escapeHtml(data.error)}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error de conexion: ${escapeHtml(e.message)}</div>`;
    }

    btn.disabled = false;
    btn.textContent = 'Crear composicion';
}

function resetAntesDespues() {
    adFotoAntes = null;
    adFotoDespues = null;
    document.getElementById('ad-foto-antes').value = '';
    document.getElementById('ad-foto-despues').value = '';
    document.getElementById('ad-preview-antes').style.display = 'none';
    document.getElementById('ad-preview-despues').style.display = 'none';
    document.getElementById('ad-placeholder-antes').style.display = '';
    document.getElementById('ad-placeholder-despues').style.display = '';
    document.getElementById('btn-ad').disabled = true;
    document.getElementById('btn-ad').textContent = 'Sube las dos fotos';
    document.getElementById('result-antes-despues').style.display = 'none';
}


// ============================================================
// DESCARGAR IMAGEN (universal - URL y base64)
// ============================================================

function descargarImagen(src, nombre) {
    const fecha = new Date();
    const timestamp = fecha.toISOString().slice(0,10).replace(/-/g, '');
    const hora = fecha.toTimeString().slice(0,5).replace(':', '');
    // Detectar extensión desde la URL o data URI
    let ext = 'jpg';
    if (src.startsWith('data:image/png')) ext = 'png';
    else if (src.startsWith('data:image/webp') || src.includes('.webp')) ext = 'webp';
    else if (src.includes('.png')) ext = 'png';
    const filename = `${nombre || 'esteticai'}_${timestamp}_${hora}.${ext}`;

    function _descargar(href) {
        const a = document.createElement('a');
        a.href = href;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        mostrarToast('Imagen descargada', 'success', 2000);
    }

    if (src.startsWith('data:')) {
        _descargar(src);
    } else {
        fetch(src)
            .then(r => r.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                _descargar(url);
                setTimeout(() => URL.revokeObjectURL(url), 5000);
            })
            .catch(() => {
                window.open(src, '_blank', 'noopener,noreferrer');
                mostrarToast('Abriendo imagen en nueva ventana', 'info', 2000);
            });
    }
}


function copiarTexto(btn) {
    const texto = decodeURIComponent(btn.dataset.copy);
    const original = btn.textContent;

    function marcarCopiado() {
        btn.textContent = '\u2713 Copiado';
        btn.style.background = '#27ae60';
        btn.style.color = '#fff';
        btn.style.borderColor = '#27ae60';
        mostrarToast('Texto copiado al portapapeles', 'success', 2000);
        setTimeout(() => {
            btn.textContent = original;
            btn.style.background = '';
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 2000);
    }

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(texto).then(marcarCopiado).catch(() => {
            _copiarFallback(texto);
            marcarCopiado();
        });
    } else {
        _copiarFallback(texto);
        marcarCopiado();
    }
}

function _copiarFallback(texto) {
    const ta = document.createElement('textarea');
    ta.value = texto;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
}


// ============================================================
// EXPORTAR CALENDARIO A PDF
// ============================================================

async function exportarCalendarioPDF() {
    if (!window._ultimoCalendario) {
        mostrarToast('Genera un calendario primero', 'warning');
        return;
    }

    try {
        const data = await apiCall('/api/calendario/pdf', {
            calendario: window._ultimoCalendario
        });

        if (data.ok && data.pdf_base64) {
            const a = document.createElement('a');
            a.href = data.pdf_base64;
            a.download = data.filename || 'calendario_esteticai.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            mostrarToast('PDF descargado', 'success', 2000);
        } else {
            mostrarToast(data.error || 'Error al generar el PDF', 'error');
        }
    } catch (e) {
        mostrarToast('Error de conexion: ' + e.message, 'error');
    }
}


// ============================================================
// HISTORIAL - FILTROS
// ============================================================

// ============================================================
// INDICADOR DE FORTALEZA DE CONTRASEÑA
// ============================================================

function evaluarPassword(password) {
    const strengthDiv = document.getElementById('password-strength');
    const fill = document.getElementById('password-fill');
    const label = document.getElementById('password-label');
    if (!strengthDiv || !fill || !label) return;

    if (!password) { strengthDiv.style.display = 'none'; return; }
    strengthDiv.style.display = 'flex';

    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    const levels = [
        { min: 0, max: 1, pct: 15, color: '#e74c3c', text: 'Muy d\u00e9bil' },
        { min: 2, max: 2, pct: 35, color: '#e67e22', text: 'D\u00e9bil' },
        { min: 3, max: 3, pct: 55, color: '#f1c40f', text: 'Aceptable' },
        { min: 4, max: 4, pct: 75, color: '#27ae60', text: 'Buena' },
        { min: 5, max: 6, pct: 100, color: '#27ae60', text: 'Fuerte' },
    ];

    const level = levels.find(l => score >= l.min && score <= l.max) || levels[0];
    fill.style.width = level.pct + '%';
    fill.style.background = level.color;
    label.textContent = level.text;
    label.style.color = level.color;
}


function filtrarHistorial(tipo, btn) {
    // Actualizar botones activos y aria-pressed
    document.querySelectorAll('.historial-filtro').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');

    // Filtrar items
    document.querySelectorAll('.historial-item').forEach(item => {
        if (tipo === 'todos' || item.dataset.tipo === tipo) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}


// ============================================================
// INDICADOR OFFLINE
// ============================================================

(function() {
    let offlineBanner = null;

    function crearBannerOffline() {
        if (offlineBanner) return;
        offlineBanner = document.createElement('div');
        offlineBanner.id = 'offline-banner';
        offlineBanner.setAttribute('role', 'alert');
        offlineBanner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#e67e22;color:white;text-align:center;padding:8px 16px;font-size:13px;font-weight:600;z-index:10001;transform:translateY(-100%);transition:transform 0.3s ease;';
        offlineBanner.textContent = 'Sin conexi\u00f3n a internet — algunas funciones no estar\u00e1n disponibles';
        document.body.appendChild(offlineBanner);
        requestAnimationFrame(() => { offlineBanner.style.transform = 'translateY(0)'; });
    }

    function ocultarBannerOffline() {
        if (!offlineBanner) return;
        offlineBanner.style.transform = 'translateY(-100%)';
        setTimeout(() => { if (offlineBanner) { offlineBanner.remove(); offlineBanner = null; } }, 300);
    }

    window.addEventListener('offline', crearBannerOffline);
    window.addEventListener('online', () => {
        ocultarBannerOffline();
        mostrarToast('Conexi\u00f3n restaurada', 'success');
    });

    // Comprobar estado inicial
    if (!navigator.onLine) crearBannerOffline();
})();
