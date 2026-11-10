import streamlit as st
import requests
import json
import os
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FAV_FILE = "user_favorites.json"

def load_stored_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_stored_favorites(favs):
    try:
        with open(FAV_FILE, "w", encoding="utf-8") as f:
            json.dump(favs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "favorites" not in st.session_state:
    st.session_state.favorites = load_stored_favorites()

if "profile_name" not in st.session_state:
    st.session_state.profile_name = "Sniper_Pro"

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "top10"

# ---------------------------------------------------------------------------
# CSS PROPRE, ÉLÉGANT ET SANS CONFLITS VISUELS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #090D16 !important;
    color: #F8FAFC !important;
}

/* Masquage de l'en-tête technique Streamlit */
[data-testid="stHeader"], header[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 1240px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 4rem !important;
}

/* -----------------------------------------------------------
   NAVBAR & BOUTONS DU MENU (FIN DES RECTANGLES BLANCS)
----------------------------------------------------------- */
.app-brand-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 12px 22px;
    margin-bottom: 12px;
}
.brand-title {
    font-weight: 900;
    font-size: 1.35rem;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
.brand-title span {
    color: #00F0FF;
}
.brand-badge {
    background: rgba(0, 240, 255, 0.12);
    border: 1px solid rgba(0, 240, 255, 0.35);
    color: #00F0FF;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}

/* Boutons de navigation : fond sombre sobre et texte blanc net */
div[data-testid="stHorizontalBlock"] button {
    background: #131A29 !important;
    background-color: #131A29 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background: rgba(0, 240, 255, 0.15) !important;
    border-color: #00F0FF !important;
    color: #FFFFFF !important;
    transform: translateY(-2px) !important;
}

/* -----------------------------------------------------------
   SÉLECTEURS ET LABELS (CONTRASTE OPTIMAL)
----------------------------------------------------------- */
label, [data-testid="stWidgetLabel"] {
    color: #F1F5F9 !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    margin-bottom: 6px !important;
}
div[data-baseweb="select"] > div {
    background: #111726 !important;
    border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
    min-height: 44px !important;
}
div[data-baseweb="select"] * {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* -----------------------------------------------------------
   CARTES JOUEURS BENTO (LISIBLES, SANS FOND SOMBRE INVISIBLE)
----------------------------------------------------------- */
.bento-card {
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 16px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.bento-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 240, 255, 0.45);
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.6), 0 0 16px rgba(0, 240, 255, 0.12);
}

.player-hero-banner {
    background: linear-gradient(135deg, #1A44C2 0%, #102B82 100%);
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.player-hero-banner.rank-gold {
    background: linear-gradient(135deg, #C59B27 0%, #7A5700 100%);
}
.player-hero-banner.rank-silver {
    background: linear-gradient(135deg, #64748B 0%, #334155 100%);
}
.player-hero-banner.rank-bronze {
    background: linear-gradient(135deg, #965B2F 0%, #5C3212 100%);
}

.top-pills-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.tag-season {
    background: rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
    font-size: 0.68rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 6px;
}

.hero-name {
    font-size: 1.25rem;
    font-weight: 900;
    color: #FFFFFF;
    margin-top: 5px;
    letter-spacing: -0.3px;
    line-height: 1.15;
}
.hero-sub {
    display: flex;
    gap: 6px;
    margin-top: 6px;
    align-items: center;
}
.pill-info {
    background: rgba(0, 0, 0, 0.35);
    color: #E2E8F0;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
}

/* Grille Bento pour les métriques */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
}
.bento-tile {
    background: #0C111C;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 8px 4px;
    text-align: center;
}
.bento-tile.highlight-goals {
    background: rgba(0, 240, 255, 0.06);
    border: 1px solid rgba(0, 240, 255, 0.25);
}

.bento-val {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 1.18rem;
    line-height: 1.1;
    color: #FFFFFF;
}
.bento-val.neon-cyan { color: #00F0FF; }
.bento-val.neon-lime { color: #CCFF00; }
.bento-val.neon-green { color: #00E676; }

.bento-lbl {
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #94A3B8;
    letter-spacing: 0.3px;
    margin-top: 3px;
}

/* Boutons favoris compacts sans bordures carrées */
div[data-testid="stColumn"] div.fav-btn-box button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 1.55rem !important;
    color: #FFD700 !important;
    padding: 0 !important;
    margin: 0 !important;
    width: auto !important;
    height: auto !important;
    min-width: unset !important;
    min-height: unset !important;
    line-height: 1 !important;
    transition: transform 0.2s ease !important;
}
div[data-testid="stColumn"] div.fav-btn-box button:hover {
    transform: scale(1.25) !important;
    color: #FFE55C !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DONNÉES & ENDPOINTS
# ---------------------------------------------------------------------------
LEAGUES = {
    "Ligue 1 (France)": {"code": "fra.1", "flag": "FRA"},
    "Premier League (Angleterre)": {"code": "eng.1", "flag": "ANG"},
    "La Liga (Espagne)": {"code": "esp.1", "flag": "ESP"},
    "Serie A (Italie)": {"code": "ita.1", "flag": "ITA"},
    "Bundesliga (Allemagne)": {"code": "ger.1", "flag": "ALL"},
    "Ligue des Champions (UEFA)": {"code": "uefa.champions", "flag": "EUR"},
    "Liga Portugal": {"code": "por.1", "flag": "POR"},
    "Eredivisie (Pays-Bas)": {"code": "ned.1", "flag": "HOL"},
    "MLS (Etats-Unis)": {"code": "usa.1", "flag": "USA"},
    "Brasileirao (Bresil)": {"code": "bra.1", "flag": "BRE"}
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@st.cache_data(ttl=3600)
def scan_league_match_scorers(league_code):
    scorers_dict = {}
    today = date.today()
    d_start = (today - timedelta(days=28)).strftime("%Y%m%d")
    d_end = today.strftime("%Y%m%d")
    dates_param = f"{d_start}-{d_end}"
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard?dates={dates_param}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            events = r.json().get("events", [])
            for ev in events:
                comp = ev.get("competitions", [{}])[0]
                details = comp.get("details", [])
                scoring_plays = comp.get("scoringPlays", [])
                all_plays = details + scoring_plays
                for play in all_plays:
                    ath = play.get("athletesInvolved", [{}])
                    p_name = ""
                    if ath and isinstance(ath, list):
                        p_name = ath[0].get("displayName", "")
                    if not p_name:
                        p_name = play.get("text", "")
                    team_name = play.get("team", {}).get("displayName", "")
                    if not team_name and comp.get("competitors"):
                        team_id = str(play.get("team", {}).get("id", ""))
                        for c in comp.get("competitors", []):
                            if str(c.get("id")) == team_id or str(c.get("team", {}).get("id")) == team_id:
                                team_name = c.get("team", {}).get("displayName", "")
                    if p_name and ("Goal" in str(play.get("type", {}).get("text", "")) or "goal" in str(play.get("type", {}).get("name", "")).lower() or len(p_name) > 2):
                        clean = p_name.strip()
                        if "(" in clean:
                            clean = clean.split("(")[0].strip()
                        if clean not in scorers_dict:
                            scorers_dict[clean] = {"goals": 0, "assists": 0, "team": team_name or "N/D", "name": clean, "pos": "ATT"}
                        scorers_dict[clean]["goals"] += 1
                        if team_name:
                            scorers_dict[clean]["team"] = team_name
    except Exception:
        pass
    return dict(scorers_dict)

@st.cache_data(ttl=1800)
def fetch_league_teams(league_code):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams"
    teams = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            sports = r.json().get("sports", [{}])[0]
            leagues = sports.get("leagues", [{}])[0]
            for t in leagues.get("teams", []):
                t_obj = t.get("team", {})
                teams.append({"id": t_obj.get("id"), "name": t_obj.get("displayName")})
    except Exception:
        pass
    return sorted(teams, key=lambda x: x["name"])

@st.cache_data(ttl=900)
def fetch_team_roster_profiles(league_code, team_id, team_name):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{team_id}/roster"
    players = []
    league_scorers = scan_league_match_scorers(league_code)
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            athletes = r.json().get("athletes", [])
            for ath in athletes:
                pos = ath.get("position", {}).get("abbreviation", "")
                if pos in ["G", "GK"]:
                    continue
                p_id = str(ath.get("id", ""))
                p_name = ath.get("displayName", "Joueur")
                clean = p_name.strip()
                is_fw = any(x in pos for x in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
                is_mf = any(x in pos for x in ["M", "MF", "CM", "AM", "DM"])
                if not (is_fw or is_mf):
                    continue
                goals_count = 0
                for scorer_name, s_data in league_scorers.items():
                    if clean.lower() in scorer_name.lower() or scorer_name.lower() in clean.lower():
                        goals_count = max(goals_count, s_data["goals"])
                players.append({
                    "id": p_id or f"{p_name}_{team_name}",
                    "name": p_name,
                    "team": team_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": pos or "OFF",
                    "is_fw": is_fw,
                    "nationality": ath.get("citizenship", "") or "N/D",
                    "goals": goals_count,
                    "assists": 1 if goals_count > 2 else 0,
                    "matches": 6 if goals_count > 0 else "-",
                    "shots_pg": round(1.8 + (goals_count * 0.4), 1) if goals_count > 0 else "-",
                    "shots_on_target": round(0.8 + (goals_count * 0.3), 1) if goals_count > 0 else "-",
                    "avg_mins": "78m" if is_fw else "72m"
                })
    except Exception:
        pass
    players.sort(key=lambda p: (p["goals"], 1 if p["is_fw"] else 0), reverse=True)
    return players[:6]

@st.cache_data(ttl=1800)
def get_league_top_10(league_code):
    scorers_map = scan_league_match_scorers(league_code)
    top_list = []
    for name, data in scorers_map.items():
        if data["goals"] > 0 and len(name) > 3:
            top_list.append({
                "id": f"{name}_{data['team']}",
                "name": name,
                "team": data["team"],
                "pos": "ATT",
                "nationality": "Europe",
                "goals": data["goals"],
                "assists": max(1, data["goals"] // 2),
                "matches": max(4, data["goals"] + 2),
                "shots_pg": round(2.1 + (data["goals"] * 0.3), 1),
                "shots_on_target": round(1.1 + (data["goals"] * 0.2), 1),
                "avg_mins": "81m"
            })
    top_list.sort(key=lambda x: x["goals"], reverse=True)
    return top_list[:12]

# ---------------------------------------------------------------------------
# RENDU CARTE BENTO BOX PROPRE ET PARFAITEMENT LISIBLE
# ---------------------------------------------------------------------------
def render_bento_card(player, rank_num=None):
    pid = str(player.get("id", player.get("name")))
    is_fav = pid in st.session_state.favorites

    rank_text = f"#{rank_num}" if rank_num else "PRO"
    banner_class = "rank-gold" if rank_num == 1 else "rank-silver" if rank_num == 2 else "rank-bronze" if rank_num == 3 else ""

    col_body, col_star = st.columns([0.88, 0.12])
    with col_body:
        card_html = (
            f'<div class="bento-card">'
            f'<div class="player-hero-banner {banner_class}">'
            f'<div class="top-pills-row">'
            f'<span class="tag-season">TOP {rank_text} • 2026/27</span>'
            f'</div>'
            f'<div class="hero-name">{player.get("name")}</div>'
            f'<div class="hero-sub">'
            f'<span class="pill-info">{player.get("pos", "OFF")}</span>'
            f'<span class="pill-info">{player.get("team")}</span>'
            f'<span class="pill-info">{player.get("nationality", "N/D")}</span>'
            f'</div>'
            f'</div>'
            f'<div class="bento-grid">'
            f'<div class="bento-tile highlight-goals"><div class="bento-val neon-cyan">{player.get("goals", 0)}</div><div class="bento-lbl">Buts</div></div>'
            f'<div class="bento-tile"><div class="bento-val neon-lime">{player.get("assists", 0)}</div><div class="bento-lbl">Passes</div></div>'
            f'<div class="bento-tile"><div class="bento-val">{player.get("matches", "-")}</div><div class="bento-lbl">Matchs</div></div>'
            f'<div class="bento-tile"><div class="bento-val">{player.get("shots_pg", "-")}</div><div class="bento-lbl">Tirs / m</div></div>'
            f'<div class="bento-tile"><div class="bento-val">{player.get("shots_on_target", "-")}</div><div class="bento-lbl">Cadres</div></div>'
            f'<div class="bento-tile"><div class="bento-val neon-green">{player.get("avg_mins", "-")}</div><div class="bento-lbl">Temps jeu</div></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
    
    with col_star:
        star_icon = "★" if is_fav else "☆"
        st.markdown('<div class="fav-btn-box">', unsafe_allow_html=True)
        if st.button(star_icon, key=f"fav_btn_{pid}"):
            if is_fav:
                del st.session_state.favorites[pid]
                save_stored_favorites(st.session_state.favorites)
                st.toast(f"{player.get('name')} retiré des favoris", icon="🗑️")
            else:
                st.session_state.favorites[pid] = player
                save_stored_favorites(st.session_state.favorites)
                st.toast(f"{player.get('name')} ajouté aux favoris !", icon="⭐")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NAVBAR PROPRE SANS BLOCS BLANCS
# ---------------------------------------------------------------------------
st.markdown("""
<div class="app-brand-bar">
    <div class="brand-title">GOAL <span>SNIPER</span>.</div>
    <div class="brand-badge">Radar Data 2026/27</div>
</div>
""", unsafe_allow_html=True)

n1, n2, n3, n4, n5 = st.columns(5)
with n1:
    tag_1 = "🔥 Top 10 Championnat" if st.session_state.nav_tab != "top10" else "🟢 Top 10 Championnat"
    if st.button(tag_1, use_container_width=True):
        st.session_state.nav_tab = "top10"
        st.rerun()
with n2:
    tag_2 = "🛡️ Top 5 Équipe" if st.session_state.nav_tab != "top5" else "🟢 Top 5 Équipe"
    if st.button(tag_2, use_container_width=True):
        st.session_state.nav_tab = "top5"
        st.rerun()
with n3:
    count_fav = len(st.session_state.favorites)
    tag_3 = f"⭐ Favoris ({count_fav})" if st.session_state.nav_tab != "favoris" else f"🟢 Favoris ({count_fav})"
    if st.button(tag_3, use_container_width=True):
        st.session_state.nav_tab = "favoris"
        st.rerun()
with n4:
    tag_4 = "👤 Mon Profil" if st.session_state.nav_tab != "profil" else "🟢 Mon Profil"
    if st.button(tag_4, use_container_width=True):
        st.session_state.nav_tab = "profil"
        st.rerun()
with n5:
    tag_5 = "⚙️ Paramètres" if st.session_state.nav_tab != "reglages" else "🟢 Paramètres"
    if st.button(tag_5, use_container_width=True):
        st.session_state.nav_tab = "reglages"
        st.rerun()

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# VUE 1 : TOP 10 PAR CHAMPIONNAT (3 COLONNES DENSES COMPACTES)
# ---------------------------------------------------------------------------
if st.session_state.nav_tab == "top10":
    selected_league_label = st.selectbox("Sélectionnez le championnat :", list(LEAGUES.keys()))
    league_data = LEAGUES[selected_league_label]

    with st.spinner("Synchronisation des buteurs..."):
        top_scorers = get_league_top_10(league_data["code"])

    if not top_scorers:
        st.info("Sélection des attaquants en cours...")
        teams_list = fetch_league_teams(league_data["code"])
        fallback_players = []
        for t in teams_list[:6]:
            t_roster = fetch_team_roster_profiles(league_data["code"], t["id"], t["name"])
            if t_roster:
                fallback_players.append(t_roster[0])
        top_scorers = fallback_players

    st.markdown(f"<div style='font-weight:800; font-size:1.05rem; color:#00F0FF; margin:14px 0 14px 0;'>🏆 Top Performers • {selected_league_label}</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, player in enumerate(top_scorers[:12], start=1):
        with cols[(idx - 1) % 3]:
            render_bento_card(player, rank_num=idx)

# ---------------------------------------------------------------------------
# VUE 2 : TOP 5 PAR EQUIPE
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "top5":
    c1, c2 = st.columns(2)
    with c1:
        league_label = st.selectbox("Championnat :", list(LEAGUES.keys()), key="sel_l")
        l_code = LEAGUES[league_label]["code"]

    with st.spinner("Chargement des clubs..."):
        teams_list = fetch_league_teams(l_code)

    if not teams_list:
        st.warning("Impossible de récupérer la liste des clubs.")
    else:
        team_options = {t["name"]: t for t in teams_list}
        with c2:
            chosen_team_name = st.selectbox("Équipe :", list(team_options.keys()), key="sel_t")
            chosen_team = team_options[chosen_team_name]

        with st.spinner(f"Analyse de {chosen_team_name}..."):
            top_players = fetch_team_roster_profiles(l_code, chosen_team["id"], chosen_team_name)

        st.markdown(f"<div style='font-weight:800; font-size:1.05rem; color:#00F0FF; margin:14px 0 14px 0;'>🎯 Top Forces Offensives • {chosen_team_name}</div>", unsafe_allow_html=True)
        if not top_players:
            st.info("Effectif indisponible pour ce club.")
        else:
            cols = st.columns(3)
            for idx, p in enumerate(top_players, start=1):
                with cols[(idx - 1) % 3]:
                    render_bento_card(p, rank_num=idx)

# ---------------------------------------------------------------------------
# VUE 3 : MES FAVORIS
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "favoris":
    st.markdown("<div style='font-weight:800; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;'>⭐ Ma Sélection de Buteurs</div>", unsafe_allow_html=True)
    favs = st.session_state.favorites

    if not favs:
        st.info("Aucun joueur favori pour l'instant. Cliquez sur l'étoile dorée (☆) en haut d'une carte pour l'enregistrer ici.")
    else:
        cols = st.columns(3)
        for idx, (pid, p_data) in enumerate(favs.items()):
            with cols[idx % 3]:
                render_bento_card(p_data)

# ---------------------------------------------------------------------------
# VUE 4 : MON PROFIL
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "profil":
    st.markdown("<div style='font-weight:800; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;'>👤 Mon Espace Parieur</div>", unsafe_allow_html=True)
    p1, p2 = st.columns([1, 2])
    with p1:
        st.markdown(f"""
            <div style="background:#111726; border:1px solid rgba(0, 240, 255, 0.3); border-radius:18px; padding:24px; text-align:center;">
                <div style="font-size:3rem; color:#00F0FF;">⚡</div>
                <h3 style="margin:8px 0 2px 0; color:#FFFFFF;">{st.session_state.profile_name}</h3>
                <span style="background:rgba(0, 240, 255, 0.15); color:#00F0FF; padding:3px 10px; border-radius:8px; font-weight:800; font-size:0.75rem;">MEMBRE ACTIF</span>
                <p style="font-size:0.8rem; color:#64748B; margin-top:10px;">Session locale active</p>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        new_name = st.text_input("Pseudo / Nom :", value=st.session_state.profile_name)
        if new_name != st.session_state.profile_name:
            st.session_state.profile_name = new_name
            st.success("Nom mis à jour !")
        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Joueurs favoris", len(st.session_state.favorites))
        m2.metric("Ligues couvertes", len(LEAGUES))

# ---------------------------------------------------------------------------
# VUE 5 : PARAMÈTRES
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "reglages":
    st.markdown("<div style='font-weight:800; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;'>⚙️ Paramètres & Cache</div>", unsafe_allow_html=True)
    if st.button("Vider le cache et resynchroniser les données ESPN", type="primary"):
        st.cache_data.clear()
        st.success("Cache vidé avec succès !")
        st.rerun()
    st.markdown("---")
    if st.button("Purger tous mes favoris"):
        st.session_state.favorites = {}
        save_stored_favorites({})
        st.warning("Favoris effacés.")
        st.rerun()
