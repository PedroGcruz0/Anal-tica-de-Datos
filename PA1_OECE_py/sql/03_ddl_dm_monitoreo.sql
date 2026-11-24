-- 03_ddl_dm_monitoreo: generado desde modelos.py con SQLAlchemy (postgresql)

CREATE TABLE "DimCategoria" (
	"CategoriaKey" INTEGER NOT NULL, 
	"CategoriaNombre" VARCHAR(30), 
	PRIMARY KEY ("CategoriaKey")
);

CREATE TABLE "DimEntidad" (
	"EntidadKey" INTEGER NOT NULL, 
	"EntidadCodigo" VARCHAR(40), 
	"EntidadNombre" VARCHAR(300), 
	PRIMARY KEY ("EntidadKey")
);

CREATE TABLE "DimMes" (
	"MesKey" INTEGER NOT NULL, 
	"Anio" INTEGER, 
	"Trimestre" INTEGER, 
	"Mes" INTEGER, 
	"NombreMes" VARCHAR(15), 
	"PrimerDia" DATE, 
	PRIMARY KEY ("MesKey")
);

CREATE TABLE "DimMetodo" (
	"MetodoKey" INTEGER NOT NULL, 
	"MetodoNombre" VARCHAR(120), 
	"MetodoGeneral" VARCHAR(30), 
	"Competitivo" BOOLEAN, 
	PRIMARY KEY ("MetodoKey")
);

CREATE TABLE "DimProveedor" (
	"ProveedorKey" INTEGER NOT NULL, 
	"ProveedorRUC" VARCHAR(40), 
	"ProveedorNombre" VARCHAR(300), 
	"TipoProveedor" VARCHAR(30), 
	PRIMARY KEY ("ProveedorKey")
);

CREATE TABLE "FactContratoMes" (
	"MesKey" INTEGER NOT NULL, 
	"EntidadKey" INTEGER NOT NULL, 
	"ProveedorKey" INTEGER NOT NULL, 
	"CategoriaKey" INTEGER NOT NULL, 
	"MetodoKey" INTEGER NOT NULL, 
	"NumContratos" INTEGER, 
	"MontoContratoPEN" NUMERIC(18, 2), 
	"SumaPlazoDias" BIGINT, 
	"SumaDiasConvocatoriaAFirma" BIGINT, 
	"NumContratosConPlazo" INTEGER, 
	"NumContratosConDias" INTEGER, 
	PRIMARY KEY ("MesKey", "EntidadKey", "ProveedorKey", "CategoriaKey", "MetodoKey"), 
	FOREIGN KEY("MesKey") REFERENCES "DimMes" ("MesKey"), 
	FOREIGN KEY("EntidadKey") REFERENCES "DimEntidad" ("EntidadKey"), 
	FOREIGN KEY("ProveedorKey") REFERENCES "DimProveedor" ("ProveedorKey"), 
	FOREIGN KEY("CategoriaKey") REFERENCES "DimCategoria" ("CategoriaKey"), 
	FOREIGN KEY("MetodoKey") REFERENCES "DimMetodo" ("MetodoKey")
);

CREATE TABLE "FactConvocatoriaMes" (
	"MesKey" INTEGER NOT NULL, 
	"EntidadKey" INTEGER NOT NULL, 
	"CategoriaKey" INTEGER NOT NULL, 
	"MetodoKey" INTEGER NOT NULL, 
	"NumConvocatorias" INTEGER, 
	"ValorReferencialPEN" NUMERIC(18, 2), 
	"SumaPostores" BIGINT, 
	"NumConvocatoriasConPostores" INTEGER, 
	"NumAdjudicadas" INTEGER, 
	"MontoAdjudicadoPEN" NUMERIC(18, 2), 
	"ValorRefAdjudicadasPEN" NUMERIC(18, 2), 
	PRIMARY KEY ("MesKey", "EntidadKey", "CategoriaKey", "MetodoKey"), 
	FOREIGN KEY("MesKey") REFERENCES "DimMes" ("MesKey"), 
	FOREIGN KEY("EntidadKey") REFERENCES "DimEntidad" ("EntidadKey"), 
	FOREIGN KEY("CategoriaKey") REFERENCES "DimCategoria" ("CategoriaKey"), 
	FOREIGN KEY("MetodoKey") REFERENCES "DimMetodo" ("MetodoKey")
);
