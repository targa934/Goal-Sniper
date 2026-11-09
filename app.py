import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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

# ---------------------------------------------------------------------------
# APPELS API ESPN
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

@st.cache_data(ttl=300)
def fetch_match_or_team_players(league_code, event_id, home_id, away_id):
    home_players = []
    away_players = []

    # 1. Tente de récupérer la feuille de match officielle (matchs passés ou imminents)
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
                        
                        # Extraction des statistiques de match/saison si présentes
                        stats_list = entry.get("stats", [])
                        goals, assists, mins = 0, 0, 0
                        for s in stats_list:
                            name_s = s.get("name", "").lower()
                            val = s.get("value", 0)
                            if name_s == "goals": goals = int(val)
                            elif name_s == "assists": assists = int(val)
                            elif name_s in ["minutes", "timeplayed"]: mins = int(val)

                        target_list.append({
                            "name": ath.get("displayName", ""),
                            "jersey": entry.get("jersey", ""),
                            "pos": pos,
                            "starter": entry.get("starter", False),
                            "goals": goals,
                            "assists": assists,
                            "avg_mins": mins if mins > 0 else 65
                        })
                if home_players or away_players:
                    return home_players, away_players
    except Exception:
        pass

    # 2. Roster pour matchs à venir
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
                    
                    # Simulation/extraction statistiques moyennes selon expérience et poste
                    exp = ath.get("experience
