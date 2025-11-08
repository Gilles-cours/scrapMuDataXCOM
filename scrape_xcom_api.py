#!/usr/bin/env python3
"""
Script pour récupérer les données µ/rho et µen/rho en utilisant
l'interface CGI du NIST XCOM
"""

import requests
import os
import time
import re

# Liste des éléments chimiques (Z=1 à Z=92)
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

def create_output_directory():
    """Crée le répertoire de sortie"""
    output_dir = "nist_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_xcom_data(z_number, element_symbol):
    """
    Récupère les données via l'interface CGI XCOM

    Args:
        z_number: Numéro atomique
        element_symbol: Symbole de l'élément

    Returns:
        str: Données brutes ou None
    """
    # URL de l'interface CGI XCOM
    url = "https://physics.nist.gov/cgi-bin/Xcom/xcom3_1"

    # Paramètres pour la requête
    # On demande les données pour un seul élément
    params = {
        'ZNum': z_number,
        'Output': 'on',  # Output to screen
        'Method': '1',    # Enter energies manually
    }

    # Energies typiques en MeV (logarithmiquement espacées)
    energies = [
        1e-3, 1.5e-3, 2e-3, 3e-3, 4e-3, 5e-3, 6e-3, 8e-3,
        1e-2, 1.5e-2, 2e-2, 3e-2, 4e-2, 5e-2, 6e-2, 8e-2,
        1e-1, 1.5e-1, 2e-1, 3e-1, 4e-1, 5e-1, 6e-1, 8e-1,
        1, 1.25, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20
    ]

    # Formater les énergies pour la requête
    params['Energies'] = ' '.join([f"{e:.6f}" for e in energies])

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    try:
        print(f"Récupération des données pour {element_symbol} (Z={z_number})...")
        response = requests.post(url, data=params, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.text
        else:
            print(f"  Erreur HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"  Erreur: {e}")
        return None

def parse_xcom_output(html_content):
    """
    Parse la sortie HTML de XCOM

    Args:
        html_content: Contenu HTML

    Returns:
        list: Liste de tuples (energie, mu_rho, mu_en_rho)
    """
    data = []

    # Chercher les données dans le HTML
    # XCOM retourne généralement les données dans un format tabulaire
    lines = html_content.split('\n')

    in_data_section = False
    for line in lines:
        line = line.strip()

        # Chercher le début des données
        if 'Energy' in line and ('mu/rho' in line or 'μ/ρ' in line):
            in_data_section = True
            continue

        if in_data_section:
            # Extraire les nombres de la ligne
            # Format attendu: Energy  mu/rho  mu_en/rho  ...
            match = re.search(r'([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)', line)
            if match:
                try:
                    energy = float(match.group(1))
                    mu_rho = float(match.group(2))
                    mu_en_rho = float(match.group(3))
                    data.append((energy, mu_rho, mu_en_rho))
                except ValueError:
                    continue

    return data

def save_data(element_symbol, data, output_dir):
    """Sauvegarde les données dans un fichier"""
    if not data:
        return False

    output_file = os.path.join(output_dir, f"{element_symbol}.txt")

    with open(output_file, 'w') as f:
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")
        for energy, mu_rho, mu_en_rho in data:
            f.write(f"{energy:.6e}\t{mu_rho:.6e}\t{mu_en_rho:.6e}\n")

    print(f"  ✓ Données sauvegardées: {output_file} ({len(data)} points)")
    return True

def main():
    """Fonction principale"""
    print("=== Récupération des données via XCOM CGI ===\n")

    output_dir = create_output_directory()
    print(f"Répertoire de sortie: {output_dir}\n")

    # Test avec quelques éléments d'abord
    test_elements = [(1, 'H'), (6, 'C'), (13, 'Al'), (26, 'Fe'), (29, 'Cu'), (82, 'Pb')]

    print("Test avec quelques éléments...\n")
    success_count = 0
    fail_count = 0

    for z_number, element_symbol in test_elements:
        html_data = get_xcom_data(z_number, element_symbol)

        if html_data:
            # Sauvegarder le HTML brut pour debug
            with open(f"debug_xcom_{element_symbol}.html", 'w') as f:
                f.write(html_data)

            data = parse_xcom_output(html_data)

            if data and save_data(element_symbol, data, output_dir):
                success_count += 1
            else:
                print(f"  ⚠ Pas de données trouvées (voir debug_xcom_{element_symbol}.html)")
                fail_count += 1
        else:
            fail_count += 1

        time.sleep(2)  # Pause pour ne pas surcharger le serveur

    print(f"\n=== Résultats ===")
    print(f"Succès: {success_count}/{len(test_elements)}")
    print(f"Échecs: {fail_count}/{len(test_elements)}")

    if success_count > 0:
        print("\n✓ Le script fonctionne!")
        print("Pour récupérer tous les éléments, modifiez la liste test_elements")
    else:
        print("\n⚠ Vérifiez les fichiers debug_xcom_*.html")

if __name__ == "__main__":
    main()
