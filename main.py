#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 PIPELINE PRINCIPAL - CANCER DATA ANALYSIS
Orchestre le scraping, la recherche API et le nettoyage des données
"""

import sys
import os
import time
from datetime import datetime


# ==========================================
# 🎨 CONFIGURATION DES LOGS
# ==========================================
class Logger:
    """Classe pour les jolis logs"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @staticmethod
    def header(text):
        print(f"\n{Logger.BOLD}{Logger.CYAN}{'='*70}{Logger.END}")
        print(f"{Logger.BOLD}{Logger.CYAN}🚀 {text}{Logger.END}")
        print(f"{Logger.BOLD}{Logger.CYAN}{'='*70}{Logger.END}\n")

    @staticmethod
    def success(text):
        print(f"{Logger.GREEN}✅ {text}{Logger.END}")

    @staticmethod
    def error(text):
        print(f"{Logger.RED}❌ {text}{Logger.END}")

    @staticmethod
    def info(text):
        print(f"{Logger.BLUE}ℹ️  {text}{Logger.END}")

    @staticmethod
    def warning(text):
        print(f"{Logger.YELLOW}⚠️  {text}{Logger.END}")

    @staticmethod
    def step(step_num, text):
        print(
            f"\n{Logger.BOLD}{Logger.CYAN}[ÉTAPE {step_num}]{Logger.END} {Logger.BOLD}{text}{Logger.END}"
        )
        print(f"{Logger.CYAN}{'-'*70}{Logger.END}")

    @staticmethod
    def divider():
        print(f"\n{Logger.CYAN}{'-'*70}{Logger.END}\n")


# ==========================================
# 🔧 IMPORTS ET CONFIGURATION
# ==========================================
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ==========================================
# ✅ VÉRIFIER SI FICHIERS EXISTENT DÉJÀ
# ==========================================
def check_scraping_files_exist():
    """Vérifie si les fichiers de scraping existent déjà"""
    files_to_check = [
        "data/scraping/FINAL_DATASET_CANCER.csv",
        "data/DATA_API_PUBMED.csv",
    ]

    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    return len(missing_files) == 0, missing_files


def ask_user_confirmation(message):
    """Demande la confirmation à l'utilisateur"""
    while True:
        response = (
            input(f"\n{Logger.BOLD}{Logger.YELLOW}{message} (y/n): {Logger.END}")
            .strip()
            .lower()
        )
        if response in ["oui", "o", "yes", "y"]:
            return True
        elif response in ["non", "n", "no"]:
            return False
        else:
            Logger.warning("Réponse invalide. Veuillez entrer 'oui' ou 'non'.")


# ==========================================
# 📊 ÉTAPE 1 : SCRAPING DES ESSAIS CLINIQUES
# ==========================================
def run_scraping(force_rerun=False):
    """Lance le scraping des essais cliniques"""
    Logger.step(1, "Scraping des essais cliniques & Recherche PubMed")

    # Vérifier si les fichiers existent
    files_exist, missing_files = check_scraping_files_exist()

    if files_exist and not force_rerun:
        Logger.info("✓ Scraping ignoré - fichiers existants utilisés")
        return True

    if missing_files and not force_rerun:
        Logger.warning(f"Fichiers manquants: {missing_files}")
        Logger.info("Relancement du scraping...")

    try:
        from scrapping_module import main as scraping_main

        Logger.info("Module de scraping importé avec succès")
        time.sleep(0.5)

        Logger.info("Démarrage du scraping...")
        scraping_main()

        Logger.success("Scraping et recherche PubMed terminés!")
        return True

    except ImportError:
        # Si l'import échoue, on lance le fichier directement
        Logger.warning("Import échoué, lancement du fichier Python directement...")
        try:
            import subprocess

            result = subprocess.run(
                [sys.executable, "scripts/1_Scrapping.py"],
                capture_output=False,
                text=True,
            )
            if result.returncode == 0:
                Logger.success("Scraping et recherche PubMed terminés!")
                return True
            else:
                Logger.error(f"Erreur lors du scraping (code: {result.returncode})")
                return False
        except Exception as e:
            Logger.error(f"Impossible de lancer le scraping: {e}")
            return False

    except Exception as e:
        Logger.error(f"Erreur lors du scraping: {e}")
        import traceback

        traceback.print_exc()
        return False


# ==========================================
# 🧹 ÉTAPE 2 : NETTOYAGE ET TRAITEMENT
# ==========================================
def run_cleaning():
    """Lance le nettoyage des données"""
    Logger.step(2, "Nettoyage et traitement des données")

    try:
        Logger.info("Vérification des fichiers générés...")

        # Vérifier les fichiers
        files_to_check = [
            "data/DATA_API_PUBMED.csv",
            "data/scraping/FINAL_DATASET_CANCER.csv",
        ]

        for file_path in files_to_check:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                Logger.success(f"Fichier trouvé: {file_path} ({file_size} bytes)")
            else:
                Logger.warning(f"Fichier non trouvé: {file_path}")

        Logger.info("Démarrage du nettoyage...")
        time.sleep(0.5)

        # Importer et lancer le nettoyage
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/3_Nettoyage.py"], capture_output=False, text=True
        )

        if result.returncode == 0:
            Logger.success("Nettoyage et traitement terminés!")

            # Vérifier les fichiers générés
            output_files = [
                "data_clean/cancer_mortality_2022.csv",
                "data_clean/cancer_research_vs_mortality.csv",
                "data_clean/clinical_trials_clean.csv",
                "data_clean/trials_count_by_cancer.csv",
            ]

            Logger.divider()
            Logger.info("Fichiers générés:")
            for file_path in output_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    Logger.success(f"  ✓ {file_path} ({file_size} bytes)")
                else:
                    Logger.warning(f"  ✗ {file_path} (non trouvé)")

            return True
        else:
            Logger.error(f"Erreur lors du nettoyage (code: {result.returncode})")
            return False

    except Exception as e:
        Logger.error(f"Erreur lors du nettoyage: {e}")
        import traceback

        traceback.print_exc()
        return False


# ==========================================
# 📊 ÉTAPE 3 : SUPABASE
# ==========================================
def run_supabase():
    """Lance le script Supabase"""
    Logger.step(3, "Configuration et import Supabase")

    try:
        Logger.info("Démarrage du script Supabase...")
        time.sleep(0.5)

        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/4_Supabase.py"], capture_output=False, text=True
        )

        if result.returncode == 0:
            Logger.success("Script Supabase terminé!")
            return True
        else:
            Logger.error(f"Erreur lors du script Supabase (code: {result.returncode})")
            return False

    except Exception as e:
        Logger.error(f"Erreur lors du script Supabase: {e}")
        import traceback

        traceback.print_exc()
        return False


# ==========================================
# 📊 ÉTAPE 4 : VISUALISATION
# ==========================================
def run_visualization():
    """Lance le notebook de visualisation"""
    Logger.step(4, "Génération des visualisations")

    try:
        Logger.info("Exécution du notebook de visualisation...")
        time.sleep(0.5)

        import subprocess

        # Essayer d'exécuter le notebook avec jupyter
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                "scripts/5_Visualisation.ipynb",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            Logger.success("Visualisations générées avec succès!")
            Logger.info(
                "Vous pouvez ouvrir scripts/5_Visualisation.ipynb pour voir les résultats"
            )
            return True
        else:
            Logger.warning("Impossible d'exécuter automatiquement le notebook")
            Logger.info(
                "Veuillez ouvrir scripts/5_Visualisation.ipynb manuellement avec Jupyter"
            )
            return False

    except Exception as e:
        Logger.warning(f"Impossible d'exécuter le notebook automatiquement: {e}")
        Logger.info(
            "Veuillez ouvrir scripts/5_Visualisation.ipynb manuellement avec Jupyter"
        )
        return False


# ==========================================
# 📈 RÉSUMÉ FINAL
# ==========================================
def print_summary(scraping_ok, cleaning_ok, supabase_ok, visualization_ok):
    """Affiche un résumé du pipeline"""
    Logger.divider()
    Logger.header("RÉSUMÉ DU PIPELINE")

    print(
        f"  {Logger.BOLD}Scraping & API PubMed{Logger.END}     : {Logger.GREEN + '✅ SUCCÈS' + Logger.END if scraping_ok else Logger.RED + '❌ ERREUR' + Logger.END}"
    )
    print(
        f"  {Logger.BOLD}Nettoyage des données{Logger.END}     : {Logger.GREEN + '✅ SUCCÈS' + Logger.END if cleaning_ok else Logger.RED + '❌ ERREUR' + Logger.END}"
    )
    print(
        f"  {Logger.BOLD}Configuration Supabase{Logger.END}    : {Logger.GREEN + '✅ SUCCÈS' + Logger.END if supabase_ok else Logger.RED + '❌ ERREUR' + Logger.END}"
    )
    print(
        f"  {Logger.BOLD}Visualisations{Logger.END}            : {Logger.GREEN + '✅ SUCCÈS' + Logger.END if visualization_ok else Logger.RED + '❌ ERREUR' + Logger.END}"
    )

    if scraping_ok and cleaning_ok and supabase_ok and visualization_ok:
        Logger.success(f"\n🎉 PIPELINE COMPLET AVEC SUCCÈS!")
        print(f"\n{Logger.BOLD}Les fichiers sont prêts dans:{Logger.END}")
        print(f"  📁 data/ → Données brutes")
        print(f"  📁 data_clean/ → Données nettoyées et traitées")
        print(f"  📁 scripts/5_Visualisation.ipynb → Visualisations")
    else:
        Logger.error("\n⚠️  Le pipeline a rencontré des erreurs")

    print(f"\n{Logger.CYAN}{'='*70}{Logger.END}\n")


# ==========================================
# 🚀 MAIN
# ==========================================
def main():
    """Fonction principale"""
    start_time = time.time()

    # Banner d'accueil
    Logger.header("PIPELINE D'ANALYSE DU CANCER")
    print(
        f"{Logger.BOLD}Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Logger.END}\n"
    )

    # Vérifier si le scraping a déjà été fait
    files_exist, _ = check_scraping_files_exist()
    force_rerun = False
    if files_exist:
        Logger.warning("Scraping déjà effectué!")
        if ask_user_confirmation("Voulez-vous le relancer?"):
            force_rerun = True

    # Étape 1: Scraping
    scraping_ok = run_scraping(force_rerun=force_rerun)
    Logger.divider()

    # Étape 2: Nettoyage
    cleaning_ok = run_cleaning()
    Logger.divider()

    # Étape 3: Supabase
    supabase_ok = run_supabase()
    Logger.divider()

    # Étape 4: Visualisation
    visualization_ok = run_visualization()
    Logger.divider()

    # Résumé
    print_summary(scraping_ok, cleaning_ok, supabase_ok, visualization_ok)

    # Temps d'exécution
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"{Logger.BOLD}Temps total: {minutes}m {seconds}s{Logger.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Logger.warning("\n\n⚠️  Pipeline interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"\n\n❌ Erreur critique: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
