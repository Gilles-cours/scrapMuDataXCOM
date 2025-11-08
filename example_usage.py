#!/usr/bin/env python3
"""
Script d'exemple pour utiliser les données de coefficients d'absorption
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def load_element_data(element_symbol, data_dir='nist_data'):
    """
    Charge les données pour un élément donné

    Args:
        element_symbol: Symbole de l'élément (ex: 'Fe', 'Pb', 'C')
        data_dir: Répertoire contenant les données

    Returns:
        dict: Dictionnaire avec 'energie', 'mu_rho', 'mu_en_rho'
    """
    filepath = os.path.join(data_dir, f"{element_symbol}.txt")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier {filepath} non trouvé")

    # Charger les données
    data = np.loadtxt(filepath, skiprows=1)

    return {
        'energie': data[:, 0],      # MeV
        'mu_rho': data[:, 1],       # cm²/g
        'mu_en_rho': data[:, 2]     # cm²/g
    }

def plot_single_element(element_symbol):
    """
    Trace les coefficients pour un seul élément

    Args:
        element_symbol: Symbole de l'élément
    """
    data = load_element_data(element_symbol)

    plt.figure(figsize=(10, 6))
    plt.loglog(data['energie'], data['mu_rho'], 'b-', linewidth=2, label='µ/rho')
    plt.loglog(data['energie'], data['mu_en_rho'], 'r--', linewidth=2, label='µen/rho')

    plt.xlabel('Énergie (MeV)', fontsize=12)
    plt.ylabel('Coefficient (cm²/g)', fontsize=12)
    plt.title(f'Coefficients d\'absorption pour {element_symbol}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, which='both', alpha=0.3)
    plt.tight_layout()

    # Sauvegarder
    plt.savefig(f'plot_{element_symbol}.png', dpi=150)
    print(f"Graphique sauvegardé: plot_{element_symbol}.png")

    plt.show()

def plot_multiple_elements(elements):
    """
    Compare les coefficients µ/rho pour plusieurs éléments

    Args:
        elements: Liste de symboles d'éléments
    """
    plt.figure(figsize=(12, 7))

    colors = plt.cm.tab10(np.linspace(0, 1, len(elements)))

    for i, element in enumerate(elements):
        try:
            data = load_element_data(element)
            plt.loglog(data['energie'], data['mu_rho'],
                      linewidth=2, label=element, color=colors[i])
        except FileNotFoundError:
            print(f"Données non trouvées pour {element}")

    plt.xlabel('Énergie (MeV)', fontsize=12)
    plt.ylabel('µ/rho (cm²/g)', fontsize=12)
    plt.title('Comparaison des coefficients d\'absorption massique', fontsize=14)
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, which='both', alpha=0.3)
    plt.tight_layout()

    plt.savefig('plot_comparison.png', dpi=150)
    print("Graphique sauvegardé: plot_comparison.png")

    plt.show()

def get_coefficient_at_energy(element_symbol, energy_mev):
    """
    Obtient les coefficients à une énergie donnée (par interpolation)

    Args:
        element_symbol: Symbole de l'élément
        energy_mev: Énergie en MeV

    Returns:
        dict: Coefficients interpolés
    """
    data = load_element_data(element_symbol)

    # Interpolation logarithmique
    mu_rho_interp = np.interp(
        np.log10(energy_mev),
        np.log10(data['energie']),
        np.log10(data['mu_rho'])
    )

    mu_en_rho_interp = np.interp(
        np.log10(energy_mev),
        np.log10(data['energie']),
        np.log10(data['mu_en_rho'])
    )

    return {
        'energie': energy_mev,
        'mu_rho': 10**mu_rho_interp,
        'mu_en_rho': 10**mu_en_rho_interp
    }

def print_statistics(element_symbol):
    """
    Affiche des statistiques sur les coefficients

    Args:
        element_symbol: Symbole de l'élément
    """
    data = load_element_data(element_symbol)

    print(f"\n=== Statistiques pour {element_symbol} ===")
    print(f"Nombre de points: {len(data['energie'])}")
    print(f"\nPlage d'énergie:")
    print(f"  Min: {data['energie'].min():.6e} MeV")
    print(f"  Max: {data['energie'].max():.6e} MeV")
    print(f"\nµ/rho (cm²/g):")
    print(f"  Min: {data['mu_rho'].min():.6e}")
    print(f"  Max: {data['mu_rho'].max():.6e}")
    print(f"  Moyenne: {data['mu_rho'].mean():.6e}")
    print(f"\nµen/rho (cm²/g):")
    print(f"  Min: {data['mu_en_rho'].min():.6e}")
    print(f"  Max: {data['mu_en_rho'].max():.6e}")
    print(f"  Moyenne: {data['mu_en_rho'].mean():.6e}")

def main():
    """Fonction principale avec exemples"""
    print("=== Exemples d'utilisation des données NIST ===\n")

    # Exemple 1: Statistiques pour le fer
    print("Exemple 1: Statistiques pour le Fer (Fe)")
    print_statistics('Fe')

    # Exemple 2: Interpolation à une énergie donnée
    print("\n\nExemple 2: Coefficients à 100 keV pour différents éléments")
    elements_test = ['C', 'Al', 'Fe', 'Pb']
    energy = 0.1  # MeV (100 keV)

    print(f"\nÉnergie: {energy} MeV ({energy*1000} keV)\n")
    print(f"{'Élément':<10} {'µ/rho (cm²/g)':<15} {'µen/rho (cm²/g)':<15}")
    print("-" * 45)

    for elem in elements_test:
        try:
            coef = get_coefficient_at_energy(elem, energy)
            print(f"{elem:<10} {coef['mu_rho']:<15.6e} {coef['mu_en_rho']:<15.6e}")
        except FileNotFoundError:
            print(f"{elem:<10} Données non disponibles")

    # Exemple 3: Graphique pour un élément
    print("\n\nExemple 3: Génération de graphique pour le Plomb (Pb)")
    try:
        plot_single_element('Pb')
    except Exception as e:
        print(f"Erreur lors de la génération du graphique: {e}")

    # Exemple 4: Comparaison de plusieurs éléments
    print("\nExemple 4: Comparaison de plusieurs éléments")
    elements_compare = ['C', 'Al', 'Cu', 'Pb', 'U']
    try:
        plot_multiple_elements(elements_compare)
    except Exception as e:
        print(f"Erreur lors de la génération du graphique: {e}")

    print("\n=== Fin des exemples ===")

if __name__ == "__main__":
    # Vérifier que matplotlib est installé
    try:
        import matplotlib
        main()
    except ImportError:
        print("Pour utiliser les fonctions de visualisation, installez matplotlib:")
        print("  pip install matplotlib")
        print("\nVous pouvez toujours utiliser les fonctions de chargement de données:")
        print("\nExemple:")
        print("  from example_usage import load_element_data")
        print("  data = load_element_data('Fe')")
        print("  print(data)")
