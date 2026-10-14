// Proxy hacia el API de las estaciones: oculta la API key y evita problemas de CORS.
// Variables de entorno en Netlify (Site configuration → Environment variables):
//   STATION_API_URL     URL del API. Puede incluir {id}: https://api.smability.io/v1/stations/{id}/latest
//                       Si no incluye {id}, se agrega ?id=CHAAK al final.
//   STATION_API_KEY     llave del API (opcional)
//   STATION_API_HEADER  encabezado donde va la llave (por defecto x-api-key; usa "Authorization" para Bearer)
const ALLOWED = new Set(["CHAAK", "SMAA"]);

export default async (req) => {
  const id = (new URL(req.url).searchParams.get("id") || "").toUpperCase();
  if (!ALLOWED.has(id)) return Response.json({ error: "estación no válida" }, { status: 400 });

  const base = process.env.STATION_API_URL;
  if (!base) return Response.json({ error: "STATION_API_URL no configurada" }, { status: 503 });

  const url = base.includes("{id}") ? base.replaceAll("{id}", encodeURIComponent(id))
                                    : `${base}${base.includes("?") ? "&" : "?"}id=${encodeURIComponent(id)}`;
  const headers = { accept: "application/json" };
  const key = process.env.STATION_API_KEY;
  if (key) {
    const h = process.env.STATION_API_HEADER || "x-api-key";
    headers[h] = h.toLowerCase() === "authorization" && !/^bearer /i.test(key) ? `Bearer ${key}` : key;
  }

  try {
    const ctl = AbortSignal.timeout(6000);
    const r = await fetch(url, { headers, signal: ctl });
    if (!r.ok) return Response.json({ error: "el API respondió con error", status: r.status }, { status: 502 });
    const data = await r.json();
    return Response.json(data, { headers: { "cache-control": "public, max-age=15" } });
  } catch (e) {
    return Response.json({ error: "sin conexión con la estación" }, { status: 504 });
  }
};
