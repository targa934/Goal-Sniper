import streamlit as st
import requests
from datetime import datetime, date

# ---------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="⚽", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.fotmob.com/",
    "Accept": "application/json"
}

LEAGUES = [
    "Ligue 1 (France)",
    "Premier League (Angleterre)",
    "Ligue des Champions",
    "Liga (Espagne)",
    "Serie A (Italie)",
    "Bundesliga (Allemagne)"
]

# ---------------------------------------------------------------------------
# EXTRACTION DES DONNÉES FOTMOB
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_matches(date_str, league_choice):
    url = f"https://www.fotmob.com/api/matches?date={date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            st.error(f"Erreur API FotMob (code {r.status_code})")
            return []
        
        data = r.json()
        leagues = data.get("leagues", [])
        
        # Mots-clés pour identifier le championnat dans le flux FotMob
        keywords_map = {
            "Ligue 1": ["ligue 1"],
            "Premier League": ["premier league"],
            "Ligue des Champions": ["champions league"],
            "Liga": ["laliga", "la liga", "primera division"],
            "Serie A": ["serie a"],
            "Bundesliga": ["bundesliga"]
        }
        
        target_keys = []
        for key, words in keywords_map.items():
            if key.lower() in league_choice.lower():
                target_keys = words
                break

        matches = []
        for lg in leagues:
            lg_name = lg.get("name", "").lower()
            # Vérifie si le nom de la ligue correspond
            if any(word in lg_name for word in target_keys):
                for m in lg.get("matches", []):
                    time_raw = m.get("status", {}).get("utcTime", "")
                    time_display = time_raw[11:16] if len(time_raw) >= 16 else "Heure N/D"
                    matches.append({
                        "id": m.get("id"),
                        "home": m.get("home", {}).get("name"),
                        "away": m.get("away", {}).get("name"),
                        "time": time_display,
                        "started": m.get("status", {}).get("started", False)
                    })
        return matches
    except Exception as e:
        st.error(f"Erreur de lecture des matchs : {e}")
        return []

@st.cache_data(ttl=90)
def fetch_match_lineup(match_id):
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        content = r.json().get("content", {})
        lineup_block = content.get("lineup", {})
        if not lineup_block or not lineup_block.get("lineup"):
            return None

        teams = lineup_block.get("lineup", [])

        def parse_team_players(team_entry):
            players = []
            for item in team_entry.get("players", []):
                sub_list = item if isinstance(item, list) else [item]
                for p in sub_list:
                    role = p.get("role", "")
                    if role in ["Keeper", "GK"]:
                        continue
                    players.append({
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "shirt": p.get("shirtNumber", ""),
                        "role": role,
                        "team": team_entry.get("teamName", "")
                    })
            return players

        home_name = teams[0].get("teamName", "Domicile") if len(teams) > 0 else "Domicile"
        away_name = teams[1].get("teamName", "Extérieur") if len(teams) > 1 else "Extérieur"

        return {
            "home_team": home_name,
            "away_team": away_name,
            "home": parse_team_players(teams[0]) if len(teams) > 0 else [],
            "away": parse_team_players(teams[1]) if len(teams) > 1 else []
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_player_season_stats(player_id):
    url = f"https://www.fotmob.com/api/playerData?id={player_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code != 200:
            return None
        data = r.json()
        
        stats_section = data.get("statSeasons", [])
        if not stats_section:
            return None

        latest_season = stats_section[0]
        stats_list = latest_season.get("stats", {})

        shots_p90 = 0.0
        xg_p90 = 0.0
        xa_p90 = 0.0
        key_passes = 0.0
        minutes = 0

        for group in stats_list:
            items = group.get("stats", {})
            for key, val_obj in items.items():
                title = val_obj.get("key", "").lower()
                val = val_obj.get("value", 0)
                try:
                    num_val = float(val)
