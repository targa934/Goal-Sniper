import streamlit as st
import requests
import json
import os
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs & Passeurs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

FAV_FILE = "user_favorites.json"

def load_stored_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_stored_favorites(favs):
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f:
            json.dump(favs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "favorites" not in st.session_state:
    st.session_state.favorites = load_stored_favorites()

if "profile_name" not in st.session_state:
    st.session_state.profile_name = "Sniper_Pro"

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;0,900;1,800&family=JetBrains+Mono:wght@500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, #151c2e 0%, #0a0d14 70%, #06080d 100%);
    color: #F0F4F8;
}

.header-hero {
    background: linear-gradient(135deg, rgba(20, 28, 48, 0.8) 0%, rgba(10, 14, 24, 0.9) 100%);
    border: 1px solid rgba(0, 230, 118, 0.25);
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 22px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(10px);
}
.header-hero h1 {
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: -0.5px;
    margin: 0;
    background: linear-gradient(90deg, #FFFFFF 0%, #00E676 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header-hero p {
    color: #94A3B8;
    margin-top: 5px;
    font-size: 0.92rem;
}

/* Carte Joueur Type EA Sports FC */
.player-card-box {
    background: linear-gradient(145deg, #131b2e 0%, #0e1422 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 16px;
    position: relative;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
    transition: all 0.25s ease-in-out;
}
.player-card-box:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 230, 118, 0.5);
    box-shadow: 0 12px 28px rgba(0, 230, 118, 0.12);
}
.player-card-box.rank-top {
    border-top: 3px solid #FFD700;
}

.rank-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
    color: #000;
    font-weight: 900;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 8px;
    display: inline-block;
}

.player-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.2;
    margin-top: 4px;
}

.player-sub {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 4px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 10px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.stat-box {
    background: rgba(15, 23, 42,
