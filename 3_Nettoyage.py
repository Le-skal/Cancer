import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import pandas as pd
import re
import os

# ===== CRÉER LE DOSSIER DE SORTIE =====
os.makedirs("data_clean", exist_ok=True)


# ===== PARTIE 1 : Nettoyer le fichier OMS =====
df_oms = pd.read_csv(
    "data/oms/dataset-absolute-numbers-mort-both-sexes-in-2022-continents (1).csv"
)

# Garder seulement 2 colonnes
df_clean = df_oms[["Label", "Mortality"]]

# Supprimer les lignes vides/inutiles
df_clean = df_clean.dropna()
df_clean = df_clean[df_clean["Mortality"] > 0]

# Trier par mortalité décroissante
df_clean = df_clean.sort_values("Mortality", ascending=False)

# Sauvegarder
df_clean.to_csv("data_clean/cancer_mortality_2022.csv", index=False)


# ===== PARTIE 2 : Ajouter Mortality au fichier PubMed =====
df_pubmed = pd.read_csv("data/DATA_API_PUBMED.csv")

# Mapping OMS → PubMed (pour faire correspondre les noms)
cancer_mapping = {
    "Lung Cancer": "Trachea bronchus and lung",
    "Breast Cancer": "Breast",
    "Pancreatic Cancer": "Pancreas",
    "Leukemia": "Leukaemia",
    "Prostate Cancer": "Prostate",
}

# Créer une colonne avec le nom OMS
df_pubmed["Label_OMS"] = df_pubmed["Maladie"].map(cancer_mapping)

# Fusionner avec les données de mortalité
df_pubmed_enriched = df_pubmed.merge(
    df_clean[["Label", "Mortality"]], left_on="Label_OMS", right_on="Label", how="left"
)

# Garder seulement les colonnes utiles
df_pubmed_enriched = df_pubmed_enriched[
    ["Maladie", "Nb_Publications_2024", "Mortality"]
]

# Renommer pour plus de clarté
df_pubmed_enriched.columns = ["Cancer", "Publications_2024", "Mortality_2022"]

# Calculer le ratio (publications pour 1000 morts)
df_pubmed_enriched["Publications_per_1000_deaths"] = (
    df_pubmed_enriched["Publications_2024"]
    / df_pubmed_enriched["Mortality_2022"]
    * 1000
).round(2)

# Sauvegarder
df_pubmed_enriched.to_csv("data_clean/cancer_research_vs_mortality.csv", index=False)

print(df_pubmed_enriched)


# ===== PARTIE 3 : Nettoyer les essais cliniques =====
df_trials = pd.read_csv("data/scraping/FINAL_DATASET_CANCER.csv")

print(f"\n📊 Essais cliniques - Nombre de lignes initial : {len(df_trials)}")


# Fonction pour extraire l'ID NCT
def extract_nct_id(url):
    """Extrait l'ID NCT depuis l'URL"""
    match = re.search(r"NCT\d+", url)
    return match.group(0) if match else None


# Fonction pour nettoyer le titre
def clean_title(titre):
    """Extrait le vrai titre depuis la chaîne scraped"""
    if pd.isna(titre):
        return None

    # Pattern : "Study Details | NCT... | TITRE | ClinicalTrials.gov"
    parts = titre.split("|")
    if len(parts) >= 3:
        title = parts[2].strip()
        title = title.replace("ClinicalTrials.gov", "").strip()
        return title
    return titre


# Extraire l'ID et nettoyer le titre
df_trials["Clinical_Trial_ID"] = df_trials["URL"].apply(extract_nct_id)
df_trials["Title_Clean"] = df_trials["Titre"].apply(clean_title)

# Supprimer les doublons (garder la première occurrence de chaque ID)
df_trials_unique = df_trials.drop_duplicates(subset=["Clinical_Trial_ID"], keep="first")

print(f"🗑️  Doublons supprimés : {len(df_trials) - len(df_trials_unique)}")
print(f"✅ Nombre de lignes final : {len(df_trials_unique)}")

# Réorganiser les colonnes
df_trials_clean = df_trials_unique[
    ["Maladie", "Clinical_Trial_ID", "Title_Clean", "Sponsor", "Statut", "URL"]
].copy()

# Renommer pour cohérence
df_trials_clean.columns = ["Cancer", "Trial_ID", "Title", "Sponsor", "Status", "URL"]

# Compter les essais par cancer
trials_count = df_trials_clean["Cancer"].value_counts().reset_index()
trials_count.columns = ["Cancer", "Clinical_Trials_Count"]

print("\n📈 Nombre d'essais cliniques par cancer :")
print(trials_count)

# Sauvegarder
df_trials_clean.to_csv("data_clean/clinical_trials_clean.csv", index=False)
trials_count.to_csv("data_clean/trials_count_by_cancer.csv", index=False)

print("\n✅ Fichiers essais cliniques sauvegardés :")
print("   - clinical_trials_clean.csv")
print("   - trials_count_by_cancer.csv")


# ===== PARTIE 4 : Nettoyer les budgets NCI =====
# https://www.cancer.gov/about-nci/budget/fact-book/data/research-funding
df_budget = pd.read_csv("data/Budget.csv")

print(f"\n💰 Budget NCI - Nombre de lignes initial : {len(df_budget)}")


# Fonction pour nettoyer les montants
def clean_budget(value):
    """Convertit les montants en float"""
    if pd.isna(value):
        return None

    # Convertir en string
    value = str(value)

    # Supprimer $ et espaces
    value = value.replace("$", "").replace(" ", "")

    # Remplacer virgules par points
    value = value.replace(",", ".")

    try:
        return float(value)
    except:
        return None


# Nettoyer la colonne 2023 Estimate
df_budget["Budget_2023_Million_USD"] = df_budget["2023 Estimate"].apply(clean_budget)

# Garder seulement les colonnes utiles
df_budget_clean = df_budget[["Disease Area", "Budget_2023_Million_USD"]].copy()

# Renommer
df_budget_clean.columns = ["Cancer", "Budget_2023_Million_USD"]

# Filtrer pour garder seulement les 5 cancers qui nous intéressent
cancers_to_keep = [
    "Lung Cancer",
    "Breast Cancer",
    "Pancreatic Cancer",
    "Leukemia",
    "Prostate Cancer",
]
df_budget_filtered = df_budget_clean[
    df_budget_clean["Cancer"].isin(cancers_to_keep)
].copy()

print("\n💵 Budgets NCI 2023 extraits :")
print(df_budget_filtered)

# Sauvegarder
df_budget_filtered.to_csv("data_clean/nci_budget_2023.csv", index=False)

print("\n✅ Fichier budget sauvegardé : nci_budget_2023.csv")
