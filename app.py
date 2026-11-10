import streamlit as st
import requests
import json
import os

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

# Récupération du token d'accès officiel
if "api_token" not in st.session_state:
    st.session_state.api_token = st.secrets.get("FOOTBALL_DATA_KEY", "")

# ---------------------------------------------------------------------------
# CSS ULTRA-CLEAN : CONTRASTES NETS, ZÉRO BOUTON BLANC, GRILLE BENTO
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@700;800&display=swap');

html, body {
    background-color: #090D16 !important;
    background: #090D16 !important;
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #090D16 !important;
    color: #F8FAFC !important;
}

[data-testid="stHeader"], header[data-testid="stHeader"],
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 1220px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 4rem !important;
}

label, [data-testid="stWidgetLabel"] {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    margin-bottom: 6px !important;
}
div[data-baseweb="select"] > div {
    background: #111726 !important;
    border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
}
div[data-baseweb="select"] * {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Header de marque */
.brand-shell {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 12px 22px;
    margin-bottom: 12px;
}
.brand-name {
    font-weight: 900;
    font-size: 1.35rem;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
.brand-name span {
    color: #00F0FF;
}
.brand-pill {
    background: rgba(0, 240, 255, 0.12);
    border: 1px solid rgba(0, 240, 255, 0.35);
    color: #00F0FF;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
}

/* Boutons de navigation */
div.nav-row div[data-testid="stHorizontalBlock"] button {
    background: #131A29 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    font-weight: 700 !important;
    font-size: 0.86rem !important;
    padding: 10px 12px !important;
    transition: all 0.2s ease !important;
}
div.nav-row div[data-testid="stHorizontalBlock"] button:hover {
    background: rgba(0, 240, 255, 0.15) !important;
    border-color: #00F0FF !important;
    color: #FFFFFF !important;
    transform: translateY(-2px) !important;
}

/* CARTE BENTO BOX PROPRE */
.bento-card {
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 14px;
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

/* Bouton favori intégré sous chaque carte */
div.fav-row-action button {
    background: rgba(255, 215, 0, 0.08) !important;
    border: 1px solid rgba(255, 215, 0, 0.3) !important;
    border-radius: 12px !important;
    color: #FFD700 !important;
    font-weight: 800 !important;
    font-size: 0.78rem !important;
    padding: 6px 12px !important;
    transition: all 0.2s ease !important;
}
div.fav-row-action button:hover {
    background: rgba(255, 215, 0, 0.22) !important;
    border-color: #FFD700 !important;
    transform: translateY(-1px) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# COMPÉTITIONS OFFICIELLES (SAISON EN COURS CERTIFIÉE)
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
                    "shots_pg": penalties,
                    "shots_on_target": "-",
                    "avg_mins": "Certifié"
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

# ---------------------------------------------------------------------------
# RENDU CARTE BENTO BOX
# ---------------------------------------------------------------------------
def render_bento_card(player, rank_num=None):
    pid = str(player.get("id", player.get("name")))
    is_fav = pid in st.session_state.favorites

    rank_text = f"#{rank_num}" if rank_num else "TOP"
    banner_class = "rank-gold" if rank_num == 1 else "rank-silver" if rank_num == 2 else "rank-bronze" if rank_num == 3 else ""

    card_html = (
        f'<div class="bento-card">'
        f'<div class="player-hero-banner {banner_class}">'
        f'<div class="top-pills-row">'
        f'<span class="tag-season">TOP {rank_text} • OFFICIEL</span>'
        f'<span class="tag-season">SAISON EN COURS</span>'
        f'</div>'
        f'<div class="hero-name">{player.get("name")}</div>'
        f'<div class="hero-sub">'
        f'<span class="pill-info">{player.get("pos", "ATT")}</span>'
        f'<span class="pill-info">{player.get("team")}</span>'
        f'<span class="pill-info">{player.get("nationality", "EUR")}</span>'
        f'</div>'
        f'</div>'
        f'<div class="bento-grid">'
        f'<div class="bento-tile highlight-goals"><div class="bento-val neon-cyan">{player.get("goals", 0)}</div><div class="bento-lbl">⚽ Buts</div></div>'
        f'<div class="bento-tile"><div class="bento-val neon-lime">{player.get("assists", 0)}</div><div class="bento-lbl">🅰️ Passes</div></div>'
        f'<div class="bento-tile"><div class="bento-val">{player.get("matches", "-")}</div><div class="bento-lbl">🏟️ Matchs</div></div>'
        f'<div class="bento-tile"><div class="bento-val">{player.get("shots_pg", 0)}</div><div class="bento-lbl">🎯 Penaltys</div></div>'
        f'<div class="bento-tile"><div class="bento-val">{round(player.get("goals", 0) / player.get("matches", 1), 2) if isinstance(player.get("matches"), int) and player.get("matches") > 0 else "-"}</div><div class="bento-lbl">Ratio / m</div></div>'
        f'<div class="bento-tile"><div class="bento-val neon-green">✓</div><div class="bento-lbl">Certifié</div></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
    
    st.markdown('<div class="fav-row-action">', unsafe_allow_html=True)
    fav_label = "★ DANS MES FAVORIS" if is_fav else "☆ AJOUTER AUX FAVORIS"
    if st.button(fav_label, key=f"fbtn_{pid}", use_container_width=True):
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
# NAVIGATION PRINCIPALE
# ---------------------------------------------------------------------------
st.markdown("""
<div class="brand-shell">
    <div class="brand-name">GOAL <span>SNIPER</span>.</div>
    <div class="brand-pill">Données Réelles Certifiées</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-row">', unsafe_allow_html=True)
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    l1 = "🟢 TOP 10 CHAMPIONNAT" if st.session_state.nav_tab == "top10" else "TOP 10 CHAMPIONNAT"
    if st.button(l1, use_container_width=True):
        st.session_state.nav_tab = "top10"
        st.rerun()
with b2:
    l2 = "🟢 TOP PAR ÉQUIPE" if st.session_state.nav_tab == "top5" else "TOP PAR ÉQUIPE"
    if st.button(l2, use_container_width=True):
        st.session_state.nav_tab = "top5"
        st.rerun()
with b3:
    count_fav = len(st.session_state.favorites)
    l3 = f"🟢 FAVORIS ({count_fav})" if st.session_state.nav_tab == "favoris" else f"FAVORIS ({count_fav})"
    if st.button(l3, use_container_width=True):
        st.session_state.nav_tab = "favoris"
        st.rerun()
with b4:
    l4 = "🟢 MON PROFIL" if st.session_state.nav_tab == "profil" else "MON PROFIL"
    if st.button(l4, use_container_width=True):
        st.session_state.nav_tab = "profil"
        st.rerun()
with b5:
    l5 = "🟢 PARAMÈTRES" if st.session_state.nav_tab == "reglages" else "PARAMÈTRES"
    if st.button(l5, use_container_width=True):
        st.session_state.nav_tab = "reglages"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# VUE 1 : TOP 10 DU CHAMPIONNAT (100% OFFICIEL SANS STATS INVENTÉES)
# ---------------------------------------------------------------------------
if st.session_state.nav_tab == "top10":
    selected_league_label = st.selectbox("Sélectionnez la compétition officielle :", list(FD_LEAGUES.keys()))
    league_info = FD_LEAGUES[selected_league_label]

    with st.spinner(f"Chargement des vraies statistiques certifiées pour {selected_league_label}..."):
        top_scorers = fetch_official_scorers(league_info["code"], st.session_state.api_token)

    if not top_scorers:
        st.warning(
            "Aucune donnée reçue de l'API officielle pour ce championnat sans clé API. "
            "Rendez-vous dans la section **Paramètres** pour renseigner votre token gratuit Football-Data.org (gratuit en 30 secondes)."
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
        st.info("Veuillez renseigner votre token Football-Data dans **Paramètres** pour accéder à la liste des clubs de ce championnat.")
    else:
        team_names = [t["name"] for t in teams_list]
        chosen_team = st.selectbox("Sélectionnez l'équipe :", team_names, key="eq_team")

        all_scorers = fetch_official_scorers(league_info["code"], st.session_state.api_token)
        team_scorers = [p for p in all_scorers if chosen_team.lower() in p["team"].lower() or p["team"].lower() in chosen_team.lower()]

        st.markdown(f"<div style='font-weight:800; font-size:1.1rem; color:#00F0FF; margin:14px 0 14px 0;'>🎯 Buteurs officiels en forme — {chosen_team}</div>", unsafe_allow_html=True)
        if not team_scorers:
            st.info(f"Aucun buteur de {chosen_team} ne figure actuellement dans le classement des meilleurs buteurs du championnat.")
        else:
            cols = st.columns(3)
            for idx, p in enumerate(team_scorers, start=1):
                with cols[(idx - 1) % 3]:
                    render_bento_card(p, rank_num=idx)

# ---------------------------------------------------------------------------
# VUE 3 : MES FAVORIS
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "favoris":
    st.markdown("<div style='font-weight:800; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;'>⭐ Ma Sélection de Buteurs</div>", unsafe_allow_html=True)
    favs = st.session_state.favorites

    if not favs:
        st.info("Aucun joueur favori pour l'instant. Cliquez sur 'Ajouter aux favoris' sous une carte pour l'enregistrer ici.")
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
        m2.metric("Compétitions officielles", len(FD_LEAGUES))

# ---------------------------------------------------------------------------
# VUE 5 : PARAMÈTRES (CONFIG CLÉ OFFICIELLE & CACHE)
# ---------------------------------------------------------------------------
elif st.session_state.nav_tab == "reglages":
    st.markdown("<div style='font-weight:800; font-size:1.2rem; color:#FFFFFF; margin-bottom:12px;'>⚙️ Paramètres & Clé API</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("#### 🔑 Clé API Football-Data.org (Gratuite)")
        st.caption("Pour garantir des données 100% réelles et sans coupure de quota :")
        current_token = st.text_input("Token API Football-Data.org :", value=st.session_state.api_token, type="password")
        if current_token != st.session_state.api_token:
            st.session_state.api_token = current_token
            st.success("Clé API enregistrée !")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🧹 Données & Cache")
    if st.button("Vider le cache et resynchroniser", type="primary"):
        st.cache_data.clear()
        st.success("Cache vidé avec succès !")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🗑️ Favoris")
    if st.button("Purger tous mes favoris"):
        st.session_state.favorites = {}
        save_stored_favorites({})
        st.warning("Favoris effacés.")
        st.rerun()
