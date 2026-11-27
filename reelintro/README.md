# Reel intro · «De la física y la química… a tu mano»

Apertura de 64 s para el keynote, en una sola toma:
sintonía de TV → logo → limbo azul profundo: la onda «enciende» el combo CHAAK + SMAA en su trípode → giro alrededor del combo,
SMAA despierta → interior a distancia media con foco por pieza: láser (física), espiral de gas a los barriles (química) →
mediciones → API → la toma se abre: el piso del estudio se vuelve una azotea, la ciudad se enciende y llueve → los datos suben a
AIreGPT → cierre.

- Página: `/reelintro/` (three.js r128; usa `../models/smaa.glb`, `../models/chaak.glb`, `../models/montaje.glb` y `../images/logo_smability.png`).
- Versión Mapbox: `/reelintro/?map=1` — la ciudad del final es Mapbox: el combo en la azotea de la oficina (casa de 2 pisos,
  6 m; 19.414878, −99.167249). Altura y rumbo en `CONFIG.site`. Si Mapbox no carga, se usa la ciudad simulada.
- Parámetros: `?lang=es|en` · `?format=h|v` (16:9 o 9:16) · `?t=20` · `?autoplay=1` · `?render=1` (sin controles, para exportar).
- Teclas: espacio (pausa), L (idioma), F (pantalla completa), ← → (±2 s). Los controles se esconden solos mientras corre el reel.
- Subtítulos: botón ES/EN en la página; para video, `subtitulos_es.srt` y `subtitulos_en.srt`.
- Datos simulados, sin ciudad ni hora en el texto.
- Exportar a MP4: `python3 tools/reelintro_render.py http://localhost:8000/reelintro/index.html h es 30 salida.mp4`

## Versiones
- v1 (26 nov): primera versión completa, sin música.
- v2 (26 nov): frases de entrada nuevas; textos sin ciudad ni hora; CHAAK y lluvia con rebote; controles que se esconden; versión Mapbox.
- v3–v4 (26 nov): Mapbox en azotea; transición sólido → translúcido suave y escalonada; lluvia sin «basurita».
- v5 (27 nov): sin ciudad al inicio (limbo azul profundo y combo en trípode); interior a ~40 cm con foco y etiquetas por pieza;
  espiral de gas hacia los barriles; la ciudad aparece al final (revelación lenta de 8 s) con la lluvia; Mapbox en la azotea de la
  oficina; duración 64 s.
