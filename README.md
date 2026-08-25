# Climate and Health Metadata Catalogue — how it fits together

One source of truth, two ways of reading it.

| File | What it is | Who uses it |
|---|---|---|
| `catalogue.json` | The source of truth. One object per dataset, one key per field. | You, when adding or editing a record |
| `climate_health_catalogue_register.csv` | The same content as a flat table. Opens in Excel or Google Sheets; import into CKAN or Airtable. | Partner agencies filling in their own rows |
| `climate_health_catalogue.html` | Single-file web page. Search, filter by project, domain and access, expand any record. No server, no build step, no internet needed. | Anyone who needs to look something up |
| `climate_health_catalogue.docx` | Printable and editable. One page per dataset, a summary table, the open gaps, the field definitions and a change log. | The revewer report, and anyone who prefers paper |

## The loop

Edit `catalogue.json`, then rebuild both outputs:

```bash
python3 build_web.py     # writes the CSV and the HTML
node   build_docx.js     # writes the DOCX
```

If you would rather work in a spreadsheet, edit the CSV and convert it back to JSON before rebuilding. Do not edit the DOCX and expect the change to survive a rebuild — copy it back into the source first.

## Publishing the web page

The HTML is one self-contained file with no external dependencies, so it travels anywhere — put it on the IPSP web server, or email it and it opens from disk.

It is also published as a GitHub Page:

**https://mauroccm.github.io/climate-health-catalogue/**

To update it, rebuild and push:

```bash
python3 build_web.py
git commit -am "Update catalogue"
git push
```

GitHub rebuilds on every push to `main`. The new version is live in under a minute.

Two things about that setup:

- `index.html` is a six-line redirect to `climate_health_catalogue.html`. GitHub Pages serves `index.html` at the site root, and without it the bare URL 404s. It holds no copy of the page, so it never goes stale.
- **The repository is private. The published site is not.** Anyone with the URL can read every file at the repo root, including `catalogue.json` and the CSV register. Restricting a Pages site to logged-in users requires GitHub Enterprise Cloud. The URL is the only thing between the catalogue and the open web.

## Field standard

The 27 fields follow DCAT (the EU and Brazilian government standard for data catalogues) with four additions that matter for climate–health work and are not in DCAT: **analysis unit**, **latency**, **linkage key** and **known limitations**. Latency is the field that decides whether a dataset can support an operational decision. Linkage key is the field that makes the catalogue usable rather than merely descriptive.

Any organisation joining the catalogue fills in these fields for its own datasets and keeps its own data where it is. That is all the coordination required.
