from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from tqdm import tqdm
import sys
import io

# Fix pour l'encodage Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ClinicalTrialsScraper:
    def __init__(self):
        """Initialise le driver Chrome"""
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.all_studies = []
        
    def get_total_results(self, url):
        """Récupère le nombre total d'études"""
        self.driver.get(url)
        time.sleep(3)  # Attendre le chargement
        
        try:
            # Chercher le nombre total d'études
            search_details = self.driver.find_element(By.CLASS_NAME, "search-terms").find_element(By.XPATH, "..")
            total_text = search_details.text
            # Extraire le nombre (ex: "Viewing 1-10 out of 13,559 studies")
            total = int(total_text.split("out of")[1].split("studies")[0].strip().replace(",", ""))
            print(f"Total d'etudes a scraper: {total}")
            return total
        except Exception as e:
            print(f"Erreur lors de la recuperation du total: {e}")
            return 0
    
    def scrape_current_page(self):
        """Scrape toutes les études de la page actuelle"""
        try:
            # Attendre que les cartes soient chargées
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "ctg-search-hit-card")))
            time.sleep(2)  # Petit délai supplémentaire
            
            # Récupérer toutes les cartes d'études
            study_cards = self.driver.find_elements(By.TAG_NAME, "ctg-search-hit-card")
            
            for card in study_cards:
                try:
                    study_data = {}
                    
                    # NCT ID
                    try:
                        study_data['nct_id'] = card.find_element(By.CLASS_NAME, "nct-id").text
                    except:
                        study_data['nct_id'] = None
                    
                    # Titre
                    try:
                        study_data['title'] = card.find_element(By.CLASS_NAME, "hit-card-title").text
                    except:
                        study_data['title'] = None
                    
                    # Statut
                    try:
                        status_elem = card.find_element(By.TAG_NAME, "ctg-overall-status")
                        study_data['status'] = status_elem.find_element(By.TAG_NAME, "span").text
                    except:
                        study_data['status'] = None
                    
                    # Nouveau (badge "New")
                    try:
                        card.find_element(By.TAG_NAME, "ctg-new-pill")
                        study_data['is_new'] = True
                    except:
                        study_data['is_new'] = False
                    
                    # Conditions
                    try:
                        conditions_container = card.find_element(By.TAG_NAME, "ctg-conditions")
                        condition_elements = conditions_container.find_elements(By.CSS_SELECTOR, ".condition-text-mark, .condition-text")
                        conditions = [elem.text.strip() for elem in condition_elements if elem.text.strip()]
                        study_data['conditions'] = " | ".join(conditions) if conditions else None
                    except:
                        study_data['conditions'] = None
                    
                    # Localisations
                    try:
                        locations_container = card.find_element(By.TAG_NAME, "ctg-locations")
                        location_elements = locations_container.find_elements(By.CLASS_NAME, "location-text")
                        locations = []
                        for loc in location_elements:
                            loc_text = loc.find_element(By.TAG_NAME, "span").text
                            locations.append(loc_text)
                        study_data['locations'] = " | ".join(locations) if locations else None
                        study_data['num_locations'] = len(locations) if locations else 0
                    except:
                        study_data['locations'] = None
                        study_data['num_locations'] = 0
                    
                    # URL de l'étude
                    try:
                        study_url = card.find_element(By.CLASS_NAME, "hit-card-title").get_attribute("href")
                        study_data['url'] = study_url
                    except:
                        study_data['url'] = None
                    
                    self.all_studies.append(study_data)
                    
                except Exception as e:
                    print(f"Erreur lors du scraping d'une carte: {e}")
                    continue
            
            return len(study_cards)
        
        except Exception as e:
            print(f"Erreur lors du scraping de la page: {e}")
            return 0
    
    def click_next_page(self):
        """Clique sur le bouton 'Next' pour aller à la page suivante"""
        try:
            # Scroller vers le bas pour s'assurer que la pagination est visible
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Chercher le bouton "Next" directement
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button.usa-pagination__next-page[aria-label='Next page']")
            
            # Vérifier si le bouton parent (li) est caché (dernière page)
            parent_li = next_button.find_element(By.XPATH, "..")
            if parent_li.get_attribute("style") and "visibility: hidden" in parent_li.get_attribute("style"):
                print("Bouton 'Next' cache - derniere page atteinte")
                return False
            
            # Cliquer sur le bouton avec JavaScript pour éviter les problèmes
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Attendre le chargement de la nouvelle page
            
            # Scroller vers le haut
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            return True
            
        except NoSuchElementException:
            print("Bouton 'Next' non trouve - derniere page atteinte")
            return False
        except Exception as e:
            print(f"Erreur lors du clic sur 'Next': {e}")
            return False
        
    def scrape_all_pages(self, cancer_type, max_pages=None):
        """
        Scrape toutes les pages pour un type de cancer donné
        
        Args:
            cancer_type: Type de cancer à rechercher (ex: "Lung Cancer", "Breast Cancer")
            max_pages: Nombre maximum de pages à scraper (None = toutes)
        """
        # Construire l'URL
        base_url = f"https://clinicaltrials.gov/search?cond={cancer_type.replace(' ', '%20')}"
        
        print(f"\n{'='*60}")
        print(f"Scraping de: {cancer_type}")
        print(f"{'='*60}\n")
        
        # Récupérer le nombre total d'études
        total_studies = self.get_total_results(base_url)
        
        if total_studies == 0:
            print("Aucune etude trouvee ou erreur")
            return
        
        # Scraper page par page
        page_num = 1
        with tqdm(total=total_studies, desc=f"Scraping {cancer_type}") as pbar:
            while True:
                if max_pages and page_num > max_pages:
                    print(f"\nLimite de {max_pages} pages atteinte")
                    break
                
                print(f"\nPage {page_num}...")
                studies_scraped = self.scrape_current_page()
                pbar.update(studies_scraped)
                
                # Essayer d'aller à la page suivante
                if not self.click_next_page():
                    print("\nDerniere page atteinte!")
                    break
                
                page_num += 1
        
        print(f"\n[OK] Total scraped: {len(self.all_studies)} etudes")
    
    def save_to_csv(self, filename):
        """Sauvegarde les données dans un fichier CSV"""
        if not self.all_studies:
            print("Aucune donnee a sauvegarder")
            return
        
        df = pd.DataFrame(self.all_studies)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig pour Excel
        print(f"\n[OK] Donnees sauvegardees dans: {filename}")
        
        # Afficher un aperçu des données
        print(f"\nApercu des donnees:")
        print(f"- Nombre total d'etudes: {len(df)}")
        print(f"- Colonnes: {list(df.columns)}")
        print(f"\nRepartition des statuts:")
        print(df['status'].value_counts())
        
    def close(self):
        """Ferme le navigateur"""
        self.driver.quit()
        print("\n[OK] Navigateur ferme")


# ====================
# UTILISATION
# ====================

if __name__ == "__main__":
    # Liste des cancers à scraper
    cancers = [
        "Lung Cancer",
        "Breast Cancer",
        "Pancreatic Cancer",
        "Colorectal Cancer",
        "Prostate Cancer",
    ]
    
    # Créer le scraper
    scraper = ClinicalTrialsScraper()
    
    try:
        # Option 1: Scraper UN SEUL cancer (pour tester)
        scraper.scrape_all_pages("Lung Cancer", max_pages=5)  # Limite à 5 pages pour test
        scraper.save_to_csv("data/lung_cancer_trials.csv")
        
        # Option 2: Scraper TOUS les cancers (décommenter pour utiliser)
        # for cancer in cancers:
        #     scraper.scrape_all_pages(cancer)  # Pas de limite de pages
        # scraper.save_to_csv("all_cancer_trials.csv")
        
    except Exception as e:
        print(f"ERREUR: {e}")
    finally:
        scraper.close()