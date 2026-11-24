"""Modelos físicos (DDL) de STG_OECE, DW_OECE y DM_Monitoreo con SQLAlchemy Core.
'python generar_ddl.py' exporta estos modelos a scripts .sql (carpeta sql/)."""
from sqlalchemy import (MetaData, Table, Column, Integer, BigInteger, String, Text, Float, Numeric, Boolean,
                        Date, DateTime, ForeignKey, UniqueConstraint, Index, func)

PK_BIG = BigInteger().with_variant(Integer, "sqlite")   # SQLite solo autoincrementa INTEGER PRIMARY KEY
MONTO = Numeric(18, 2)

# ------------------------------------------------------------------ STG_OECE
stg_md = MetaData()
def _stg(nombre, *cols):
    return Table(nombre, stg_md, *cols, Column("source_year", Integer), Column("load_ts", DateTime, server_default=func.now()))
_stg("stg_main", Column("ocid", Text), Column("release_date", Text), Column("buyer_id", Text), Column("buyer_name", Text),
     Column("tender_id", Text), Column("tender_title", Text), Column("main_category", Text), Column("method_details", Text),
     Column("method_general", Text), Column("date_published", Text), Column("num_tenderers", Float), Column("value_amount", Float),
     Column("value_currency", Text), Column("value_amount_pen", Float), Column("tender_end_date", Text), Column("budget_description", Text))
_stg("stg_tender_items", Column("main_ocid", Text), Column("item_id", Text), Column("position", Text), Column("quantity", Float),
     Column("total_value_amount", Float), Column("total_value_currency", Text), Column("classification_scheme", Text))
_stg("stg_awards", Column("award_id", Text), Column("award_date", Text), Column("value_amount", Float), Column("value_currency", Text), Column("main_ocid", Text))
_stg("stg_awards_fx", Column("rate", Float), Column("currency", Text), Column("main_ocid", Text), Column("awards_id", Text))
_stg("stg_awards_suppliers", Column("supplier_id", Text), Column("supplier_name", Text), Column("main_ocid", Text), Column("awards_id", Text))
_stg("stg_contracts", Column("contract_id", Text), Column("status_details", Text), Column("date_signed", Text), Column("status", Text),
     Column("award_id", Text), Column("value_amount", Float), Column("value_currency", Text), Column("period_end", Text),
     Column("period_start", Text), Column("main_ocid", Text))
_stg("stg_contracts_fx", Column("rate", Float), Column("currency", Text), Column("main_ocid", Text), Column("contracts_id", Text))

# ------------------------------------------------------------------ DW_OECE
dw_md = MetaData()
DimFecha = Table("DimFecha", dw_md,
    Column("FechaKey", Integer, primary_key=True, autoincrement=False), Column("Fecha", Date), Column("Anio", Integer), Column("Trimestre", Integer),
    Column("Mes", Integer), Column("NombreMes", String(15)), Column("AnioMes", Integer), Column("Dia", Integer), Column("DiaSemana", Integer),
    Column("NombreDia", String(12)), Column("EsFinSemana", Boolean))
DimEntidad = Table("DimEntidad", dw_md,                       # SCD tipo 2 sobre EntidadNombre
    Column("EntidadKey", Integer, primary_key=True, autoincrement=True), Column("EntidadCodigo", String(40), nullable=False),
    Column("EntidadNombre", String(300), nullable=False), Column("FechaInicio", Date, nullable=False), Column("FechaFin", Date),
    Column("EsVigente", Boolean, nullable=False, default=True), Column("Activo", Boolean, nullable=False, default=True),
    Column("FechaCarga", DateTime, server_default=func.now()), Index("ix_dimentidad_bk", "EntidadCodigo", "EsVigente"))
DimProveedor = Table("DimProveedor", dw_md,                   # SCD tipo 1
    Column("ProveedorKey", Integer, primary_key=True, autoincrement=True), Column("ProveedorRUC", String(40), nullable=False, unique=True),
    Column("ProveedorNombre", String(300), nullable=False), Column("TipoProveedor", String(30), nullable=False),
    Column("Activo", Boolean, nullable=False, default=True), Column("FechaCarga", DateTime, server_default=func.now()), Column("FechaActualizacion", DateTime))
DimCategoria = Table("DimCategoria", dw_md,
    Column("CategoriaKey", Integer, primary_key=True, autoincrement=True), Column("CategoriaCodigo", String(20), nullable=False, unique=True),
    Column("CategoriaNombre", String(30), nullable=False), Column("Activo", Boolean, nullable=False, default=True))
DimMetodo = Table("DimMetodo", dw_md,
    Column("MetodoKey", Integer, primary_key=True, autoincrement=True), Column("MetodoNombre", String(120), nullable=False, unique=True),
    Column("MetodoGeneral", String(30), nullable=False), Column("Competitivo", Boolean, nullable=False), Column("Activo", Boolean, nullable=False, default=True))
DimEstadoContrato = Table("DimEstadoContrato", dw_md,
    Column("EstadoKey", Integer, primary_key=True, autoincrement=True), Column("Estado", String(30), nullable=False),
    Column("EstadoDetalle", String(80), nullable=False), UniqueConstraint("Estado", "EstadoDetalle"))
DimMoneda = Table("DimMoneda", dw_md,
    Column("MonedaKey", Integer, primary_key=True, autoincrement=True), Column("MonedaCodigo", String(5), nullable=False, unique=True))
FactConvocatoria = Table("FactConvocatoria", dw_md,           # grano: un proceso de selección (ocid)
    Column("ConvocatoriaKey", PK_BIG, primary_key=True, autoincrement=True), Column("Ocid", String(80), nullable=False, unique=True),
    Column("TenderId", String(30)),
    Column("FechaPublicacionKey", Integer, ForeignKey("DimFecha.FechaKey"), nullable=False),
    Column("FechaCierreKey", Integer, ForeignKey("DimFecha.FechaKey"), nullable=False),
    Column("EntidadKey", Integer, ForeignKey("DimEntidad.EntidadKey"), nullable=False),
    Column("CategoriaKey", Integer, ForeignKey("DimCategoria.CategoriaKey"), nullable=False),
    Column("MetodoKey", Integer, ForeignKey("DimMetodo.MetodoKey"), nullable=False),
    Column("ValorReferencialPEN", MONTO), Column("NumPostores", Integer), Column("NumItems", Integer), Column("DiasConvocatoria", Integer),
    Column("NumAdjudicaciones", Integer), Column("MontoAdjudicadoPEN", MONTO),
    Column("Activo", Boolean, nullable=False, default=True), Column("FechaCarga", DateTime, server_default=func.now()),
    Index("ix_fc_fecha", "FechaPublicacionKey"))
FactContrato = Table("FactContrato", dw_md,                   # grano: un contrato (ocid + id de contrato)
    Column("ContratoKey", PK_BIG, primary_key=True, autoincrement=True), Column("Ocid", String(80), nullable=False), Column("ContratoId", String(30), nullable=False),
    Column("FechaFirmaKey", Integer, ForeignKey("DimFecha.FechaKey"), nullable=False),
    Column("FechaFinKey", Integer, ForeignKey("DimFecha.FechaKey"), nullable=False),
    Column("EntidadKey", Integer, ForeignKey("DimEntidad.EntidadKey"), nullable=False),
    Column("ProveedorKey", Integer, ForeignKey("DimProveedor.ProveedorKey"), nullable=False),
    Column("CategoriaKey", Integer, ForeignKey("DimCategoria.CategoriaKey"), nullable=False),
    Column("MetodoKey", Integer, ForeignKey("DimMetodo.MetodoKey"), nullable=False),
    Column("EstadoKey", Integer, ForeignKey("DimEstadoContrato.EstadoKey"), nullable=False),
    Column("MonedaKey", Integer, ForeignKey("DimMoneda.MonedaKey"), nullable=False),
    Column("MontoOriginal", MONTO), Column("TipoCambio", Numeric(12, 6)), Column("MontoContratoPEN", MONTO),
    Column("PlazoDias", Integer), Column("DiasConvocatoriaAFirma", Integer),
    Column("Activo", Boolean, nullable=False, default=True), Column("FechaCarga", DateTime, server_default=func.now()),
    UniqueConstraint("Ocid", "ContratoId"), Index("ix_fk_fecha", "FechaFirmaKey"))
EtlLog = Table("EtlLog", dw_md,
    Column("LogId", Integer, primary_key=True, autoincrement=True), Column("Proceso", String(60)), Column("Inicio", DateTime), Column("Fin", DateTime),
    Column("FilasInsertadas", BigInteger), Column("FilasActualizadas", BigInteger), Column("FilasDesactivadas", BigInteger))

# ------------------------------------------------------------------ DM_Monitoreo
dm_md = MetaData()
Table("DimMes", dm_md, Column("MesKey", Integer, primary_key=True, autoincrement=False), Column("Anio", Integer), Column("Trimestre", Integer),
      Column("Mes", Integer), Column("NombreMes", String(15)), Column("PrimerDia", Date))
Table("DimEntidad", dm_md, Column("EntidadKey", Integer, primary_key=True, autoincrement=False), Column("EntidadCodigo", String(40)), Column("EntidadNombre", String(300)))
Table("DimProveedor", dm_md, Column("ProveedorKey", Integer, primary_key=True, autoincrement=False), Column("ProveedorRUC", String(40)),
      Column("ProveedorNombre", String(300)), Column("TipoProveedor", String(30)))
Table("DimCategoria", dm_md, Column("CategoriaKey", Integer, primary_key=True, autoincrement=False), Column("CategoriaNombre", String(30)))
Table("DimMetodo", dm_md, Column("MetodoKey", Integer, primary_key=True, autoincrement=False), Column("MetodoNombre", String(120)),
      Column("MetodoGeneral", String(30)), Column("Competitivo", Boolean))
Table("FactContratoMes", dm_md,                               # grano: mes de firma x entidad x proveedor x categoría x método
    Column("MesKey", Integer, ForeignKey("DimMes.MesKey"), primary_key=True), Column("EntidadKey", Integer, ForeignKey("DimEntidad.EntidadKey"), primary_key=True),
    Column("ProveedorKey", Integer, ForeignKey("DimProveedor.ProveedorKey"), primary_key=True),
    Column("CategoriaKey", Integer, ForeignKey("DimCategoria.CategoriaKey"), primary_key=True),
    Column("MetodoKey", Integer, ForeignKey("DimMetodo.MetodoKey"), primary_key=True),
    Column("NumContratos", Integer), Column("MontoContratoPEN", MONTO), Column("SumaPlazoDias", BigInteger),
    Column("SumaDiasConvocatoriaAFirma", BigInteger), Column("NumContratosConPlazo", Integer), Column("NumContratosConDias", Integer))
Table("FactConvocatoriaMes", dm_md,                           # grano: mes de publicación x entidad x categoría x método
    Column("MesKey", Integer, ForeignKey("DimMes.MesKey"), primary_key=True), Column("EntidadKey", Integer, ForeignKey("DimEntidad.EntidadKey"), primary_key=True),
    Column("CategoriaKey", Integer, ForeignKey("DimCategoria.CategoriaKey"), primary_key=True),
    Column("MetodoKey", Integer, ForeignKey("DimMetodo.MetodoKey"), primary_key=True),
    Column("NumConvocatorias", Integer), Column("ValorReferencialPEN", MONTO), Column("SumaPostores", BigInteger),
    Column("NumConvocatoriasConPostores", Integer), Column("NumAdjudicadas", Integer), Column("MontoAdjudicadoPEN", MONTO),
    Column("ValorRefAdjudicadasPEN", MONTO))
