

-- KPI1 : Nombre total d'essais cliniques 

SELECT COUNT(*) AS total_trials
FROM clinical_trials;

-- KPI2 : Nombre d'essais par type de cancer 
SELECT cancer, COUNT(*) AS trials_count
FROM clinical_trials
GROUP BY cancer
ORDER BY trials_count DESC;

-- KPI3 : Nombre d'essais par statut 
SELECT status, COUNT(*) AS nb_trials
FROM clinical_trials
GROUP BY status
ORDER BY nb_trials DESC;

-- KPI4 : Moyenne / Min / Max du budget NCI 
SELECT
  AVG(budget_2023_million_usd) AS avg_budget_musd,
  MIN(budget_2023_million_usd) AS min_budget_musd,
  MAX(budget_2023_million_usd) AS max_budget_musd
FROM nci_budget;

-- KPI5 : Cancer le plus / le moins mortel 
SELECT label AS cancer, mortality
FROM cancer_mortality
ORDER BY mortality DESC
LIMIT 1;
-- KPI6 : Cancer le plus / le moins mortel 
SELECT label AS cancer, mortality
FROM cancer_mortality
ORDER BY mortality ASC
LIMIT 1;


-- KPI7: Top sponsors 
SELECT sponsor, COUNT(*) AS nb_trials
FROM clinical_trials
GROUP BY sponsor
ORDER BY nb_trials DESC
LIMIT 10;

-- KPI8 : “Research gap” 

SELECT
  cancer,
  mortality_2022,
  publications_2024,
  (mortality_2022 * 1.0 / NULLIF(publications_2024, 0)) AS deaths_per_publication
FROM research_vs_mortality
ORDER BY deaths_per_publication DESC;

-- KPI9 : Répartition géographique globale des essais 
SELECT
  SUM(usa)           AS usa,
  SUM(europe)        AS europe,
  SUM(asia)          AS asia,
  SUM(canada)        AS canada,
  SUM(latin_america) AS latin_america,
  SUM(middle_east)   AS middle_east,
  SUM(oceania)       AS oceania,
  SUM(other)         AS other
FROM geography_count;

-- KPI10: Google Trends - moyenne d'intérêt + max 
SELECT
  AVG(mean_interest_score) AS avg_interest_score,
  MAX(max_score) AS max_peak_score
FROM google_trends;

