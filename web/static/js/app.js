/* ============================================================
   ESTETICAI - Frontend v1.0
   ============================================================ */

let ultimaImagenUrl = null;

// Toggle cards
document.querySelectorAll('.gen-card').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT' ||
            e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
            e.target.tagName === 'LABEL' || e.target.tagName === 'IMG' ||
            e.target.closest('.upload-area') || e.target.closest('.foto-opciones') ||
            e.target.closest('.foto-comparacion') || e.target.closest('.foto-actions') ||
            e.target.closest('.gen-result')) return;
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


async function apiCall(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return await res.json();
}


// ============================================================
// GENERAR COPY
// ============================================================

async function generarCopy() {
    const tipo = document.getElementById('copy-tipo').value;
    const servicio = document.getElementById('copy-servicio').value;
    const resultDiv = document.getElementById('result-copy');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">Generando copy</div>';

    try {
        const data = await apiCall('/api/generar/copy', { tipo, servicio });
        if (data.ok) {
            const copy = data.copy;
            if (copy.error) {
                resultDiv.innerHTML = `<div>Error: ${copy.error}</div>`;
                return;
            }
            let html = '';

            // Copy principal (preservar saltos de linea)
            const copyText = (copy.copy || '').replace(/\n/g, '<br>');
            html += `<div class="copy-texto">${copyText}</div>`;

            // Hashtags
            if (copy.hashtags && copy.hashtags.length > 0) {
                html += `<div class="copy-hashtags">${copy.hashtags.join(' ')}</div>`;
            }

            // Meta info
            html += `<div class="copy-meta">`;
            if (copy.formato_recomendado) html += `<span class="copy-tag">${copy.formato_recomendado}</span>`;
            if (copy.red_social_ideal) html += `<span class="copy-tag">${copy.red_social_ideal}</span>`;
            if (copy.hora_recomendada) html += `<span class="copy-tag">${copy.hora_recomendada}</span>`;
            html += `</div>`;

            // CTA
            if (copy.cta) html += `<div class="copy-cta">${copy.cta}</div>`;

            // Nota para la clienta
            if (copy.nota_para_la_clienta) {
                html += `<div class="copy-nota">${copy.nota_para_la_clienta}</div>`;
            }

            // Boton copiar
            html += `<div class="copy-actions">`;
            html += `<button class="btn btn-secondary" onclick="copiarTexto(this)" data-copy="${encodeURIComponent(copy.copy || '')}">Copiar copy</button>`;
            html += `</div>`;

            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<div>Error: ${data.error}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error de conexion: ${e.message}</div>`;
    }
}


// ============================================================
// GENERAR IMAGEN
// ============================================================

async function generarImagen() {
    const servicio = document.getElementById('img-servicio').value;
    const tipo = document.getElementById('img-tipo').value;
    const resultDiv = document.getElementById('result-imagen');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">Generando imagen (10-20 segundos)</div>';

    try {
        const data = await apiCall('/api/generar/imagen', {
            servicio, tipo_publicacion: tipo, modo: 'servicio'
        });
        if (data.ok && data.imagen) {
            const img = data.imagen;
            if (img.url && img.url.startsWith('http')) {
                ultimaImagenUrl = img.url;
                resultDiv.innerHTML = `
                    <img src="${img.url}" alt="Imagen generada">
                    <div style="margin-top:12px;">
                        <button class="btn btn-primary" onclick="prepararVideo()">
                            Convertir en video para Reels
                        </button>
                    </div>
                `;
                // Habilitar boton de video
                document.getElementById('video-url').value = img.url;
                document.getElementById('btn-video').disabled = false;
                document.getElementById('btn-video').textContent = 'Crear video';
            } else {
                resultDiv.innerHTML = `<div>${img.url || 'Imagen generada en modo demo'}</div>`;
            }
        } else {
            resultDiv.innerHTML = `<div>Error: ${data.error || 'Error desconocido'}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
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
    const urlImagen = document.getElementById('video-url').value;
    const movimiento = document.getElementById('video-movimiento').value;
    const duracion = parseInt(document.getElementById('video-duracion').value);
    const resultDiv = document.getElementById('result-video');

    if (!urlImagen.startsWith('http')) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>Genera una imagen primero</div>';
        return;
    }

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">Generando video (1-3 minutos, paciencia)</div>';

    try {
        const data = await apiCall('/api/generar/video', {
            url_imagen: urlImagen,
            tipo_movimiento: movimiento,
            duracion: duracion,
        });
        if (data.ok && data.video) {
            const video = data.video;
            if (video.url && video.url.startsWith('http')) {
                resultDiv.innerHTML = `
                    <video controls autoplay muted loop>
                        <source src="${video.url}" type="video/mp4">
                    </video>
                    <div style="margin-top:8px;">
                        <a href="${video.url}" download class="btn btn-secondary" target="_blank">
                            Descargar video
                        </a>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `<div>${video.url || 'Video generado en modo demo'}</div>`;
            }
        } else {
            resultDiv.innerHTML = `<div>Error: ${data.error || 'Error desconocido'}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
    }
}


// ============================================================
// GENERAR CALENDARIO
// ============================================================

async function generarCalendario() {
    const contexto = document.getElementById('cal-contexto').value;
    const resultDiv = document.getElementById('result-calendario');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">Generando calendario semanal (15-30 segundos)</div>';

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
                html += `<div class="cal-estrategia"><strong>Estrategia de la semana:</strong> ${estrategia}</div>`;
            }

            // Publicaciones (soporta ambos formatos)
            const pubs = cal.calendario_semanal || cal.publicaciones || [];
            if (pubs.length > 0) {
                pubs.forEach(pub => {
                    const hora = pub.hora_publicacion || pub.hora || '';
                    const red = pub.red_social || '';
                    const tipo = pub.tipo_contenido || pub.tipo || '';
                    const formato = pub.formato || '';

                    html += `<div class="cal-dia">`;
                    html += `<div class="cal-dia-header">`;
                    html += `<strong>${pub.dia || ''}</strong>`;
                    html += `<span class="cal-meta">${hora} · ${red} · ${formato}</span>`;
                    html += `</div>`;
                    if (tipo) html += `<span class="cal-tipo">${tipo}</span>`;
                    html += `<div class="cal-copy">${pub.copy || ''}</div>`;
                    if (pub.hashtags) {
                        html += `<div class="hashtags">${Array.isArray(pub.hashtags) ? pub.hashtags.join(' ') : pub.hashtags}</div>`;
                    }
                    if (pub.cta) html += `<div class="cal-cta">${pub.cta}</div>`;
                    if (pub.nota_para_la_clienta) {
                        html += `<div class="cal-nota">${pub.nota_para_la_clienta}</div>`;
                    }
                    html += `</div>`;
                });
            }

            // Consejo de la semana
            const consejo = cal.consejo_de_la_semana || cal.consejo || '';
            if (consejo) {
                html += `<div class="cal-consejo"><strong>Consejo de la semana:</strong> ${consejo}</div>`;
            }

            resultDiv.innerHTML = html || '<div>Calendario generado (revisa la consola para detalles)</div>';
        } else {
            resultDiv.innerHTML = `<div>Error: ${data.error || 'Error desconocido'}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
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
        const resultDiv = document.getElementById('result-foto');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>La foto es demasiado grande. Maximo 10MB.</div>';
        return;
    }
    if (!allowedTypes.includes(fotoSeleccionada.type)) {
        const resultDiv = document.getElementById('result-foto');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>Formato no soportado. Usa JPG, PNG o WebP.</div>';
        return;
    }

    const tipoTratamiento = document.getElementById('foto-tipo-tratamiento').value;
    const tipoFondo = document.getElementById('foto-fondo').value;
    const quitarFondo = document.getElementById('foto-quitar-fondo').checked;
    const mejorarCalidad = document.getElementById('foto-mejorar').checked;
    const resultDiv = document.getElementById('result-foto');
    const btn = document.getElementById('btn-foto');

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div class="loading">Procesando foto (30-60 segundos)</div>';
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
                html += `<a href="${r.url_final}" download class="btn btn-primary" target="_blank">Descargar imagen</a>`;
                html += `<button class="btn btn-secondary" onclick="usarParaVideo('${r.url_final}')">Crear video con esta foto</button>`;
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
            resultDiv.innerHTML = `<div>Error: ${data.error || 'Error desconocido'}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error de conexion: ${e.message}</div>`;
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


function copiarTexto(btn) {
    const texto = decodeURIComponent(btn.dataset.copy);
    navigator.clipboard.writeText(texto).then(() => {
        const original = btn.textContent;
        btn.textContent = 'Copiado!';
        btn.style.background = '#27ae60';
        btn.style.color = '#fff';
        setTimeout(() => {
            btn.textContent = original;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    }).catch(() => {
        // Fallback para navegadores sin clipboard API
        const ta = document.createElement('textarea');
        ta.value = texto;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = 'Copiado!';
        setTimeout(() => { btn.textContent = 'Copiar copy'; }, 2000);
    });
}
