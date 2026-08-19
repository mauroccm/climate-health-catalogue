# How to edit the catalogue

Everything lives in **`catalogue.json`**. You edit that one file, run two commands, and the web page, the Word document and the CSV all update together. You never edit the `.html` or the `.docx` directly — they get overwritten.

```
catalogue.json  ──►  python3 build_web.py   ──►  .csv + .html
                └──►  node build_docx.js     ──►  .docx
```

## Three rules

1. **Text goes in double quotes.** `"access": "Open"` — never single quotes.
2. **Every line ends with a comma, except the last one in a block.** This is the mistake that breaks the file 90% of the time.
3. **Don't invent field names.** Every dataset uses the same 28 keys. If a field doesn't apply, write `"Not applicable"` — don't delete the line, or the table will have a hole in it.

To check you haven't broken anything before rebuilding:

```bash
python3 -c "import json; json.load(open('catalogue.json')); print('valid')"
```

If it prints an error with a line number, go to that line — the problem is almost always a missing or extra comma just above it.

---

## Recipe A — change a field on an existing dataset

Find the record by its ID, change the text, save.

**Example: dew-point was added to the Pará download (fix 1).** Search for `"CLI-001"`, then edit:

```json
"limitations": "Temperatures arrive in Kelvin (subtract 273.15). ... The Pará download was extended to dew-point temperature in August 2026; series before that date do not contain it."
```

That's the whole operation. The web page and the Word file pick it up on the next build.

**Which field to touch, for the fixes you sent:**

| Your fix | Record | Fields changed |
|---|---|---|
| 1 · humidity for Pará | `CLI-001`, `DER-003` | `limitations`, `key_variables`, `description` |
| 3 · human footprint source | `ENV-007` | nearly all — see Recipe C |
| 4 · COVISA after ethics | `HEA-003` | `sharing_conditions`, `holding_status`, `record_status`, `key_variables` |
| 5 · CGE at project start | `CLI-004` | `sharing_conditions`, `holding_status`, `record_status` |
| 6 · INMET bias check | `CLI-005` | `description`, `holding_status`, `limitations` |

---

## Recipe B — add a new dataset

Copy any existing record, paste it below, change the values. Two things are easy to forget:

**1. Give it an ID that doesn't exist yet.** The prefix sets the colour and the section it lands in: `HEA` health, `CLI` climate, `ENV` environment, `REF` reference geography, `DER` derived by you.

**2. Add it to the `GRAIN` table in `build_web.py`.** This drives the two-bar resolution mark on the web page. Two numbers, 1 (coarse) to 5 (fine): space first, time second.

```python
"CLI-006": (4, 5),   # river gauges: fine in space, daily in time
"ENV-008": (5, 3),   # 30 m water extent, monthly
```

Rough scale, if you're unsure:

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **Space** | global index | ~9 km | ~1 km, municipality | 100–250 m | 30 m or finer, point, address |
| **Time** | static | annual | monthly | weekly | daily or hourly |

Miss this step and nothing breaks — the dataset just shows 3/3 by default.

---

## Recipe C — the blank template

Copy this into the `datasets` list and fill it in.

```json
{
  "id": "CLI-007",
  "title": "",
  "title_pt": "",
  "domain": "Climate",
  "projects": ["ACL-AMZ"],
  "description": "",
  "key_variables": "",
  "custodian": "",
  "producer": "",
  "contact": "",
  "spatial_coverage": "",
  "native_resolution": "",
  "analysis_unit": "",
  "temporal_coverage": "",
  "temporal_resolution": "",
  "update_frequency": "",
  "latency": "",
  "access": "Open",
  "access_url": "",
  "formats": "",
  "licence": "",
  "sharing_conditions": "",
  "personal_data": "No",
  "linkage_key": "",
  "limitations": "",
  "holding_status": "Candidate - not yet acquired",
  "steward": "IPSP Climate and Health Laboratory",
  "record_status": "Draft"
}
```

Three fields have a fixed set of values, because the web page filters and colours on them:

- `domain` — `Health` · `Climate` · `Environment` · `Reference` · `Derived`
- `access` — anything starting `Open` is green, `Partly open` is amber, `Restricted` or `Internal` is red
- `projects` — `YF-TMIN` · `DENGUE-SUHI` · `ACL-AMZ`, one or more

---

## Recipe D — update a gap

Gaps live in `gaps.json`, which sits beside the checkout and is not committed. Each one now carries a status, an owner and a date.

```json
{
  "gap": "What is missing, in a short phrase.",
  "status": "Planned",
  "detail": "What is missing, in one or two sentences.",
  "action": "The step that closes it.",
  "owner": "IPSP",
  "when": "Next data cycle"
}
```

`status` must be exactly `Resolved`, `In progress` or `Planned` — those three strings set the colour and the label. When something is resolved, don't delete the gap: change the status and rewrite `action` to say what was done. The reviewer wants to see the closed ones, and the label above `action` flips from "Next step" to "What was done" on its own.

---

## Rebuild

```bash
python3 build_web.py     # → CSV and HTML
node   build_docx.js     # → DOCX
```

Then bump `"version"` at the top of the file and add a row to the change-log table in `build_docx.js`.

---

## What changed in v0.2

Seven gaps were reviewed and the catalogue went from 24 to 26 datasets. The gap-by-gap
detail is internal review material: it lives in `gaps.json`, which is not committed, and is
rendered into the DOCX.
