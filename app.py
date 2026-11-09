import streamlit as st
import requests
from datetime import datetime, date

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="⚽", layout="wide")

HEADERS_SOFA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.sofascore.com/"
}

# Tournois majeurs sur SofaScore (IDs officiels SofaScore)
TOURNAMENTS = {
    "Ligue 1 (France)": 34,
    "Premier League (Angleterre)": 17,
    "Ligue des Champions": 7,
    "Liga (Espagne)": 8,
    "Serie A (Italie)": 23,
    "Bundesliga (Allemagne)": 35
}

# Profils cibles avec métriques d'appui
WATCHLIST_SCORERS = {
    "Bradley Barcola": {"team": "Paris SG", "type": "buteur", "shots": 2.9, "xg": 0.52, "pen": False},
    "Mason Greenwood": {"team": "Marseille", "type": "buteur", "shots": 3.7, "xg": 0.55, "pen": True},
    "Erling Haaland": {"team": "Manchester City", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    "Mohamed Salah": {"team": "Liverpool", "type": "buteur", "shots": 3.5, "xg": 0.60, "pen": True},
    "Vinicius Junior": {"team": "Real Madrid", "type": "buteur", "shots": 3.2, "xg": 0.50, "pen": False},
    "Harry Kane": {"team": "Bayern München", "type": "buteur", "shots": 4.0, "xg": 0.78, "pen": True},
    "Ousmane Dembélé": {"team": "Paris SG", "type": "passeur", "key_passes": 3.1, "xa": 0.45, "set_piece": True},
    "Kevin De Bruyne": {"team": "Manchester City", "type": "passeur", "key_passes": 3.5, "xa": 0.48, "set_piece": True},
    "Bukayo Saka": {"team": "Arsenal", "type": "passeur", "key_passes": 2.8, "xa": 0.40, "set_piece": True},
    "Achraf Hakimi": {"team": "Paris SG", "type": "passeur", "key_passes": 2.2, "xa": 0.28, "set_piece": False}
}

# ---------------------------------------------------------------------------
# FONCTIONS API SOFASCORE (100% GRATUITES)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=90)
def fetch_sofa_matches(date_str, tournament_id):
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    try:
        r = requests.get(url, headers=HEADERS_SOFA, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        events = data.get("events", [])
        
        matches = []
        for ev in events:
            # Filtre par ligue
            t_id = ev.get("tournament", {}).get("uniqueTournament", {}).get("id")
            if t_id == tournament_id:
                start_ts = ev.get("startTimestamp", 0)
                hour_str = datetime.fromtimestamp(start_ts).strftime("%H:%M") if start_ts else "N/D"
                status_desc = ev.get("status", {}).get("description", "Non commencé")
                matches.append({
                    "id": ev.get("id"),
                    "home": ev.get("homeTeam", {}).get("name"),
                    "away": ev.get("awayTeam", {}).get("name"),
                    "status": status_desc,
                    "time": hour_str
                })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=60)
def fetch_sofa_lineups(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/lineups"
    try:
        r = requests.get(url, headers=HEADERS_SOFA, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        
        # Vérifie si les compos sont sorties
        if data.get("confirmed") is False and not data.get("home", {}).get("players"):
            return None

        def extract_players(team_data):
            starters = []
            for p_obj in team_data.get("players", []):
                # On ne prend que les titulaires (substitute == False)
                if not p_obj.get("substitute", False):
                    p = p_obj.get("player", {})
                    pos = p_obj.get("position", "")
                    if pos != "G":  # On ignore le gardien
                        starters.append({
                            "name": p.get("name", ""),
                            "shirt": p_obj.get("shirtNumber", ""),
                            "pos": pos
                        })
            return starters

        return {
            "confirmed": data.get("confirmed", False),
            "home": extract_players(data.get("home", {})),
            "away": extract_players(data.get("away", {}))
        }
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Automatique : Buteurs & Passeurs")
st.caption("Flux temps réel SofaScore • Feuilles de match et compositions officielles.")

with st.sidebar:
    st.header("⚙️ Filtres")
    selected_comp = st.selectbox("Championnat", list(TOURNAMENTS.keys()))
    t_id = TOURNAMENTS[selected_comp]
    
    selected_date = st.date_input("Date", date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

matches = fetch_sofa_matches(date_str, t_id)

if not matches:
    st.info(f"Aucune rencontre trouvée pour {selected_comp} à la date du {date_str}.")
else:
    match_map = {f"[{m['time']}] {m['home']} vs {m['away']} ({m['status']})": m for m in matches}
    choice = st.selectbox("Sélectionnez le match :", list(match_map.keys()))
    current_match = match_map[choice]

    st.divider()

    with st.spinner("Récupération de la feuille de match..."):
        lineups = fetch_sofa_lineups(current_match["id"])

    if not lineups or (not lineups["home"] and not lineups["away"]):
        st.warning(f"⏳ Statut : **{current_match['status']}**. Les compositions ne sont pas encore officialisées (disponibles ~45-60 min avant le coup d'envoi).")
    else:
        st.success("✅ Compositions officielles confirmées !")
        
        all_field_players = lineups["home"] + lineups["away"]
        all_names = [p["name"] for p in all_field_players]

        detected_buteurs = []
        detected_passeurs = []

        for p_name in all_names:
            for target_name, stats in WATCHLIST_SCORERS.items():
                if target_name.lower() in p_name.lower():
                    if stats["type"] == "buteur":
                        score = min(round((stats["shots"] * 1.5) + (stats["xg"] * 8.0) + (1.5 if stats["pen"] else 0), 1), 9.9)
                        detected_buteurs.append({"name": target_name, "score": score, **stats})
                    elif stats["type"] == "passeur":
                        score = min(round((stats["key_passes"] * 1.5) + (stats["xa"] * 9.0) + (1.0 if stats["set_piece"] else 0), 1), 9.9)
                        detected_passeurs.append({"name": target_name, "score": score, **stats})

        tab_buteurs, tab_passeurs, tab_lineups = st.tabs(["🎯 Buteurs Détectés", "🅰️ Passeurs Détectés", "📋 11 Titulaires"])

        with tab_buteurs:
            if detected_buteurs:
                for b in sorted(detected_buteurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### ⚽ {b['name']} ({b['team']}) — Note : `{b['score']}/10`")
                        st.write(f"- **Volume offensif :** {b['shots']} tirs/90m | **xG moyen :** {b['xg']}")
                        st.write(f"- **Tireur Penalty :** {'Oui 🎯' if b['pen'] else 'Non'}")
            else:
                st.write("Aucun joueur de la liste buteur clé n'est titulaire sur cette rencontre.")

        with tab_passeurs:
            if detected_passeurs:
                for p in sorted(detected_passeurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### 🅰️ {p['name']} ({p['team']}) — Note : `{p['score']}/10`")
                        st.write(f"- **Créativité :** {p['key_passes']} passes clés/90m | **xA moyen :** {p['xa']}")
                        st.write(f"- **Coups de pied arrêtés :** {'Oui (Corners/CF) 🎯' if p['set_piece'] else 'Non'}")
            else:
                st.write("Aucun passeur clé identifié parmi les titulaires.")

        with tab_lineups:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{current_match['home']}**")
                for pl in lineups["home"]:
                    st.text(f"#{pl['shirt']} {pl['name']} ({pl['pos']})")
            with c2:
                st.markdown(f"**{current_match['away']}**")
                for pl in lineups["away"]:
                    st.text(f"#{pl['shirt']} {pl['name']} ({pl['pos']})")
