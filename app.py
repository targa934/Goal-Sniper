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
            h_team, a_team, h_id, a_id = "Domicile", "Extérieur", "", ""
            h_score, a_score = "", ""
            for c in competitors:
                t = c.get("team", {})
                if c.get("homeAway") == "home":
                    h_team, h_id, h_score = t.get("displayName", ""), t.get("id", ""), c.get("score", "")
                else:
                    a_team, a_id, a_score = t.get("displayName", ""), t.get("id", ""), c.get("score", "")
            raw_d = ev.get("date", "")
            matches.append({
                "id": ev.get("id"),
                "home": h_team, "home_id": h_id,
                "away": a_team, "away_id": a_id,
                "time": raw_d[11:16] if len(raw_d) >= 16 else "N/D",
                "status": comp.get("status", {}).get("type", {}).get("shortDetail", ""),
                "score": f"({h_score} - {a_score})" if (h_score and a_score) else "",
                "date": raw_d[:10]
            })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=300)
def fetch_match_players(league_code, event_id, home_id, away_id):
    home_p, away_p = [], []
    sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(sum_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            if rosters:
                for idx, t_roster in enumerate(rosters):
                    target = home_p if idx == 0 else away_p
                    for entry in t_roster.get("roster", []):
                        ath = entry.get("athlete", {})
                        pos = entry.get("position", {}).get("abbreviation", "")
                        if pos in ["G", "GK"]:
                            continue
                        g, a, m = 0, 0, 68
                        for s in entry.get("stats", []):
                            n = s.get("name",
