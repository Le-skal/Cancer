import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Cancer Research Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Style sobre et professionnel inspiré des newsletters
st.markdown("""
    <style>
        /* Polices */
        @import url('https://fonts.googleapis.com/css2?family=Georgia&display=swap');

        /* Background principal */
        .stApp {
            background: #fafaf8;
            font-family: Arial, Helvetica, sans-serif;
        }

        /* Main container */
        .main .block-container {
            padding: 2rem 3rem;
            background: #ffffff;
            max-width: 1400px;
            margin: 0 auto;
            border-bottom: 4px double #2d5a7b;
        }

        /* Sidebar épurée */
        [data-testid="stSidebar"] {
            background: #f5f5f3;
            padding: 1.5rem 1rem;
            border-right: 1px solid #d8d2c7;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: transparent;
        }

        [data-testid="stSidebar"] label {
            color: #1b1b1b !important;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Multiselect complètement repensé */
        .stMultiSelect > div > div,
        div[data-baseweb="select"] {
            background: white !important;
            border: 1px solid #d8d2c7 !important;
            border-radius: 0px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            padding: 4px 8px !important;
            min-height: 42px !important;
        }

        .stMultiSelect > div > div:focus-within,
        div[data-baseweb="select"]:focus-within {
            border-color: #2d5a7b !important;
            box-shadow: 0 0 0 1px #2d5a7b !important;
        }

        /* Container des tags */
        div[data-baseweb="select"] > div {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        /* Tags individuels - style sobre */
        .stMultiSelect span[data-baseweb="tag"],
        span[data-baseweb="tag"] {
            background-color: #f5f5f3 !important;
            color: #1b1b1b !important;
            border: 1px solid #d8d2c7 !important;
            border-radius: 0px !important;
            font-size: 11px !important;
            font-weight: 500 !important;
            padding: 4px 8px !important;
            margin: 2px 4px 2px 0 !important;
            font-family: Arial, Helvetica, sans-serif !important;
        }

        /* Hover sur les tags */
        span[data-basewe="tag"]:hover {
            background-color: #e8e8e6 !important;
            border-color: #2d5a7b !important;
        }

        /* Texte dans les tags */
        span[data-baseweb="tag"] > span:first-child {
            color: #1b1b1b !important;
            font-size: 11px !important;
        }

        /* Icône de suppression dans les tags */
        span[data-baseweb="tag"] > span:last-child svg {
            width: 12px !important;
            height: 12px !important;
            fill: #666 !important;
        }

        span[data-baseweb="tag"] > span:last-child:hover svg {
            fill: #000 !important;
        }

        /* Input dans le multiselect */
        div[data-baseweb="select"] input {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            color: #1b1b1b !important;
        }

        /* Icônes du multiselect */
        div[data-baseweb="select"] svg {
            fill: #666 !important;
        }

        div[data-baseweb="select"] svg:hover {
            fill: #2d5a7b !important;
        }

        /* Dropdown */
        [data-baseweb="popover"] {
            border: 1px solid #d8d2c7 !important;
            border-radius: 0px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }

        /* Options dans le dropdown */
        [role="option"] {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 13px !important;
            padding: 8px 12px !important;
        }

        [role="option"]:hover {
            background-color: #f5f5f3 !important;
        }

        [aria-selected="true"] {
            background-color: #2d5a7b !important;
            color: white !important;
        }

        /* Métriques KPI - style sobre */
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d8d2c7;
            border-radius: 0px;
            padding: 1.25rem;
            box-shadow: none;
            transition: all 0.2s ease;
        }

        div[data-testid="stMetric"]:hover {
            border-color: #2d5a7b;
            box-shadow: 0 2px 8px rgba(45, 90, 123, 0.1);
        }

        div[data-testid="stMetricValue"] {
            font-size: 2.25rem;
            color: #2d5a7b !important;
            font-weight: 700;
            font-family: Georgia, 'Times New Roman', serif;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] > div,
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] span,
        [class*="st-emotion-cache"] div[data-testid="stMetricLabel"],
        div[data-testid="stMetric"] label {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 1.2px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            margin-bottom: 0.5rem !important;
        }

        /* Titres */
        h1 {
            color: #2d5a7b !important;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
            font-family: Georgia, 'Times New Roman', serif !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.5px;
        }

        h2 {
            color: #1b1b1b !important;
            font-weight: 600 !important;
            font-size: 1.5rem !important;
            font-family: Georgia, 'Times New Roman', serif !important;
            margin-top: 2rem !important;
            margin-bottom: 1rem !important;
            border-bottom: 1px solid #d8d2c7;
            padding-bottom: 0.5rem;
        }

        h3 {
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1.125rem !important;
            font-family: Arial, Helvetica, sans-serif !important;
            margin-bottom: 1rem !important;
        }

        /* Boutons */
        .stButton>button {
            background: #1b1b1b;
            color: white;
            border-radius: 2px;
            border: 1px solid #000000;
            font-weight: 400;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            padding: 7px 10px;
            transition: all 0.2s ease;
        }

        .stButton>button:hover {
            background: #2d5a7b;
            border-color: #2d5a7b;
        }

        /* Tabs style sobre */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            background-color: transparent;
            border-bottom: 2px solid #1b1b1b;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 0px;
            color: #6b665f;
            font-weight: 400;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 10px 20px;
            border-bottom: 3px solid transparent;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #2d5a7b;
        }

        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #1b1b1b !important;
            border-bottom: 3px solid #2d5a7b;
        }

        /* Selectbox */
        .stSelectbox > div > div {
            background: white;
            border: 1px solid #d8d2c7;
            border-radius: 0px;
            font-family: Arial, Helvetica, sans-serif;
        }

        /* Divider sobre */
        hr {
            margin: 1.5rem 0;
            border: none;
            height: 0;
            border-top: 1px solid #d8d2c7;
        }

        /* Dataframe */
        .dataframe {
            border-radius: 0px !important;
            border: 1px solid #d8d2c7 !important;
        }

        /* Checkbox et slider */
        .stCheckbox label,
        .stCheckbox label span,
        .stCheckbox > label > div {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #000000 !important;
        }

        .stCheckbox {
            padding: 0.5rem 0;
        }

        /* Case à cocher */
        .stCheckbox input[type="checkbox"] {
            width: 18px !important;
            height: 18px !important;
            accent-color: #2d5a7b !important;
        }

        /* Forcer la couleur bleue sur tous les états */
        .stCheckbox input[type="checkbox"]:checked {
            background-color: #2d5a7b !important;
            border-color: #2d5a7b !important;
        }

        /* Surcharger les classes Streamlit qui mettent du rouge */
        .st-c2,
        .stCheckbox .st-c2,
        [class*="st-"][class*="c2"] {
            background-color: #2d5a7b !important;
        }

        /* Cibler spécifiquement le span de la checkbox */
        .stCheckbox span.st-c2 {
            background-color: #2d5a7b !important;
        }

        .stSlider {
            padding: 1rem 0;
        }

        .stSlider label {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #000000 !important;
        }

        /* Info boxes */
        .stAlert {
            border-radius: 0px;
            border-left: 3px solid #2d5a7b;
            background-color: #fafaf8;
            font-family: Arial, Helvetica, sans-serif;
        }

        /* Pills/Button Group - Thème bleu */
        button[kind="pillsActive"] {
            background-color: #2d5a7b !important;
            color: white !important;
            border: 1px solid #2d5a7b !important;
            border-radius: 20px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-weight: 500 !important;
            padding: 6px 16px !important;
            transition: all 0.2s ease !important;
        }

        button[kind="pillsActive"]:hover {
            background-color: #1b3a4f !important;
            border-color: #1b3a4f !important;
            box-shadow: 0 2px 4px rgba(45, 90, 123, 0.2) !important;
        }

        button[kind="pillsInactive"] {
            background-color: #f5f5f3 !important;
            color: #666 !important;
            border: 1px solid #d8d2c7 !important;
            border-radius: 20px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-weight: 500 !important;
            padding: 6px 16px !important;
            transition: all 0.2s ease !important;
        }

        button[kind="pillsInactive"]:hover {
            background-color: #e8e8e6 !important;
            border-color: #2d5a7b !important;
            color: #2d5a7b !important;
        }

        /* Pas de border-radius sur les graphiques */
        .js-plotly-plot {
            border: 1px solid #e0e0e0;
        }

        /* Scrollbar sobre */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f5f5f3;
        }

        ::-webkit-scrollbar-thumb {
            background: #2d5a7b;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #1b3a4f;
        }
    </style>
""", unsafe_allow_html=True)

# Configuration Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def fetch_supabase_table(table_name):
    """Récupère une table depuis Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    endpoint = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table_name}"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Erreur lors du chargement de {table_name}: {response.status_code}")
        return pd.DataFrame()

# Chargement des données depuis Supabase
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_data():
    """Charge toutes les données depuis Supabase"""
    data = {
        'mortality': fetch_supabase_table('research_vs_mortality'),
        'budget': fetch_supabase_table('nci_budget'),
        'trials': fetch_supabase_table('clinical_trials'),
        'geography': fetch_supabase_table('geography_count'),
        'trends': fetch_supabase_table('google_trends'),
    }

    # Nettoyer les noms de colonnes
    for key in data:
        data[key].columns = data[key].columns.str.strip().str.lower()

    return data

@st.cache_data(ttl=300)
def load_kpis():
    """Calcule les KPI depuis les données Supabase"""
    kpis = {}

    # KPI1: Total trials
    trials = fetch_supabase_table('clinical_trials')
    kpis['kpi1'] = pd.DataFrame({'total_trials': [len(trials)]})

    # KPI2: Trials par cancer
    if not trials.empty:
        kpis['kpi2'] = trials.groupby('cancer').size().reset_index(name='trials_count')

    # KPI4: Budget stats
    budget = fetch_supabase_table('nci_budget')
    if not budget.empty:
        kpis['kpi4'] = pd.DataFrame({
            'avg_budget_musd': [budget['budget_2023_million_usd'].mean()],
            'min_budget_musd': [budget['budget_2023_million_usd'].min()],
            'max_budget_musd': [budget['budget_2023_million_usd'].max()]
        })

    # KPI5: Cancer le plus mortel
    mortality = fetch_supabase_table('cancer_mortality')
    if not mortality.empty:
        most_deadly = mortality.nlargest(1, 'mortality')[['label', 'mortality']]
        most_deadly.columns = ['cancer', 'mortality']
        kpis['kpi5'] = most_deadly

    # KPI8: Research Gap
    research = fetch_supabase_table('research_vs_mortality')
    if not research.empty:
        research['deaths_per_publication'] = research['mortality_2022'] / research['publications_2024'].replace(0, 1)
        kpis['kpi8'] = research[['cancer', 'mortality_2022', 'publications_2024', 'deaths_per_publication']].sort_values('deaths_per_publication', ascending=False)

    # KPI10: Google Trends moyenne
    trends = fetch_supabase_table('google_trends')
    if not trends.empty:
        kpis['kpi10'] = pd.DataFrame({
            'avg_interest_score': [trends['mean_interest_score'].mean()],
            'max_peak_score': [trends['max_score'].max()]
        })

    return kpis

# Charger les données
data = load_data()
kpis = load_kpis()

# Header style newsletter
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0; border-bottom: 1px solid #2d5a7b;'>
        <div style='padding-bottom: 8px; font-family: Georgia, "Times New Roman", serif; font-size: 11px;
                    font-weight: 400; text-transform: uppercase; letter-spacing: 1px; color: #666;'>
            Janvier 2026
        </div>
        <div style='font-family: Georgia, "Times New Roman", serif; font-size: 42px; font-weight: 700;
                    letter-spacing: -0.5px; line-height: 1.1; color: #2d5a7b; margin: 0.5rem 0;'>
            Cancer Research Analytics
        </div>
        <div style='padding-top: 6px; font-family: Georgia, "Times New Roman", serif; font-size: 13px;
                    font-style: italic; color: #666; letter-spacing: 0.3px;'>
            Analyse de la recherche sur le cancer, des budgets et des essais cliniques
        </div>
        <div style='padding-top: 12px; font-family: Arial, Helvetica, sans-serif; font-size: 11px; color: #666;'>
            <span style='font-weight: 600; color: #2d5a7b;'>TABLEAU DE BORD</span> · Données 2023-2024
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar - Filtres
with st.sidebar:
    st.markdown("""
        <div style='padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 2px solid #1b1b1b;'>
            <div style='font-family: Arial, Helvetica, sans-serif; font-size: 12px; letter-spacing: 1px;
                        text-transform: uppercase; color: #1b1b1b; font-weight: 600;'>
                Filtres
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Filtre par type de cancer
    all_cancers = list(data['mortality']['cancer'].unique())
    selected_cancers = st.pills(
        "Types de cancer",
        options=all_cancers,
        default=all_cancers,
        selection_mode="multi",
        help="Sélectionnez les types de cancer à afficher"
    )

    # Filtre par statut d'essai clinique
    if 'status' in data['trials'].columns:
        all_status = list(data['trials']['status'].unique())
        selected_status = st.pills(
            "Statut des essais",
            options=all_status,
            default=all_status,
            selection_mode="multi",
            help="Filtrer par statut d'essai clinique"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 2px solid #1b1b1b;'>
            <div style='font-family: Arial, Helvetica, sans-serif; font-size: 12px; letter-spacing: 1px;
                        text-transform: uppercase; color: #1b1b1b; font-weight: 600;'>
                Options
            </div>
        </div>
    """, unsafe_allow_html=True)
    show_data_table = st.checkbox("Afficher les tables de données", value=False)
    chart_height = st.slider("Hauteur des graphiques", 300, 800, 500, 50)

# Filtrer les données
filtered_mortality = data['mortality'][data['mortality']['cancer'].isin(selected_cancers)]
filtered_budget = data['budget'][data['budget']['cancer'].isin(selected_cancers)]
filtered_geography = data['geography'][data['geography']['cancer'].isin(selected_cancers)]
filtered_trends = data['trends'][data['trends']['cancer'].isin(selected_cancers)]

if 'status' in data['trials'].columns:
    filtered_trials = data['trials'][
        (data['trials']['cancer'].isin(selected_cancers)) &
        (data['trials']['status'].isin(selected_status))
    ]
else:
    filtered_trials = data['trials'][data['trials']['cancer'].isin(selected_cancers)]

# Section KPIs
st.markdown("""
    <div style='padding: 1.5rem 0 1rem 0;'>
        <div style='border-top: 2px solid #1b1b1b; margin-bottom: 0.75rem;'></div>
        <div style='font-family: Arial, Helvetica, sans-serif; font-size: 12px; letter-spacing: 1px;
                    text-transform: uppercase; color: #1b1b1b; font-weight: 600; margin-bottom: 0.5rem;'>
            Indicateurs Clés de Performance
        </div>
        <div style='border-bottom: 1px solid #d8d2c7; margin-bottom: 1.5rem;'></div>
    </div>
""", unsafe_allow_html=True)

kpi_cols = st.columns(5)

with kpi_cols[0]:
    total_trials = kpis['kpi1']['total_trials'].iloc[0] if 'kpi1' in kpis else len(filtered_trials)
    st.metric("Total Essais", f"{total_trials:,}")

with kpi_cols[1]:
    if 'kpi4' in kpis:
        avg_budget = kpis['kpi4']['avg_budget_musd'].iloc[0]
        st.metric("Budget Moyen", f"${avg_budget:.1f}M")

with kpi_cols[2]:
    if 'kpi5' in kpis and not kpis['kpi5'].empty:
        most_deadly = kpis['kpi5']['cancer'].iloc[0]
        # Afficher le nom complet ou juste les 2 premiers mots si trop long
        display_name = ' '.join(most_deadly.split()[:2]) if len(most_deadly.split()) > 2 else most_deadly
        st.metric("Cancer + Mortel", display_name)

with kpi_cols[3]:
    if 'kpi10' in kpis:
        avg_interest = kpis['kpi10']['avg_interest_score'].iloc[0]
        st.metric("Intérêt Média Moy.", f"{avg_interest:.1f}")

with kpi_cols[4]:
    nb_cancers = len(selected_cancers)
    st.metric("Types de Cancer", nb_cancers)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs pour organiser les graphiques
tab1, tab2, tab3, tab4 = st.tabs(["Recherche & Mortalité", "Budget NCI", "Essais Cliniques", "Tendances Média"])

# TAB 1: Recherche & Mortalité
with tab1:
    st.header("Recherche & Mortalité")

    col1, col2 = st.columns(2)

    with col1:
        # Scatter plot: Corrélation Mortalité vs Publications
        if not filtered_mortality.empty:
            fig = px.scatter(
                filtered_mortality,
                x='mortality_2022',
                y='publications_2024',
                color='cancer',
                size='mortality_2022',
                title="Corrélation Mortalité vs Effort de Recherche",
                labels={
                    'mortality_2022': 'Mortalité 2022 (décès)',
                    'publications_2024': 'Publications 2024'
                },
                color_discrete_sequence=['#2d5a7b', '#4a7ba7', '#6b9bc3', '#8fb8d9', '#b3d4ed', '#d6ebf5'],
                height=chart_height
            )
            fig.update_traces(marker=dict(line=dict(width=1, color='#1b1b1b'), opacity=0.85))
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color="#000000", size=12, family='Arial'),
                title_font=dict(size=18, color='#141311', family='Georgia'),
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Publications par 1000 décès
        if not filtered_mortality.empty and 'publications_per_1000_deaths' in filtered_mortality.columns:
            sorted_data = filtered_mortality.sort_values('publications_per_1000_deaths', ascending=True)
            fig = px.bar(
                sorted_data,
                y='cancer',
                x='publications_per_1000_deaths',
                orientation='h',
                title="Intensité de la Recherche par Type de Cancer",
                labels={
                    'publications_per_1000_deaths': 'Publications par 1000 décès',
                    'cancer': 'Type de Cancer'
                },
                color='publications_per_1000_deaths',
                color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
                height=chart_height
            )
            fig.update_traces(marker_line_color='#1b1b1b', marker_line_width=0.5)
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                showlegend=False,
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    # KPI8: Research Gap
    if 'kpi8' in kpis:
        st.subheader("Research Gap (Décès par Publication)")
        gap_data = kpis['kpi8']
        gap_data = gap_data[gap_data['cancer'].isin(selected_cancers)]

        fig = px.bar(
            gap_data,
            x='cancer',
            y='deaths_per_publication',
            title="Research Gap: Plus la barre est haute, plus le cancer est sous-représenté dans la recherche",
            labels={
                'deaths_per_publication': 'Décès par Publication',
                'cancer': 'Type de Cancer'
            },
            color='deaths_per_publication',
            color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
            height=400
        )
        fig.update_traces(marker_line_color='white', marker_line_width=1.5)
        fig.update_layout(
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            font=dict(color='#000000', size=14),
            title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
            xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
            yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
            hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: Budget NCI
with tab2:
    st.header("Budget NCI 2023")

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart: Répartition du Budget
        if not filtered_budget.empty:
            fig = px.pie(
                filtered_budget,
                values='budget_2023_million_usd',
                names='cancer',
                title="Répartition du Budget NCI 2023",
                color_discrete_sequence=['#2d5a7b', '#4a7ba7', '#6b9bc3', '#8fb8d9', '#b3d4ed', '#d6ebf5'],
                height=chart_height
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=14,
                textfont_color='white',
                marker=dict(line=dict(color='#1b1b1b', width=1))
            )
            fig.update_layout(
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar chart: Budget par cancer
        if not filtered_budget.empty:
            fig = px.bar(
                filtered_budget,
                x='cancer',
                y='budget_2023_million_usd',
                title="Budget NCI 2023 par Type de Cancer",
                labels={
                    'budget_2023_million_usd': 'Budget (Millions USD)',
                    'cancer': 'Type de Cancer'
                },
                color='budget_2023_million_usd',
                color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
                height=chart_height
            )
            fig.update_traces(marker_line_color='#1b1b1b', marker_line_width=0.5)
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    # Budget par décès
    if not filtered_budget.empty:
        budget_merged = pd.merge(
            filtered_budget,
            filtered_mortality[['cancer', 'mortality_2022']],
            on='cancer',
            how='left'
        )
        budget_merged['budget_per_death'] = (
            budget_merged['budget_2023_million_usd'] * 1_000_000
        ) / budget_merged['mortality_2022']

        budget_sorted = budget_merged.sort_values('budget_per_death', ascending=True)

        fig = px.bar(
            budget_sorted,
            y='cancer',
            x='budget_per_death',
            orientation='h',
            title="Investissement par Décès (USD)",
            labels={
                'budget_per_death': 'Budget par Décès (USD)',
                'cancer': 'Type de Cancer'
            },
            color='budget_per_death',
            color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
            height=500
        )
        fig.update_traces(marker_line_color='white', marker_line_width=1.5)
        fig.update_layout(
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            font=dict(color='#2d3748', size=12, family='Inter'),
            title_font=dict(size=18, color='#1a202c', family='Inter'),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter")
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 3: Essais Cliniques
with tab3:
    st.header("Distribution Géographique des Essais Cliniques")

    # Stacked bar chart
    if not filtered_geography.empty:
        regions = ['asia', 'canada', 'europe', 'latin_america', 'middle_east', 'oceania', 'usa', 'other']
        available_regions = [r for r in regions if r in filtered_geography.columns]

        fig = go.Figure()
        colors_map = {
            'asia': '#2d5a7b',
            'canada': '#4a7ba7',
            'europe': '#6b9bc3',
            'latin_america': '#8fb8d9',
            'middle_east': '#b3d4ed',
            'oceania': '#d6ebf5',
            'usa': '#1b3a4f',
            'other': '#c0c0c0'
        }

        for region in available_regions:
            fig.add_trace(go.Bar(
                name=region.replace('_', ' ').title(),
                x=filtered_geography[region],
                y=filtered_geography['cancer'],
                orientation='h',
                marker=dict(
                    color=colors_map.get(region, '#2d5a7b'),
                    line=dict(color='#1b1b1b', width=0.5)
                )
            ))

        fig.update_layout(
            barmode='stack',
            title="Distribution Géographique des Essais Cliniques",
            xaxis_title="Nombre d'Essais",
            yaxis_title="Type de Cancer",
            height=chart_height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#000000', size=14, family='Arial'),
            title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
            xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
            yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
            hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000"),
            legend=dict(
                bgcolor='white',
                bordercolor='#d8d2c7',
                borderwidth=1,
                font=dict(family='Arial', size=12, color='#000000')
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Total par cancer
        if not filtered_geography.empty:
            filtered_geography['total_trials'] = filtered_geography[available_regions].sum(axis=1)
            fig = px.bar(
                filtered_geography,
                x='cancer',
                y='total_trials',
                title="Total des Essais Cliniques par Cancer",
                labels={
                    'total_trials': "Nombre Total d'Essais",
                    'cancer': 'Type de Cancer'
                },
                color='total_trials',
                color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
                height=chart_height
            )
            fig.update_traces(marker_line_color='#1b1b1b', marker_line_width=0.5)
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Heatmap
        if not filtered_geography.empty:
            heatmap_data = filtered_geography.set_index('cancer')[available_regions]
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Région", y="Cancer", color="Nb Essais"),
                title="Heatmap: Essais par Cancer et Région",
                color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
                height=chart_height
            )
            fig.update_layout(
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    # KPI2: Nombre d'essais par cancer
    if 'kpi2' in kpis:
        st.subheader("Nombre d'Essais par Type de Cancer")
        trials_data = kpis['kpi2']
        trials_filtered = trials_data[trials_data['cancer'].isin(selected_cancers)]

        fig = px.bar(
            trials_filtered,
            x='cancer',
            y='trials_count',
            color='trials_count',
            color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
            title="Distribution des Essais Cliniques",
            height=400
        )
        fig.update_traces(marker_line_color='white', marker_line_width=1.5)
        fig.update_layout(
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            font=dict(color='#2d3748', size=12, family='Inter'),
            title_font=dict(size=18, color='#1a202c', family='Inter'),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter")
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 4: Tendances Média
with tab4:
    st.header("Intérêt Médiatique (Google Trends)")

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart: Intérêt moyen
        if not filtered_trends.empty and 'mean_interest_score' in filtered_trends.columns:
            fig = px.bar(
                filtered_trends,
                x='cancer',
                y='mean_interest_score',
                title="Intérêt Médiatique par Cancer (Google Trends)",
                labels={
                    'mean_interest_score': "Score d'Intérêt Moyen",
                    'cancer': 'Type de Cancer'
                },
                color='mean_interest_score',
                color_continuous_scale=['#d6ebf5', '#6b9bc3', '#2d5a7b'],
                height=chart_height
            )
            fig.update_traces(marker_line_color='#1b1b1b', marker_line_width=0.5)
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Pie chart: Visibilité relative
        if not filtered_trends.empty and 'relative_visibility_percent' in filtered_trends.columns:
            fig = px.pie(
                filtered_trends,
                values='relative_visibility_percent',
                names='cancer',
                title="Répartition de l'Attention Médiatique",
                color_discrete_sequence=['#2d5a7b', '#4a7ba7', '#6b9bc3', '#8fb8d9', '#b3d4ed', '#d6ebf5'],
                height=chart_height
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=14,
                textfont_color='white',
                marker=dict(line=dict(color='#1b1b1b', width=1))
            )
            fig.update_layout(
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

    # Scatter: Mortalité vs Intérêt médiatique
    if not filtered_trends.empty:
        trends_merged = pd.merge(
            filtered_trends,
            filtered_mortality[['cancer', 'mortality_2022']],
            on='cancer',
            how='left'
        )

        if 'mean_interest_score' in trends_merged.columns:
            fig = px.scatter(
                trends_merged,
                x='mortality_2022',
                y='mean_interest_score',
                size='mortality_2022',
                color='cancer',
                title="Visibilité Médiatique vs Gravité Sanitaire",
                labels={
                    'mortality_2022': 'Mortalité 2022 (décès)',
                    'mean_interest_score': "Score d'Intérêt Média"
                },
                color_discrete_sequence=['#2d5a7b', '#4a7ba7', '#6b9bc3', '#8fb8d9', '#b3d4ed', '#d6ebf5'],
                height=500
            )
            fig.update_traces(marker=dict(line=dict(width=1, color='#1b1b1b'), opacity=0.85))
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#000000', size=14, family='Arial'),
                title_font=dict(size=20, color='#1b1b1b', family='Georgia'),
                xaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                yaxis=dict(title_font=dict(size=13, color='#000000'), tickfont=dict(size=12, color='#000000')),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial", font_color="#000000")
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()

# Section des tables de données
if show_data_table:
    st.header("📋 Aperçu des Données")

    table_tab1, table_tab2, table_tab3, table_tab4 = st.tabs([
        "Mortalité", "Budget", "Essais Cliniques", "Tendances"
    ])

    with table_tab1:
        st.dataframe(filtered_mortality, use_container_width=True, height=400)

    with table_tab2:
        st.dataframe(filtered_budget, use_container_width=True, height=400)

    with table_tab3:
        st.dataframe(filtered_trials.head(100), use_container_width=True, height=400)
        st.info(f"Affichage des 100 premiers essais sur {len(filtered_trials)} au total")

    with table_tab4:
        st.dataframe(filtered_trends, use_container_width=True, height=400)

# Footer sobre
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='padding: 20px 30px; background: #fafaf8; border-top: 3px double #2d5a7b; text-align: center;'>
        <div style='padding-bottom: 8px; font-family: Georgia, "Times New Roman", serif; font-size: 13px; color: #333;'>
            Cancer Research Analytics Dashboard
        </div>
        <div style='font-family: Arial, Helvetica, sans-serif; font-size: 10px; color: #999; line-height: 1.6;'>
            <strong>Sources:</strong> NCI Budget 2023 · PubMed 2024 · Google Trends · ClinicalTrials.gov<br>
            Dernière mise à jour: Janvier 2026
        </div>
    </div>
""", unsafe_allow_html=True)
