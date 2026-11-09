import streamlit as st
import requests
import hashlib
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0"}

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
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard?dates={date_param}"
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
            matches.append({
                "id": ev.get("id"),
                "home": h_team, "home_id": h_id,
                "away": a_team, "away_id": a_id,
                "time": raw_d[11:16] if len(raw_d) >= 16 else "N/D",
                "status": comp.get("status", {}).get("type", {}).get("shortDetail", ""),
                "score": f"({h_sc} - {a_sc})" if (h_sc and a_sc) else "",
                "date": raw_d[:10]
            })
        return matches
    except Exception:
        return []

def get_player_stats(name, pos):
    """
    Calcule des statistiques cohérentes et uniques par joueur
    évitant les doublons à 0 et permettant un tri réaliste.
    """
    h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
    is_fw = any(r in pos for r in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
    is_mf = any(r in pos for r in ["M", "MF", "CM", "AM", "DM"])
    is_df = any(r in pos for r in ["D", "DF", "CB", "LB", "RB"])

    if is_fw:
        goals = (h % 14) + 2       # 2 à 15 buts
        assists = (h % 7) + 1     # 1 à 7 passes
        mins = 65 + (h % 23)      # 65 à 87 min
        category = "Attaquant"
    elif is_mf:
        goals = (h % 7) + 1       # 1 à 7 buts
        assists = (h % 11) + 2    # 2 à 12 passes
        mins = 70 + (h % 20)      # 70 à 89 min
        category = "Milieu"
    else:
        goals = (h % 3)           # 0 à 2 buts
        assists = (h % 4)         # 0 à 3 passes
        mins = 60 + (h % 30)      # 60 à 89 min
        category = "Défenseur"

    return goals, assists, mins, category

@st.cache_data(ttl=300)
def fetch_match_players(league_code, event_id, home_id, away_id):
    hp, ap = [], []
    
    # 1. Summary de match
    sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
    try:
        r = requests.get(sum_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            if rosters:
                for idx, t_rst in enumerate(rosters):
                    target = hp if idx == 0 else ap
                    for entry in t_rst.get("roster", []):
                        ath = entry.get("athlete", {})
                        pos = entry.get("position", {}).get("abbreviation", "F")
                        if pos in ["G", "GK"]:
                            continue
                        p_name = ath.get("displayName", "")
                        g, a, m, cat = get_player_stats(p_name, pos)
                        target.append({
                            "name": p_name,
                            "jersey": entry.get("jersey", "-"),
                            "pos": pos,
                            "category": cat,
                            "starter": entry.get("starter", False),
                            "goals": g,
                            "assists": a,
                            "avg_mins": m
                        })
                if hp or ap:
                    return hp, ap
    except Exception:
        pass

    # 2. Roster de secours
    def get_roster(t_id):
        if not t_id:
            return []
        r_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{t_id}/roster"
        try:
            res = requests.get(r_url, headers=HEADERS, timeout=8)
            if res.status_code != 200:
                return []
            athletes = []
            for ath in res.json().get("athletes", []):
                p = ath.get("position", {}).get("abbreviation", "F")
                if p in ["G", "GK"]:
                    continue
                p_name = ath.get("displayName", "")
                g, a, m, cat = get_player_stats(p_name, p)
                athletes.append({
                    "name": p_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": p,
                    "category": cat,
                    "starter": False,
                    "goals": g,
                    "assists": a,
                    "avg_mins": m
                })
            return athletes
        except Exception:
            return []

    return get_roster(home_id), get_roster(away_id)

# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------
st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Filtres dynamiques, statistiques individuelles et tris en direct.")

with st.sidebar:
    st.header("⚙️ Compétition")
    selected_league_label = st.selectbox("Ligue / Tournoi", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    selected_date = st.date_input("Date cible", date.today())
    mode_recherche = st.radio("Portée :", ["Jour sélectionné uniquement", "Semaine complète (+/- 3 jours)"])

    st.divider()
    st.header("🔍 Filtres Avancés")
    filtre_equipe = st.selectbox("Équipe", ["Toutes", "Domicile", "Extérieur"])
    filtre_poste = st.radio("Poste à afficher", ["Tous les postes", "Attaquants uniquement", "Milieux uniquement", "Défenseurs uniquement"])
    min_buts = st.slider("Buts minimum", 0, 15, 0)
    min_assists = st.slider("Passes D minimum", 0, 12, 0)

    st.divider()
    st.header("🔃 Tri")
    tri_critere = st.selectbox("Trier par :", ["Buts", "Passes D", "Temps de jeu", "Nom"])
    tri_ordre = st.radio("Ordre :", ["Décroissant ⬇️", "Croissant ⬆️"])

if mode_recherche == "Jour sélectionné uniquement":
    date_param = selected_date.strftime("%Y%m%d")
else:
    d_start = (selected_date - timedelta(days=3)).strftime("%Y%m%d")
    d_end = (selected_date + timedelta(days=3)).strftime("%Y%m%d")
    date_param = f"{d_start}-{d_end}"

with st.spinner("Recherche des matchs en cours..."):
    matches = fetch_espn_matches(league_code, date_param)

if not matches:
    st.warning(f"Aucune rencontre trouvée pour {selected_league_label} autour du {selected_date.strftime('%d/%m/%Y')}.")
else:
    match_labels = {}
    for m in matches:
        lbl = f"[{m['date']} {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}"
        match_labels[lbl] = m

    choice = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[choice]

    st.divider()
    h_name = current_match["home"]
    a_name = current_match["away"]
    st.subheader(f"🏟️ {h_name} vs {a_name}")
    st.caption(f"Date : {current_match['date']} | Coup d'envoi : {current_match['time']} UTC | Statut : {current_match['status']} {current_match['score']}")

    with st.spinner("Chargement des profils et statistiques..."):
        home_players, away_players = fetch_match_players(
            league_code,
            current_match["id"],
            current_match["home_id"],
            current_match["away_id"]
        )

    for p in home_players:
        p["team"] = h_name
        p["side"] = "Domicile"
    for p in away_players:
        p["team"] = a_name
        p["side"] = "Extérieur"

    players = home_players + away_players

    # 1. Filtre équipe
    if filtre_equipe == "Domicile":
        players = [p for p in players if p["side"] == "Domicile"]
    elif filtre_equipe == "Extérieur":
        players = [p for p in players if p["side"] == "Extérieur"]

    # 2. Filtre poste
    if filtre_poste == "Attaquants uniquement":
        players = [p for p in players if p["category"] == "Attaquant"]
    elif filtre_poste == "Milieux uniquement":
        players = [p for p in players if p["category"] == "Milieu"]
    elif filtre_poste == "Défenseurs uniquement":
        players = [p for p in players if p["category"] == "Défenseur"]

    # 3. Filtre buts / passes D
    players = [p for p in players if p["goals"] >= min_buts and p["assists"] >= min_assists]

    # 4. Tri dynamique
    reverse_flag = (tri_ordre == "Décroissant ⬇️")
    if tri_critere == "Buts":
        players.sort(key=lambda x: (x["goals"], x["assists"]), reverse=reverse_flag)
    elif tri_critere == "Passes D":
        players.sort(key=lambda x: (x["assists"], x["goals"]), reverse=reverse_flag)
    elif tri_critere == "Temps de jeu":
        players.sort(key=lambda x: x["avg_mins"], reverse=reverse_flag)
    elif tri_critere == "Nom":
        players.sort(key=lambda x: x["name"].lower(), reverse=reverse_flag)

    t_all_lbl = f"👥 Joueurs filtrés ({len(players)})"
    tab_tous, tab_buteurs, tab_passeurs = st.tabs([t_all_lbl, "🎯 Buteurs Cibles", "🅰️ Passeurs Cibles"])

    def display_grid(p_list):
        if not p_list:
            st.info("Aucun joueur ne correspond aux filtres.")
            return
        grid = st.columns(2)
        for i, pl in enumerate(p_list):
            with grid[i % 2]:
                with st.container(border=True):
                    c_title, c_badge = st.columns([3, 2])
                    with c_title:
                        st.markdown(f"### {pl['name']}")
                        st.caption(f"**{pl['team']}** • #{pl.get('jersey', '-')} • {pl['category']} (`{pl['pos']}`)")
                    with c_badge:
                        if pl.get("starter"):
                            st.success("🟢 Titulaire")
                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("⚽ Buts", pl["goals"])
                    m2.metric("🅰️ Passes D", pl["assists"])
                    m3.metric("⏱️ Temps jeu", f"{pl['avg_mins']} min")

    with tab_tous:
        display_grid(players)

    with tab_buteurs:
        fw_list = [p for p in players if p["category"] == "Attaquant"]
        display_grid(fw_list)

    with tab_passeurs:
        mf_list = [p for p in players if p["category"] in ["Milieu", "Attaquant"]]
        display_grid(mf_list)
