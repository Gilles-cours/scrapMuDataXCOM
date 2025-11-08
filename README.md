# Récupération des Données de Coefficients d'Absorption NIST

Ce projet contient des scripts pour récupérer les coefficients d'absorption massique (µ/rho) et les coefficients d'absorption d'énergie massique (µen/rho) pour tous les éléments chimiques (Z=1 à Z=92).

## Solution Recommandée: xraydb (✓ Fonctionne)

Le script **`get_nist_data_xraydb.py`** utilise la bibliothèque Python `xraydb` qui contient les données NIST/XCOM.

### Installation

```bash
pip install -r requirements.txt
```

Ou uniquement les dépendances nécessaires:

```bash
pip install xraydb numpy
```

### Utilisation

```bash
python get_nist_data_xraydb.py
```

### Résultats

Le script crée un répertoire `nist_data/` contenant 92 fichiers (un par élément):
- `H.txt`, `He.txt`, `Li.txt`, ..., `U.txt`

Chaque fichier contient:
- **Colonne 1**: Énergie (MeV)
- **Colonne 2**: µ/rho (cm²/g) - Coefficient d'absorption massique
- **Colonne 3**: µen/rho (cm²/g) - Coefficient d'absorption d'énergie massique

### Format des Fichiers

```
# Energie (MeV)	µ/rho (cm²/g)	µen/rho (cm²/g)
1.000000e-03	5.075144e+04	5.074659e+04
1.051025e-03	5.075144e+04	5.074659e+04
1.104654e-03	5.075144e+04	5.074659e+04
...
```

Les fichiers sont au format texte avec séparateurs de tabulation, facilement lisibles par:
- Python (numpy.loadtxt, pandas.read_csv)
- Excel, LibreOffice Calc
- MATLAB, Octave
- R, Julia, etc.

### Exemple d'Utilisation des Données

#### Python avec NumPy

```python
import numpy as np

# Charger les données du fer
data = np.loadtxt('nist_data/Fe.txt', skiprows=1)

energie = data[:, 0]      # MeV
mu_rho = data[:, 1]       # cm²/g
mu_en_rho = data[:, 2]    # cm²/g

# Tracer les données
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.loglog(energie, mu_rho, label='µ/rho')
plt.loglog(energie, mu_en_rho, label='µen/rho')
plt.xlabel('Énergie (MeV)')
plt.ylabel('Coefficient (cm²/g)')
plt.legend()
plt.grid(True)
plt.title('Coefficients d\'absorption pour le Fer')
plt.show()
```

#### Python avec Pandas

```python
import pandas as pd

# Charger les données
df = pd.read_csv('nist_data/Fe.txt', sep='\t', comment='#',
                 names=['Energie', 'mu_rho', 'mu_en_rho'])

print(df.head())
print(f"Nombre de points: {len(df)}")
```

## Autres Scripts (Ne fonctionnent pas directement)

### Script avec Requests: `scrape_nist_data.py`

⚠️ Ne fonctionne pas car le site NIST bloque les requêtes automatiques (erreur 403).

### Script avec Selenium: `scrape_nist_selenium.py`

Nécessite l'installation de Chrome et ChromeDriver. Potentiellement fonctionnel mais plus complexe.

### Script CGI XCOM: `scrape_xcom_api.py`

⚠️ Ne fonctionne pas car l'interface CGI bloque également les requêtes automatiques.

### Script Shell: `scrape_nist_direct.sh`

⚠️ Ne fonctionne pas pour les mêmes raisons.

## Structure du Projet

```
scrapMuDataXCOM/
├── README.md                      # Ce fichier
├── requirements.txt               # Dépendances Python
├── get_nist_data_xraydb.py       # ✓ Script principal (recommandé)
├── scrape_nist_data.py           # ✗ Script avec requests (ne fonctionne pas)
├── scrape_nist_selenium.py       # Script avec Selenium (complexe)
├── scrape_nist_improved.py       # ✗ Script amélioré (ne fonctionne pas)
├── scrape_xcom_api.py            # ✗ Script CGI (ne fonctionne pas)
├── scrape_nist_direct.sh         # ✗ Script shell (ne fonctionne pas)
└── nist_data/                    # Répertoire de sortie
    ├── H.txt
    ├── He.txt
    ├── ...
    └── U.txt
```

## Notes Importantes

1. **Grille d'Énergie**: Le script génère 200 points d'énergie logarithmiquement espacés entre 1 keV et 20 MeV.

2. **Source des Données**: Les données proviennent de la bibliothèque `xraydb` qui utilise les tables Elam basées sur les données NIST.

3. **Avertissement**: Pour les énergies < 100 eV, les tables Elam peuvent être moins précises (un avertissement est affiché).

4. **µen/rho**: Dans ce script, µen/rho utilise le coefficient photoélectrique comme approximation. Pour des valeurs plus précises de µen/rho (coefficient d'absorption d'énergie), consultez directement les tables NIST.

## Références

- **NIST XCOM**: https://physics.nist.gov/PhysRefData/XrayMassCoef/tab4.html
- **xraydb Documentation**: https://xraypy.github.io/XrayDB/
- **Tables Elam**: E.P. Elam et al., Radiat. Phys. Chem. 63 (2002) 121

## Auteur

Script créé pour récupérer automatiquement les données de coefficients d'absorption NIST.

## Licence

Ce projet est destiné à un usage éducatif et de recherche. Les données proviennent du NIST et sont dans le domaine public.
