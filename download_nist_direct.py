#!/usr/bin/env python3
"""
Essai de téléchargement direct des fichiers ASCII NIST
en testant différentes URLs possibles
"""

import requests
import time

def try_download_element(z_number, element_symbol):
    """
    Essaie différentes URLs pour télécharger les données d'un élément
    """

    # Liste d'URLs possibles à essayer
    url_patterns = [
        f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{z_number:02d}.html",
        f"https://physics.nist.gov/PhysRefData/FFast/Text/z{z_number:02d}.txt",
        f"https://physics.nist.gov/PhysRefData/FFast/html/z{z_number:02d}.html",
        f"https://www.nist.gov/sites/default/files/documents/pml/data/xraycoef/z{z_number:02d}.txt",
        f"https://physics.nist.gov/cgi-bin/ffast/ffast.pl?Z={z_number}&Type=0",
    ]

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    print(f"\n=== Essai pour {element_symbol} (Z={z_number}) ===")

    for url in url_patterns:
        try:
            print(f"Essai: {url}")
            response = session.get(url, timeout=10)

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                # Sauvegarder pour inspection
                filename = f"test_download_{element_symbol}_pattern{url_patterns.index(url)}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  ✓ Téléchargé! Sauvegardé dans {filename}")
                print(f"  Taille: {len(response.text)} caractères")
                print(f"  Premiers 200 caractères:\n{response.text[:200]}")
                return True

        except Exception as e:
            print(f"  Erreur: {e}")

    return False

# Test avec Fe (Z=26)
try_download_element(26, 'Fe')

# Test avec C (Z=6)
time.sleep(1)
try_download_element(6, 'C')
