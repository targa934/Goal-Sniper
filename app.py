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

LEAGUES = {
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Ligue des Champions": "uefa.champions"
}

# ---------------------------------------------------------------------------
# BASE STATISTIQUE JOUEURS & CLUBS (Tirs, xG, xA, Penalties)
# ---------------------------------------------------------------------------
PLAYERS_DATABASE = [
    # Ligue 1
    {"name": "Bradley Barcola", "team": "Paris Saint-Germain", "role": "Ailier", "type": "buteur", "shots": 2.9, "xg": 0.54, "pen": False},
    {"name": "Ousmane Dembélé", "team": "Paris Saint-Germain", "role": "Ailier", "type": "passeur", "key_passes": 3.2, "xa": 0.46, "set_piece": True},
    {"name": "Achraf Hakimi", "team": "Paris Saint-Germain", "role": "Latéral", "type": "passeur", "key_passes": 2.2, "xa": 0.28, "set_piece": False},
    {"name": "Mason Greenwood", "team": "Marseille", "role": "Attaquant", "type": "buteur", "shots": 3.7, "xg": 0.58, "pen": True},
    {"name": "Elye Wahi", "team": "Marseille", "role": "Buteur", "type": "buteur", "shots": 2.5, "xg": 0.44, "pen": False},
    {"name": "Jonathan David", "team": "Lille", "role": "Buteur", "type": "buteur", "shots": 3.1, "xg": 0.59, "pen": True},
    {"name": "Alexandre Lacazette", "team": "Lyon", "role": "Buteur", "type": "buteur", "shots": 2.8, "xg": 0.51, "pen": True},
    {"name": "Rayan Cherki", "team": "Lyon", "role": "Milieu Off", "type": "passeur", "key_passes": 2.9, "xa": 0.39, "set_piece": True},
    {"name": "Wissam Ben Yedder", "team": "Monaco", "role": "Buteur", "type": "buteur", "shots": 2.7, "xg": 0.48, "pen": True},

    # Premier League
    {"name": "Erling Haaland", "team": "Manchester City", "role": "Buteur", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    {"name": "Kevin De Bruyne", "team": "Manchester City", "role": "Milieu Off", "type": "passeur", "key_passes": 3.6, "xa": 0.49, "set_piece": True},
    {"name": "Mohamed Salah", "team": "Liverpool", "role": "Ailier", "type": "buteur", "shots": 3.6, "xg": 0.62, "pen": True},
    {"name": "Cole Palmer", "team": "Chelsea", "role": "Milieu Off", "type": "buteur", "shots": 3.2, "xg": 0.55, "pen": True},
    {"name": "Bukayo Saka", "team": "Arsenal", "role": "Ailier", "type": "passeur", "key_passes": 2.8, "xa": 0.41, "set_piece": True},
    {"name": "Kai Havertz", "team": "Arsenal", "role": "Buteur", "type": "buteur", "shots": 2.7, "xg": 0.48, "pen": False},
    {"name": "Son Heung-min", "team": "Tottenham", "role": "Attaquant", "type": "buteur", "shots": 2.8, "xg": 0.47, "pen": True},

    # La Liga
    {"name": "Kylian Mbappé", "team": "Real Madrid", "role": "Buteur", "type": "buteur", "shots": 4.3, "xg": 0.81, "pen": True},
    {"name": "Vinicius Junior", "team": "Real Madrid", "role": "Ailier", "type": "buteur", "shots": 3.3, "xg": 0.52, "pen": False},
    {"name": "Robert Lewandowski", "team": "Barcelona", "role": "Buteur", "type": "buteur", "shots": 3.8, "xg": 0.73, "pen": True},
    {"name": "Raphinha", "team": "Barcelona", "role": "Ailier", "type": "buteur", "shots": 3.1, "xg": 0.48, "pen": False},
    {"name": "Lamine Yamal", "team": "Barcelona", "role": "Ailier", "type": "passeur", "key_passes": 3.0, "xa": 0.43, "set_piece": True},
    {"name": "Antoine Griezmann", "team": "Atlético Madrid", "role": "Attaquant", "type": "buteur", "shots": 2.6, "xg": 0.45, "pen": True},
    {"name": "Julian Alvarez", "team": "Atlético Madrid", "role": "Attaquant", "type": "buteur", "shots": 2.8, "xg": 0.42, "pen": False},

    # Bundesliga & Serie A
    {"name": "Harry Kane", "team": "Bayern Munich", "role": "Buteur", "type": "buteur", "shots": 4.1, "xg": 0.80, "pen": True},
    {"name": "Florian Wirtz", "team": "Bayer Leverkusen", "role": "Milieu Off", "type": "passeur", "key_passes": 3.1, "xa": 0.45, "set_piece": True},
    {"name": "Lautaro Martínez", "team": "Inter", "role": "Buteur", "type": "buteur", "shots": 3.5, "xg": 0.60, "pen": True}
]

# ---------------------------------------------------------------------------
# APPEL API ESPN (CALENDRIER ILLIMITÉ PAR DATE)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_espn_matches_by_date(league_code, date_str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard?dates={date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        matches = []
        for ev in data.get("events", []):
            comp = ev.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            
            home_team, away_team = "Domicile", "Extérieur"
            home_score, away_score = "", ""
            
            for c in competitors:
                if c.get("homeAway") == "home":
                    home_team = c.get("team", {}).get("displayName", "")
                    home_score = c.get("score", "")
                else:
                    away_team = c.get("team", {}).get("displayName", "")
                    away_score = c.get("score", "")

            raw_date = ev.get("date", "")
            time_str = raw_date[11:16] if len(raw_date) >= 16 else "N/D"
            status_text = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            score_display = f"({home_score} - {away_score})" if home_score and away_score else ""

            matches.append({
                "id": ev.get("id"),
                "home": home_team,
                "away": away_team,
                "time": time_str,
                "status": status_text,
                "score": score_display,
                "date": raw_date[:10]
            })
        return matches
    except Exception:
        return []

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Sélection libre par calendrier • Analyse instantanée passée ou à venir.")

with st.sidebar:
    st.header("⚙️ Filtres de Recherche")
    selected_league_label = st.selectbox("Championnat", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    # Sélecteur de date (Calendrier complet)
    selected_date = st.date_input("Date cible", date.today())
    date_query = selected_date.strftime("%Y%m%d")

    mode_recherche = st.radio("Portée :", ["Jour sélectionné uniquement", "Semaine complète (+/- 3 jours)"])

    st.divider()
    st.subheader("Sensibilité du Radar")
    min_shots = st.slider("Tirs min / 90m (Buteurs)", 1.5, 4.0, 2.3, step=0.1)
    min_xg = st.slider("xG min / 90m (Buteurs)", 0.20, 0.80, 0.35, step=0.05)
    min_xa = st.slider("xA min / 90m (Passeurs)", 0.15, 0.60, 0.25, step=0.05)

# Récupération des matchs
if mode_recherche == "Jour sélectionné uniquement":
    matches = fetch_espn_matches_by_date(league_code, date_query)
else:
    matches = []
    # Interroge de J-3 à J+3
    for offset in range(-3, 4):
        d_str = (selected_date + timedelta(days=offset)).strftime("%Y%m%d")
        matches.extend(fetch_espn_matches_by_date(league_code, d_str))

if not matches:
    st.info(f"Aucune rencontre trouvée pour {selected_league_label} autour du {selected_date.strftime('%d/%m/%Y')}.")
else:
    match_labels = {
        f"[{m['date']} à {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}
