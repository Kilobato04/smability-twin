"""Exporta reelintro/ a MP4 cuadro a cuadro (render(t) es determinista).
Uso: python3 tools/reelintro_render.py <url_base> <h|v> <es|en> <fps> <salida.mp4> [audio.mp3]
  audio.mp3 (opcional): p. ej. reelintro/audio/neon-drive_voz.mp3 (con voz) o reelintro/audio/neon-drive.mp3 (solo música); se agrega como pista de audio (AAC 192k)
  url_base: p. ej. http://localhost:8765/reelintro/index.html (servir el repo con cualquier servidor estático)
Requiere: playwright (chromium) y ffmpeg."""
import asyncio, subprocess, sys
from playwright.async_api import async_playwright
base, fmt, lang, fps, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
audio = sys.argv[6] if len(sys.argv) > 6 else None
W, H = (1920, 1080) if fmt == "h" else (1080, 1920)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.goto(f"{base}?render=1&format={fmt}&lang={lang}")
        await pg.wait_for_function("window.REEL && REEL.ready", timeout=120000)
        dur = await pg.evaluate("REEL.duration"); n = int(round(dur * fps))
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                               *(["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"] if audio else []),
                               "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        for i in range(n):
            await pg.evaluate(f"REEL.seek({i / fps:.5f})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=95))
            if i % 150 == 0: print(f"{fmt} {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); await b.close(); print("listo", out)
asyncio.run(main())
