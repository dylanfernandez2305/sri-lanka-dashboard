import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from streamlit_folium import st_folium

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sri Lanka Explorer",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #FFF8F0;
  }

  .main { background-color: #FFF8F0; }

  h1, h2, h3 {
    font-family: 'Playfair Display', serif;
    color: #1a3a2a;
  }

  /* Hero banner */
  .hero {
    background: linear-gradient(135deg, #1a6b3c 0%, #e8a020 50%, #c0392b 100%);
    border-radius: 20px;
    padding: 40px 50px;
    color: white;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "🌴🌊🐘🦚";
    position: absolute;
    right: 30px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 3rem;
    letter-spacing: 10px;
    opacity: 0.8;
  }
  .hero h1 { color: white; font-size: 3rem; margin: 0; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
  .hero p  { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 8px; }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(26,106,60,0.1);
    border-top: 5px solid;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .kpi-value { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 900; }
  .kpi-label { font-size: 0.8rem; color: #666; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }
  .kpi-icon  { font-size: 1.6rem; margin-bottom: 4px; }

  /* Section titles */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: #1a3a2a;
    border-left: 5px solid #e8a020;
    padding-left: 14px;
    margin: 30px 0 16px 0;
  }

  /* Season badge */
  .season-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 0.85rem;
    margin: 4px;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a2a 0%, #1a6b3c 100%);
  }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stSelectbox label { color: #a8d5b5 !important; }

  /* Footer */
  .footer {
    text-align: center;
    padding: 20px;
    color: #888;
    font-size: 0.8rem;
    margin-top: 40px;
    border-top: 1px solid #eee;
  }
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
MONTHS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]

# Météo côte ouest (Colombo)
TEMP_WEST  = [27, 28, 29, 30, 30, 29, 28, 28, 28, 27, 27, 27]
RAIN_WEST  = [89, 69, 147, 231, 371, 224, 135, 109, 160, 348, 315, 147]

# Météo côte est (Trincomalee)
TEMP_EAST  = [26, 27, 28, 30, 31, 31, 30, 30, 29, 27, 26, 26]
RAIN_EAST  = [230, 120, 60, 40, 55, 40, 65, 110, 180, 280, 390, 310]

# Tourisme mensuel (milliers d'arrivées)
TOURISTS   = [280, 260, 290, 220, 180, 150, 160, 170, 190, 210, 250, 300]

# Saisons par région
SEASONS_WEST = ["☀️ Haute","☀️ Haute","☀️ Haute","🌦 Inter","🌧 Mousson","🌧 Mousson",
                "🌧 Mousson","🌧 Mousson","🌦 Inter","🌦 Inter","☀️ Haute","☀️ Haute"]
SEASONS_EAST = ["🌧 Mousson","🌧 Mousson","🌦 Inter","☀️ Haute","☀️ Haute","☀️ Haute",
                "☀️ Haute","☀️ Haute","🌦 Inter","🌦 Inter","🌧 Mousson","🌧 Mousson"]

# Top destinations
DESTINATIONS = {
    "Sigiriya":        {"lat": 7.9570,  "lon": 80.7603, "type": "Patrimoine", "rating": 9.5, "emoji": "🏰"},
    "Galle":           {"lat": 6.0535,  "lon": 80.2210, "type": "Ville",      "rating": 9.0, "emoji": "🏛️"},
    "Ella":            {"lat": 6.8667,  "lon": 81.0466, "type": "Nature",     "rating": 9.2, "emoji": "🌿"},
    "Kandy":           {"lat": 7.2906,  "lon": 80.6337, "type": "Culture",    "rating": 8.8, "emoji": "🏯"},
    "Mirissa":         {"lat": 5.9483,  "lon": 80.4716, "type": "Plage",      "rating": 9.1, "emoji": "🏖️"},
    "Yala":            {"lat": 6.3728,  "lon": 81.5168, "type": "Safari",     "rating": 9.3, "emoji": "🐆"},
    "Trincomalee":     {"lat": 8.5874,  "lon": 81.2152, "type": "Plage",      "rating": 8.7, "emoji": "🌊"},
    "Nuwara Eliya":    {"lat": 6.9497,  "lon": 80.7891, "type": "Nature",     "rating": 8.6, "emoji": "🍵"},
    "Anuradhapura":    {"lat": 8.3114,  "lon": 80.4037, "type": "Patrimoine", "rating": 8.9, "emoji": "🏛️"},
    "Arugam Bay":      {"lat": 6.8400,  "lon": 81.8400, "type": "Surf",       "rating": 9.0, "emoji": "🏄"},
}

# Villes avec région (ouest/est) pour coloration saisonnière
CITIES = {
    "Colombo":      {"lat": 6.9271,  "lon": 79.8612, "region": "west", "emoji": "🏙️", "desc": "Capitale économique"},
    "Galle":        {"lat": 6.0535,  "lon": 80.2210, "region": "west", "emoji": "🏛️", "desc": "Fort colonial UNESCO"},
    "Mirissa":      {"lat": 5.9483,  "lon": 80.4716, "region": "west", "emoji": "🐋", "desc": "Observation baleines"},
    "Kandy":        {"lat": 7.2906,  "lon": 80.6337, "region": "centre","emoji": "🏯", "desc": "Temple de la Dent"},
    "Nuwara Eliya": {"lat": 6.9497,  "lon": 80.7891, "region": "centre","emoji": "🍵", "desc": "Plantations de thé"},
    "Ella":         {"lat": 6.8667,  "lon": 81.0466, "region": "centre","emoji": "🌿", "desc": "Randonnée & nature"},
    "Sigiriya":     {"lat": 7.9570,  "lon": 80.7603, "region": "centre","emoji": "🏰", "desc": "Rocher forteresse UNESCO"},
    "Anuradhapura": {"lat": 8.3114,  "lon": 80.4037, "region": "north", "emoji": "🏛️", "desc": "Cité sacrée bouddhiste"},
    "Trincomalee":  {"lat": 8.5874,  "lon": 81.2152, "region": "east",  "emoji": "🌊", "desc": "Plages immaculées"},
    "Arugam Bay":   {"lat": 6.8400,  "lon": 81.8400, "region": "east",  "emoji": "🏄", "desc": "Spot de surf mondial"},
    "Yala":         {"lat": 6.3728,  "lon": 81.5168, "region": "east",  "emoji": "🐆", "desc": "Parc national léopards"},
    "Jaffna":       {"lat": 9.6615,  "lon": 80.0255, "region": "north", "emoji": "🌺", "desc": "Culture tamoule"},
    "Batticaloa":   {"lat": 7.7170,  "lon": 81.6924, "region": "east",  "emoji": "🦩", "desc": "Lagon & mangroves"},
    "Tangalle":     {"lat": 6.0210,  "lon": 80.7970, "region": "west",  "emoji": "🐢", "desc": "Tortues marines"},
    "Negombo":      {"lat": 7.2081,  "lon": 79.8358, "region": "west",  "emoji": "🐟", "desc": "Village de pêcheurs"},
}

# Données faune sauvage
WILDLIFE = [
    {
        "name": "Éléphant d'Asie", "emoji": "🐘",
        "scientific": "Elephas maximus",
        "habitat": "Forêts, savanes, zones humides",
        "temperament": "Généralement paisible, peut être dangereux si menacé ou en rut",
        "size": "2.5 – 3.5 m au garrot", "weight": "3 000 – 5 000 kg",
        "spots": ["Parc national de Minneriya", "Parc national de Kaudulla", "Udawalawe"],
        "best_month": "Juil – Oct (rassemblement de Minneriya)",
        "status": "En danger", "status_color": "#c0392b",
        "color": "#8B4513", "bg": "#f5e6d3",
        "fun_fact": "Le Sri Lanka abrite la plus haute densité d'éléphants d'Asie au monde."
    },
    {
        "name": "Léopard de Ceylan", "emoji": "🐆",
        "scientific": "Panthera pardus kotiya",
        "habitat": "Forêts denses, zones rocheuses, savanes arbustives",
        "temperament": "Solitaire, discret, chasseur nocturne mais visible en journée à Yala",
        "size": "1.0 – 1.6 m (corps)", "weight": "50 – 77 kg",
        "spots": ["Parc national de Yala (zone 1)", "Parc de Wilpattu", "Horton Plains"],
        "best_month": "Fév – Juil (saison sèche, végétation clairsemée)",
        "status": "Vulnérable", "status_color": "#e8a020",
        "color": "#d4a017", "bg": "#fff8e1",
        "fun_fact": "Yala possède la plus forte densité de léopards sauvages au monde."
    },
    {
        "name": "Baleine bleue", "emoji": "🐋",
        "scientific": "Balaenoptera musculus",
        "habitat": "Océan Indien profond, eaux côtières sud",
        "temperament": "Docile, curieux, migrateur majestueux",
        "size": "24 – 30 m", "weight": "100 000 – 150 000 kg",
        "spots": ["Mirissa (bateau)", "Trincomalee (bateau)", "Dondra Head"],
        "best_month": "Nov – Avr (Mirissa) | Avr – Sep (Trincomalee)",
        "status": "En danger", "status_color": "#c0392b",
        "color": "#1a5276", "bg": "#d6eaf8",
        "fun_fact": "Le Sri Lanka est l'un des meilleurs endroits au monde pour observer la baleine bleue."
    },
    {
        "name": "Paon bleu de Ceylan", "emoji": "🦚",
        "scientific": "Pavo cristatus",
        "habitat": "Forêts ouvertes, zones rurales, jardins",
        "temperament": "Timide mais habitué à l'homme dans les parcs nationaux",
        "size": "100 – 120 cm (+ 150 cm queue)", "weight": "4 – 6 kg",
        "spots": ["Yala", "Wilpattu", "Udawalawe", "Temples partout"],
        "best_month": "Toute l'année",
        "status": "Préoccupation mineure", "status_color": "#27ae60",
        "color": "#1a6b3c", "bg": "#d4efdf",
        "fun_fact": "Oiseau national du Sri Lanka, omniprésent dans les parcs et temples."
    },
    {
        "name": "Crocodile des marais", "emoji": "🐊",
        "scientific": "Crocodylus palustris",
        "habitat": "Rivières, lacs, mangroves, zones humides",
        "temperament": "Potentiellement dangereux — ne jamais s'approcher",
        "size": "3 – 4 m", "weight": "150 – 250 kg",
        "spots": ["Parc de Yala", "Bundala", "Maduganga (mangrove)"],
        "best_month": "Toute l'année",
        "status": "Vulnérable", "status_color": "#e8a020",
        "color": "#2d6a4f", "bg": "#d8f3dc",
        "fun_fact": "Présent au Sri Lanka depuis 65 millions d'années, peu changé depuis les dinosaures."
    },
    {
        "name": "Tortue de mer verte", "emoji": "🐢",
        "scientific": "Chelonia mydas",
        "habitat": "Mer ouverte, plages de ponte sableuses",
        "temperament": "Indifférente aux plongeurs, se laisse approcher doucement",
        "size": "80 – 120 cm", "weight": "70 – 190 kg",
        "spots": ["Hikkaduwa (snorkeling)", "Tangalle (ponte nocturne)", "Rekawa"],
        "best_month": "Jan – Mar (ponte) | Toute l'année (snorkeling)",
        "status": "En danger", "status_color": "#c0392b",
        "color": "#148f77", "bg": "#d1f2eb",
        "fun_fact": "Les femelles retournent toujours pondre sur la plage où elles sont nées."
    },
    {
        "name": "Ours lippu de Ceylan", "emoji": "🐻",
        "scientific": "Melursus ursinus inornatus",
        "habitat": "Forêts sèches, affleurements rocheux",
        "temperament": "Imprévisible et potentiellement agressif — espèce peu craintive",
        "size": "1.4 – 1.8 m", "weight": "80 – 140 kg",
        "spots": ["Parc de Yala", "Parc de Wilpattu", "Wasgamuwa"],
        "best_month": "Juin – Sep",
        "status": "Vulnérable", "status_color": "#e8a020",
        "color": "#6e2c00", "bg": "#fce8d5",
        "fun_fact": "Sous-espèce endémique du Sri Lanka, reconnaissable à son museau blanc distinctif."
    },
    {
        "name": "Dauphin fileur", "emoji": "🐬",
        "scientific": "Stenella longirostris",
        "habitat": "Eaux côtières chaudes, océan ouvert",
        "temperament": "Très joueur, adore surfer sur la proue des bateaux",
        "size": "1.3 – 2.0 m", "weight": "50 – 80 kg",
        "spots": ["Mirissa (sortie bateau tôt matin)", "Trincomalee", "Kalpitiya"],
        "best_month": "Nov – Avr",
        "status": "Préoccupation mineure", "status_color": "#27ae60",
        "color": "#2471a3", "bg": "#d6eaf8",
        "fun_fact": "Des milliers de dauphins fileurs voyagent en bancs au large de Mirissa chaque matin."
    },
]


COLORS = {
    "Patrimoine": "#c0392b", "Ville": "#8e44ad", "Nature": "#27ae60",
    "Culture": "#e8a020",   "Plage": "#2980b9",  "Safari": "#d35400",
    "Surf": "#16a085",
}

STATS = [
    {"icon": "👥", "value": "22M",      "label": "Population",       "color": "#1a6b3c"},
    {"icon": "📐", "value": "65 610",   "label": "km² superficie",   "color": "#e8a020"},
    {"icon": "💰", "value": "84 Mds$",  "label": "PIB (USD)",        "color": "#c0392b"},
    {"icon": "✈️", "value": "2.1M",     "label": "Touristes/an",     "color": "#8e44ad"},
    {"icon": "🏖️", "value": "1 340",   "label": "km de côtes",      "color": "#2980b9"},
    {"icon": "🐘", "value": "5 879",    "label": "Éléphants sauvages","color": "#27ae60"},
    {"icon": "🍵", "value": "300k t",   "label": "Production de thé","color": "#d35400"},
    {"icon": "🏛️", "value": "8",        "label": "Sites UNESCO",     "color": "#16a085"},
]

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌴 Navigation")
    st.markdown("---")
    page = st.selectbox("", ["🏠 Vue générale", "🌤️ Météo & Saisons", "🗺️ Carte interactive", "🌈 Carte saisonnière", "🏙️ Villes & Saisons", "🐘 Faune sauvage", "📊 Tourisme"])
    st.markdown("---")
    st.markdown("### 📅 Mois de voyage")
    month_idx = st.slider("", 0, 11, 0, format="")
    selected_month = MONTHS[month_idx]
    st.markdown(f"**Mois sélectionné : {selected_month}**")
    st.markdown("---")
    st.markdown("### 🌊 Côte préférée")
    coast = st.radio("", ["Côte Ouest", "Côte Est", "Les deux"])
    st.markdown("---")
    st.markdown("*Dashboard Sri Lanka • 2024*")

# ─── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🇱🇰 Sri Lanka Explorer</h1>
  <p>Votre guide interactif pour planifier le voyage parfait dans la Perle de l'Océan Indien</p>
</div>
""", unsafe_allow_html=True)

# ─── PAGE : VUE GÉNÉRALE ───────────────────────────────────────────────────────
if "Vue générale" in page:

    st.markdown('<div class="section-title">Chiffres clés</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, stat in enumerate(STATS[:4]):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{stat['color']}">
              <div class="kpi-icon">{stat['icon']}</div>
              <div class="kpi-value" style="color:{stat['color']}">{stat['value']}</div>
              <div class="kpi-label">{stat['label']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cols2 = st.columns(4)
    for i, stat in enumerate(STATS[4:]):
        with cols2[i]:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{stat['color']}">
              <div class="kpi-icon">{stat['icon']}</div>
              <div class="kpi-value" style="color:{stat['color']}">{stat['value']}</div>
              <div class="kpi-label">{stat['label']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Recommandation pour ' + selected_month + '</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    season_w = SEASONS_WEST[month_idx]
    season_e = SEASONS_EAST[month_idx]
    temp_w   = TEMP_WEST[month_idx]
    temp_e   = TEMP_EAST[month_idx]
    rain_w   = RAIN_WEST[month_idx]
    rain_e   = RAIN_EAST[month_idx]

    with col_a:
        color_w = "#27ae60" if "Haute" in season_w else ("#e8a020" if "Inter" in season_w else "#c0392b")
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border-left:6px solid {color_w}">
          <h3 style="margin:0 0 12px 0">🌅 Côte Ouest</h3>
          <p style="font-size:1.4rem;margin:4px 0">{season_w}</p>
          <p>🌡️ Température : <b>{temp_w}°C</b></p>
          <p>🌧️ Précipitations : <b>{rain_w} mm</b></p>
          <p>{'✅ Idéale pour la baignade' if 'Haute' in season_w else ('⚠️ Conditions variables' if 'Inter' in season_w else '❌ Eviter la côte ouest')}</p>
        </div>""", unsafe_allow_html=True)

    with col_b:
        color_e = "#27ae60" if "Haute" in season_e else ("#e8a020" if "Inter" in season_e else "#c0392b")
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border-left:6px solid {color_e}">
          <h3 style="margin:0 0 12px 0">🌄 Côte Est</h3>
          <p style="font-size:1.4rem;margin:4px 0">{season_e}</p>
          <p>🌡️ Température : <b>{temp_e}°C</b></p>
          <p>🌧️ Précipitations : <b>{rain_e} mm</b></p>
          <p>{'✅ Idéale pour la baignade' if 'Haute' in season_e else ('⚠️ Conditions variables' if 'Inter' in season_e else '❌ Eviter la côte est')}</p>
        </div>""", unsafe_allow_html=True)

# ─── PAGE : MÉTÉO & SAISONS ────────────────────────────────────────────────────
elif "Météo" in page:

    st.markdown('<div class="section-title">Températures & Précipitations</div>', unsafe_allow_html=True)

    temps  = TEMP_WEST  if coast == "Côte Ouest" else (TEMP_EAST  if coast == "Côte Est" else TEMP_WEST)
    rains  = RAIN_WEST  if coast == "Côte Ouest" else (RAIN_EAST  if coast == "Côte Est" else RAIN_WEST)
    label  = coast if coast != "Les deux" else "Côte Ouest"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=MONTHS, y=rains, name="Précipitations (mm)",
        marker_color=["#c0392b" if r > 250 else ("#e8a020" if r > 150 else "#27ae60") for r in rains],
        yaxis="y2", opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS, y=temps, name="Température (°C)",
        line=dict(color="#1a3a2a", width=3), mode="lines+markers",
        marker=dict(size=8, color="#e8a020")
    ))
    if coast == "Les deux":
        fig.add_trace(go.Scatter(
            x=MONTHS, y=TEMP_EAST, name="Température Est (°C)",
            line=dict(color="#2980b9", width=3, dash="dash"), mode="lines+markers",
            marker=dict(size=8, color="#2980b9")
        ))

    fig.update_layout(
        paper_bgcolor="#FFF8F0", plot_bgcolor="white",
        font=dict(family="DM Sans"), height=420,
        yaxis=dict(title="Température (°C)", range=[20, 35], color="#1a3a2a"),
        yaxis2=dict(title="Précipitations (mm)", overlaying="y", side="right", color="#888"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=30),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Calendrier des saisons</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    def season_color(s):
        if "Haute" in s: return "#27ae60"
        if "Inter" in s: return "#e8a020"
        return "#c0392b"

    with col1:
        st.markdown("**🌅 Côte Ouest (Colombo, Mirissa, Galle)**")
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"
        for m, s in zip(MONTHS, SEASONS_WEST):
            bg = season_color(s)
            html += f"<div style='background:{bg};color:white;padding:8px 12px;border-radius:10px;font-size:0.85rem;font-weight:600'>{m}<br><span style='font-size:0.75rem'>{s}</span></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with col2:
        st.markdown("**🌄 Côte Est (Trincomalee, Arugam Bay)**")
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"
        for m, s in zip(MONTHS, SEASONS_EAST):
            bg = season_color(s)
            html += f"<div style='background:{bg};color:white;padding:8px 12px;border-radius:10px;font-size:0.85rem;font-weight:600'>{m}<br><span style='font-size:0.75rem'>{s}</span></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_leg1, col_leg2, col_leg3, _ = st.columns([1,1,1,3])
    with col_leg1: st.markdown("🟢 **Haute saison** — Idéal")
    with col_leg2: st.markdown("🟡 **Inter-saison** — Variable")
    with col_leg3: st.markdown("🔴 **Mousson** — Déconseillé")

# ─── PAGE : CARTE INTERACTIVE ──────────────────────────────────────────────────
elif "Carte" in page:

    st.markdown('<div class="section-title">Destinations incontournables</div>', unsafe_allow_html=True)

    type_filter = st.multiselect(
        "Filtrer par type :",
        options=list(COLORS.keys()),
        default=list(COLORS.keys())
    )

    col_map, col_info = st.columns([2, 1])

    with col_map:
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=7,
                       tiles="CartoDB positron")

        for name, info in DESTINATIONS.items():
            if info["type"] not in type_filter:
                continue
            color = COLORS[info["type"]]
            folium.CircleMarker(
                location=[info["lat"], info["lon"]],
                radius=12,
                color=color, fill=True, fill_color=color, fill_opacity=0.8,
                popup=folium.Popup(f"""
                  <div style='font-family:sans-serif;width:160px'>
                    <b style='font-size:1rem'>{info['emoji']} {name}</b><br>
                    <span style='color:{color};font-weight:600'>{info['type']}</span><br>
                    ⭐ Note : {info['rating']}/10
                  </div>""", max_width=200),
                tooltip=f"{info['emoji']} {name}"
            ).add_to(m)

        st_folium(m, width=700, height=520)

    with col_info:
        st.markdown("**📍 Destinations filtrées**")
        for name, info in DESTINATIONS.items():
            if info["type"] not in type_filter:
                continue
            color = COLORS[info["type"]]
            st.markdown(f"""
            <div style='background:white;border-radius:12px;padding:12px 14px;margin-bottom:8px;
                        border-left:4px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.06)'>
              <b>{info['emoji']} {name}</b><br>
              <span style='color:{color};font-size:0.8rem'>{info['type']}</span>
              <span style='float:right;font-weight:700'>⭐ {info['rating']}</span>
            </div>""", unsafe_allow_html=True)

# ─── PAGE : CARTE SAISONNIÈRE ─────────────────────────────────────────────────
elif "saisonnière" in page:

    st.markdown('<div class="section-title">Carte saisonnière interactive 🌈</div>', unsafe_allow_html=True)
    st.markdown("Déplacez le curseur pour voir les meilleures zones selon le mois choisi.")

    # Slider mois dédié à cette page
    map_month = st.slider("📅 Mois", 0, 11, month_idx,
                          format="", key="map_slider")
    month_label = MONTHS[map_month]

    # Saison par région pour ce mois
    sw = SEASONS_WEST[map_month]
    se = SEASONS_EAST[map_month]
    sc = SEASONS_WEST[map_month]  # Centre suit globalement l'ouest
    sn = SEASONS_WEST[map_month]  # Nord similaire

    def region_color(season):
        if "Haute"  in season: return ("#1a6b3c", "#d4f5e0", "✅ Haute saison")
        if "Inter"  in season: return ("#b8860b", "#fff3cd", "⚠️ Inter-saison")
        return                         ("#8B0000", "#fde8e8", "❌ Mousson")

    col_nord_c,   col_nord_fill,  col_nord_lbl  = region_color(sn)
    col_ouest_c,  col_ouest_fill, col_ouest_lbl = region_color(sw)
    col_est_c,    col_est_fill,   col_est_lbl   = region_color(se)
    col_centre_c, col_centre_fill,col_centre_lbl= region_color(sc)
    col_sud_c,    col_sud_fill,   col_sud_lbl   = region_color(sw)  # Sud suit l'ouest

    # SVG carte stylisée du Sri Lanka avec régions colorées
    svg = f"""
    <div style="display:flex;gap:30px;align-items:flex-start;justify-content:center;flex-wrap:wrap;margin-top:10px">
      <div>
        <svg width="320" height="480" viewBox="0 0 320 480" xmlns="http://www.w3.org/2000/svg"
             style="filter:drop-shadow(0 8px 24px rgba(0,0,0,0.18))">

          <!-- Océan background -->
          <rect width="320" height="480" fill="#a8d4e8" rx="16"/>

          <!-- Vagues décoratives -->
          <path d="M0 30 Q80 20 160 30 Q240 40 320 30" fill="none" stroke="#7bbfd6" stroke-width="1.5" opacity="0.6"/>
          <path d="M0 450 Q80 440 160 450 Q240 460 320 450" fill="none" stroke="#7bbfd6" stroke-width="1.5" opacity="0.6"/>

          <!-- === RÉGIONS DU SRI LANKA === -->

          <!-- NORD (Jaffna, Vanni) -->
          <path d="M130 45 L155 38 L185 42 L200 55 L195 75 L185 88 L170 92
                   L155 90 L140 85 L125 75 L120 60 Z"
                fill="{col_nord_fill}" stroke="{col_nord_c}" stroke-width="2.5" rx="4"/>
          <text x="160" y="70" text-anchor="middle" font-size="11" font-weight="700"
                fill="{col_nord_c}" font-family="DM Sans,sans-serif">NORD</text>

          <!-- NORD-OUEST (Puttalam, Mannar) -->
          <path d="M100 90 L125 75 L140 85 L138 105 L130 125 L118 140
                   L105 145 L95 135 L90 118 L92 100 Z"
                fill="{col_ouest_fill}" stroke="{col_ouest_c}" stroke-width="2.5"/>
          <text x="112" y="116" text-anchor="middle" font-size="9" font-weight="700"
                fill="{col_ouest_c}" font-family="DM Sans,sans-serif">N-OUEST</text>

          <!-- NORD-EST (Trincomalee, Batticaloa) -->
          <path d="M185 88 L205 80 L225 90 L235 110 L230 135 L220 155
                   L205 162 L192 158 L183 145 L180 125 L182 105 Z"
                fill="{col_est_fill}" stroke="{col_est_c}" stroke-width="2.5"/>
          <text x="208" y="125" text-anchor="middle" font-size="9" font-weight="700"
                fill="{col_est_c}" font-family="DM Sans,sans-serif">N-EST</text>

          <!-- CÔTE OUEST (Colombo, Negombo, Galle) -->
          <path d="M90 140 L105 145 L118 140 L125 158 L122 180 L115 205
                   L108 230 L100 255 L95 275 L90 295 L85 270 L80 245
                   L78 220 L80 195 L82 170 L85 155 Z"
                fill="{col_ouest_fill}" stroke="{col_ouest_c}" stroke-width="2.5"/>
          <text x="97" y="220" text-anchor="middle" font-size="9" font-weight="700"
                fill="{col_ouest_c}" font-family="DM Sans,sans-serif" transform="rotate(-5,97,220)">OUEST</text>

          <!-- CENTRE (Kandy, Nuwara Eliya, collines) -->
          <path d="M138 105 L155 90 L170 92 L185 88 L182 105 L183 145
                   L180 125 L192 158 L188 175 L175 185 L158 182 L145 178
                   L132 165 L125 158 L118 140 L130 125 Z"
                fill="{col_centre_fill}" stroke="{col_centre_c}" stroke-width="2.5"/>
          <text x="158" y="140" text-anchor="middle" font-size="10" font-weight="700"
                fill="{col_centre_c}" font-family="DM Sans,sans-serif">CENTRE</text>

          <!-- EST (Arugam Bay, Ampara) -->
          <path d="M205 162 L220 155 L235 165 L238 190 L232 215 L222 238
                   L210 255 L198 260 L188 252 L182 235 L180 210 L183 188
                   L188 175 L192 158 Z"
                fill="{col_est_fill}" stroke="{col_est_c}" stroke-width="2.5"/>
          <text x="213" y="210" text-anchor="middle" font-size="10" font-weight="700"
                fill="{col_est_c}" font-family="DM Sans,sans-serif">EST</text>

          <!-- SUD (Galle, Mirissa, Tangalle, Yala) -->
          <path d="M100 275 L108 295 L118 315 L130 332 L145 345 L158 352
                   L172 350 L185 342 L196 330 L205 315 L208 295 L205 275
                   L198 260 L188 252 L175 255 L160 258 L145 258 L132 262
                   L118 268 L108 270 Z"
                fill="{col_sud_fill}" stroke="{col_sud_c}" stroke-width="2.5"/>
          <text x="155" y="308" text-anchor="middle" font-size="11" font-weight="700"
                fill="{col_sud_c}" font-family="DM Sans,sans-serif">SUD</text>

          <!-- Pointe sud -->
          <path d="M145 345 L158 352 L172 350 L160 370 Z"
                fill="{col_sud_fill}" stroke="{col_sud_c}" stroke-width="2"/>

          <!-- Titre mois -->
          <rect x="80" y="390" width="160" height="36" rx="18"
                fill="white" opacity="0.92" stroke="#ddd" stroke-width="1"/>
          <text x="160" y="414" text-anchor="middle" font-size="15" font-weight="900"
                fill="#1a3a2a" font-family="Playfair Display,serif">{month_label}</text>
        </svg>
      </div>

      <!-- Légende et détails par région -->
      <div style="min-width:260px;max-width:340px">
        <div style="background:white;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,0.08);margin-bottom:16px">
          <p style="font-weight:700;font-size:1rem;color:#1a3a2a;margin:0 0 14px 0">📍 Détail par région — {month_label}</p>

          <div style="background:{col_nord_fill};border-left:5px solid {col_nord_c};border-radius:10px;padding:10px 14px;margin-bottom:10px">
            <b style="color:{col_nord_c}">🏔️ Nord (Jaffna)</b><br>
            <span style="font-size:0.85rem;color:#444">{col_nord_lbl}</span>
          </div>
          <div style="background:{col_ouest_fill};border-left:5px solid {col_ouest_c};border-radius:10px;padding:10px 14px;margin-bottom:10px">
            <b style="color:{col_ouest_c}">🌅 Côte Ouest (Colombo, Galle)</b><br>
            <span style="font-size:0.85rem;color:#444">{col_ouest_lbl}</span>
          </div>
          <div style="background:{col_est_fill};border-left:5px solid {col_est_c};border-radius:10px;padding:10px 14px;margin-bottom:10px">
            <b style="color:{col_est_c}">🌄 Côte Est (Trinco, Arugam Bay)</b><br>
            <span style="font-size:0.85rem;color:#444">{col_est_lbl}</span>
          </div>
          <div style="background:{col_centre_fill};border-left:5px solid {col_centre_c};border-radius:10px;padding:10px 14px;margin-bottom:10px">
            <b style="color:{col_centre_c}">🍵 Centre (Kandy, Ella, Nuwara Eliya)</b><br>
            <span style="font-size:0.85rem;color:#444">{col_centre_lbl}</span>
          </div>
          <div style="background:{col_sud_fill};border-left:5px solid {col_sud_c};border-radius:10px;padding:10px 14px">
            <b style="color:{col_sud_c}">🐆 Sud (Mirissa, Yala, Tangalle)</b><br>
            <span style="font-size:0.85rem;color:#444">{col_sud_lbl}</span>
          </div>
        </div>

        <!-- Légende couleurs -->
        <div style="background:white;border-radius:16px;padding:16px 20px;box-shadow:0 4px 20px rgba(0,0,0,0.08)">
          <p style="font-weight:700;color:#1a3a2a;margin:0 0 10px 0">Légende</p>
          <div style="display:flex;flex-direction:column;gap:8px">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:22px;height:22px;background:#1a6b3c;border-radius:5px"></div>
              <span style="font-size:0.9rem"><b>Haute saison</b> — Idéale, soleil garanti</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:22px;height:22px;background:#b8860b;border-radius:5px"></div>
              <span style="font-size:0.9rem"><b>Inter-saison</b> — Conditions variables</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:22px;height:22px;background:#8B0000;border-radius:5px"></div>
              <span style="font-size:0.9rem"><b>Mousson</b> — Pluies importantes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)

    # Timeline visuelle en bas
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:1.1rem">Calendrier annuel rapide</div>', unsafe_allow_html=True)

    col_w, col_e = st.columns(2)
    with col_w:
        st.markdown("**🌅 Côte Ouest & Centre**")
        html = "<div style='display:flex;gap:4px;flex-wrap:wrap'>"
        for i, (m, s) in enumerate(zip(MONTHS, SEASONS_WEST)):
            bg = "#1a6b3c" if "Haute" in s else ("#b8860b" if "Inter" in s else "#8B0000")
            border = "3px solid #1a3a2a" if i == map_month else "3px solid transparent"
            html += f"<div style='background:{bg};color:white;padding:6px 10px;border-radius:8px;font-size:0.8rem;font-weight:700;border:{border};min-width:38px;text-align:center'>{m}</div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with col_e:
        st.markdown("**🌄 Côte Est**")
        html = "<div style='display:flex;gap:4px;flex-wrap:wrap'>"
        for i, (m, s) in enumerate(zip(MONTHS, SEASONS_EAST)):
            bg = "#1a6b3c" if "Haute" in s else ("#b8860b" if "Inter" in s else "#8B0000")
            border = "3px solid #1a3a2a" if i == map_month else "3px solid transparent"
            html += f"<div style='background:{bg};color:white;padding:6px 10px;border-radius:8px;font-size:0.8rem;font-weight:700;border:{border};min-width:38px;text-align:center'>{m}</div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

# ─── PAGE : TOURISME ───────────────────────────────────────────────────────────
elif "Tourisme" in page:

    st.markdown('<div class="section-title">Affluence touristique mensuelle</div>', unsafe_allow_html=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=MONTHS, y=TOURISTS,
        marker_color=["#c0392b" if t >= 270 else ("#e8a020" if t >= 200 else "#27ae60") for t in TOURISTS],
        text=[f"{t}k" for t in TOURISTS], textposition="outside",
        hovertemplate="<b>%{x}</b><br>Touristes : %{y}k<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="#FFF8F0", plot_bgcolor="white",
        font=dict(family="DM Sans"), height=380,
        yaxis=dict(title="Milliers d'arrivées", showgrid=True, gridcolor="#f0f0f0"),
        xaxis=dict(showgrid=False),
        margin=dict(t=20, b=20),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Origine des touristes</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        origins = {"Inde": 22, "Chine": 14, "UK": 9, "Allemagne": 7,
                   "Australie": 6, "France": 5, "Maldives": 4, "Autres": 33}
        fig3 = go.Figure(go.Pie(
            labels=list(origins.keys()),
            values=list(origins.values()),
            hole=0.45,
            marker_colors=["#1a6b3c","#e8a020","#c0392b","#2980b9",
                           "#8e44ad","#27ae60","#d35400","#95a5a6"]
        ))
        fig3.update_layout(
            paper_bgcolor="#FFF8F0", font=dict(family="DM Sans"),
            height=350, margin=dict(t=20, b=20),
            annotations=[dict(text="🌍", x=0.5, y=0.5, font_size=30, showarrow=False)]
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("**💡 Conseils par niveau d'affluence**")
        tips = [
            ("🔴 Haute saison (Déc–Mar)", "#c0392b",
             "Réservez hôtels et transports 2–3 mois à l'avance. Tarifs majorés de 30 à 50%."),
            ("🟡 Moyenne saison (Sep–Nov)", "#e8a020",
             "Bon compromis prix/affluence. Quelques pluies possibles en soirée."),
            ("🟢 Basse saison (Mai–Aoû)", "#27ae60",
             "Tarifs attractifs, moins de monde. Idéal côte Est. Mousson côte Ouest."),
        ]
        for title, color, text in tips:
            st.markdown(f"""
            <div style='background:white;border-radius:14px;padding:16px 18px;margin-bottom:12px;
                        border-left:5px solid {color};box-shadow:0 2px 10px rgba(0,0,0,0.07)'>
              <b style='color:{color}'>{title}</b><br>
              <span style='color:#555;font-size:0.9rem'>{text}</span>
            </div>""", unsafe_allow_html=True)


# ─── PAGE : VILLES & SAISONS ──────────────────────────────────────────────────
elif "Villes" in page:

    st.markdown('<div class="section-title">Carte des villes par saison 🏙️</div>', unsafe_allow_html=True)
    st.markdown("Les marqueurs sont **verts** si la région est en haute saison, **orange** en inter-saison, **rouges** en mousson.")

    city_month = st.slider("📅 Mois", 0, 11, month_idx, format="", key="city_slider")
    city_month_label = MONTHS[city_month]

    def get_season(region, m):
        if region == "west" or region == "centre" or region == "north":
            return SEASONS_WEST[m]
        else:
            return SEASONS_EAST[m]

    def season_marker_color(season):
        if "Haute"  in season: return "#1a6b3c", "green",  "✅ Haute saison"
        if "Inter"  in season: return "#b8860b", "orange", "⚠️ Inter-saison"
        return                         "#8B0000", "red",    "❌ Mousson"

    m_map = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB positron")

    for city, info in CITIES.items():
        season = get_season(info["region"], city_month)
        hex_color, marker_color, season_label = season_marker_color(season)

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=13,
            color=hex_color, fill=True, fill_color=hex_color, fill_opacity=0.85,
            popup=folium.Popup(f"""
              <div style='font-family:sans-serif;width:180px;padding:4px'>
                <b style='font-size:1rem'>{info['emoji']} {city}</b><br>
                <span style='color:#555;font-size:0.85rem'>{info['desc']}</span><br><br>
                <span style='color:{hex_color};font-weight:700'>{season_label}</span><br>
                <span style='color:#888;font-size:0.8rem'>{city_month_label}</span>
              </div>""", max_width=220),
            tooltip=f"{info['emoji']} {city} — {season_label}"
        ).add_to(m_map)

        # Label ville
        folium.Marker(
            location=[info["lat"] + 0.08, info["lon"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:10px;font-weight:700;color:{hex_color};white-space:nowrap;text-shadow:1px 1px 2px white,-1px -1px 2px white">{city}</div>',
                icon_size=(120, 20), icon_anchor=(0, 0)
            )
        ).add_to(m_map)

    col_map2, col_legend = st.columns([2, 1])
    with col_map2:
        st_folium(m_map, width=700, height=540)

    with col_legend:
        st.markdown(f"**📅 Mois : {city_month_label}**")
        st.markdown("---")
        for city, info in CITIES.items():
            season = get_season(info["region"], city_month)
            hex_c, _, season_lbl = season_marker_color(season)
            st.markdown(f"""
            <div style='background:white;border-radius:10px;padding:10px 12px;margin-bottom:6px;
                        border-left:4px solid {hex_c};box-shadow:0 2px 6px rgba(0,0,0,0.06)'>
              <b style='font-size:0.9rem'>{info['emoji']} {city}</b><br>
              <span style='color:{hex_c};font-size:0.78rem;font-weight:600'>{season_lbl}</span>
            </div>""", unsafe_allow_html=True)

# ─── PAGE : FAUNE SAUVAGE ─────────────────────────────────────────────────────
elif "Faune" in page:

    st.markdown('<div class="section-title">Faune sauvage du Sri Lanka 🐘</div>', unsafe_allow_html=True)
    st.markdown("Découvrez les animaux emblématiques de l'île, leurs habitats et où les observer.")

    # Filtre par statut
    status_filter = st.multiselect(
        "Filtrer par statut de conservation :",
        ["En danger", "Vulnérable", "Préoccupation mineure"],
        default=["En danger", "Vulnérable", "Préoccupation mineure"]
    )

    filtered = [a for a in WILDLIFE if a["status"] in status_filter]

    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(filtered): break
            animal = filtered[i + j]
            with col:
                st.markdown(f"""
                <div style='background:white;border-radius:20px;padding:24px;margin-bottom:20px;
                            box-shadow:0 6px 24px rgba(0,0,0,0.08);border-top:6px solid {animal["color"]}'>

                  <!-- Header -->
                  <div style='display:flex;align-items:center;gap:14px;margin-bottom:16px'>
                    <div style='font-size:3rem;line-height:1'>{animal["emoji"]}</div>
                    <div>
                      <div style='font-family:Playfair Display,serif;font-size:1.25rem;font-weight:900;color:#1a3a2a'>{animal["name"]}</div>
                      <div style='color:#888;font-style:italic;font-size:0.85rem'>{animal["scientific"]}</div>
                      <span style='background:{animal["status_color"]};color:white;padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:700'>{animal["status"]}</span>
                    </div>
                  </div>

                  <!-- Stats grid -->
                  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px'>
                    <div style='background:{animal["bg"]};border-radius:10px;padding:10px 12px'>
                      <div style='font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:1px'>Taille</div>
                      <div style='font-weight:700;color:{animal["color"]};font-size:0.9rem'>{animal["size"]}</div>
                    </div>
                    <div style='background:{animal["bg"]};border-radius:10px;padding:10px 12px'>
                      <div style='font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:1px'>Poids</div>
                      <div style='font-weight:700;color:{animal["color"]};font-size:0.9rem'>{animal["weight"]}</div>
                    </div>
                  </div>

                  <!-- Infos -->
                  <div style='margin-bottom:10px'>
                    <div style='font-size:0.8rem;font-weight:700;color:#1a3a2a;margin-bottom:3px'>🌿 Habitat</div>
                    <div style='font-size:0.85rem;color:#444'>{animal["habitat"]}</div>
                  </div>
                  <div style='margin-bottom:10px'>
                    <div style='font-size:0.8rem;font-weight:700;color:#1a3a2a;margin-bottom:3px'>🧠 Tempérament</div>
                    <div style='font-size:0.85rem;color:#444'>{animal["temperament"]}</div>
                  </div>
                  <div style='margin-bottom:10px'>
                    <div style='font-size:0.8rem;font-weight:700;color:#1a3a2a;margin-bottom:3px'>📍 Où les voir</div>
                    <div style='font-size:0.85rem;color:#444'>{"  •  ".join(animal["spots"])}</div>
                  </div>
                  <div style='margin-bottom:14px'>
                    <div style='font-size:0.8rem;font-weight:700;color:#1a3a2a;margin-bottom:3px'>📅 Meilleure période</div>
                    <div style='font-size:0.85rem;color:{animal["color"]};font-weight:600'>{animal["best_month"]}</div>
                  </div>

                  <!-- Fun fact -->
                  <div style='background:{animal["bg"]};border-radius:12px;padding:12px 14px;border-left:4px solid {animal["color"]}'>
                    <span style='font-size:0.8rem;font-weight:700;color:{animal["color"]}'>💡 Le saviez-vous ?</span><br>
                    <span style='font-size:0.83rem;color:#444'>{animal["fun_fact"]}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)


st.markdown("""
<div class="footer">
  🇱🇰 Sri Lanka Explorer Dashboard • Données indicatives 2024 • Fait avec ❤️ et Streamlit
</div>
""", unsafe_allow_html=True)
