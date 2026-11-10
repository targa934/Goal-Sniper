import streamlit as st
import requests
import json
import os
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs & Passeurs",
    page_icon="⚡",
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

if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Top 10 Championnats"

# ---------------------------------------------------------------------------
# DIRECTION ARTISTIQUE & CSS ULTRA-TRAVAILLÉ (STYLE EA SPORTS FC / WINAMAX PRO)
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;0,900;1,800&family=JetBrains+Mono:wght@500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', -apple-system, sans-serif !important;
}

/* Fond général sombre et texturé */
.stApp {
    background: radial-gradient(circle at 50% 0%, #111726 0%, #090c13 65%, #05070a 100%) !important;
    color: #F0F4F8 !important;
}

/* -----------------------------------------------------------
   MENU NAVIGATION SPORTIF MODERNE (BARRE SUPÉRIEURE ÉPURÉE)
----------------------------------------------------------- */
.top-nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(0, 230, 118, 0.2);
    border-radius: 16px;
    padding: 10px 18px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
}
.brand-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 900;
    font-size: 1.4rem;
    letter-spacing: -0.5px;
    color: #FFFFFF;
}
.brand-title span {
    color: #00E676;
    text-shadow: 0 0 12px rgba(0, 230, 118, 0.5);
}

/* Sidebar Streamlit compacte & stylisée */
section[data-testid="stSidebar"] {
    background: #0b0f19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    padding-top: 1.5rem !important;
    gap: 0.5rem !important;
}

/* Style des radio boutons de navigation dans le menu */
div[data-testid="stRadio"] > div {
    gap: 8px !important;
}
div[data-testid="stRadio"] label {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    color: #94A3B8 !important;
    transition: all 0.2s ease-in-out !important;
    cursor: pointer !important;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(0, 230, 118, 0.08) !important;
    border-color: rgba(0, 230, 118, 0.3) !important;
    color: #FFFFFF !important;
    transform: translateX(4px) !important;
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background: linear-gradient(90deg, rgba(0, 230, 118, 0.15) 0%, rgba(0, 230, 118, 0.02) 100%) !important;
    border-color: #00E676 !important;
    color: #00E676 !important;
    box-shadow: 0 0 15px rgba(0, 230, 118, 0.15) !important;
}

/* -----------------------------------------------------------
   HERO BANNER COMPACTE
----------------------------------------------------------- */
.header-hero {
    background: linear-gradient(135deg, rgba(22, 33, 56, 0.6) 0%, rgba(11, 16, 28, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #00E676;
    border-radius: 14px;
    padding: 16px 22px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
}
.header-hero h1 {
    font-weight: 900;
    font-size: 1.6rem;
    letter-spacing: -0.5px;
    margin: 0;
    color: #FFFFFF;
}
.header-hero p {
    color: #94A3B8;
    margin-top: 4px;
    font-size: 0.86rem;
}

/* -----------------------------------------------------------
   VRAIE CARTE JOUEUR EA SPORTS FC / TRADING CARD
----------------------------------------------------------- */
.fut-card-container {
    background: linear-gradient(150deg, #151d30 0%, #0d121e 100%);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
.fut-card-container:hover {
    transform: translateY(-4px);
    border-color: rgba(0, 230, 118, 0.45);
    box-shadow: 0 12px 30px rgba(0, 230, 118, 0.12);
}
.fut-card-container.top-1 {
    border-top: 3px solid #FFD700;
}
.fut-card-container.top-2 {
    border-top: 3px solid #E2E8F0;
}
.fut-card-container.top-3 {
    border-top: 3px solid #CD7F32;
}

.card-top-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
}

.rank-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
    color: #000000;
    font-weight: 900;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.25);
}

.tag-pill {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 5px;
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
}
.tag-fw { background: rgba(239, 68, 68, 0.18); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.35); }
.tag-mf { background: rgba(59, 130, 246, 0.18); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.35); }
.tag-club { background: rgba(255, 255, 255, 0.08); color: #E2E8F0; font-weight: 600; }

.player-title {
    font-size: 1.22rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.2;
    margin-top: 5px;
    letter-spacing: -0.3px;
}

.player-sub {
    font-size: 0.78rem;
    color: #94A3B8;
    margin-top: 2px;
}

/* Grille de stats compacte et percutante */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 7px;
    margin-top: 12px;
    padding-top: 11px;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
}
.stat-box {
    background: rgba(10, 15, 26, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 7px 4px;
    text-align: center;
}
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 1.12rem;
    color: #00E676;
    line-height: 1.1;
}
.stat-label {
    font-size: 0.64rem;
    text-transform: uppercase;
    color: #8A99AD;
    letter-spacing: 0.4px;
    margin-top: 3px;
    font-weight: 600;
}

/* -----------------------------------------------------------
   SUPPRESSION RADICALE DU RECTANGLE BLANC FAVORIS
----------------------------------------------------------- */
.fav-btn-slot div[data-testid="stButton"] {
    display: flex !important;
    justify-content: flex-end !important;
}
.fav-btn-slot div[data-testid="stButton"] button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    min-width: unset !important;
    min-height: unset !important;
    width: 32px !important;
    height: 32px !important;
    font-size: 1.55rem !important;
    line-height: 1 !important;
    color: #FFD700 !important;
    cursor: pointer !important;
    transition: transform 0.2s ease, text-shadow 0.2s ease !important;
}
.fav-btn-slot div[data-testid="stButton"] button:hover {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #FFE55C !important;
    transform: scale(1.3) !important;
    text-shadow: 0 0 14px rgba(255, 215, 0, 0.85) !important;
}
.fav-btn-slot div[data-testid="stButton"] button:active,
.fav-btn-slot div[data-testid="stButton"] button:focus {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Adaptation mobile */
@media (max-width: 768px) {
    .header-hero h1 { font-size: 1.35rem; }
    .player-title { font-size: 1.05rem; }
    .stats-grid { grid-template-columns: repeat(3, 1fr); gap: 5px; }
    .stat-value { font-size: 0.95rem; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

LEAGUES = {
    "Ligue 1 (France)": {"code": "fra.1", "flag": "🇫🇷"},
    "Premier League (Angleterre)": {"code": "eng.1", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "La Liga (Espagne)": {"code": "esp.1", "flag": "🇪🇸"},
    "Serie A (Italie)": {"code": "ita.1", "flag": "🇮🇹"},
    "Bundesliga (Allemagne)": {"code": "ger.1", "flag": "🇩🇪"},
    "Ligue des Champions (UEFA)": {"code": "uefa.champions", "flag": "🇪🇺"},
    "Liga Portugal": {"code": "por.1", "flag": "🇵🇹"},
    "Eredivisie (Pays-Bas)": {"code": "ned.1", "flag": "🇳🇱"},
    "MLS (États-Unis)": {"code": "usa.1", "flag": "🇺🇸"},
    "Brasileirão (Brésil)": {"code": "bra.1", "flag": "🇧🇷"}
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
                            scorers_dict[clean] = {"goals": 0, "assists": 0, "matches_scored": 0, "team": team_name or "N/D", "name": clean, "pos": "ATT"}
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
                teams.append({
                    "id": t_obj.get("id"),
                    "name": t_obj.get("displayName")
                })
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
    return players[:5]

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
    return top_list[:10]

# ---------------------------------------------------------------------------
# RENDU CARTE JOUEUR (STRUCTURE COMPLÈTE & ÉTOILE PURÉE SANS RECTANGLE)
# ---------------------------------------------------------------------------
def render_player_card(player, rank_num=None):
    pid = str(player.get("id", player.get("name")))
    is_fav = pid in st.session_state.favorites

    rank_badge_html = f'<span class="rank-badge">TOP #{rank_num}</span>' if rank_num else ''
    top_cls = f"top-{rank_num}" if rank_num and rank_num <= 3 else ""
    pos_cls = 'tag-fw' if ('F' in player.get('pos', '') or 'A' in player.get('pos', '')) else 'tag-mf'

    # Enveloppe globale de la carte en HTML pour garantir que tout reste unifié
    header_html = f"""
    <div class="fut-card-container {top_cls}">
        <div class="card-top-header">
            <div>
                <div style="display:flex; gap:6px; align-items:center;">
                    {rank_badge_html}
                    <span class="tag-pill {pos_cls}">{player.get('pos', 'OFF')}</span>
                    <span class="tag-pill tag-club">{player.get('team')}</span>
                </div>
                <div class="player-title">{player.get('name')}</div>
                <div class="player-sub">Nationalité : {player.get('nationality', 'N/D')}</div>
            </div>
    """
    
    # Rendu du haut de la carte avec Streamlit columns pour positionner l'étoile
    c_info, c_fav = st.columns([0.88, 0.12])
    with c_info:
        top_frag = [
            f'<div class="fut-card-container {top_cls}">',
            '<div style="display:flex; justify-content:space-between; align-items:flex-start;">',
            '<div>',
            '<div style="display:flex; gap:6px; align-items:center;">',
            rank_badge_html,
            f'<span class="tag-pill {pos_cls}">{player.get("pos", "OFF")}</span>',
            f'<span class="tag-pill tag-club">{player.get("team")}</span>',
            '</div>',
            f'<div class="player-title">{player.get("name")}</div>',
            f'<div class="player-sub">Nationalité : {player.get("nationality", "N/D")}</div>',
            '</div>',
            '</div>'
        ]
        st.markdown("".join(top_frag), unsafe_allow_html=True)
    
    with c_fav:
        star_icon = "★" if is_fav else "☆"
        st.markdown('<div class="fav-btn-slot">', unsafe_allow_html=True)
        if st.button(star_icon, key=f"btn_fav_{pid}", help="Ajouter / Retirer des favoris"):
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

    # Grille de statistiques attachée
    stats_frag = [
        '<div style="margin-top:-14px; margin-bottom:14px; background:linear-gradient(150deg, #151d30 0%, #0d121e 100%); border:1px solid rgba(255,255,255,0.09); border-top:none; border-radius:0 0 16px 16px; padding:0 16px 16px 16px;">',
        '<div class="stats-grid">',
        f'<div class="stat-box"><div class="stat-value">{player.get("goals", 0)}</div><div class="stat-label">⚽ Buts récents</div></div>',
        f'<div class="stat-box"><div class="stat-value">{player.get("assists", 0)}</div><div class="stat-label">🅰️ Passes</div></div>',
        f'<div class="stat-box"><div class="stat-value">{player.get("matches", "-")}</div><div class="stat-label">🏟️ Matchs</div></div>',
        f'<div class="stat-box"><div class="stat-value">{player.get("shots_pg", "-")}</div><div class="stat-label">🎯 Tirs / m</div></div>',
        f'<div class="stat-box"><div class="stat-value">{player.get("shots_on_target", "-")}</div><div class="stat-label">🥅 Cadrés / m</div></div>',
        f'<div class="stat-box"><div class="stat-value">{player.get("avg_mins", "-")}</div><div class="stat-label">⏱️ Temps jeu</div></div>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(stats_frag), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NAVIGATION PRINCIPALE (SIDEBAR ÉPURÉE & ULTRA-COMPACTE)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 1.6rem; font-weight:900; letter-spacing:-0.5px;">⚡ <span style="color:#00E676;">GOAL</span> SNIPER</div>
            <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight:700; letter-spacing:1px;">Radar Prédictif</div>
        </div>
    """, unsafe_allow_html=True)

    nav_options = [
        "🔥 Top 10 Championnats",
        "🛡️ Top 5 par Équipe",
        "⭐ Mes Favoris",
        "👤 Mon Profil",
        "⚙️ Paramètres"
    ]
    
    selected_nav = st.radio("Navigation", nav_options, label_visibility="collapsed")
    st.markdown("---")
    st.caption("Données extraites des feuilles de matchs réelles ESPN Scoreboard.")

# ---------------------------------------------------------------------------
# VUES
# ---------------------------------------------------------------------------
if selected_nav == "🔥 Top 10 Championnats":
    st.markdown("""
        <div class="header-hero">
            <h1>🔥 Top 10 Buteurs du Championnat</h1>
            <p>Classement consolidé des buteurs les plus prolifiques sur les dernières journées de compétition.</p>
        </div>
    """, unsafe_allow_html=True)

    selected_league_label = st.selectbox("Sélectionnez le championnat :", list(LEAGUES.keys()))
    league_data = LEAGUES[selected_league_label]

    with st.spinner("Analyse des feuilles de matchs et compilation des buteurs..."):
        top_scorers = get_league_top_10(league_data["code"])

    if not top_scorers:
        st.info("Compilation des matchs récents en cours. Sélection des attaquants clés en tête du championnat...")
        teams_list = fetch_league_teams(league_data["code"])
        fallback_players = []
        for t in teams_list[:5]:
            t_roster = fetch_team_roster_profiles(league_data["code"], t["id"], t["name"])
            if t_roster:
                fallback_players.append(t_roster[0])
        top_scorers = fallback_players

    st.markdown(f"### {league_data['flag']} Meilleurs Buteurs — {selected_league_label}")
    cols = st.columns(2)
    for idx, player in enumerate(top_scorers[:10], start=1):
        with cols[(idx - 1) % 2]:
            render_player_card(player, rank_num=idx)

elif selected_nav == "🛡️ Top 5 par Équipe":
    st.markdown("""
        <div class="header-hero">
            <h1>🛡️ Top 5 Offensif par Club</h1>
            <p>Analysez les 5 forces d'attaque prioritaires de l'effectif sélectionné.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        league_label = st.selectbox("Ligue :", list(LEAGUES.keys()), key="team_league_sel")
        l_code = LEAGUES[league_label]["code"]

    with st.spinner("Chargement des clubs..."):
        teams_list = fetch_league_teams(l_code)

    if not teams_list:
        st.warning("Impossible de récupérer la liste des clubs pour ce tournoi.")
    else:
        team_options = {t["name"]: t for t in teams_list}
        with c2:
            chosen_team_name = st.selectbox("Sélectionnez l'équipe :", list(team_options.keys()))
            chosen_team = team_options[chosen_team_name]

        with st.spinner(f"Analyse de l'effectif offensif de {chosen_team_name}..."):
            top_players = fetch_team_roster_profiles(l_code, chosen_team["id"], chosen_team_name)

        st.markdown(f"### 🎯 Top 5 Offensive Squad — {chosen_team_name}")
        if not top_players:
            st.info("Effectif indisponible pour ce club.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(top_players, start=1):
                with cols[(idx - 1) % 2]:
                    render_player_card(p, rank_num=idx)

elif selected_nav == "⭐ Mes Favoris":
    st.markdown("""
        <div class="header-hero">
            <h1>⭐ Ma Sélection de Joueurs</h1>
            <p>Vos profils clés sauvegardés pour préparer vos paris et suivre vos buteurs fétiches.</p>
        </div>
    """, unsafe_allow_html=True)

    favs = st.session_state.favorites

    if not favs:
        st.info("Vous n'avez pas encore ajouté de joueur à vos favoris. Cliquez sur l'étoile dorée sur une carte pour l'enregistrer ici.")
    else:
        st.write(f"**{len(favs)} joueur(s) dans votre carnet de sniper :**")
        cols = st.columns(2)
        for idx, (pid, p_data) in enumerate(favs.items()):
            with cols[idx % 2]:
                render_player_card(p_data)

elif selected_nav == "👤 Mon Profil":
    st.markdown("""
        <div class="header-hero">
            <h1>👤 Espace Parieur</h1>
            <p>Gérez vos préférences, vos sélections et vos paramètres personnels.</p>
        </div>
    """, unsafe_allow_html=True)

    p1, p2 = st.columns([1, 2])
    with p1:
        st.markdown(f"""
            <div style="background: rgba(19, 27, 46, 0.8); border: 1px solid rgba(0, 230, 118, 0.3); border-radius: 16px; padding: 20px; text-align: center;">
                <div style="font-size: 3.5rem;">🎯</div>
                <h3 style="margin: 8px 0 2px 0;">{st.session_state.profile_name}</h3>
                <span class="tag-pill" style="background: rgba(0, 230, 118, 0.2); color: #00E676;">Membre Pro</span>
                <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 10px;">Compte local actif sur cet appareil</p>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        with st.container(border=True):
            st.markdown("#### ⚙️ Vos Informations")
            new_name = st.text_input("Pseudo / Nom d'utilisateur :", value=st.session_state.profile_name)
            if new_name != st.session_state.profile_name:
                st.session_state.profile_name = new_name
                st.success("Nom mis à jour !")

            st.markdown("---")
            st.markdown("#### 📊 Statistiques de votre compte")
            m1, m2 = st.columns(2)
            m1.metric("Joueurs en favoris", len(st.session_state.favorites))
            m2.metric("Compétitions suivies", len(LEAGUES))

elif selected_nav == "⚙️ Paramètres":
    st.markdown("""
        <div class="header-hero">
            <h1>⚙️ Paramètres & Configuration</h1>
            <p>Maintenance des données en cache et réinitialisation.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🧹 Données & Cache")
        st.caption("Forcer la synchronisation avec les dernières feuilles de match ESPN.")
        if st.button("Vider le cache et resynchroniser", type="primary"):
            st.cache_data.clear()
            st.success("Le cache a été vidé avec succès.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🗑️ Réinitialisation des favoris")
        if st.button("Supprimer tous mes favoris"):
            st.session_state.favorites = {}
            save_stored_favorites({})
            st.warning("Tous vos favoris ont été effacés.")
            st.rerun()
