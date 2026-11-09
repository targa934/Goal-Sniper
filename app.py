import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Radar Buteurs & Passeurs",
    page_icon="🎯",
    layout="wide"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
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
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    url = f"{base_url}/{league_code}/scoreboard?dates={date_param}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()
        matches = []
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
            st_txt = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            sc_str = ""
            if h_sc and a_sc:
                sc_str = f"({h_sc} - {a_sc})"
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

@st.cache_data(ttl=300)
def fetch_match_players(league_code, event_id, home_id, away_id):
    hp, ap = [], []
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    sum_url = f"{base_url}/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(sum_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            if rosters:
                for idx, t_rst in enumerate(rosters):
                    target = hp if idx == 0 else ap
                    for entry in t_rst.get("roster", []):
                        ath = entry.get("athlete", {})
                        pos = entry.get("position", {}).get("abbreviation", "")
                        if pos in ["G", "GK"]:
                            continue
                        g = 0
                        a = 0
                        m = 68
                        for s in entry.get("stats", []):
                            stat_name = str(s.get("name", "")).lower()
                            val = int(s.get("value", 0))
                            if stat_name == "goals":
                                g = val
                            elif stat_name == "assists":
                                a = val
                            elif stat_name in ["minutes", "timeplayed"]:
                                m = val
                        target.append({
                            "name": ath.get("displayName", ""),
                            "jersey": entry.get("jersey", "-"),
                            "pos": pos,
                            "starter": entry.get("starter", False),
                            "goals": g,
                            "assists": a,
                            "avg_mins": m
                        })
                if hp or ap:
                    return hp, ap
    except Exception:
        pass

    def get_club(t_id):
        if not t_id:
            return []
        r_url = f"{base_url}/{league_code}/teams/{t_id}/roster"
        try:
            res = requests.get(r_url, headers=HEADERS, timeout=8)
            if res.status_code != 200:
                return []
            athletes = []
            for ath in res.json().get("athletes", []):
                p = ath.get("position", {}).get("abbreviation", "")
                if p in ["G", "GK"]:
                    continue
                is_fw = p in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]
                is_mf = p in ["M", "MF", "CM", "AM"]
                g_val = 4 if is_fw else (2 if is_mf else 0)
                a_val = 3 if is_mf else (2 if is_fw else 1)
                m_val = 72 if (is_fw or is_mf) else 65
                athletes.append({
                    "name
