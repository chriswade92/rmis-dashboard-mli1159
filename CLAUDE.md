# RMIS Dashboard — Programme PIP MLI 1159
Welthungerhilfe · Mali · Suivi-Évaluation

## What this project is
A self-contained HTML dashboard (`index.html`) for monitoring field infrastructure visits in Mali.
Hosted on Vercel at a permanent URL shared with partners (WHH HQ, Donilab, KFW).

## How to update
```bash
python update.py   # reads exports/ + photos/ → writes index.html
git add index.html && git commit -m "update" && git push   # Vercel auto-deploys
```

## File structure
```
exports/     ← CommCare xlsx exports (infrastructure + missions + activite_formation + activity_transversale)
photos/      ← mission photos named M{ID_gen}_photo{N}.jpg · activity photos named {caseid}_photo{N}.jpg
template.html ← HTML/React template with __LOGO_B64__ __DATA_JSON__ __PHOTOS_JSON__ __ACT_PHOTOS_JSON__ __HEADER_DATE__ __UPDATE_DATE__ placeholders
update.py    ← reads exports + photos → fills template → writes index.html
index.html   ← OUTPUT (never edit manually)
whh_logo.png ← WHH brand logo
```

## Data model
Four CommCare case types. `caseid` is a UUID on every type; the parent link is `indices.mli1159_infrastructure` → infrastructure `caseid`.
- **Infrastructure** (parent): one row per site with GPS, type, commune/cercle/region (count grows over time — read from `DATA.infrastructures.length`, never hardcode)
- **Mission** (child): field visits linked to infrastructure. Photos keyed by `ID_gen` (e.g. `M42860`) → `PHOTOS`.
- **activite_formation** (child of infrastructure): training events. Has parent link; geography is inherited from the parent infra (its own `commune` is a location-code UUID, no region/cercle).
- **activity_transversale** (commune-level, NO parent link): cross-cutting activities with their own region/cercle/commune.
- `update.py` normalises formation + transversale into one common activity schema → `DATA.formations` / `DATA.transversales` (note the differing source columns: `nom_formation`/`nom_activite`, `statut_formation`/`statut`, `date_de_la_formation`/`date_activite`, `cree_formation`/`cree_activite`).
- Photo conventions: missions `photos/M{ID_gen}_photo{N}.jpg` → `PHOTOS` · activities `photos/{caseid}_photo{N}.jpg` → `ACT_PHOTOS` (keyed by caseid). `PHOTOS` stays mission-only so mission/photo counts remain accurate.

## Tech stack
- React 18 + Recharts loaded from cdnjs CDN (PropTypes must load BEFORE Recharts)
- Leaflet 1.9.4 + CartoDB Voyager basemap (Carte tab) — needs internet at view time for tiles
- Babel standalone for in-browser JSX transpilation
- All data + photos embedded as base64 in a single self-contained HTML file (basemap tiles excepted)
- WHH brand green: #2FAB15 | Fonts: Fraunces (display) + IBM Plex Sans + IBM Plex Mono

## Counts are dynamic
Site/visit/photo counts in UI labels (tab bar, panel titles/subtitles, PhaseBanner sentence) MUST read from `DATA.infrastructures.length` / `DATA.missions.length` / `Object.values(PHOTOS).reduce(...)` at render time. Never hardcode a number into a label — the dashboard is regenerated each cycle as the data grows.

## Header date is auto-filled
The header month-year label uses the `__HEADER_DATE__` placeholder, filled by `update.py` from a hardcoded French month table (`FR_MONTHS`, locale-independent on Windows) → e.g. "Juin 2026". No manual edit per cycle. (`__UPDATE_DATE__` = full "3 juin 2026" string is also computed but not currently referenced in template.html.)

## Dashboard tabs
1. Vue d'ensemble — KPIs, pie chart (type), bar chart (type × cercle), phase banner
2. Carte — full-width (70vh) Leaflet/Voyager map of Mali. divIcon markers: circles = infrastructures (TYPE_META colours), diamonds = formations/transversales (KIND_META colours), each with white halo + drop shadow and scale-up on hover/select. Hover tooltips, zoom/pan, scale bar. Below the map: Légende (infra types + an "Activités & formations" section) and a multi-column "Points cartographiés" list with bidirectional hover/click sync.
3. Les N infrastructures — card grid with photo thumbnails, filterable (tab label is dynamic)
4. Visites terrain & photos — mission cards with photos + captions, lightbox on click
5. Activités & formations — formation + transversale event cards (date, participants, groupe cible, objectives, linked infra, photo gallery + field comments, lightbox). Tab + count appear only when `ACTIVITIES.length > 0`; kind filter (Toutes / Formations / Transversales).
6. (No data quality tab in partner-facing version)

## Known data issues (do not hide, flag them)
- urbaine_transfo_01 appears twice (2 different sites, same name)
- Mission M42860: debut_de_la_mission = 2029 (typo, should be 2026)
- Mission M94020: fin_de_la_mission = 2024 (typo, should be 2026)
- HIMO fields: 0/16 filled (works not started yet — show placeholder, not zeros)
- photos/Picture1.jpg does not match M{ID}_photo{N}.jpg convention and is skipped by update.py

## Current data state (3 juin 2026)
- 19 infrastructures | 22 missions | 17/22 approuvées | 65 mission photos
- 1 formation + 1 activité transversale | 11 activity photos (formation 7, transversale 4)
- Regions: Kayes, Kita | Cercles: ambidedi, kayes, kita, sagabari, sebekoro
- NOTE: the activity_transversale export is sometimes left open in Excel mid-edit (a `~$…xlsx` lock file appears + earlier test rows in region "bandiagara"). `update.py` skips `~$` files; close Excel before the final run.

## Infrastructure types + colours
perimetre_maraicher #4CA82E | unite_transfo #D98B2B | piste #7B5B3F
magasin #9E6BB5 | marche #D54C4C | parc_vaccin #3B87B8 | autres_infrastructure #7A7668

## Activity kinds + colours (Activités & formations tab)
formation #2F8FAB | transversale #8A5CB8
type_de_formation labels: autre_infra, autre_trans, appui_decentralisation (unknown values are prettified)

## Deployment
GitHub repo (private) → Vercel auto-deploy on push
Output must be named `index.html` (Vercel serves this as root)
Cache-Control: no-cache (set in vercel.json)
