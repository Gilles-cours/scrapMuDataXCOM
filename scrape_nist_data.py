#!/usr/bin/env python3
"""
Script pour récupérer les coefficients d'absorption massique (µ/rho) et
d'absorption d'énergie massique (µen/rho) depuis le site NIST
"""

import requests
from bs4 import BeautifulSoup
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
    """Crée le répertoire de sortie pour les données"""
    output_dir = "nist_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_element_data(z_number, element_symbol):
    """
    Récupère les données µ/rho et µen/rho pour un élément donné

    Args:
        z_number: Numéro atomique de l'élément
        element_symbol: Symbole de l'élément

    Returns:
        tuple: (success, data) où data contient les lignes de données
    """
    # URL de base pour les données NIST
    base_url = f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{z_number:02d}.html"

    # Headers pour éviter le blocage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        print(f"Récupération des données pour {element_symbol} (Z={z_number})...")
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parser le HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher le lien vers les données ASCII
        # Le site NIST a généralement un lien "Text" ou similaire
        links = soup.find_all('a')
        ascii_url = None

        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip().lower()
            if 'text' in text or 'ascii' in text:
                if not href.startswith('http'):
                    ascii_url = f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/{href}"
                else:
                    ascii_url = href
                break

        # Si on ne trouve pas de lien ASCII, essayer un pattern direct
        if not ascii_url:
            ascii_url = f"https://physics.nist.gov/cgi-bin/XrayMassCoef/ElemTab/z{z_number:02d}.txt"

        # Récupérer les données ASCII
        print(f"  Téléchargement depuis: {ascii_url}")
        ascii_response = requests.get(ascii_url, headers=headers, timeout=10)
        ascii_response.raise_for_status()

        return True, ascii_response.text

    except requests.exceptions.RequestException as e:
        print(f"  Erreur lors de la récupération de {element_symbol}: {e}")
        return False, None

def parse_and_save_data(element_symbol, raw_data, output_dir):
    """
    Parse les données brutes et les sauvegarde dans un fichier

    Args:
        element_symbol: Symbole de l'élément
        raw_data: Données brutes ASCII
        output_dir: Répertoire de sortie
    """
    if not raw_data:
        return

    lines = raw_data.split('\n')
    data_lines = []

    # Chercher le début des données (après les en-têtes)
    data_started = False
    for line in lines:
        line = line.strip()

        # Ignorer les lignes vides et les commentaires
        if not line or line.startswith('#'):
            continue

        # Détecter le début des données numériques
        # Format attendu: Energy   µ/rho   µen/rho
        if not data_started:
            # Chercher une ligne qui commence par un nombre
            if re.match(r'^\s*[\d.eE+-]+', line):
                data_started = True

        if data_started:
            # Parser la ligne de données
            parts = line.split()
            if len(parts) >= 3:
                try:
                    energy = float(parts[0])
                    mu_rho = float(parts[1])
                    mu_en_rho = float(parts[2])
                    data_lines.append(f"{energy:.6e}\t{mu_rho:.6e}\t{mu_en_rho:.6e}\n")
                except ValueError:
                    continue

    # Sauvegarder dans un fichier
    output_file = os.path.join(output_dir, f"{element_symbol}.txt")
    with open(output_file, 'w') as f:
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")
        f.writelines(data_lines)

    print(f"  ✓ Données sauvegardées dans {output_file} ({len(data_lines)} points)")

def main():
    """Fonction principale"""
    print("=== Récupération des données NIST ===\n")

    # Créer le répertoire de sortie
    output_dir = create_output_directory()
    print(f"Répertoire de sortie: {output_dir}\n")

    # Compteurs
    success_count = 0
    fail_count = 0

    # Parcourir tous les éléments
    for z_number, element_symbol in ELEMENTS.items():
        success, raw_data = get_element_data(z_number, element_symbol)

        if success and raw_data:
            parse_and_save_data(element_symbol, raw_data, output_dir)
            success_count += 1
        else:
            fail_count += 1

        # Pause pour éviter de surcharger le serveur
        time.sleep(0.5)

    print(f"\n=== Résumé ===")
    print(f"Éléments récupérés avec succès: {success_count}")
    print(f"Éléments en échec: {fail_count}")
    print(f"Total: {len(ELEMENTS)}")

if __name__ == "__main__":
    main()
