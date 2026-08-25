# Climate and Health Metadata Catalogue — how it fits together

One source, two ways of reading it.

| File | What it is | Who uses it |
|---|---|---|
| `catalogue.json` | The source. One object per dataset, one key per field. | You, when adding or editing a record |
| `climate_health_catalogue_register.csv` | The same content as a flat table. Opens in Excel or Google Sheets; import into CKAN or Airtable. | Partner agencies filling in their own rows |
| `climate_health_catalogue.html` | Single-file web page. Search, filter by project, domain and access, expand any record. No server and no build step. Works offline; only the two webfonts need a connection, and it falls back to system fonts without one. | Anyone who needs to look something up |
| `climate_health_catalogue.docx` | Printable and editable. One page per dataset, a summary table, the open gaps, the field definitions and a change log. | The revewer report, and anyone who prefers paper |

## The loop

Edit `catalogue.json`, then rebuild both outputs:

```bash
python3 build_web.py     # writes the CSV and the HTML
node   build_docx.js     # writes the DOCX
```

If you would rather work in a spreadsheet, edit the CSV and convert it back to JSON before rebuilding. Do not edit the DOCX and expect the change to survive a rebuild — copy it back into the source first.

## Publishing the web page

The HTML is one file, so it travels anywhere — put it on the IPSP web server, or email it and it opens from disk. Its only external reference is the Google Fonts stylesheet for Montserrat and Noto Sans JP; offline it renders in the system sans fallback, with every colour, rule and layout intact.

It is also published as a GitHub Page:

**https://mauroccm.github.io/climate-health-catalogue/**

To update it, rebuild and push:

```bash
python3 build_web.py
git commit -am "Update catalogue"
git push
```

GitHub rebuilds on every push to `main`. The new version is live in under a minute.

Three things about that setup:

- **Only `docs/` is published.** Pages serves that folder and nothing above it, so `catalogue.json`, the CSV register, the DOCX and the build scripts stay in the repository and off the web. `build_web.py` writes the page into `docs/` and the register into the repo root — that split is the whole mechanism, so do not move files between the two without meaning it.
- `docs/index.html` is a six-line redirect to `climate_health_catalogue.html`. GitHub Pages serves `index.html` at the site root, and without it the bare URL 404s. It holds no copy of the page, so it never goes stale.
- **The repository is private. The published site is not.** Anyone with the URL can read anything in `docs/`. Restricting a Pages site to logged-in users requires GitHub Enterprise Cloud. The URL is the only thing between the published page and the open web — which is why internal material, such as the gaps register, is kept out of the page and left to the DOCX.

## Look and feel

The page follows the palette and typefaces of https://mauroccm.github.io — washi off-white `#FDFCF9`, ink `#3A3A3A`, pastel-red accent `#D96666`, Montserrat for headings and Noto Sans JP for text. Those live in the `:root` block of `build_web.py`; change them there, not in the generated HTML.

Two things are deliberately *not* taken from the personal site. The domain and access colours — health, climate, environment, reference, derived, and open/by-request/restricted — carry meaning, so they stay as they are rather than collapsing into the single accent. And the small uppercase labels stay monospace, because they mark structure rather than voice.

## Field standard

The 27 fields follow DCAT (the EU and Brazilian government standard for data catalogues) with four additions that matter for climate–health work and are not in DCAT: **analysis unit**, **latency**, **linkage key** and **known limitations**. Latency is the field that decides whether a dataset can support an operational decision. Linkage key is the field that makes the catalogue usable rather than merely descriptive.

Any organisation joining the catalogue fills in these fields for its own datasets and keeps its own data where it is. That is all the coordination required.
