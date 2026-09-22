# South Africa Political Data

This repository contains a wide selection of public data from the RSA, as well as the necessary scripts to load it to a database and to analyze it.


## Data Sources

The data is partially extracted from public sources, and from semi-public data sources.

- Cole, Megan (2026), "Operating mines of South Africa. Feb 2026 version.", Mendeley Data, V1, doi: 10.17632/8hf9sb73tw.1. Licensed CC BY-NC 3.0.

- People's Assembly (pa.org.za), Popolo/Pombola data on MPs, parties, and committees.

- IEC (Electoral Commission of South Africa), Political Party Funding declarations, published quarterly under the Political Party Funding Act 6 of 2018. Source: results.elections.org.za/home/downloads/party-funding-reports

### NPO Registry Scraper

This is a scraper for the South African government's database of non-profit organisations (NPOs), extracted from the Siyazana project. **Currently non-functional** — it targets an old npo.gov.za search endpoint that no longer exists. The site has since been rebuilt; a working data source (API or bulk export) has not yet been identified.

### People's Assembly

Information about all members of the national parliament, their financial declarations and data about political parties and committees. Sourced from the [Pombola data provided by PA](http://www.pa.org.za/help/api). 

**Known limitation:** This dataset covers currently seated National Assembly members only. It does not include former MPs, provincial legislators, or party leaders in non-parliamentary roles (e.g. Helen Zille, who now serves as DA Federal Council Chairperson rather than as an MP). Politicians outside current national parliamentary membership will not appear in searches.

### Department of Mineral Resources

Information about all mines and their owners in RSA, which is part of the [directories](http://www.dmr.gov.za/publications/viewcategory/121-directories.html) published by the department.

### IEC Political Party Funding

Quarterly declarations of donations made to registered political parties, as required under the Political Party Funding Act 6 of 2018. Added to cross-reference political funders against mine ownership and MPs' declared business interests, since a donor also appearing as a mine owner or a politician's declared interest is a genuine accountability signal this directory is built to surface. Sourced from the [IEC's published declarations reports](https://results.elections.org.za/home/downloads/party-funding-reports), currently covering financial years 2022/2023 through 2026/2027.

## Exploring the data

Let's check out the people owning the largest number of mines in South Africa:

```sql
SELECT owner, COUNT(*) FROM sa_mines GROUP BY owner ORDER BY COUNT(*) DESC LIMIT 20;
```

## Running the Streamlit app

The repository includes a searchable Streamlit directory (`app.py`) over the loaded data — People, Mines, and Political Funding.

1. Activate the virtual environment:
```bash
   source .venv/bin/activate
```
2. Make sure Postgres is running and the environment variables are set:
```bash
   export DATABASE_URI='postgresql://localhost/madlanga_commission'
   export DATA_PATH=$(pwd)/data
```
3. Run the app:
```bash
   streamlit run app.py
```

This launches the app locally at `http://localhost:8501`. There is no public domain or hosted deployment yet — the app currently only runs locally via the steps above.

