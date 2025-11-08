# Guide de Téléchargement Manuel des Données NIST

Le site NIST bloque les requêtes automatiques. Voici comment télécharger manuellement les données.

## Méthode 1: Téléchargement individuel par élément

### Étapes:

1. **Ouvrir la page principale**:
   https://physics.nist.gov/PhysRefData/XrayMassCoef/tab4.html

2. **Pour chaque élément** (exemple avec Fe - Fer):
   - Cliquer sur le lien de l'élément (ex: "Fe")
   - Dans la page qui s'ouvre, chercher un lien "Text" ou "ASCII" ou "Table"
   - Clic droit → "Enregistrer sous..."
   - Sauvegarder dans le dossier `nist_raw_data/`
   - Nommer le fichier: `Fe.txt` (ou `z26.txt`)

3. **Répéter** pour tous les éléments de H (Z=1) à U (Z=92)

## Méthode 2: Via le formulaire XCOM

1. **Aller sur**:
   https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html

2. **Pour chaque élément**:
   - Sélectionner "Element" dans le formulaire
   - Entrer le numéro atomique (ex: 26 pour Fe)
   - Sélectionner "Output data format": **ASCII**
   - Énergie: garder la plage par défaut ou personnaliser
   - Cliquer "Submit"
   - Copier-coller les données dans un fichier texte
   - Sauvegarder dans `nist_raw_data/Fe.txt`

## Méthode 3: Utiliser Selenium (automatique mais complexe)

Si vous avez Chrome/Chromium installé:
```bash
python scrape_nist_selenium.py
```

## Structure attendue des fichiers

Créez un dossier `nist_raw_data/` contenant:
```
nist_raw_data/
├── H.txt   (ou z01.txt)
├── He.txt  (ou z02.txt)
├── Li.txt  (ou z03.txt)
...
└── U.txt   (ou z92.txt)
```

## Parser les données téléchargées

Une fois les fichiers téléchargés, utilisez:
```bash
python parse_nist_files.py
```

Ce script:
- Lit les fichiers bruts dans `nist_raw_data/`
- Extrait Énergie, µ/rho, µen/rho
- **AUCUNE interpolation** - données brutes uniquement
- Sauvegarde dans `nist_data/` au format standardisé
