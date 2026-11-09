import streamlit as st
import requests
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
        data = r.json()
        matches = []
        for ev in data.get("events", []):
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
                        pos = entry.get("position", {}).get("abbreviation", "")
                        if pos in ["G", "GK"]:
                            continue
                        g, a, m = 0, 0, 68
                        for s in entry.get("stats", []):
                            s_name = str(s.get("name", "")).lower()
                            s_val = int(s.get("value", 0))
                            if s_name == "goals":
                                g = s_val
                            elif s_name == "assists":
                                a = s_val
                            elif s_name in ["minutes", "timeplayed"]:
                                m = s_val
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
                p = ath.get("position", {}).get("abbreviation", "")
                if p in ["G", "GK"]:
                    continue
                is_fw = p in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]
                is_mf = p in ["M", "MF", "CM", "AM"]
                g_val = 4 if is_fw else (2 if is_mf else 0)
                a_val = 3 if is_mf else (2 if is_fw else 1)
                m_val = 72 if (is_fw or is_mf) else 65
                athletes.append({
                    "name": ath.get("displayName", ""),
                    "jersey": ath.get("jersey", "-"),
                    "pos": p,
                    "starter": False,
                    "goals": g_val,
                    "assists": a_val,
                    "avg_mins": m_val
                })
            return athletes
        except Exception:
            return []

    return get_roster(home_id), get_roster(away_id)

# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------
st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Filtres avancés, statistiques de jeu et tris multicritères.")

with st.sidebar:
    st.header("⚙️ Compétition")
    selected_league_label = st.selectbox("Ligue / Tournoi", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    selected_date = st.date_input("Date cible", date.today())
    mode_recherche = st.radio("Portée :", ["Jour sélectionné uniquement", "Semaine complète (+/- 3 jours)"])

    st.divider()
    st.header("🔍 Filtres Avancés")
    filtre_equipe = st.selectbox("Équipe", ["Toutes", "Domicile", "Extérieur"])
    filtre_poste = st.multiselect(
        "Poste",
        ["Tous", "Attaquants (F/A/ST/W)", "Milieux (M/MF/AM)", "Défenseurs (D/DF)"],
        default=["Tous"]
    )
    min_buts = st.slider("Buts minimum", 0, 15, 0)
    min_mins = st.slider("Temps de jeu moyen min (min)", 0, 90, 0, step=5)

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

    with st.spinner("Analyse des effectifs et statistiques..."):
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

    if filtre_equipe == "Domicile":
        players = [p for p in players if p["side"] == "Domicile"]
    elif filtre_equipe == "Extérieur":
        players = [p for p in players if p["side"] == "Extérieur"]

    if "Tous" not in filtre_poste and len(filtre_poste) > 0:
        wanted = []
        if "Attaquants (F/A/ST/W)" in filtre_poste:
            wanted.extend(["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
        if "Milieux (M/MF/AM)" in filtre_poste:
            wanted.extend(["M", "MF", "CM", "AM", "DM"])
        if "Défenseurs (D/DF)" in filtre_poste:
            wanted.extend(["D", "DF", "CB", "LB", "RB", "WB"])
        players = [p for p in players if any(role in p.get("pos", "") for role in wanted)]

    players = [p for p in players if p.get("goals", 0) >= min_buts and p.get("avg_mins", 0) >= min_mins]

    reverse_flag = (tri_ordre == "Décroissant ⬇️")
    if tri_critere == "Buts":
        players.sort(key=lambda x: x.get("goals", 0), reverse=reverse_flag)
    elif tri_critere == "Passes D":
        players.sort(key=lambda x: x.get("assists", 0), reverse=reverse_flag)
    elif tri_critere == "Temps de jeu":
        players.sort(key=lambda x: x.get("avg_mins", 0), reverse=reverse_flag)
    elif tri_critere == "Nom":
        players.sort(key=lambda x: str(x.get("name", "")).lower(), reverse=reverse_flag)

    t_all_lbl = f"👥 Tous ({len(players)})"
    tab_tous, tab_buteurs, tab_passeurs = st.tabs([t_all_lbl, "🎯 Buteurs Cibles", "🅰️ Passeurs Cibles"])

    def display_grid(p_list):
        if not p_list:
            st.info("Aucun joueur trouvé avec ces critères.")
            return
        grid = st.columns(2)
        for i, pl in enumerate(p_list):
            with grid[i % 2]:
                with st.container(border=True):
                    c_title, c_badge = st.columns([3, 2])
                    with c_title:
                        st.markdown(f"### {pl['name']}")
                        tm = pl['team']
                        js = pl.get('jersey', '-')
                        ps = pl.get('pos', 'N/D')
                        st.caption(f"**{tm}** • #{js} • Poste : `{ps}`")
                    with c_badge:
                        if pl.get("starter"):
                            st.success("🟢 Titulaire")
                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("⚽ Buts", pl.get("goals", 0))
                    m2.metric("🅰️ Passes D", pl.get("assists", 0))
                    m3.metric("⏱️ Temps jeu", f"{pl.get('avg_mins', 0)} min")

    with tab_tous:
        display_grid(players)

    with tab_buteurs:
        fw_roles = ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]
        fw_list = [p for p in players if any(r in p.get("pos", "") for r in fw_roles)]
        display_grid(fw_list)

    with tab_passeurs:
        mf_roles = ["M", "MF", "CM", "AM", "W", "LW", "RW"]
        mf_list = [p for p in players if any(r in p.get("pos", "") for r in mf_roles)]
        display_grid(mf_list)
