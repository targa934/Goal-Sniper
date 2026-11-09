import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Radar Buteurs & Passeurs", page_icon="🎯", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0"}

LEAGUES = {
    "Ligue 1 (France)": "fra.1",
    "Premier League (Angleterre)": "eng.1",
    "Liga (Espagne)": "esp.1",
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
def fetch_espn_matches(league_code, date_param):
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/scoreboard?dates=" + str(date_param)
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
            t_str = raw_d[11:16] if len(raw_d) >= 16 else "N/D"
            st_txt = comp.get("status", {}).get("type", {}).get("shortDetail", "")
            sc_str = ""
            if h_sc and a_sc:
                sc_str = "(" + str(h_sc) + " - " + str(a_sc) + ")"
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

@st.cache_data(ttl=3600)
def fetch_league_real_stats(league_code):
    stats = {}
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/statistics"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            categories = r.json().get("stats", {}).get("categories", [])
            for cat in categories:
                c_name = str(cat.get("name", "")).lower()
                is_goal = ("goal" in c_name or "scorer" in c_name)
                is_assist = ("assist" in c_name)
                for leader in cat.get("leaders", []):
                    ath = leader.get("athlete", {})
                    p_name = ath.get("displayName", "").strip().lower()
                    val = int(leader.get("value", 0))
                    if p_name not in stats:
                        stats[p_name] = {"goals": 0, "assists": 0}
                    if is_goal:
                        stats[p_name]["goals"] = val
                    elif is_assist:
                        stats[p_name]["assists"] = val
    except Exception:
        pass
    return stats

def get_role_category(pos):
    p = str(pos).upper()
    if any(r in p for r in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]):
        return "Attaquant"
    if any(r in p for r in ["M", "MF", "CM", "AM", "DM"]):
        return "Milieu"
    return "Défenseur"

def get_headshot_url(ath):
    h = ath.get("headshot", {})
    if isinstance(h, dict) and h.get("href"):
        return h.get("href")
    ath_id = str(ath.get("id", ""))
    if ath_id:
        return "https://a.espncdn.com/combiner/i?img=/i/headshots/soccer/players/full/" + ath_id + ".png&w=350&h=254"
    return "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=250&h=180"

@st.cache_data(ttl=300)
def fetch_match_or_team_players(league_code, event_id, home_id, away_id):
    hp = []
    ap = []
    real_stats = fetch_league_real_stats(league_code)

    sum_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/summary?event=" + str(event_id)
    try:
        r = requests.get(sum_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            rosters = r.json().get("rosters", [])
            for idx, t_rst in enumerate(rosters):
                target = hp if idx == 0 else ap
                for entry in t_rst.get("roster", []):
                    ath = entry.get("athlete", {})
                    p_pos = entry.get("position", {})
                    pos = p_pos.get("abbreviation", "") if isinstance(p_pos, dict) else str(p_pos)
                    if pos in ["G", "GK"]:
                        continue
                    p_name = ath.get("displayName", "")
                    clean_name = p_name.strip().lower()

                    g_val = real_stats.get(clean_name, {}).get("goals", 0)
                    a_val = real_stats.get(clean_name, {}).get("assists", 0)

                    target.append({
                        "name": p_name,
                        "jersey": entry.get("jersey", "-"),
                        "pos": pos,
                        "category": get_role_category(pos),
                        "photo": get_headshot_url(ath),
                        "starter": entry.get("starter", False),
                        "goals": g_val,
                        "assists": a_val,
                        "avg_mins": 75 if entry.get("starter") else 30
                    })
            if hp or ap:
                return hp, ap
    except Exception:
        pass

    def get_team_roster(t_id):
        if not t_id:
            return []
        r_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/" + league_code + "/teams/" + str(t_id) + "/roster"
        try:
            res = requests.get(r_url, headers=HEADERS, timeout=8)
            if res.status_code != 200:
                return []
            athletes = []
            for ath in res.json().get("athletes", []):
                p_pos = ath.get("position", {})
                pos = p_pos.get("abbreviation", "") if isinstance(p_pos, dict) else str(p_pos)
                if pos in ["G", "GK"]:
                    continue
                p_name = ath.get("displayName", "")
                clean_name = p_name.strip().lower()

                g_val = real_stats.get(clean_name, {}).get("goals", 0)
                a_val = real_stats.get(clean_name, {}).get("assists", 0)

                athletes.append({
                    "name": p_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": pos,
                    "category": get_role_category(pos),
                    "photo": get_headshot_url(ath),
                    "starter": False,
                    "goals": g_val,
                    "assists": a_val,
                    "avg_mins": 65
                })
            return athletes
        except Exception:
            return []

    return get_team_roster(home_id), get_team_roster(away_id)

st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Données statistiques réelles ESPN et fiches détaillées par joueur.")

st.sidebar.header("⚙️ Compétition")
selected_league_label = st.sidebar.selectbox("Ligue / Tournoi", list(LEAGUES.keys()))
league_code = LEAGUES[selected_league_label]
selected_date = st.sidebar.date_input("Date cible", date.today())
mode_recherche = st.sidebar.radio("Portée :", ["Jour sélectionné uniquement", "Semaine complète (+/- 3 jours)"])

if mode_recherche == "Jour sélectionné uniquement":
    date_param = selected_date.strftime("%Y%m%d")
else:
    d1 = selected_date - timedelta(days=3)
    d2 = selected_date + timedelta(days=3)
    date_param = d1.strftime("%Y%m%d") + "-" + d2.strftime("%Y%m%d")

with st.spinner("Recherche des matchs en cours..."):
    matches = fetch_espn_matches(league_code, date_param)

if not matches:
    st.warning("Aucune rencontre trouvée pour cette période.")
else:
    match_labels = {}
    for m in matches:
        label = "[" + m["date"] + " " + m["time"] + " UTC] " + m["home"] + " vs " + m["away"] + " " + m["score"] + " - " + m["status"]
        match_labels[label] = m

    selected_label = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()
    home_name = current_match["home"]
    away_name = current_match["away"]

    st.subheader("🏟️ " + home_name + " vs " + away_name)
    st.caption("Date : " + current_match["date"] + " | Coup d'envoi : " + current_match["time"] + " UTC | Statut : " + current_match["status"] + " " + current_match["score"])

    with st.spinner("Synchronisation des effectifs et statistiques..."):
        home_players, away_players = fetch_match_or_team_players(
            league_code, current_match["id"], current_match["home_id"], current_match["away_id"]
        )

    for p in home_players:
        p["team"] = home_name
    for p in away_players:
        p["team"] = away_name

    all_field = home_players + away_players

    buteurs = [p for p in all_field if p["category"] == "Attaquant"]
    buteurs.sort(key=lambda x: (x["goals"], x["assists"]), reverse=True)

    passeurs = [p for p in all_field if p["category"] in ["Milieu", "Attaquant"]]
    passeurs.sort(key=lambda x: (x["assists"], x["goals"]), reverse=True)

    tab_buteurs, tab_passeurs, tab_effectifs = st.tabs(["🎯 Buteurs Cibles", "🅰️ Passeurs Cibles", "📋 Effectifs Complets"])

    def render_player_cards(players_to_show):
        if not players_to_show:
            st.info("Aucun joueur répertorié pour cette sélection.")
            return

        cols = st.columns(2)
        placeholder_img = "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=250&h=180"

        for idx, p in enumerate(players_to_show):
            with cols[idx % 2]:
                with st.container(border=True):
                    img_c, info_c = st.columns([1, 2.5])
                    photo_url = p.get("photo") if p.get("photo") else placeholder_img
                    try:
                        img_c.image(photo_url, use_container_width=True)
                    except Exception:
                        img_c.image(placeholder_img, use_container_width=True)

                    badge = " 🟢 Titulaire" if p.get("starter") else ""
                    info_c.markdown("**" + p["name"] + "**" + badge)
                    info_c.caption("Club : **" + p["team"] + "** • #" + str(p.get("jersey", "-")) + " • Poste : `" + str(p.get("pos", "N/D")) + "`")

                    g_cnt = p.get("goals", 0)
                    a_cnt = p.get("assists", 0)
                    m_cnt = str(p.get("avg_mins", 0)) + "m"

                    m1, m2, m3 = info_c.columns(3)
                    m1.metric("⚽ Buts", g_cnt)
                    m2.metric("🅰️ Passes", a_cnt)
                    m3.metric("⏱️ Temps", m_cnt)

    with tab_buteurs:
        st.markdown(f"**Attaquants classés par buts ({len(buteurs)}) :**")
        render_player_cards(buteurs)

    with tab_passeurs:
        st.markdown(f"**Milieux / Créateurs classés par passes ({len(passeurs)}) :**")
        render_player_cards(passeurs)

    with tab_effectifs:
        st.markdown(f"**Tous les joueurs de champ ({len(all_field)}) :**")
        render_player_cards(all_field)
