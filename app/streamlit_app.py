"""
NidDouillet — Observatoire du marche immobilier toulonnais
Dashboard principal Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from analysis.stats import (
    mean, median, variance, standard_deviation,
    correlation, percentile, describe
)
from analysis.regression import least_squares_fit, predict, r_squared
from analysis.scoring import opportunity_score, knn_similar

st.set_page_config(
    page_title="NidDouillet - Observatoire Immobilier",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :root {
    --nd-bg: #fafafa;
    --nd-surface: #ffffff;
    --nd-border: #e5e7eb;
    --nd-text: #1a1a2e;
    --nd-text-secondary: #374151;
    --nd-text-muted: #6b7280;
    --nd-text-faint: #9ca3af;
    --nd-hover: #f9fafb;
    --nd-input-bg: #ffffff;
    --nd-accent: #2563eb;
    --nd-green-bg: #f0fdf4;
    --nd-green: #16a34a;
    --nd-green-border: #bbf7d0;
    --nd-yellow-bg: #fffbeb;
    --nd-yellow: #d97706;
    --nd-yellow-border: #fde68a;
    --nd-red-bg: #fef2f2;
    --nd-red: #dc2626;
    --nd-red-border: #fecaca;
    --nd-info-bg: #eff6ff;
    --nd-info: #1e40af;
    --nd-info-border: #bfdbfe;
    --nd-success-bg: #f0fdf4;
    --nd-success: #166534;
    --nd-success-border: #bbf7d0;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --nd-bg: #0f1117;
      --nd-surface: #1a1c25;
      --nd-border: #2d3040;
      --nd-text: #e8e9ed;
      --nd-text-secondary: #c4c7cf;
      --nd-text-muted: #8b8fa3;
      --nd-text-faint: #6b6f82;
      --nd-hover: #22242e;
      --nd-input-bg: #1a1c25;
      --nd-accent: #4d8ef7;
      --nd-green-bg: #0d2818;
      --nd-green: #4ade80;
      --nd-green-border: #166534;
      --nd-yellow-bg: #271e08;
      --nd-yellow: #fbbf24;
      --nd-yellow-border: #92400e;
      --nd-red-bg: #2a0f0f;
      --nd-red: #f87171;
      --nd-red-border: #991b1b;
      --nd-info-bg: #0c1a33;
      --nd-info: #93c5fd;
      --nd-info-border: #1e3a5f;
      --nd-success-bg: #0d2818;
      --nd-success: #86efac;
      --nd-success-border: #166534;
    }
  }

  html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"],
  [data-testid="stHeader"], .main, .main .block-container,
  [data-testid="stAppViewBlockContainer"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--nd-text) !important;
  }

  .stApp, [data-testid="stAppViewContainer"], .main,
  [data-testid="stAppViewBlockContainer"] {
    background-color: var(--nd-bg) !important;
  }

  [data-testid="stHeader"] {
    background-color: var(--nd-bg) !important;
  }

  h1, h2, h3, h4, h5, h6,
  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Inter', sans-serif !important;
    color: var(--nd-text) !important;
    font-weight: 700 !important;
  }

  p, span, div, label, li {
    color: var(--nd-text);
  }

  section[data-testid="stSidebar"] {
    background: var(--nd-surface) !important;
    border-right: 1px solid var(--nd-border) !important;
  }
  section[data-testid="stSidebar"] > div {
    background: var(--nd-surface) !important;
  }
  section[data-testid="stSidebar"] * {
    color: var(--nd-text-secondary) !important;
  }
  section[data-testid="stSidebar"] hr {
    border-color: var(--nd-border) !important;
  }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stSlider label {
    color: var(--nd-text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
  }

  .stRadio > div {
    gap: 0.2rem !important;
  }
  .stRadio label span {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
  }

  .sidebar-brand {
    padding: 0.8rem 0 0.6rem 0;
    border-bottom: 1px solid var(--nd-border);
    margin-bottom: 1rem;
  }
  .sidebar-brand .logo-text {
    font-size: 1.15rem;
    color: var(--nd-text) !important;
    font-weight: 700;
    letter-spacing: -0.02em;
  }
  .sidebar-brand .logo-sub {
    font-size: 0.7rem;
    color: var(--nd-text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
  }

  .main .block-container {
    padding-top: 1.5rem;
  }

  .hero {
    background: var(--nd-surface);
    border: 1px solid var(--nd-border);
    border-radius: 12px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.5rem;
  }
  .hero h1 {
    font-size: 1.8rem !important;
    margin: 0 0 0.3rem 0 !important;
    letter-spacing: -0.02em !important;
  }
  .hero p {
    color: var(--nd-text-muted) !important;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.5;
  }
  .hero-badge {
    display: inline-block;
    background: var(--nd-green-bg);
    color: var(--nd-green) !important;
    border: 1px solid var(--nd-green-border);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
  }

  .kpi-card {
    background: var(--nd-surface);
    border: 1px solid var(--nd-border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
  }
  .kpi-label {
    color: var(--nd-text-muted) !important;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
  }
  .kpi-value {
    color: var(--nd-text) !important;
    font-size: 1.6rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.02em;
  }
  .kpi-sub {
    color: var(--nd-text-faint) !important;
    font-size: 0.72rem;
    margin-top: 0.3rem;
  }
  .kpi-desc {
    color: var(--nd-text-muted) !important;
    font-size: 0.68rem;
    margin-top: 0.5rem;
    line-height: 1.4;
    border-top: 1px solid var(--nd-border);
    padding-top: 0.4rem;
  }

  .score-high   { background: var(--nd-green-bg); color: var(--nd-green) !important; border: 1px solid var(--nd-green-border); border-radius: 6px; padding: 3px 10px; font-weight: 600; font-size: 0.8rem; display: inline-block; }
  .score-medium { background: var(--nd-yellow-bg); color: var(--nd-yellow) !important; border: 1px solid var(--nd-yellow-border); border-radius: 6px; padding: 3px 10px; font-weight: 600; font-size: 0.8rem; display: inline-block; }
  .score-low    { background: var(--nd-red-bg); color: var(--nd-red) !important; border: 1px solid var(--nd-red-border); border-radius: 6px; padding: 3px 10px; font-weight: 600; font-size: 0.8rem; display: inline-block; }

  .section-title {
    font-size: 1.1rem;
    color: var(--nd-text) !important;
    font-weight: 700;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--nd-border);
  }

  [data-testid="stDataFrame"] {
    background: var(--nd-surface) !important;
    border-radius: 8px;
    border: 1px solid var(--nd-border) !important;
  }

  [data-testid="metric-container"] {
    background: var(--nd-surface) !important;
    border: 1px solid var(--nd-border) !important;
    border-radius: 10px !important;
    padding: 1rem;
  }
  [data-testid="metric-container"] label {
    color: var(--nd-text-muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--nd-text) !important;
  }

  [data-testid="stInfo"] {
    background: var(--nd-info-bg) !important;
    border: 1px solid var(--nd-info-border) !important;
    color: var(--nd-info) !important;
    border-radius: 8px;
  }

  [data-testid="stSuccess"] {
    background: var(--nd-success-bg) !important;
    border: 1px solid var(--nd-success-border) !important;
    color: var(--nd-success) !important;
    border-radius: 8px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    color: var(--nd-text-secondary) !important;
  }
  th {
    background: var(--nd-hover) !important;
    color: var(--nd-text-muted) !important;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 10px 14px;
    border-bottom: 1px solid var(--nd-border);
    font-weight: 600;
  }
  td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--nd-border);
    color: var(--nd-text-secondary) !important;
  }
  tr:hover td { background: var(--nd-hover) !important; }

  .footer {
    text-align: center;
    color: var(--nd-text-faint) !important;
    font-size: 0.7rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--nd-border);
    letter-spacing: 0.03em;
  }

  .ann-card {
    background: var(--nd-surface);
    border: 1px solid var(--nd-border);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.8rem;
  }
  .ann-card:hover { border-color: var(--nd-accent); }

  [data-baseweb="select"] > div {
    background: var(--nd-input-bg) !important;
    border-color: var(--nd-border) !important;
  }
  [data-baseweb="input"] > div {
    background: var(--nd-input-bg) !important;
    border-color: var(--nd-border) !important;
  }
  .stSlider [data-testid="stTickBarMin"],
  .stSlider [data-testid="stTickBarMax"] {
    color: var(--nd-text-muted) !important;
  }
</style>
""", unsafe_allow_html=True)


def _no_data_screen(message: str):
    st.markdown(f"""
    <div style="
        background: var(--nd-surface);
        border: 1px solid var(--nd-border);
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem 0;
    ">
      <div style="font-size: 1.3rem; color: var(--nd-text); font-weight: 700; margin-bottom: 0.6rem;">
        Donnees en attente
      </div>
      <div style="color: var(--nd-text-muted); font-size: 0.9rem; max-width: 400px; margin: 0 auto; line-height: 1.6;">
        {message}
      </div>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(show_spinner="Chargement des donnees DVF...")
def load_dvf():
    dvf_path = ROOT / "data" / "dvf_toulon_clean.csv"
    if not dvf_path.exists():
        dvf_path = ROOT / "data" / "dvf_toulon.csv"
    if not dvf_path.exists():
        return None

    df = pd.read_csv(dvf_path, low_memory=False)
    col_map = {}
    prix_mapped = False
    for col in df.columns:
        lc = col.lower().replace(" ", "_")
        if not prix_mapped and ("valeur" in lc or lc == "prix"):
            col_map[col] = "prix"
            prix_mapped = True
        elif "surface" in lc and "bati" in lc:
            col_map[col] = "surface"
        elif "commune" in lc or "nom_commune" in lc:
            col_map[col] = "commune"
        elif "code_postal" in lc or "cp" in lc:
            col_map[col] = "code_postal"
        elif "type_local" in lc or "nature" in lc:
            col_map[col] = "type_bien"
        elif "date" in lc and "mutation" in lc:
            col_map[col] = "date"
        elif "zone" in lc or "quartier" in lc:
            col_map[col] = "quartier"
        elif "nombre_pieces" in lc or "nb_pieces" in lc:
            col_map[col] = "pieces"
    df = df.rename(columns=col_map)
    if "commune" in df.columns:
        df = df[df["commune"].str.upper().str.contains("TOULON", na=False)]
    elif "code_postal" in df.columns:
        df["code_postal"] = pd.to_numeric(df["code_postal"], errors="coerce")
        df = df[(df["code_postal"] >= 83000) & (df["code_postal"] <= 83100)]
    for col in ["prix", "surface"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "prix" in df.columns and "surface" in df.columns:
        df = df[(df["prix"] > 10_000) & (df["surface"] > 5) & (df["surface"] < 500)]
        df["prix_m2"] = df["prix"] / df["surface"]
    return df


@st.cache_data(show_spinner="Chargement des annonces...")
def load_annonces():
    for name in ["annonces_toulon.csv", "annonces.csv", "annonces_actuelles.csv"]:
        p = ROOT / "data" / name
        if p.exists():
            df = pd.read_csv(p, low_memory=False)
            if "prix" in df.columns:
                df["prix"] = df["prix"].astype(str).str.replace(r"[^\d]", "", regex=True)
                df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
            if "surface" in df.columns:
                df["surface"] = pd.to_numeric(df["surface"], errors="coerce")
            if "prix_m2" in df.columns:
                df["prix_m2"] = df["prix_m2"].astype(str).str.replace(r"[^\d]", "", regex=True)
                df["prix_m2"] = pd.to_numeric(df["prix_m2"], errors="coerce")
            elif "prix" in df.columns and "surface" in df.columns:
                df["prix_m2"] = df["prix"] / df["surface"]
            if "nb_pieces" in df.columns and "pieces" not in df.columns:
                df = df.rename(columns={"nb_pieces": "pieces"})
            return df
    return None


with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="logo-text">NidDouillet</div>
      <div class="logo-sub">Observatoire Immobilier Toulonnais</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Tableau de bord", "Carte des prix", "Tendances",
         "Opportunites", "Analyse detaillee"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("<span style='color:var(--nd-text-muted);font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em'>Filtres</span>", unsafe_allow_html=True)

    df_dvf_raw = load_dvf()
    df_ann_raw = load_annonces()

    dvf_ok = df_dvf_raw is not None
    ann_ok = df_ann_raw is not None

    type_options = ["Tous"] + sorted(df_dvf_raw["type_bien"].dropna().unique().tolist()) \
        if dvf_ok and "type_bien" in df_dvf_raw.columns else ["Tous"]
    type_filter = st.selectbox("Type de bien", type_options)

    prix_max = int(df_dvf_raw["prix"].quantile(0.99)) \
        if dvf_ok and "prix" in df_dvf_raw.columns else 900_000
    budget = st.slider("Budget max", 100_000, prix_max, 450_000, step=10_000, format="%d EUR")

    surface_min = st.slider("Surface min", 10, 150, 30, format="%d m2")

    quartier_options = ["Tous"] + sorted(df_dvf_raw["quartier"].dropna().unique().tolist()) \
        if dvf_ok and "quartier" in df_dvf_raw.columns else ["Tous"]
    quartier_filter = st.selectbox("Quartier", quartier_options)

    pieces_options = ["Tous"] + sorted(df_dvf_raw["pieces"].dropna().astype(int).unique().tolist()) \
        if dvf_ok and "pieces" in df_dvf_raw.columns else ["Tous"]
    pieces_filter = st.selectbox("Nombre de pieces", pieces_options)

    st.divider()
    dvf_count = f"{len(df_dvf_raw):,}" if dvf_ok else "—"
    ann_count = f"{len(df_ann_raw):,}" if ann_ok else "—"
    st.markdown(
        f"<small style='color:var(--nd-text-faint)'>{dvf_count} transactions DVF<br>{ann_count} annonces actives</small>",
        unsafe_allow_html=True
    )


def apply_filters(df):
    if df is None:
        return None
    d = df.copy()
    if type_filter != "Tous" and "type_bien" in d.columns:
        d = d[d["type_bien"] == type_filter]
    if "prix" in d.columns:
        d = d[d["prix"] <= budget]
    if "surface" in d.columns:
        d = d[d["surface"] >= surface_min]
    if quartier_filter != "Tous" and "quartier" in d.columns:
        d = d[d["quartier"] == quartier_filter]
    if pieces_filter != "Tous" and "pieces" in d.columns:
        d = d[d["pieces"] == int(pieces_filter)]
    return d

df_dvf = apply_filters(df_dvf_raw)
df_ann = apply_filters(df_ann_raw)

ACCENT = "#1a1a2e"
BLUE   = "#2563eb"
GREEN  = "#16a34a"
COLORS = [BLUE, "#0891b2", "#7c3aed", "#db2777", "#ea580c", "#16a34a"]

_dark = st.get_option("theme.base") == "dark"

if _dark:
    _paper = "#0f1117"
    _plot  = "#0f1117"
    _font_c = "#c4c7cf"
    _grid  = "#2d3040"
    _tpl   = "plotly_dark"
    _map_style = "carto-darkmatter"
else:
    _paper = "#ffffff"
    _plot  = "#ffffff"
    _font_c = "#374151"
    _grid  = "#f3f4f6"
    _tpl   = "plotly_white"
    _map_style = "carto-positron"

PLOTLY_LAYOUT = dict(
    template=_tpl,
    paper_bgcolor=_paper,
    plot_bgcolor=_plot,
    font=dict(color=_font_c, family="Inter"),
    margin=dict(l=0, r=0, t=10, b=0),
)


if page == "Tableau de bord":

    st.markdown("""
    <div class="hero">
      <div class="hero-badge">Donnees a jour</div>
      <h1>Observatoire NidDouillet</h1>
      <p>Marche immobilier de Toulon — Donnees DVF data.gouv.fr et annonces SeLoger</p>
    </div>
    """, unsafe_allow_html=True)

    if df_dvf is None:
        _no_data_screen("Les donnees DVF n'ont pas encore ete integrees.")
        st.stop()

    pm2_vals = df_dvf["prix_m2"].dropna().tolist() if "prix_m2" in df_dvf.columns else []
    pm2_mean = mean(pm2_vals) if pm2_vals else 0
    pm2_med  = median(pm2_vals) if pm2_vals else 0
    pm2_std  = standard_deviation(pm2_vals) if pm2_vals else 0
    n_trans  = len(df_dvf)

    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        (
            "Prix moyen au m2",
            f"{pm2_mean:,.0f} EUR/m2",
            f"Mediane : {pm2_med:,.0f} EUR/m2",
            "Prix de vente moyen par metre carre, calcule sur l'ensemble des transactions DVF filtrees.",
        ),
        (
            "Transactions",
            f"{n_trans:,} ventes",
            f"sur {len(df_dvf_raw):,} au total",
            "Nombre de ventes immobilieres enregistrees correspondant aux filtres appliques (type, budget, surface, quartier).",
        ),
        (
            "Budget au m2",
            f"{budget / surface_min:,.0f} EUR/m2",
            f"Budget de {budget // 1000:,.0f}k EUR pour {surface_min} m2 min",
            "Rapport entre votre budget et la surface minimum. Permet de comparer avec le prix moyen du marche.",
        ),
        (
            "Ecart-type",
            f"{pm2_std:,.0f} EUR/m2",
            f"Moyenne a {pm2_mean:,.0f} EUR/m2",
            "Dispersion des prix au m2 autour de la moyenne. Plus il est eleve, plus les prix varient entre les biens.",
        ),
    ]
    for col, (label, value, sub, desc) in zip([col1, col2, col3, col4], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{value}</div>
              <div class="kpi-sub">{sub}</div>
              <div class="kpi-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Distribution des prix au m2</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        if pm2_vals:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=pm2_vals, nbinsx=50,
                                       marker_color=BLUE, opacity=0.8, name="DVF"))
            if df_ann is not None and "prix_m2" in df_ann.columns:
                fig.add_trace(go.Histogram(
                    x=df_ann["prix_m2"].dropna().tolist(),
                    nbinsx=40, marker_color="#0891b2", opacity=0.6, name="Annonces"))
            fig.add_vline(x=pm2_mean, line_dash="dash", line_color="#dc2626",
                          annotation_text=f"Moyenne {pm2_mean:,.0f}",
                          annotation_font_color="#dc2626")
            fig.add_vline(x=pm2_med, line_dash="dot", line_color="#7c3aed",
                          annotation_text=f"Mediane {pm2_med:,.0f}",
                          annotation_font_color="#7c3aed")
            fig.update_layout(**PLOTLY_LAYOUT, height=320, barmode="overlay",
                               legend=dict(orientation="h", y=1.02),
                               xaxis_title="EUR/m2", yaxis_title="Nombre de biens",
                               xaxis=dict(gridcolor=_grid),
                               yaxis=dict(gridcolor=_grid))
            st.plotly_chart(fig, width="stretch")

    with col_b:
        if pm2_vals and len(pm2_vals) >= 4:
            stats = describe(pm2_vals)
            rows = {
                "Minimum":     f"{stats.get('min', min(pm2_vals)):,.0f} EUR/m2",
                "P25":         f"{percentile(pm2_vals, 25):,.0f} EUR/m2",
                "Mediane":     f"{pm2_med:,.0f} EUR/m2",
                "Moyenne":     f"{pm2_mean:,.0f} EUR/m2",
                "P75":         f"{percentile(pm2_vals, 75):,.0f} EUR/m2",
                "Maximum":     f"{stats.get('max', max(pm2_vals)):,.0f} EUR/m2",
                "Ecart-type":  f"{pm2_std:,.0f} EUR/m2",
                "Transactions": f"{n_trans:,}",
            }
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            for k, v in rows.items():
                c1, c2 = st.columns([1.3, 1])
                c1.markdown(f"<small style='color:var(--nd-text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.03em;font-size:0.7rem'>{k}</small>", unsafe_allow_html=True)
                c2.markdown(f"<small style='color:var(--nd-text);font-weight:600'>{v}</small>", unsafe_allow_html=True)

    if "quartier" in df_dvf.columns and "prix_m2" in df_dvf.columns:
        st.markdown('<div class="section-title">Prix moyen par quartier</div>', unsafe_allow_html=True)
        q_stats = (df_dvf.groupby("quartier")["prix_m2"]
                   .agg(["mean", "count"])
                   .sort_values("mean", ascending=True)
                   .reset_index())
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            y=q_stats["quartier"], x=q_stats["mean"], orientation="h",
            marker=dict(color=BLUE, opacity=0.85),
            name="Moyenne EUR/m2",
            text=q_stats["mean"].apply(lambda v: f"{v:,.0f} EUR"),
            textposition="outside",
            textfont=dict(color=_font_c, size=11),
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=280,
                            xaxis_title="EUR/m2",
                            xaxis=dict(gridcolor=_grid),
                            yaxis=dict(gridcolor=_grid))
        st.plotly_chart(fig2, width="stretch")


elif page == "Carte des prix":
    st.markdown('<div class="section-title">Carte des prix par zone</div>', unsafe_allow_html=True)
    if df_dvf is None:
        _no_data_screen("Les donnees DVF sont necessaires pour la carte.")
        st.stop()

    COORDS = {
        "Centre / Littoral": (43.1242, 5.9300),
        "Ouest Toulon":      (43.1400, 5.9050),
        "Est Toulon":        (43.1250, 5.9550),
    }

    if "quartier" in df_dvf.columns and "prix_m2" in df_dvf.columns:
        q_agg = df_dvf.groupby("quartier")["prix_m2"].mean().reset_index()
        q_agg["lat"] = q_agg["quartier"].map(lambda q: COORDS.get(q, (43.125, 5.93))[0])
        q_agg["lon"] = q_agg["quartier"].map(lambda q: COORDS.get(q, (43.125, 5.93))[1])
        q_agg.columns = ["quartier", "prix_m2_moyen", "lat", "lon"]

        fig_map = px.scatter_mapbox(
            q_agg, lat="lat", lon="lon",
            size="prix_m2_moyen", color="prix_m2_moyen",
            color_continuous_scale=[[0, "#dbeafe"], [0.5, BLUE], [1, "#1e3a5f"]],
            hover_name="quartier",
            hover_data={"prix_m2_moyen": ":.0f", "lat": False, "lon": False},
            zoom=12, height=520, size_max=50,
        )
        fig_map.update_layout(
            mapbox_style=_map_style,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=_paper,
            coloraxis_colorbar=dict(title="EUR/m2", tickfont=dict(color=_font_c), title_font=dict(color=_font_c)),
        )
        st.plotly_chart(fig_map, width="stretch")
        st.dataframe(
            q_agg[["quartier", "prix_m2_moyen"]].rename(
                columns={"quartier": "Zone", "prix_m2_moyen": "Prix moyen EUR/m2"}),
            width="stretch", hide_index=True)
    else:
        st.info("Donnees par quartier non disponibles.")


elif page == "Tendances":
    st.markdown('<div class="section-title">Evolution des prix dans le temps</div>', unsafe_allow_html=True)
    if df_dvf is None:
        _no_data_screen("Les donnees DVF sont necessaires pour les tendances.")
        st.stop()

    if "date" in df_dvf.columns and "prix_m2" in df_dvf.columns:
        df_t = df_dvf.copy()
        df_t["date"] = pd.to_datetime(df_t["date"], errors="coerce")
        df_t = df_t.dropna(subset=["date", "prix_m2"])
        df_t["mois"] = df_t["date"].dt.to_period("M").astype(str)
        monthly = (df_t.groupby("mois")["prix_m2"]
                   .agg(["mean", "count"])
                   .reset_index())
        monthly.columns = ["Mois", "Moyenne", "Transactions"]
        monthly = monthly[monthly["Transactions"] >= 3]

        if len(monthly) >= 3:
            xs = list(range(len(monthly)))
            ys = monthly["Moyenne"].tolist()
            alpha, beta = least_squares_fit(xs, ys)
            trend = [predict(alpha, beta, x) for x in xs]

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=monthly["Mois"], y=monthly["Moyenne"],
                mode="lines+markers", name="Prix moyen mensuel",
                line=dict(color=BLUE, width=2.5),
                marker=dict(size=5, color=BLUE)))
            fig_trend.add_trace(go.Scatter(
                x=monthly["Mois"], y=trend, mode="lines",
                name=f"Tendance ({beta:+.1f} EUR/mois)",
                line=dict(color="#dc2626", width=2, dash="dash")))
            fig_trend.update_layout(
                **PLOTLY_LAYOUT, height=380,
                legend=dict(orientation="h", y=1.05),
                xaxis_title="Mois", yaxis_title="Prix moyen EUR/m2",
                xaxis=dict(tickangle=45, gridcolor=_grid),
                yaxis=dict(gridcolor=_grid))
            st.plotly_chart(fig_trend, width="stretch")
            _trend_dir = "hausse" if beta > 0 else "baisse"
            st.markdown(f"""
            <div class="kpi-card" style="max-width:400px">
              <div class="kpi-label">Tendance mensuelle</div>
              <div class="kpi-value">{beta:+.1f} EUR/m2/mois</div>
              <div class="kpi-sub">Marche en {_trend_dir}</div>
              <div class="kpi-desc">Variation moyenne du prix au m2 d'un mois a l'autre, calculee par regression lineaire sur les donnees DVF.</div>
            </div>""", unsafe_allow_html=True)

    if "type_bien" in df_dvf.columns and "prix_m2" in df_dvf.columns:
        st.markdown('<div class="section-title">Repartition par type de bien</div>', unsafe_allow_html=True)
        fig_box = px.box(
            df_dvf.dropna(subset=["type_bien", "prix_m2"]),
            x="type_bien", y="prix_m2",
            color="type_bien", color_discrete_sequence=COLORS,
            template="plotly_white", height=340)
        fig_box.update_layout(
            paper_bgcolor=_paper, plot_bgcolor=_plot,
            font=dict(color=_font_c),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis_title="Type de bien", yaxis_title="EUR/m2",
            xaxis=dict(gridcolor=_grid),
            yaxis=dict(gridcolor=_grid))
        st.plotly_chart(fig_box, width="stretch")


elif page == "Opportunites":
    st.markdown('<div class="section-title">Analyse des opportunites</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:var(--nd-text-muted);font-size:0.88rem'>Chaque annonce est comparee au prix median du marche DVF. Un score eleve indique un bien potentiellement sous-evalue.</p>", unsafe_allow_html=True)
    if df_dvf is None or df_ann is None:
        _no_data_screen("Les donnees DVF et les annonces sont necessaires pour l'analyse des opportunites.")
        st.stop()

    if "prix_m2" in df_ann.columns and len(df_ann) > 0 and "prix_m2" in df_dvf.columns:
        market_pm2 = df_dvf["prix_m2"].dropna().tolist()
        scored = df_ann.copy()
        scored["score"] = scored["prix_m2"].apply(
            lambda p: opportunity_score(p, market_pm2) if pd.notna(p) else 0)
        scored = scored.sort_values("score", ascending=False)

        def _score_badge(s):
            if s >= 70:
                return "score-high", "Opportunite"
            elif s >= 45:
                return "score-medium", "Prix marche"
            return "score-low", "Surevalue"

        top = scored.head(12)
        cols = st.columns(3)
        for i, (_, row) in enumerate(top.iterrows()):
            with cols[i % 3]:
                photo = row.get("photo_1", "")
                if pd.notna(photo) and photo:
                    st.image(photo, use_container_width=True)
                sc_class, sc_label = _score_badge(row["score"])
                prix_fmt = f"{row['prix']:,.0f} EUR" if pd.notna(row.get("prix")) else "N/A"
                pm2_fmt = f"{row['prix_m2']:,.0f} EUR/m2" if pd.notna(row.get("prix_m2")) else ""
                surface_fmt = f"{row['surface']:.0f} m2" if pd.notna(row.get("surface")) else ""
                quartier = row.get("quartier", "")
                pieces = f"{int(row['pieces'])}p" if pd.notna(row.get("pieces")) else ""
                lien = row.get("lien", "")
                st.markdown(f"""
                <div class="ann-card">
                  <div style="margin-bottom:0.4rem">
                    <span class="{sc_class}">{row['score']:.0f}/100 — {sc_label}</span>
                  </div>
                  <div style="color:var(--nd-text);font-weight:700;font-size:1rem;margin-bottom:0.2rem">{prix_fmt}</div>
                  <div style="color:var(--nd-text-muted);font-size:0.82rem">{surface_fmt} {pieces} — {pm2_fmt}</div>
                  <div style="color:var(--nd-text-faint);font-size:0.78rem;margin-top:0.15rem">{quartier}</div>
                  {"<a href='" + str(lien) + "' target='_blank' style='color:" + BLUE + ";font-size:0.78rem;text-decoration:none;font-weight:500'>Voir l annonce</a>" if pd.notna(lien) and lien else ""}
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Prix vs Score</div>', unsafe_allow_html=True)
        fig_sc = px.scatter(
            scored.dropna(subset=["prix", "score"]),
            x="prix", y="score", color="score",
            color_continuous_scale=[[0, "#fecaca"], [0.45, "#fde68a"], [1, "#bbf7d0"]],
            size="surface" if "surface" in scored.columns else None,
            template="plotly_white", height=380)
        fig_sc.add_hline(y=70, line_dash="dot", line_color=GREEN,
                         annotation_text="Seuil opportunite",
                         annotation_font_color=GREEN)
        fig_sc.update_layout(
            paper_bgcolor=_paper, plot_bgcolor=_plot,
            font=dict(color=_font_c),
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Prix (EUR)", yaxis_title="Score",
            xaxis=dict(gridcolor=_grid),
            yaxis=dict(gridcolor=_grid))
        st.plotly_chart(fig_sc, width="stretch")

        st.markdown('<div class="section-title">Biens similaires — k-NN</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:var(--nd-text-muted);font-size:0.85rem'>Selectionnez un bien pour identifier les 5 annonces les plus proches par surface et prix.</p>", unsafe_allow_html=True)

        ann_valid = scored.dropna(subset=["prix", "surface"]).reset_index(drop=True)
        if len(ann_valid) >= 6:
            ann_labels = [f"{r['prix']:,.0f} EUR — {r['surface']:.0f} m2 — {r.get('quartier','')}" for _, r in ann_valid.iterrows()]
            selected_idx = st.selectbox("Selectionner un bien de reference", range(len(ann_labels)), format_func=lambda i: ann_labels[i])

            target = [ann_valid.iloc[selected_idx]["surface"], ann_valid.iloc[selected_idx]["prix"]]
            dataset = ann_valid[["surface", "prix"]].values.tolist()
            labels = list(range(len(ann_valid)))

            neighbors = knn_similar(target, dataset, labels, k=6)
            neighbors = [n for n in neighbors if n != selected_idx][:5]

            n_cols = st.columns(5)
            for i, idx in enumerate(neighbors):
                row = ann_valid.iloc[idx]
                with n_cols[i]:
                    photo = row.get("photo_1", "")
                    if pd.notna(photo) and photo:
                        st.image(photo, use_container_width=True)
                    prix_fmt = f"{row['prix']:,.0f} EUR" if pd.notna(row.get("prix")) else ""
                    surface_fmt = f"{row['surface']:.0f} m2" if pd.notna(row.get("surface")) else ""
                    lien = row.get("lien", "")
                    st.markdown(f"""
                    <div class="ann-card" style="font-size:0.8rem">
                      <div style="color:var(--nd-text);font-weight:700">{prix_fmt}</div>
                      <div style="color:var(--nd-text-muted)">{surface_fmt}</div>
                      <div style="color:var(--nd-text-faint);font-size:0.72rem">{row.get('quartier','')}</div>
                      {"<a href='" + str(lien) + "' target='_blank' style='color:" + BLUE + ";font-size:0.72rem;text-decoration:none'>Voir</a>" if pd.notna(lien) and lien else ""}
                    </div>""", unsafe_allow_html=True)


elif page == "Analyse detaillee":
    st.markdown('<div class="section-title">Statistiques detaillees</div>', unsafe_allow_html=True)
    if df_dvf is None:
        _no_data_screen("Les donnees DVF sont necessaires.")
        st.stop()

    if "prix_m2" in df_dvf.columns and "surface" in df_dvf.columns:
        pm2  = df_dvf["prix_m2"].dropna().tolist()
        surf = df_dvf["surface"].dropna().tolist()

        _stat_labels = {
            "min": ("Minimum", "Valeur la plus basse observee dans les transactions filtrees."),
            "max": ("Maximum", "Valeur la plus haute observee dans les transactions filtrees."),
            "mean": ("Moyenne", "Somme des valeurs divisee par le nombre de transactions."),
            "median": ("Mediane", "Valeur centrale : 50%% des biens sont au-dessus, 50%% en dessous."),
            "variance": ("Variance", "Mesure mathematique de la dispersion des valeurs autour de la moyenne."),
            "std": ("Ecart-type", "Dispersion typique des valeurs. Plus il est grand, plus les prix sont heterogenes."),
        }

        if pm2 and surf:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Prix au m2")
                for k, v in describe(pm2).items():
                    lbl, tip = _stat_labels.get(k, (k.capitalize(), ""))
                    st.markdown(f"""
                    <div class="kpi-card" style="margin-bottom:0.6rem">
                      <div class="kpi-label">{lbl}</div>
                      <div class="kpi-value">{v:,.0f} EUR/m2</div>
                      <div class="kpi-desc">{tip}</div>
                    </div>""", unsafe_allow_html=True)
            with col2:
                st.subheader("Surface")
                for k, v in describe(surf[:len(pm2)]).items():
                    lbl, tip = _stat_labels.get(k, (k.capitalize(), ""))
                    st.markdown(f"""
                    <div class="kpi-card" style="margin-bottom:0.6rem">
                      <div class="kpi-label">{lbl}</div>
                      <div class="kpi-value">{v:,.0f} m2</div>
                      <div class="kpi-desc">{tip}</div>
                    </div>""", unsafe_allow_html=True)

            n_min = min(len(pm2), len(surf))
            if n_min >= 5:
                corr = correlation(pm2[:n_min], surf[:n_min])
                st.divider()
                _corr_interp = "forte" if abs(corr) > 0.7 else "moderee" if abs(corr) > 0.4 else "faible"
                _corr_dir = "negative" if corr < 0 else "positive"
                st.markdown(f"""
                <div class="kpi-card" style="max-width:500px">
                  <div class="kpi-label">Correlation surface / prix au m2</div>
                  <div class="kpi-value">{corr:.4f}</div>
                  <div class="kpi-sub">Correlation {_corr_interp} {_corr_dir}</div>
                  <div class="kpi-desc">Coefficient entre -1 et 1. Indique si la surface et le prix au m2 evoluent ensemble (positif) ou en sens inverse (negatif). Proche de 0 = pas de lien lineaire.</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-title">Regression : surface vers prix</div>', unsafe_allow_html=True)
            prix_list = df_dvf["prix"].dropna().tolist()
            surf_list = df_dvf["surface"].dropna().tolist()
            n_min2 = min(len(prix_list), len(surf_list))
            if n_min2 >= 10:
                alpha, beta = least_squares_fit(surf_list[:n_min2], prix_list[:n_min2])
                r2 = r_squared(alpha, beta, surf_list[:n_min2], prix_list[:n_min2])
                _r2_qual = "excellent" if r2 > 0.8 else "correct" if r2 > 0.5 else "faible"
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom:1rem">
                  <div class="kpi-label">Modele de regression lineaire</div>
                  <div class="kpi-value" style="font-size:1.1rem">Prix = {alpha:,.0f} EUR + {beta:,.0f} EUR/m2 x Surface</div>
                  <div class="kpi-sub">R2 = {r2:.3f} — ajustement {_r2_qual}</div>
                  <div class="kpi-desc">Le R2 mesure la qualite du modele (0 a 1). Alpha est le prix de base, beta le cout par m2 supplementaire. Plus le R2 est proche de 1, mieux le modele predit les prix reels.</div>
                </div>""", unsafe_allow_html=True)

                xs_plot = sorted(surf_list[:n_min2])
                ys_pred = [predict(alpha, beta, x) for x in xs_plot]
                fig_reg = go.Figure()
                fig_reg.add_trace(go.Scatter(
                    x=surf_list[:n_min2], y=prix_list[:n_min2],
                    mode="markers",
                    marker=dict(color=BLUE, opacity=0.35, size=4), name="Transactions"))
                fig_reg.add_trace(go.Scatter(
                    x=xs_plot, y=ys_pred, mode="lines",
                    line=dict(color="#dc2626", width=2.5),
                    name=f"Regression (beta={beta:,.0f} EUR/m2)"))
                fig_reg.update_layout(
                    **PLOTLY_LAYOUT, height=370,
                    xaxis_title="Surface (m2)", yaxis_title="Prix (EUR)",
                    xaxis=dict(gridcolor=_grid),
                    yaxis=dict(gridcolor=_grid))
                st.plotly_chart(fig_reg, width="stretch")

                st.markdown('<div class="section-title">Simulateur de prix</div>', unsafe_allow_html=True)
                st.markdown("<p style='color:var(--nd-text-muted);font-size:0.85rem'>Estimez le prix d'un bien en fonction de sa surface, a partir du modele de regression.</p>", unsafe_allow_html=True)
                sim_surf = st.slider("Surface (m2)", 20, 200, 65)
                sim_prix = predict(alpha, beta, sim_surf)
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">Estimation pour {sim_surf} m2</div>
                  <div class="kpi-value">{sim_prix:,.0f} EUR</div>
                  <div class="kpi-sub">{sim_prix/sim_surf:,.0f} EUR/m2</div>
                  <div class="kpi-desc">Prix estime par le modele de regression lineaire. A comparer avec les prix reels du quartier pour identifier les opportunites.</div>
                </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="footer">
  NidDouillet — Observatoire Immobilier Toulonnais — Donnees DVF data.gouv.fr<br>
  Mamoune NIDAM — Jimmy RIBEIRO — Lamiae ZRIOUALI — Matthias CARO-BECKER — Inde HADAOUI<br>
  {datetime.now().strftime("%d/%m/%Y")}
</div>
""", unsafe_allow_html=True)
