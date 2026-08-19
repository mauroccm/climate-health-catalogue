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

The HTML is one self-contained file with no external dependencies. Any of these work:

- Drop it in a GitHub repository and turn on GitHub Pages
- Put it on the IPSP web server
- Email it — it opens from a local file

## Field standard

The 27 fields follow DCAT (the EU and Brazilian government standard for data catalogues) with four additions that matter for climate–health work and are not in DCAT: **analysis unit**, **latency**, **linkage key** and **known limitations**. Latency is the field that decides whether a dataset can support an operational decision. Linkage key is the field that makes the catalogue usable rather than merely descriptive.

Any organisation joining the catalogue fills in these fields for its own datasets and keeps its own data where it is. That is all the coordination required.
