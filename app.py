import streamlit as st
import requests

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "top10"

if "api_token" not in st.session_state:
    st.session_state.api_token = st.secrets.get("FOOTBALL_DATA_KEY", "")

# ---------------------------------------------------------------------------
# CSS PROPRE SANS GUILLEMETS MULTILIGNES
# ---------------------------------------------------------------------------
css_rules = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@700;800&display=swap');",
    "html, body { background-color: #090D16 !important; background: #090D16 !important; color: #F8FAFC !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }",
    ".stApp { background: #090D16 !important; color: #F8FAFC !important; }",
    "[data-testid='stHeader'], header[data-testid='stHeader'], [data-testid='stSidebar'], section[data-testid='stSidebar'], [data-testid='collapsedControl'] { display: none !important; }",
    ".block-container { max-width: 1220px !important; padding-top: 2rem !important; padding-bottom: 4rem !important; }",
    ".brand-shell { display: flex; justify-content: space-between; align-items: center; background: #111726; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 14px 24px; margin-bottom: 16px; }",
    ".brand-name { font-weight: 900; font-size: 1.35rem; color: #FFFFFF; letter-spacing: -0.5px; }",
    ".brand-name span { color: #00F0FF; }",
    ".brand-pill { background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.35); color: #00F0FF; font-size: 0.72rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; }",
    "div.text-nav-bar div[data-testid='stHorizontalBlock'] { align-items: center !important; justify-content: center !important; gap: 20px !important; background: transparent !important; }",
    "div.text-nav-bar button { background: transparent !important; background-color: transparent !important; border: none !important; outline: none !important; box-shadow: none !important; color: #8E9BAE !important; font-size: 0.92rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; padding: 8px 14px !important; margin: 0 !important; cursor: pointer !important; border-radius: 0 !important; transition: all 0.25s ease !important; }",
    "div.text-nav-bar button:hover { background: transparent !important; border: none !important; color: #00F0FF !important; text-shadow: 0 0 12px rgba(0, 240, 255, 0.6) !important; transform: translateY(-2px) !important; }",
    "div.text-nav-bar button:active, div.text-nav-bar button:focus { background: transparent !important; border: none !important; box-shadow: none !important; }",
    "label, [data-testid='stWidgetLabel'] { color: #F1F5F9 !important; font-weight: 700 !important; font-size: 0.9rem !important; margin-bottom: 6px !important; }",
    "div[data-baseweb='select'] > div { background: #111726 !important; border: 1.5px solid rgba(255, 255, 255, 0.12) !important; border-radius: 14px !important; }",
    "div[data-baseweb='select'] * { color: #FFFFFF !important; font-weight: 600 !important; }",
    ".bento-card { background: #111726; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 14px; margin-bottom: 16px; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4); transition: transform 0.2s ease, border-color 0.2s ease; }",
    ".bento-card:hover { transform: translateY(-3px); border-color: rgba(0, 240, 255, 0.45); box-shadow: 0 14px 30px rgba(0, 0, 0, 0.6), 0 0 16px rgba(0, 240, 255, 0.12); }",
    ".player-hero-banner { background: linear-gradient(135deg, #1A44C2 0%, #102B82 100%); border-radius: 14px; padding: 12px 14px; margin-bottom: 10px; }",
    ".player-hero-banner.rank-gold { background: linear-gradient(135deg, #C59B27 0%, #7A5700 100%); }",
    ".player-hero-banner.rank-silver { background: linear-gradient(135deg, #64748B 0%, #334155 100%); }",
    ".player-hero-banner.rank-bronze { background: linear-gradient(135deg, #965B2F 0%, #5C3212 100%); }",
    ".top-pills-row { display: flex; justify-content: space-between; align-items: center; }",
    ".tag-season { background: rgba(255, 255, 255, 0.2); color: #FFFFFF; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 6px; }",
    ".hero-name { font-size: 1.25rem; font-weight: 900; color: #FFFFFF; margin-top: 5px; letter-spacing: -0.3px; line-height: 1.15; }",
    ".hero-sub { display: flex; gap: 6px; margin-top: 6px; align-items: center; }",
    ".pill-info { background: rgba(0, 0, 0, 0.35); color: #E2E8F0; font-size: 0.7rem; font-weight: 700; padding: 2px 7px; border-radius: 6px; }",
    ".bento-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }",
    ".bento-tile { background: #0C111C; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 8px 4px; text-align: center; }",
    ".bento-tile.highlight-goals { background: rgba(0, 240, 255, 0.06); border: 1px solid rgba(0, 240, 255, 0.25); }",
    ".bento-val { font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 1.18rem; line-height: 1.1; color: #FFFFFF; }",
    ".bento-val.neon-cyan { color: #00F0FF; }",
    ".bento-val.neon-lime { color: #CCFF00; }",
    ".bento-val.neon-green { color: #00E676; }",
    ".bento-lbl { font-size: 0.64rem; font-weight: 700; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.3px; margin-top: 3px; }",
    "</style>"
]
st.markdown("".join(css_rules), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DONNÉES OFFICIELLES FOOTBALL-DATA.ORG
# ---------------------------------------------------------------------------
FD_LEAGUES = {
    "Ligue 1 (France)": {"code": "FL1", "flag": "🇫🇷"},
    "Premier League (Angleterre)": {"code": "PL", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "La Liga (Espagne)": {"code": "PD", "flag": "🇪🇸"},
    "Serie A (Italie)": {"code": "SA", "flag": "🇮🇹"},
    "Bundesliga (Allemagne)": {"code": "BL1", "flag": "🇩🇪"},
    "Ligue des Champions (UEFA)": {"code": "CL", "flag": "🇪🇺"}
}

@st.cache_data(ttl=3600)
def fetch_official_scorers(league_code, token=""):
    headers = {"X-Auth-Token": token} if token else {}
    url = f"https://api.football-data.org/v4/competitions/{league_code}/scorers?limit=15"
    players = []
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            scorers = data.get("scorers", [])
            for s in scorers:
                p_obj = s.get("player", {})
                t_obj = s.get("team", {})
                p_name = p_obj.get("name", "Joueur")
                t_name = t_obj.get("name", "Club")
                p_nat = p_obj.get("nationality", "Europe")
                p_pos = p_obj.get("section", "Offence")
                goals = s.get("goals", 0)
                assists = s.get("assists") or 0
                penalties = s.get("penalties") or 0
                played = s.get("playedMatches") or "-"
                pos_label = "ATT" if "offence" in str(p_pos).lower() or "forward" in str(p_pos).lower() else "MIL"
                players.append({
                    "id": f"{p_name}_{t_name}".replace(" ", "_"),
                    "name": p_name,
                    "team": t_name,
                    "pos": pos_label,
                    "nationality": p_nat,
                    "goals": goals,
                    "assists": assists,
                    "matches": played,
                    "penalties": penalties
                })
    except Exception:
        pass
    return players

@st.cache_data(ttl=3600)
def fetch_competition_teams(league_code, token=""):
    headers = {"X-Auth-Token": token} if token else {}
    url = f"https://api.football-data.org/v4/competitions/{league_code}/teams"
    teams = []
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            for t in r.json().get("teams", []):
                teams.append({"id": t.get("id"), "name": t.get("name")})
    except Exception:
        pass
    return sorted(teams, key=lambda x: x["name"])

def render_bento_card(player, rank_num=None):
    rank_text = f"#{rank_num}" if rank_num else "TOP"
    banner_class = "rank-gold" if rank_num == 1 else "rank-silver" if rank_num == 2 else "rank-bronze" if rank_num == 3 else ""
    ratio = round(player.get("goals", 0) / player.get("matches", 1), 2) if isinstance(player.get("matches"), int) and player.get("matches") > 0 else "-"

    card_lines = [
        '<div class="bento-card">',
        f'<div class="player-hero-banner {banner_class}">',
        '<div class="top-pills-row">',
        f'<span class="tag-season">TOP {rank_text} • OFFICIEL</span>',
        '<span class="tag-season">SAISON EN COURS</span>',
        '</div>',
        f'<div class="hero-name">{player.get("name")}</div>',
        '<div class="hero-sub">',
        f'<span class="pill-info">{player.get("pos", "ATT")}</span>',
        f'<span class="pill-info">{player.get("team")}</span>',
        f'<span class="pill-info">{player.get("nationality", "EUR")}</span>',
        '</div>',
        '</div>',
        '<div class="bento-grid">',
        f'<div class="bento-tile highlight-goals"><div class="bento-val neon-cyan">{player.get("goals", 0)}</div><div class="bento-lbl">⚽ Buts</div></div>',
        f'<div class="bento-tile"><div class="bento-val neon-lime">{player.get("assists", 0)}</div><div class="bento-lbl">🅰️ Passes</div></div>',
        f'<div class="bento-tile"><div class="bento-val">{player.get("matches", "-")}</div><div class="bento-lbl">🏟️ Matchs</div></div>',
        f'<div class="bento-tile"><div class="bento-val">{player.get("penalties", 0)}</div><div class="bento-lbl">🎯 Penaltys</div></div>',
        f'<div class="bento-tile"><div class="bento-val">{ratio}</div><div class="bento-lbl">Ratio / m</div></div>',
        '<div class="bento-tile"><div class="bento-val neon-green">✓</div><div class="bento-lbl">Certifié</div></div>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(card_lines), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NAVIGATION STYLE ZYRON (SANS BLOCS BLANCS)
# ---------------------------------------------------------------------------
header_lines = [
    '<div class="brand-shell">',
    '<div class="brand-name">GOAL <span>SNIPER</span>.</div>',
    '<div class="brand-pill">Données Certifiées</div>',
    '</div>'
]
st.markdown("".join(header_lines), unsafe_allow_html=True)

st.markdown('<div class="text-nav-bar">', unsafe_allow_html=True)
col_nav = st.columns([1, 1, 1])

with col_nav[0]:
    t1 = "• TOP 10 CHAMPIONNAT •" if st.session_state.nav_tab == "top10" else "Top 10 Championnat"
    if st.button(t1, key="nav_top10", use_container_width=True):
        st.session_state.nav_tab = "top10"
        st.rerun()

with col_nav[1]:
    t2 = "• TOP PAR ÉQUIPE •" if st.session_state.nav_tab == "top5" else "Top par Équipe"
    if st.button(t2, key="nav_top5", use_container_width=True):
        st.session_state.nav_tab = "top5"
        st.rerun()

with col_nav[2]:
    t3 = "• PARAMÈTRES •" if st.session_state.nav_tab == "reglages" else "Paramètres"
    if st.button(t3, key="nav_reglages", use_container_width=True):
        st.session_state.nav_tab = "reglages"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# VUE 1 : TOP 10 DU CHAMPIONNAT
# ---------------------------------------------------------------------------
if st.session_state.nav_tab == "top10":
    selected_league_label = st.selectbox("Sélectionnez la compétition officielle :", list(FD_LEAGUES.keys()))
    league_info = FD_LEAGUES[selected_league_label]

    with st.spinner(f"Chargement des vraies statistiques pour {selected_league_label}..."):
        top_scorers = fetch_official_scorers(league_info["code"], st.session_state.api_token)

    if not top_scorers:
        st.warning(
            "Aucune donnée reçue. Rendez-vous dans **Paramètres** pour vérifier votre clé Football-Data.org."
        )
    else:
        st.markdown(f"<div style='font-weight:800; font-size:1.1rem; color:#00F0FF; margin:14px 0 14px 0;'>🏆 {league_info['flag']} Vrais Meilleurs Buteurs — {selected_league_label}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, player in enumerate(top_scorers[:12], start=1):
            with cols[(idx - 1) % 3]:
                render_bento_card(player, rank_num=idx)

# ---------------------------------------------------------------------------
# VUE 2 : TOP PAR ÉQUIPE
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "top5":
    selected_league_label = st.selectbox("Compétition :", list(FD_LEAGUES.keys()), key="eq_comp")
    league_info = FD_LEAGUES[selected_league_label]

    with st.spinner("Chargement des clubs officiels..."):
        teams_list = fetch_competition_teams(league_info["code"], st.session_state.api_token)

    if not teams_list:
        st.info("Veuillez renseigner votre token Football-Data dans **Paramètres** pour accéder à la liste des clubs.")
    else:
        team_names = [t["name"] for t in teams_list]
        chosen_team = st.selectbox("Sélectionnez l'équipe :", team_names, key="eq_team")

        all_scorers = fetch_official_scorers(league_info["code"], st.session_state.api_token)
        team_scorers = [p for p in all_scorers if chosen_team.lower() in p["team"].lower() or p["team"].lower() in chosen_team.lower()]

        st.markdown(f"<div style='font-weight:800; font-size:1.1rem; color:#00F0FF; margin:14px 0 14px 0;'>🎯 Buteurs officiels — {chosen_team}</div>", unsafe_allow_html=True)
        if not team_scorers:
            st.info(f"Aucun joueur de {chosen_team} ne figure actuellement dans le top buteurs de la ligue.")
        else:
            cols = st.columns(3)
            for idx, p in enumerate(team_scorers, start=1):
                with cols[(idx - 1) % 3]:
                    render_bento_card(p, rank_num=idx)

# ---------------------------------------------------------------------------
# VUE 3 : PARAMÈTRES (CLÉ API & CACHE)
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "reglages":
    with st.container():
        st.markdown("#### 🔑 Clé API Football-Data.org (Gratuite)")
        st.caption("Garantit des données certifiées en temps réel :")
        current_token = st.text_input("Token API :", value=st.session_state.api_token, type="password")
        if current_token != st.session_state.api_token:
            st.session_state.api_token = current_token
            st.success("Clé API mise à jour !")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🧹 Données & Cache")
    if st.button("Vider le cache et resynchroniser", type="primary"):
        st.cache_data.clear()
        st.success("Cache vidé avec succès !")
        st.rerun()
