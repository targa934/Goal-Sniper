import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

LEAGUES = {
    "Ligue des Nations (UEFA)": "uefa.nations",
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Liga Portugal": "por.1",
    "Eredivisie (Pays-Bas)": "ned.1",
    "Ligue des Champions": "uefa.champions",
    "Ligue Europa": "uefa.europa",
    "Brésil (Brasileirão)": "bra.1",
    "Japon (J1 League)": "jpn.1",
    "Chine (Super League)": "chn.1",
    "MLS (États-Unis)": "usa.1"
}

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

@st.cache_data(ttl=300)
def fetch_match_or_team_players(league_code, event_id, home_id, away_id):
    home_players = []
    away_players = []

    summary_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(summary_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            if rosters:
                for idx, team_roster in enumerate(rosters):
                    target_list = home_players if idx == 0 else away_players
                    for entry in team_roster.get("roster", []):
                        ath = entry.get("athlete", {})
                        pos = entry.get("position", {}).get("abbreviation", "")
                        if pos in ["G", "GK"]:
                            continue
                        target_list.append({
                            "name": ath.get("displayName", ""),
                            "jersey": entry.get("jersey", ""),
                            "pos": pos,
                            "starter": entry.get("starter", False)
                        })
                if home_players or away_players:
                    return home_players, away_players
    except Exception:
        pass

    def get_roster(team_id):
        if not team_id:
            return []
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{team_id}/roster"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                athletes = []
                for ath in r.json().get("athletes", []):
                    pos = ath.get("position", {}).get("abbreviation", "")
                    if pos in ["G", "GK"]:
                        continue
                    athletes.append({
                        "name": ath.get("displayName", ""),
                        "jersey": ath.get("jersey", ""),
                        "pos": pos,
                        "starter": False
                    })
                return athletes
        except Exception:
            return []
        return []

    return get_roster(home_id), get_roster(away_id)

st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Détection automatique des forces offensives sur les matchs à venir.")

with st.sidebar:
    st.header("⚙️ Compétition")
    selected_league_label = st.selectbox("Ligue / Tournoi", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    selected_date = st.date_input("Date cible", date.today())
    mode_recherche = st.radio("Portée :", ["Jour sélectionné uniquement", "Semaine complète (+/- 3 jours)"])

def date_to_num(d):
    return d.isoformat().replace("-", "")

if mode_recherche == "Jour sélectionné uniquement":
    date_param = date_to_num(selected_date)
else:
    d1 = selected_date - timedelta(days=3)
    d2 = selected_date + timedelta(days=3)
    date_param = f"{date_to_num(d1)}-{date_to_num(d2)}"

with st.spinner("Recherche des matchs en cours..."):
    matches = fetch_espn_matches(league_code, date_param)

if not matches:
    st.warning(f"Aucune rencontre trouvée pour {selected_league_label} autour de la date choisie.")
else:
    match_labels = {}
    for m in matches:
        label = f"[{m['date']} {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}"
        match_labels[label] = m

    selected_label = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()

    home_name = current_match["home"]
    away_name = current_match["away"]

    st.subheader(f"🏟️ {home_name} vs {away_name}")
    st.caption(f"Date : {current_match['date']} | Coup d'envoi : {current_match['time']} UTC | Statut : {current_match['status']} {current_match['score']}")

    with st.spinner("Analyse des effectifs en cours..."):
        home_players, away_players = fetch_match_or_team_players(
            league_code, current_match["id"], current_match["home_id"], current_match["away_id"]
        )

    for p in home_players:
        p["team"] = home_name
    for p in away_players:
        p["team"] = away_name

    all_field = home_players + away_players

    buteurs_potentiels = []
    passeurs_potentiels = []

    for p in all_field:
        pos = p.get("pos",
