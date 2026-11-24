"""Ejecuta toda la solución en orden:  python ejecutar_todo.py [--sin-descarga]
1) descarga CSV  2) STG  3) DW inicial  4) DM  5) validación  6) incremental 2026 (STG + DW + DM + validación)  7) tablero"""
import sys, subprocess
py = sys.executable
def paso(*cmd):
    print("\n$", " ".join(cmd)); subprocess.run([py, *cmd], check=True)
if "--sin-descarga" not in sys.argv: paso("descargar_datos.py")
paso("crear_bases.py"); paso("generar_ddl.py")
paso("etl_01_staging.py"); paso("etl_02_dw.py"); paso("etl_03_dm.py"); paso("validar.py", "2023", "2024", "2025")
paso("etl_01_staging.py", "--append", "2026"); paso("etl_02_dw.py", "--incremental"); paso("etl_03_dm.py"); paso("validar.py", "2023", "2024", "2025", "2026")
paso("tablero.py")
print("\nListo. Revisa la carpeta salida/ (tablero_monitoreo.png, validacion_*.csv, kpis.csv) y las bases en PostgreSQL (stg_oece, dw_oece, dm_monitoreo).")
