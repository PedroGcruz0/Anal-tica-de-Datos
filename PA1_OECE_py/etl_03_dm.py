"""ETL_03_DM: DW_OECE -> DM_Monitoreo (Data Mart dependiente: solo lee del DW). pandas + SQLAlchemy.
Alcance: 2022-2026, registros activos. Hechos agregados por mes con groupby."""
import time, datetime as dt
import pandas as pd
import config, modelos
from etl_02_dw import leer

def main():
    t0 = time.time(); inicio = dt.datetime.now(); w, m = config.dw(), config.dm()
    modelos.dm_md.drop_all(m); modelos.dm_md.create_all(m)
    desde, hasta = config.DM_DESDE, config.DM_HASTA
    # --- dimensiones
    fecha = leer(w, "DimFecha"); fecha = fecha[fecha["Anio"].between(desde, hasta)]
    mes = fecha.drop_duplicates("AnioMes").assign(MesKey=lambda x: x["AnioMes"], PrimerDia=lambda x: pd.to_datetime(dict(year=x["Anio"], month=x["Mes"], day=1)).dt.date)
    mes[["MesKey", "Anio", "Trimestre", "Mes", "NombreMes", "PrimerDia"]].to_sql("DimMes", m, if_exists="append", index=False)
    ent_all = leer(w, "DimEntidad"); vig = ent_all[ent_all["EsVigente"].astype(bool)]
    vig[["EntidadKey", "EntidadCodigo", "EntidadNombre"]].to_sql("DimEntidad", m, if_exists="append", index=False)
    ent_map = ent_all[["EntidadKey", "EntidadCodigo"]].merge(vig[["EntidadKey", "EntidadCodigo"]], on="EntidadCodigo", suffixes=("", "_vig")).set_index("EntidadKey")["EntidadKey_vig"]
    leer(w, "DimProveedor")[["ProveedorKey", "ProveedorRUC", "ProveedorNombre", "TipoProveedor"]].to_sql("DimProveedor", m, if_exists="append", index=False)
    leer(w, "DimCategoria")[["CategoriaKey", "CategoriaNombre"]].to_sql("DimCategoria", m, if_exists="append", index=False)
    leer(w, "DimMetodo")[["MetodoKey", "MetodoNombre", "MetodoGeneral", "Competitivo"]].to_sql("DimMetodo", m, if_exists="append", index=False)
    # --- hecho de contratos: contratos activos firmados en el rango, agregados por mes
    k = leer(w, "FactContrato"); k = k[k["Activo"].astype(bool) & k["FechaFirmaKey"].between(desde * 10000 + 101, hasta * 10000 + 1231)].copy()
    k["MesKey"] = k["FechaFirmaKey"] // 100; k["EntidadKey"] = k["EntidadKey"].map(ent_map)
    fc = (k.groupby(["MesKey", "EntidadKey", "ProveedorKey", "CategoriaKey", "MetodoKey"], as_index=False)
           .agg(NumContratos=("ContratoKey", "size"), MontoContratoPEN=("MontoContratoPEN", lambda s: s.sum(min_count=1)),
                SumaPlazoDias=("PlazoDias", "sum"), SumaDiasConvocatoriaAFirma=("DiasConvocatoriaAFirma", "sum"),
                NumContratosConPlazo=("PlazoDias", "count"), NumContratosConDias=("DiasConvocatoriaAFirma", "count")))
    fc.to_sql("FactContratoMes", m, if_exists="append", index=False, chunksize=20_000)
    # --- hecho de convocatorias
    c = leer(w, "FactConvocatoria"); c = c[c["Activo"].astype(bool) & c["FechaPublicacionKey"].between(desde * 10000 + 101, hasta * 10000 + 1231)].copy()
    c["MesKey"] = c["FechaPublicacionKey"] // 100; c["EntidadKey"] = c["EntidadKey"].map(ent_map)
    c["adj"] = c["NumAdjudicaciones"] > 0
    c["MontoAdj"] = c["MontoAdjudicadoPEN"].where(c["adj"]); c["RefAdj"] = c["ValorReferencialPEN"].where(c["adj"])
    fv = (c.groupby(["MesKey", "EntidadKey", "CategoriaKey", "MetodoKey"], as_index=False)
           .agg(NumConvocatorias=("ConvocatoriaKey", "size"), ValorReferencialPEN=("ValorReferencialPEN", lambda s: s.sum(min_count=1)),
                SumaPostores=("NumPostores", "sum"), NumConvocatoriasConPostores=("NumPostores", "count"), NumAdjudicadas=("adj", "sum"),
                MontoAdjudicadoPEN=("MontoAdj", lambda s: s.sum(min_count=1)), ValorRefAdjudicadasPEN=("RefAdj", lambda s: s.sum(min_count=1))))
    fv.to_sql("FactConvocatoriaMes", m, if_exists="append", index=False, chunksize=20_000)
    pd.DataFrame([{"Proceso": "ETL_03_DM", "Inicio": inicio, "Fin": dt.datetime.now(), "FilasInsertadas": len(fc) + len(fv)}]).to_sql("EtlLog", w, if_exists="append", index=False)
    print(f"FactContratoMes {len(fc):,} · FactConvocatoriaMes {len(fv):,}"); print(f"ETL_03_DM OK en {time.time() - t0:.0f}s")

if __name__ == "__main__":
    main()
