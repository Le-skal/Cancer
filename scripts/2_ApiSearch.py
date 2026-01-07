import requests
import pandas as pd
import time

LISTE_MALADIES = [
    "Lung Cancer", 
    "Breast Cancer", 
    "Pancreatic Cancer", 
    "Leukemia", 
    "Prostate Cancer"
]

ANNEE = 2024
resultats_api = []

print("🌍 Interrogation de l'API PubMed (NCBI)...")

for maladie in LISTE_MALADIES:
    # On construit la requête : Cherche "Lung Cancer" ET "2024"
    term = f'"{maladie}"[Title/Abstract] AND {ANNEE}[Date - Publication]'
    
    # URL de l'API publique (E-utilities)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json"
    }
    
    try:
        reponse = requests.get(url, params=params)
        data = reponse.json()
        
        # Le nombre total est dans 'count'
        nb_articles = data['esearchresult']['count']
        print(f"   > {maladie} : {nb_articles} articles scientifiques trouvés.")
        
        resultats_api.append({
            "Maladie": maladie,
            "Nb_Publications_2024": nb_articles,
            "Source_API": "PubMed NCBI"
        })
        
    except Exception as e:
        print(f"   ❌ Erreur pour {maladie}: {e}")
        resultats_api.append({"Maladie": maladie, "Nb_Publications_2024": 0})
    
    time.sleep(1) # Petite pause pour respecter l'API

# Sauvegarde
df = pd.DataFrame(resultats_api)
nom_fichier = "DATA_API_PUBMED.csv"
df.to_csv(nom_fichier, index=False)

print(f"\n✅ Fichier API généré : {nom_fichier}")