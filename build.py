"""Genera index.html (página completa para Netlify) a partir de twin.html, que es la fuente que editamos.
Uso: python3 build.py"""
from pathlib import Path
src = Path("twin.html").read_text(encoding="utf-8")
head_end = src.index("</style>") + len("</style>")
head = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Gemelo digital de las estaciones CHAAK y SMAA de Smability: datos en tiempo real, vista explosionada y guía de instalación por sitio.">
<meta property="og:title" content="Smability · Gemelo digital e instalación guiada">
<meta property="og:description" content="Explora las estaciones en 3D, sus datos en tiempo real y cómo instalarlas en tu ciudad.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#11201d">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
"""
base = "<style>html,body{margin:0}html{box-sizing:border-box;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>\n</head>\n<body>\n"
Path("index.html").write_text(head + src[:head_end] + "\n" + base + src[head_end:].lstrip("\n") + "\n</body>\n</html>\n", encoding="utf-8")
print("index.html listo")
