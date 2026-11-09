import streamlit as st
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="⚽", layout="wide")

# Insérez ici votre clé reçue par email
API_KEY = "3d731125ea3347f4ae83d477b8f536da"

HEADERS = {
    "X-Auth-Token": API_KEY
}

COMPETITIONS = {
    "Ligue 1 (France)": "FL1",
    "Premier League (Angleterre)": "PL",
    "Ligue des Champions": "CL",
    "Liga (Espagne)": "PD",
    "Serie A (Italie)": "SA",
    "Bundesliga (Allemagne)": "BL1"
}

WATCHLIST_SCORERS = {
    "Bradley Barcola": {"team": "Paris Saint-Germain FC", "type": "buteur", "shots": 2.9, "xg": 0.52, "pen": False},
    "Mason Greenwood": {"team": "Olympique de Marseille", "type": "buteur", "shots": 3.7, "xg": 0.55, "pen": True},
    "Erling Haaland": {"team": "Manchester City FC", "type": "buteur", "shots": 4.1, "xg": 0.85, "pen": True},
    "Mohamed Salah": {"team": "Liverpool FC", "type": "buteur", "shots": 3.5, "xg": 0.60, "pen": True},
    "Vinicius Junior": {"team": "Real Madrid CF", "type": "buteur", "shots": 3.2, "xg": 0.50, "pen": False},
    "Harry Kane": {"team": "FC Bayern München", "type": "buteur", "shots": 4.0, "xg": 0.78, "pen": True},
    "Ousmane Dembélé": {"team": "Paris Saint-Germain FC", "type": "passeur", "key_passes": 3.1, "xa": 0.45, "set_piece": True},
    "Kevin De Bruyne": {"team": "Manchester City FC", "type": "passeur", "key_passes": 3.5, "xa": 0.48, "set_piece": True},
    "Bukayo Saka": {"team": "Arsenal FC", "type": "passeur", "key_passes": 2.8, "xa": 0.40, "set_piece": True},
    "Achraf Hakimi": {"team": "Paris Saint-Germain FC", "type": "passeur", "key_passes": 2.2, "xa": 0.28, "set_piece": False}
}

# ---------------------------------------------------------------------------
# APPEL API OFFICIEL
# ---------------------------------------------------------------------------
@st.cache_data(ttl=120)
def fetch_matches(comp_code):
    url = f"https://api.football-data.org/v4/competitions/{comp_code}/matches"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 403:
            st.error("Clé API invalide. Vérifiez la clé copiée depuis votre email.")
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
                "status": m.get("status"),
                "matchday": m.get("matchday"),
                "date": utc_time[:10] if len(utc_time) >= 10 else "N/D",
                "time": utc_time[11:16] if len(utc_time) >= 16 else "N/D"
            })
        return matches
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return []

@st.cache_data(ttl=60)
def fetch_match_details(match_id):
    url = f"https://api.football-data.org/v4/matches/{match_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Automatique : Buteurs & Passeurs")
st.caption("Flux certifié Football-Data.org • Analyse en direct des feuilles de match.")

with st.sidebar:
    st.header("⚙️ Championnat")
    selected_comp = st.selectbox("Ligue", list(COMPETITIONS.keys()))
    comp_code = COMPETITIONS[selected_comp]
    
    st.subheader("Filtrage des rencontres")
    view_type = st.radio("Afficher :", ["Matchs à venir", "Derniers matchs joués"])

matches_raw = fetch_matches(comp_code)

if not matches_raw:
    st.info("Chargement des rencontres en cours...")
else:
    if view_type == "Matchs à venir":
        filtered = [m for m in matches_raw if m["status"] in ["SCHEDULED", "TIMED", "IN_PLAY", "PAUSED"]]
        if not filtered:
            st.info("Aucun match à venir programmé immédiatement dans cette ligue. Consultez les derniers matchs joués.")
            filtered = matches_raw[-15:]
    else:
        filtered = [m for m in matches_raw if m["status"] == "FINISHED"][-15:]

    if filtered:
        match_options = {f"[{m['date']} à {m['time']} UTC] {m['home']} vs {m['away']} ({m['status']})": m for m in filtered}
        choice = st.selectbox("Sélectionnez le match :", list(match_options.keys()))
        selected_match = match_options[choice]

        st.divider()

        with st.spinner("Analyse des compositions..."):
            details = fetch_match_details(selected_match["id"])

        lineup_home = []
        lineup_away = []

        if details:
            lineup_home = details.get("lineup", {}).get("homeTeam", [])
            lineup_away = details.get("lineup", {}).get("awayTeam", [])

        if not lineup_home and not lineup_away:
            st.warning(f"Statut : **{selected_match['status']}**. Les compositions officielles ne sont pas transmises (elles arrivent environ 45 min avant le coup d'envoi).")
        else:
            st.success("✅ Compositions officielles confirmées !")
            all_starters = [p.get("name", "") for p in lineup_home + lineup_away]

            buteurs_detectes = []
            passeurs_detectes = []

            for p_name in all_starters:
                for target_name, stats in WATCHLIST_SCORERS.items():
                    if target_name.lower() in p_name.lower():
                        if stats["type"] == "buteur":
                            score = min(round((stats["shots"] * 1.5) + (stats["xg"] * 8.0) + (1.5 if stats["pen"] else 0), 1), 9.9)
                            buteurs_detectes.append({"name": target_name, "score": score, **stats})
                        elif stats["type"] == "passeur":
                            score = min(round((stats["key_passes"] * 1.5) + (stats["xa"] * 9.0) + (1.0 if stats["set_piece"] else 0), 1), 9.9)
                            passeurs_detectes.append({"name": target_name, "score": score, **stats})

            tab_buteurs, tab_passeurs, tab_lineups = st.tabs(["🎯 Buteurs Détectés", "🅰️ Passeurs Détectés", "📋 Compositions"])

            with tab_buteurs:
                if buteurs_detectes:
                    for b in sorted(buteurs_detectes, key=lambda x: x["score"], reverse=True):
                        with st.container(border=True):
                            st.markdown(f"### ⚽ {b['name']} ({b['team']}) — Note : `{b['score']}/10`")
                            st.write(f"- **Volume :** {b['shots']} tirs/90m | **xG moyen :** {b['xg']}")
                            st.write(f"- **Penalty :** {'Oui (Tireur désigné) 🎯' if b['pen'] else 'Non'}")
                else:
                    st.write("Aucun joueur de la liste buteur prioritaire parmi les titulaires.")

            with tab_passeurs:
                if passeurs_detectes:
                    for p in sorted(passeurs_detectes, key=lambda x: x["score"], reverse=True):
                        with st.container(border=True):
                            st.markdown(f"### 🅰️ {p['name']} ({p['team']}) — Note : `{p['score']}/10`")
                            st.write(f"- **Créativité :** {p['key_passes']} passes clés/90m | **xA moyen :** {p['xa']}")
                            st.write(f"- **Coups de pied arrêtés :** {'Oui (Corners/CF) 🎯' if p['set_piece'] else 'Non'}")
                else:
                    st.write("Aucun profil passeur prioritaire parmi les titulaires.")

            with tab_lineups:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{selected_match['home']}**")
                    for pl in lineup_home:
                        st.text(f"• {pl.get('name')} ({pl.get('position', 'N/D')})")
                with c2:
                    st.markdown(f"**{selected_match['away']}**")
                    for pl in lineup_away:
                        st.text(f"• {pl.get('name')} ({pl.get('position', 'N/D')})")
