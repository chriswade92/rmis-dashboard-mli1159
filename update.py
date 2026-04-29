#!/usr/bin/env python3
"""
RMIS Dashboard — Script de mise à jour
Programme PIP MLI 1159 · Welthungerhilfe

Usage:
    python update.py

Ce script lit vos exports CommCare (.xlsx) et vos photos locales,
et génère un fichier HTML autonome que vous pouvez envoyer aux partenaires.

Structure attendue:
    exports/
        mli1159_infrastructure_<date>.xlsx   ← dernier export CommCare
        mli1159_activity_mission_<date>.xlsx  ← dernier export CommCare
    photos/
        M42860_photo1.jpg
        M42860_photo2.jpg
        M05855_photo1.jpg
        ...
    whh_logo.png       ← logo WHH (fourni dans ce kit)
    update.py          ← ce script

Output:
    RMIS_Dashboard_MLI1159.html   ← envoyer aux partenaires
"""

import os, sys, json, base64, re, io
from pathlib import Path
from datetime import datetime

# ── check dependencies ────────────────────────────────────────────────
missing = []
try:
    import pandas as pd
except ImportError:
    missing.append("pandas")
try:
    from PIL import Image, ImageOps
except ImportError:
    missing.append("Pillow")
try:
    import openpyxl
except ImportError:
    missing.append("openpyxl")

if missing:
    print(f"\n❌ Bibliothèques manquantes : {', '.join(missing)}")
    print("   Installez-les avec : pip install " + " ".join(missing))
    sys.exit(1)

# ── paths ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
EXPORTS    = BASE_DIR / "exports"
PHOTOS_DIR = BASE_DIR / "photos"
LOGO_PATH  = BASE_DIR / "whh_logo.png"
OUTPUT     = BASE_DIR / "index.html"

# ── helpers ───────────────────────────────────────────────────────────
def find_latest(folder, pattern):
    """Find the most recently modified xlsx matching pattern."""
    files = sorted(folder.glob(f"*{pattern}*.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"Aucun fichier '{pattern}' trouvé dans {folder}/")
    print(f"  ✓ {files[0].name}")
    return files[0]

def parse_gps(s):
    if not s or str(s).strip() in ['---', '', 'nan']: return (None, None)
    parts = str(s).split()
    if len(parts) >= 2:
        try: return (float(parts[0]), float(parts[1]))
        except: return (None, None)
    return (None, None)

def to_date(val):
    try:
        import pandas as pd
        return pd.to_datetime(val, errors='coerce').strftime('%Y-%m-%d')
    except: return None

def encode_logo(path):
    if not path.exists():
        print(f"  ⚠ Logo non trouvé : {path}. Le dashboard utilisera du texte à la place.")
        return ""
    img = Image.open(path).convert("RGBA")
    img.thumbnail((480, 240), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

def encode_photo(path, max_width=900, quality=78):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode != 'RGB': img = img.convert('RGB')
    w, h = img.size
    if w > max_width:
        img = img.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

# ── 1. load data ──────────────────────────────────────────────────────
print("\n📂 Chargement des exports CommCare...")
import pandas as pd

inf_path = find_latest(EXPORTS, "infrastructure")
mis_path = find_latest(EXPORTS, "mission")

inf = pd.read_excel(inf_path, sheet_name="Cases")
mis = pd.read_excel(mis_path, sheet_name="Cases")

# GPS
inf['lat'], inf['lon'] = zip(*inf['gps_coordonnees'].apply(parse_gps))

# Select + rename infrastructure
inf_cols = ['caseid','name','type_infrastructure','phase_actuelle',
            'commune','cercle','region','lat','lon','opened_date']
inf_sub = inf[[c for c in inf_cols if c in inf.columns]].copy()
for c in ['opened_date']:
    if c in inf_sub:
        inf_sub[c] = pd.to_datetime(inf_sub[c], errors='coerce').dt.strftime('%Y-%m-%d')

# Select + rename missions
mis_cols = ['caseid','ID_gen','nom_mission','type_de_mission','statut_mission',
            'commune','cercle','region','debut_de_la_mission','fin_de_la_mission',
            'indices.mli1159_infrastructure','opened_by_username','opened_date',
            'objectifs_de_la_mission','details_ouvrage',
            'commentaire_de_la_photo_1','commentaire_de_la_photo_2','commentaire_de_la_photo_3']
mis_sub = mis[[c for c in mis_cols if c in mis.columns]].copy()
for c in ['debut_de_la_mission','fin_de_la_mission','opened_date']:
    if c in mis_sub:
        mis_sub[c] = pd.to_datetime(mis_sub[c], errors='coerce').dt.strftime('%Y-%m-%d')

inf_records = json.loads(inf_sub.to_json(orient='records'))
mis_records = json.loads(mis_sub.to_json(orient='records'))
for r in mis_records:
    key = 'indices.mli1159_infrastructure'
    if key in r: r['parent_caseid'] = r.pop(key)

print(f"  ✓ {len(inf_records)} infrastructures, {len(mis_records)} missions")

# ── 2. load photos ────────────────────────────────────────────────────
print("\n📸 Chargement des photos...")
PHOTOS_DIR.mkdir(exist_ok=True)
photo_map = {}  # mission_id → [data_uri, ...]

if not any(PHOTOS_DIR.glob("*.jpg")) and not any(PHOTOS_DIR.glob("*.jpeg")):
    print("  ⚠ Aucune photo trouvée dans photos/. Le dashboard n'affichera pas de photos.")
    print("    Convention de nommage attendue : M42860_photo1.jpg, M42860_photo2.jpg, etc.")
else:
    photo_files = sorted([
        f for f in PHOTOS_DIR.iterdir()
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
    ])
    for f in photo_files:
        match = re.search(r'(M\d+)', f.name)
        if not match:
            print(f"  ⚠ Ignoré (pas d'ID mission) : {f.name}")
            continue
        mid = match.group(1)
        try:
            uri = encode_photo(f)
            photo_map.setdefault(mid, []).append(uri)
        except Exception as e:
            print(f"  ⚠ Erreur lecture {f.name}: {e}")

    total = sum(len(v) for v in photo_map.values())
    print(f"  ✓ {total} photos pour {len(photo_map)} missions")

# ── 3. encode logo ────────────────────────────────────────────────────
print("\n🎨 Chargement du logo...")
logo_b64 = encode_logo(LOGO_PATH)

# ── 4. build HTML ─────────────────────────────────────────────────────
print("\n🔨 Génération du HTML...")

today = datetime.now().strftime("%d %B %Y")
approved = sum(1 for r in mis_records if r.get('statut_mission') == 'approuvee')

data_json   = json.dumps({"infrastructures": inf_records, "missions": mis_records}, ensure_ascii=False)
photos_json = json.dumps(photo_map, ensure_ascii=False)

# Read the HTML template
template_path = BASE_DIR / "template.html"
if not template_path.exists():
    print("  ❌ template.html non trouvé. Relancez le kit d'installation.")
    sys.exit(1)

html = template_path.read_text(encoding='utf-8')

# Inject data
html = html.replace("__LOGO_B64__",    logo_b64)
html = html.replace("__DATA_JSON__",   data_json)
html = html.replace("__PHOTOS_JSON__", photos_json)
html = html.replace("__UPDATE_DATE__", today)
html = html.replace("__NB_INFRA__",    str(len(inf_records)))
html = html.replace("__NB_MISSION__",  str(len(mis_records)))
html = html.replace("__NB_APPROVED__", str(approved))

OUTPUT.write_text(html, encoding='utf-8')
size_mb = OUTPUT.stat().st_size / 1024 / 1024

print(f"\n✅ Dashboard généré : {OUTPUT.name}")
print(f"   Taille : {size_mb:.1f} MB")
print(f"   Données : {len(inf_records)} infrastructures · {len(mis_records)} missions · {approved} approuvées")
print(f"   Photos  : {sum(len(v) for v in photo_map.values())} photos pour {len(photo_map)} missions")
print(f"\n📤 Partagez ce fichier avec vos partenaires :")
print(f"   {OUTPUT.absolute()}\n")
