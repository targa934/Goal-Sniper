import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Prédictif Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Catalogue étendu de compétitions via ESPN
LEAGUES = {
    # Compétitions Internationales
    "Ligue des Nations (UEFA)": "uefa.nations",
    "Ligue des Champions": "uefa.champions",
    "Ligue Europa": "uefa.europa",
    "Copa Libertadores": "conmebol.libertadores",
    
    # Europe Majeure
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Liga Portugal": "por.1",
    "Eredivisie (Pays-Bas)": "ned.1",

    # Amériques & Asie
    "Brésil (Brasileirão Série A)": "bra.1",
    "Japon (J1 League)": "jpn.1",
    "Chine (Chinese Super League)": "chn.1",
    "MLS (États-Unis)": "usa.1"
}

# ---------------------------------------------------------------------------
# BASE STATISTIQUE JOUEURS MULTI-LIGUES
# ---------------------------------------------------------------------------
PLAYERS_DATABASE = [
    # Ligue 1
    {"name": "Bradley Barcola", "team": "Paris Saint-Germain", "role": "Ailier", "type": "buteur", "shots": 2.9, "xg": 0.54, "pen": False},
    {"name": "Ousmane Dembélé", "team": "Paris Saint-Germain", "role": "Ailier", "type": "passeur", "key_passes": 3.2, "xa": 0.46, "set_piece": True},
    {"name": "Achraf Hakimi", "team": "Paris Saint-Germain", "role": "Latéral", "type": "passeur", "key_passes": 2.2, "xa": 0.28, "set_piece": False},
    {"name": "Mason Greenwood", "team": "Marseille", "role": "Attaquant", "type": "buteur", "shots": 3.7, "xg": 0.58, "pen": True},
    {"name": "Jonathan David", "team": "Lille", "role": "Buteur", "type": "buteur", "shots": 3.1, "xg": 0.59, "pen": True},
    {"name": "Alexandre Lacazette", "team": "Lyon", "role": "Buteur", "type": "buteur", "shots": 2.8, "xg": 0.51, "pen": True},
    {"name": "Rayan Cherki", "team": "Lyon", "role": "Milieu Off", "type": "passeur", "key_passes": 2.9, "xa": 0.39, "set_piece": True},

    # Premier League
    {"name": "Erling Haaland", "team": "Manchester City", "role": "Buteur", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    {"name": "Kevin De Bruyne", "team": "Manchester City", "role": "Milieu Off", "type": "passeur", "key_passes": 3.6, "xa": 0.49, "set_piece": True},
    {"name": "Mohamed Salah", "team": "Liverpool", "role": "Ailier", "type": "buteur", "shots": 3.6, "xg": 0.62, "pen": True},
    {"name": "Cole Palmer", "team": "Chelsea", "role": "Milieu Off", "type": "buteur", "shots": 3.2, "xg": 0.55, "pen": True},
    {"name": "Bukayo Saka", "team": "Arsenal", "role": "Ailier", "type": "passeur", "key_passes": 2.8, "xa": 0.41, "set_piece": True},

    # La Liga
    {"name": "Kylian Mbappé", "team": "Real Madrid", "role": "Buteur", "type": "buteur", "shots": 4.3, "xg": 0.81, "pen": True},
    {"name": "Vinicius Junior", "team": "Real Madrid", "role": "Ailier", "type": "buteur", "shots": 3.3, "xg": 0.52, "pen": False},
    {"name": "Robert Lewandowski", "team": "Barcelona", "role": "Buteur", "type": "buteur", "shots": 3.8, "xg": 0.73, "pen": True},
    {"name": "Raphinha", "team": "Barcelona", "role": "Ailier", "type": "buteur", "shots": 3.1, "xg": 0.48, "pen": False},
    {"name": "Lamine Yamal", "team": "Barcelona", "role": "Ailier", "type": "passeur", "key_passes": 3.0, "xa": 0.43, "set_piece": True},
    {"name": "Antoine Griezmann", "team": "Atlético Madrid", "role": "Attaquant", "type": "buteur", "shots": 2.6, "xg": 0.45, "pen": True},

    # Brésil (Brasileirão)
    {"name": "Pedro", "team": "Flamengo", "role": "Buteur", "type": "buteur", "shots": 3.4, "xg": 0.65, "pen": True},
    {"name": "Giorgian de Arrascaeta", "team": "Flamengo", "role": "Milieu Off", "type": "passeur", "key_passes": 3.1, "xa": 0.44, "set_piece": True},
    {"name": "Raphael Veiga", "team": "Palmeiras", "role": "Milieu Off", "type": "buteur", "shots": 2.8, "xg": 0.42, "pen": True},
    {"name": "Yuri Alberto", "team": "Corinthians", "role": "Buteur", "type": "buteur", "shots": 2.9, "xg": 0.51, "pen": False},
    {"name": "Lucas Moura", "team": "Sao Paulo", "role": "Ailier", "type": "buteur", "shots": 2.6, "xg": 0.38, "pen": True},

    # Japon (J-League)
    {"name": "Anderson Lopes", "team": "Yokohama F. Marinos", "role": "Buteur", "type": "buteur", "shots": 3.3, "xg": 0.60, "pen": True},
    {"name": "Leo Ceara", "team": "Cerezo Osaka", "role": "Buteur", "type": "buteur", "shots": 3.1, "xg": 0.55, "pen": True},
    {"name": "Yuya Osako", "team": "Vissel Kobe", "role": "Buteur", "type": "buteur", "shots": 2.8, "xg": 0.48, "pen": True},
    {"name": "Yoshinori Muto", "team": "Vissel Kobe", "role": "Ailier", "type": "passeur", "key_passes": 2.5, "xa": 0.35, "set_piece": False},

    # Chine (Super League)
    {"name": "Wu Lei", "team": "Shanghai Port", "role": "Attaquant", "type": "buteur", "shots": 3.9, "xg": 0.75, "pen": False},
    {"name": "Oscar", "team": "Shanghai Port", "role": "Milieu Off", "type": "passeur", "key_passes": 3.8, "xa": 0.52, "set_piece": True},
    {"name": "Gustavo", "team": "Shanghai Port", "role": "Buteur", "type": "buteur", "shots": 3.2, "xg": 0.62, "pen": True},
    {"name": "Cephas Malele", "team": "Shanghai Shenhua", "role": "Buteur", "type": "buteur", "shots": 3.0, "xg": 0.53, "pen": False},

    # Sélections Nationales (Ligue des Nations)
    {"name": "Kylian Mbappé", "team": "France", "role": "Attaquant", "type": "buteur", "shots
