# Reel intro · «De la física y la química… a tu mano»

Apertura de 78 s para el keynote, en una sola toma:
sintonía de TV → logo → limbo azul profundo: la onda «enciende» el combo CHAAK + SMAA en su trípode → SMAA despierta →
la carcasa se vuelve translúcida y las piezas se arman una por una mientras la cámara gira → láser (física) → espiral de gas a
los barriles (química) → tarjeta → vista explotada y «clic» de cierre → cifras del producto → API → la toma se abre con lluvia
y lecturas → los datos suben a AIreGPT → cierre.

- Página: `/reelintro/` (three.js r128; usa `../models/smaa.glb`, `../models/chaak.glb`, `../models/montaje.glb` y `../images/logo_smability.png`).
- Por defecto: limbo, sin mapa ni edificios.
- Versión Mapbox: `/reelintro/?map=1` — al abrirse la toma (53–62 s) aparece Mapbox con el combo en la azotea de la oficina
  (casa de 2 pisos, 6 m; 19.414878, −99.167249). Altura y rumbo en `CONFIG.site` (`roofH`, `bearing`). Si Mapbox no carga, sigue en limbo.
- Parámetros: `?lang=es|en` · `?format=h|v` (16:9 o 9:16) · `?t=20` · `?autoplay=1` · `?render=1` (sin controles, para exportar).
- Teclas: espacio (pausa), L (idioma), M (música), F (pantalla completa), ← → (±2 s). Los controles se esconden solos mientras corre el reel.
- Subtítulos: botón ES/EN en la página; para video, `subtitulos_es.srt` y `subtitulos_en.srt`.
- Datos simulados, sin ciudad ni hora en el texto.
- Música: `audio/musica.mp3` — «Neon Drive» de Artur Aravidi (Pixabay, licencia de contenido de Pixabay), editada a 78 s sobre el ritmo
  (100 BPM): intro 0–8 s, entra el ritmo con la onda, pausa ambiental dentro de SMAA (≈26–47 s), vuelve al cerrar la vista
  explosionada (≈48.6 s) y termina con el logo. Botón ♪ para silenciar; `?mute=1` la apaga.
- Exportar a MP4 (con música): `python3 tools/reelintro_render.py http://localhost:8000/reelintro/index.html h es 30 salida.mp4 reelintro/audio/musica.mp3`

## Versiones
- v1 (26 nov): primera versión completa, sin música.
- v2 (26 nov): frases de entrada nuevas; textos sin ciudad ni hora; CHAAK y lluvia con rebote; controles que se esconden; versión Mapbox.
- v3–v4 (26 nov): Mapbox en azotea; transición sólido → translúcido suave y escalonada; lluvia sin «basurita».
- v5 (27 nov): sin ciudad al inicio (limbo azul profundo y combo en trípode); interior a ~40 cm con foco y etiquetas por pieza;
  espiral de gas hacia los barriles; la ciudad aparece al final (revelación lenta de 8 s) con la lluvia; Mapbox en la azotea de la
  oficina; duración 64 s.
- v6 (27 nov): logo con la onda cortada al borde del cuadro, SMABILITY al pie y ©; por defecto en limbo (sin ciudad simulada);
  Mapbox solo con `?map=1`; armado pieza por pieza con lista de componentes y giro de cámara; vista explotada; cifras
  «12 variables · 2 equipos · 1 min» y lecturas PM2.5 38 µg/m³ · ozono 21 ppb · lluvia 4.2 mm/h; duración 75 s.
- v7 (27 nov): panel solar y su batería en la lista de componentes (se resaltan antes del interior); CHAAK con su cabezal de estado
  sólido y 3 variables críticas (viento, lluvia, radiación solar); lluvia desde el acercamiento al combo, más tenue dentro de SMAA,
  y se retira por completo al alejarse hacia el cierre.
- v8 (27 nov): logo igual al oficial (cuadro con la onda y «smability» en Arial Bold a la derecha, con ©); la lluvia se retira
  entre 50 y 53 s y las tomas siguientes (API, ciudad, AIreGPT, cierre) van sin lluvia.
- v9 (27 nov): nueva conversación de AIreGPT con el estilo de airegpt.ai (Telegram): pregunta del usuario, tarjeta «Aire ahora · casa»
  (IAS regular 62, PM2.5 38 µg/m³, ozono 21 ppb, clima), notificación «Regresa la lluvia · trabajo» y alerta de lluvia; el teléfono
  dura ~11 s; duración 78 s.
- v10 (27 nov): música de fondo («Neon Drive», editada al ritmo del reel), botón ♪ y exportación con audio.
