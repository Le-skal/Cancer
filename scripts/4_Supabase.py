import os
import sys
import json
import pandas as pd
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Logger:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @staticmethod
    def info(text): print(f"{Logger.BLUE}i  {text}{Logger.END}")
    @staticmethod
    def success(text): print(f"{Logger.GREEN}+ {text}{Logger.END}")
    @staticmethod
    def error(text): print(f"{Logger.RED}x {text}{Logger.END}")
    @staticmethod
    def warning(text): print(f"{Logger.YELLOW}!  {text}{Logger.END}")
    @staticmethod
    def header(text): print(f"\n{Logger.BOLD}{Logger.CYAN}{'='*60}\n {text}\n{'='*60}{Logger.END}\n")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "VOTRE_SUPABASE_URL_ICI")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "VOTRE_SUPABASE_ANON_KEY_ICI")

if "VOTRE_SUPABASE" in SUPABASE_URL or "VOTRE_SUPABASE" in SUPABASE_KEY:
    Logger.warning("Attention: Identifiants Supabase non configurés.")

FILES_MAP = {
    "cancer_mortality_2022.csv": "cancer_mortality",
    "cancer_research_vs_mortality.csv": "research_vs_mortality",
    "clinical_trials_clean.csv": "clinical_trials",
    "clinical_trials_geography_count.csv": "geography_count",
    "clinical_trials_geography_percentage.csv": "geography_percentage",
    "google_trends_comparison.csv": "google_trends",
    "nci_budget_2023.csv": "nci_budget",
    "trials_count_by_cancer.csv": "trials_count"
}

def push_to_supabase():
    Logger.header("ENVOI DES DONNÉES VERS SUPABASE (API REST)")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data_clean")

    if not os.path.exists(data_dir):
        Logger.error(f"Dossier {data_dir} introuvable.")
        return

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" 
    }

    success_count = 0
    total_files = len(FILES_MAP)

    for filename, table_name in FILES_MAP.items():
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            Logger.warning(f"Fichier manquant: {filename}")
            continue

        Logger.info(f"Traitement de {filename} -> {table_name}")
        
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower()
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient='records')
            total_records = len(records)
            
            if total_records == 0:
                Logger.warning(f"  Fichier vide: {filename}")
                continue

            BATCH_SIZE = 1000
            endpoint = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table_name}"
            
            for i in range(0, total_records, BATCH_SIZE):
                batch = records[i:i + BATCH_SIZE]
                
                try:
                    response = requests.post(endpoint, headers=headers, json=batch)
                    
                    if response.status_code in [200, 201]:
                        pass 
                    else:
                        Logger.error(f"  Erreur HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    Logger.error(f"  Exception Requête: {e}")

            Logger.success(f"  {total_records} enregistrements traités.")
            success_count += 1

        except Exception as e:
            Logger.error(f"  Erreur globale fichier: {e}")

    Logger.header("RÉSUMÉ")
    if success_count == total_files:
        Logger.success("Migration terminée avec succès !")
    else:
        Logger.warning(f"⚠️  {success_count}/{total_files} fichiers envoyés.")

if __name__ == "__main__":
    push_to_supabase()
