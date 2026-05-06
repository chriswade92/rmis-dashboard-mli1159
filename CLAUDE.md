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
exports/     ← CommCare xlsx exports (infrastructure + missions)
photos/      ← field photos named {ID_gen}_photo{N}.jpg  e.g. M42860_photo1.jpg
template.html ← HTML/React template with __LOGO_B64__ __DATA_JSON__ __PHOTOS_JSON__ __UPDATE_DATE__ placeholders
update.py    ← reads exports + photos → fills template → writes index.html
index.html   ← OUTPUT (never edit manually)
whh_logo.png ← WHH brand logo
```

## Data model
Two CommCare case types linked parent→child:
- **Infrastructure** (parent): 15 sites with GPS, type, commune/cercle/region
- **Mission** (child): field visits linked via `indices.mli1159_infrastructure` → `parent_caseid`
- Photo convention: `photos/M{ID_gen}_photo{N}.jpg`

## Tech stack
- React 18 + Recharts loaded from cdnjs CDN (PropTypes must load BEFORE Recharts)
- Babel standalone for in-browser JSX transpilation
- All data + photos embedded as base64 in a single self-contained HTML file
- WHH brand green: #2FAB15 | Fonts: Fraunces (display) + IBM Plex Sans + IBM Plex Mono

## Dashboard tabs
1. Vue d'ensemble — KPIs, pie chart (type), bar chart (type × cercle), phase banner
2. Carte — scatter plot lat/lon of all 15 sites coloured by type
3. Les 15 infrastructures — card grid with photo thumbnails, filterable
4. Visites terrain & photos — mission cards with photos + captions, lightbox on click
5. (No data quality tab in partner-facing version)

## Known data issues (do not hide, flag them)
- urbaine_transfo_01 appears twice (2 different sites, same name)
- Mission M42860: debut_de_la_mission = 2029 (typo, should be 2026)
- Mission M94020: fin_de_la_mission = 2024 (typo, should be 2026)
- HIMO fields: 0/16 filled (works not started yet — show placeholder, not zeros)
- photos/Picture1.jpg does not match M{ID}_photo{N}.jpg convention and is skipped by update.py

## Current data state (29 avril 2026)
- 14 infrastructures | 16 missions | 16/16 approuvées | 47 photos (16 missions)
- Regions: Kayes, Kita | Cercles: ambidedi, kayes, kita, sagabari, sebekoro

## Infrastructure types + colours
perimetre_maraicher #4CA82E | unite_transfo #D98B2B | piste #7B5B3F
magasin #9E6BB5 | marche #D54C4C | parc_vaccin #3B87B8 | autres_infrastructure #7A7668

## Deployment
GitHub repo (private) → Vercel auto-deploy on push
Output must be named `index.html` (Vercel serves this as root)
Cache-Control: no-cache (set in vercel.json)
