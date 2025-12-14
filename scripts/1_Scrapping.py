import time
import pandas as pd
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# ==========================================
# 🔧 CONFIGURATION DU PROJET
# ==========================================
LISTE_MALADIES = [
    "Lung Cancer", 
    "Breast Cancer", 
    "Pancreatic Cancer",
    "Leukemia",
    "Prostate Cancer"
]

NB_PAGES_PAR_MALADIE = 30
NOM_FICHIER_SORTIE = "data/scraping/FINAL_DATASET_CANCER.csv"

# ==========================================
# 🧠 LE ROBOT BLINDÉ
# ==========================================
class UltimateScraper:
    def __init__(self):
        print("🤖 Initialisation du robot...")
        self.setup_driver()
        self.all_data = []

    def setup_driver(self):
        """Configure et lance Chrome (utilisé au début et pour redémarrer)"""
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--headless") # Décommente pour mode sans fenêtre
        self.options.add_argument("--window-size=1920,1080")
        # Anti-detection basique
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        except Exception as e:
            print(f"❌ Erreur au lancement du driver: {e}")

    def verifier_et_reparer_driver(self):
        """Vérifie si Chrome est vivant. Si non, le relance."""
        try:
            # On essaie une commande simple pour voir si ça répond
            self.driver.current_url
        except:
            print("\n🚑 ALERTE : Le navigateur ne répond plus ! Redémarrage d'urgence...")
            try:
                self.driver.quit()
            except:
                pass
            # On relance
            self.setup_driver()
            print("✅ Navigateur relancé. On reprend.")

    def recuperer_urls_dune_page(self, maladie, page_num):
        # Vérification santé avant d'agir
        self.verifier_et_reparer_driver()
        
        url = f"https://clinicaltrials.gov/search?cond={maladie.replace(' ', '%20')}&viewType=Card&page={page_num}"
        
        try:
            self.driver.get(url)
            urls_page = []
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".usa-card__container"))
            )
            time.sleep(2)
            
            elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/study/')]")
            for el in elements:
                href = el.get_attribute('href')
                if href and "/study/" in href and "#" not in href:
                    if href not in urls_page:
                        urls_page.append(href)
            
            print(f"   PAGE {page_num}: {len(urls_page)} liens trouvés.")
            return urls_page
            
        except Exception:
            # Si ça plante sur une page liste, on retourne vide et on continue
            return []

    def aspirer_details_fiche(self, url, maladie):
        # Vérification santé avant d'agir
        self.verifier_et_reparer_driver()
        
        info = {
            "Maladie": maladie,
            "Titre": "Titre Inconnu",
            "Statut": "Inconnu",
            "Sponsor": "Non spécifié",
            "URL": url
        }

        try:
            self.driver.get(url)
            
            # Attente chargement
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(0.5)

            # 1. TITRE
            titre_page = self.driver.title
            if "-" in titre_page:
                info["Titre"] = titre_page.rsplit('-', 1)[0].strip()
            else:
                info["Titre"] = titre_page

            # 2. SCANNER LE TEXTE
            texte_brut = self.driver.find_element(By.TAG_NAME, "body").text
            lignes = texte_brut.split('\n')

            # Recherche du STATUT
            if "Recruiting" in texte_brut: info["Statut"] = "Recruiting"
            elif "Completed" in texte_brut: info["Statut"] = "Completed"
            elif "Active, not recruiting" in texte_brut: info["Statut"] = "Active"
            elif "Terminated" in texte_brut: info["Statut"] = "Terminated"
            elif "Withdrawn" in texte_brut: info["Statut"] = "Withdrawn"

            # Recherche du SPONSOR
            for i, ligne in enumerate(lignes):
                ligne = ligne.strip()
                if ligne.startswith("Lead Sponsor") or ligne.startswith("Responsible Party") or ligne.startswith("Sponsor"):
                    if ":" in ligne:
                        try:
                            candidat = ligne.split(":", 1)[1].strip()
                            if len(candidat) > 2:
                                info["Sponsor"] = candidat
                                break
                        except: pass
                    elif i + 1 < len(lignes):
                        candidat_next = lignes[i+1].strip()
                        if len(candidat_next) > 2 and "NCT" not in candidat_next:
                            info["Sponsor"] = candidat_next
                            break
                            
            print(f"      ✅ Sponsor: {info['Sponsor']}")

        except Exception as e:
            print(f"      ❌ Erreur fiche (passé): {e}")

        return info

    def lancer_mission(self):
        try:
            # Si un fichier existe déjà, on prévient (pour ne pas écraser bêtement si tu relances)
            if os.path.exists(NOM_FICHIER_SORTIE):
                print(f"⚠️ Attention : Le fichier {NOM_FICHIER_SORTIE} existe déjà.")
            
            compteur_total = 0
            
            for maladie in LISTE_MALADIES:
                print(f"\n🔬 TRAITEMENT DE : {maladie}")
                print("="*40)
                
                # ÉTAPE 1 : Récupérer les liens
                liens_a_visiter = []
                for page in range(1, NB_PAGES_PAR_MALADIE + 1):
                    liens = self.recuperer_urls_dune_page(maladie, page)
                    liens_a_visiter.extend(liens)
                
                print(f"   👉 Total à analyser : {len(liens_a_visiter)} liens.")
                
                # ÉTAPE 2 : Visiter chaque lien
                for index, lien in enumerate(liens_a_visiter):
                    donnees = self.aspirer_details_fiche(lien, maladie)
                    self.all_data.append(donnees)
                    compteur_total += 1
                    
                    # SÉCURITÉ : Sauvegarde tous les 10 essais !
                    if compteur_total % 10 == 0:
                        self.sauvegarder()
                
                # Sauvegarde aussi à la fin de chaque maladie
                self.sauvegarder()

        except KeyboardInterrupt:
            print("\n🛑 Arrêt manuel demandé. Sauvegarde en cours...")
            self.sauvegarder()
            
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
            print("\n👋 Robot arrêté.")

    def sauvegarder(self):
        if self.all_data:
            df = pd.DataFrame(self.all_data)
            cols = ["Maladie", "Sponsor", "Statut", "Titre", "URL"]
            cols_finales = [c for c in cols if c in df.columns]
            df = df[cols_finales]
            
            df.to_csv(NOM_FICHIER_SORTIE, index=False, encoding='utf-8-sig')
            print(f"💾 Sauvegarde auto ({len(df)} lignes)...")

# ==========================================
# 🚀 LANCEMENT
# ==========================================
if __name__ == "__main__":
    bot = UltimateScraper()
    bot.lancer_mission()