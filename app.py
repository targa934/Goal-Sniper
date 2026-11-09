import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0"}

LEAGUES = {
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Ligue des Champions": "uefa.champions",
    "Ligue des Nations (UEFA)": "uefa.nations",
    "Liga Portugal": "por.1",
    "Eredivisie (Pays-Bas)": "ned.1",
    "Brésil (Brasileirão)": "bra.1",
    "Japon (J1 League)": "jpn.1",
    "Chine (Super League)": "chn.1",
    "MLS (États-Unis)": "usa.1"
}

@st.cache_data(ttl=180)
def fetch_espn_matches(league_code, date_param):
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/scoreboard?dates=" + str(date_param)
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return []
        matches = []
        for ev in r.json().get("events", []):
            comp = ev.get("competitions", [{}])[0]
            comps = comp.get("competitors", [])
            h_team, a_team, h_id, a_id = "Domicile", "Extérieur", "", ""
            h_sc, a_sc = "", ""
            for c in comps:
                tm = c.get("team", {})
                if c.get("homeAway") == "home":
                    h_team = tm.get("displayName", "")
                    h_id = tm.get("id", "")
                    h_sc = c.get("score", "")
                else:
                    a_team = tm.get("displayName", "")
                    a_id = tm.get("id", "")
                    a_sc = c.get("score", "")
            raw_d = ev.get("date", "")
            t_str = raw_d[11:16] if len(raw_d) >= 16 else "N/D"
            st_txt = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            sc_str = ""
            if h_sc and a_sc:
                sc_str = "(" + str(h_sc) + " - " + str(a_sc) + ")"
            matches.append({
                "id": ev.get("id"),
                "home": h_team,
                "home_id": h_id,
                "away": a_team,
                "away_id": a_id,
                "time": t_str,
                "status": st_txt,
                "score": sc_str,
                "date": raw_d[:10]
            })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_league_real_stats(league_code):
    stats_dict = {}
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/statistics"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            categories = r.json().get("stats", {}).get("categories", [])
            for cat in categories:
                c_name = str(cat.get("name", "")).lower()
                is_goal = ("goal" in c_name or "scorer" in c_name)
                is_assist = ("assist" in c_name)
                for leader in cat.get("leaders", []):
                    ath = leader.get("athlete", {})
                    p_name = ath.get("displayName", "").strip().lower()
                    val = int(leader.get("value", 0))
                    if p_name not in stats_dict:
                        stats_
