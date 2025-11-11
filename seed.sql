# create tables from current data
CREATE TABLE suppliers AS SELECT * FROM read_csv_auto('./data/suppliers.csv');
CREATE TABLE requests AS SELECT * FROM read_csv_auto('./data/data_requests.csv');
CREATE TABLE blacklist AS SELECT * FROM read_csv_auto('./data/supplier_blacklist.csv');
CREATE TABLE qa_officers AS SELECT * FROM read_csv_auto('./data/quality_officers.csv');

