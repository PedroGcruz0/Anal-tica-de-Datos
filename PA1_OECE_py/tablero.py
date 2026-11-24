"""Tablero de indicadores con matplotlib sobre DM_Monitoreo (pandas + numpy + SQLAlchemy).
Genera salida/tablero_monitoreo.png, un PNG por indicador y salida/kpis.csv."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config
from etl_02_dw import leer

AZUL, NARANJA, VERDE, MORADO, GRIS = "#2a6fb0", "#e08a2c", "#3a9a78", "#8a5fb0", "#6b7280"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": .25, "axes.axisbelow": True, "font.size": 9})
fm = lambda x, d=1: f"{x:,.{d}f}"

def datos():
    m = config.dm()
    mes, ent, prov, cat, met = (leer(m, t) for t in ("DimMes", "DimEntidad", "DimProveedor", "DimCategoria", "DimMetodo"))
    k = leer(m, "FactContratoMes").merge(mes[["MesKey", "Anio"]], on="MesKey").merge(cat, on="CategoriaKey").merge(met, on="MetodoKey")
    k["Competitivo"] = k["Competitivo"].astype(bool); k["MontoContratoPEN"] = k["MontoContratoPEN"].astype(float)
    c = leer(m, "FactConvocatoriaMes").merge(mes[["MesKey", "Anio"]], on="MesKey")
    return k, c, ent, prov

def calcular(k, c, ent, prov):
    A = {}
    anual = k.groupby("Anio").agg(contratos=("NumContratos", "sum"), monto=("MontoContratoPEN", "sum"), dias=("SumaDiasConvocatoriaAFirma", "sum"),
                                  n_dias=("NumContratosConDias", "sum"), plazo=("SumaPlazoDias", "sum"), n_plazo=("NumContratosConPlazo", "sum"))
    anual["monto"] /= 1e6; anual["dias_firma"] = anual["dias"] / anual["n_dias"]; anual["plazo_medio"] = anual["plazo"] / anual["n_plazo"]
    A["anual"] = anual
    A["categoria"] = k.pivot_table(index="Anio", columns="CategoriaNombre", values="MontoContratoPEN", aggfunc="sum") / 1e6
    tot = k.groupby("Anio")["MontoContratoPEN"].sum()
    A["directa"] = 100 * k[~k["Competitivo"]].groupby("Anio")["MontoContratoPEN"].sum().reindex(tot.index).fillna(0) / tot
    cc = c.groupby("Anio").agg(post=("SumaPostores", "sum"), n=("NumConvocatoriasConPostores", "sum"), conv=("NumConvocatorias", "sum"), adj=("NumAdjudicadas", "sum"))
    cc["postores"] = cc["post"] / cc["n"]; cc["pct_adj"] = 100 * cc["adj"] / cc["conv"]; A["conv"] = cc
    r = k[k["Anio"].between(2023, 2025)]
    tp = r[r["ProveedorKey"].map(prov.set_index("ProveedorKey")["ProveedorRUC"]) != "SIN-PROVEEDOR"]
    top = tp.groupby("ProveedorKey").agg(contratos=("NumContratos", "sum"), monto=("MontoContratoPEN", "sum")).nlargest(10, "monto").join(prov.set_index("ProveedorKey"))
    top["monto"] /= 1e6; A["top_prov"] = top; A["pct_top10"] = 100 * top["monto"].sum() * 1e6 / r["MontoContratoPEN"].sum()
    A["top_ent"] = (r.groupby("EntidadKey")["MontoContratoPEN"].sum().nlargest(10) / 1e6).to_frame("monto").join(ent.set_index("EntidadKey"))
    A["metodo"] = (r.groupby("MetodoNombre")["MontoContratoPEN"].sum().nlargest(8) / 1e6)
    return A

def barras(ax, serie, color, fmt, titulo, sub=None):
    x = np.arange(len(serie)); ax.bar(x, serie.values, color=color, width=.6)
    ax.set_xticks(x, [f"{i}{'*' if i == 2026 else ''}" for i in serie.index])
    for i, v in enumerate(serie.values): ax.text(i, v, fmt(v), ha="center", va="bottom", fontsize=8)
    ax.set_title(titulo, loc="left", fontweight="bold", fontsize=10.5, pad=16 if sub else 6)
    if sub: ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=7.5, color=GRIS)
    ax.margins(y=.15)

def hbarras(ax, serie, color, titulo, etiquetas=None, sub=None):
    etiquetas = etiquetas if etiquetas is not None else serie.index
    etq = [e if len(e) < 38 else e[:37] + "…" for e in etiquetas]
    ax.barh(range(len(serie))[::-1], serie.values, color=color); ax.set_yticks(range(len(serie))[::-1], etq, fontsize=7.5)
    for i, v in zip(range(len(serie))[::-1], serie.values): ax.text(v, i, " " + fm(v, 0), va="center", fontsize=7.5)
    ax.set_title(titulo, loc="left", fontweight="bold", fontsize=10.5); ax.margins(x=.18); ax.grid(axis="y", visible=False)

def kpis(A):
    a, c, d = A["anual"], A["conv"], A["directa"]
    return [("Monto contratado 2025", f"S/ {fm(a.loc[2025, 'monto'] / 1000)} mil M", "RA-01"),
            ("Crecimiento interanual 2025", f"{fm(100 * (a.loc[2025, 'monto'] / a.loc[2024, 'monto'] - 1))} %", "RA-08"),
            ("% monto contratación directa 2025", f"{fm(d.loc[2025])} %", "RA-03"),
            ("Concentración top-10 proveedores 2023-25", f"{fm(A['pct_top10'])} %", "RA-04"),
            ("Postores por convocatoria 2025", fm(c.loc[2025, "postores"]), "RA-05"),
            ("Días convocatoria → firma 2025", fm(a.loc[2025, "dias_firma"], 0), "RA-06")]

def tablero(A):
    a, c, d, cat = A["anual"].loc[2023:], A["conv"].loc[2023:], A["directa"].loc[2023:], A["categoria"].loc[2023:]
    fig = plt.figure(figsize=(17, 15), facecolor="#f6f7f9")
    gk = fig.add_gridspec(1, 6, left=.06, right=.985, top=.915, bottom=.86, wspace=.1)
    gs = fig.add_gridspec(3, 6, left=.06, right=.985, top=.80, bottom=.05, height_ratios=[2.2, 2.2, 2.6], hspace=.55, wspace=.7)
    fig.suptitle("Monitoreo de Contrataciones Públicas del Perú · DM_Monitoreo (OECE/SEACE)", x=.06, ha="left", fontsize=16, fontweight="bold", y=.985)
    fig.text(.06, .945, "Fuente: Open Contracting Data Registry, publicación 135 (CC BY 4.0) · Montos en millones de soles (S/ M) · * 2026 parcial", fontsize=9, color=GRIS)
    for i, (t, v, r) in enumerate(kpis(A)):
        ax = fig.add_subplot(gk[0, i]); ax.axis("off"); ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fc="white", ec="#e5e7eb"))
        ax.text(.05, .72, t, fontsize=7, wrap=True, color=GRIS, transform=ax.transAxes); ax.text(.05, .28, v, fontsize=15, fontweight="bold", transform=ax.transAxes)
        ax.text(.06, .06, r, fontsize=7.5, color=GRIS, transform=ax.transAxes)
    barras(fig.add_subplot(gs[0, 0:2]), a["monto"], AZUL, lambda v: fm(v, 0), "Monto contratado por año (S/ M)", "RA-01")
    ax = fig.add_subplot(gs[0, 2:4]); w = .27; x = np.arange(len(cat))
    for j, (nombre, col) in enumerate(zip(["Bienes", "Servicios", "Obras"], [AZUL, NARANJA, VERDE])):
        ax.bar(x + (j - 1) * w, cat[nombre], w, label=nombre, color=col)
    ax.set_xticks(x, [f"{i}{'*' if i == 2026 else ''}" for i in cat.index]); ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    ax.set_title("Monto por categoría (S/ M)", loc="left", fontweight="bold", fontsize=10.5, pad=16); ax.text(0, 1.02, "RA-02", transform=ax.transAxes, fontsize=7.5, color=GRIS); ax.margins(y=.2)
    barras(fig.add_subplot(gs[0, 4:6]), d, NARANJA, lambda v: f"{v:.1f}%", "% del monto por contratación directa", "RA-03")
    barras(fig.add_subplot(gs[1, 0:2]), c["postores"], VERDE, lambda v: f"{v:.1f}", "Postores promedio por convocatoria", "RA-05")
    barras(fig.add_subplot(gs[1, 2:4]), a["dias_firma"], MORADO, lambda v: f"{v:.0f}", "Días promedio de convocatoria a firma", "RA-06 · 2026* sesgado al alza (solo contratos ya firmados)")
    barras(fig.add_subplot(gs[1, 4:6]), c["pct_adj"], GRIS, lambda v: f"{v:.0f}%", "% de convocatorias adjudicadas", "RA-09")
    hbarras(fig.add_subplot(gs[2, 0:3]), A["top_ent"]["monto"], AZUL, "Top 10 entidades por monto 2023-25 (S/ M)", A["top_ent"]["EntidadNombre"])
    ax = fig.add_subplot(gs[2, 3:6]); ax.axis("off"); t = A["top_prov"]
    ax.set_title(f"Top 10 proveedores 2023-25 · concentración {fm(A['pct_top10'])} % del monto (RA-04)", loc="left", fontweight="bold", fontsize=10.5)
    filas = [[n[:34], ti, f"{int(cn):,}", fm(mo, 0)] for n, ti, cn, mo in zip(t["ProveedorNombre"], t["TipoProveedor"], t["contratos"], t["monto"])]
    tb = ax.table(cellText=filas, colLabels=["Proveedor", "Tipo", "Contratos", "S/ M"], loc="upper center", cellLoc="left", colWidths=[.5, .22, .14, .14])
    tb.auto_set_font_size(False); tb.set_fontsize(7.5); tb.scale(1, 1.55)
    for (r, cc), cell in tb.get_celld().items(): cell.set_edgecolor("#e5e7eb"); cell.set_facecolor("#d9e2f3" if r == 0 else "white")
    fig.text(.06, .015, "Nota: 2022 está subrepresentado (los archivos anuales agrupan por última actualización); las comparaciones fiables son 2023-2025. "
             "Personas naturales anonimizadas.", fontsize=8, color=GRIS)
    fig.savefig(config.SALIDA / "tablero_monitoreo.png", dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)

def individuales(A):
    a, c, d = A["anual"].loc[2023:], A["conv"].loc[2023:], A["directa"].loc[2023:]
    for nombre, serie, col, f, t in [("RA01_monto_anual", a["monto"], AZUL, lambda v: fm(v, 0), "Monto contratado por año (S/ M)"),
        ("RA03_pct_directa", d, NARANJA, lambda v: f"{v:.1f}%", "% del monto por contratación directa"),
        ("RA05_postores", c["postores"], VERDE, lambda v: f"{v:.1f}", "Postores promedio por convocatoria"),
        ("RA06_dias_a_firma", a["dias_firma"], MORADO, lambda v: f"{v:.0f}", "Días promedio de convocatoria a firma")]:
        fig, ax = plt.subplots(figsize=(6, 3.6)); barras(ax, serie, col, f, t); fig.savefig(config.SALIDA / f"kpi_{nombre}.png", dpi=150, bbox_inches="tight"); plt.close(fig)

def main():
    A = calcular(*datos()); tablero(A); individuales(A)
    pd.DataFrame(kpis(A), columns=["KPI", "Valor", "Requerimiento"]).to_csv(config.SALIDA / "kpis.csv", index=False, encoding="utf-8-sig")
    print("Generado:", sorted(p.name for p in config.SALIDA.glob("*.png"))); print(pd.DataFrame(kpis(A), columns=["KPI", "Valor", "Req"]).to_string(index=False))
    return A

if __name__ == "__main__":
    main()
