#!/usr/bin/env python3
"""
Test de xraylib pour vérifier les valeurs correctes
"""

import xraylib as xrl

# Test pour le fer à différentes énergies
element = 'Fe'
Z = 26  # Numéro atomique du fer

# Tester plusieurs énergies
test_energies_keV = [1, 10, 50, 100, 200, 500]  # keV

print(f"Tests pour {element} (Z={Z}):\n")
print(f"{'Energie (keV)':<15} {'Energie (MeV)':<15} {'µ/rho (cm²/g)':<20}")
print("-" * 50)

for energy_keV in test_energies_keV:
    try:
        # Calculer µ/rho (coefficient d'absorption massique total)
        mu_rho = xrl.CS_Total(Z, energy_keV)  # cm²/g
        energy_MeV = energy_keV / 1000
        print(f"{energy_keV:<15} {energy_MeV:<15.3f} {mu_rho:<20.6e}")
    except Exception as e:
        print(f"{energy_keV:<15} ERREUR: {e}")

# Valeur de référence NIST à 1 MeV
print(f"\nValeur NIST à 1 MeV (1000 keV): µ/rho ≈ 5.99E-2 cm²/g")
