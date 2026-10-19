"""Convierte las piezas STL exportadas de AutoCAD en un solo .glb para el visor.

Uso:  python3 tools/stl2glb.py tools/chaak.json  carpeta_con_stl  models/chaak.glb

El .json define, por pieza: archivo, nombre del nodo (clave que lee el visor), corrección en Y
(AutoCAD movió cada pieza a coordenadas positivas por separado), material y tamaño de simplificación.
Convención de salida: metros, Y arriba, origen en la base de la estación sobre el eje del tubo,
cara principal hacia −X (el visor la gira hacia sotavento de la lluvia).
"""
import json, struct, sys
import numpy as np


def load_stl(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    if 84 + n * 50 == len(b):
        rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        return np.frombuffer(b, dtype=rec, count=n, offset=84)["v"].astype(np.float64)
    tris, cur = [], []                                   # STL ASCII
    for line in b.decode("latin-1").splitlines():
        p = line.split()
        if p and p[0] == "vertex":
            cur.append([float(x) for x in p[1:4]])
            if len(cur) == 3: tris.append(cur); cur = []
    return np.array(tris, dtype=np.float64)


def cylinder(p0, p1, r, seg):
    """Cilindro cerrado entre p0 y p1 (mm), como triángulos."""
    p0, p1 = np.array(p0, float), np.array(p1, float); ax = p1 - p0; ax /= np.linalg.norm(ax)
    u = np.cross(ax, [0, 0, 1] if abs(ax[2]) < .9 else [1, 0, 0]); u /= np.linalg.norm(u); w = np.cross(ax, u)
    ang = np.linspace(0, 2 * np.pi, seg + 1)[:-1] + np.pi / seg
    ring = lambda c: [c + r * (np.cos(a) * u + np.sin(a) * w) for a in ang]
    a, b, out = ring(p0), ring(p1), []
    for i in range(seg):
        j = (i + 1) % seg
        out += [[a[i], b[i], b[j]], [a[i], b[j], a[j]], [p0, a[j], a[i]], [p1, b[i], b[j]]]
    return np.array(out)


def ring(cx, cy, z0, z1, r, seg, inward=False):
    """Pared cilíndrica abierta (sin tapas) entre z0 y z1; inward=True para la cara interior de un tubo."""
    a = np.linspace(0, 2 * np.pi, seg + 1)
    P = lambda k, z: [cx + r * np.cos(a[k]), cy + r * np.sin(a[k]), z]
    out = []
    for i in range(seg):
        t1, t2 = [P(i, z0), P(i + 1, z0), P(i + 1, z1)], [P(i, z0), P(i + 1, z1), P(i, z1)]
        if inward: t1, t2 = t1[::-1], t2[::-1]
        out += [t1, t2]
    return np.array(out, float)


def clip_z(tris, z0, keep_below):
    """Recorta triángulos contra el plano z = z0 y devuelve la parte de abajo (o de arriba), re-triangulada."""
    out = []
    for t in tris:
        inside = (t[:, 2] <= z0) if keep_below else (t[:, 2] >= z0)
        if inside.all(): out.append(t); continue
        if not inside.any(): continue
        poly = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]; ia, ib = inside[i], inside[(i + 1) % 3]
            if ia: poly.append(a)
            if ia != ib:
                k = (z0 - a[2]) / (b[2] - a[2]); poly.append(a + k * (b - a))
        for i in range(1, len(poly) - 1): out.append(np.array([poly[0], poly[i], poly[i + 1]]))
    return np.array(out, float)


def screws(spec):
    """Tornillos con eje en Y: cabeza hexagonal en y_head (lado opuesto a la carcasa) y vástago hasta y_tip."""
    tris = []
    if "radial" in spec:                                       # tornillos radiales alrededor de un eje vertical
        R = spec["radial"]; cx, cy = R["center"]
        for ang in R["angles"]:
            d = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang)), 0.0]); c = np.array([cx, cy, R["z"]])
            tris.append(cylinder(c + d * R["r_head"], c + d * (R["r_head"] + spec["head_h"]), spec["head_r"], 6))
            tris.append(cylinder(c + d * R["r_tip"], c + d * R["r_head"], spec["r"], 16))
        return np.vstack(tris)
    for x, z in spec["at"]:
        yh, yt, hh = spec["y_head"], spec["y_tip"], spec["head_h"]
        tris.append(cylinder([x, yh - hh, z], [x, yh, z], spec["head_r"], 6))
        tris.append(cylinder([x, yh, z], [x, yt, z], spec["r"], 16))
    return np.vstack(tris)


def cluster(tris, cell):
    """Simplificación por agrupamiento de vértices en una rejilla de `cell` (mismas unidades que el STL)."""
    v = tris.reshape(-1, 3)
    if not cell:
        keys = np.round(v, 4)
    else:
        keys = np.floor(v / cell).astype(np.int64)
    uniq, inv = np.unique(keys, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    pos = np.zeros((len(uniq), 3)); cnt = np.zeros(len(uniq))
    np.add.at(pos, inv, v); np.add.at(cnt, inv, 1); pos /= cnt[:, None]
    f = inv.reshape(-1, 3)
    ok = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    f = f[ok]
    srt = np.sort(f, axis=1); _, first = np.unique(srt, axis=0, return_index=True)
    f = f[np.sort(first)]
    used, remap = np.unique(f, return_inverse=True)
    return pos[used], remap.reshape(-1, 3)


def main(cfg_path, src_dir, out_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    axis_x, base_z, front = cfg["axis_x"], cfg["base_z"], cfg["front"]   # front: "+Y", "-Y", "+X", "-X"
    rot = {"+Y": 90, "-Y": -90, "+X": 180, "-X": 0}[front]                # giro en Z para llevar el frente a −X
    c, s = np.cos(np.radians(rot)), np.sin(np.radians(rot))
    mats, nodes, meshes, accessors, views, blob = [], [], [], [], [], bytearray()
    mat_index = {}

    def add_view(data, target):
        while len(blob) % 4: blob.append(0)
        off = len(blob); blob.extend(data)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(views) - 1

    report = []
    for p in cfg["parts"]:
        tris = screws(p["screws"]) if "screws" in p else load_stl(f"{src_dir}/{p['file']}")
        if "cut_below_z" in p:                                    # recorta lo que cuelga bajo esa altura (p. ej. cable)
            tris = tris[tris[:, :, 2].mean(1) >= p["cut_below_z"]]
        if "fill_ring" in p:                                      # tapa una ventana del tubo: quita lo que cae en la franja y la rehace lisa
            f = p["fill_ring"]
            tris = np.vstack([clip_z(tris, f["z0"], keep_below=True), clip_z(tris, f["z1"], keep_below=False)])
            tris = np.vstack([tris, ring(*f["center"], f["z0"], f["z1"], f["r_out"], f.get("seg", 72)),
                              ring(*f["center"], f["z0"], f["z1"], f["r_in"], f.get("seg", 72), inward=True)])
        n0 = len(tris)
        v = tris.reshape(-1, 3).copy()
        v[:, 0] -= axis_x
        v[:, 1] += p.get("dy", 0.0)
        if p.get("flip"):                                         # 180° alrededor del eje del tubo (mismos barrenos, otro lado)
            v[:, 0] = -v[:, 0]; v[:, 1] = -v[:, 1]          # (x ya está centrado en el eje)
        v[:, 2] += p.get("dz", 0.0)                               # sube o baja la pieza completa (mm)
        if "stretch" in p:                                        # alarga una pieza: todo lo que está arriba de z sube dz
            st = p["stretch"]; v[v[:, 2] > st["z"], 2] += st["dz"]
        v[:, 2] -= base_z
        x, y = v[:, 0].copy(), v[:, 1].copy()
        v[:, 0], v[:, 1] = c * x - s * y, s * x + c * y                       # giro en Z
        pos, idx = cluster(v.reshape(-1, 3, 3), p.get("cell", 0))
        g = np.empty_like(pos)                                               # Z arriba → Y arriba, mm → m
        g[:, 0], g[:, 1], g[:, 2] = pos[:, 0], pos[:, 2], -pos[:, 1]
        g = (g * cfg.get("scale", 0.001)).astype(np.float32)
        ind = idx.astype(np.uint16 if len(g) < 65536 else np.uint32)
        pv = add_view(g.tobytes(), 34962); iv = add_view(ind.tobytes(), 34963)
        accessors.append({"bufferView": pv, "componentType": 5126, "count": len(g), "type": "VEC3",
                          "min": g.min(0).tolist(), "max": g.max(0).tolist()})
        accessors.append({"bufferView": iv, "componentType": 5123 if ind.dtype == np.uint16 else 5125,
                          "count": int(ind.size), "type": "SCALAR"})
        m = p.get("material", "blanco")
        if m not in mat_index:
            mc = cfg["materials"][m]
            mat_index[m] = len(mats)
            mats.append({"name": m, "pbrMetallicRoughness": {"baseColorFactor": mc["color"] + [1.0],
                         "metallicFactor": mc.get("metal", 0.0), "roughnessFactor": mc.get("rough", 0.6)}, "doubleSided": True})
        meshes.append({"name": p["name"], "primitives": [{"attributes": {"POSITION": len(accessors) - 2},
                       "indices": len(accessors) - 1, "material": mat_index[m]}]})
        nodes.append({"name": p["name"], "mesh": len(meshes) - 1})
        report.append((p["name"], n0, int(ind.size) // 3, g.min(0), g.max(0)))

    while len(blob) % 4: blob.append(0)
    gltf = {"asset": {"version": "2.0", "generator": "smability stl2glb"}, "scene": 0,
            "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes,
            "materials": mats, "accessors": accessors, "bufferViews": views, "buffers": [{"byteLength": len(blob)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    open(out_path, "wb").write(out)
    for name, a, b, lo, hi in report:
        print(f"{name:32s} {a:7d} → {b:6d} triángulos   y {lo[1]:.3f}–{hi[1]:.3f} m")
    print(f"{out_path}: {len(out)/1e6:.2f} MB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
