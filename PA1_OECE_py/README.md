# Data Warehouse + Data Mart – Contrataciones públicas del Perú (OECE/SEACE)

Solución 100 % Python: **pandas, numpy, SQLAlchemy y matplotlib**. Gestor de base de datos: **PostgreSQL** (tres bases: `stg_oece`, `dw_oece`, `dm_monitoreo`).

Fuente: Open Contracting Data Registry, publicación 135 – https://data.open-contracting.org/es/publication/135 (OECE, CC BY 4.0).

## Requisitos
- Python 3.10 o superior, ~3 GB libres en disco y ~8 GB de RAM.
- PostgreSQL en ejecución (local). Usuario y clave por variables de entorno (por defecto `postgres` / `postgres` en `localhost:5432`):
```bash
export PGUSER=postgres PGPASSWORD=tu_clave PGHOST=localhost PGPORT=5432     # Windows PowerShell: $env:PGPASSWORD="tu_clave"
pip install -r requirements.txt
```
Si `psycopg2-binary` no instala en tu versión de Python: `pip install "psycopg[binary]"` y `export PG_DRIVER=psycopg`.

## Ejecución
Todo de una vez (crea las bases, descarga ~430 MB, carga inicial 2023-2025, incremental 2026, validación y tablero):
```bash
python ejecutar_todo.py
```
O paso a paso:
```bash
python crear_bases.py                      # crea stg_oece, dw_oece y dm_monitoreo si no existen
python descargar_datos.py                  # CSV de 2023-2026 a data/ (reintenta ante errores temporales)
python generar_ddl.py                      # scripts CREATE TABLE en sql/ (opcional: mssql | mysql | oracle | sqlite)
python etl_01_staging.py                   # STG_OECE (carga inicial)
python etl_02_dw.py                        # DW_OECE (carga inicial)
python etl_03_dm.py                        # DM_Monitoreo (solo lee del DW)
python validar.py 2023 2024 2025           # conteos y totales fuente vs STG vs DW vs DM
python etl_01_staging.py --append 2026     # carga incremental: agrega 2026 al staging
python etl_02_dw.py --incremental          # SCD1 / SCD2 / hechos nuevos / baja lógica
python etl_03_dm.py
python validar.py 2023 2024 2025 2026
python tablero.py                          # salida/tablero_monitoreo.png, kpi_*.png, kpis.csv
```
Si una descarga falla, vuelve a ejecutar `python descargar_datos.py`; los años ya bajados se conservan. Para saltar la descarga: `python ejecutar_todo.py --sin-descarga`.

## Archivos
| Archivo | Función |
|---|---|
| `config.py` | Conexión a PostgreSQL, rutas, años, alcance del DM |
| `crear_bases.py` | Crea las 3 bases en PostgreSQL |
| `modelos.py` | DDL de STG, DW y DM con SQLAlchemy Core (claves subrogadas, PK, FK, auditoría) |
| `generar_ddl.py` | Exporta los modelos a `sql/*.sql` |
| `descargar_datos.py` | Descarga y descomprime los CSV |
| `etl_01_staging.py` | CSV → STG_OECE |
| `etl_02_dw.py` | STG → DW (inicial e `--incremental`) |
| `etl_03_dm.py` | DW → DM |
| `validar.py` | Controles de conteo y totales |
| `tablero.py` | Tablero de KPI con matplotlib |
| `docs/`, `GRUPO_01_PA01.docx` | Informe del PA1 (Word) y figuras |

## Diseño
- **DW (constelación):** FactConvocatoria (un proceso) y FactContrato (un contrato); 7 dimensiones: DimFecha, DimEntidad (SCD2), DimProveedor (SCD1, personas naturales anonimizadas), DimCategoria, DimMetodo, DimEstadoContrato, DimMoneda. Conformadas: Fecha, Entidad, Categoría, Método.
- **DM:** FactContratoMes y FactConvocatoriaMes (agregados por mes) con DimMes, DimEntidad, DimProveedor, DimCategoria, DimMetodo; alcance 2022-2026.
- **Limitación de la fuente:** cada proceso aparece solo en el archivo anual de su última actualización; 2022 está subrepresentado, compara 2023-2025.
