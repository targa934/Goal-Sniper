import streamlit as st
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="⚽", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Codes de ligues sur l'API publique ESPN (100% ouverte et gratuite, avec compos réelles)
LEAGUES_ESPN = {
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
    "Serie A (Italie)": "ita.1",
    "Bundesliga (Allemagne)": "ger.1",
    "Ligue des Champions": "uefa.champions"
}

# Base statistique des joueurs clés
WATCHLIST_SCORERS = {
    "Bradley Barcola": {"team": "Paris Saint-Germain", "type": "buteur", "shots": 2.9, "xg": 0.52, "pen": False},
    "Mason Greenwood": {"team": "Marseille", "type": "buteur", "shots": 3.7, "xg": 0.55, "pen": True},
    "Erling Haaland": {"team": "Manchester City", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    "Mohamed Salah": {"team": "Liverpool", "type": "buteur", "shots": 3.5, "xg": 0.60, "pen": True},
    "Robert Lewandowski": {"team": "Barcelona", "type": "buteur", "shots": 3.8, "xg": 0.72, "pen": True},
    "Raphinha": {"team": "Barcelona", "type": "buteur", "shots": 3.1, "xg": 0.48, "pen": False},
    "Lamine Yamal": {"team": "Barcelona", "type": "passeur", "key_passes": 2.9, "xa": 0.42, "set_piece": True},
    "Vinicius Junior": {"team": "Real Madrid", "type": "buteur", "shots": 3.2, "xg": 0.50, "pen": False},
    "Kylian Mbappé": {"team": "Real Madrid", "type": "buteur", "shots": 4.2, "xg": 0.80, "pen": True},
    "Antoine Griezmann": {"team": "Atlético Madrid", "type": "buteur", "shots": 2.6, "xg": 0.45, "pen": True},
    "Julian Alvarez": {"team": "Atlético Madrid", "type": "buteur", "shots": 2.8, "xg": 0.40, "pen": False},
    "Ousmane Dembélé": {"team": "Paris Saint-Germain", "type": "passeur", "key_passes": 3.1, "xa": 0.45, "set_piece": True},
    "Kevin De Bruyne": {"team": "Manchester City", "type": "passeur", "key_passes": 3.5, "xa": 0.48, "set_piece": True},
    "Bukayo Saka": {"team": "Arsenal", "type": "passeur", "key_passes": 2.8, "xa": 0.40, "set_piece": True}
}

# ---------------------------------------------------------------------------
# APPEL API ESPN (TOTALEMENT GRATUIT & SANS CLÉ)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=90)
def fetch_espn_matches(league_code, date_str):
    """
    Récupère la liste des matchs pour une date donnée (format YYYYMMDD)
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard?dates={date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        matches = []
        for ev in data.get("events", []):
            comp = ev.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            
            home_team = "Domicile"
            away_team = "Extérieur"
            home_score = ""
            away_score = ""
            
            for c in competitors:
                if c.get("homeAway") == "home":
                    home_team = c.get("team", {}).get("displayName", "")
                    home_score = c.get("score", "")
                else:
                    away_team = c.get("team", {}).get("displayName", "")
                    away_score = c.get("score", "")

            status_text = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            
            matches.append({
                "id": ev.get("id"),
                "name": ev.get("name"),
                "home": home_team,
                "away": away_team,
                "score": f"{home_score} - {away_score}" if home_score and away_score else "",
                "status": status_text,
                "date": ev.get("date", "")[:10]
            })
        return matches
    except Exception:
        return []

@st.cache_data(ttl=60)
def fetch_espn_summary(league_code, event_id):
    """
    Récupère la feuille de match avec les 11 titulaires officiels
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        
        rosters = data.get("rosters", [])
        if not rosters:
            return None

        teams_lineups = {}
        for team_roster in rosters:
            team_name = team_roster.get("team", {}).get("displayName", "Équipe")
            starters = []
            
            for p_entry in team_roster.get("roster", []):
                # starter == True indique qu'il est dans le 11 de départ
                if p_entry.get("starter", False):
                    athlete = p_entry.get("athlete", {})
                    pos = p_entry.get("position", {}).get("abbreviation", "")
                    # On ignore les gardiens de but
                    if pos != "G":
                        starters.append({
                            "name": athlete.get("displayName", ""),
                            "jersey": p_entry.get("jersey", ""),
                            "position": pos
                        })
            teams_lineups[team_name] = starters

        return teams_lineups
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Automatique : Buteurs & Passeurs")
st.caption("Compositions officielles en direct • Détection et scoring des profils clés.")

with st.sidebar:
    st.header("⚙️ Filtres")
    selected_league_label = st.selectbox("Championnat", list(LEAGUES_ESPN.keys()))
    league_code = LEAGUES_ESPN[selected_league_label]

    selected_date = st.date_input("Date du match", datetime.now().date())
    date_query = selected_date.strftime("%Y%m%d")

matches = fetch_espn_matches(league_code, date_query)

if not matches:
    st.info(f"Aucune rencontre trouvée pour {selected_league_label} le {selected_date.strftime('%d/%m/%Y')}.")
else:
    match_labels = {f"{m['home']} vs {m['away']} ({m['status']}) {m['score']}": m for m in matches}
    selected_label = st.selectbox("Sélectionnez la rencontre :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()

    with st.spinner("Analyse de la feuille de match officielle..."):
        lineups_data = fetch_espn_summary(league_code, current_match["id"])

    if not lineups_data:
        st.warning(f"⏳ Statut : **{current_match['status']}**. Les compositions officielles ne sont pas encore transmises (généralement disponibles 45 à 60 minutes avant le coup d'envoi).")
    else:
        st.success("✅ Compositions officielles confirmées !")

        all_starters_names = []
        for team_name, players in lineups_data.items():
            for p in players:
                all_starters_names.append((p["name"], team_name))

        detected_buteurs = []
        detected_passeurs = []

        for p_name, t_name in all_starters_names:
            for target_name, stats in WATCHLIST_SCORERS.items():
                if target_name.lower() in p_name.lower():
                    if stats["type"] == "buteur":
                        score = min(round((stats["shots"] * 1.5) + (stats["xg"] * 8.0) + (1.5 if stats["pen"] else 0), 1), 9.9)
                        detected_buteurs.append({"name": target_name, "club": t_name, "score": score, **stats})
                    elif stats["type"] == "passeur":
                        score = min(round((stats["key_passes"] * 1.5) + (stats["xa"] * 9.0) + (1.0 if stats["set_piece"] else 0), 1), 9.9)
                        detected_passeurs.append({"name": target_name, "club": t_name, "score": score, **stats})

        tab_buteurs, tab_passeurs, tab_compos = st.tabs(["🎯 Buteurs Détectés", "🅰️ Passeurs Détectés", "📋 11 de Départ"])

        with tab_buteurs:
            if detected_buteurs:
                for b in sorted(detected_buteurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### ⚽ {b['name']} ({b['club']}) — Note : `{b['score']}/10`")
                        st.write(f"- **Volume :** {b['shots']} tirs/90m | **xG moyen :** {b['xg']}")
                        st.write(f"- **Tireur Penalty :** {'Oui (Tireur désigné) 🎯' if b['pen'] else 'Non'}")
            else:
                st.write("Aucun joueur de la liste buteur prioritaire n'est présent dans le 11 de départ.")

        with tab_passeurs:
            if detected_passeurs:
                for p in sorted(detected_passeurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### 🅰️ {p['name']} ({p['club']}) — Note : `{p['score']}/10`")
                        st.write(f"- **Créativité :** {p['key_passes']} passes clés/90m | **xA moyen :** {p['xa']}")
                        st.write(f"- **Coups de pied arrêtés :** {'Oui (Corners/CF) 🎯' if p['set_piece'] else 'Non'}")
            else:
                st.write("Aucun profil passeur prioritaire identifié parmi les titulaires.")

        with tab_compos:
            team_names = list(lineups_data.keys())
            if len(team_names) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{team_names[0]}**")
                    for pl in lineups_data[team_names[0]]:
                        st.text(f"#{pl['jersey']} {pl['name']} ({pl['position']})")
                with c2:
                    st.markdown(f"**{team_names[1]}**")
                    for pl in lineups_data[team_names[1]]:
                        st.text(f"#{pl['jersey']} {pl['name']} ({pl['position']})")
