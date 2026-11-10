import streamlit as st
import requests

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# GESTION DES ONGLETS VIA SESSION STATE
# ---------------------------------------------------------------------------
if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "top10"

if "api_token" not in st.session_state:
    st.session_state.api_token = st.secrets.get("FOOTBALL_DATA_KEY", "")

# ---------------------------------------------------------------------------
# CSS PREMIUM ÉPURÉ : ZÉRO CADRE, MENU TEXTE AVEC HOVER NÉON
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@700;800&display=swap');

html, body {
    background-color: #090D16 !important;
    background: #090D16 !important;
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #090D16 !important;
    color: #F8FAFC !important;
}

/* Masquage des composants natifs non désirés */
[data-testid="stHeader"], header[data-testid="stHeader"],
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 1220px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
}

/* -------------------------------------------------------------------------
   NAVBAR ZYRON : LOGO + LIENS TEXTUELS PURS SANS CADRE
------------------------------------------------------------------------- */
.brand-shell {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 14px 24px;
    margin-bottom: 16px;
}
.brand-name {
    font-weight: 900;
    font-size: 1.35rem;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
.brand-name span {
    color: #00F0FF;
}
.brand-pill {
    background: rgba(0, 240, 255, 0.12);
    border: 1px solid rgba(0, 240, 255, 0.35);
    color: #00F0FF;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
}

/* Conteneur de navigation textuelle */
div.text-nav-bar div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    justify-content: center !important;
    gap: 20px !important;
    background: transparent !important;
}

/* SUPPRESSION ABSOLUE DE TOUT CADRE OU FOND SUR LE MENU */
div.text-nav-bar button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #8E9BAE !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    padding: 8px 14px !important;
    margin: 0 !important;
    cursor: pointer !important;
    border-radius: 0 !important;
    transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
}

/* EFFET HOVER : TEXTE CYAN ÉCLATANT + ÉLÉVATION FLUIDE */
div.text-nav-bar button:hover {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #00F0FF !important;
    text-shadow: 0 0 12px rgba(0, 240, 255, 0.6) !important;
    transform: translateY(-2px) !important;
}

div.text-nav-bar button:active,
div.text-nav-bar button:focus {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* -------------------------------------------------------------------------
   SÉLECTEURS & LABELS
------------------------------------------------------------------------- */
label, [data-testid="stWidgetLabel"] {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    margin-bottom: 6px !important;
}
div[data-baseweb="select"] > div {
    background: #111726 !important;
    border: 1.5px solid rgba(255, 255, 255, 0.
