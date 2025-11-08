#!/usr/bin/env python3
"""
Script pour récupérer les coefficients d'absorption en utilisant la bibliothèque xraydb
qui contient les données NIST/XCOM
"""

try:
    import xraydb
    XRAYDB_AVAILABLE = True
except ImportError:
    XRAYDB_AVAILABLE = False
    print("La bibliothèque xraydb n'est pas installée.")
    print("Installez-la avec: pip install xraydb")

import numpy as np
import os

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

def create_output_directory():
    """Crée le répertoire de sortie"""
    output_dir = "nist_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_element_data_xraydb(element_symbol):
    """
    Récupère les données µ/rho et µen/rho pour un élément avec xraydb

    Args:
        element_symbol: Symbole de l'élément

    Returns:
        tuple: (energies, mu_rho, mu_en_rho) ou None
    """
    if not XRAYDB_AVAILABLE:
        return None

    try:
        # Créer une grille d'énergies logarithmique de 1 keV à 20 MeV
        energies_kev = np.logspace(np.log10(1), np.log10(20000), 200)  # keV
        energies_mev = energies_kev / 1000.0  # Convertir en MeV

        # Récupérer les coefficients d'absorption massique
        mu_rho = []
        mu_en_rho = []

        for e_kev in energies_kev:
            try:
                # mu_total en cm²/g
                mu_val = xraydb.mu_elam(element_symbol, e_kev, kind='total')
                mu_rho.append(mu_val)

                # mu_en (coefficient d'absorption d'énergie) en cm²/g
                # Note: xraydb peut ne pas avoir directement mu_en, on utilise mu_photo comme approximation
                mu_en_val = xraydb.mu_elam(element_symbol, e_kev, kind='photo')
                mu_en_rho.append(mu_en_val)

            except Exception:
                # Si l'énergie n'est pas disponible, utiliser NaN
                mu_rho.append(np.nan)
                mu_en_rho.append(np.nan)

        # Filtrer les valeurs NaN
        valid_indices = ~(np.isnan(mu_rho) | np.isnan(mu_en_rho))
        energies_mev = energies_mev[valid_indices]
        mu_rho = np.array(mu_rho)[valid_indices]
        mu_en_rho = np.array(mu_en_rho)[valid_indices]

        return energies_mev, mu_rho, mu_en_rho

    except Exception as e:
        print(f"  Erreur avec xraydb: {e}")
        return None

def save_data(element_symbol, energies, mu_rho, mu_en_rho, output_dir):
    """Sauvegarde les données dans un fichier"""
    if energies is None or len(energies) == 0:
        return False

    output_file = os.path.join(output_dir, f"{element_symbol}.txt")

    with open(output_file, 'w') as f:
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")
        for e, mu, mu_en in zip(energies, mu_rho, mu_en_rho):
            f.write(f"{e:.6e}\t{mu:.6e}\t{mu_en:.6e}\n")

    print(f"  ✓ Données sauvegardées: {output_file} ({len(energies)} points)")
    return True

def main():
    """Fonction principale"""
    print("=== Récupération des données avec xraydb ===\n")

    if not XRAYDB_AVAILABLE:
        print("\nInstallez xraydb avec:")
        print("  pip install xraydb")
        return

    output_dir = create_output_directory()
    print(f"Répertoire de sortie: {output_dir}\n")

    success_count = 0
    fail_count = 0

    # Récupérer les données pour tous les éléments
    for z_number, element_symbol in ELEMENTS.items():
        print(f"Traitement de {element_symbol} (Z={z_number})...")

        result = get_element_data_xraydb(element_symbol)

        if result:
            energies, mu_rho, mu_en_rho = result
            if save_data(element_symbol, energies, mu_rho, mu_en_rho, output_dir):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"  ✗ Échec pour {element_symbol}")
            fail_count += 1

    print(f"\n=== Résumé ===")
    print(f"Succès: {success_count}")
    print(f"Échecs: {fail_count}")
    print(f"Total: {len(ELEMENTS)}")

if __name__ == "__main__":
    main()
