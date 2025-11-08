#!/usr/bin/env python3
"""
Téléchargement automatique avec Selenium (simule un vrai navigateur)
Nécessite: Chrome/Chromium + ChromeDriver
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium n'est pas installé.")
    print("Installez-le avec: pip install selenium")

import time
import os
import re

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

def setup_driver(headless=True):
    """Configure le driver Selenium"""
    if not SELENIUM_AVAILABLE:
        return None

    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Erreur lors de l'initialisation du driver: {e}")
        print("\nAssurez-vous que:")
        print("  1. Chrome/Chromium est installé")
        print("  2. ChromeDriver est installé et dans le PATH")
        print("  3. Les versions de Chrome et ChromeDriver sont compatibles")
        return None

def download_element_data(driver, z_number, element_symbol, output_dir):
    """
    Télécharge les données pour un élément via Selenium
    """
    url = f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{z_number:02d}.html"

    try:
        print(f"Accès à {url}...")
        driver.get(url)

        # Attendre que la page se charge
        time.sleep(2)

        # Récupérer tout le texte de la page
        page_source = driver.page_source

        # Sauvegarder la page brute
        output_file = os.path.join(output_dir, f"{element_symbol}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_source)

        print(f"  ✓ Page sauvegardée: {output_file}")
        return True

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    if not SELENIUM_AVAILABLE:
        return

    print("=== Téléchargement avec Selenium ===\n")

    # Répertoire de sortie
    output_dir = "nist_raw_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Configurer le driver
    print("Initialisation du navigateur...")
    driver = setup_driver(headless=True)

    if not driver:
        print("\nImpossible de démarrer Selenium.")
        return

    print(f"✓ Navigateur démarré\n")
    print(f"Répertoire de sortie: {output_dir}\n")

    success_count = 0
    fail_count = 0

    try:
        # Télécharger pour quelques éléments d'abord (test)
        test_elements = [(1, 'H'), (6, 'C'), (26, 'Fe'), (82, 'Pb')]

        print("Test avec quelques éléments...\n")

        for z_number, element_symbol in test_elements:
            print(f"Traitement de {element_symbol} (Z={z_number})...")

            if download_element_data(driver, z_number, element_symbol, output_dir):
                success_count += 1
            else:
                fail_count += 1

            # Pause pour ne pas surcharger le serveur
            time.sleep(3)

        print(f"\n=== Résultats du test ===")
        print(f"Succès: {success_count}/{len(test_elements)}")

        if success_count > 0:
            print(f"\n✓ Le téléchargement fonctionne!")
            print(f"\nUtilisez maintenant:")
            print(f"  python parse_nist_files.py")
            print(f"\nPour télécharger TOUS les éléments, modifiez ce script")
            print(f"pour boucler sur ELEMENTS.items() au lieu de test_elements")
        else:
            print(f"\n✗ Le téléchargement a échoué")
            print(f"Le site NIST bloque peut-être même Selenium...")

    finally:
        # Fermer le driver
        driver.quit()
        print("\nNavigateur fermé")

if __name__ == "__main__":
    main()
