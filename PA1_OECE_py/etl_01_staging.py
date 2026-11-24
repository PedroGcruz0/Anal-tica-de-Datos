"""ETL_01_Staging: CSV de la fuente (OECE/SEACE) -> STG_OECE, solo con pandas + SQLAlchemy.
Uso: python etl_01_staging.py                (carga inicial: recrea STG con 2023-2025)
     python etl_01_staging.py --append 2026  (incremental: agrega el año indicado sin borrar)"""
import sys, time
import pandas as pd
import config, modelos

NUM = {"num_tenderers", "value_amount", "value_amount_pen", "quantity", "total_value_amount", "rate"}
SPEC = {   # tabla_stg: (archivo csv, {columna_csv: columna_stg})
 "stg_main": ("main", {"ocid": "ocid", "date": "release_date", "buyer_id": "buyer_id", "buyer_name": "buyer_name", "tender_id": "tender_id",
    "tender_title": "tender_title", "tender_mainProcurementCategory": "main_category", "tender_procurementMethodDetails": "method_details",
    "tender_procurementMethod": "method_general", "tender_datePublished": "date_published", "tender_numberOfTenderers": "num_tenderers",
    "tender_value_amount": "value_amount", "tender_value_currency": "value_currency", "tender_value_amount_PEN": "value_amount_pen",
    "tender_tenderPeriod_endDate": "tender_end_date", "planning_budget_description": "budget_description"}),
 "stg_tender_items": ("tender_items", {"main_ocid": "main_ocid", "id": "item_id", "position": "position", "quantity": "quantity",
    "totalValue_amount": "total_value_amount", "totalValue_currency": "total_value_currency", "classification_scheme": "classification_scheme"}),
 "stg_awards": ("awards", {"id": "award_id", "date": "award_date", "value_amount": "value_amount", "value_currency": "value_currency", "main_ocid": "main_ocid"}),
 "stg_awards_fx": ("awards_value_exchangeRates", {"rate": "rate", "currency": "currency", "main_ocid": "main_ocid", "awards_id": "awards_id"}),
 "stg_awards_suppliers": ("awards_suppliers", {"id": "supplier_id", "name": "supplier_name", "main_ocid": "main_ocid", "awards_id": "awards_id"}),
 "stg_contracts": ("contracts", {"id": "contract_id", "statusDetails": "status_details", "dateSigned": "date_signed", "status": "status",
    "awardID": "award_id", "value_amount": "value_amount", "value_currency": "value_currency", "period_endDate": "period_end",
    "period_startDate": "period_start", "main_ocid": "main_ocid"}),
 "stg_contracts_fx": ("contracts_value_exchangeRates", {"rate": "rate", "currency": "currency", "main_ocid": "main_ocid", "contracts_id": "contracts_id"}),
}

def cargar(anios, append):
    t0 = time.time(); eng = config.stg()
    if not append:
        modelos.stg_md.drop_all(eng); modelos.stg_md.create_all(eng)
    for tabla, (csv, mapa) in SPEC.items():
        n = 0
        for y in anios:
            ruta = config.DATA / y / y / f"{csv}.csv"
            for ch in pd.read_csv(ruta, usecols=list(mapa), dtype=str, chunksize=100_000):
                ch = ch.rename(columns=mapa)
                for c in NUM.intersection(ch.columns):
                    ch[c] = pd.to_numeric(ch[c], errors="coerce")
                ch["source_year"] = int(y)
                ch.to_sql(tabla, eng, if_exists="append", index=False, chunksize=20_000)
                n += len(ch)
        print(f"{tabla}: {n:,} filas")
    print(f"ETL_01_Staging OK en {time.time() - t0:.0f}s")

if __name__ == "__main__":
    a = sys.argv[1:]
    append = "--append" in a
    anios = [x for x in a if x.isdigit()] or config.ANIOS_INICIALES
    cargar(anios, append)
