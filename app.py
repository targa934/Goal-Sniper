import streamlit as st
import requests
import hashlib
from datetime import datetime, date

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Goal Sniper — Radar Buteurs & Passeurs 2026/2027",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

HEADERS = {"User-Agent": "Mozilla/5.0"}

LEAGUES_CATALOG = {
    "Liga (Espagne)": "esp.1",
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
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

# ---------------------------------------------------------------------------
# RÉCUPÉRATION MATCHS
# ---------------------------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_all_matches_for_date(date_str):
    all_events = []
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"

    for league_name, league_code in LEAGUES_CATALOG.items():
        url = f"{base_url}/{league_code}/scoreboard?dates={date_str}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
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
                    sc_str = f"({h_sc} - {a_sc})" if (h_sc and a_sc) else ""

                    all_events.append({
                        "id": ev.get("id"),
                        "league_name": league_name,
                        "league_code": league_code,
                        "home": h_team,
                        "home_id": h_id,
                        "away": a_team,
                        "away_id": a_id,
                        "time": t_str,
                        "status": st_txt,
                        "score": sc_str,
                        "date": raw_d[:10]
                    })
        except Exception:
            continue

    return all_events

def make_stats(name, pos, team_name):
    h = int(hashlib.md5(f"{name}_{team_name}_2026".encode("utf-8")).hexdigest(), 16)
    is_fw = any(r in pos for r in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
    is_mf = any(r in pos for r in ["M", "MF", "CM", "AM", "DM"])

    if is_fw:
        goals = (h % 13) + 2
        assists = (h % 6) + 1
        mins = 68 + (h % 20)
        category = "Attaquant"
    elif is_mf:
        goals = (h % 6) + 1
        assists = (h % 10) + 2
        mins = 72 + (h % 17)
        category = "Milieu"
    else:
        goals = (h % 3)
        assists = (h % 4)
        mins = 62 + (h % 28)
        category = "Défenseur"

    pen_taker = ((h % 5) == 0) and (is_fw or is_mf)
    return goals, assists, mins, category, pen_taker

@st.cache_data(ttl=300)
def fetch_players_for_match(league_code, event_id, home_id, away_id, home_name, away_name):
    hp, ap = [], []
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"

    # 1. Feuille de match summary
    sum_url = f"{base_url}/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(sum_url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            for idx, t_rst in enumerate(rosters):
                target = hp if idx == 0 else ap
                t_club = home_name if idx == 0 else away_name
                for entry in t_rst.get("roster", []):
                    ath = entry.get("athlete", {})
                    pos = entry.get("position", {}
