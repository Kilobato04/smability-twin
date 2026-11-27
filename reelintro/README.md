# Reel intro · «De la física y la química… a tu mano»

Apertura de 60 s para el keynote, en una sola toma: sintonía de TV → logo → calle chica de noche → el combo CHAAK + SMAA en un
poste de banqueta → la onda toca a CHAAK y empieza a llover (gotas que rebotan en CHAAK y en el panel de SMAA) → SMAA despierta
y respira → láser (física) → electrodos (química) → mediciones → API → AIreGPT → cierre.

- Página: `/reelintro/` (three.js r128; usa `../models/smaa.glb`, `../models/chaak.glb` y `../images/logo_smability.png`).
- Versión Mapbox: `/reelintro/?map=reforma` — el combo en su trípode, en la azotea del antiguo edificio de la Secretaría de Salud
  (Reforma y Lieja · 19.422432, −99.175614), con los edificios reales alrededor; usa el token del reel (`/reel`).
  Altura de la azotea: `CONFIG.reforma.roofH` (19 m, estimada). Si Mapbox no carga, cae solo a la ciudad estilizada.
- Parámetros: `?lang=es|en` · `?format=h|v` (16:9 o 9:16) · `?t=20` · `?autoplay=1` · `?render=1` (sin controles, para exportar).
- Teclas: espacio (pausa), L (idioma), F (pantalla completa), ← → (±2 s). Los controles se esconden solos mientras corre el reel.
- Subtítulos: botón ES/EN en la página; para video, `subtitulos_es.srt` y `subtitulos_en.srt`.
- Datos simulados, sin ciudad ni hora en el texto.
- Exportar a MP4: `python3 tools/reelintro_render.py http://localhost:8000/reelintro/index.html h es 30 salida.mp4`
  (para la versión Mapbox agrega `&map=reforma` a mano en el script; necesita conexión a Mapbox).

## Versiones
- v1 (26 nov 2026): primera versión completa, sin música.
- v2 (26 nov 2026): frases de entrada nuevas («La naturaleza habla en ondas…», «El aire no se ve…»); textos sin ciudad ni hora;
  calle chica con banquetas y árboles; combo CHAAK + SMAA en poste de banqueta; lluvia con rebote en CHAAK y en el panel;
  controles que se esconden; versión `?map=reforma` con Mapbox. Duración 60 s.
- v3 (26 nov 2026): Mapbox en la azotea (trípode, altura del edificio, llegada desde Chapultepec y paneo de la ciudad alrededor
  del combo); transición sólido → translúcido más suave y escalonada (primero CHAAK, panel y poste; luego la carcasa de SMAA).
- v4 (26 nov 2026): azotea 2 m más abajo (`roofH` 17 m); la lluvia empieza en el acercamiento a CHAAK y la lejana entra después.
