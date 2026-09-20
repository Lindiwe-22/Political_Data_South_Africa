# South Africa Political Data

This repository contains a wide selection of public data from the RSA, as well as the necessary scripts to load it to a database and to analyze it.

## Data Sources

The data is partially extracted from public sources, and from semi-public data sources.

- Cole, Megan (2026), "Operating mines of South Africa. Feb 2026 version.", Mendeley Data, V1, doi: 10.17632/8hf9sb73tw.1. Licensed CC BY-NC 3.0.

- People's Assembly (pa.org.za), Popolo/Pombola data on MPs, parties, and committees.

### NPO Registry Scraper

This is a scraper for the South African government's database of non-political organisations (NPOs). The code is extracted from the Siyazana project because it may be useful on its own.

### People's Assembly

Information about all members of the national parliament, their financial declarations and data about political parties and committees. Sourced from the [Pombola data provided by PA](http://www.pa.org.za/help/api). 

### Department of Mineral Resources

Information about all mines and their owners in RSA, which is part of the [directories](http://www.dmr.gov.za/publications/viewcategory/121-directories.html) published by the department.

## Exploring the data

Let's check out the people owning the largest number of mines in South Africa:

```sql
SELECT mine_owner, COUNT(*) FROM sa_mines GROUP BY mine_owner  ORDER BY COUNT(*) DESC LIMIT 20;
```


