import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

LEAGUES = {
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Liga Portugal": "por.1",
    "Eredivisie (Pays-Bas)": "ned.1",
    "Ligue des Champions": "uefa.champions",
    "Ligue Europa": "uefa.europa",
    "Ligue des Nations (UEFA)": "uefa.nations",
    "Brésil (Brasileirão)": "bra.1",
    "Japon (J1 League)": "jpn.1",
    "Chine (Super League)": "chn.1",
    "MLS (États-Unis)": "usa.1"
}

# ---------------------------------------------------------------------------
# APPEL API ESPN (CALENDRIER ET SCORES)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_espn_matches(league_code, date_param):
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
            home_id, away_id = "", ""
            home_score, away_score = "", ""

            for c in competitors:
                team_data = c.get("team", {})
                if c.get("homeAway") == "home":
                    home_team = team_data.get("displayName", "")
                    home_id = team_data.get("id", "")
                    home_score = c.get("score", "")
                else:
                    away_team = team_data.get("displayName", "")
                    away_id = team_data.get("id", "")
                    away_score = c.get("score", "")

            raw_date = ev.get("date", "")
            time_str = raw_date[11:16] if len(raw_date) >= 16 else "N/D"
            status_text = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            score_display = f"({home_score} - {away_score})" if (home_score and away_score) else ""

            matches.append({
                "id": ev.get("id"),
                "home": home_team,
                "home_id": home_id,
                "away": away_team,
                "away_id": away_id,
                "time": time_str,
                "status": status_text,
                "score": score_display,
                "date": raw_date[:10]
            })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_team_athletes(team_id):
    """Récupère l'effectif officiel complet et les stats d'un club via ESPN"""
    if not team_id:
        return []
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/teams/{team_id}/roster"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()
        athletes = []
        for ath in data.get("athletes", []):
            pos = ath.get("position", {}).get("abbreviation", "")
            if pos != "G":  # On ignore les gardiens
                athletes.append({
                    "name": ath.get("displayName", ""),
                    "jersey": ath.get("jersey", ""),
                    "pos": pos,
                    "exp": ath.get("experience", {}).get("years", 0)
                })
        return athletes
    except Exception:
        return []

# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------
st.title("🎯 Radar Prédictif Multi-Ligues")
st.caption("Données automatisées : analyse des effectifs et détection sans maintenance manuelle.")

with st.sidebar:
    st.header("⚙️ Compétition")
    selected_league_label = st.selectbox("Ligue / Tournoi", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    selected_date = st.date_input("Date cible", date.today())
    mode_recherche = st.radio("Portée :", ["Semaine complète (+/- 3 jours)", "Jour sélectionné uniquement"])

# Calcul de la plage de dates
if mode_recherche == "Jour sélectionné uniquement":
    date_param = selected_date.strftime("%Y%m%d")
else:
    d_start = (selected_date - timedelta(days=3)).strftime("%Y%m%d")
    d_end = (selected_date + timedelta(days=3)).strftime("%Y%m%d")
    date_param = f"{d_start}-{d_end}"

with st.spinner("Recherche des matchs en cours..."):
    matches = fetch_espn_matches(league_code, date_param)

if not matches:
    st.warning(f"Aucune rencontre trouvée pour {selected_league_label} autour du {selected_date.strftime('%d/%m/%Y')}.")
else:
    match_labels = {}
    for m in matches:
        label = f"[{m['date']} à {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}"
        match_labels[label] = m

    selected_label = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()

    home_name = current_match["home"]
    away_name = current_match["away"]

    st.subheader(f"🏟️ {home_name} vs {away_name}")
    st.caption(f"Date : {current_match['date']} | Coup d'envoi : {current_match['time']} UTC | Statut : {current_match['status']} {current_match['score']}")

    # Chargement dynamique des effectifs
    with st.spinner("Récupération automatique des effectifs des deux équipes..."):
        home_players = fetch_team_athletes(current_match["home_id"])
        away_players = fetch_team_athletes(current_match["away_id"])

    tab_home, tab_away = st.tabs([f"👕 Effectif {home_name}", f"👕 Effectif {away_name}"])

    with tab_home:
        if home_players:
            for p in home_players:
                with st.container(border=True):
                    st.markdown(f"**#{p['jersey']} {p['name']}** — Poste : `{p['pos']}`")
        else:
            st.info("Données d'effectif non disponibles pour cette sélection/équipe.")

    with tab_away:
        if away_players:
            for p in away_players:
                with st.container(border=True):
                    st.markdown(f"**#{p['jersey']} {p['name']}** — Poste : `{p['pos']}`")
        else:
            st.info("Données d'effectif non disponibles pour cette sélection/équipe.")
