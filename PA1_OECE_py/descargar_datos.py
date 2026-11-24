"""Descarga y descomprime los CSV anuales de la publicación 135 del Open Contracting Data Registry (OECE/SEACE, CC BY 4.0).
Reintenta automáticamente ante errores temporales del servidor (p. ej. HTTP 520/502/503) y omite los años ya descargados.
Uso: python descargar_datos.py            (2023, 2024, 2025 y 2026)
     python descargar_datos.py 2025       (solo ese año)"""
import sys, time, tarfile, urllib.request, urllib.error
from config import DATA, ANIOS_INICIALES, ANIO_INCREMENTAL

URL = "https://data.open-contracting.org/es/publication/135/download?name={y}.csv.tar.gz"
INTENTOS, ESPERA = 8, 10   # reintentos y segundos base de espera (crece con cada intento)

def bajar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (descarga academica OCDS)"})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
        total, leido, t0 = int(r.headers.get("Content-Length", 0)), 0, time.time()
        while True:
            bloque = r.read(1 << 20)
            if not bloque: break
            f.write(bloque); leido += len(bloque)
            print(f"\r   {leido/1e6:7.1f} / {total/1e6:.1f} MB", end="", flush=True)
        print()
        if total and leido != total: raise IOError(f"descarga incompleta ({leido} de {total} bytes)")

def descargar(y):
    destino = DATA / y
    if (destino / y / "main.csv").exists():
        print(f"{y}: ya existe, se omite"); return
    destino.mkdir(parents=True, exist_ok=True)
    arch = DATA / f"{y}.csv.tar.gz"
    for n in range(1, INTENTOS + 1):
        try:
            print(f"{y}: descargando (intento {n}/{INTENTOS})…")
            bajar(URL.format(y=y), arch); break
        except (urllib.error.URLError, IOError, TimeoutError) as e:
            print(f"   error: {e}")
            if n == INTENTOS: raise SystemExit(f"No se pudo descargar {y}. Vuelve a ejecutar más tarde (los años ya bajados se conservan).")
            time.sleep(ESPERA * n)
    with tarfile.open(arch) as t:
        try: t.extractall(destino, filter="data")
        except TypeError: t.extractall(destino)
    arch.unlink()
    print(f"{y}: listo")

if __name__ == "__main__":
    for y in (sys.argv[1:] or ANIOS_INICIALES + [ANIO_INCREMENTAL]):
        descargar(y)
