# Reel intro · «De la física y la química… a tu mano»

Apertura de 55 s para el keynote. Una sola toma: sintonía de TV → logo → tarde fría en la CDMX → SMAA despierta y respira →
láser (física) → electrodos (química) → mediciones → API → AIreGPT → cierre.

- Página: `/reelintro/` (three.js r128, usa `../models/smaa.glb` y `../images/logo_smability.png`).
- Parámetros: `?lang=es|en` · `?format=h|v` (16:9 o 9:16) · `?t=20` (empezar en el segundo 20) · `?autoplay=1` · `?render=1` (sin controles, para exportar).
- Teclas: espacio (pausa), L (idioma), F (pantalla completa), ← → (±2 s).
- Subtítulos: en la página cambian con el botón ES/EN; para video, `subtitulos_es.srt` y `subtitulos_en.srt`.
- Datos simulados: CDMX, jueves 3 de diciembre de 2026, 18:24 h (PM2.5 38 µg/m³, PM10 64, CO 1.6 ppm, O₃ 21 ppb, 13.6 °C, HR 47 %, 63 dB).
- Exportar a MP4: `python3 tools/reelintro_render.py http://localhost:8000/reelintro/index.html h es 30 salida.mp4`

## Versiones
- v1 (26 nov 2026): primera versión completa, sin música.
