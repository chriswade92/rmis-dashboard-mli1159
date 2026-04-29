# RMIS Dashboard — Kit de mise à jour
## Programme PIP MLI 1159 · Welthungerhilfe

### Structure du dossier

```
RMIS_Dashboard/
├── update.py                        ← script principal (lancer pour rebuilder)
├── template.html                    ← ne pas modifier
├── whh_logo.png                     ← logo WHH (ne pas renommer)
├── exports/
│   ├── mli1159_infrastructure_<date>.xlsx
│   └── mli1159_activity_mission_<date>.xlsx
├── photos/
│   ├── M42860_photo1.jpg
│   ├── M42860_photo2.jpg
│   ├── M05855_photo1.jpg
│   └── ...
└── RMIS_Dashboard_MLI1159.html      ← OUTPUT (généré automatiquement)
```

### Convention de nommage des photos

Chaque fichier photo doit être nommé selon le format :
```
{ID_gen}_photo{N}.jpg
```

Exemples :
- `M42860_photo1.jpg`
- `M42860_photo2.jpg`
- `M05855_photo1.jpg`

L'**ID_gen** se trouve dans l'export CommCare, colonne `ID_gen` de chaque mission.
Le numéro de photo (1, 2, 3...) correspond à l'ordre des photos prises lors de la visite.

### Prérequis (une seule fois)

Installez Python 3 et les bibliothèques nécessaires :

```bash
pip install pandas openpyxl Pillow
```

### Mise à jour du dashboard (procédure mensuelle)

1. **Exporter les données** depuis CommCare HQ (EU) :
   - Données → Export → Case Data → `mli1159_infrastructure` → Exporter
   - Données → Export → Case Data → `mli1159_activity_missioN` → Exporter
   - Placer les deux fichiers `.xlsx` dans le dossier `exports/`

2. **Ajouter les nouvelles photos** dans le dossier `photos/` en respectant la convention de nommage.

3. **Lancer le script** :
   ```bash
   python update.py
   ```
   ou double-cliquer sur `update.py` si Python est configuré sur votre système.

4. **Le fichier `RMIS_Dashboard_MLI1159.html` est mis à jour** dans le dossier.

5. **Partager avec les partenaires** : envoyer le fichier HTML par email, ou le déposer sur Google Drive / SharePoint.

### Dépannage

| Problème | Solution |
|---|---|
| `ModuleNotFoundError: pandas` | Lancer `pip install pandas openpyxl Pillow` |
| `FileNotFoundError: exports/` | Vérifier que les fichiers xlsx sont dans le dossier `exports/` |
| Photo non affichée | Vérifier le nom du fichier (ex: `M42860_photo1.jpg`) |
| HTML vide | Vérifier que le fichier `template.html` est présent |

### Contact

Problème technique : Hassan (Dimagi)
Données CommCare : Clara / Équipe M&E WHH Mali
