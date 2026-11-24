-- 02_ddl_dw_oece: generado desde modelos.py con SQLAlchemy (postgresql)

CREATE TABLE "DimCategoria" (
	"CategoriaKey" SERIAL NOT NULL, 
	"CategoriaCodigo" VARCHAR(20) NOT NULL, 
	"CategoriaNombre" VARCHAR(30) NOT NULL, 
	"Activo" BOOLEAN NOT NULL, 
	PRIMARY KEY ("CategoriaKey"), 
	UNIQUE ("CategoriaCodigo")
);

CREATE TABLE "DimEntidad" (
	"EntidadKey" SERIAL NOT NULL, 
	"EntidadCodigo" VARCHAR(40) NOT NULL, 
	"EntidadNombre" VARCHAR(300) NOT NULL, 
	"FechaInicio" DATE NOT NULL, 
	"FechaFin" DATE, 
	"EsVigente" BOOLEAN NOT NULL, 
	"Activo" BOOLEAN NOT NULL, 
	"FechaCarga" TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY ("EntidadKey")
);

CREATE INDEX ix_dimentidad_bk ON "DimEntidad" ("EntidadCodigo", "EsVigente");

CREATE TABLE "DimEstadoContrato" (
	"EstadoKey" SERIAL NOT NULL, 
	"Estado" VARCHAR(30) NOT NULL, 
	"EstadoDetalle" VARCHAR(80) NOT NULL, 
	PRIMARY KEY ("EstadoKey"), 
	UNIQUE ("Estado", "EstadoDetalle")
);

CREATE TABLE "DimFecha" (
	"FechaKey" INTEGER NOT NULL, 
	"Fecha" DATE, 
	"Anio" INTEGER, 
	"Trimestre" INTEGER, 
	"Mes" INTEGER, 
	"NombreMes" VARCHAR(15), 
	"AnioMes" INTEGER, 
	"Dia" INTEGER, 
	"DiaSemana" INTEGER, 
	"NombreDia" VARCHAR(12), 
	"EsFinSemana" BOOLEAN, 
	PRIMARY KEY ("FechaKey")
);

CREATE TABLE "DimMetodo" (
	"MetodoKey" SERIAL NOT NULL, 
	"MetodoNombre" VARCHAR(120) NOT NULL, 
	"MetodoGeneral" VARCHAR(30) NOT NULL, 
	"Competitivo" BOOLEAN NOT NULL, 
	"Activo" BOOLEAN NOT NULL, 
	PRIMARY KEY ("MetodoKey"), 
	UNIQUE ("MetodoNombre")
);

CREATE TABLE "DimMoneda" (
	"MonedaKey" SERIAL NOT NULL, 
	"MonedaCodigo" VARCHAR(5) NOT NULL, 
	PRIMARY KEY ("MonedaKey"), 
	UNIQUE ("MonedaCodigo")
);

CREATE TABLE "DimProveedor" (
	"ProveedorKey" SERIAL NOT NULL, 
	"ProveedorRUC" VARCHAR(40) NOT NULL, 
	"ProveedorNombre" VARCHAR(300) NOT NULL, 
	"TipoProveedor" VARCHAR(30) NOT NULL, 
	"Activo" BOOLEAN NOT NULL, 
	"FechaCarga" TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	"FechaActualizacion" TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY ("ProveedorKey"), 
	UNIQUE ("ProveedorRUC")
);

CREATE TABLE "EtlLog" (
	"LogId" SERIAL NOT NULL, 
	"Proceso" VARCHAR(60), 
	"Inicio" TIMESTAMP WITHOUT TIME ZONE, 
	"Fin" TIMESTAMP WITHOUT TIME ZONE, 
	"FilasInsertadas" BIGINT, 
	"FilasActualizadas" BIGINT, 
	"FilasDesactivadas" BIGINT, 
	PRIMARY KEY ("LogId")
);

CREATE TABLE "FactContrato" (
	"ContratoKey" BIGSERIAL NOT NULL, 
	"Ocid" VARCHAR(80) NOT NULL, 
	"ContratoId" VARCHAR(30) NOT NULL, 
	"FechaFirmaKey" INTEGER NOT NULL, 
	"FechaFinKey" INTEGER NOT NULL, 
	"EntidadKey" INTEGER NOT NULL, 
	"ProveedorKey" INTEGER NOT NULL, 
	"CategoriaKey" INTEGER NOT NULL, 
	"MetodoKey" INTEGER NOT NULL, 
	"EstadoKey" INTEGER NOT NULL, 
	"MonedaKey" INTEGER NOT NULL, 
	"MontoOriginal" NUMERIC(18, 2), 
	"TipoCambio" NUMERIC(12, 6), 
	"MontoContratoPEN" NUMERIC(18, 2), 
	"PlazoDias" INTEGER, 
	"DiasConvocatoriaAFirma" INTEGER, 
	"Activo" BOOLEAN NOT NULL, 
	"FechaCarga" TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY ("ContratoKey"), 
	UNIQUE ("Ocid", "ContratoId"), 
	FOREIGN KEY("FechaFirmaKey") REFERENCES "DimFecha" ("FechaKey"), 
	FOREIGN KEY("FechaFinKey") REFERENCES "DimFecha" ("FechaKey"), 
	FOREIGN KEY("EntidadKey") REFERENCES "DimEntidad" ("EntidadKey"), 
	FOREIGN KEY("ProveedorKey") REFERENCES "DimProveedor" ("ProveedorKey"), 
	FOREIGN KEY("CategoriaKey") REFERENCES "DimCategoria" ("CategoriaKey"), 
	FOREIGN KEY("MetodoKey") REFERENCES "DimMetodo" ("MetodoKey"), 
	FOREIGN KEY("EstadoKey") REFERENCES "DimEstadoContrato" ("EstadoKey"), 
	FOREIGN KEY("MonedaKey") REFERENCES "DimMoneda" ("MonedaKey")
);

CREATE INDEX ix_fk_fecha ON "FactContrato" ("FechaFirmaKey");

CREATE TABLE "FactConvocatoria" (
	"ConvocatoriaKey" BIGSERIAL NOT NULL, 
	"Ocid" VARCHAR(80) NOT NULL, 
	"TenderId" VARCHAR(30), 
	"FechaPublicacionKey" INTEGER NOT NULL, 
	"FechaCierreKey" INTEGER NOT NULL, 
	"EntidadKey" INTEGER NOT NULL, 
	"CategoriaKey" INTEGER NOT NULL, 
	"MetodoKey" INTEGER NOT NULL, 
	"ValorReferencialPEN" NUMERIC(18, 2), 
	"NumPostores" INTEGER, 
	"NumItems" INTEGER, 
	"DiasConvocatoria" INTEGER, 
	"NumAdjudicaciones" INTEGER, 
	"MontoAdjudicadoPEN" NUMERIC(18, 2), 
	"Activo" BOOLEAN NOT NULL, 
	"FechaCarga" TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY ("ConvocatoriaKey"), 
	UNIQUE ("Ocid"), 
	FOREIGN KEY("FechaPublicacionKey") REFERENCES "DimFecha" ("FechaKey"), 
	FOREIGN KEY("FechaCierreKey") REFERENCES "DimFecha" ("FechaKey"), 
	FOREIGN KEY("EntidadKey") REFERENCES "DimEntidad" ("EntidadKey"), 
	FOREIGN KEY("CategoriaKey") REFERENCES "DimCategoria" ("CategoriaKey"), 
	FOREIGN KEY("MetodoKey") REFERENCES "DimMetodo" ("MetodoKey")
);

CREATE INDEX ix_fc_fecha ON "FactConvocatoria" ("FechaPublicacionKey");
