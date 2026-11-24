"""ETL_02_DW (carga inicial) y ETL_04_Incremental (--incremental): STG_OECE -> DW_OECE con pandas + numpy + SQLAlchemy.
Orden: dimensiones primero (limpieza, anonimización, claves subrogadas, SCD), hechos después (lookups con merge).
La carga inicial recrea el DW; la incremental conserva lo existente, aplica SCD1/SCD2, agrega hechos nuevos y da de baja lógica."""
import sys, time, hashlib, datetime as dt
import numpy as np, pandas as pd
from sqlalchemy import update, bindparam
import config, modelos
from modelos import (DimFecha, DimEntidad, DimProveedor, DimCategoria, DimMetodo, DimEstadoContrato, DimMoneda,
                     FactConvocatoria, FactContrato, EtlLog)

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
CONT = {"ins": 0, "upd": 0, "des": 0}

# ---------------------------------------------------------------- utilidades
def leer(eng, tabla, cols=None):
    df = pd.read_sql_table(tabla, eng)
    return df[cols] if cols else df

def agregar(eng, tabla, df):
    if len(df):
        df.to_sql(tabla, eng, if_exists="append", index=False, chunksize=20_000)
        CONT["ins"] += len(df)

def actualizar(eng, tabla, clave, filas, valores, baja=False):
    """UPDATE masivo (executemany): filas = lista de dicts con la clave y los nuevos valores."""
    if not filas: return
    stmt = update(tabla).where(tabla.c[clave] == bindparam("b_" + clave)).values({v: bindparam(v) for v in valores})
    with eng.begin() as cn:
        cn.execute(stmt, [{("b_" + clave if k == clave else k): v for k, v in f.items()} for f in filas])
    CONT["des" if baja else "upd"] += len(filas)

def parse_fecha(s):
    """Texto ISO -> (Serie datetime, o NaT si falta/fuera de 2000-2030; clave AAAAMMDD, 0 si no hay fecha)."""
    d = pd.to_datetime(s.astype("string").str[:10], format="%Y-%m-%d", errors="coerce")
    d = d.where(d.between("2000-01-01", "2030-12-31"))
    clave = (d.dt.year * 10000 + d.dt.month * 100 + d.dt.day).fillna(0).astype("int64")
    return d, clave

def mapa(df, bk, key):
    return df.drop_duplicates(bk).set_index(bk)[key]

# ---------------------------------------------------------------- dimensiones
def dim_fecha(eng):
    d = pd.DataFrame({"Fecha": pd.date_range("2000-01-01", "2030-12-31")})
    f = d["Fecha"]
    d = pd.DataFrame({
        "FechaKey": (f.dt.year * 10000 + f.dt.month * 100 + f.dt.day).astype(int), "Fecha": f.dt.date, "Anio": f.dt.year,
        "Trimestre": f.dt.quarter, "Mes": f.dt.month, "NombreMes": np.array(MESES)[f.dt.month - 1], "AnioMes": f.dt.year * 100 + f.dt.month,
        "Dia": f.dt.day, "DiaSemana": f.dt.isocalendar().day.astype(int), "NombreDia": np.array(DIAS)[f.dt.day_of_week],
        "EsFinSemana": f.dt.day_of_week >= 5})
    d = pd.concat([pd.DataFrame([{"FechaKey": 0, "Fecha": None, "Anio": 0, "Trimestre": 0, "Mes": 0, "NombreMes": "Sin fecha", "AnioMes": 0,
                                  "Dia": 0, "DiaSemana": 0, "NombreDia": "Sin fecha", "EsFinSemana": False}]), d], ignore_index=True)
    existentes = set(leer(eng, "DimFecha", ["FechaKey"])["FechaKey"])
    agregar(eng, "DimFecha", d[~d["FechaKey"].isin(existentes)])

def dims_simples(eng, main, contracts):
    # Categoría
    cat = main["main_category"].dropna().drop_duplicates().to_frame("CategoriaCodigo")
    cat["CategoriaNombre"] = cat["CategoriaCodigo"].map({"goods": "Bienes", "services": "Servicios", "works": "Obras"}).fillna(cat["CategoriaCodigo"].str.title())
    cat = pd.concat([pd.DataFrame([{"CategoriaCodigo": "N/D", "CategoriaNombre": "No especificado"}]), cat])
    ex = set(leer(eng, "DimCategoria", ["CategoriaCodigo"])["CategoriaCodigo"])
    cat = cat[~cat["CategoriaCodigo"].isin(ex)].assign(Activo=True); agregar(eng, "DimCategoria", cat)
    # Método (Competitivo = método general abierto o selectivo)
    m = main.dropna(subset=["method_details"]).assign(comp=lambda x: x["method_general"].isin(["open", "selective"]))
    met = m.groupby("method_details").agg(MetodoGeneral=("method_general", lambda s: s.dropna().max() if s.notna().any() else "N/D"),
                                          Competitivo=("comp", "max")).reset_index().rename(columns={"method_details": "MetodoNombre"})
    met = pd.concat([pd.DataFrame([{"MetodoNombre": "No especificado", "MetodoGeneral": "N/D", "Competitivo": False}]), met])
    ex = set(leer(eng, "DimMetodo", ["MetodoNombre"])["MetodoNombre"])
    agregar(eng, "DimMetodo", met[~met["MetodoNombre"].isin(ex)].assign(Activo=True))
    # Estado del contrato y moneda
    est = contracts[["status", "status_details"]].fillna({"status": "Sin estado", "status_details": "Sin detalle"}).drop_duplicates()
    est.columns = ["Estado", "EstadoDetalle"]
    est = pd.concat([pd.DataFrame([{"Estado": "Sin estado", "EstadoDetalle": "Sin detalle"}]), est]).drop_duplicates()
    ex = leer(eng, "DimEstadoContrato", ["Estado", "EstadoDetalle"])
    est = est.merge(ex, how="left", indicator=True); agregar(eng, "DimEstadoContrato", est[est["_merge"] == "left_only"].drop(columns="_merge"))
    mon = pd.DataFrame({"MonedaCodigo": ["N/D"] + sorted(contracts["value_currency"].dropna().unique())})
    ex = set(leer(eng, "DimMoneda", ["MonedaCodigo"])["MonedaCodigo"]); agregar(eng, "DimMoneda", mon[~mon["MonedaCodigo"].isin(ex)])

def dim_proveedor(eng, sup):
    """SCD tipo 1 (sobrescribe nombre/tipo) + miembro 'Sin proveedor' + baja lógica. Personas naturales (RUC 10) anonimizadas."""
    g = sup.dropna(subset=["supplier_id"]).groupby("supplier_id")["supplier_name"].max().reset_index()
    g.columns = ["ProveedorRUC", "nom"]
    natural = g["ProveedorRUC"].str.startswith("PE-RUC-10")
    hash8 = g["ProveedorRUC"].map(lambda r: hashlib.md5(r.encode()).hexdigest()[:8].upper())
    g["ProveedorNombre"] = np.where(natural, "PERSONA NATURAL " + hash8, g["nom"].fillna("Sin nombre")).astype(str)
    g["TipoProveedor"] = np.select([g["ProveedorRUC"].str.startswith("PE-RUC-20"), natural, g["ProveedorRUC"].str.startswith("PE-RUC-")],
                                   ["Persona jurídica", "Persona natural", "Otro RUC"], "Extranjero / otro")
    g["ProveedorNombre"] = g["ProveedorNombre"].str[:300]; g = g[["ProveedorRUC", "ProveedorNombre", "TipoProveedor"]]
    ex = leer(eng, "DimProveedor")
    if ex.empty:
        agregar(eng, "DimProveedor", pd.DataFrame([{"ProveedorRUC": "SIN-PROVEEDOR", "ProveedorNombre": "Sin proveedor identificado", "TipoProveedor": "Desconocido", "Activo": True}]))
        ex = leer(eng, "DimProveedor")
    m = g.merge(ex[["ProveedorKey", "ProveedorRUC", "ProveedorNombre", "TipoProveedor"]], on="ProveedorRUC", how="left", suffixes=("", "_old"))
    cambio = m[m["ProveedorKey"].notna() & ((m["ProveedorNombre"] != m["ProveedorNombre_old"]) | (m["TipoProveedor"] != m["TipoProveedor_old"]))]
    actualizar(eng, DimProveedor, "ProveedorKey",
               [{"ProveedorKey": int(r.ProveedorKey), "ProveedorNombre": r.ProveedorNombre, "TipoProveedor": r.TipoProveedor, "FechaActualizacion": dt.datetime.now()}
                for r in cambio.itertuples()], ["ProveedorNombre", "TipoProveedor", "FechaActualizacion"])
    agregar(eng, "DimProveedor", m[m["ProveedorKey"].isna()][["ProveedorRUC", "ProveedorNombre", "TipoProveedor"]].assign(Activo=True))
    baja = ex[(ex["ProveedorRUC"] != "SIN-PROVEEDOR") & ex["Activo"].astype(bool) & ~ex["ProveedorRUC"].isin(g["ProveedorRUC"])]
    actualizar(eng, DimProveedor, "ProveedorKey", [{"ProveedorKey": int(k), "Activo": False} for k in baja["ProveedorKey"]], ["Activo"], baja=True)

def dim_entidad(eng, main):
    """SCD tipo 2 sobre EntidadNombre: si cambia el nombre se cierra la versión vigente y se inserta una nueva."""
    ult = (main.dropna(subset=["buyer_id", "buyer_name"]).sort_values("release_date").drop_duplicates("buyer_id", keep="last")
           [["buyer_id", "buyer_name"]].rename(columns={"buyer_id": "EntidadCodigo", "buyer_name": "EntidadNombre"}))
    ult["EntidadNombre"] = ult["EntidadNombre"].str[:300]
    ex = leer(eng, "DimEntidad"); vig = ex[ex["EsVigente"].astype(bool)]
    m = ult.merge(vig[["EntidadKey", "EntidadCodigo", "EntidadNombre"]], on="EntidadCodigo", how="left", suffixes=("", "_old"))
    cambia = m[m["EntidadKey"].notna() & (m["EntidadNombre"] != m["EntidadNombre_old"])]
    hoy = dt.date.today()
    actualizar(eng, DimEntidad, "EntidadKey", [{"EntidadKey": int(k), "EsVigente": False, "FechaFin": hoy} for k in cambia["EntidadKey"]], ["EsVigente", "FechaFin"])
    nuevas = m[m["EntidadKey"].isna() | m.index.isin(cambia.index)][["EntidadCodigo", "EntidadNombre"]].copy()
    previo = nuevas["EntidadCodigo"].isin(ex["EntidadCodigo"])
    nuevas["FechaInicio"] = np.where(previo, hoy, dt.date(2000, 1, 1))
    agregar(eng, "DimEntidad", nuevas.assign(EsVigente=True, Activo=True))
    baja = vig[vig["Activo"].astype(bool) & ~vig["EntidadCodigo"].isin(ult["EntidadCodigo"])]
    actualizar(eng, DimEntidad, "EntidadKey", [{"EntidadKey": int(k), "Activo": False} for k in baja["EntidadKey"]], ["Activo"], baja=True)

# ---------------------------------------------------------------- tipo de cambio
def con_tipo_cambio(df, fx, clave_df, clave_fx, col_moneda, col_monto, promedio):
    """Monto en soles: PEN -> 1; otra moneda -> tasa de la fuente; si falta, promedio por moneda."""
    fx = fx.drop_duplicates(clave_fx)[clave_fx + ["rate"]].rename(columns=dict(zip(clave_fx, clave_df)))
    out = df.merge(fx, on=clave_df, how="left")
    prom = out[col_moneda].map(promedio)
    out["TipoCambio"] = np.where(out[col_moneda] == "PEN", 1.0, out["rate"].fillna(prom))
    out["MontoPEN"] = out[col_monto] * out["TipoCambio"]
    return out

# ---------------------------------------------------------------- hechos
def fact_convocatoria(eng, main, items, awards, awards_fx, promedio):
    ex = leer(eng, "FactConvocatoria", ["ConvocatoriaKey", "Ocid", "Activo"])
    nuevos = main[~main["ocid"].isin(ex["Ocid"])].copy()
    ent = mapa(leer(eng, "DimEntidad").query("EsVigente"), "EntidadCodigo", "EntidadKey")
    cat = mapa(leer(eng, "DimCategoria"), "CategoriaCodigo", "CategoriaKey"); met = mapa(leer(eng, "DimMetodo"), "MetodoNombre", "MetodoKey")
    pub, kpub = parse_fecha(nuevos["date_published"]); fin, kfin = parse_fecha(nuevos["tender_end_date"])
    aw = con_tipo_cambio(awards, awards_fx, ["main_ocid", "award_id"], ["main_ocid", "awards_id"], "value_currency", "value_amount", promedio)
    aw = aw.groupby("main_ocid").agg(NumAdjudicaciones=("award_id", "nunique"), MontoAdjudicadoPEN=("MontoPEN", lambda s: s.sum(min_count=1)))
    n_items = items.groupby("main_ocid").size()
    f = pd.DataFrame({"Ocid": nuevos["ocid"].values, "TenderId": nuevos["tender_id"].values, "FechaPublicacionKey": kpub.values, "FechaCierreKey": kfin.values,
        "EntidadKey": nuevos["buyer_id"].map(ent).values, "CategoriaKey": nuevos["main_category"].map(cat).fillna(cat["N/D"]).astype(int).values,
        "MetodoKey": nuevos["method_details"].map(met).fillna(met["No especificado"]).astype(int).values,
        "ValorReferencialPEN": nuevos["value_amount_pen"].values, "NumPostores": nuevos["num_tenderers"].round().astype("Int64").values,
        "NumItems": nuevos["ocid"].map(n_items).fillna(0).astype(int).values, "DiasConvocatoria": (fin - pub).dt.days.astype("Int64").values})
    f = f.join(aw, on="Ocid"); f["NumAdjudicaciones"] = f["NumAdjudicaciones"].fillna(0).astype(int); f["Activo"] = True
    f = f[f["EntidadKey"].notna()].astype({"EntidadKey": int})
    agregar(eng, "FactConvocatoria", f)
    baja = ex[ex["Activo"].astype(bool) & ~ex["Ocid"].isin(main["ocid"])]            # eliminación lógica
    actualizar(eng, FactConvocatoria, "ConvocatoriaKey", [{"ConvocatoriaKey": int(k), "Activo": False} for k in baja["ConvocatoriaKey"]], ["Activo"], baja=True)

def fact_contrato(eng, contracts, contracts_fx, awards_sup, promedio):
    ex = leer(eng, "FactContrato", ["ContratoKey", "Ocid", "ContratoId", "Activo"])
    llave_ex = pd.MultiIndex.from_frame(ex[["Ocid", "ContratoId"]])
    llave_src = pd.MultiIndex.from_frame(contracts[["main_ocid", "contract_id"]])
    nuevos = contracts[~llave_src.isin(llave_ex)].copy()
    fc = leer(eng, "FactConvocatoria", ["Ocid", "FechaPublicacionKey", "EntidadKey", "CategoriaKey", "MetodoKey"]).rename(columns={"Ocid": "main_ocid"})
    nuevos = nuevos.merge(fc, on="main_ocid", how="inner")                               # solo contratos con proceso conocido
    est = leer(eng, "DimEstadoContrato"); mon = mapa(leer(eng, "DimMoneda"), "MonedaCodigo", "MonedaKey")
    prov = mapa(leer(eng, "DimProveedor"), "ProveedorRUC", "ProveedorKey")
    nuevos["Estado"] = nuevos["status"].fillna("Sin estado"); nuevos["EstadoDetalle"] = nuevos["status_details"].fillna("Sin detalle")
    nuevos = nuevos.merge(est, on=["Estado", "EstadoDetalle"], how="left")
    sup = awards_sup.sort_values(["main_ocid", "awards_id", "supplier_id"]).drop_duplicates(["main_ocid", "awards_id"])[["main_ocid", "awards_id", "supplier_id"]]
    nuevos = nuevos.merge(sup, left_on=["main_ocid", "award_id"], right_on=["main_ocid", "awards_id"], how="left")
    nuevos = con_tipo_cambio(nuevos, contracts_fx, ["main_ocid", "contract_id"], ["main_ocid", "contracts_id"], "value_currency", "value_amount", promedio)
    firma, kfirma = parse_fecha(nuevos["date_signed"]); _, kfin = parse_fecha(nuevos["period_end"])
    ini, _ = parse_fecha(nuevos["period_start"]); fin_, _ = parse_fecha(nuevos["period_end"])
    pub = pd.to_datetime(nuevos["FechaPublicacionKey"].astype(str), format="%Y%m%d", errors="coerce")
    f = pd.DataFrame({"Ocid": nuevos["main_ocid"], "ContratoId": nuevos["contract_id"], "FechaFirmaKey": kfirma, "FechaFinKey": kfin,
        "EntidadKey": nuevos["EntidadKey"], "ProveedorKey": nuevos["supplier_id"].map(prov).fillna(prov["SIN-PROVEEDOR"]).astype(int),
        "CategoriaKey": nuevos["CategoriaKey"], "MetodoKey": nuevos["MetodoKey"], "EstadoKey": nuevos["EstadoKey"],
        "MonedaKey": nuevos["value_currency"].fillna("N/D").map(mon), "MontoOriginal": nuevos["value_amount"],
        "TipoCambio": nuevos["TipoCambio"], "MontoContratoPEN": nuevos["MontoPEN"],
        "PlazoDias": (fin_ - ini).dt.days.astype("Int64"), "DiasConvocatoriaAFirma": (firma - pub).dt.days.astype("Int64"), "Activo": True})
    agregar(eng, "FactContrato", f)
    llave_nueva = pd.MultiIndex.from_frame(ex[["Ocid", "ContratoId"]]).isin(llave_src)
    baja = ex[ex["Activo"].astype(bool) & ~llave_nueva]
    actualizar(eng, FactContrato, "ContratoKey", [{"ContratoKey": int(k), "Activo": False} for k in baja["ContratoKey"]], ["Activo"], baja=True)

# ---------------------------------------------------------------- orquestación
def main(incremental=False):
    t0 = time.time(); inicio = dt.datetime.now(); s, d = config.stg(), config.dw()
    if not incremental:
        modelos.dw_md.drop_all(d)
    modelos.dw_md.create_all(d)
    main_ = leer(s, "stg_main"); items = leer(s, "stg_tender_items", ["main_ocid"]); awards = leer(s, "stg_awards")
    awards_fx = leer(s, "stg_awards_fx"); sup = leer(s, "stg_awards_suppliers"); contracts = leer(s, "stg_contracts"); contracts_fx = leer(s, "stg_contracts_fx")
    # tipo de cambio promedio por moneda (respaldo cuando la fuente no trae tasa)
    cf = contracts.merge(contracts_fx.drop_duplicates(["main_ocid", "contracts_id"]), left_on=["main_ocid", "contract_id"], right_on=["main_ocid", "contracts_id"])
    promedio = cf[cf["value_currency"] != "PEN"].groupby("value_currency")["rate"].mean()
    dim_fecha(d); dims_simples(d, main_, contracts); dim_proveedor(d, sup); dim_entidad(d, main_)   # 1) dimensiones
    fact_convocatoria(d, main_, items, awards, awards_fx, promedio)                               # 2) hechos
    fact_contrato(d, contracts, contracts_fx, sup, promedio)
    pd.DataFrame([{"Proceso": "ETL_04_Incremental" if incremental else "ETL_02_DW", "Inicio": inicio, "Fin": dt.datetime.now(),
                   "FilasInsertadas": CONT["ins"], "FilasActualizadas": CONT["upd"], "FilasDesactivadas": CONT["des"]}]).to_sql("EtlLog", d, if_exists="append", index=False)
    for t in ("FactConvocatoria", "FactContrato", "DimEntidad", "DimProveedor"):
        print(t, f"{len(leer(d, t, [leer(d, t).columns[0]])):,}")
    print(f"Insertadas {CONT['ins']:,} · actualizadas {CONT['upd']:,} · dadas de baja {CONT['des']:,}")
    print(f"{'Incremental' if incremental else 'Carga inicial DW'} OK en {time.time() - t0:.0f}s")

if __name__ == "__main__":
    main("--incremental" in sys.argv)
