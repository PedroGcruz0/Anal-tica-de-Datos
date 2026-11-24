from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import csv
d = Document()
for s in d.sections: s.left_margin=s.right_margin=Cm(2.2); s.top_margin=s.bottom_margin=Cm(2)
st = d.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(12); st.element.rPr.rFonts.set(qn("w:eastAsia"),"Calibri")
st.paragraph_format.space_after=Pt(4); st.paragraph_format.line_spacing=1.0
for n,sz in (("Heading 1",14),("Heading 2",12)):
    h=d.styles[n]; h.font.name="Calibri"; h.font.size=Pt(sz); h.font.bold=True; h.font.color.rgb=None
    h.element.rPr.rFonts.set(qn("w:ascii"),"Calibri"); h.element.rPr.rFonts.set(qn("w:hAnsi"),"Calibri")
    h.paragraph_format.space_before=Pt(8); h.paragraph_format.space_after=Pt(3)
def P(t,b=False,i=False,al=None,sz=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=b; r.italic=i
    if sz: r.font.size=Pt(sz)
    if al=="c": p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    elif al!="l": p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p
def B(t): 
    p=d.add_paragraph(style="List Bullet"); p.add_run(t); p.paragraph_format.space_after=Pt(1); return p
def shade(c,color):
    tcPr=c._tc.get_or_add_tcPr(); s=OxmlElement("w:shd"); s.set(qn("w:val"),"clear"); s.set(qn("w:fill"),color); tcPr.append(s)
def T(head,rows,widths=None,sz=9.5):
    t=d.add_table(rows=1,cols=len(head)); t.style="Table Grid"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(head):
        c=t.rows[0].cells[i]; c.text=""; r=c.paragraphs[0].add_run(h); r.bold=True; r.font.size=Pt(sz); shade(c,"D9E2F3")
    for row in rows:
        cs=t.add_row().cells
        for i,v in enumerate(row):
            cs[i].text=""; r=cs[i].paragraphs[0].add_run(str(v)); r.font.size=Pt(sz)
    for row in t.rows:
        for c in row.cells: c.paragraphs[0].paragraph_format.space_after=Pt(0)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    d.add_paragraph().paragraph_format.space_after=Pt(0)
def IMG(p,w,cap):
    d.add_picture(p,width=Inches(w)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    P(cap,i=True,al="c",sz=10)

# 1 Portada
P("UNIVERSIDAD SEÑOR DE SIPÁN",b=True,al="c",sz=16)
P("FACULTAD DE INGENIERÍA, ARQUITECTURA Y URBANISMO",al="c"); P("ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS",al="c")
P("[Insertar logo de la USS]",i=True,al="c")
P("Curso: Analítica de Datos – Ciclo 2026-II (VII ciclo)",al="c")
P("PERFIL DE PROYECTO",b=True,al="c",sz=16)
P("Diseño e implementación de un Data Warehouse y un Data Mart para el monitoreo de las contrataciones públicas del Estado peruano (OECE/SEACE)",b=True,al="c",sz=14)
P("Equipo: GRUPO_[N°]   |   Integrantes: [Apellidos y nombres de los integrantes, máx. 5]",al="c")
P("Docente responsable: [Nombre del docente]   |   Fecha de entrega: [dd/mm/2026]",al="c")
d.add_page_break()
# 2
d.add_heading("2. Datos informativos",1)
T(["Campo","Contenido"],[
 ["2.1 Nombre del proyecto","DW_OECE y DM_Monitoreo: inteligencia de negocios para las contrataciones públicas del Perú"],
 ["2.2 Organización","Organismo Especializado para las Contrataciones Públicas Eficientes (OECE), ex OSCE; rubro: regulación y supervisión de contrataciones del Estado; ubicación: Lima, Perú. Datos del Sistema Electrónico de Contrataciones del Estado (SEACE)."],
 ["2.3 Unidad de negocio","Procesos que integra el DW: (1) convocatoria de procesos de selección y (2) contratos derivados."],
 ["2.4 Área usuaria del Data Mart","Unidad de Monitoreo y Transparencia de Contrataciones; responsable: [jefe/a del área – a confirmar]"],
 ["2.5 Miembros del equipo","[Nombre – rol (líder, modelador DW, ETL, BI, documentación)]"],
 ["2.6 Fecha de inicio y presentación","Inicio: 14/09/2026 · Presentación: [dd/mm/2026]"]],[5,11])
# 3
d.add_heading("3. Planificación del proyecto",1)
d.add_heading("3.1 Planteamiento del problema",2)
P("El OECE publica en su portal de contrataciones abiertas los procesos generados en el SEACE en archivos planos (JSON, CSV, Excel) y los redistribuye el Open Contracting Data Registry (publicación 135, licencia CC BY 4.0). Cada año se publican cientos de miles de registros: entre 2023 y oct-2026 el portal contiene 414 022 procesos de selección, 338 492 contratos y 348 532 registros de proveedores adjudicados, repartidos en 21 tablas por año, de las cuales solo siete son necesarias para el análisis. Para obtener una cifra como el monto contratado por categoría y método, el analista debe descargar un archivo por año, unir manualmente tablas por la clave ocid, convertir montos de varias monedas y reconciliar duplicados, lo que es lento (varias horas por consulta), difícil de repetir y propenso a errores.")
P("Como consecuencia, el área de monitoreo no puede responder con oportunidad preguntas básicas: cuánto se contrata por categoría, qué parte se adjudica sin competencia, cuán concentrados están los proveedores, cuántos postores hay por proceso o cuánto demora pasar de la convocatoria a la firma del contrato. Los datos tampoco están anonimizados: 20 % de los proveedores son personas naturales (RUC 10) con nombre propio.")
d.add_heading("3.2 Objetivos",2)
P("Objetivo general: implementar un Data Warehouse que integre los procesos de convocatoria y contratación del OECE/SEACE 2023-2026 y un Data Mart de Monitoreo y Transparencia que permita analizar monto, competencia y plazos de las contrataciones por entidad, categoría, método, proveedor y mes, reduciendo de horas a segundos el tiempo de obtención de un indicador.")
for t in ["OE1. Documentar al menos 9 requerimientos analíticos como preguntas de negocio con indicador y dimensiones (sección 4).",
 "OE2. Diseñar un DW en constelación con 2 hechos, 7 dimensiones (4 conformadas) y claves subrogadas.",
 "OE3. Implementar los ETL a STG, DW y DM con carga inicial e incremental (SCD tipo 1 y tipo 2) y validar conteos y totales al 100 %.",
 "OE4. Construir un tablero con 6 KPI asociados a los requerimientos y proponer al menos 3 decisiones."]: B(t)
d.add_heading("3.3 Cronograma (diagrama de Gantt)",2)
IMG("img/gantt.png",5.9,"Figura 1. Cronograma del proyecto (responsables: ver tabla 2.5).")
# 4
d.add_heading("4. Gestión de requerimientos analíticos",1)
P("Al ser una base pública, los requerimientos se obtuvieron del análisis de la documentación publicada por el OECE (política de publicación y esquema OCDS) y de los indicadores de transparencia habituales en contrataciones abiertas (competencia, uso de contratación directa, concentración).")
d.add_heading("4.1 Requerimientos funcionales analíticos",2)
T(["ID","Pregunta de negocio","Indicador","Dimensiones","Atiende"],[
 ["RA-01","¿Cuánto se contrata por año y mes?","Monto contratado (S/); N.º contratos","Fecha","DW y DM"],
 ["RA-02","¿Cómo se reparte el monto entre bienes, servicios y obras?","Monto por categoría","Categoría, Fecha","DW y DM"],
 ["RA-03","¿Qué parte del monto se contrata sin competencia?","% monto en métodos no competitivos","Método, Fecha","DW y DM"],
 ["RA-04","¿Cuán concentrado está el mercado de proveedores?","% del monto del top 10","Proveedor","DW y DM"],
 ["RA-05","¿Cuántos postores participan por proceso?","Postores promedio","Método, Categoría, Fecha","DW y DM"],
 ["RA-06","¿Cuánto demora llegar de la convocatoria a la firma?","Días promedio","Entidad, Fecha","DW y DM"],
 ["RA-07","¿Qué entidades contratan más?","Monto por entidad","Entidad, Fecha","DW y DM"],
 ["RA-08","¿Cómo evoluciona el monto frente al año anterior?","% crecimiento interanual","Fecha","DW y DM"],
 ["RA-09","¿Qué % de convocatorias termina adjudicado? ¿Qué relación hay entre lo adjudicado y el valor referencial?","% adjudicadas; adjudicado/referencial","Entidad, Método","DW"],
 ["RA-10","¿Cuánto pagamos a cada estado de contrato (nulos, resueltos, en ejecución)?","Contratos y monto por estado","Estado, Moneda","DW"]],[1.4,5.6,3.8,3.2,1.6],sz=9)
d.add_heading("4.2 Requerimientos no funcionales",2)
T(["ID","Requerimiento no funcional","Validación"],[
 ["RNF-01","La carga incremental debe completarse en menos de 15 minutos.","Tabla EtlLog: ETL_04 = ver tabla EtlLog (134 917 procesos y 104 571 contratos nuevos)"],
 ["RNF-02","El DW conserva al menos 3 años de historia.","DimFecha 2000-2030; contratos firmados 2012-2027 (74 % en 2022-2026; DM con 5 años)"],
 ["RNF-03","Los datos personales deben estar anonimizados.","Proveedores RUC 10 sustituidos por PERSONA NATURAL + hash de 8 caracteres"],
 ["RNF-04","El tablero debe actualizarse con un solo clic.","python tablero.py regenera el tablero desde el DM con un solo comando"]],[1.6,7.2,7.4],sz=9)
d.add_heading("4.3 Modelo relacional de la unidad de negocio",2)
IMG("img/er.png",5.8,"Figura 2. Diagrama entidad-relación de las tablas fuente (OCDS en formato CSV plano).")
T(["Tabla fuente","Registros","Periodo","Uso en el proyecto"],[
 ["main","414 022","2013-2026","Hecho de convocatoria; DimEntidad, DimCategoria, DimMetodo"],
 ["tender_items","500 161","2013-2026","NumItems del hecho de convocatoria"],
 ["awards","352 531","2013-2026","NumAdjudicaciones y MontoAdjudicadoPEN"],
 ["awards_suppliers","348 532","2013-2026","DimProveedor"],
 ["contracts","338 492","2012-2027","Hecho de contrato; DimEstadoContrato, DimMoneda"],
 ["*_exchangeRates","11 000 aprox.","2023-2026","Tipo de cambio a soles"]],[3.4,2.6,2.6,7.6],sz=9)
P("Los datos provienen del archivo anual (2023, 2024, 2025 y 2026) de cada tabla en https://data.open-contracting.org/es/publication/135. Cada proceso aparece en un solo archivo anual: el de su última actualización.",sz=11)
# 5
d.add_heading("5. Diseño del Data Warehouse",1)
d.add_heading("5.1 Procesos de negocio y matriz de bus",2)
T(["Proceso","Fecha","Entidad","Categoría","Método","Proveedor","Estado","Moneda"],[
 ["Convocatoria","X","X","X","X","","",""],["Contrato","X","X","X","X","X","X","X"]],[3,1.8,1.8,2,1.8,2.2,1.8,1.8])
P("Las dimensiones marcadas en ambas filas (Fecha, Entidad, Categoría y Método) son las dimensiones conformadas.")
d.add_heading("5.2 Declaración del grano",2)
B("FactConvocatoria: una fila por proceso de selección (identificado por ocid).")
B("FactContrato: una fila por contrato firmado (ocid + id de contrato).")
d.add_heading("5.3 Dimensiones identificadas",2)
T(["Dimensión","Atributos principales","Clave de negocio","SCD"],[
 ["DimFecha","Fecha, año, trimestre, mes, nombre del mes, día de semana","Fecha (AAAAMMDD)","Tipo 0"],
 ["DimEntidad","Código y nombre de la entidad, FechaInicio/Fin, EsVigente","buyer.id","Tipo 2 (nombre)"],
 ["DimProveedor","RUC, nombre (anonimizado), tipo de proveedor","RUC","Tipo 1"],
 ["DimCategoria","Bienes, servicios, obras","mainProcurementCategory","Tipo 1"],
 ["DimMetodo","Método (licitación, adjudicación simplificada, contratación directa…), indicador Competitivo","procurementMethodDetails","Tipo 1"],
 ["DimEstadoContrato","Estado y detalle del estado","status + statusDetails","Tipo 1"],
 ["DimMoneda","PEN, USD, EUR, GBP…","Código ISO","Tipo 1"]],[3.2,7.4,3.6,2],sz=9)
P("Todas las dimensiones incluyen un miembro 'Desconocido' o 'Sin fecha' para evitar claves nulas en los hechos, además de la columna Activo para la eliminación lógica.",sz=11)
d.add_heading("5.4 Hechos y métricas",2)
T(["Hecho","Métrica","Cálculo desde la fuente","Aditividad"],[
 ["FactConvocatoria","ValorReferencialPEN","main.tender_value_amount_PEN","Aditiva"],
 ["FactConvocatoria","NumPostores","main.tender_numberOfTenderers","Aditiva (se promedia)"],
 ["FactConvocatoria","DiasConvocatoria","fin de ofertas − publicación","Semiaditiva (se promedia)"],
 ["FactConvocatoria","MontoAdjudicadoPEN","Σ awards.value × tipo de cambio","Aditiva"],
 ["FactContrato","MontoContratoPEN","contracts.value_amount × tipo de cambio (1 si PEN)","Aditiva"],
 ["FactContrato","PlazoDias","period_endDate − period_startDate","Se promedia"],
 ["FactContrato","DiasConvocatoriaAFirma","dateSigned − tender_datePublished","Se promedia"],
 ["Indicadores","% directa, % concentración, crecimiento","Razones calculadas en el tablero","No aditivas"]],[3.2,3.6,6.4,3],sz=9)
d.add_heading("5.5 Tipo de esquema y justificación",2)
P("Se eligió una constelación de hechos: dos procesos con granos distintos comparten las dimensiones Fecha, Entidad, Categoría y Método, lo que permite cruzar competencia (convocatoria) con monto (contrato) sin duplicar dimensiones. Se evitó el copo de nieve para simplificar las consultas del tablero; las jerarquías (año-trimestre-mes) están desnormalizadas en DimFecha.")
d.add_heading("5.6 Modelo dimensional del Data Warehouse",2)
IMG("img/dw.png",6.3,"Figura 3. Modelo dimensional de DW_OECE (constelación de dos hechos).")
# 6
d.add_heading("6. Diseño del Data Mart",1)
d.add_heading("6.1 Área usuaria y alcance",2)
P("El Data Mart DM_Monitoreo atiende a la Unidad de Monitoreo y Transparencia de Contrataciones (jefatura y analistas) y responde los requerimientos RA-01 a RA-08 de la tabla 4.1. Su alcance son los contratos firmados y convocatorias publicadas entre 2022 y 2026.")
d.add_heading("6.2 Relación entre el Data Warehouse y el Data Mart",2)
T(["Criterio","Data Warehouse","Data Mart de Monitoreo"],[
 ["Alcance","Convocatorias y contratos 2012-2027, sin filtro","Convocatorias y contratos 2022-2026, solo registros activos"],
 ["Fuente de carga","Staging (STG_OECE)","Solo el Data Warehouse (DW_OECE)"],
 ["Grano","Un proceso / un contrato","Mes × entidad × proveedor × categoría × método (contratos); mes × entidad × categoría × método (convocatorias)"],
 ["Medidas","Montos y plazos por registro","Sumas y conteos reaggregables (promedios = suma / conteo)"],
 ["Usuarios","Analistas de varias áreas","Jefatura de monitoreo y transparencia"]],[3,5.6,7.6],sz=9)
P("Se eligió un hecho agregado mensual porque los indicadores se consultan por mes y el tablero se acelera; se conserva el proveedor en el grano para obtener rankings y concentración. Para evitar medidas no aditivas, los promedios se guardan como suma y conteo (por ejemplo SumaDiasConvocatoriaAFirma y NumContratosConDias).")
d.add_heading("6.3 Modelo estrella del Data Mart",2)
IMG("img/dm.png",5.9,"Figura 4. Modelo estrella de DM_Monitoreo (dos hechos agregados y cinco dimensiones).")
P("DimMes sustituye a DimFecha porque el grano es mensual; DimEntidad y DimProveedor responden RA-07 y RA-04; DimCategoria y DimMetodo, RA-02, RA-03 y RA-05.",sz=11)
# 7
d.add_heading("7. Diseño físico",1)
d.add_heading("7.1 DBMS y arquitectura de bases de datos",2)
P("Gestor: PostgreSQL 16, accedido con SQLAlchemy (el gestor se define solo en la URL de config.py). Tres bases independientes: STG_OECE (copia de 7 tablas fuente con columnas de auditoría source_year y load_ts), DW_OECE y DM_Monitoreo. Los modelos se definen una sola vez en modelos.py con SQLAlchemy Core y generar_ddl.py los exporta como scripts CREATE TABLE para cualquier gestor. El DM lee solo del DW (con pandas), por lo que es dependiente.")
d.add_heading("7.2 Implementación del modelo dimensional",2)
P("Los scripts DDL completos, generados desde modelos.py, están en el anexo 12.2 (archivos sql/01 a sql/03). Ejemplo de FactContrato: clave primaria bigserial ContratoKey, 8 claves foráneas, clave única (Ocid, ContratoId) y columnas de auditoría Activo y FechaCarga.")
d.add_heading("7.3 Diccionario de datos (extracto)",2)
T(["Tabla","Atributo","PK","FK","NULL","Tipo","Descripción"],[
 ["DimEntidad","EntidadKey","Sí","","No","serial","Clave subrogada"],
 ["DimEntidad","EntidadCodigo","","","No","varchar(40)","Clave de negocio (buyer.id)"],
 ["DimProveedor","ProveedorRUC","","","No","varchar(40)","Clave de negocio, única"],
 ["FactContrato","EntidadKey","","Sí","No","int","Referencia a DimEntidad (versión vigente)"],
 ["FactContrato","MontoContratoPEN","","","Sí","numeric(18,2)","Monto en soles (nulo si la fuente no informa monto)"],
 ["FactConvocatoria","Ocid","","","No","varchar(80)","Clave degenerada, única"]],[3,3.4,1,1,1.1,2.6,4.6],sz=9)
# 8
d.add_heading("8. Proceso ETL",1)
d.add_heading("8.1 Herramienta de software",2)
P("Los procesos ETL se implementaron en Python 3 solo con pandas (extracción y transformación), numpy (cálculos vectorizados), SQLAlchemy (conexión, modelos y carga) y matplotlib (tablero), en lugar de SSIS o Pentaho; los scripts están en el anexo 12.3. La estructura (extraer, transformar, cargar, dimensiones antes que hechos, lookups con merge) es la misma que en las herramientas gráficas.")
d.add_heading("8.2 Matriz fuente-destino",2)
T(["Destino","Origen","Transformación aplicada"],[
 ["DW.DimEntidad.EntidadNombre","main.buyer_name","Último nombre por buyer_id (según release_date); SCD tipo 2"],
 ["DW.DimProveedor.ProveedorNombre","awards_suppliers.name","Si RUC empieza con 10: PERSONA NATURAL + md5; SCD tipo 1"],
 ["DW.FactConvocatoria.FechaPublicacionKey","main.tender_datePublished","Conversión a entero AAAAMMDD; 0 si falta o está fuera de rango"],
 ["DW.FactConvocatoria.EntidadKey","main.buyer_id","Lookup sobre DimEntidad vigente"],
 ["DW.FactContrato.ProveedorKey","contracts.awardID → awards_suppliers","Un proveedor por adjudicación (menor RUC en consorcios); 'Sin proveedor' si no hay"],
 ["DW.FactContrato.MontoContratoPEN","contracts.value_amount, exchangeRates","× tipo de cambio de la fuente; si falta, promedio por moneda"],
 ["DM.FactContratoMes.MontoContratoPEN","DW.FactContrato","Suma por mes de firma, entidad, proveedor, categoría y método"]],[5.2,4.6,6.4],sz=9)
d.add_heading("8.3 Diseño de paquetes y transformaciones",2)
T(["Etapa","Script","Tareas principales"],[
 ["1. Staging","etl_01_staging.py","Lectura por bloques con pandas.read_csv y to_sql a STG_OECE (7 tablas); --append agrega un año"],
 ["2. Data Warehouse","etl_02_dw.py","Recrea tablas; carga dimensiones (limpieza, anonimización, claves subrogadas) y luego hechos con lookups (merge)"],
 ["3. Data Mart","etl_03_dm.py","Lee el DW; filtra 2022-2026; agrega por mes con groupby"],
 ["4. Incremental","etl_02_dw.py --incremental","Carga 2026 en STG; SCD1/SCD2 en dimensiones; inserta hechos nuevos; baja lógica (Activo=false)"]],[3,4.6,8.6],sz=9)
P("La carga incremental real consistió en agregar el archivo 2026 (publicado por el OECE en oct-2026) al staging y reejecutar el DW y el DM: se añadieron 134 917 procesos, 104 571 contratos, 42 entidades y 41 763 proveedores, y se actualizaron 120 registros de dimensiones (SCD). En una prueba controlada sobre una copia se renombró una entidad (generó una segunda fila de DimEntidad con la primera cerrada: SCD2), se renombró un proveedor (se sobrescribió: SCD1) y se eliminaron 5 contratos de la fuente (quedaron con Activo = false).")
d.add_heading("8.4 Resultados y validación",2)
rows=list(csv.DictReader(open("../salida/validacion_2023_2024_2025_2026.csv",encoding="utf-8-sig")))
def n(x):
    if x in ("","None","nan",None): return "No aplica"
    try: v=float(x); return f"{v:,.0f}".replace(","," ") if abs(v)>=1000 else f"{v:g}"
    except: return x
T(["Control","Fuente","STG","DW","DM","¿Cuadra?"],[[r["Control"],n(r["Fuente"]) if r["Fuente"][:1]!="(" else r["Fuente"],n(r["STG"]),n(r["DW"]),n(r["DM"]),r["Cuadra"]] for r in rows],[5.2,2.6,2.3,2.3,2.3,1.5],sz=8.5)
P("Todos los controles cuadran (tolerancia de S/ 1). El DM contiene menos filas que el DW porque solo carga 2022-2026 y agrega; por eso se comparan las cuentas del mismo rango. 6 493 contratos (1,9 %) no tienen monto en la fuente y quedan con MontoContratoPEN nulo.",sz=11)
# 9
d.add_heading("9. Explotación de la información",1)
d.add_heading("9.1 Tablero de indicadores",2)
P("El tablero se construyó con matplotlib sobre el Data Mart (tablero.py genera salida/tablero_monitoreo.png y un PNG por indicador). Cada KPI se calcula con pandas desde DM_Monitoreo; la fórmula equivalente en DAX se muestra en la tabla siguiente por si se desea replicarlo en Power BI.")
IMG("../salida/tablero_monitoreo.png",5.5,"Figura 5. Tablero de indicadores (matplotlib) sobre DM_Monitoreo.")
T(["KPI","Fórmula (DAX)","Req."],[
 ["Monto contratado","SUM(FactContratoMes[MontoContratoPEN])","RA-01"],
 ["% crecimiento interanual","DIVIDE([Monto]-[Monto Año Ant.],[Monto Año Ant.])","RA-08"],
 ["% monto por contratación directa","DIVIDE(CALCULATE([Monto],DimMetodo[Competitivo]=FALSE()),[Monto])","RA-03"],
 ["% concentración top 10 proveedores","DIVIDE([Monto Top10],CALCULATE([Monto],ALL(DimProveedor)))","RA-04"],
 ["Postores promedio","DIVIDE(SUM(SumaPostores),SUM(NumConvocatoriasConPostores))","RA-05"],
 ["Días convocatoria a firma","DIVIDE(SUM(SumaDiasConvocatoriaAFirma),SUM(NumContratosConDias))","RA-06"]],[4.6,9.6,2],sz=9)
d.add_heading("9.2 Interpretación y recomendaciones",2)
P("Los resultados de 2025 (año completo) muestran un monto contratado de S/ 81 372 millones, 25,5 % más que en 2024 (S/ 64 862 M), impulsado por obras (+62 %). La contratación directa pasó de 7,5 % del monto en 2024 a 11,3 % en 2025 y a 19,0 % en 2026 (parcial). La competencia es moderada: 13,3 postores por convocatoria en 2025, bajo los 14,3 de 2024. El mercado de proveedores está fragmentado: los 10 mayores proveedores de 2023-2025 concentran solo 4,3 % del monto. El plazo de convocatoria a firma subió de 39 días en 2023 a 66 días en 2025 (la cifra de 2026, 133 días, está sesgada porque solo incluye contratos ya firmados).")
P("Decisiones que podría tomar la organización:",b=True,al="l")
B("Auditar con prioridad las entidades y categorías con mayor crecimiento de la contratación directa, que pasó de 7,5 % (2024) a 19,0 % (2026 parcial).")
B("Atender el aumento del tiempo de convocatoria a firma (de 39 a 66 días) con una revisión de cuellos de botella por entidad y método.")
B("Dar seguimiento a los procesos con pocos postores, por ejemplo un monitoreo mensual con alerta cuando el promedio baje de 10, para promover la competencia.")
B("Priorizar la supervisión de obras, categoría que más creció (de S/ 29 519 M en 2024 a S/ 47 822 M en 2025).")
# 10
d.add_heading("10. Conclusiones y trabajo futuro",1)
B("Se implementó un DW en constelación (2 hechos, 7 dimensiones, 4 conformadas) y un DM dependiente, con claves subrogadas y eliminación lógica; los conteos y totales cuadran entre fuente, STG, DW y DM.")
B("La carga incremental con el archivo 2026 (134 917 procesos nuevos en 57 s) demostró SCD tipo 1 y tipo 2 y la baja lógica.")
B("Limitación: cada proceso aparece solo en el archivo anual de su última actualización, por lo que 2022 y años previos están incompletos. Comparar 2023-2025.")
B("Trabajo futuro: agregar tender_tenderers (postores) como tercer hecho, dimensión geográfica de las entidades, cubo OLAP y un tablero interactivo (Power BI o Dash).")
# 11
d.add_heading("11. Referencias bibliográficas",1)
for r in ["Kimball, R., & Ross, M. (2013). The data warehouse toolkit: The definitive guide to dimensional modeling (3.ª ed.). Wiley.",
 "Open Contracting Partnership. (2026). Perú: Organismo Especializado para las Contrataciones Públicas Eficientes (OECE) [Conjunto de datos, publicación 135]. Open Contracting Data Registry. https://data.open-contracting.org/es/publication/135 (CC BY 4.0)",
 "Organismo Especializado para las Contrataciones Públicas Eficientes. (s. f.). Portal de contrataciones abiertas. https://contratacionesabiertas.oece.gob.pe/",
 "Open Contracting Partnership. (s. f.). Open Contracting Data Standard: Documentation. https://standard.open-contracting.org/"]:
    p=P(r,al="l"); p.paragraph_format.left_indent=Cm(1); p.paragraph_format.first_line_indent=Cm(-1)
# 12
d.add_heading("12. Anexos",1)
for r in ["12.1 Carta de autorización: no aplica por ser datos abiertos con licencia CC BY 4.0; adjuntar la constancia de la licencia.",
 "12.2 Scripts DDL: sql/01_ddl_stg_oece.sql, 02_ddl_dw_oece.sql y 03_ddl_dm_monitoreo.sql, generados desde modelos.py (en GRUPO_01_PA01.zip).",
 "12.3 Proyecto Python (config.py, modelos.py, etl_01..03, validar.py, tablero.py, ejecutar_todo.py) y tablero (salida/tablero_monitoreo.png).",
 "12.4 Rúbrica del atributo del graduado Conocimientos de Computación, por integrante (Anexo 02 de la guía): pendiente de completar por el equipo."]: B(r)
d.save("GRUPO_01_PA01.docx"); print("ok")
