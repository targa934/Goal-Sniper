import streamlit as st
import requests
import json
import os

st.set_page_config(
    page_title="Goal Sniper | Radar Buteurs & Passeurs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
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

@st.cache_data(ttl=1800)
def fetch_league_all_stats(league_code):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/statistics"
    stats_map = {}
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
                    p_id = str(ath.get("id", ""))
                    val = int(leader.get("value", 0))

                    for key in [p_name, p_id]:
                        if not key:
                            continue
                        if key not in stats_map:
                            stats_map[key] = {"goals": 0, "assists": 0, "matches": "-"}
                        if is_goal:
                            stats_map[key]["goals"] = val
                        elif is_assist:
                            stats_map[key]["assists"] = val
    except Exception:
        pass
    return stats_map

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

                    # Extraction propre des matchs joués si disponible
                    gp = ath.get("statistics", {}).get("gamesPlayed", "-")

                    player_dict = {
                        "id": p_id or f"{ath.get('displayName')}_{team_name}",
                        "rank": rank,
                        "name": ath.get("displayName", "Joueur"),
                        "team": team_name,
                        "pos": pos_name,
                        "nationality": nat_info,
                        "goals": val_stat if is_goal else 0,
                        "assists": val_stat if is_assist else 0,
                        "matches": gp,
                        "shots_pg": "-",
                        "shots_on_target": "-",
                        "avg_mins": "-"
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

@st.cache_data(ttl=1800)
def fetch_team_internal_stats(league_code, team_id):
    """
    Interroge les statistiques officielles publiées par ESPN pour le club ciblé.
    Renvoie le dictionnaire {player_id / player_name: {goals, assists, matches}}.
    """
    team_stats = {}
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{team_id}/statistics"
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            categories = r.json().get("stats", {}).get("categories", [])
            for cat in categories:
                c_name = str(cat.get("name", "")).lower()
                is_goal = ("goal" in c_name or "scorer" in c_name)
                is_assist = ("assist" in c_name)
                for leader in cat.get("leaders", []):
                    ath = leader.get("athlete", {})
                    p_name = ath.get("displayName", "").strip().lower()
                    p_id = str(ath.get("id", ""))
                    val = int(leader.get("value", 0))
                    for k in [p_name, p_id]:
                        if not k:
                            continue
                        if k not in team_stats:
                            team_stats[k] = {"goals": 0, "assists": 0, "matches": "-"}
                        if is_goal:
                            team_stats[k]["goals"] = val
                        elif is_assist:
                            team_stats[k]["assists"] = val
    except Exception:
        pass
    return team_stats

@st.cache_data(ttl=900)
def fetch_team_top_players(league_code, team_id, team_name):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/teams/{team_id}/roster"
    players = []
    
    # 1. Stats spécifiques au club depuis ESPN
    club_stats = fetch_team_internal_stats(league_code, team_id)
    # 2. Stats globales de la ligue
    league_stats = fetch_league_all_stats(league_code)

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
                clean_name = p_name.strip().lower()
                is_fw = any(x in pos for x in ["F", "A", "FW", "CF", "ST", "W", "LW", "RW"])
                is_mf = any(x in pos for x in ["M", "MF", "CM", "AM", "DM"])

                if not (is_fw or is_mf):
                    continue

                # Récupération des stats réelles :
                g = 0
                a = 0
                
                # Vérification dans les stats du club
                if p_id in club_stats:
                    g = max(g, club_stats[p_id].get("goals", 0))
                    a = max(a, club_stats[p_id].get("assists", 0))
                elif clean_name in club_stats:
                    g = max(g, club_stats[clean_name].get("goals", 0))
                    a = max(a, club_stats[clean_name].get("assists", 0))

                # Vérification dans les stats de la ligue
                if p_id in league_stats:
                    g = max(g, league_stats[p_id].get("goals", 0))
                    a = max(a, league_stats[p_id].get("assists", 0))
                elif clean_name in league_stats:
                    g = max(g, league_stats[clean_name].get("goals", 0))
                    a = max(a, league_stats[clean_name].get("assists", 0))

                # Matchs joués si renseignés dans l'objet ath
                matches_played = ath.get("statistics", {}).get("gamesPlayed", "-")

                players.append({
                    "id": p_id or f"{p_name}_{team_name}",
                    "name": p_name,
                    "team": team_name,
                    "jersey": ath.get("jersey", "-"),
                    "pos": pos or "OFF",
                    "is_fw": is_fw,
                    "nationality": ath.get("citizenship", "") or "N/D",
                    "goals": g,
                    "assists": a,
                    "matches": matches_played,
                    "shots_pg": "-",
                    "shots_on_target": "-",
                    "avg_mins": "-"
                })
    except Exception:
        pass

    # Classement : Priorité aux joueurs ayant déjà marqué/délivré des passes, puis profil pur attaquant
    players.sort(key=lambda p: (p["goals"], p["assists"], 1 if p["is_fw"] else 0), reverse=True)
    return players[:5]

def render_player_card(player, rank_num=None, category_mode="Buteur"):
    pid = str(player.get("id", player.get("name")))
    is_fav = pid in st.session_state.favorites

    col_card, col_btn = st.columns([5.2, 0.8])
    
    with col_card:
        rank_badge_html = f'<span class="rank-badge">TOP #{rank_num}</span>' if rank_num else ''
        rank_top_cls = 'rank-top' if rank_num and rank_num <= 3 else ''
        pos_cls = 'tag-fw' if ('F' in player.get('pos', '') or 'A' in player.get('pos', '')) else 'tag-mf'
        
        card_lines = [
            f'<div class="player-card {rank_top_cls}">',
            '<div class="card-header-bar">',
            '<div>',
            '<div style="display:flex;gap:6px;align-items:center;">',
            rank_badge_html,
            f'<span class="tag-pill {pos_cls}">{player.get("pos", "OFF")}</span>',
            f'<span class="tag-pill tag-club">{player.get("team")}</span>',
            '</div>',
            f'<div class="player-title">{player.get("name")}</div>',
            f'<div class="player-sub">Nationalité : {player.get("nationality", "N/D")}</div>',
            '</div>',
            '</div>',
            '<div class="stats-grid">',
            f'<div class="stat-box"><div class="stat-value">{player.get("goals", 0)}</div><div class="stat-label">⚽ Buts</div></div>',
            f'<div class="stat-box"><div class="stat-value">{player.get("assists", 0)}</div><div class="stat-label">🅰️ Passes</div></div>',
            f'<div class="stat-box"><div class="stat-value">{player.get("matches", "-")}</div><div class="stat-label">🏟️ Matchs</div></div>',
            f'<div class="stat-box"><div class="stat-value">{player.get("shots_pg", "-")}</div><div class="stat-label">🎯 Tirs / m</div></div>',
            f'<div class="stat-box"><div class="stat-value">{player.get("shots_on_target", "-")}</div><div class="stat-label">🥅 Cadrés / m</div></div>',
            f'<div class="stat-box"><div class="stat-value">{player.get("avg_mins", "-")}</div><div class="stat-label">⏱️ Temps jeu</div></div>',
            '</div>',
            '</div>'
        ]
        st.markdown("".join(card_lines), unsafe_allow_html=True)

    with col_btn:
        st.write("")
        fav_label = "★" if is_fav else "☆"
        fav_help = "Retirer des favoris" if is_fav else "Ajouter aux favoris"
        if st.button(fav_label, key=f"fav_{pid}", help=fav_help, use_container_width=True):
            if is_fav:
                del st.session_state.favorites[pid]
                save_stored_favorites(st.session_state.favorites)
                st.toast(f"{player.get('name')} retiré des favoris", icon="🗑️")
            else:
                st.session_state.favorites[pid] = player
                save_stored_favorites(st.session_state.favorites)
                st.toast(f"{player.get('name')} ajouté aux favoris !", icon="⭐")
            st.rerun()

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <div style="font-size: 2.2rem;">⚡ <b>GOAL SNIPER</b></div>
            <div style="font-size: 0.8rem; color: #00E676; letter-spacing: 1.5px; text-transform: uppercase;">Radar Offensif & Data</div>
        </div>
    """, unsafe_allow_html=True)

    menu_selection = st.radio(
        "Navigation",
        [
            "🔥 Top 10 Championnats",
            "🛡️ Top 5 par Équipe",
            "⭐ Mes Favoris",
            "👤 Mon Profil",
            "⚙️ Paramètres"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Données réelles certifiées ESPN.")

if menu_selection == "🔥 Top 10 Championnats":
    st.markdown("""
        <div class="header-hero">
            <h1>🔥 Top 10 Buteurs & Passeurs</h1>
            <p>Classement en temps réel des joueurs les plus décisifs de chaque compétition officielle.</p>
        </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2 = st.columns([2, 2])
    with f_col1:
        selected_league_label = st.selectbox("Sélectionnez le championnat :", list(LEAGUES.keys()))
        league_data = LEAGUES[selected_league_label]
    
    with f_col2:
        profil_mode = st.radio("Profil recherché :", ["⚽ Meilleurs Buteurs", "🅰️ Meilleurs Passeurs"], horizontal=True)

    with st.spinner("Synchronisation des classements officiels réels..."):
        buteurs_top, passeurs_top = fetch_official_league_leaders(league_data["code"])

    target_list = buteurs_top if "Buteurs" in profil_mode else passeurs_top

    if not target_list:
        st.info("Aucune statistique officielle publiée pour le moment sur cette compétition.")
    else:
        st.markdown(f"### {league_data['flag']} Top 10 {selected_league_label} — {profil_mode}")
        cols = st.columns(2)
        for idx, player in enumerate(target_list[:10], start=1):
            with cols[(idx - 1) % 2]:
                render_player_card(player, rank_num=idx, category_mode=profil_mode)

elif menu_selection == "🛡️ Top 5 par Équipe":
    st.markdown("""
        <div class="header-hero">
            <h1>🛡️ Top 5 Offensif par Club</h1>
            <p>Analysez les 5 joueurs d'attaque les plus dangereux d'un effectif ciblé.</p>
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

        with st.spinner(f"Analyse des forces offensives de {chosen_team_name}..."):
            top_players = fetch_team_top_players(l_code, chosen_team["id"], chosen_team_name)

        st.markdown(f"### 🎯 Top 5 Offensive Squad — {chosen_team_name}")
        if not top_players:
            st.info("Effectif indisponible pour ce club.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(top_players, start=1):
                with cols[(idx - 1) % 2]:
                    render_player_card(p, rank_num=idx)

elif menu_selection == "⭐ Mes Favoris":
    st.markdown("""
        <div class="header-hero">
            <h1>⭐ Ma Sélection de Joueurs</h1>
            <p>Vos profils clés sauvegardés pour préparer vos paris et suivre vos buteurs fétiches.</p>
        </div>
    """, unsafe_allow_html=True)

    favs = st.session_state.favorites

    if not favs:
        st.info("Vous n'avez pas encore ajouté de joueur à vos favoris. Cliquez sur l'étoile (☆) sur une carte pour l'enregistrer ici.")
    else:
        st.write(f"**{len(favs)} joueur(s) dans votre carnet de sniper :**")
        cols = st.columns(2)
        for idx, (pid, p_data) in enumerate(favs.items()):
            with cols[idx % 2]:
                render_player_card(p_data)

elif menu_selection == "👤 Mon Profil":
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

elif menu_selection == "⚙️ Paramètres":
    st.markdown("""
        <div class="header-hero">
            <h1>⚙️ Paramètres & Configuration</h1>
            <p>Personnalisation de l'affichage et maintenance des données en cache.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🧹 Données & Cache")
        st.caption("Si une statistique vient d'évoluer en direct, vous pouvez forcer le rafraîchissement des données ESPN.")
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
