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
# APPEL API ESPN UNIQUE (PLAGE DE DATES DIRECTE)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_espn_matches(league_code, date_param):
    """
    date_param peut être soit une date simple (YYYYMMDD) soit une plage (YYYYMMDD-YYYYMMDD)
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard?dates={date_param}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
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
            score_display = f"({home_score} - {away_score})" if (home_score and away_score) else ""

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

    selected_date = st.date_input("Date cible", date.today())
    mode_recherche = st.radio("Portée :", ["Semaine complète (+/- 3 jours)", "Jour sélectionné uniquement"])

    st.divider()
    st.subheader("Sensibilité du Radar")
    min_shots = st.slider("Tirs min / 90m (Buteurs)", 1.5, 4.0, 2.3, step=0.1)
    min_xg = st.slider("xG min / 90m (Buteurs)", 0.20, 0.80, 0.35, step=0.05)
    min_xa = st.slider("xA min / 90m (Passeurs)", 0.15, 0.60, 0.25, step=0.05)

# Calcul du paramètre dates pour ESPN
if mode_recherche == "Jour sélectionné uniquement":
    date_param = selected_date.strftime("%Y%m%d")
else:
    d_start = (selected_date - timedelta(days=3)).strftime("%Y%m%d")
    d_end = (selected_date + timedelta(days=3)).strftime("%Y%m%d")
    date_param = f"{d_start}-{d_end}"

with st.spinner("Chargement des rencontres..."):
    matches = fetch_espn_matches(league_code, date_param)

if not matches:
    st.warning(f"Aucune rencontre trouvée pour {selected_league_label} sur cette période.")
    st.info("💡 Astuce : Si aucun match n'est programmé ce jour précis, essayez de changer la date ou la ligue.")
else:
    # Construction propre des options du menu déroulant
    match_labels = {}
    for m in matches:
        label = f"[{m['date']} {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}"
        match_labels[label] = m

    selected_label = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()

    home_name = current_match["home"]
    away_name = current_match["away"]

    st.subheader(f"🏟️ Affiche : {home_name} vs {away_name}")
    st.caption(f"Date : {current_match['date']} | Heure : {current_match['time']} UTC | Statut : {current_match['status']} {current_match['score']}")

    def match_team(team_ref, candidate_name):
        return team_ref.lower() in candidate_name.lower() or candidate_name.lower() in team_ref.lower()

    players_match = [p for p in PLAYERS_DATABASE if match_team(p["team"], home_name) or match_team(p["team"], away_name)]

    buteurs = []
    passeurs = []

    for p in players_match:
        if p["type"] == "buteur":
            if p["shots"] >= min_shots or p["xg"] >= min_xg:
                score = min(round((p["shots"] * 1.5) + (p["xg"] * 8.0) + (1.5 if p["pen"] else 0), 1), 9.9)
                buteurs.append({**p, "score": score})
        elif p["type"] == "passeur":
            if p["xa"] >= min_xa or p["key_passes"] >= 2.0:
                score = min(round((p["key_passes"] * 1.5) + (p["xa"] * 9.0) + (1.0 if p["set_piece"] else 0), 1), 9.9)
                passeurs.append({**p, "score": score})

    tab_buteurs, tab_passeurs = st.tabs(["🎯 Buteurs Recommandés", "🅰️ Passeurs Recommandés"])

    with tab_buteurs:
        if buteurs:
            for b in sorted(buteurs, key=lambda x: x["score"], reverse=True):
                with st.container(border=True):
                    col_info, col_metrics = st.columns([2, 3])
                    with col_info:
                        st.markdown(f"### ⚽ {b['name']}")
                        st.write(f"**Club :** {b['team']} ({b['role']})")
                        st.metric("Indice de Confiance", f"{b['score']} / 10")
                    with col_metrics:
                        st.progress(min(b["shots"] / 5.0, 1.0), text=f"Tirs / 90m : {b['shots']}")
                        st.progress(min(b["xg"] / 1.0, 1.0), text=f"xG moyen : {b['xg']}")
                        st.markdown(f"**Tireur de Penalty :** {'Oui 🎯' if b['pen'] else 'Non'}")
        else:
            st.info("Aucun profil de pur buteur répertorié au-dessus des seuils choisis pour cette affiche.")

    with tab_passeurs:
        if passeurs:
            for p in sorted(passeurs, key=lambda x: x["score"], reverse=True):
                with st.container(border=True):
                    col_info, col_metrics = st.columns([2, 3])
                    with col_info:
                        st.markdown(f"### 🅰️ {p['name']}")
                        st.write(f"**Club :** {p['team']} ({p['role']})")
                        st.metric("Indice de Confiance", f"{p['score']} / 10")
                    with col_metrics:
                        st.progress(min(p["key_passes"] / 4.0, 1.0), text=f"Passes clés / 90m : {p['key_passes']}")
                        st.progress(min(p["xa"] / 0.8, 1.0), text=f"xA moyen : {p['xa']}")
                        st.markdown(f"**Coups de pied arrêtés :** {'Oui (Corners / CF) 🎯' if p['set_piece'] else 'Non'}")
        else:
            st.info("Aucun profil passeur répertorié au-dessus des seuils choisis pour ce match.")
