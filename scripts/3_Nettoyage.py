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


# ===== PARTIE 5 : Analyser Google Trends =====
print(f"\n📊 Google Trends - Visibilité médiatique des cancers\n")

# Liste des fichiers Google Trends
google_trends_files = {
    "Lung Cancer": "data/Google-Trend/lung_cancer.csv",
    "Breast Cancer": "data/Google-Trend/breast_cancer.csv",
    "Pancreatic Cancer": "data/Google-Trend/pancreatic_cancer.csv",
    "Leukemia": "data/Google-Trend/leukemia.csv",
    "Prostate Cancer": "data/Google-Trend/prostate_cancer.csv",
}

# Liste pour stocker les résultats
trends_results = []

# Analyser chaque fichier
for cancer_name, filepath in google_trends_files.items():
    # Charger le fichier (skip les 2 premières lignes)
    df_trend = pd.read_csv(filepath, skiprows=2)

    # La colonne 2 contient les scores
    column_name = df_trend.columns[1]

    # Nettoyer : supprimer les lignes vides et convertir en numérique
    df_trend[column_name] = pd.to_numeric(df_trend[column_name], errors="coerce")

    # Supprimer les NaN
    df_trend_clean = df_trend.dropna(subset=[column_name])

    # Calculer les statistiques
    mean_score = df_trend_clean[column_name].mean()
    max_score = df_trend_clean[column_name].max()
    count_countries = len(df_trend_clean)

    # Top 3 pays
    top_countries = df_trend_clean.head(3)["Country"].tolist()
    top_scores = df_trend_clean.head(3)[column_name].tolist()

    trends_results.append(
        {
            "Cancer": cancer_name,
            "Mean_Interest_Score": round(mean_score, 2),
            "Max_Score": int(max_score),
            "Countries_Count": count_countries,
            "Top_3_Countries": ", ".join(top_countries[:3]),
        }
    )

    print(f"✅ {cancer_name}")
    print(f"   Score moyen : {mean_score:.2f}")
    print(f"   Score max : {max_score}")
    print(f"   Nombre de pays : {count_countries}")
    print(
        f"   Top 3 pays : {', '.join([f'{c} ({s})' for c, s in zip(top_countries[:3], top_scores[:3])])}"
    )
    print()

# Créer un DataFrame de comparaison
df_trends_comparison = pd.DataFrame(trends_results)

# Trier par score moyen décroissant
df_trends_comparison = df_trends_comparison.sort_values(
    "Mean_Interest_Score", ascending=False
)

print("\n" + "=" * 70)
print("📈 CLASSEMENT DE LA VISIBILITÉ MÉDIATIQUE (Google Trends)")
print("=" * 70)
print(
    df_trends_comparison[["Cancer", "Mean_Interest_Score", "Max_Score"]].to_string(
        index=False
    )
)

# Calcul du ratio de visibilité
max_score_overall = df_trends_comparison["Mean_Interest_Score"].max()

df_trends_comparison["Relative_Visibility_%"] = (
    df_trends_comparison["Mean_Interest_Score"] / max_score_overall * 100
).round(2)

print("\n" + "=" * 70)
print("🔍 ANALYSE : Visibilité relative")
print("=" * 70)
print(
    df_trends_comparison[
        ["Cancer", "Mean_Interest_Score", "Relative_Visibility_%"]
    ].to_string(index=False)
)

# Sauvegarder
df_trends_comparison.to_csv("data_clean/google_trends_comparison.csv", index=False)

print("\n✅ Fichier Google Trends sauvegardé : google_trends_comparison.csv")


# ===== PARTIE 6 : Répartition géographique des essais cliniques =====
print(f"\n🌍 Répartition géographique des essais cliniques\n")


# Dictionnaire de mapping pour identifier les pays/régions
def extract_country_region(sponsor):
    """Extrait le pays/région depuis le sponsor"""
    if pd.isna(sponsor):
        return "Unknown"

    sponsor = sponsor.lower()

    # USA - hôpitaux et institutions
    usa_keywords = [
        "united states",
        "usa",
        "u.s.",
        "texas",
        "california",
        "new york",
        "massachusetts",
        "florida",
        "ohio",
        "pennsylvania",
        "maryland",
        "michigan",
        "north carolina",
        "washington",
        "arizona",
        "georgia",
        "boston",
        "harvard",
        "yale",
        "stanford",
        "duke",
        "johns hopkins",
        "mayo clinic",
        "cleveland clinic",
        "md anderson",
        "m.d. anderson",
        "memorial sloan",
        "dana-farber",
        "national cancer institute",
        "nci",
        "nih",
        "national institutes of health",
        "wake forest",
        "case comprehensive",
        "city of hope",
        "weill cornell",
        "columbia university",
        "vanderbilt",
        "emory",
        "kaiser permanente",
        "adventhealth",
        "moffitt cancer",
        "abramson cancer",
        "university of arkansas",
        "university of colorado",
        "precog",
        "alliance for clinical trials",
        "eastern cooperative oncology",
        "swog cancer",
        "children's oncology group",
        "henry ford",
        "dartmouth",
        "utah",
        "indiana",
        "alabama",
        "kentucky",
        "tennessee",
        "minnesota",
        "wisconsin",
        "iowa",
        "nanospectra",
        "cougar biotechnology",
        "galvanize therapeutics",
        "everest detection",
        "integro theranostics",
        "phenomapper",
        "jonsson comprehensive",
        "ucla",
        "us oncology",
        "baylor",
        "methodist health",
        "seagen",
        "novian health",
        "tigris pharmaceuticals",
        "university of nebraska",
        "university of illinois",
        "va office",
        "cmx research",
        "aragon pharmaceuticals",
        "exosome diagnostics",
        "ohsu knight",
        "roswell park",
        "syndax pharmaceuticals",
        "adenocyte",
        "curium",
        "bastyr university",
        "tulane university",
        "gtx",
        "gaad medical",
        "oncomed pharmaceuticals",
        "mereo biopharma",
        "georgetown university",
        "rutgers",
        "brigham and women",
        "state university of new york",
        "suny",
        "university of california",
        "baptist health",
        "christian hospital",
        "novarx",
        "broncus technologies",
        "menssana research",
        "ka imaging",
        "auris health",
        "c. r. bard",
        "mirati therapeutics",
        "csa medical",
        "university of vermont",
        "thomas jefferson university",
        "sharp healthcare",
        "schiffler cancer center",
        "university of pittsburgh",
        "university of missouri",
        "national center for plastic surgery",
        "hibercell",
        "bhr pharma",
        "enzon pharmaceuticals",
        "aegera therapeutics",
    ]

    # USA - Big Pharma avec siège US
    usa_pharma = [
        "merck sharp",
        "msd",
        "eli lilly",
        "pfizer",
        "johnson & johnson",
        "janssen",
        "bristol-myers",
        "bms",
        "amgen",
        "celgene",
        "abbvie",
        "gilead",
        "abbott",
        "koning corporation",
    ]

    # Europe - hôpitaux et institutions
    europe_keywords = [
        "united kingdom",
        "uk",
        "england",
        "scotland",
        "wales",
        "london",
        "oxford",
        "cambridge",
        "manchester",
        "glasgow",
        "edinburgh",
        "southampton nhs",
        "bristol nhs",
        "nhs foundation",
        "france",
        "french",
        "paris",
        "lyon",
        "marseille",
        "foch",
        "tours",
        "amiens",
        "paoli-calmettes",
        "institut de cancérologie",
        "institut curie",
        "centre leon berard",
        "centre hospitalier universitaire de nice",
        "chu nice",
        "chu besancon",
        "chu toulouse",
        "hospital, toulouse",
        "hospital, brest",
        "unicancer",
        "germany",
        "german",
        "berlin",
        "munich",
        "heidelberg",
        "tuebingen",
        "tübingen",
        "medac gmbh",
        "italy",
        "italian",
        "rome",
        "milan",
        "european institute of oncology",
        "regina elena",
        "link campus",
        "fondazione del piemonte",
        "fondazione piemonte",
        "spain",
        "spanish",
        "madrid",
        "barcelona",
        "granada",
        "pethema",
        "grupo espanol",
        "netherlands",
        "dutch",
        "amsterdam",
        "rotterdam",
        "radboud",
        "maastricht university",
        "groningen",
        "belgium",
        "brussels",
        "leuven",
        "ku leuven",
        "universitaire ziekenhuizen",
        "gasthuisberg",
        "jules bordet",
        "switzerland",
        "swiss",
        "zurich",
        "geneva",
        "sweden",
        "stockholm",
        "region stockholm",
        "denmark",
        "copenhagen",
        "herlev",
        "aalborg",
        "norway",
        "norwegian",
        "oslo",
        "st. olavs",
        "trondheim",
        "finland",
        "helsinki",
        "austria",
        "vienna",
        "otto wagner",
        "portugal",
        "lisbon",
        "leiria",
        "instituto politécnico",
        "ireland",
        "dublin",
        "poland",
        "silesia",
        "czech",
        "greece",
        "trakya university",
        "european lung cancer",
        "montpellier",
        "antoine lacassagne",
        "nantes university",
        "nantes hospital",
        "institut bergonié",
        "bergonie",
        "henri becquerel",
        "becquerel",
        "besancon",
        "chu besançon",
        "technische universität",
        "technische universitat",
        "dresden",
        "cliniques universitaires saint-luc",
        "université catholique de louvain",
        "universite catholique",
        "cell medica",
        "medsir",
        "institut fuer frauengesundheit",
        "wissenschaftliches institut bethanien",
        "naestved hospital",
        "næstved",
        "tampere university",
        "fundació institut de recerca",
        "fundacio",
        "sant pau",
        "santa creu",
        "irccs",
        "sacro cuore",
        "negrar",
        "ente ospedaliero",
        "galliera",
        "tethis",
        "frisius medisch centrum",
        "bozok university",
        "oslo university hospital",
        "university of hull",
        "hellenic cooperative oncology",
        "trans tasman",
        "grupo oncologico italia meridionale",
        "baselşehir",
        "hacettepe university",
        "maltepe university",
        "institut universitaire de cardiologie",
        "quebec",
        "laval",
        "assistance publique",
        "hopitaux de paris",
        "hôpitaux de paris",
        "medical university of vienna",
        "oncology center of biochemical",
        "sheba medical center",
        "national institute for tuberculosis",
        "spanish lung cancer group",
        "institut de cancérologie de la loire",
        "university of bristol",
        "hospital, limoges",
        "limoges",
        "aarhus university hospital",
        "aarhus",
        "biocruces bizkaia",
        "cantonal hospital of st. gallen",
        "st. gallen",
        "umeå university",
        "umea",
        "pantarhei oncology",
        "maria sklodowska-curie",
        "sklodowska",
        "debiopharm",
        "danish cancer society",
        "institut rafael",
        "region skane",
        "skåne",
        "istituto clinico humanitas",
        "humanitas",
        "ab-ct",
        "advanced breast-ct",
        "siemens healthcare",
        "centre hospitalier emile roux",
        "neutec pharma",
        "pulsion medical",
        "pierre fabre medicament",
        "karolinska institutet",
        "karolinska",
    ]

    # Europe - Big Pharma
    europe_pharma = [
        "novartis",
        "roche",
        "hoffmann-la roche",
        "sanofi",
        "glaxosmithkline",
        "gsk",
        "astrazeneca",
        "bayer",
        "boehringer",
        "servier",
        "ipsen",
        "astellas",
    ]

    # Asie - hôpitaux et institutions
    asia_keywords = [
        "china",
        "chinese",
        "beijing",
        "peking union",
        "peking university",
        "shanghai",
        "ruijin hospital",
        "renji hospital",
        "chest hospital",
        "guangzhou",
        "guangdong",
        "fuda cancer",
        "tianjin medical",
        "sichuan",
        "fuzhou general",
        "guang'anmen",
        "tongji hospital",
        "hong kong polytechnic",
        "hong kong",
        "fudan university",
        "sun yat-sen",
        "xi'an jiaotong",
        "xian jiaotong",
        "nanjing drum tower",
        "hangzhou",
        "chongqing",
        "tang-du hospital",
        "zhejiang",
        "wonju severance",
        "severance hospital",
        "chandigarh",
        "post graduate institute of medical education",
        "assiut university",
        "taipei medical university",
        "national taipei university",
        "seoul st. mary",
        "bundang hospital",
        "china medical university hospital",
        "affiliated cancer hospital",
        "guangzhou medical university",
        "shanghai pulmonary hospital",
        "beijing tongren hospital",
        "central south university",
        "chinese alliance against lung cancer",
        "jiangsu hengrui medicine",
        "innovent biologics",
        "guangzhou fineimmune",
        "jiangsu shengdiya",
        "shanghai zhongshan hospital",
        "first people's hospital of lianyungang",
        "nantong university",
        "air force military medical university",
        "xiamen university",
        "tianjin medical university second hospital",
        "fakultas kedokteran universitas indonesia",
        "japan",
        "shenzhen gene health",
        "shenzhen",
        "swami rama cancer hospital",
        "xijing hospital",
        "qilu hospital of shandong university",
        "shandong university",
        "vardhman mahavir medical college",
        "safdarjung hospital",
        "olive healthcare",
        "nippon kayaku",
        "aryogen pharmed",
        "japanese",
        "tokyo",
        "osaka",
        "kyoto",
        "japan clinical oncology",
        "south korea",
        "korea",
        "korean",
        "seoul",
        "yonsei",
        "samsung medical",
        "asan medical",
        "chonnam national",
        "india",
        "indian",
        "mumbai",
        "delhi",
        "bangalore",
        "lahore",
        "ain shams",
        "tata memorial",
        "singapore",
        "taiwan",
        "national taiwan",
        "chang gung",
        "thailand",
        "malaysia",
        "philippines",
        "indonesia",
        "vietnam",
        "pakistan",
    ]

    # Asie - Pharma
    asia_pharma = [
        "ethicon",
        "rgene corporation",
        "foresee pharmaceuticals",
        "shanghai youhe",
        "daiichi sankyo",
        "takeda",
        "chia tai tianqing",
        "primo biotechnology",
        "qilu pharmaceutical",
    ]

    # Moyen-Orient
    middle_east_keywords = [
        "israel",
        "tel aviv",
        "jerusalem",
        "saudi",
        "emirates",
        "dubai",
        "qatar",
        "turkey",
        "istanbul",
        "iran",
        "egypt",
        "cairo",
        "tunisian",
        "tunisia",
        "zagazig",
        "rabin medical center",
        "kasr el aini hospital",
    ]

    # Amérique Latine
    latin_america_keywords = [
        "brazil",
        "brazilian",
        "sao paulo",
        "são paulo",
        "instituto do cancer do estado",
        "instituto brasileiro de controle do cancer",
        "rio",
        "hospital israelita albert einstein",
        "latin american cooperative oncology",
        "lacog",
        "mexico",
        "mexican",
        "argentina",
        "buenos aires",
        "chile",
        "colombia",
        "peru",
        "venezuela",
        "universidade estadual paulista",
        "paulista",
        "julio de mesquita",
    ]

    # Océanie
    oceania_keywords = [
        "australia",
        "australian",
        "sydney",
        "melbourne",
        "new zealand",
        "auckland",
        "university of sydney",
        "royal north shore",
    ]

    # Canada
    canada_keywords = [
        "canada",
        "canadian",
        "toronto",
        "montreal",
        "vancouver",
        "quebec",
        "ontario",
        "alberta",
        "british columbia",
        "london health sciences",
        "lawson research",
        "mcmaster university",
        "ottawa hospital",
    ]

    # Pharma/Biotech multinationales (à classifier selon siège social)
    multinational_companies = {
        "clarity pharmaceuticals": "Oceania",  # Australie
        "impact biotech": "Europe",  # Israel
        "rarecells diagnostics": "Europe",  # France
        "dacima consulting": "Middle East",  # Tunisie
    }

    # Vérifier d'abord les compagnies multinationales spécifiques
    for company, region in multinational_companies.items():
        if company in sponsor:
            return region

    # Vérifier dans l'ordre
    if any(keyword in sponsor for keyword in usa_keywords) or any(
        keyword in sponsor for keyword in usa_pharma
    ):
        return "USA"
    elif any(keyword in sponsor for keyword in canada_keywords):
        return "Canada"
    elif any(keyword in sponsor for keyword in europe_keywords) or any(
        keyword in sponsor for keyword in europe_pharma
    ):
        return "Europe"
    elif any(keyword in sponsor for keyword in asia_keywords) or any(
        keyword in sponsor for keyword in asia_pharma
    ):
        return "Asia"
    elif any(keyword in sponsor for keyword in middle_east_keywords):
        return "Middle East"
    elif any(keyword in sponsor for keyword in latin_america_keywords):
        return "Latin America"
    elif any(keyword in sponsor for keyword in oceania_keywords):
        return "Oceania"
    else:
        return "Other"


# Appliquer l'extraction de pays/région
df_trials_clean["Region"] = df_trials_clean["Sponsor"].apply(extract_country_region)

# Compter les essais par cancer ET par région
geo_distribution = (
    df_trials_clean.groupby(["Cancer", "Region"]).size().reset_index(name="Count")
)

# Pivoter pour avoir un tableau lisible
geo_pivot = (
    geo_distribution.pivot(index="Cancer", columns="Region", values="Count")
    .fillna(0)
    .astype(int)
)

print("📊 Répartition géographique des essais cliniques :")
print(geo_pivot)

# Calculer les pourcentages par cancer
geo_pivot_pct = geo_pivot.div(geo_pivot.sum(axis=1), axis=0) * 100
geo_pivot_pct = geo_pivot_pct.round(1)

print("\n📊 Répartition géographique en % :")
print(geo_pivot_pct)

# Sauvegarder
geo_pivot.to_csv("data_clean/clinical_trials_geography_count.csv")
geo_pivot_pct.to_csv("data_clean/clinical_trials_geography_percentage.csv")

print("\n✅ Fichiers géographiques sauvegardés :")
print("   - clinical_trials_geography_count.csv")
print("   - clinical_trials_geography_percentage.csv")

# Statistiques globales
print("\n🌐 Statistiques globales par région :")
total_by_region = df_trials_clean["Region"].value_counts()
print(total_by_region)
