# interview

## Description
This repository contains python code which fetches two tables from the eqt-website, containing current portfolio and divestments information.
These tables are then enriched using information provided in reference datasets available on gcs.
The enriched information is saved on disk, in newline delimited json format.
Each line corresponds to a company, and the information is grouped according to the source-table from which it originates (website/org-data/funding-data), in order to avoid potential name-colision, and for some extra organizational convenience.

### Enrichment method:
In order to match the website data against the reference datasets, I have looked at all datasets and tried to identify any similar fields between them, to help me in the joining process. The "company uuid" seemed like a good candidate for a primary key, but I did not find this information on the website, so I assumed matching had to be done using other information. I chose to match website data using the "country" and "company name" information, and added assertions in the code to ensure that each website-entry would at most match 1-to-1 with companies in the reference data.

### Enrichment results:
- Current portfolio: 41/101 enriched
- Divestments: 79/165 enriched

Spending some time investigating the  unmatched entries of current portfolio, I've concluded on following reasons for explaining unmatched companies:
- "Company doesnt exist in the reference data".
- "Company seems to exist in the reference data, but country information does not correspond. Example company: "Banking Circle", where country information listed as Luxemburg on web, but Great Britain in the reference data. In all other ways, this really looks like the same company. Other example: "Azelis".

Given that the primary key CompanyName-Country does not uniquely match a company in the ref-dataset it is also possible that some enriched results have contain incorrect enrichment, should the reference dataset contain information about another company within same country with same name. But perhaps this can be deemed unlikely? Something that I would double-check anyway.

## Installation instructions

Tested with Python version: 3.7.4.
Python libraries used listed in `requirements.txt`.
Install these with pip: 
```console
pip install -r requirements.txt
```

## How to run
While standing in top level directory, run the command
```console
python main.py output-dir
```

The pipeline should then run and produce the assignment results at
- `output-dir/current_portfolio_enriched.ndjson`
- `output-dir/divestments_enriched.ndjson`
