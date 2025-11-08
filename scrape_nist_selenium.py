#!/usr/bin/env python3
"""
Script pour récupérer les coefficients d'absorption massique (µ/rho) et
d'absorption d'énergie massique (µen/rho) depuis le site NIST avec Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

def setup_driver():
    """Configure et retourne un driver Selenium"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Mode sans interface graphique
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Erreur lors de l'initialisation du driver: {e}")
        print("Assurez-vous que Chrome et ChromeDriver sont installés")
        return None

def create_output_directory():
    """Crée le répertoire de sortie pour les données"""
    output_dir = "nist_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_element_data_selenium(driver, z_number, element_symbol):
    """
    Récupère les données µ/rho et µen/rho pour un élément donné avec Selenium

    Args:
        driver: WebDriver Selenium
        z_number: Numéro atomique de l'élément
        element_symbol: Symbole de l'élément

    Returns:
        str: Données texte ou None en cas d'erreur
    """
    url = f"https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z{z_number:02d}.html"

    try:
        print(f"Récupération des données pour {element_symbol} (Z={z_number})...")
        driver.get(url)

        # Attendre que la page se charge
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Chercher un lien vers les données texte/ASCII
        try:
            # Chercher tous les liens
            links = driver.find_elements(By.TAG_NAME, "a")

            for link in links:
                text = link.text.strip().lower()
                href = link.get_attribute('href')

                if 'text' in text or 'ascii' in text or 'table' in text:
                    print(f"  Trouvé lien: {text} -> {href}")
                    # Cliquer sur le lien ou ouvrir l'URL
                    driver.get(href)
                    time.sleep(1)

                    # Récupérer le contenu de la page
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    return page_text

            # Si pas de lien trouvé, essayer de récupérer les données de la page actuelle
            # Chercher un élément <pre> qui pourrait contenir les données
            try:
                pre_element = driver.find_element(By.TAG_NAME, "pre")
                return pre_element.text
            except NoSuchElementException:
                # Sinon, récupérer tout le texte de la page
                return driver.find_element(By.TAG_NAME, "body").text

        except Exception as e:
            print(f"  Erreur lors de la recherche des données: {e}")
            return None

    except TimeoutException:
        print(f"  Timeout lors du chargement de la page pour {element_symbol}")
        return None
    except Exception as e:
        print(f"  Erreur lors de la récupération de {element_symbol}: {e}")
        return None

def parse_and_save_data(element_symbol, raw_data, output_dir):
    """
    Parse les données brutes et les sauvegarde dans un fichier

    Args:
        element_symbol: Symbole de l'élément
        raw_data: Données brutes
        output_dir: Répertoire de sortie
    """
    if not raw_data:
        return False

    lines = raw_data.split('\n')
    data_lines = []

    # Chercher le début des données (après les en-têtes)
    data_started = False
    for line in lines:
        line = line.strip()

        # Ignorer les lignes vides
        if not line:
            continue

        # Détecter le début des données numériques
        if not data_started:
            # Chercher une ligne qui commence par un nombre (format scientifique ou décimal)
            if re.match(r'^\s*[\d.eE+-]+\s+[\d.eE+-]+\s+[\d.eE+-]+', line):
                data_started = True

        if data_started:
            # Parser la ligne de données
            # Format attendu: Energy   µ/rho   µen/rho (et potentiellement d'autres colonnes)
            parts = line.split()
            if len(parts) >= 3:
                try:
                    energy = float(parts[0])
                    mu_rho = float(parts[1])
                    mu_en_rho = float(parts[2])
                    data_lines.append(f"{energy:.6e}\t{mu_rho:.6e}\t{mu_en_rho:.6e}\n")
                except (ValueError, IndexError):
                    continue

    if len(data_lines) == 0:
        print(f"  ⚠ Aucune donnée numérique trouvée pour {element_symbol}")
        return False

    # Sauvegarder dans un fichier
    output_file = os.path.join(output_dir, f"{element_symbol}.txt")
    with open(output_file, 'w') as f:
        f.write("# Energie (MeV)\tµ/rho (cm²/g)\tµen/rho (cm²/g)\n")
        f.writelines(data_lines)

    print(f"  ✓ Données sauvegardées dans {output_file} ({len(data_lines)} points)")
    return True

def main():
    """Fonction principale"""
    print("=== Récupération des données NIST avec Selenium ===\n")

    # Configurer le driver
    driver = setup_driver()
    if not driver:
        print("Impossible de démarrer le navigateur. Arrêt du programme.")
        return

    # Créer le répertoire de sortie
    output_dir = create_output_directory()
    print(f"Répertoire de sortie: {output_dir}\n")

    # Compteurs
    success_count = 0
    fail_count = 0

    try:
        # Parcourir tous les éléments (ou un sous-ensemble pour test)
        for z_number, element_symbol in ELEMENTS.items():
            raw_data = get_element_data_selenium(driver, z_number, element_symbol)

            if raw_data:
                if parse_and_save_data(element_symbol, raw_data, output_dir):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1

            # Pause pour éviter de surcharger le serveur
            time.sleep(1)

    finally:
        # Fermer le driver
        driver.quit()

    print(f"\n=== Résumé ===")
    print(f"Éléments récupérés avec succès: {success_count}")
    print(f"Éléments en échec: {fail_count}")
    print(f"Total: {len(ELEMENTS)}")

if __name__ == "__main__":
    main()
