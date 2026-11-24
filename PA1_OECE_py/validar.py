"""Validación: conteos y totales Fuente (CSV) vs STG vs DW vs DM.  Uso: python validar.py [años...]"""
import sys
import pandas as pd
import config
from etl_02_dw import leer

def src(csv, cols, anios):
    return pd.concat([pd.read_csv(config.DATA / y / y / f"{csv}.csv", usecols=cols, low_memory=False) for y in anios])

pd.options.display.float_format = "{:,.2f}".format

def main(anios):
    s, w, m = config.stg(), config.dw(), config.dm()
    D, M = config.DM_DESDE, config.DM_HASTA
    mm = src("main", ["ocid", "tender_value_amount_PEN", "tender_datePublished", "buyer_id"], anios)
    kk = src("contracts", ["id", "main_ocid", "value_amount", "value_currency", "dateSigned"], anios)
    ss = src("awards_suppliers", ["id"], anios)
    sm, sk, ssup = leer(s, "stg_main"), leer(s, "stg_contracts"), leer(s, "stg_awards_suppliers")
    fc, fk, dp, de = leer(w, "FactConvocatoria"), leer(w, "FactContrato"), leer(w, "DimProveedor"), leer(w, "DimEntidad")
    mk, mc = leer(m, "FactContratoMes"), leer(m, "FactConvocatoriaMes")
    anio_src = lambda col: pd.to_numeric(col.astype(str).str[:4], errors="coerce")
    rango = lambda a: a.between(D, M)
    filas = []
    def add(ctrl, fu, st, dw, dm, tol=0.01):
        vals = [v for v in (st, dw, dm) if v is not None]
        ok = fu is None and max(vals) - min(vals) <= tol or fu is not None and all(abs(float(v) - float(fu)) <= tol for v in vals)
        filas.append({"Control": ctrl, "Fuente": fu, "STG": st, "DW": dw, "DM": dm, "Cuadra": "Sí" if ok else "No"})
    add("Procesos de selección (filas)", len(mm), len(sm), len(fc), None)
    add("Valor referencial total PEN", round(mm["tender_value_amount_PEN"].sum(), 2), round(sm["value_amount_pen"].sum(), 2), round(fc["ValorReferencialPEN"].astype(float).sum(), 2), None, 1)
    add("Contratos (filas)", len(kk), len(sk), len(fk), None)
    kp = kk[kk["value_currency"] == "PEN"]
    mon = leer(w, "DimMoneda").set_index("MonedaKey")["MonedaCodigo"]
    add("Monto contratos con moneda original PEN", round(kp["value_amount"].sum(), 2), round(sk.loc[sk["value_currency"] == "PEN", "value_amount"].sum(), 2),
        round(fk.loc[fk["MonedaKey"].map(mon) == "PEN", "MontoOriginal"].astype(float).sum(), 2), None, 1)
    f_src = rango(anio_src(kk["dateSigned"])).sum(); f_stg = rango(anio_src(sk["date_signed"])).sum()
    f_dw = fk["FechaFirmaKey"].between(D * 10000 + 101, M * 10000 + 1231); 
    add(f"Contratos firmados {D}-{M} (filas)", int(f_src), int(f_stg), int(f_dw.sum()), int(mk["NumContratos"].sum()))
    filas.append({"Control": f"Monto contratos en PEN {D}-{M} (convertido por el ETL)", "Fuente": None, "STG": None, "DW": round(fk.loc[f_dw, "MontoContratoPEN"].astype(float).sum(), 2),
                  "DM": round(mk["MontoContratoPEN"].astype(float).sum(), 2), "Cuadra": ""})
    filas[-1]["Cuadra"] = "Sí" if abs(filas[-1]["DW"] - filas[-1]["DM"]) <= 1 else "No"
    add(f"Convocatorias publicadas {D}-{M} (filas)", int(rango(anio_src(mm["tender_datePublished"])).sum()), int(rango(anio_src(sm["date_published"])).sum()),
        int(fc["FechaPublicacionKey"].between(D * 10000 + 101, M * 10000 + 1231).sum()), int(mc["NumConvocatorias"].sum()))
    add("Proveedores distintos", ss["id"].nunique(), ssup["supplier_id"].nunique(), len(dp) - 1, len(leer(m, "DimProveedor")) - 1)
    add("Entidades compradoras distintas", mm["buyer_id"].nunique(), sm["buyer_id"].nunique(), de["EntidadCodigo"].nunique(), len(leer(m, "DimEntidad")))
    df = pd.DataFrame(filas); print(df.to_string(index=False))
    df.to_csv(config.SALIDA / f"validacion_{'_'.join(anios)}.csv", index=False, encoding="utf-8-sig")
    return df

if __name__ == "__main__":
    main(sys.argv[1:] or config.ANIOS_INICIALES)
