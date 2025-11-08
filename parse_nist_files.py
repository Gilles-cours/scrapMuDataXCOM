#!/usr/bin/env python3
"""
Parse les fichiers NIST téléchargés manuellement
AUCUNE INTERPOLATION - données brutes uniquement
"""

import os
import re
from pathlib import Path

# Liste des éléments
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

def find_input_file(z_number, element_symbol, input_dir):
    """
    Cherche le fichier d'entrée avec différents patterns de nommage
    """
    possible_names = [
        f"{element_symbol}.txt",
        f"{element_symbol}.html",
        f"{element_symbol}.dat",
        f"z{z_number:02d}.txt",
        f"z{z_number:02d}.html",
        f"{element_symbol.lower()}.txt",
    ]

    for name in possible_names:
        filepath = os.path.join(input_dir, name)
        if os.path.exists(filepath):
            return filepath

    return None

def parse_nist_file(filepath):
    """
    Parse un fichier NIST et extrait les données brutes

    Format attendu du NIST:
    Energy    µ/rho    µen/rho    (éventuellement autres colonnes)
    (MeV)     (cm²/g)  (cm²/g)

    Retourne: liste de tuples (energie_MeV, mu_rho, mu_en_rho)
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  Erreur lecture fichier: {e}")
        return None

    lines = content.split('\n')
    data = []

    # État du parsing
    in_data_section = False
    header_found = False

    for line in lines:
        line = line.strip()

        # Ignorer lignes vides
        if not line:
            continue

        # Ignorer commentaires HTML
        if line.startswith('<') or line.startswith('!'):
            continue

        # Détecter l'en-tête avec "Energy" ou "MeV"
        if not header_found:
            if re.search(r'(Energy|MeV|keV)', line, re.IGNORECASE):
                header_found = True
                # La ligne de données commence après l'en-tête
                continue

        # Si on a trouvé l'en-tête, commencer à chercher les données
        if header_found:
            # Chercher lignes qui commencent par un nombre (scientifique ou décimal)
            # Format: nombre blanc nombre blanc nombre
            match = re.match(r'^\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)', line)

            if match:
                try:
                    # Énergie en MeV
                    energy = float(match.group(1))
                    mu_rho = float(match.group(2))
                    mu_en_rho = float(match.group(3))

                    # Vérifier que les valeurs sont raisonnables
                    if energy > 0 and mu_rho > 0:
                        data.append((energy, mu_rho, mu_en_rho))

                except (ValueError, IndexError):
                    # Ligne mal formatée, ignorer
                    continue

    return data if len(data) > 0 else None

def save_parsed_data(element_symbol, data, output_dir):
    """
    Sauvegarde les données parsées sans modification
    """
    output_file = os.path.join(output_dir, f"{element_symbol}.txt")

    with open(output_file, 'w') as f:
        f.write("# Données NIST brutes (AUCUNE interpolation)\n")
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")

        for energy, mu_rho, mu_en_rho in data:
            f.write(f"{energy:.6e}\t{mu_rho:.6e}\t{mu_en_rho:.6e}\n")

    return True

def main():
    """Fonction principale"""
    print("=== Parsing des fichiers NIST téléchargés manuellement ===\n")

    # Répertoires
    input_dir = "nist_raw_data"
    output_dir = "nist_data_parsed"

    # Vérifier que le répertoire d'entrée existe
    if not os.path.exists(input_dir):
        print(f"ERREUR: Le répertoire '{input_dir}' n'existe pas!")
        print(f"Créez-le et placez-y les fichiers téléchargés depuis NIST.")
        print(f"\nConsultez GUIDE_TELECHARGEMENT_MANUEL.md pour les instructions.")
        return

    # Créer le répertoire de sortie
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Répertoire d'entrée: {input_dir}")
    print(f"Répertoire de sortie: {output_dir}\n")

    success_count = 0
    fail_count = 0
    not_found_count = 0

    # Parcourir tous les éléments
    for z_number, element_symbol in ELEMENTS.items():
        print(f"Traitement de {element_symbol} (Z={z_number})...")

        # Chercher le fichier d'entrée
        input_file = find_input_file(z_number, element_symbol, input_dir)

        if not input_file:
            print(f"  ⚠ Fichier non trouvé")
            not_found_count += 1
            continue

        print(f"  Fichier trouvé: {input_file}")

        # Parser le fichier
        data = parse_nist_file(input_file)

        if data:
            # Sauvegarder
            save_parsed_data(element_symbol, data, output_dir)
            print(f"  ✓ {len(data)} points extraits et sauvegardés")
            success_count += 1
        else:
            print(f"  ✗ Aucune donnée extraite (vérifiez le format du fichier)")
            fail_count += 1

    print(f"\n=== Résumé ===")
    print(f"Succès: {success_count}")
    print(f"Échecs: {fail_count}")
    print(f"Non trouvés: {not_found_count}")
    print(f"Total: {len(ELEMENTS)}")

    if success_count > 0:
        print(f"\n✓ Les données parsées sont dans: {output_dir}/")
        print(f"  Utilisez ces fichiers avec example_usage.py")

if __name__ == "__main__":
    main()
