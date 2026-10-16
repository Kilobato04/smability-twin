"""Arma models/smaa.glb a partir de:
  - SMAA-01TOP.stp y SMAA-01BOTTOM.stp, teselados con occt-import-js (read_step.js → *_geo.json). Ambos comparten coordenadas.
  - 8_Soporte_Panel_Solar_SMAA.stl, 9_Panel_Solar_SMAA_.stl, 10_Battery_Pack_SMAA.stl (AutoCAD; cada uno movido al octante positivo).

Marco del soporte (mm): x a lo largo, y del frente (y=0) hacia el tubo (placa vertical en y=113–115.7), z arriba (pestaña en z=0–2.8).
  - Caja: girada 180° sobre su eje vertical; la pestaña pasa por dentro del mango (hueco de 88 mm) y toca su techo (z=109.3).
  - Panel: su cara trasera asienta sobre la placa inclinada (37°) y su borde alto llega al tope del soporte.
  - Batería: su cara superior asienta bajo la placa inclinada; misma huella en x que la caja.
Salida: metros, Y arriba, origen en la cara inferior de la pestaña sobre el eje del tubo de CHAAK (r=21.5 mm), frente hacia −X.

Uso: python3 tools/smaa_build.py <carpeta_con_archivos> models/smaa.glb
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from stl2glb import load_stl, cluster, cylinder

N = np.array([0, -0.6018, 0.7986])      # normal de la placa inclinada (hacia arriba y al frente)
U = np.array([0, 0.7986, 0.6018])       # dirección a lo largo de la pendiente (hacia arriba)
TUBE_Y = 115.7 + 21.5                   # eje del tubo de CHAAK en el marco del soporte
XC = 137.0
BAT_DU = 3.0                            # mm que baja la batería por la pendiente respecto a los barrenos actuales de la placa                              # centro del soporte en x

def step_tris(path):
    g = json.load(open(path))[0]
    p = np.array(g["pos"]).reshape(-1, 3); f = np.array(g["idx"]).reshape(-1, 3)
    return p[f]

def main(src, out):
    parts = []
    # Carcasa girada 180° sobre su eje vertical (centro del mango: x=18, y=3) y colgada de la pestaña:
    # la pestaña cruza por dentro del mango y su cara superior toca el techo del mango (z=109.3).
    def place(t):
        t = t.copy(); t[..., 0] = 2*18 - t[..., 0]; t[..., 1] = 2*3 - t[..., 1]
        return t + np.array([119.0, 43.21, 2.8 - 109.3])   # barrenos del mango (x=-7/43) centrados en las ranuras de la pestaña (x=112/162, y=46.23)
    top = place(step_tris(f"{src}/top_geo.json"))
    bot = place(step_tris(f"{src}/bottom_geo.json"))
    sop = load_stl(f"{src}/8_soporte.stl")
    pan = load_stl(f"{src}/9_panel.stl")
    pan = pan + N * (40.82 - (-1.16)) + U * (172.2 - 224.5 - 19.98)   # cara trasera sobre la placa; barrenos Ø4 del panel sobre los Ø5.4 del soporte
    pan[:, :, 0] += 0.25
    bat = load_stl(f"{src}/10_bateria.stl")
    # Batería a la derecha (vista de frente al panel): sus 4 barrenos Ø3.2 (x 105/224.18, u 24.59/125.89)
    # concéntricos con los barrenos internos Ø3.5 de la placa (x 130.5/249.68, u 45.96/147.25).
    # BAT_DU: la batería baja 3 mm por la pendiente para librar la placa vertical (con 0 mm invadía 1.4 mm;
    # mínimo 1.7 mm; a partir de ~3.8 mm choca con la tuerca del tornillo inferior derecho del panel).
    # Los barrenos internos de la placa deben bajar lo mismo (u 42.96 / 144.25) o hacerse ranura.
    bat = bat + N * ((40.82 - 2.8) - 27.43) + U * (45.96 - 24.59 - BAT_DU)
    bat[:, :, 0] += 130.5 - 105.0
    # Tornillería (mm, marco del soporte).
    # Mango ↔ pestaña: 2 × M5, cabeza sobre la barra del mango, rondana y tuerca bajo la pestaña.
    tm = []
    for x in (112.0, 162.0):
        c = lambda z: [x, 46.23, z]
        tm += [cylinder(c(15.63), c(18.63), 4.25, 16), cylinder(c(15.63), c(-7.0), 2.5, 16),
               cylinder(c(-1.0), c(0.0), 5.0, 16), cylinder(c(-5.0), c(-1.0), 4.62, 6)]
    # Panel ↔ placa inclinada: 5 × M4, cabeza al frente del panel, rondana y tuerca bajo la placa.
    tp = []
    P = lambda x, u, d: np.array([x, 0, 0]) + U * u + N * d
    # El barreno central de arriba (x 137) queda bajo la oreja de la batería: no lleva tornillo.
    for x, u in ((6.65, 40.76), (267.35, 40.76), (7.65, 147.25), (266.35, 147.25)):
        tp += [cylinder(P(x, u, 44.02), P(x, u, 46.8), 3.5, 16), cylinder(P(x, u, 44.02), P(x, u, 32.0), 2.0, 12),
               cylinder(P(x, u, 37.0), P(x, u, 38.02), 4.5, 16), cylinder(P(x, u, 34.0), P(x, u, 37.0), 4.04, 6)]
    # Batería ↔ placa: 4 × M3 avellanados, a ras de la cara superior de la placa (el panel va encima); tuerca bajo la oreja.
    tb = []
    for x in (130.5, 249.68):
        for u in (45.96 - BAT_DU, 147.25 - BAT_DU):
            tb += [cylinder(P(x, u, 39.4), P(x, u, 40.82), 3.0, 16), cylinder(P(x, u, 40.82), P(x, u, 32.5), 1.5, 12),
                   cylinder(P(x, u, 35.5), P(x, u, 36.5), 3.5, 16), cylinder(P(x, u, 33.5), P(x, u, 35.5), 3.17, 6)]
    parts += [("tornillos_bateria_smaa", np.vstack(tb), [0.35, 0.37, 0.40, 1], 0.8, 0.35, 0)]
    parts += [("tornillos_mango_smaa", np.vstack(tm), [0.35, 0.37, 0.40, 1], 0.8, 0.35, 0),
              ("tornillos_panel_smaa", np.vstack(tp), [0.35, 0.37, 0.40, 1], 0.8, 0.35, 0)]
    parts += [("smaa_top", top, [0.90, 0.91, 0.90, 1], 0.0, 0.5, 0.4),
              ("smaa_bottom", bot, [0.95, 0.95, 0.94, 1], 0.0, 0.5, 0.4),
              ("soporte_panel_smaa", sop, [0.78, 0.80, 0.82, 1], 0.4, 0.4, 0),
              ("panel_solar_smaa", pan, [0.10, 0.16, 0.30, 1], 0.5, 0.25, 0),
              ("bateria_smaa", bat, [0.22, 0.24, 0.26, 1], 0.1, 0.6, 0)]
    mats, nodes, meshes, acc, views, blob = [], [], [], [], [], bytearray()
    def view(data, target):
        while len(blob) % 4: blob.append(0)
        off = len(blob); blob.extend(data); views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target}); return len(views) - 1
    for name, tris, color, metal, rough, cell in parts:
        v = tris.reshape(-1, 3)
        g = np.empty_like(v)
        g[:, 0] = v[:, 1] - TUBE_Y          # frente (y pequeño) → −X
        g[:, 1] = v[:, 2]                   # z → Y arriba
        g[:, 2] = v[:, 0] - XC              # a lo largo → Z
        pos, idx = cluster(g.reshape(-1, 3, 3), cell)
        pos = (pos * 0.001).astype(np.float32); ind = idx.astype(np.uint16 if len(pos) < 65536 else np.uint32)
        pv = view(pos.tobytes(), 34962); iv = view(ind.tobytes(), 34963)
        acc.append({"bufferView": pv, "componentType": 5126, "count": len(pos), "type": "VEC3", "min": pos.min(0).tolist(), "max": pos.max(0).tolist()})
        acc.append({"bufferView": iv, "componentType": 5123 if ind.dtype == np.uint16 else 5125, "count": int(ind.size), "type": "SCALAR"})
        mats.append({"name": name, "pbrMetallicRoughness": {"baseColorFactor": color, "metallicFactor": metal, "roughnessFactor": rough}, "doubleSided": True})
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(acc) - 2}, "indices": len(acc) - 1, "material": len(mats) - 1}]})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
        print(f"{name:22s} {ind.size//3:6d} triángulos  X {pos[:,0].min():+.3f}..{pos[:,0].max():+.3f}  Y {pos[:,1].min():+.3f}..{pos[:,1].max():+.3f}  Z {pos[:,2].min():+.3f}..{pos[:,2].max():+.3f}")
    while len(blob) % 4: blob.append(0)
    gl = {"asset": {"version": "2.0", "generator": "smability smaa_build"}, "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
          "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": acc, "bufferViews": views, "buffers": [{"byteLength": len(blob)}]}
    js = json.dumps(gl, separators=(",", ":")).encode(); js += b" " * ((4 - len(js) % 4) % 4)
    o = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    open(out, "wb").write(o); print(f"{out}: {len(o)/1e6:.2f} MB")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
