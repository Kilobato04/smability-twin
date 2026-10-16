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
  - Caja: los 2 barrenos del tope (48.6 mm entre centros) caen en las 2 ranuras de la pestaña del soporte.
  - Panel: cara trasera sobre la placa inclinada (37°), borde alto al tope del soporte.
  - Batería: bajo la placa inclinada, misma huella que la caja.
- La placa vertical del soporte asienta en el tubo de CHAAK (cinchos) del lado de la cara principal; la carcasa de CHAAK queda del lado opuesto.
- En `twin.html`, `SMAA_BASE_Y` (= `CHAAK_BASE_Y` + 0.335 m) es la altura de la pestaña. El panel gira con el montaje: es fijo a la carcasa.
- Mallas → claves: `soporte_panel` → arms, `smaa_top` → smaa_case, `smaa_bottom` → smaa_sens, `panel_solar` → solar, `bateria` → battery.
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
