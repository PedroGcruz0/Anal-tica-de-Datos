import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
def box(ax,x,y,w,title,cols,color):
    h=0.32+0.21*len(cols)
    ax.add_patch(FancyBboxPatch((x,y-h),w,h,boxstyle="round,pad=0.02",fc="white",ec=color,lw=1.6))
    ax.add_patch(FancyBboxPatch((x,y-0.32),w,0.32,boxstyle="round,pad=0.02",fc=color,ec=color))
    ax.text(x+w/2,y-0.16,title,ha="center",va="center",color="white",fontsize=9,fontweight="bold")
    for i,c in enumerate(cols): ax.text(x+0.08,y-0.32-0.21*(i+0.55),c,fontsize=7.3,va="center")
    return (x,y,w,h)
def link(ax,a,b,c="#555"):
    ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="-|>",color=c,lw=0.9,alpha=.8))
def mid(b,side):
    x,y,w,h=b
    return {"l":(x,y-h/2),"r":(x+w,y-h/2),"t":(x+w/2,y),"b":(x+w/2,y-h)}[side]
# --- DW
fig,ax=plt.subplots(figsize=(11,6.6)); ax.set_xlim(0,11); ax.set_ylim(0,6.6); ax.axis("off")
B,O,G="#2a6fb0","#d9822b","#3a9a78"
fc=box(ax,3.9,6.5,3.2,"FactConvocatoria",["PK ConvocatoriaKey","FK FechaPublicacionKey, FechaCierreKey","FK EntidadKey, CategoriaKey, MetodoKey","Ocid, TenderId (degeneradas)","ValorReferencialPEN, NumPostores","NumItems, DiasConvocatoria","NumAdjudicaciones, MontoAdjudicadoPEN","Activo"],B)
fk=box(ax,3.9,3.3,3.2,"FactContrato",["PK ContratoKey","FK FechaFirmaKey, FechaFinKey","FK EntidadKey, ProveedorKey","FK CategoriaKey, MetodoKey","FK EstadoKey, MonedaKey","Ocid, ContratoId (degeneradas)","MontoOriginal, TipoCambio","MontoContratoPEN, PlazoDias","DiasConvocatoriaAFirma, Activo"],O)
df=box(ax,0.1,6.5,2.5,"DimFecha *",["PK FechaKey (AAAAMMDD)","Fecha, Anio, Trimestre, Mes","NombreMes, AnioMes, Dia","DiaSemana, EsFinSemana"],G)
de=box(ax,0.1,4.4,2.5,"DimEntidad * (SCD2)",["PK EntidadKey","EntidadCodigo (BK)","EntidadNombre","FechaInicio, FechaFin","EsVigente, Activo"],G)
dc=box(ax,8.4,6.5,2.5,"DimCategoria *",["PK CategoriaKey","CategoriaCodigo (BK)","CategoriaNombre","Activo"],G)
dm=box(ax,8.4,4.9,2.5,"DimMetodo *",["PK MetodoKey","MetodoNombre (BK)","MetodoGeneral, Competitivo","Activo"],G)
dp=box(ax,0.1,2.0,2.5,"DimProveedor (SCD1)",["PK ProveedorKey","ProveedorRUC (BK)","ProveedorNombre (anonim.)","TipoProveedor, Activo"],"#8a5fb0")
ds=box(ax,8.4,3.3,2.5,"DimEstadoContrato",["PK EstadoKey","Estado, EstadoDetalle"],"#8a5fb0")
dmo=box(ax,8.4,1.9,2.5,"DimMoneda",["PK MonedaKey","MonedaCodigo"],"#8a5fb0")
for d in (df,de,dc,dm): link(ax,mid(fc,"l" if d[0]<3 else "r"),mid(d,"r" if d[0]<3 else "l"),"#2a6fb0")
for d in (df,de,dp): link(ax,mid(fk,"l"),mid(d,"r"),"#d9822b")
for d in (dc,dm,ds,dmo): link(ax,mid(fk,"r"),mid(d,"l"),"#d9822b")
ax.text(5.5,0.2,"* dimensión conforme (compartida por ambos hechos)   |   Constelación de hechos · claves subrogadas en todas las dimensiones",ha="center",fontsize=8.5,style="italic")
fig.savefig("img/dw.png",dpi=170,bbox_inches="tight"); plt.close(fig)
# --- DM
fig,ax=plt.subplots(figsize=(11,5.4)); ax.set_xlim(0,11); ax.set_ylim(0,5.4); ax.axis("off")
f1=box(ax,3.9,5.2,3.2,"FactContratoMes",["FK MesKey, EntidadKey, ProveedorKey","FK CategoriaKey, MetodoKey","NumContratos, MontoContratoPEN","SumaPlazoDias, NumContratosConPlazo","SumaDiasConvocatoriaAFirma","NumContratosConDias"],O)
f2=box(ax,3.9,2.7,3.2,"FactConvocatoriaMes",["FK MesKey, EntidadKey","FK CategoriaKey, MetodoKey","NumConvocatorias, ValorReferencialPEN","SumaPostores, NumConvocatoriasConPostores","NumAdjudicadas, MontoAdjudicadoPEN","ValorRefAdjudicadasPEN"],B)
a=box(ax,0.1,5.2,2.5,"DimMes",["PK MesKey (AAAAMM)","Anio, Trimestre, Mes","NombreMes, PrimerDia"],G)
b=box(ax,0.1,3.4,2.5,"DimEntidad",["PK EntidadKey","EntidadCodigo","EntidadNombre"],G)
c=box(ax,8.4,5.2,2.5,"DimCategoria",["PK CategoriaKey","CategoriaNombre"],G)
d=box(ax,8.4,3.9,2.5,"DimMetodo",["PK MetodoKey","MetodoNombre, MetodoGeneral","Competitivo"],G)
e=box(ax,8.4,2.2,2.5,"DimProveedor",["PK ProveedorKey","ProveedorRUC, ProveedorNombre","TipoProveedor"],"#8a5fb0")
for x in (a,b): link(ax,mid(f1,"l"),mid(x,"r"),"#d9822b"); link(ax,mid(f2,"l"),mid(x,"r"),"#2a6fb0")
for x in (c,d): link(ax,mid(f1,"r"),mid(x,"l"),"#d9822b"); link(ax,mid(f2,"r"),mid(x,"l"),"#2a6fb0")
link(ax,mid(f1,"r"),mid(e,"l"),"#d9822b")
fig.savefig("img/dm.png",dpi=170,bbox_inches="tight"); plt.close(fig)
# --- ER fuente
fig,ax=plt.subplots(figsize=(11,4.6)); ax.set_xlim(0,11); ax.set_ylim(0,4.6); ax.axis("off")
m=box(ax,0.1,4.5,2.9,"main (proceso/tender)",["PK ocid","buyer_id, buyer_name","tender_mainProcurementCategory","tender_procurementMethodDetails","tender_datePublished","tender_numberOfTenderers","tender_value_amount_PEN"],B)
ti=box(ax,4.1,4.5,2.6,"tender_items",["FK main_ocid","id, position, quantity","totalValue_amount"],G)
aw=box(ax,4.1,2.8,2.6,"awards",["id (award_id)","FK main_ocid","date, value_amount, currency"],G)
su=box(ax,7.8,4.5,3.0,"awards_suppliers",["id (RUC), name","FK main_ocid","FK awards_id"],G)
co=box(ax,7.8,2.8,3.0,"contracts",["id (contract_id)","FK main_ocid, awardID","dateSigned, status, statusDetails","value_amount, value_currency","period_startDate, period_endDate"],O)
for x in (ti,aw): link(ax,mid(x,"l"),mid(m,"r"),"#555")
link(ax,mid(su,"l"),mid(aw,"r"),"#555"); link(ax,mid(co,"l"),mid(aw,"r"),"#555"); link(ax,mid(co,"t"),mid(su,"b"),"#555")
fig.savefig("img/er.png",dpi=170,bbox_inches="tight"); plt.close(fig)
# --- Gantt
import datetime as dt
tasks=[("Levantamiento de requerimientos","2026-09-14","2026-09-25"),("Diseño del Data Warehouse","2026-09-28","2026-10-09"),("Diseño del Data Mart","2026-10-12","2026-10-16"),
 ("Implementación física (DDL)","2026-10-19","2026-10-30"),("ETL: STG, DW, DM e incremental","2026-11-02","2026-11-10"),("Validación de la carga","2026-11-10","2026-11-13"),("Tablero de indicadores","2026-11-11","2026-11-16"),("Informe y sustentación","2026-11-12","2026-11-20")]
fig,ax=plt.subplots(figsize=(10,3.2))
for i,(n,s,e) in enumerate(tasks):
    s=dt.date.fromisoformat(s); e=dt.date.fromisoformat(e); ax.barh(i,(e-s).days+1,left=matplotlib.dates.date2num(s),color="#2a6fb0")
ax.set_yticks(range(len(tasks))); ax.set_yticklabels([t[0] for t in tasks],fontsize=8); ax.invert_yaxis(); ax.xaxis_date()
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d-%b")); ax.tick_params(axis="x",labelsize=8); ax.grid(axis="x",alpha=.3)
fig.savefig("img/gantt.png",dpi=170,bbox_inches="tight"); plt.close(fig)
print("ok")
