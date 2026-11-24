-- 01_ddl_stg_oece: generado desde modelos.py con SQLAlchemy (postgresql)

CREATE TABLE stg_awards (
	award_id TEXT, 
	award_date TEXT, 
	value_amount FLOAT, 
	value_currency TEXT, 
	main_ocid TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_awards_fx (
	rate FLOAT, 
	currency TEXT, 
	main_ocid TEXT, 
	awards_id TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_awards_suppliers (
	supplier_id TEXT, 
	supplier_name TEXT, 
	main_ocid TEXT, 
	awards_id TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_contracts (
	contract_id TEXT, 
	status_details TEXT, 
	date_signed TEXT, 
	status TEXT, 
	award_id TEXT, 
	value_amount FLOAT, 
	value_currency TEXT, 
	period_end TEXT, 
	period_start TEXT, 
	main_ocid TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_contracts_fx (
	rate FLOAT, 
	currency TEXT, 
	main_ocid TEXT, 
	contracts_id TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_main (
	ocid TEXT, 
	release_date TEXT, 
	buyer_id TEXT, 
	buyer_name TEXT, 
	tender_id TEXT, 
	tender_title TEXT, 
	main_category TEXT, 
	method_details TEXT, 
	method_general TEXT, 
	date_published TEXT, 
	num_tenderers FLOAT, 
	value_amount FLOAT, 
	value_currency TEXT, 
	value_amount_pen FLOAT, 
	tender_end_date TEXT, 
	budget_description TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE stg_tender_items (
	main_ocid TEXT, 
	item_id TEXT, 
	position TEXT, 
	quantity FLOAT, 
	total_value_amount FLOAT, 
	total_value_currency TEXT, 
	classification_scheme TEXT, 
	source_year INTEGER, 
	load_ts TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);
