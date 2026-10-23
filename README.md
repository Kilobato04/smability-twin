# Gemelo digital CHAAK · SMAA · Smability

Visor 3D de las estaciones CHAAK y SMAA montadas en un mismo trípode. Incluye:

- **Panel por sensor con datos en tiempo real.** Filtro CHAAK, SMAA o ambas; con ambas el panel compara las dos estaciones.
- **Vista explosionada y simulación de lluvia** según el viento de temporada de cada ciudad.
- **Guía de emplazamiento** para 15 ciudades o cualquier coordenada:
  - cara principal de espaldas al viento de lluvia;
  - sol por cara del equipo;
  - paneles al ecuador;
  - caseta de referencia con su sombra.
- **Modo campo.** La brújula del celular guía la orientación de la cara principal.
- **Ficha de instalación.** Plano y lista de verificación en PDF o PNG.
- **Tour automático** para presentaciones y ferias.

Sin build ni dependencias: HTML más three.js por CDN. Netlify sirve la carpeta tal cual, y una función hace de proxy al API.

## Estructura
```
twin.html                       fuente del visor (se edita aquí)
build.py                        genera index.html a partir de twin.html
index.html                      página publicada
favicon.svg
models/montaje.glb              trípode (pivot assy sin cabezal) y mástil de 1.25"
models/chaak.glb                equipo CHAAK (modelo real v1, 7 piezas)
tools/stl2glb.py                convierte los STL de AutoCAD en .glb
tools/chaak.json                piezas de CHAAK: nombre, corrección de posición y material
models/smaa.glb                 equipo SMAA real: carcasa, placa soporte, panel y batería
tools/smaa_build.py             arma smaa.glb desde los 2 STEP y los 3 STL de SMAA
netlify/functions/station.mjs   proxy al API (oculta la API key)
netlify.toml
```
Si un .glb no existe, el visor usa el modelo provisional, así que se puede publicar desde hoy.

## 1. Subir a GitHub
```bash
cd smability-twin
git init -b main
git add .
git commit -m "Gemelo digital CHAAK · SMAA"
gh repo create smability/smability-twin --private --source=. --push
```
Sin `gh`: crea el repo vacío en github.com y luego:
```bash
git remote add origin https://github.com/<organización>/smability-twin.git
git push -u origin main
```

## 2. Publicar en Netlify
1. Entra a app.netlify.com y sigue **Add new project → Import an existing project → GitHub**. Elige el repo.
2. Configuración de build:
   - Build command: vacío.
   - Publish directory: `.`
   - Functions directory: `netlify/functions`. Ya viene en `netlify.toml`.
3. **Deploy.** Netlify asigna una URL tipo `https://smability-twin.netlify.app`; el nombre se cambia en *Site configuration → Change site name*.
4. Agrega las variables en *Site configuration → Environment variables*:

   | Variable | Ejemplo |
   |---|---|
   | `STATION_API_URL` | `https://api.smability.io/v1/stations/{id}/latest` (con `{id}` o, si no, se agrega `?id=CHAAK`) |
   | `STATION_API_KEY` | tu llave |
   | `STATION_API_HEADER` | `x-api-key` (por defecto) o `Authorization` para Bearer |

   Después de guardarlas, ejecuta **Deploys → Trigger deploy**.
5. Dominio propio (opcional): *Domain management → Add a domain*, por ejemplo `gemelo.smability.io`, con un CNAME a la URL de Netlify.

Cada push a `main` publica solo, y cada rama o PR genera una URL de preview.

**No uses Netlify Drop (arrastrar la carpeta).** No publica la función del API, y el visor se quedaría en modo demo.

### Verificación después de publicar
- Arriba a la derecha debe decir **EN VIVO** (con variables configuradas) o **DEMO** (sin ellas, o si el API no responde).
- `https://<sitio>/.netlify/functions/station?id=CHAAK` debe regresar el JSON de la estación.
- **Vientos reales:** al elegir una ciudad, la nota de la guía cambia a "calculados con datos horarios 2025 (Open-Meteo)".
- **Modo campo:** abre el sitio en el celular, toca **Modo campo → Activar brújula** y acepta el permiso (iPhone lo pide).
- **Ficha de instalación:** debe descargar el PDF y el PNG.

### Probar en local
```bash
npm i -g netlify-cli
netlify dev          # http://localhost:8888, con la función del API
```

## 3. Modelos: AutoCAD → Blender → .glb
1. **AutoCAD:** exporta las piezas desde el **ensamble completo**, para que los tres archivos compartan el mismo origen.
   - Usa `FACETRES` 5–10 y luego `STLOUT` por pieza.
   - El nombre del archivo es la clave de la pieza: `pm`, `gas`, `escudo_thr`, `anemometro`, `veleta`, `pluviometro`, `panel_solar`, `gabinete`, `brazo`, `tripode`, `mastil`.
2. **Blender:** File → Import → STL (todas a la vez). Escala en metros: si AutoCAD está en mm, usa 0.001.
3. **Convención:**
   - Origen en la base del trípode y Z arriba (el export a glTF lo pasa a Y arriba).
   - **Brazos de sensores hacia +X y cara principal (gabinetes) hacia −X.**
   - Paneles solares como objeto aparte (`panel_solar`), planos. El visor los orienta e inclina según la latitud.
4. **Limpieza:** Decimate (0.1–0.3 en piezas curvas), Merge by distance, Shade Auto Smooth y materiales PBR simples.
5. **Tres exportaciones glTF 2.0 (.glb)**, seleccionando solo las piezas de cada archivo, con Draco activado y "Selected Objects":
   - `montaje.glb`: trípode y mástil.
   - `chaak.glb`: gabinete, brazos, sensores y panel de CHAAK.
   - `smaa.glb`: lo mismo para SMAA.
6. **Compresión extra (opcional):**
   `npx @gltf-transform/cli optimize chaak.glb models/chaak.glb --compress draco --texture-compress webp`
7. **Meta:** menos de 5 MB por archivo. Haz commit en `models/` y Netlify publica.

El visor asigna cada malla a su sensor buscando fragmentos del nombre (lista `KEYMAP` en `twin.html`).

### CHAAK real (v1)
Las 7 piezas exportadas de AutoCAD se convierten con:
```bash
python3 tools/stl2glb.py tools/chaak.json carpeta_con_stl models/chaak.glb
```
- Al exportar, AutoCAD movió cada pieza en Y por separado. `dy` en `tools/chaak.json` lo corrige.
- La cara principal (tapa de la carcasa) mira hacia +Y en AutoCAD; el script la lleva a −X.
- La base de CHAAK se monta sobre el mástil del trípode a `CHAAK_BASE_Y` (1.12 m, tope del mástil) en `twin.html`.
- Para agregar piezas nuevas (electrónica, tornillería), súmalas a `tools/chaak.json` con su `dy`.
- La tapa asienta a hueso sobre la base (hombro de 14.98 mm sobre el borde de 57.71 mm).
- El cable del sensor se recorta bajo z = 853 mm (`cut_below_z`).
- Los tornillos M3 se generan en los barrenos del tubo y de las abrazaderas (z = 623.8 y 713.8 mm). Pieza `tornillos_carcasa` con `screws`.
- Tornillos del sensor: 3 radiales M3 a 120° (30°, 150° y 270°) a z = 897.6 mm, del collar del sensor al cabezal roscado. Pieza `tornillos_sensor`.

### SMAA real
```bash
# 1) teselar los STEP con occt-import-js (genera top_geo.json y bottom_geo.json)
# 2) armar el .glb
python3 tools/smaa_build.py carpeta_smaa models/smaa.glb
```
- `SMAA-01TOP` y `SMAA-01BOTTOM` comparten coordenadas; los 3 STL (soporte, panel, batería) los movió AutoCAD por separado y el script los realinea:
  - Caja: girada 180° sobre su eje vertical, con la espalda hacia el tubo. La pestaña del soporte cruza por dentro del mango y queda bajo su barra superior.
  - Los 2 barrenos del mango (50 mm entre centros) quedan concéntricos con las 2 ranuras de la pestaña (x = 112 y 162 mm, y = 46.23 mm). Tornillería generada: 2 × M5 con rondana y tuerca bajo la pestaña (`tornillos_mango_smaa`).
  - Panel: sus barrenos Ø4 asientan sobre los 5 barrenos Ø5.4 de la placa inclinada; con eso el panel baja 20 mm respecto a la primera versión. Tornillería: 4 × M4 con rondana y tuerca bajo la placa (`tornillos_panel_smaa`); el barreno central de arriba queda bajo la oreja de la batería y no lleva tornillo.
  - Batería: del lado derecho (de frente al panel), alineada en x con los barrenos internos Ø3.5 de la placa (x = 130.5 y 249.68 mm; 101.3 mm entre filas). Baja 3 mm por la pendiente (`BAT_DU`) para no invadir la placa vertical: los barrenos internos de la placa deben bajar también 3 mm (u = 42.96 y 144.25 mm) o hacerse ranura. Margen útil: de 1.7 mm (toca) a ~3.8 mm (choca con la tuerca del tornillo inferior derecho del panel). 4 × M3 avellanados a ras de la placa, tuerca bajo la oreja (`tornillos_bateria_smaa`). La placa trae el mismo patrón del lado izquierdo (x = 24.32 y 143.5 mm).
  - Panel: cara trasera sobre la placa inclinada (37°).
- La placa vertical del soporte asienta en el tubo de CHAAK (cinchos) del lado de la cara principal. La carcasa de CHAAK va en la cara opuesta: las dos carcasas se dan la espalda.
- En `twin.html`, `SMAA_BASE_Y` (= `CHAAK_BASE_Y` + 0.335 m) es la altura de la pestaña. El panel gira con el montaje: es fijo a la carcasa.
- Mallas → claves: `tornillos_bateria` → screws_bat, `tornillos_mango` → screws_smaa, `tornillos_panel` → screws_panel, `soporte_panel` → arms, `smaa_top` → smaa_case, `smaa_bottom` → smaa_sens, `panel_solar` → solar, `bateria` → battery.
- Sensor: Hongyuv HY-WDS6E. Mide viento ultrasónico (velocidad y dirección), temperatura, humedad, presión y precipitación por radar (lluvia, granizo o nieve).
- **Los STL no van al repo:** todo lo que está aquí se publica en Netlify.

## Vistas de render
Realista, Rayos X, Técnica y Componentes (cada pieza se colorea por grupo y se puede aislar desde la leyenda). En `twin.html`: `PART_GROUPS` define los grupos y colores.

## 4. Datos del API
La función `mapApi()` en `twin.html` traduce el JSON de la estación a las variables del visor. Ajusta los nombres de campo a los reales; acepta rutas como `data.pm25`.

## 5. Ciudades, vientos y brújula
- **Ciudades:**
  - México: CDMX, Cancún, Durango, Guadalajara, La Paz BCS, Monterrey, Puebla, Tijuana, Tula (Hgo.).
  - Guatemala: Ciudad de Guatemala.
  - Colombia: Bogotá, Cali, Medellín, Suárez (Cauca).
  - Perú: Lima (hemisferio sur: paneles al norte).
- **Coordenadas libres:** en Ciudad → Coordenadas…
- **Vientos y lluvias:** ya publicado, el visor calcula viento dominante, viento con lluvia, meses de lluvia y temperatura media con datos horarios de Open-Meteo (`CLIMATE_YEAR`, por defecto 2025). Los guarda en el navegador. Sin conexión usa los valores provisionales de `CITIES`.
- **Declinación magnética:** cada ciudad trae un valor aproximado (±2°) para convertir el rumbo verdadero a magnético en el modo campo y en la ficha. Para un sitio nuevo, verifícala en la calculadora de NOAA (ngdc.noaa.gov/geomag/calculators/magcalc.shtml) y escríbela en el modo campo.

## 6. Editar
Edita `twin.html` y luego ejecuta `python3 build.py`, que regenera `index.html`. Después haz commit y push.

## Energía de SMAA y orientación del panel
- Equipo: Voltaic 10 W Axon. Panel P110 de 10 W / 6 V fijo a 37° mirando con la cara principal; batería V75 de 72 Wh (Li-Ion NMC, 5 V / 2 A, deja de cargar arriba de 45 °C).
- `fetchSolar()` baja la irradiancia horaria directa y difusa del año base (Open-Meteo) y calcula, por mes y por rumbo del panel (cada 5°), la energía diaria sobre el panel. Se guarda en `localStorage` (`smab.pv1.*`). Sin conexión, `estimateSolar()` usa cielo despejado con nubosidad típica.
- Energía que entra = 10 W × horas de sol pico sobre el panel × 0.70 (temperatura, suciedad y conversión a 5 V). Consumo supuesto (falta medirlo): bajo 0.40 W, típico 0.85 W, alto 1.15 W.
- Regla (`energyPlan()`): la cara principal va de espaldas a la lluvia. Si en el peor mes el panel no da al menos 1.25× el consumo, se gira lo mínimo dentro de ±60° hasta lograrlo; si no se logra, al rumbo que más ayude. No se gira por ganancias menores al 5%. Con solo CHAAK no se gira.
- En la guía: tarjeta "Energía SMAA" con consumo, orientación (recomendada o de espaldas a la lluvia) y barras mensuales. La ficha imprime el panel y la autonomía de la batería.

## Cortes
- Dos planos que giran con el montaje (botones "Corte" junto a las vistas; en móvil, en Explorar):
  - **Longitudinal:** contiene el eje del tubo y la dirección frente–trasera. En 0 mm corta las 17 piezas de CHAAK y SMAA (sensor, cabezal, coples, tubo, carcasas, soporte, panel, batería y tornillería).
  - **Transversal:** contiene el eje del tubo, de lado a lado. En 0 mm corta el sensor, el tubo y los coples de CHAAK; con el deslizador a unos −95 mm corta la carcasa de SMAA.
- El deslizador mueve el plano (mm). Siempre se oculta la mitad del lado de la cámara, así que al girar se sigue viendo el interior.
- Las caras cortadas se rellenan con el color del grupo de la pieza (sensores, carcasa, soporte, tornillería, energía). `fixWinding()` corrige la orientación de las caras de cada malla para que el relleno salga bien. La caseta de referencia no se corta.

## Montaje en cascada (frente 1, 19 oct)
- Tubo de CHAAK de 0.65 m con 3 barrenos a 90 mm (`tools/chaak.json`: `dz` y `stretch` por pieza; marcador `tubo_soporte_barreno3`).
- Grupos en el visor: `fixedG` (trípode, tubo y sensor; la «N» del sensor al norte verdadero), `caseG` (carcasa de CHAAK: gira a su tapa y baja 9 cm al apilar), `smaaG` (SMAA: gira a su cara principal y sube 16.5 cm al apilar).
- `mountPlan(city, EP)` recorre: 1) tapa al lado fresco + mismo nivel, 2) tapa al lado fresco + apilado, 3) tapa invertida + mismo nivel, 4) tapa invertida + apilado. Toma la primera con energía ≥ 1.25× y el menor giro. Separación mínima 150° al mismo nivel (3 cm de holgura), 105° apiladas (25 cm libres bajo las tomas de SMAA, cilindro verde).
- Datos de producto: consumo típico de SMAA 0.6 W, baterías de 72 Wh + 7.4 Wh, 2 gases intercambiables (selector en el panel del módulo de sensores, se guarda en `smab.gases`), CHAAK con radiación, brújula interna, toma eléctrica 5 V / 3 A y calibración remota por SMS.
- Modo campo en 3 pasos (Norte CHAAK, Tapa CHAAK, Cara SMAA), lista «Antes de instalar», interruptor de instalador con experiencia y seguimiento de conexión (Configurado → Conectando → Recibiendo datos).
- QR: `?id=<id del equipo>` (o `?chaak=<id>&smaa=<id>`), opcional `&city=cdmx`, abre el modo campo con ese equipo.
- Ficha: nombre del sitio, instalador, altura, distancia a vialidad y hasta 4 fotos (también en el PDF). «Enviar a Smability» arma el resumen para WhatsApp o correo; el contacto va en `CONTACT`.
- Fichas técnicas en PDF: coloca `docs/ficha-smaa.pdf`, `docs/ficha-chaak.pdf` y `docs/ficha-smaa-chaak.pdf`; los botones «Fichas técnicas» aparecen solos junto a las redes (y en la ficha de instalación) cuando existen.
- Orificio del tubo: el STL trae un barreno pasado de Ø21 mm justo arriba de la carcasa (z 786–807 mm), por donde salen los cables del sensor hacia la carcasa. El alargamiento corta en z 809.5 para no deformarlo. El tubo (`fixedG`) gira 90° para que sus barrenos y este orificio queden en el eje N–S, igual que la carcasa con la tapa al norte o al sur.
- Sin temperatura interna: los equipos no la miden. Los paneles de gabinete muestran la señal celular (pastilla de señal buena, débil o insuficiente).
- Altura de SMAA a criterio del instalador (`state.smaaH`, se guarda en `smab.smaaH`): «Arriba», justo bajo el cople superior (tomas a 1.54 m), o «Mismo nivel» que CHAAK (tomas a 1.37 m). Con CHAAK baja (barrenos 2 y 3) SMAA va arriba por obligación. Nombres en pantalla: «CHAAK alta» (barrenos 1 y 2) y «CHAAK baja» (barrenos 2 y 3).

- Barra inferior: redes sociales y botones de fichas a la izquierda; en escritorio se dejan 200 px libres a la derecha para el aviso flotante de Netlify.
- Trípode y mástil son de referencia: no se venden (CHAAK y SMAA se entregan con su tubo).

## Reel · `/reel` (v0.1, primer montaje)

`reel/index.html` es el reel de 78 s "Del sensor a tu mano", en HTML. Corre como video, sin música por ahora.

- **Formatos:** 16:9 y 9:16. Se elige con `?format=h|v`; sin parámetro se toma según la orientación de la pantalla. También hay un botón para cambiarlo.
- **Subtítulos:** español o inglés, con `?lang=es|en` o con el botón.
- **Personalización:** `?city=gdl` (mismas claves que el gemelo) o `?lat=..&lon=..&name=..`. Los mapas de las escenas 1 y 4 vuelan a esa zona, y el cierre dice "Mira cómo quedaría en {ciudad}".
- **Otros parámetros:** `?t=30` abre en el segundo 30; `?autoplay=1` arranca solo; `?capture=1` oculta los controles para exportar.
- **Mapas:** Mapbox GL JS v3 (`CONFIG.mapboxToken`). Restringe el token al dominio de Netlify en el dashboard de Mapbox. Si Mapbox no carga, se dibuja una retícula de respaldo.
- **3D:** el gemelo se carga en un iframe con `/?embed=reel`. Ese modo oculta la interfaz y expone `window.TWIN` (orbit, tint, explode, clean, rig, floor, zone, align, snap, render, rain, hour) para que el reel dirija la cámara cuadro a cuadro.
- **Exportar a MP4:** `render(t)` es determinista; `window.REEL.seek(t)` permite capturar cuadro a cuadro con Playwright y armar el MP4 con ffmpeg.
- **Chat de AIreGPT (escena 6):** es la simulación del landing de airegpt.ai, sin montos de multas.
- **Datos:** la red de nodos y los campos de calidad del aire y lluvia de la escena 4 son una simulación ilustrativa (lo dice en pantalla). Están listos para cambiarse por las APIs en vivo.

Archivo único: `reel/index.html`. No usa imágenes PNG/JPEG: el logo, la tarjeta SMAA OS, los íconos, las redes y los QR (gemelo y bot) están dibujados en SVG/HTML dentro de la página.
- Escena 3: órbita cercana alrededor de la estación con SMAA y CHAAK al mismo nivel (`TWIN.align()`); arranca en rayos X y cambia a sólido con un barrido de capas (`TWIN.snap()`).
- En CDMX los mapas se centran en Paseo de la Reforma 510 (Torre BBVA).
- Red real (`NET` en `reel/index.html`): 62 nodos (en pantalla «60+») — Valle de México 36 (2 CHAAK), Ciudad de Guatemala 18 (3 + 15 EPIC), Monterrey 2, Guadalajara 2 (1 CHAAK), Durango 1, Cancún 1, Medellín 2 (1 CHAAK). Ubicaciones aproximadas dentro de cada zona metropolitana; la escena 4 usa los 36 nodos del Valle de México y la escena 7 muestra la cobertura por ciudad.
- Escena 3: aire "respirado" por SMAA (partículas hacia la toma, `TWIN.inlet()`), lluvia intensa y dos rayos (estilo airegpt.ai). Escena 8: se muestra el mástil para que la estación no flote; redes, gemelo y QR son ligas clicables al final.

### v0.5
- Narrativa aire + lluvia al mismo nivel: tormenta sobre la ciudad en la escena 1, CHAAK «lluvia y tormentas», «tormenta detectada» en el modelo de lluvia.
- Escena 3: aire que entra a las cavidades de SMAA (`TWIN.sinlet()`), salpicaduras de lluvia sobre los equipos (`TWIN.surfaces()` + `TWIN.project()`).
- Cierre con la orientación de Guadalajara (`TWIN.city("gdl","arriba")`), arreglo completo SMAA-CHAAK; con `?city=` usa la orientación de esa ciudad.
- Precarga de mosaicos de Mapbox de todas las tomas antes de reproducir (el botón muestra «Cargando mapas n/9»).

### v0.6
- Escena 1 sin lluvia ni rayo; escena 3 sin rayos (solo lluvia con salpicaduras).
- Escena 3 en tres capas con barrido: rayos X → componentes en color (como las fichas) → sólido con SMAA/CHAAK en azul, justo antes de la lluvia.
- Modo embebido del gemelo con resolución reducida (más fluido en celulares).

### v0.7
- Escena 3: callouts numerados sobre el modelo en color (1 sensor meteorológico CHAAK, 2 tubo de ensamble, 3 panel solar, 4 dispositivo CHAAK, 5 dispositivo SMAA) con `TWIN.centers()`; la cámara se detiene en un ángulo donde se ven todos.
- Cierre más cerrado sobre SMAA-CHAAK con paneo vertical; QR sin URL (son clicables).
- Celulares: resolución de Mapbox y del gemelo ajustada al tamaño real en pantalla (`pixelRatio`, `?pr=`), sin terreno 3D ni antialias en móvil, caché de mosaicos acotada.

### v0.8 (memoria y carga de mapas)
- El gemelo deja de dibujar cuando no está en pantalla (`TWIN.pause()`); en celular se carga después de los mapas.
- Ciudad → continente con corte (fundido) en lugar de vuelo continuo: evita cientos de mosaicos intermedios.
- Mapbox en Mercator, sin terreno ni edificios 3D en celular, caché de mosaicos acotada (60 en celular, 400 en escritorio), precarga de 3 tomas en celular y 8 en escritorio.
- En celular: sin captura de pantalla para el barrido de capas, menos partículas y mapas de calor a menor resolución.

### v0.9
- Escritorio: mapa tipo globo (Mapbox GL, proyección globe) con vuelo ciudad → continente; precarga de 10 tomas.
- Celular (o `?lite=1` / `?static`): sin Mapbox GL. Cada escena de mapa usa una imagen estática (Mapbox Static Images, vista plana; la primera es el Valle de México) y las capas se dibujan encima. Sin rayos X en el 3D (sus aristas consumen mucha memoria): color → sólido.

### Gemelo · acceso al reel
- Ícono de video en la barra de redes del gemelo (junto a LinkedIn): abre `/reel/` en otra pestaña con la ciudad elegida en el gemelo (`?city=`).

### v1.0 · música
- `reel/audio/musica.mp3` (77 s): "Tech House" de Jonas Blakewood (Pixabay, licencia Pixabay: uso comercial dentro del video, sin atribución obligatoria). Pista original de 41.5 s extendida en el compás de cierre del drop: intro · drop · intro · drop · cierre, para que la energía siga al guion (tormenta y SMAA OS en el primer drop; autocalibración en la intro; chat, ciclo y cobertura en el segundo drop; cierre en el final natural). Normalizada a −16 LUFS.
- Sincronizada con la línea de tiempo (play, pausa, adelantar); botón ♪ para silenciar; `?mute=1` la arranca en silencio.

### v1.1 · escena 1 más ligera
- La ciudad se ve en una "lente" circular: el lienzo de Mapbox se reduce al círculo (≈940 px) mientras dura la escena 1 y se abre a pantalla completa al empezar el vuelo al continente.
- Inclinación menor (54°→48°), niebla con `range` para no pedir mosaicos del horizonte y sin relieve (terrain) en todo el reel.

### Energía SMAA (20 oct, medido)
- Consumo nominal medido: **0.745 W** con muestreo cada minuto (17.9 Wh/día) → escenario «Típico». «Bajo» 0.47 W y «Alto» 0.95 W quedan como estimados. Reparto por componente escalado al nominal (estimado).
- Regla del panel sin cambio: peor mes ≥ 1.25× el consumo (los días nublados seguidos son el reto). Entre 1.0× y 1.25× el gemelo marca «Margen justo» y la autonomía sin sol (3.8 días).
- Batería interna sola: ~10 h.

## Reel v1.2 · Voz en inglés (20 oct)
- `reel/audio/mezcla-en.mp3` (77.1 s): voz ElevenLabs "Hope" + música, con la música bajada ~11 dB mientras habla la voz. Cada frase de la locución (56 s) se colocó en el tiempo de su escena.
- En inglés (`?lang=en` o botón EN) suena la mezcla; en español sigue solo la música (`musica.mp3`) hasta tener la voz en español.
- Subtítulos retemporizados para coincidir con la voz (aplica a ambos idiomas).

## Reel v1.3 · Nueva estructura (22 oct)
- Orden según el guion v4: Problema → Dispositivos → **Calibración (02)** → **SMAA OS / modelos (03)** → **AIreGPT (04)** → Red → Cierre. Las escenas se reordenaron con `SH4 = +10 s` (SMAA OS) y `SH5 = −11.4 s` (calibración).
- Dispositivos: sello "+ RUIDO · casi ninguna red lo mide en la región".
- Calibración: O₃ con R² 0.72 → 0.91 "validado una vez contra referencia ICAyCC-UNAM"; esquema O₃ · PM2.5; "Mínimo mantenimiento en campo" (ya no "hasta 24 meses sin visitas").
- SMAA OS: "Nuestro sistema operativo".
- AIreGPT: configuración en lenguaje natural (casa y trabajo) y alerta masiva: una celda del modelo se activa y la alerta llega a todos los usuarios dentro de ella.
- Anillo en el nuevo orden; cobertura: Valle de México 36 (1 CHAAK), Monterrey 4, Durango 2, Guadalajara 2, Cancún 1, Guatemala 18 (15 EPIC en instalación), Medellín 2 (1 CHAAK); leyenda aire · clima · agua · calor; cifras 9 años · 60+ nodos vendidos · 3 países · 1 patente en trámite.
- Subtítulos ES/EN del guion v4. Audio: solo música en ambos idiomas; `audio/mezcla-en.mp3` (guion anterior) ya no se usa.

## Reel v1.4 (22 oct)
- AIreGPT: después de la alerta de lluvia por celda llega una **contingencia ambiental en toda la ciudad** (onda naranja sobre la retícula, todos los usuarios la reciben); el chat suma la tarjeta de contingencia y la notificación cambia a "CONTINGENCIA FASE I".
- Cifras finales sin encimarse (leyenda de cobertura más arriba y separación entre número y etiqueta).
- Gemelo (`twin.html`): las salpicaduras de lluvia ahora siguen la geometría del equipo mientras gira (puntos guardados en coordenadas locales y matrices de cámara actualizadas antes de proyectar).

## Reel v1.5 (22 oct)
- Alerta masiva: íconos vectoriales (casa, trabajo y triángulo de contingencia) en lugar de emojis.
- 9:16: lista de dispositivos en un panel compacto que no choca con la estación; cajas de calibración lado a lado; teléfono de AIreGPT más arriba.
- Sello de ruido ajustado a su texto.
- Badge "Powered by Netlify" oculto en el reel y en el gemelo (CSS + observador que lo esconde si Netlify lo inyecta).

## Música v2 (22 oct)
- `reel/audio/musica.mp3` ahora es "Technology Music Promo" (Maksym Malko, Pixabay), recortada a 77.6 s sin empalmes: build 0–13 s, drop a los 13.5 s (entra el gemelo), pausa 40–52 s, segundo drop a los 64.5 s (mapa de cobertura) y desvanecido final 75.4–77.6 s. Normalizada a −16 LUFS.

## Voz en inglés v4 (22 oct)
- `reel/audio/mezcla-en.mp3` (77.6 s): voz ElevenLabs "Hope" del guion v4 + la pista nueva, con la música ~11 dB abajo mientras habla. Cada frase se colocó en su escena (la grabación de 58 s se extendió a la duración del reel sin acelerar ni estirar la voz). Subtítulos retemporizados a la voz.
- Reparto final (según la transcripción): Problema 0:00–0:14 · Dispositivos 0:14–0:23 · Calibración 0:25–0:33 · Modelos 0:35–0:43 · AIreGPT 0:46–0:57 (lluvia por celda y contingencia) · Red 0:58–1:06 · Cierre "Smability… See how it would look on your street!" 1:10–1:14.
