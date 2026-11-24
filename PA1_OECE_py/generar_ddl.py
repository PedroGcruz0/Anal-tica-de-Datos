"""Exporta los modelos de modelos.py a scripts DDL (CREATE TABLE) en sql/. Útil para el anexo 12.2 del informe.
Uso: python generar_ddl.py [dialecto]   (sqlite | postgresql | mysql | mssql | oracle; por defecto postgresql)"""
import sys
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import postgresql, sqlite, mysql, mssql, oracle
import modelos
from config import BASE
D = {"postgresql": postgresql, "sqlite": sqlite, "mysql": mysql, "mssql": mssql, "oracle": oracle}
dial = (D[sys.argv[1]] if len(sys.argv) > 1 else postgresql).dialect()
for nombre, md in (("01_ddl_stg_oece", modelos.stg_md), ("02_ddl_dw_oece", modelos.dw_md), ("03_ddl_dm_monitoreo", modelos.dm_md)):
    out = [f"-- {nombre}: generado desde modelos.py con SQLAlchemy ({dial.name})\n"]
    for t in md.sorted_tables:
        out.append(str(CreateTable(t).compile(dialect=dial)).strip() + ";\n")
        out += [str(CreateIndex(i).compile(dialect=dial)).strip() + ";\n" for i in t.indexes]
    (BASE / "sql" / f"{nombre}.sql").write_text("\n".join(out), encoding="utf8"); print("sql/%s.sql" % nombre)
