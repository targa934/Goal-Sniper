import streamlit as st
import requests
from datetime import datetime, date

st.set_page_config(
    page_title="Goal Sniper — 2026/2027",
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

@st.cache_data(ttl=180)
def fetch_all_matches_for_date(date_str):
    all_events = []
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"

    for league_name, league_code in LEAGUES_CATALOG.items():
        url = f"{base_url}/{league_code}/scoreboard?dates={date_str}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code != 200:
                continue
            data = r.json()
            for ev in data.get("events", []):
                comp = ev.get("competitions", [{}])[0]
                comps = comp.get("competitors", [])
                h_team, a_team = "Domicile", "Extérieur"
                h_id, a_id = "", ""
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
                status_obj = comp.get("status", {})
                st_type = status_obj.get("type", {})
                st_txt = st_type.get("shortDetail", "")
                sc_str = ""
                if h_sc and a_sc:
                    sc_str = f"({h_sc} - {a_sc})"
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

def make_stats(name, pos):
    val = sum(ord(c) for c in str(name))
    p = str(pos).upper()
    fw_roles = ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]
    mf_roles = ["M", "MF", "CM", "AM", "DM"]
    is_fw = any(r in p for r in fw_roles)
    is_mf = any(r in p for r in mf_roles)

    if is_fw:
        goals = 3 + (val % 12)
        assists = 1 + (val % 6)
        mins = 70 + (val % 18)
        category
