#!/usr/bin/env python3
"""Build the CSV register and the single-file HTML catalogue from catalogue.json."""
import json, csv, html, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "catalogue.json"
OUT = HERE            # register and source files: in the repo, not on the web
WEB = HERE / "docs"   # what GitHub Pages publishes, and nothing else
WEB.mkdir(exist_ok=True)

D = json.loads(SRC.read_text(encoding="utf-8"))
# "gaps" is deliberately not read here: it is internal review material and must not
# reach the public page. It stays in catalogue.json and is rendered by build_docx.js.
cat, sets, fields = D["catalogue"], D["datasets"], D["field_definitions"]

# Spatial / temporal granularity on a 5-step coarse-to-fine scale, used by the
# resolution mark in the HTML and by the "match" question the catalogue exists to answer.
GRAIN = {
    "HEA-001": (3, 5), "HEA-002": (3, 5), "HEA-003": (5, 5), "HEA-004": (3, 5),
    "HEA-005": (3, 3), "HEA-006": (3, 5),
    "CLI-001": (2, 5), "CLI-002": (2, 4), "CLI-003": (1, 4), "CLI-004": (5, 5),
    "CLI-005": (5, 5), "CLI-006": (4, 5),
    "ENV-001": (4, 3), "ENV-002": (5, 2), "ENV-003": (5, 2), "ENV-004": (4, 3),
    "ENV-005": (5, 1), "ENV-006": (1, 1), "ENV-007": (5, 1), "ENV-008": (5, 3),
    "REF-001": (3, 2), "REF-002": (5, 2), "REF-003": (3, 1),
    "DER-001": (2, 4), "DER-002": (2, 4), "DER-003": (2, 3),
}

COLS = [
    ("id", "Catalogue ID"), ("title", "Title"), ("title_pt", "Title (PT)"),
    ("domain", "Domain"), ("projects", "Projects"), ("description", "What it contains"),
    ("key_variables", "Key variables"), ("custodian", "Who holds it"),
    ("producer", "Producer"), ("contact", "Contact"),
    ("spatial_coverage", "Spatial coverage"), ("native_resolution", "Native spatial resolution"),
    ("analysis_unit", "Analysis unit"), ("temporal_coverage", "Temporal coverage"),
    ("temporal_resolution", "Temporal resolution"), ("update_frequency", "Update frequency"),
    ("latency", "Latency"), ("access", "Access"), ("access_url", "Access URL"),
    ("formats", "Formats"), ("licence", "Licence"),
    ("sharing_conditions", "Sharing conditions"), ("personal_data", "Personal data"),
    ("linkage_key", "Linkage key"), ("limitations", "Known limitations"),
    ("holding_status", "Holding status"), ("steward", "Steward"),
    ("record_status", "Record status"),
]

# ---------- CSV register ----------
csv_path = OUT / "climate_health_catalogue_register.csv"
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow([h for _, h in COLS])
    for d in sets:
        w.writerow(["; ".join(d[k]) if isinstance(d.get(k), list) else d.get(k, "") for k, _ in COLS])

# ---------- HTML ----------
DOMAIN_COLOUR = {
    "Health": "#B4531F", "Climate": "#1F6F6B", "Environment": "#4A5E23",
    "Reference": "#46506B", "Derived": "#6B3F6B",
}
PROJ = {p["code"]: p for p in cat["projects"]}
e = lambda s: html.escape(str(s or ""))


def access_tone(a):
    a = a.lower()
    if a.startswith("open") and "request" not in a:
        return "open"
    if "restricted" in a or "internal" in a:
        return "closed"
    return "part"


SHORT = {"Open":"Open","Open - registration required":"Open · registration",
         "Partly open - by request":"By request","Partly open - archive by request":"By request",
         "Restricted - by agreement":"Restricted","Internal - shareable on request":"Internal",
         "Internal - to be published with the paper":"Internal","Internal only":"Internal"}


def mark(rank):
    return "".join(
        f'<i class="seg{" on" if i < rank else ""}"></i>' for i in range(5)
    )


def row(d):
    s, t = GRAIN.get(d["id"], (3, 3))
    projs = "".join(
        f'<span class="pill" style="--c:{PROJ[p]["colour"]}">{e(PROJ[p]["code"])}</span>'
        for p in d["projects"]
    )
    detail_fields = [
        ("Key variables", d["key_variables"]), ("Producer", d["producer"]),
        ("Contact", d["contact"]), ("Spatial coverage", d["spatial_coverage"]),
        ("Analysis unit", d["analysis_unit"]), ("Temporal coverage", d["temporal_coverage"]),
        ("Formats", d["formats"]), ("Licence", d["licence"]),
        ("Linkage key", d["linkage_key"]), ("Personal data", d["personal_data"]),
        ("Access", d["access"]), ("Holding status", d["holding_status"]),
        ("Record status", d["record_status"]),
    ]
    dl = "".join(f'<div class="kv"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in detail_fields)
    url = d["access_url"]
    link = (f'<a href="{e(url)}" target="_blank" rel="noopener">{e(url)}</a>'
            if url.startswith("http") else e(url))
    blob = " ".join([d["id"], d["title"], d["title_pt"], d["description"], d["key_variables"],
                     d["custodian"], d["domain"], " ".join(d["projects"]), d["limitations"]]).lower()
    return f'''<article class="rec" data-domain="{e(d["domain"])}" data-projects="{e(" ".join(d["projects"]))}" data-access="{access_tone(d["access"])}" data-search="{e(blob)}" style="--d:{DOMAIN_COLOUR[d["domain"]]}">
 <header class="rec-head" tabindex="0" role="button" aria-expanded="false">
  <span class="id">{e(d["id"])}</span>
  <span class="ttl"><b>{e(d["title"])}</b><em>{e(d["title_pt"])}</em></span>
  <span class="grain" title="Spatial grain {s}/5, temporal grain {t}/5">
    <span class="glabel">space</span><span class="bar">{mark(s)}</span>
    <span class="glabel">time</span><span class="bar">{mark(t)}</span>
  </span>
  <span class="who">{e(d["custodian"].split(";")[0].split(",")[0])}</span>
  <span class="acc acc-{access_tone(d["access"])}">{e(SHORT.get(d["access"], d["access"]))}</span>
  <span class="chev" aria-hidden="true"></span>
 </header>
 <div class="rec-body">
  <p class="lede">{e(d["description"])}</p>
  <div class="specs">
   <div class="spec"><span>Spatial resolution</span><code>{e(d["native_resolution"])}</code></div>
   <div class="spec"><span>Temporal resolution</span><code>{e(d["temporal_resolution"])}</code></div>
   <div class="spec"><span>Updated</span><code>{e(d["update_frequency"])}</code></div>
   <div class="spec"><span>Latency</span><code>{e(d["latency"])}</code></div>
  </div>
  <div class="cond"><h4>Conditions for sharing</h4><p>{e(d["sharing_conditions"])}</p></div>
  <div class="cond warn"><h4>Known limitations</h4><p>{e(d["limitations"])}</p></div>
  <div class="where"><span>Where to get it</span> {link}</div>
  <dl class="grid">{dl}</dl>
  <p class="proj">Used by {projs}</p>
 </div>
</article>'''


proj_cards = "".join(
    f'''<div class="pcard" style="--c:{p["colour"]}">
  <span class="pcode">{e(p["code"])}</span>
  <h3>{e(p["name"])}</h3>
  <p class="q">{e(p["question"])}</p>
  <dl><dt>Unit of analysis</dt><dd>{e(p["unit"])}</dd><dt>Extent</dt><dd>{e(p["extent"])}</dd></dl>
 </div>''' for p in cat["projects"])

proj_filters = "".join(
    f'<button class="f" data-f="proj" data-v="{e(p["code"])}" style="--c:{p["colour"]}">{e(p["code"])}</button>'
    for p in cat["projects"])

dom_filters = "".join(
    f'<button class="f" data-f="dom" data-v="{d}" style="--c:{c}">{d}</button>'
    for d, c in DOMAIN_COLOUR.items())

field_rows = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in fields)

counts = {}
for d in sets:
    counts[d["domain"]] = counts.get(d["domain"], 0) + 1
count_line = " · ".join(f"{v} {k.lower()}" for k, v in counts.items())

HTML = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(cat["title"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{{
 --ink:#3A3A3A; --ink-2:#555555; --ink-3:#7A746D;
 --paper:#FDFCF9; --card:#FFFFFF; --rule:#E0E0E0;
 --accent:#D96666; --accent-hover:#C85555; --link:#BD4D4D;
 --open:#2E6B3E; --part:#9A6B15; --closed:#8C3A3A;
 --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
 --sans:'Noto Sans JP',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 --head:'Montserrat','Noto Sans JP',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 var(--sans);
 -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 20px 80px}}
a{{color:var(--link)}}
a:hover{{color:var(--accent-hover)}}

/* ---- masthead ---- */
header.top{{border-bottom:2px solid var(--accent);padding:34px 0 18px;margin-bottom:26px}}
.eyebrow{{font:11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3)}}
h1{{font-family:var(--head);font-size:clamp(26px,3.6vw,40px);line-height:1.08;margin:12px 0 6px;letter-spacing:-.02em;font-weight:700}}
.sub{{max-width:62ch;color:var(--ink-2);margin:0 0 16px}}
.meta{{display:flex;flex-wrap:wrap;gap:6px 22px;font:12px/1.4 var(--mono);color:var(--ink-3)}}
.purpose{{max-width:70ch;border-left:3px solid var(--ink);padding-left:16px;margin:22px 0 0;color:var(--ink-2)}}

h2{{font-size:13px;font-family:var(--head);font-weight:600;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink-3);margin:44px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--rule)}}

/* ---- projects ---- */
.projects{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
.pcard{{background:var(--card);border:1px solid var(--rule);border-top:4px solid var(--c);padding:16px 18px}}
.pcode{{font:11px/1 var(--mono);letter-spacing:.1em;color:var(--c);font-weight:700}}
.pcard h3{{font-family:var(--head);font-size:17px;margin:8px 0 8px;line-height:1.25}}
.pcard .q{{color:var(--ink-2);margin:0 0 12px;font-size:14px}}
.pcard dl{{margin:0;font-size:12.5px}}
.pcard dt{{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-top:8px}}
.pcard dd{{margin:2px 0 0}}

/* ---- controls ---- */
.controls{{position:sticky;top:0;z-index:5;background:var(--paper);
 padding:12px 0 10px;border-bottom:1px solid var(--rule);margin-bottom:2px}}
#q{{width:100%;padding:11px 13px;border:1px solid var(--ink);background:var(--card);
 font:14px var(--mono);color:var(--ink)}}
#q:focus{{outline:2px solid var(--ink);outline-offset:1px}}
.filters{{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px;align-items:center}}
.fgroup{{font:10px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-right:2px}}
.f{{font:11px var(--mono);letter-spacing:.06em;padding:5px 10px;border:1px solid var(--rule);
 background:var(--card);color:var(--ink-2);cursor:pointer}}
.f:hover{{border-color:var(--c,var(--ink))}}
.f.on{{background:var(--c,var(--ink));border-color:var(--c,var(--ink));color:#fff}}
.tally{{margin-left:auto;font:11px var(--mono);color:var(--ink-3)}}

/* ---- records ---- */
.rec{{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--d);margin-top:6px}}
.rec.hide{{display:none}}
.rec-head{{display:grid;grid-template-columns:74px minmax(200px,1.6fr) 150px 1fr 150px 18px;
 gap:14px;align-items:center;padding:11px 14px;cursor:pointer}}
.rec-head:focus-visible{{outline:2px solid var(--ink);outline-offset:-2px}}
.id{{font:11.5px var(--mono);color:var(--d);font-weight:700;letter-spacing:.02em}}
.ttl b{{display:block;font-size:14.5px;font-weight:600;line-height:1.25}}
.ttl em{{display:block;font-style:normal;font-size:11.5px;color:var(--ink-3);font-family:var(--mono)}}
.who{{font-size:12.5px;color:var(--ink-2)}}
.acc{{font:10.5px var(--mono);letter-spacing:.06em;text-transform:uppercase;text-align:right}}
.acc-open{{color:var(--open)}} .acc-part{{color:var(--part)}} .acc-closed{{color:var(--closed)}}
.chev{{width:9px;height:9px;border-right:1.6px solid var(--ink-3);border-bottom:1.6px solid var(--ink-3);
 transform:rotate(45deg);transition:transform .18s;justify-self:end;margin-top:-4px}}
.rec.open .chev{{transform:rotate(-135deg);margin-top:3px}}

/* the resolution mark: how fine this dataset is in space and in time */
.grain{{display:grid;grid-template-columns:auto 1fr;gap:2px 6px;align-items:center}}
.glabel{{font:9px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}}
.bar{{display:flex;gap:2px}}
.seg{{width:9px;height:5px;background:var(--rule);display:block}}
.seg.on{{background:var(--d)}}

.rec-body{{display:none;padding:4px 14px 20px 14px;border-top:1px solid var(--rule)}}
.rec.open .rec-body{{display:block}}
.lede{{max-width:78ch;margin:14px 0 16px}}
.specs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1px;
 background:var(--rule);border:1px solid var(--rule);margin-bottom:16px}}
.spec{{background:#FAF9F6;padding:9px 11px}}
.spec span{{display:block;font:9.5px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-bottom:3px}}
.spec code{{font:12.5px var(--mono);color:var(--ink)}}
.cond{{border-left:2px solid var(--rule);padding:2px 0 2px 13px;margin:0 0 14px}}
.cond.warn{{border-left-color:var(--part)}}
.cond h4{{font:10px var(--mono);letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3);margin:0 0 4px}}
.cond p{{margin:0;max-width:78ch;font-size:14px}}
.where{{font-size:13px;margin-bottom:16px;word-break:break-word}}
.where span{{font:9.5px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-right:8px}}
dl.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:11px 24px;margin:0 0 16px}}
dl.grid dt{{font:9.5px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}}
dl.grid dd{{margin:1px 0 0;font-size:13px}}
.proj{{margin:0;font-size:12px;color:var(--ink-3)}}
.pill{{display:inline-block;font:10.5px var(--mono);letter-spacing:.06em;padding:2px 7px;
 background:var(--c);color:#fff;margin-left:5px}}

table.defs{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--rule)}}
table.defs th{{text-align:left;vertical-align:top;width:210px;padding:9px 14px;
 font:11.5px var(--mono);font-weight:600;border-bottom:1px solid var(--rule);color:var(--ink)}}
table.defs td{{padding:9px 14px;border-bottom:1px solid var(--rule);font-size:13.5px;color:var(--ink-2)}}
footer{{margin-top:50px;padding-top:16px;border-top:1px solid var(--rule);
 font:11.5px var(--mono);color:var(--ink-3);line-height:1.7}}

@media (max-width:860px){{
 .rec-head{{grid-template-columns:1fr auto;gap:6px}}
 .grain,.who{{display:none}}
 .controls{{position:static}}
}}
@media print{{
 .controls,.chev{{display:none}}
 body{{background:#fff;font-size:10pt}}
 .rec-body{{display:block !important}}
 .rec{{break-inside:avoid;border:1px solid #999}}
 .rec.hide{{display:block}}
}}
@media (prefers-reduced-motion:reduce){{*{{transition:none !important}}}}
</style></head><body>
<div class="wrap">

<header class="top">
 <p class="eyebrow">{e(cat["institution"])} — Climate and Health Laboratory</p>
 <h1>{e(cat["title"])}</h1>
 <p class="sub">{e(cat["subtitle"])}</p>
 <div class="meta">
  <span>Version {e(cat["version"])}</span><span>{e(cat["date"])}</span>
  <span>{len(sets)} datasets — {e(count_line)}</span>
  <span>Maintainer: {e(cat["maintainer"])}</span>
 </div>
 <p class="purpose">{e(cat["purpose"])}</p>
</header>

<h2>Research lines</h2>
<div class="projects">{proj_cards}</div>

<h2>Dataset register</h2>
<div class="controls">
 <input id="q" type="search" placeholder="Search datasets, variables, holders, limitations…" autocomplete="off">
 <div class="filters">
  <span class="fgroup">Project</span>{proj_filters}
  <span class="fgroup" style="margin-left:14px">Domain</span>{dom_filters}
  <span class="fgroup" style="margin-left:14px">Access</span>
  <button class="f" data-f="acc" data-v="open" style="--c:var(--open)">Open</button>
  <button class="f" data-f="acc" data-v="part" style="--c:var(--part)">By request</button>
  <button class="f" data-f="acc" data-v="closed" style="--c:var(--closed)">Restricted</button>
  <span class="tally" id="tally"></span>
 </div>
</div>
<div id="list">{"".join(row(d) for d in sets)}</div>

<h2>What each field means</h2>
<table class="defs">{field_rows}</table>

<footer>
 Maintained by {e(cat["maintainer"])}.<br>
 Source: <code>climate_health_catalogue_register.csv</code>. This page is generated from it — edit the register, rebuild the page.<br>
 Health data: Portal de Dados Abertos do SUS · <a href="https://dadosabertos.saude.gov.br/">dadosabertos.saude.gov.br</a><br>
 Climate data: Copernicus Climate Data Store (CDS) · <a href="https://climate.copernicus.eu/">climate.copernicus.eu</a>
</footer>
</div>

<script>
(function(){{
 var recs=[].slice.call(document.querySelectorAll('.rec')),
     q=document.getElementById('q'), tally=document.getElementById('tally'),
     state={{proj:new Set(),dom:new Set(),acc:new Set()}};

 function apply(){{
  var term=q.value.trim().toLowerCase(), n=0;
  recs.forEach(function(r){{
   var ok = (!term || r.dataset.search.indexOf(term)>-1)
     && (!state.proj.size || r.dataset.projects.split(' ').some(function(p){{return state.proj.has(p);}}))
     && (!state.dom.size  || state.dom.has(r.dataset.domain))
     && (!state.acc.size  || state.acc.has(r.dataset.access));
   r.classList.toggle('hide',!ok); if(ok) n++;
  }});
  tally.textContent = n===recs.length ? recs.length+' datasets' : n+' of '+recs.length+' datasets';
 }}

 q.addEventListener('input',apply);
 document.querySelectorAll('.f').forEach(function(b){{
  b.addEventListener('click',function(){{
   var s=state[b.dataset.f], v=b.dataset.v;
   if(s.has(v)){{s.delete(v);b.classList.remove('on');}} else {{s.add(v);b.classList.add('on');}}
   apply();
  }});
 }});

 function toggle(r){{
  var open=r.classList.toggle('open');
  r.querySelector('.rec-head').setAttribute('aria-expanded',open);
 }}
 recs.forEach(function(r){{
  var h=r.querySelector('.rec-head');
  h.addEventListener('click',function(){{toggle(r);}});
  h.addEventListener('keydown',function(ev){{
   if(ev.key==='Enter'||ev.key===' '){{ev.preventDefault();toggle(r);}}
  }});
 }});
 apply();
}})();
</script>
</body></html>'''

(WEB / "climate_health_catalogue.html").write_text(HTML, encoding="utf-8")
print("CSV rows:", len(sets))
print("HTML bytes:", len(HTML))
