"""Agrega el interior de la carcasa SMAA a models/smaa.glb (después de tools/smaa_build.py).

Piezas (marco del gemelo en mm: X frente(−)/atrás, Y arriba, Z a lo largo de la caja; se guardan en metros):
  - Sensores_barriles_pcb.stl → smaa_in_tarjeta (tarjeta) + smaa_in_gases (2 barriles de gas en sus aros del piso)
  - Sensores_pm2.5.stl        → smaa_in_pm25: sobre el pretil del bolsillo, entre los postes, ventilador alineado con el túnel extractor
  - Sensores_temp_hum.stl     → smaa_in_temphum: cuerpo en la ventana hexagonal del piso, tarjeta apoyada en el clip
  - Sensores_GPS.stl          → smaa_in_gps: bajo el techo de la tapa, entre sus clips
  - Sin 3D (se modelan aquí):
      smaa_in_ruido     placa de ruido sobre 4 postes del piso + micrófono en el poste libre
      smaa_in_switches  ON/OFF y Móvil/Fijo en los 2 barrenos redondos del piso (propuesta)
      smaa_in_lipo      LiPo de bolsa ~8 × 50 × 40 mm (7.4 Wh) en la cavidad vertical de la pared frontal
      smaa_in_silica    bolsa de sílica gel en los clips de la pared Z−
  - Tapa: el poste entre los barriles se recorta 2.6 mm para que apoye sobre la tarjeta.

Es idempotente: si el .glb ya trae piezas smaa_in_*, las reemplaza.
Uso: python3 tools/smaa_interior.py <carpeta_con_los_4_STL> models/smaa.glb [salida.glb]
Los STL de sensores no necesitan estar en el repo (todo lo de models/ se publica).
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from stl2glb import load_stl, cylinder, cluster

def box(mn, mx):
    """Prisma cerrado con caras hacia afuera."""
    (x0, y0, z0), (x1, y1, z1) = mn, mx
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]], float)
    f = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5)]
    return v[np.array(f)]

# Rotación (filas: X, Y, Z del gemelo en función de x, y, z del STL) y traslación final, en mm.
STL = {
    "pcb": ("Sensores_barriles_pcb.stl", [[0,1,0],[0,0,1],[1,0,0]],  [-133.0,  -108.5, -75.78]),
    "pm":  ("Sensores_pm2.5.stl",        [[0,1,0],[0,0,1],[1,0,0]],  [-140.35, -103.4, -67.7]),
    "th":  ("Sensores_temp_hum.stl",     [[-1,0,0],[0,0,1],[0,1,0]], [-77.05,  -113.6, -29.7]),
    "gps": ("Sensores_GPS.stl",          [[0,1,0],[0,0,-1],[-1,0,0]], [-102.8,  -27.5, -23.5]),
}
BOARD_BOTTOM = -60.2           # cara inferior de la tarjeta (Y); abajo quedan los barriles

def interior(src):
    T = {k: load_stl(f"{src}/{f}") @ np.array(R, float).T + np.array(t) for k, (f, R, t) in STL.items()}
    pcb = T["pcb"]; top = pcb[:, :, 1].mean(1) >= BOARD_BOTTOM - 0.05
    # Placa de ruido: 4 postes (tope Y −98.5) + micrófono Ø6 en el poste libre (Z 2.5, X −124.3)
    bos = [(21.8, -70.75), (-15.0, -70.75), (-14.3, -124.3), (20.9, -124.3)]
    zs = [b[0] for b in bos]; xs = [b[1] for b in bos]
    ruido = [box([min(xs)-5, -98.5, min(zs)-5], [max(xs)+5, -96.9, max(zs)+5]),
             cylinder([-124.3, -98.5, 2.5], [-124.3, -103.5, 2.5], 3.0, 24)]
    ruido += [cylinder([x, -96.9, z], [x, -95.0, z], 2.75, 16) for z, x in bos]
    # Interruptores Ø18 (propuesta): bisel Ø21 por fuera, cuerpo Ø16 por dentro, actuador Ø6
    sw = []
    for z in (20.5, -21.25):
        sw += [cylinder([-51.7, -109.5, z], [-51.7, -111.5, z], 10.5, 32), cylinder([-51.7, -107.5, z], [-51.7, -87.5, z], 8.0, 32),
               cylinder([-51.7, -111.5, z], [-51.7, -117.5, z], 3.0, 16)]
    # LiPo en la pared frontal: hueco X −151.0..−141.3, Z 0..54.8, piso Y −99.6
    xc = (-151.0 - 141.3) / 2
    lipo = [box([xc-4, -99.5, 2.4], [xc+4, -61.5, 52.4]), box([xc-1.2, -61.5, 4.4], [xc+1.2, -60.0, 50.4]),
            box([xc-.2, -60.0, 20], [xc+.2, -59.0, 23]), box([xc-.2, -60.0, 31], [xc+.2, -59.0, 34])]
    # Sílica gel entre la pared Z− (−79.7) y las costillas (−73.4), sobre los pads del piso (Y −110)
    zc = (-79.7 - 73.4) / 2
    silica = [box([-98.5, -109.5, zc-2.0], [-66.5, -70.0, zc+2.0]), box([-99.5, -110.0, zc-.4], [-65.5, -69.0, zc+.4])]
    v = np.vstack
    return [  # nombre, triángulos (mm), color, metal, rugosidad
        ("smaa_in_tarjeta",  pcb[top],  [0.10, 0.42, 0.25, 1], 0.1, 0.55),
        ("smaa_in_gases",    pcb[~top], [0.62, 0.64, 0.67, 1], 0.6, 0.35),
        ("smaa_in_pm25",     T["pm"],   [0.22, 0.26, 0.34, 1], 0.1, 0.6),
        ("smaa_in_temphum",  T["th"],   [0.93, 0.93, 0.90, 1], 0.0, 0.6),
        ("smaa_in_gps",      T["gps"],  [0.12, 0.30, 0.45, 1], 0.1, 0.5),
        ("smaa_in_ruido",    v(ruido),  [0.16, 0.36, 0.24, 1], 0.2, 0.5),
        ("smaa_in_switches", v(sw),     [0.08, 0.08, 0.09, 1], 0.1, 0.5),
        ("smaa_in_lipo",     v(lipo),   [0.80, 0.82, 0.86, 1], 0.5, 0.35),
        ("smaa_in_silica",   v(silica), [0.95, 0.96, 0.97, 1], 0.0, 0.9),
    ]

def read_glb(path):
    b = open(path, "rb").read(); jl = struct.unpack("<I", b[12:16])[0]; g = json.loads(b[20:20+jl]); bo = 20 + jl + 8
    CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}
    def acc(i):
        a = g["accessors"][i]; vw = g["bufferViews"][a["bufferView"]]; n = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        arr = np.frombuffer(b, CT[a["componentType"]], a["count"]*n, bo + vw.get("byteOffset", 0) + a.get("byteOffset", 0))
        return arr.reshape(-1, n) if n > 1 else arr
    out = []
    for nd in g["nodes"]:
        pr = g["meshes"][nd["mesh"]]["primitives"][0]
        out.append((nd["name"], acc(pr["attributes"]["POSITION"]).astype(np.float64), acc(pr["indices"]).reshape(-1, 3).copy(), g["materials"][pr["material"]]))
    return out

def write_glb(path, items):
    mats, nodes, meshes, acc, views, blob = [], [], [], [], [], bytearray()
    def view(data, target):
        while len(blob) % 4: blob.append(0)
        off = len(blob); blob.extend(data); views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target}); return len(views) - 1
    for name, pos, idx, mat in items:
        pos = pos.astype(np.float32); ind = idx.astype(np.uint16 if len(pos) < 65536 else np.uint32)
        pv = view(pos.tobytes(), 34962); iv = view(ind.tobytes(), 34963)
        acc.append({"bufferView": pv, "componentType": 5126, "count": len(pos), "type": "VEC3", "min": pos.min(0).tolist(), "max": pos.max(0).tolist()})
        acc.append({"bufferView": iv, "componentType": 5123 if ind.dtype == np.uint16 else 5125, "count": int(ind.size), "type": "SCALAR"})
        mats.append(mat)
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(acc) - 2}, "indices": len(acc) - 1, "material": len(mats) - 1}]})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
    while len(blob) % 4: blob.append(0)
    gl = {"asset": {"version": "2.0", "generator": "smability smaa_build + smaa_interior"}, "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
          "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": acc, "bufferViews": views, "buffers": [{"byteLength": len(blob)}]}
    js = json.dumps(gl, separators=(",", ":")).encode(); js += b" " * ((4 - len(js) % 4) % 4)
    o = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    open(path, "wb").write(o); print(f"{path}: {len(o)/1e6:.2f} MB")

def main(src, glb, out=None):
    items = [it for it in read_glb(glb) if not it[0].startswith("smaa_in_")]
    for name, pos, idx, mat in items:
        if name == "smaa_top":   # poste entre los barriles (Z 68, X −89.7): recorte a la cara superior de la tarjeta (Y −58.4)
            p = pos * 1000
            m = (p[:, 2] > 63) & (p[:, 2] < 74) & (p[:, 0] > -95) & (p[:, 0] < -84) & (p[:, 1] < -58.4) & (p[:, 1] > -62)
            pos[m, 1] = -0.0584; print(f"smaa_top: poste recortado ({m.sum()} vértices)")
    for name, tris, color, metal, rough in interior(src):
        pos, idx = cluster(tris, 0)
        items.append((name, pos * 0.001, idx, {"name": name, "pbrMetallicRoughness": {"baseColorFactor": color, "metallicFactor": metal, "roughnessFactor": rough}, "doubleSided": True}))
        print(f"{name:18s} {len(idx):6d} triángulos")
    write_glb(out or glb, items)

if __name__ == "__main__":
    main(*sys.argv[1:4])
