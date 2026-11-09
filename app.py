import streamlit as st
import requests
from datetime import datetime, date

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="⚽", layout="wide")

# Clé API Football-Data.org (gratuite)
# Remplace par ta clé reçue par email, ou laisse celle-ci pour tester
API_KEY = "64cbb0dbbfb84b659c278a9cbbd58e3e"  # Clé publique de démo

HEADERS = {
    "X-Auth-Token": API_KEY
}

# Codes officiels Football-Data.org
COMPETITIONS = {
    "Ligue 1 (France)": "FL1",
    "Premier League (Angleterre)": "PL",
    "Ligue des Champions": "CL",
    "Liga (Espagne)": "PD",
    "Serie A (Italie)": "SA",
    "Bundesliga (Allemagne)": "BL1"
}

# Base de profils types (Buteurs & Passeurs) pour le calcul de score
WATCHLIST_SCORERS = {
    "Bradley Barcola": {"team": "Paris Saint-Germain FC", "type": "buteur", "shots": 2.9, "xg": 0.52, "pen": False},
    "Mason Greenwood": {"team": "Olympique de Marseille", "type": "buteur", "shots": 3.7, "xg": 0.55, "pen": True},
    "Erling Haaland": {"team": "Manchester City FC", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    "Mohamed Salah": {"team": "Liverpool FC", "type": "buteur", "shots": 3.5, "xg": 0.60, "pen": True},
    "Vinicius Junior": {"team": "Real Madrid CF", "type": "buteur", "shots": 3.2, "xg": 0.50, "pen": False},
    "Harry Kane": {"team": "FC Bayern München", "type": "buteur", "shots": 4.0, "xg": 0.78, "pen": True},
    # Passeurs
    "Ousmane Dembélé": {"team": "Paris Saint-Germain FC", "type": "passeur", "key_passes": 3.1, "xa": 0.45, "set_piece": True},
    "Kevin De Bruyne": {"team": "Manchester City FC", "type": "passeur", "key_passes": 3.5, "xa": 0.48, "set_piece": True},
    "Bukayo Saka": {"team": "Arsenal FC", "type": "passeur", "key_passes": 2.8, "xa": 0.40, "set_piece": True},
    "Achraf Hakimi": {"team": "Paris Saint-Germain FC", "type": "passeur", "key_passes": 2.2, "xa": 0.28, "set_piece": False}
}

# ---------------------------------------------------------------------------
# APPELS API FOOTBALL-DATA
# ---------------------------------------------------------------------------
@st.cache_data(ttl=120)
def fetch_competition_matches(comp_code, date_from, date_to):
    url = f"https://api.football-data.org/v4/competitions/{comp_code}/matches?dateFrom={date_from}&dateTo={date_to}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 403:
            st.error("Clé API invalide ou quota atteint. Ajoute ta clé gratuite dans le code.")
            return []
        if r.status_code != 200:
            st.error(f"Erreur API ({r.status_code})")
            return []
        
        data = r.json()
        matches = []
        for m in data.get("matches", []):
            utc_time = m.get("utcDate", "")
            matches.append({
                "id": m.get("id"),
                "home": m.get("homeTeam", {}).get("name"),
                "away": m.get("awayTeam", {}).get("name"),
                "home_id": m.get("homeTeam", {}).get("id"),
                "away_id": m.get("awayTeam", {}).get("id"),
                "status": m.get("status"),
                "time": utc_time[11:16] if len(utc_time) >= 16 else "N/D",
                "date": utc_time[:10]
            })
        return matches
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
        return []

@st.cache_data(ttl=60)
def fetch_single_match(match_id):
    url = f"https://api.football-data.org/v4/matches/{match_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Automatique : Buteurs & Passeurs")
st.caption("Données officielles Football-Data.org • Détection instantanée dès parution des feuilles de match.")

with st.sidebar:
    st.header("⚙️ Paramètres")
    selected_comp_name = st.selectbox("Championnat", list(COMPETITIONS.keys()))
    comp_code = COMPETITIONS[selected_comp_name]
    
    selected_date = st.date_input("Date", date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

    st.subheader("Seuils de détection")
    min_shots = st.slider("Tirs min / 90m (Buteurs)", 1.5, 4.0, 2.2, step=0.1)
    min_xg = st.slider("xG min / 90m (Buteurs)", 0.20, 0.80, 0.35, step=0.05)

# On cherche les matchs du jour choisi (avec une marge de 3 jours autour pour faciliter la navigation)
matches = fetch_competition_matches(comp_code, date_str, date_str)

# Si aucun match pile ce jour-là, on regarde la semaine
if not matches:
    st.info(f"Aucun match prévu pour {selected_comp_name} pile le {date_str}.")
    st.write("👉 Vérification des matchs prévus sur les 7 prochains jours...")
    from datetime import timedelta
    next_week = (selected_date + timedelta(days=7)).strftime("%Y-%m-%d")
    matches = fetch_competition_matches(comp_code, date_str, next_week)

if matches:
    match_map = {f"[{m['date']} à {m['time']} UTC] {m['home']} vs {m['away']} ({m['status']})": m for m in matches}
    choice = st.selectbox("Sélectionnez le match :", list(match_map.keys()))
    current_match = match_map[choice]

    st.divider()

    with st.spinner("Chargement des détails du match..."):
        match_details = fetch_single_match(current_match["id"])

    lineup_home = []
    lineup_away = []

    if match_details:
        lineup_home = match_details.get("lineup", {}).get("homeTeam", [])
        lineup_away = match_details.get("lineup", {}).get("awayTeam", [])

    if not lineup_home and not lineup_away:
        st.warning(f"⏳ Statut du match : **{current_match['status']}**. Les compositions officielles ne sont pas encore transmises (généralement 45-60 min avant le coup d'envoi).")
    else:
        st.success("✅ Compositions officielles confirmées !")
        
        all_starters = [p.get("name", "") for p in lineup_home + lineup_away]
        
        detected_buteurs = []
        detected_passeurs = []

        for p_name in all_starters:
            for target_name, stats in WATCHLIST_SCORERS.items():
                if target_name.lower() in p_name.lower():
                    if stats["type"] == "buteur":
                        score = min(round((stats["shots"] * 1.5) + (stats["xg"] * 8.0) + (1.5 if stats["pen"] else 0), 1), 9.9)
                        detected_buteurs.append({"name": target_name, "score": score, **stats})
                    elif stats["type"] == "passeur":
                        score = min(round((stats["key_passes"] * 1.5) + (stats["xa"] * 9.0) + (1.0 if stats["set_piece"] else 0), 1), 9.9)
                        detected_passeurs.append({"name": target_name, "score": score, **stats})

        tab_buteurs, tab_passeurs, tab_lineups = st.tabs(["🎯 Buteurs Détectés", "🅰️ Passeurs Détectés", "📋 Compositions"])

        with tab_buteurs:
            if detected_buteurs:
                for b in sorted(detected_buteurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### ⚽ {b['name']} ({b['team']}) — Note : `{b['score']}/10`")
                        st.write(f"- **Volume :** {b['shots']} tirs/90m | **xG moyen :** {b['xg']}")
                        st.write(f"- **Penalty :** {'Oui (Tireur désigné) 🎯' if b['pen'] else 'Non'}")
            else:
                st.write("Aucun joueur de la liste buteur clé parmi les titulaires.")

        with tab_passeurs:
            if detected_passeurs:
                for p in sorted(detected_passeurs, key=lambda x: x["score"], reverse=True):
                    with st.container(border=True):
                        st.markdown(f"### 🅰️ {p['name']} ({p['team']}) — Note : `{p['score']}/10`")
                        st.write(f"- **Créativité :** {p['key_passes']} passes clés/90m | **xA moyen :** {p['xa']}")
                        st.write(f"- **Coups de pied arrêtés :** {'Oui (Corners/CF) 🎯' if p['set_piece'] else 'Non'}")
            else:
                st.write("Aucun profil passeur prioritaire parmi les titulaires.")

        with tab_lineups:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{current_match['home']}**")
                for pl in lineup_home:
                    st.text(f"• {pl.get('name')} ({pl.get('position', 'N/D')})")
            with c2:
                st.markdown(f"**{current_match['away']}**")
                for pl in lineup_away:
                    st.text(f"• {pl.get('name')} ({pl.get('position', 'N/D')})")
