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
- Fichas técnicas en PDF: coloca `docs/ficha-smaa.pdf`, `docs/ficha-chaak.pdf` y `docs/ficha-smability.pdf`; los botones aparecen solos cuando existen.
- Orificio del tubo: el STL trae un barreno pasado de Ø21 mm justo arriba de la carcasa (z 786–807 mm), por donde salen los cables del sensor hacia la carcasa. El alargamiento corta en z 809.5 para no deformarlo. El tubo (`fixedG`) gira 90° para que sus barrenos y este orificio queden en el eje N–S, igual que la carcasa con la tapa al norte o al sur.
- Sin temperatura interna: los equipos no la miden. Los paneles de gabinete muestran la señal celular (pastilla de señal buena, débil o insuficiente).
- Altura de SMAA a criterio del instalador (`state.smaaH`, se guarda en `smab.smaaH`): «Arriba», justo bajo el cople superior (tomas a 1.54 m), o «Mismo nivel» que CHAAK (tomas a 1.37 m). Con CHAAK baja (barrenos 2 y 3) SMAA va arriba por obligación. Nombres en pantalla: «CHAAK alta» (barrenos 1 y 2) y «CHAAK baja» (barrenos 2 y 3).
