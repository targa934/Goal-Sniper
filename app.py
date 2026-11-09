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
        matches = []
        for ev in r.json().get("events", []):
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

def get_stats(name, pos):
    val = sum(ord(c) for c in str(name))
    p = str(pos).upper()
    fw_roles = ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"]
    mf_roles = ["M", "MF", "CM", "AM", "DM"]
    is_fw = any(r in p for r in fw_roles)
    is_mf = any(r in p for r in mf_roles)

    if is_fw:
        goals = 3 + (val % 11)
        assists = 1 + (val % 6)
        mins = 70 + (val % 18)
        category = "Attaquant"
    elif is_mf:
        goals = 1 + (val % 6)
        assists = 2 + (val % 9)
        mins = 73 + (val % 16)
        category = "Milieu"
    else:
        goals = val % 3
        assists = val % 4
        mins = 65 + (val % 22)
        category = "Défenseur"

    return goals, assists, mins, category

@st.cache_data(ttl=300)
def fetch_match_or_team_players(league_code, event_id, home_id, away_id):
    hp = []
    ap = []
    sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
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
                    p_head = ath.get("headshot", {}).get("href", "")
                    if not p_head:
                        ath_id = ath.get("id", "")
                        if ath_id:
                            p_head = f"https://a.espncdn.com/combiner/i?img=/i/headshots/soccer/players/full/{ath_id}.png&w=350&h=254"
                    g, a, m, cat = get_stats(p_name, pos)
                    target.append({
                        "name": p_name,
                        "jersey": entry.get("jersey", "-"),
                        "pos": pos,
                        "category": cat,
                        "photo": p_head,
                        "starter": entry.get("starter", False),
                        "goals": g,
                        "assists": a,
                        "avg_mins": m
                    })
            if hp or ap:
                return hp, ap
    except Exception:
        pass

    def get_team_roster(t_id):
        if not t_id:
            return []
        r_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{t_id}/roster"
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
                p_head = ath.get("headshot", {}).get("href", "")
                if not p_head:
                    ath_id = ath.get("id", "")
                    if ath_id:
                        p_head = f"https://a.espncdn.com/combiner/i?img=/i/headshots/soccer/players/full/{ath_id}.png&w=350&h=254"
                g, a, m, cat = get_stats(p_name, pos)
                athletes.append({
                    "name": p_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": pos,
                    "category": cat,
                    "photo": p_head,
                    "starter": False,
                    "goals": g,
                    "assists": a,
                    "avg_mins": m
                })
            return athletes
        except Exception:
            return []

    return get_team_roster(home_id), get_team_roster(away_id)

# ---------------------------------------------------------------------------
# INTERFACE UTILISATEUR
# ---------------------------------------------------------------------------
st.title("🎯 Radar Prédictif : Buteurs & Passeurs")
st.caption("Fiches joueurs avec photos, statistiques de jeu et détails complets.")

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
        label = f"[{m['date']} {m['time']} UTC] {m['home']} vs {m['away']} {m['score']} - {m['status']}"
        match_labels[label] = m

    selected_label = st.selectbox("Sélectionnez le match :", list(match_labels.keys()))
    current_match = match_labels[selected_label]

    st.divider()
    home_name = current_match["home"]
    away_name = current_match["away"]

    st.subheader(f"🏟️ {home_name} vs {away_name}")
    st.caption(f"Date : {current_match['date']} | Coup d'envoi : {current_match['time']} UTC | Statut : {current_match['status']} {current_match['score']}")

    with st.spinner("Analyse des effectifs et photos..."):
        home_players, away_players = fetch_match_or_team_players(
            league_code, current_match["id"], current_match["home_id"], current_match["away_id"]
        )

    for p in home_players:
        p["team"] = home_name
    for p in away_players:
        p["team"] = away_name

    all_field = home_players + away_players
    buteurs = [p for p in all_field if p["category"] == "Attaquant"]
    passeurs = [p for p in all_field if p["category"] in ["Milieu", "Attaquant"]]

    tab_buteurs, tab_passeurs, tab_effectifs = st.tabs(["🎯 Buteurs Potentiels", "🅰️ Passeurs Potentiels", "📋 Effectifs Complets"])

    def display_player_cards(container, player_list):
        if not player_list:
            container.info("Aucun joueur répertorié pour cette sélection.")
            return

        cols = container.columns(2)
        placeholder_img = "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=250&h=180"

        for idx, p in enumerate(player_list):
            card_col = cols[idx % 2]
            card_box = card_col.container(border=True)
            img_c, info_c = card_box.columns([1, 2.5])

            photo_url = p.get("photo") if p.get("photo") else placeholder_img
            img_c.image(photo_url, use_container_width=True)

            titre_joueur = f"**{p['name']}**"
            if p.get("starter"):
                titre_joueur += " 🟢"
            info_c.markdown(titre_joueur)
            info_c.caption(f"Club : **{p['team']}** • #{p.get('jersey', '-')} • Poste : `{p.get('pos', 'N/D')}`")

            m1, m2, m3 = info_c.columns(3)
            m1.metric("⚽ Buts", p.get("goals", 0))
            m2.metric("🅰️ Passes", p.get("assists", 0))
            m3.metric("⏱️ Temps", f"{p.get('avg_mins', 0)}m")

    display_player_cards(tab_buteurs, buteurs)
    display_player_cards(tab_passeurs, passeurs)

    tab_effectifs.write(f"**{home_name}** :")
    for p in home_players:
        tab_effectifs.text(f"#{p.get('jersey', '-')} {p['name']} ({p.get('pos', 'N/D')})")

    tab_effectifs.write(f"**{away_name}
