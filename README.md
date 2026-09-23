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

### Water Compliance Violations

Mine water use licence compliance ratings for 2015-2018, sourced from the Department of Water & Sanitation via Oxpeckers Investigative Environmental Journalism Centre's #MineAlert investigation. Licensed CC BY. Joined against mine ownership data to surface which mine owners had compliance issues.

### UK Company Payments to SA Government

Payments made to South African government entities by UK-listed companies with mining/petroleum projects, disclosed under UK payment transparency law (2018 reporting period). Sourced from Oxpeckers Investigative Environmental Journalism Centre via openAFRICA (#MineAlert). Licensed CC BY. Company names can be cross-referenced against mine ownership and IEC donor data.

### DMR 2019 Operating Mines, Quarries & Works

The National Department of Mineral Resources' official 2019 list of operating mines, quarries, and mineral processing works (1,897 entries) - broader in scope than the Feb 2026 Mendeley dataset (245 large-scale mines), including smaller operations, quarries (aggregate, dimension stone, clay/brick materials), and processing works. Older than the Mendeley data, so treat as a complementary historical reference rather than current status. Sourced from DMR via Oxpeckers/openAFRICA. Licensed CC BY.

## Known Gaps in Public Data

Building this directory surfaced several structural gaps in what's publicly accessible about wealth, ownership, and licensing in South Africa. These aren't gaps in this repository's effort — they're genuine transparency gaps in the underlying systems, and documenting them is itself part of this project's purpose.


- **Company ownership (CIPC).** South Africa's Companies and Intellectual Property Commission exposes company data only via a paid, pay-per-lookup API, and its terms restrict redistribution of results. This is also why OpenCorporates' South African company data has been frozen since 2014. There is no free, bulk, redistributable source of who owns/directs which registered companies.
- **NPO registry.** The Department of Social Development's public NPO search (formerly at npo.gov.za) has been replaced by a login-gated self-service portal for NPOs to manage their own registration. There is no public search or bulk data access; status/compliance enquiries are handled manually, one at a time, by email.
- **Mining rights and licenses.** South Africa's mining cadastre (replacing the long-criticised SAMRAD system) is still in phased pilot rollout as of late 2025 (Western Cape only, ~37 rightholders registered), with a national rollout most recently targeted for March 2027 - a date that has slipped multiple times already. There is currently no public way to see who holds which mining/prospecting rights.
- **Derelict and ownerless (D&O) mines.** An estimated 6,100 abandoned mines exist nationally (2,568 flagged high-risk by the Auditor-General), but the government's own D&O database has been publicly flagged by researchers and the Auditor-General for accuracy and transparency problems, and no public bulk dataset is available.

If any of these systems open up public, redistributable data in the future, this directory is a natural place to incorporate it.


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

