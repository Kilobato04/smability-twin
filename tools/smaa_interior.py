"""Agrega el interior de la carcasa SMAA a models/smaa.glb (después de tools/smaa_build.py).

Piezas (marco del gemelo en mm: X frente(−)/atrás, Y arriba, Z a lo largo de la caja; se guardan en metros):
  - Sensores_barriles_pcb.stl → smaa_in_tarjeta (tarjeta) + smaa_in_gases (2 barriles de gas en sus aros del piso)
  - Sensores_pm2.5.stl        → smaa_in_pm25: sobre el pretil del bolsillo, entre los postes, ventilador alineado con el túnel extractor
  - Sensores_temp_hum.stl     → smaa_in_temphum: cuerpo en la ventana hexagonal del piso, tarjeta apoyada en el clip
  - Sensores_GPS.stl          → smaa_in_gps: bajo el techo de la tapa, entre sus clips
  - Sin 3D (se modelan aquí):
      smaa_in_ruido     placa de ruido sobre 4 postes del piso + micrófono en el poste libre
      smaa_in_switches  ON/OFF y Móvil/Fijo: botones con anillo LED del diámetro de los barrenos del piso (Ø18), a hueso
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


def hole_outline(tris, y, center, rmax=12.0):
    """Contorno (X, Z) del barreno de la base que rodea `center`, cortando la malla en el plano Y = y."""
    segs = []
    for t in tris:
        d = t[:, 1] - y; pts = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]
            if (d[i] > 0) != (d[(i + 1) % 3] > 0):
                u = d[i] / (d[i] - d[(i + 1) % 3]); pts.append(a + u * (b - a))
        if len(pts) == 2:
            p, q = (np.array([pts[0][0], pts[0][2]]), np.array([pts[1][0], pts[1][2]]))
            if max(np.hypot(*(p - center)), np.hypot(*(q - center))) < rmax: segs.append((p, q))
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    nxt = {}
    for p, q in segs: nxt.setdefault(key(p), []).append(q); nxt.setdefault(key(q), []).append(p)
    start = segs[0][0]; loop = [start]; prev = None; cur = start
    while True:
        cands = [q for q in nxt[key(cur)] if prev is None or key(q) != key(prev)]
        prev, cur = cur, cands[0]
        if key(cur) == key(start) or len(loop) > 5000: break
        loop.append(cur)
    return np.array(loop)

def prism(poly, y0, y1):
    """Extrusión cerrada de un polígono (X, Z) en forma de estrella respecto a su centro, entre Y = y0 y y1."""
    c = poly.mean(0); n = len(poly); T = []
    P = lambda p, y: [p[0], y, p[1]]
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        T += [[P(c, y0), P(a, y0), P(b, y0)], [P(c, y1), P(b, y1), P(a, y1)], [P(a, y0), P(a, y1), P(b, y1)], [P(a, y0), P(b, y1), P(b, y0)]]
    return np.array(T, float)

# Rotación (filas: X, Y, Z del gemelo en función de x, y, z del STL) y traslación final, en mm.
STL = {
    "pcb": ("Sensores_barriles_pcb.stl", [[0,1,0],[0,0,1],[1,0,0]],  [-133.0,  -108.5, -75.78]),
    "pm":  ("Sensores_pm2.5.stl",        [[0,1,0],[0,0,1],[1,0,0]],  [-140.35, -103.4, -67.7]),
    "th":  ("Sensores_temp_hum.stl",     [[-1,0,0],[0,0,1],[0,1,0]], [-77.05,  -113.6, -29.7]),
    "gps": ("Sensores_GPS.stl",          [[0,1,0],[0,0,-1],[-1,0,0]], [-102.8,  -27.5, -23.5]),
}
BOARD_BOTTOM = -60.2           # cara inferior de la tarjeta (Y); abajo quedan los barriles

def interior(src, bottom):
    T = {k: load_stl(f"{src}/{f}") @ np.array(R, float).T + np.array(t) for k, (f, R, t) in STL.items()}
    pcb = T["pcb"]; top = pcb[:, :, 1].mean(1) >= BOARD_BOTTOM - 0.05
    # Placa de ruido: 4 postes (tope Y −98.5) + micrófono Ø6 en el poste libre (Z 2.5, X −124.3)
    bos = [(21.8, -70.75), (-15.0, -70.75), (-14.3, -124.3), (20.9, -124.3)]
    zs = [b[0] for b in bos]; xs = [b[1] for b in bos]
    ruido = [box([min(xs)-5, -98.5, min(zs)-5], [max(xs)+5, -96.9, max(zs)+5]),
             cylinder([-124.3, -98.5, 2.5], [-124.3, -103.5, 2.5], 3.0, 24)]
    ruido += [cylinder([x, -96.9, z], [x, -95.0, z], 2.75, 16) for z, x in bos]
    # Interruptores: botón momentáneo antivandálico con anillo LED, del mismo diámetro que los barrenos de la base (Ø18).
    # Entra a hueso: el tapón copia el contorno exacto de cada barreno (con sus cuñas y muescas) en todo el grueso del piso
    # (Y −109.5 a −107.5), así que no queda holgura por donde se vea el interior. Por fuera asoma 1.5 mm la cara del botón.
    sw, swm, led = [], [], []
    for z in (20.5, -21.25):
        c = lambda y: [-51.7, y, z]
        sw += [prism(hole_outline(bottom, -108.5, (-51.7, z)), -109.5, -107.5),   # tapón a la medida del barreno
               cylinder(c(-109.5), c(-111.0), 9.0, 48),                            # cara del botón Ø18
               cylinder(c(-107.5), c(-88.0), 8.0, 40),                             # cuerpo roscado
               cylinder(c(-111.0), c(-111.12), 6.4, 40)]                           # botón dentro del anillo
        led += [cylinder(c(-111.0), c(-111.06), 7.6, 48)]                          # anillo LED
        swm += [cylinder(c(-107.5), c(-104.5), 10.4, 6)]                           # tuerca hexagonal
        swm += [box([-51.7 + dx - 1.4, -88.0 - 6.0, z - .25], [-51.7 + dx + 1.4, -88.0, z + .25]) for dx in (-3.2, 3.2)]
        swm += [box([-51.7 - .25, -88.0 - 6.0, z + dx - 1.4], [-51.7 + .25, -88.0, z + dx + 1.4]) for dx in (-3.2, 3.2)]
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
        ("smaa_in_switches", v(sw),     [0.07, 0.07, 0.08, 1], 0.3, 0.45),
        ("smaa_in_switches_led", v(led), [0.95, 0.10, 0.08, 1], 0.0, 0.3),
        ("smaa_in_switches_metal", v(swm), [0.72, 0.73, 0.75, 1], 0.8, 0.3),
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
    bottom = next(pos * 1000 for name, pos, idx, mat in items if name == "smaa_bottom")[next(idx for name, pos, idx, mat in items if name == "smaa_bottom")]
    for name, tris, color, metal, rough in interior(src, bottom):
        pos, idx = cluster(tris, 0)
        items.append((name, pos * 0.001, idx, {"name": name, "pbrMetallicRoughness": {"baseColorFactor": color, "metallicFactor": metal, "roughnessFactor": rough}, "doubleSided": True}))
        print(f"{name:18s} {len(idx):6d} triángulos")
    write_glb(out or glb, items)

if __name__ == "__main__":
    main(*sys.argv[1:4])
