/* ============================================================
   ESTETICAI - Frontend v1.0
   ============================================================ */

let ultimaImagenUrl = null;

// Toggle cards
document.querySelectorAll('.gen-card').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT' ||
            e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
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
            resultDiv.innerHTML = `
                <div>${copy.copy || ''}</div>
                <div class="hashtags">${(copy.hashtags || []).join(' ')}</div>
                <div class="cta">${copy.cta || ''}</div>
            `;
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
            if (cal.estrategia) {
                html += `<div style="margin-bottom:16px;"><strong>Estrategia:</strong> ${cal.estrategia}</div>`;
            }
            if (cal.publicaciones) {
                cal.publicaciones.forEach(pub => {
                    html += `<div style="border-top:1px solid #ddd; padding-top:12px; margin-top:12px;">`;
                    html += `<strong>${pub.dia || ''} | ${pub.hora || ''} | ${pub.red_social || ''}</strong>`;
                    html += `<div style="margin-top:4px;">${pub.copy || ''}</div>`;
                    if (pub.hashtags) {
                        html += `<div class="hashtags">${Array.isArray(pub.hashtags) ? pub.hashtags.join(' ') : pub.hashtags}</div>`;
                    }
                    html += `</div>`;
                });
            }
            if (cal.consejo) {
                html += `<div style="border-top:1px solid #ddd; padding-top:12px; margin-top:12px;"><strong>Consejo:</strong> ${cal.consejo}</div>`;
            }
            resultDiv.innerHTML = html || '<div>Calendario generado (revisa la consola para detalles)</div>';
        } else {
            resultDiv.innerHTML = `<div>Error: ${data.error || 'Error desconocido'}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div>Error: ${e.message}</div>`;
    }
}
