#!/usr/bin/env python3
"""
Script amélioré pour récupérer les données NIST avec gestion de session
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin

# Liste des éléments chimiques
ELEMENTS = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U'
}

def create_session():
    """Crée une session requests avec headers appropriés"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    })
    return session

def create_output_directory():
    """Crée le répertoire de sortie"""
    output_dir = "nist_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def extract_data_from_html(html_content, element_symbol):
    """
    Extrait les données numériques d'une page HTML

    Args:
        html_content: Contenu HTML
        element_symbol: Symbole de l'élément

    Returns:
        list: Liste de tuples (energie, mu_rho, mu_en_rho)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Chercher les données dans des balises <pre>
    pre_tags = soup.find_all('pre')
    all_data = []

    for pre in pre_tags:
        text = pre.get_text()
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Chercher des lignes avec 3 nombres ou plus (Energy, µ/rho, µen/rho)
            match = re.match(r'^\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)', line)
            if match:
                try:
                    energy = float(match.group(1))
                    mu_rho = float(match.group(2))
                    mu_en_rho = float(match.group(3))
                    all_data.append((energy, mu_rho, mu_en_rho))
                except ValueError:
                    continue

    # Si pas de <pre>, chercher dans les tableaux
    if not all_data:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    try:
                        energy = float(cells[0].get_text().strip())
                        mu_rho = float(cells[1].get_text().strip())
                        mu_en_rho = float(cells[2].get_text().strip())
                        all_data.append((energy, mu_rho, mu_en_rho))
                    except (ValueError, IndexError):
                        continue

    return all_data

def get_element_data(session, z_number, element_symbol):
    """
    Récupère les données pour un élément

    Args:
        session: Session requests
        z_number: Numéro atomique
        element_symbol: Symbole de l'élément

    Returns:
        list: Données extraites ou None
    """
    print(f"Récupération des données pour {element_symbol} (Z={z_number})...")

    # URLs à essayer
    urls_to_try = [
        f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{z_number:02d}.html",
        f"https://physics.nist.gov/cgi-bin/XrayMassCoef/ElemTab/z{z_number:02d}",
        f"https://www.nist.gov/pml/x-ray-mass-attenuation-coefficients/element/{element_symbol.lower()}",
    ]

    for url in urls_to_try:
        try:
            response = session.get(url, timeout=15, allow_redirects=True)

            # Si la réponse est OK (200)
            if response.status_code == 200:
                print(f"  Connecté à: {url}")

                # Extraire les données
                data = extract_data_from_html(response.text, element_symbol)

                if data:
                    print(f"  ✓ {len(data)} points de données trouvés")
                    return data
                else:
                    # Sauvegarder la page pour debug
                    debug_file = f"debug_{element_symbol}.html"
                    with open(debug_file, 'w') as f:
                        f.write(response.text)
                    print(f"  ⚠ Page téléchargée mais aucune donnée trouvée (sauvegardée dans {debug_file})")

        except requests.exceptions.RequestException as e:
            print(f"  Erreur avec {url}: {e}")
            continue

    return None

def save_data(element_symbol, data, output_dir):
    """Sauvegarde les données dans un fichier"""
    if not data:
        return False

    output_file = os.path.join(output_dir, f"{element_symbol}.txt")

    with open(output_file, 'w') as f:
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")
        for energy, mu_rho, mu_en_rho in data:
            f.write(f"{energy:.6e}\t{mu_rho:.6e}\t{mu_en_rho:.6e}\n")

    print(f"  ✓ Données sauvegardées dans {output_file}")
    return True

def main():
    """Fonction principale"""
    print("=== Récupération des données NIST (version améliorée) ===\n")

    # Créer session et répertoire de sortie
    session = create_session()
    output_dir = create_output_directory()
    print(f"Répertoire de sortie: {output_dir}\n")

    # Compteurs
    success_count = 0
    fail_count = 0

    # Tester d'abord avec quelques éléments
    test_elements = [(1, 'H'), (6, 'C'), (26, 'Fe'), (82, 'Pb')]

    print("Test avec quelques éléments d'abord...\n")
    for z_number, element_symbol in test_elements:
        data = get_element_data(session, z_number, element_symbol)

        if data and save_data(element_symbol, data, output_dir):
            success_count += 1
        else:
            fail_count += 1

        time.sleep(1)

    print(f"\n=== Résultats du test ===")
    print(f"Succès: {success_count}/{len(test_elements)}")

    if success_count > 0:
        print("\n✓ Le script fonctionne! Voulez-vous continuer avec tous les éléments?")
        print("  Décommentez la section ci-dessous pour récupérer tous les éléments.")
    else:
        print("\n✗ Le script ne fonctionne pas. Vérifiez les fichiers debug_*.html")

    # Pour récupérer tous les éléments, décommentez ci-dessous:
    """
    print("\nRécupération de tous les éléments...\n")
    for z_number, element_symbol in ELEMENTS.items():
        if (z_number, element_symbol) in test_elements:
            continue  # Déjà téléchargé

        data = get_element_data(session, z_number, element_symbol)

        if data and save_data(element_symbol, data, output_dir):
            success_count += 1
        else:
            fail_count += 1

        time.sleep(1)

    print(f"\n=== Résumé final ===")
    print(f"Succès: {success_count}")
    print(f"Échecs: {fail_count}")
    print(f"Total: {len(ELEMENTS)}")
    """

if __name__ == "__main__":
    main()
