import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs & Passeurs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# GESTION DES FAVORIS ET PERSISTANCE LOCALE
# ---------------------------------------------------------------------------
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

if "theme_accent" not in st.session_state:
    st.session_state.theme_accent = "Vert Néon (#00E676)"

# ---------------------------------------------------------------------------
# DIRECTION ARTISTIQUE & CSS PERSONNALISÉ SANS PHOTOS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;0,900;1,800&family=JetBrains+Mono:wght@500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, #151c2e 0%, #0a0d14 70%, #06080d 100%);
    color: #F0F4F8;
}

.header-hero {
    background: linear-gradient(135deg, rgba(20, 28, 48, 0.8) 0%, rgba(10, 14, 24, 0.9) 100%);
    border: 1px solid rgba(0, 230, 118, 0.25);
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 22px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(10px);
}
.header-hero h1 {
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: -0.5px;
    margin: 0;
    background: linear-gradient(90deg, #FFFFFF 0%, #00E676 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header-hero p {
    color: #94A3B8;
    margin-top: 5px;
    font-size: 0.92rem;
}

.player-card {
    background: linear-gradient(145deg, #131b2e 0%, #0e1422 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 16px;
    position: relative;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
    transition: all 0.25s ease-in-out;
}
.player-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 230, 118, 0.5);
    box-shadow: 0 12px 28px rgba(0, 230, 118, 0.12);
}
.player-card.rank-top {
    border-top: 3px solid #FFD700;
}

.card-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.rank-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
    color: #000;
    font-weight: 900;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 8px;
    display: inline-block;
}

.player-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.2;
    margin-top: 4px;
}

.player-sub {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 4px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 10px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.stat-box {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 8px 6px;
    text-align: center;
}
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 1.15rem;
    color: #00E676;
}
.stat-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    color: #94A3B8;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

.tag-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
}
.tag-fw { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.tag-mf { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); }
.tag-club { background: rgba(255, 255, 255, 0.08); color: #E2E8F0; }

@media (max-width: 768px) {
    .header-hero h1 { font-size: 1.45rem; }
    .player-title { font-size: 1.1rem; }
    .stats-grid { grid-template-columns: repeat(3, 1fr); gap: 6px; }
    .stat-value { font-size: 1rem; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CONFIGURATION DES LIGUES & ENDPOINTS ESPN
# ---------------------------------------------------------------------------
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ---------------------------------------------------------------------------
# CHARGEMENT DES DONNÉES RÉELLES
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_official_league_leaders(league_code):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/statistics"
    buteurs = []
    passeurs = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            categories = r.json().get("stats", {}).get("categories", [])
            for cat in categories:
                c_name = str(cat.get("name", "")).lower()
                is_goal = ("goal" in c_name or "scorer" in c_name)
                is_assist = ("assist" in c_name)
                
                if not (is_goal or is_assist):
                    continue

                for rank, leader in enumerate(cat.get("leaders", []), start=1):
                    ath = leader.get("athlete", {})
                    team_name = ath.get("team", {}).get("displayName", "Club N/D")
                    pos_name = ath.get("position", {}).get("abbreviation", "ATT" if is_goal else "MIL")
                    p_id = str(ath.get("id", ""))
                    nat_info = ath.get("citizenship", "") or ath.get("flag", {}).get("alt", "N/D")
                    val_stat = int(leader.get("value", 0))

                    player_dict = {
                        "id": p_id or f"{ath.get('displayName')}_{team_name}",
                        "rank": rank,
                        "name": ath.get("displayName", "Joueur"),
                        "team": team_name,
                        "pos": pos_name,
                        "nationality": nat_info,
                        "goals": val_stat if is_goal else "N/D",
                        "assists": val_stat if is_assist else "N/D",
                        "matches": ath.get("statistics", {}).get("gamesPlayed", "N/D"),
                        "shots_pg": "N/D",
                        "shots_on_target": "N/D",
                        "avg_mins": "N/D"
                    }

                    if is_goal:
                        buteurs.append(player_dict)
                    elif is_assist:
                        passeurs.append(player_dict)
    except Exception:
        pass

    return buteurs[:15], passeurs[:15]

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
def fetch_team_top_players(league_code, team_id, team_name):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{team_id}/roster"
    players = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            athletes = r.json().get("athletes", [])
            for ath in athletes:
                pos = ath.get("position", {}).get("abbreviation", "")
                if pos in ["G", "GK"]:
                    continue
                
                p_id = str(ath.get("id", ""))
                is_fw = any(x in pos for x in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
                
                players.append({
                    "id": p_id or f"{ath.get('displayName')}_{team_name}",
                    "name": ath.get("displayName", "Joueur"),
                    "team": team_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": pos or "OFF",
                    "is_fw": is_fw,
                    "nationality": ath.get("citizenship", "N/D"),
                    "goals": "En cours",
                    "assists": "En cours",
                    "matches": "N/D",
                    "shots_pg": "N/D",
                    "shots_on_target": "N/D",
                    "avg_mins": "N/D"
                })
    except Exception:
        pass

    players.sort(key=lambda p: (1 if p["is_fw"] else 0), reverse=True)
    return players[:5]

# ---------------------------------------------------------------------------
# CARTE JOUEUR ÉPURÉE SANS PHOTO
# ---------------------------------------------------------------------------
def render_player_card(player,
