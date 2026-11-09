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

LEAGUES = {
    "Ligue 1 (France)": 53,
    "Premier League (Angleterre)": 47,
    "Ligue des Champions": 42,
    "Liga (Espagne)": 87,
    "Serie A (Italie)": 55,
    "Bundesliga (Allemagne)": 54
}

# ---------------------------------------------------------------------------
# EXTRACTION DES DONNÉES FOTMOB
# ---------------------------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_matches(date_str, league_id):
    url = f"https://www.fotmob.com/api/matches?date={date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()
        matches = []
        for lg in data.get("leagues", []):
            if lg.get("primaryId") == league_id or lg.get("id") == league_id:
                for m in lg.get("matches", []):
                    matches.append({
                        "id": m.get("id"),
                        "home": m.get("home", {}).get("name"),
                        "away": m.get("away", {}).get("name"),
                        "time": m.get("status", {}).get("utcTime", "")[11:16],
                        "started": m.get("status", {}).get("started", False)
                    })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=90)
def fetch_match_lineup(match_id):
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
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
                except (ValueError, TypeError):
                    continue

                if "expected_goals_per_90" in title or "xg per 90" in title:
                    xg_p90 = num_val
                elif "shots_per_90" in title or "tirs par 90" in title:
                    shots_p90 = num_val
                elif "expected_assists_per_90" in title or "xa per 90" in title:
                    xa_p90 = num_val
                elif "key_passes" in title:
                    key_passes = num_val
                elif "minutes" in title:
                    minutes = int(num_val)

        if shots_p90 == 0.0 and minutes > 200:
            for group in stats_list:
                items = group.get("stats", {})
                if "goals" in items and "expected_goals" in items:
                    raw_xg = float(items["expected_goals"].get("value", 0))
                    xg_p90 = round(raw_xg / (minutes / 90), 2)
                if "shots" in items:
                    raw_shots = float(items["shots"].get("value", 0))
                    shots_p90 = round(raw_shots / (minutes / 90), 2)

        return {
            "shots_p90": shots_p90,
            "xg_p90": xg_p90,
            "xa_p90": xa_p90,
            "key_passes": key_passes,
            "minutes": minutes
        }
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Automatique : Buteurs & Passeurs")
st.caption("Détection des profils clés dès la parution des compositions officielles.")

with st.sidebar:
    st.header("⚙️ Paramètres")
    selected_date = st.date_input("Date", date.today())
    date_str = selected_date.strftime("%Y%m%d")
    selected_league = st.selectbox("Ligue", list(LEAGUES.keys()))
    league_id = LEAGUES[selected_league]

    st.subheader("Seuils de détection")
    min_shots = st.slider("Tirs min / 90m (Buteurs)", 1.5, 4.0, 2.2, step=0.1)
    min_xg = st.slider("xG min / 90m (Buteurs)", 0.20, 0.80, 0.35, step=0.05)
    min_xa = st.slider("xA min / 90m (Passeurs)", 0.15, 0.60, 0.25, step=0.05)

matches = fetch_matches(date_str, league_id)

if not matches:
    st.info(f"Aucune rencontre répertoriée pour {selected_league} à cette date.")
else:
    match_map = {f"{m['time']} UTC — {m['home']} vs {m['away']}": m for m in matches}
    choice = st.selectbox("Sélectionnez le match :", list(match_map.keys()))
    current_match = match_map[choice]

    st.divider()

    with st.spinner("Vérification des feuilles de match..."):
        lineups = fetch_match_lineup(current_match["id"])

    if not lineups:
        st.warning("⏳ Les compositions officielles ne sont pas encore publiées pour cette rencontre (disponibles ~45-60 min avant le coup d'envoi).")
    else:
        st.success("✅ Compositions officielles confirmées !")
        all_field_players = lineups["home"] + lineups["away"]
        
        with st.spinner(f"Analyse statistique des {len(all_field_players)} titulaires en cours..."):
            detected_buteurs = []
            detected_passeurs = []

            for p in all_field_players:
                p_id = p.get("id")
                if not p_id:
                    continue
                
                stats = fetch_player_season_stats(p_id)
                if not stats:
                    continue

                if stats["shots_p90"] >= min_shots or stats["xg_p90"] >= min_xg:
                    score_buteur = min(round((stats["shots_p90"] * 1.5) + (stats["xg_p90"] * 8.0), 1), 9.9)
                    detected_buteurs.append({
                        "name": p["name"],
                        "team": p["team"],
                        "role": p["role"],
                        "score": score_buteur,
                        **stats
                    })

                if stats["xa_p90"] >= min_xa or stats["key_passes"] >= 1.8:
                    score_passeur = min(round((stats["key_passes"] * 1.5) + (stats["xa_p90"] * 9.0), 1), 9.9)
                    detected_passeurs.append({
                        "name": p["name"],
                        "team": p["team"],
                        "role": p["role"],
                        "score": score_passeur,
                        **stats
                    })

        tab_buteurs, tab_passeurs, tab_lineups = st.tabs(["🎯 Buteurs Détectés", "🅰️ Passeurs Détectés", "📋 Feuilles de match"])

        with tab_buteurs:
            if detected_buteurs:
                for b in sorted(detected_buteurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        col_info, col_metrics = st.columns([2, 3])
                        with col_info:
                            st.markdown(f"### ⚽ {b['name']}")
                            st.caption(f"{b['team']} • {b['role']}")
                            st.metric("Score Potentiel", f"{b['score']} / 10")
                        with col_metrics:
                            st.progress(min(b["shots_p90"] / 5.0, 1.0), text=f"Tirs / 90m : {b['shots_p90']}")
                            st.progress(min(b["xg_p90"] / 1.0, 1.0), text=f"xG / 90m : {b['xg_p90']}")
            else:
                st.write("Aucun joueur de champ n'atteint les seuils offensifs requis.")

        with tab_passeurs:
            if detected_passeurs:
                for p in sorted(detected_passeurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        col_info, col_metrics = st.columns([2, 3])
                        with col_info:
                            st.markdown(f"### 🅰️ {p['name']}")
                            st.caption(f"{p['team']} • {p['role']}")
                            st.metric("Score Potentiel", f"{p['score']} / 10")
                        with col_metrics:
                            st.progress(min(p["key_passes"] / 4.0, 1.0), text=f"Passes clés / 90m : {p['key_passes']}")
                            st.progress(min(p["xa_p90"] / 0.8, 1.0), text=f"xA / 90m : {p['xa_p90']}")
            else:
                st.write("Aucun joueur ne franchit les seuils de création / xA.")

        with tab_lineups:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{lineups['home_team']}**")
                for pl in lineups["home"]:
                    st.text(f"#{pl['shirt']} {pl['name']} ({pl['role']})")
            with c2:
                st.markdown(f"**{lineups['away_team']}**")
                for pl in lineups["away"]:
                    st.text(f"#{pl['shirt']} {pl['name']} ({pl['role']})")
