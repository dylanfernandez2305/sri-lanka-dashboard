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

  /* Flèche animée pointant vers le selectbox */
  [data-testid="stSidebar"] .stSelectbox {
    position: relative;
  }
  [data-testid="stSidebar"] .stSelectbox::before {
    content: "▼ Clique ici pour choisir une section";
    display: block;
    color: #f0b80a !important;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-align: center;
    animation: pulse-hint 1.5s ease-in-out infinite;
    margin-bottom: 4px;
  }
  @keyframes pulse-hint {
    0%   { opacity: 1;   transform: translateY(0); }
    50%  { opacity: 0.4; transform: translateY(3px); }
    100% { opacity: 1;   transform: translateY(0); }
  }

  /* Highlight the selectbox border */
  [data-testid="stSidebar"] .stSelectbox > div > div {
    border: 2px solid #f0b80a !important;
    border-radius: 10px !important;
  }

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



# ─── DONNÉES FIXES (numériques) ────────────────────────────────────────────────
TEMP_WEST  = [27,28,29,30,30,29,28,28,28,27,27,27]
RAIN_WEST  = [89,69,147,231,371,224,135,109,160,348,315,147]
TEMP_EAST  = [26,27,28,30,31,31,30,30,29,27,26,26]
RAIN_EAST  = [230,120,60,40,55,40,65,110,180,280,390,310]
TOURISTS   = [280,260,290,220,180,150,160,170,190,210,250,300]

COLORS = {
    "Patrimoine":"#c0392b","Stad":"#8e44ad","Natuur":"#27ae60",
    "Cultuur":"#e8a020","Strand":"#2980b9","Safari":"#d35400","Surf":"#16a085",
}

# ─── LANG : tout le contenu FR + NL ───────────────────────────────────────────
WILDLIFE_FR = [
    # ── MAMMIFÈRES ──────────────────────────────────────────────────────────────
    {"category":"Mammifères terrestres","name":"Éléphant d'Asie","emoji":"🐘","scientific":"Elephas maximus",
     "habitat":"Forêts, savanes, zones humides",
     "temperament":"Généralement paisible, dangereux si menacé ou en rut",
     "size":"2.5–3.5 m au garrot","weight":"3 000–5 000 kg",
     "spots":["Minneriya","Kaudulla","Udawalawe"],
     "best_month":"Juil–Oct (rassemblement Minneriya)",
     "status":"En danger","status_color":"#c0392b","color":"#8B4513","bg":"#f5e6d3",
     "fun_fact":"Le Sri Lanka abrite la plus haute densité d'éléphants d'Asie au monde."},
    {"category":"Mammifères terrestres","name":"Ours lippu de Ceylan","emoji":"🐻","scientific":"Melursus ursinus inornatus",
     "habitat":"Forêts sèches, affleurements rocheux",
     "temperament":"Imprévisible et potentiellement agressif — peu craintif",
     "size":"1.4–1.8 m","weight":"80–140 kg",
     "spots":["Yala","Wilpattu","Wasgamuwa"],
     "best_month":"Juin–Sep",
     "status":"Vulnérable","status_color":"#e8a020","color":"#6e2c00","bg":"#fce8d5",
     "fun_fact":"Sous-espèce endémique du Sri Lanka, reconnaissable à son museau blanc distinctif."},
    {"category":"Poissons & Vie marine","name":"Dauphin fileur","emoji":"🐬","scientific":"Stenella longirostris",
     "habitat":"Eaux côtières chaudes, océan ouvert",
     "temperament":"Très joueur, adore surfer sur la proue des bateaux",
     "size":"1.3–2.0 m","weight":"50–80 kg",
     "spots":["Mirissa (tôt matin)","Trincomalee","Kalpitiya"],
     "best_month":"Nov–Avr",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#2471a3","bg":"#d6eaf8",
     "fun_fact":"Des milliers de dauphins fileurs voyagent en bancs au large de Mirissa chaque matin."},
    {"category":"Poissons & Vie marine","name":"Baleine bleue","emoji":"🐋","scientific":"Balaenoptera musculus",
     "habitat":"Océan Indien profond, eaux côtières sud",
     "temperament":"Docile, curieux, migrateur majestueux",
     "size":"24–30 m","weight":"100 000–150 000 kg",
     "spots":["Mirissa (bateau)","Trincomalee (bateau)","Dondra Head"],
     "best_month":"Nov–Avr (Mirissa) | Avr–Sep (Trinco)",
     "status":"En danger","status_color":"#c0392b","color":"#1a5276","bg":"#d6eaf8",
     "fun_fact":"Le Sri Lanka est l'un des meilleurs endroits au monde pour observer la baleine bleue."},
    {"category":"Poissons & Vie marine","name":"Dauphin à bosse indo-pacifique","emoji":"🐳","scientific":"Sousa chinensis",
     "habitat":"Eaux côtières peu profondes, estuaires",
     "temperament":"Curieux, se mêle parfois aux dauphins fileurs",
     "size":"2.0–2.8 m","weight":"150–280 kg",
     "spots":["Kalpitiya","Trincomalee","Côte ouest"],
     "best_month":"Nov–Avr",
     "status":"Vulnérable","status_color":"#e8a020","color":"#2980b9","bg":"#d6eaf8",
     "fun_fact":"Reconnaissable à sa bosse dorsale caractéristique et sa teinte rose-gris."},
    {"category":"Mammifères terrestres","name":"Cerf axis (Axis deer)","emoji":"🦌","scientific":"Axis axis",
     "habitat":"Forêts ouvertes, prairies, lisières de parc",
     "temperament":"Timide, alerte — principal rôle de proie du léopard",
     "size":"70–95 cm au garrot","weight":"30–75 kg",
     "spots":["Yala","Wilpattu","Fort Frederick (Trinco)"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#c8860a","bg":"#fef9e7",
     "fun_fact":"Présent en si grand nombre à Yala qu'il est la proie favorite du léopard de Ceylan."},
    {"category":"Mammifères terrestres","name":"Buffle d'eau","emoji":"🐃","scientific":"Bubalus bubalis",
     "habitat":"Zones humides, rizières, prairies inondées",
     "temperament":"Puissant et imprévisible — respecter les distances",
     "size":"1.5–1.9 m au garrot","weight":"700–1 200 kg",
     "spots":["Udawalawe","Bundala","Minneriya"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#555","bg":"#f0f0f0",
     "fun_fact":"Les buffles sauvages du Sri Lanka sont parmi les plus grands d'Asie."},
    {"category":"Mammifères terrestres","name":"Sambhar","emoji":"🦌","scientific":"Rusa unicolor",
     "habitat":"Forêts denses, montagnes, zones humides",
     "temperament":"Discret et nocturne, fuit à l'approche",
     "size":"1.2–1.6 m au garrot","weight":"150–320 kg",
     "spots":["Horton Plains","Knuckles Range","Sinharaja"],
     "best_month":"Toute l'année",
     "status":"Vulnérable","status_color":"#e8a020","color":"#7d5a3c","bg":"#f5ebe0",
     "fun_fact":"Le sambhar est le cerf le plus lourd d'Asie — sa vocalisation nocturne est très reconnaissable."},

    # ── FÉLINS ──────────────────────────────────────────────────────────────────
    {"category":"Félins","name":"Léopard de Ceylan","emoji":"🐆","scientific":"Panthera pardus kotiya",
     "habitat":"Forêts denses, zones rocheuses, savanes arbustives",
     "temperament":"Solitaire, discret, chasseur nocturne mais visible en journée à Yala",
     "size":"1.0–1.6 m (corps)","weight":"50–77 kg",
     "spots":["Yala (zone 1)","Wilpattu","Horton Plains"],
     "best_month":"Fév–Juil (saison sèche)",
     "status":"Vulnérable","status_color":"#e8a020","color":"#d4a017","bg":"#fff8e1",
     "fun_fact":"Yala possède la plus forte densité de léopards sauvages au monde — sous-espèce endémique."},
    {"category":"Félins","name":"Chat pêcheur","emoji":"🐱","scientific":"Prionailurus viverrinus",
     "habitat":"Zones humides, mangroves, bords de rivières",
     "temperament":"Nocturne, excellent nageur, difficile à observer",
     "size":"57–78 cm (corps)","weight":"5–16 kg",
     "spots":["Bundala","Muthurajawela","Parc de Yala"],
     "best_month":"Nov–Mar (saison sèche zones humides)",
     "status":"Vulnérable","status_color":"#e8a020","color":"#5d6d7e","bg":"#eaf2f8",
     "fun_fact":"Le chat pêcheur plonge sous l'eau pour attraper les poissons — unique parmi les félins."},
    {"category":"Félins","name":"Chat-léopard de Prionailurus","emoji":"🐈","scientific":"Prionailurus bengalensis",
     "habitat":"Forêts, plantations de thé, zones rurales",
     "temperament":"Très discret, strictement nocturne, rarement observé",
     "size":"38–66 cm (corps)","weight":"0.5–7 kg",
     "spots":["Sinharaja","Knuckles","Plantations du centre"],
     "best_month":"Toute l'année (nocturne)",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#c0392b","bg":"#fadbd8",
     "fun_fact":"Le plus petit félin sauvage du Sri Lanka, souvent confondu avec un chat domestique."},

    # ── REPTILES ────────────────────────────────────────────────────────────────
    {"category":"Reptiles","name":"Crocodile des marais","emoji":"🐊","scientific":"Crocodylus palustris",
     "habitat":"Rivières, lacs, mangroves, zones humides",
     "temperament":"Potentiellement dangereux — ne jamais s'approcher",
     "size":"3–4 m","weight":"150–250 kg",
     "spots":["Yala","Bundala","Maduganga (mangrove)"],
     "best_month":"Toute l'année",
     "status":"Vulnérable","status_color":"#e8a020","color":"#2d6a4f","bg":"#d8f3dc",
     "fun_fact":"Présent au Sri Lanka depuis 65 millions d'années, peu changé depuis les dinosaures."},
    {"category":"Reptiles","name":"Crocodile marin","emoji":"🐊","scientific":"Crocodylus porosus",
     "habitat":"Estuaires, mangroves, côtes marines",
     "temperament":"Extrêmement dangereux — espèce la plus grande et agressive",
     "size":"4–6 m","weight":"200–1 000 kg",
     "spots":["Bentota River","Pottuvil Lagoon","Mannar"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#1a5e3a","bg":"#d8f3dc",
     "fun_fact":"Le plus grand reptile vivant au monde — peut nager des centaines de km en mer ouverte."},
    {"category":"Reptiles","name":"Tortue de mer verte","emoji":"🐢","scientific":"Chelonia mydas",
     "habitat":"Mer ouverte, plages de ponte sableuses",
     "temperament":"Indifférente aux plongeurs, se laisse approcher doucement",
     "size":"80–120 cm","weight":"70–190 kg",
     "spots":["Hikkaduwa (snorkeling)","Tangalle (ponte)","Rekawa"],
     "best_month":"Jan–Mar (ponte) | Toute l'année (snorkeling)",
     "status":"En danger","status_color":"#c0392b","color":"#148f77","bg":"#d1f2eb",
     "fun_fact":"Les femelles retournent toujours pondre sur la plage exacte où elles sont nées."},
    {"category":"Reptiles","name":"Tortue imbriquée","emoji":"🐢","scientific":"Eretmochelys imbricata",
     "habitat":"Récifs coralliens, lagons côtiers",
     "temperament":"Timide, se cache dans les coraux",
     "size":"60–95 cm","weight":"45–90 kg",
     "spots":["Pigeon Island","Hikkaduwa","Weligama"],
     "best_month":"Toute l'année (snorkeling)",
     "status":"En danger critique","status_color":"#922b21","color":"#d4ac0d","bg":"#fef9e7",
     "fun_fact":"Son bec en forme de faucon lui permet d'extraire les éponges des récifs coralliens."},
    {"category":"Reptiles","name":"Varan indien","emoji":"🦎","scientific":"Varanus bengalensis",
     "habitat":"Forêts, zones rocheuses, bords de cours d'eau",
     "temperament":"Fuyard et méfiant, mord si acculé",
     "size":"1.0–1.75 m","weight":"5–20 kg",
     "spots":["Yala","Wilpattu","Parcs nationaux en général"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#5d4037","bg":"#efebe9",
     "fun_fact":"Excellent nageur et grimpeur, il joue un rôle clé en consommant les charognes dans l'écosystème."},
    {"category":"Reptiles","name":"Serpent de mer jaune","emoji":"🐍","scientific":"Hydrophis platurus",
     "habitat":"Eaux marines tropicales, surface de l'océan",
     "temperament":"Venimeux mais peu agressif, morsure rare",
     "size":"50–88 cm","weight":"0.2–0.5 kg",
     "spots":["Côte sud","Kalpitiya","Large de Trincomalee"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#f1c40f","bg":"#fefbd8",
     "fun_fact":"Le seul serpent entièrement pélagique au monde — il ne revient jamais sur terre."},
    {"category":"Reptiles","name":"Gecko tokay","emoji":"🦎","scientific":"Gekko gecko",
     "habitat":"Forêts tropicales, maisons, murs de temples",
     "temperament":"Territorial et bruyant la nuit, morsure possible",
     "size":"25–35 cm","weight":"100–300 g",
     "spots":["Partout dans l'île","Temples","Maisons rurales"],
     "best_month":"Toute l'année (nocturne)",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#8e44ad","bg":"#f5eef8",
     "fun_fact":"Son cri \"to-kay\" est l'un des sons les plus caractéristiques des nuits tropicales du Sri Lanka."},

    # ── OISEAUX ─────────────────────────────────────────────────────────────────
    {"category":"Oiseaux","name":"Paon bleu de Ceylan","emoji":"🦚","scientific":"Pavo cristatus",
     "habitat":"Forêts ouvertes, zones rurales, jardins",
     "temperament":"Timide mais habitué à l'homme dans les parcs nationaux",
     "size":"100–120 cm (+150 cm queue)","weight":"4–6 kg",
     "spots":["Yala","Wilpattu","Udawalawe","Temples"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#1a6b3c","bg":"#d4efdf",
     "fun_fact":"Oiseau national du Sri Lanka, omniprésent dans les parcs et temples de l'île."},
    {"category":"Oiseaux","name":"Flamant rose","emoji":"🦩","scientific":"Phoenicopterus roseus",
     "habitat":"Lagunes salées, mangroves, marais côtiers",
     "temperament":"Grégaire, vit en grands groupes, très méfiant",
     "size":"120–145 cm","weight":"2–4 kg",
     "spots":["Bundala NP","Kumana","Mannar"],
     "best_month":"Nov–Mar (migration) | Avr–Juil (Kumana)",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#e91e8c","bg":"#fce4ec",
     "fun_fact":"Les flamants doivent courir sur l'eau plusieurs mètres avant de pouvoir décoller."},
    {"category":"Oiseaux","name":"Aigle pêcheur de Pallas","emoji":"🦅","scientific":"Haliaeetus leucoryphus",
     "habitat":"Grands lacs, réservoirs, côtes",
     "temperament":"Territorial et dominant, pêche en plongeant depuis les airs",
     "size":"72–84 cm (envergure 180–200 cm)","weight":"2–3.7 kg",
     "spots":["Minneriya","Kaudulla","Gal Oya"],
     "best_month":"Nov–Mar",
     "status":"En danger","status_color":"#c0392b","color":"#7f8c8d","bg":"#f2f3f4",
     "fun_fact":"Capable de pêcher sous l'eau et de saisir une proie pesant jusqu'à 3 fois son poids."},
    {"category":"Oiseaux","name":"Calao de Ceylan","emoji":"🦜","scientific":"Anthracoceros coronatus",
     "habitat":"Forêts tropicales humides, zones boisées",
     "temperament":"Bruyant, vole en groupes familiaux, impressionnant en vol",
     "size":"60–65 cm","weight":"0.6–1.2 kg",
     "spots":["Sinharaja","Kitulgala","Knuckles"],
     "best_month":"Toute l'année",
     "status":"Quasi menacé","status_color":"#e8a020","color":"#2c3e50","bg":"#eaecee",
     "fun_fact":"La femelle se mure dans le nid avec de la boue pendant la couvaison — le mâle la nourrit par une fente."},
    {"category":"Oiseaux","name":"Rollier indien","emoji":"🦜","scientific":"Coracias benghalensis",
     "habitat":"Terres agricoles ouvertes, zones arborées",
     "temperament":"Territorial, se perche en évidence pour chasser les insectes",
     "size":"26–27 cm","weight":"90–125 g",
     "spots":["Campagnes du nord","Anuradhapura","Bords de route"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#2980b9","bg":"#d6eaf8",
     "fun_fact":"Son plumage turquoise électrique est l'un des plus beaux parmi les oiseaux du Sri Lanka."},
    {"category":"Oiseaux","name":"Pélican frisé","emoji":"🦢","scientific":"Pelecanus crispus",
     "habitat":"Grands lacs, lagunes côtières, estuaires",
     "temperament":"Grégaire, pêche en groupes coordonnés",
     "size":"160–183 cm (envergure 270–310 cm)","weight":"7–15 kg",
     "spots":["Kumana","Bundala","Mannar"],
     "best_month":"Oct–Mar (migration hivernale)",
     "status":"Vulnérable","status_color":"#e8a020","color":"#85929e","bg":"#f2f3f4",
     "fun_fact":"Son sac gulaire peut contenir jusqu'à 13 litres d'eau lors de la pêche."},
    {"category":"Oiseaux","name":"Héron pourpré","emoji":"🦢","scientific":"Ardea purpurea",
     "habitat":"Roselières, marais, bords de rivières boisés",
     "temperament":"Solitaire et discret, s'immobilise parfaitement camouflé",
     "size":"78–90 cm","weight":"0.6–1.4 kg",
     "spots":["Kumana","Bundala","Pottuvil Lagoon"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#922b21","bg":"#fadbd8",
     "fun_fact":"Il peut rester immobile pendant des heures, utilisant sa silhouette pour se fondre dans les roseaux."},
    {"category":"Oiseaux","name":"Martin-pêcheur pie","emoji":"🐦","scientific":"Ceryle rudis",
     "habitat":"Rivières, lacs, côtes marines, canaux",
     "temperament":"Territorial, plonge verticalement à grande vitesse",
     "size":"25–27 cm","weight":"68–108 g",
     "spots":["Toutes les zones humides","Kandy Lake","Bords de rivières"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#1a5276","bg":"#d6eaf8",
     "fun_fact":"Il survole l'eau en vol stationnaire avant de plonger — l'un des rares martin-pêcheurs à le faire régulièrement."},

    # ── POISSONS & VIE MARINE ───────────────────────────────────────────────────
    {"category":"Poissons & Vie marine","name":"Raie manta","emoji":"🐟","scientific":"Mobula birostris",
     "habitat":"Eaux océaniques ouvertes et côtières profondes",
     "temperament":"Totalement inoffensive, curieuse des plongeurs",
     "size":"3–7 m d'envergure","weight":"1 350–3 000 kg",
     "spots":["Baa Atoll voisin","Large de Trinco","Kalpitiya"],
     "best_month":"Nov–Avr",
     "status":"En danger","status_color":"#c0392b","color":"#1a3a5c","bg":"#d6eaf8",
     "fun_fact":"Les raies mantas sautent hors de l'eau et font des acrobaties — la raison reste un mystère."},
    {"category":"Poissons & Vie marine","name":"Requin baleine","emoji":"🐋","scientific":"Rhincodon typus",
     "habitat":"Eaux tropicales ouvertes, zones riches en plancton",
     "temperament":"Totalement inoffensif, se nourrit de plancton",
     "size":"5.5–14 m","weight":"5 000–21 000 kg",
     "spots":["Large de Trincomalee","Mirissa","Kalpitiya"],
     "best_month":"Mar–Juil",
     "status":"En danger","status_color":"#c0392b","color":"#1f618d","bg":"#d6eaf8",
     "fun_fact":"Le plus grand poisson au monde — sa bouche peut atteindre 1.5 m de large."},
    {"category":"Poissons & Vie marine","name":"Poisson-clown","emoji":"🐠","scientific":"Amphiprion ocellaris",
     "habitat":"Récifs coralliens peu profonds, anémones de mer",
     "temperament":"Territorial autour de son anémone, inoffensif",
     "size":"8–11 cm","weight":"150–250 g",
     "spots":["Pigeon Island","Hikkaduwa","Weligama"],
     "best_month":"Toute l'année (snorkeling)",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#e67e22","bg":"#fdebd0",
     "fun_fact":"Tous les poissons-clowns naissent mâles — le dominant change de sexe pour devenir femelle."},
    {"category":"Poissons & Vie marine","name":"Murène géante","emoji":"🐍","scientific":"Gymnothorax javanicus",
     "habitat":"Récifs coralliens, crevasses rocheuses",
     "temperament":"Inoffensive si non provoquée, morsure puissante",
     "size":"1.5–3 m","weight":"30 kg",
     "spots":["Pigeon Island","Hikkaduwa","Nilaveli"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#7d6608","bg":"#fef9e7",
     "fun_fact":"La murène respire en ouvrant constamment la bouche — ce n'est pas un comportement menaçant."},
    {"category":"Poissons & Vie marine","name":"Thon à nageoires jaunes","emoji":"🐟","scientific":"Thunnus albacares",
     "habitat":"Eaux océaniques ouvertes, zones de courant",
     "temperament":"Rapide et puissant, chasse en bancs coordonnés",
     "size":"1.0–2.0 m","weight":"30–200 kg",
     "spots":["Large de Trincomalee","Côte sud","Excursions de pêche"],
     "best_month":"Avr–Sep (côte est)",
     "status":"Quasi menacé","status_color":"#e8a020","color":"#f4d03f","bg":"#fefbd8",
     "fun_fact":"Le thon n'a pas de vessie natatoire — il doit nager en permanence ou il coule."},
    {"category":"Poissons & Vie marine","name":"Lion de mer / Poisson-lion","emoji":"🐡","scientific":"Pterois volitans",
     "habitat":"Récifs coralliens, épaves, fonds rocheux",
     "temperament":"Inoffensif mais ses épines sont venimeuses",
     "size":"25–40 cm","weight":"0.5–1.2 kg",
     "spots":["Hikkaduwa","Pigeon Island","Weligama"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#922b21","bg":"#fadbd8",
     "fun_fact":"Ses 18 épines dorsales injectent un venin douloureux mais rarement mortel pour l'homme."},
    {"category":"Poissons & Vie marine","name":"Barracuda","emoji":"🐟","scientific":"Sphyraena barracuda",
     "habitat":"Eaux côtières claires, récifs, eaux ouvertes",
     "temperament":"Inquisiteur et impressionnant, rarement dangereux pour l'homme",
     "size":"1.0–2.0 m","weight":"2.5–50 kg",
     "spots":["Trincomalee","Nilaveli","Hikkaduwa"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#5d6d7e","bg":"#eaf2f8",
     "fun_fact":"Le barracuda peut nager en pointes à 45 km/h — l'un des prédateurs les plus rapides du récif."},

    # ── PRIMATES ────────────────────────────────────────────────────────────────
    {"category":"Primates","name":"Macaque à toque","emoji":"🐒","scientific":"Macaca sinica",
     "habitat":"Forêts sèches, zones de temple, environs urbains",
     "temperament":"Social et audacieux, vole nourriture aux touristes",
     "size":"42–53 cm (corps)","weight":"3.5–8.4 kg",
     "spots":["Dambulla","Polonnaruwa","Sigiriya"],
     "best_month":"Toute l'année",
     "status":"En danger","status_color":"#c0392b","color":"#c0392b","bg":"#fadbd8",
     "fun_fact":"Endémique du Sri Lanka — son nom vient de la touffe de poils rayonnante sur le sommet du crâne."},
    {"category":"Primates","name":"Langur de Ceylan","emoji":"🐒","scientific":"Semnopithecus vetulus",
     "habitat":"Forêts humides, zones montageuses, parcs",
     "temperament":"Timide et réservé, vit en groupes hiérarchisés",
     "size":"55–75 cm (corps)","weight":"4–9 kg",
     "spots":["Sinharaja","Kitulgala","Kandy"],
     "best_month":"Toute l'année",
     "status":"Vulnérable","status_color":"#e8a020","color":"#7f8c8d","bg":"#f2f3f4",
     "fun_fact":"Endémique du Sri Lanka — son visage noir contraste avec son pelage gris argenté."},
    {"category":"Primates","name":"Langur Hanuman (entelle)","emoji":"🐵","scientific":"Semnopithecus priam",
     "habitat":"Forêts sèches, abords de temples, zones agricoles",
     "temperament":"Social, calme, considéré sacré dans la tradition hindoue",
     "size":"50–78 cm (corps)","weight":"8–21 kg",
     "spots":["Jaffna","Polonnaruwa","Temples du nord"],
     "best_month":"Toute l'année",
     "status":"Préoccupation mineure","status_color":"#27ae60","color":"#c8860a","bg":"#fef9e7",
     "fun_fact":"Vénéré comme incarnation de Hanuman dans l'hindouisme — protégé autour de tous les temples."},
    {"category":"Primates","name":"Loris de Ceylan","emoji":"🦥","scientific":"Loris tardigradus",
     "habitat":"Forêts humides denses, zones d'altitude",
     "temperament":"Strictement nocturne, solitaire et très lent",
     "size":"17–26 cm","weight":"85–350 g",
     "spots":["Sinharaja","Knuckles Range","Plantations de thé la nuit"],
     "best_month":"Toute l'année (nocturne)",
     "status":"En danger","status_color":"#c0392b","color":"#8e44ad","bg":"#f5eef8",
     "fun_fact":"Le seul primate venimeux au monde — il s'enduit de venin de glandes brachiales pour se protéger."},
    {"category":"Poissons & Vie marine","name":"Orque","emoji":"🐳","scientific":"Orcinus orca",
     "habitat":"Eaux océaniques profondes, zones côtières occasionnelles",
     "temperament":"Intelligente, sociale, jamais agressive envers l'homme en milieu naturel",
     "size":"5–9 m","weight":"2 500–9 000 kg",
     "spots":["Large de Mirissa (rare, déc–avr)","Côte sud du Sri Lanka"],
     "best_month":"Déc–Avr (rare mais possible lors des sorties baleines)",
     "status":"Données insuffisantes","status_color":"#5d6d7e","color":"#1a1a2e","bg":"#eaf0fb",
     "fun_fact":"Les orques sont observées occasionnellement au large de Mirissa lors des saisons de baleines bleues — une rencontre exceptionnelle et mémorable."}
]

WILDLIFE_NL = [
    # ── ZOOGDIEREN ──────────────────────────────────────────────────────────────
    {"category":"Zoogdieren (terrestrisch)","name":"Aziatische olifant","emoji":"🐘","scientific":"Elephas maximus",
     "habitat":"Bossen, savannes, wetlands",
     "temperament":"Doorgaans vredig, gevaarlijk als bedreigd of bronstig",
     "size":"2,5–3,5 m schofthoogte","weight":"3.000–5.000 kg",
     "spots":["Minneriya","Kaudulla","Udawalawe"],
     "best_month":"Jul–Okt (Minneriya-verzameling)",
     "status":"Bedreigd","status_color":"#c0392b","color":"#8B4513","bg":"#f5e6d3",
     "fun_fact":"Sri Lanka heeft de hoogste dichtheid aan Aziatische olifanten ter wereld."},
    {"category":"Zoogdieren (terrestrisch)","name":"Ceylon-lippenbeer","emoji":"🐻","scientific":"Melursus ursinus inornatus",
     "habitat":"Droge bossen, rotsachtige uitstekende delen",
     "temperament":"Onvoorspelbaar en mogelijk agressief — weinig schuw",
     "size":"1,4–1,8 m","weight":"80–140 kg",
     "spots":["Yala","Wilpattu","Wasgamuwa"],
     "best_month":"Jun–Sep",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#6e2c00","bg":"#fce8d5",
     "fun_fact":"Endemische ondersoort van Sri Lanka, herkenbaar aan zijn witte snuit."},
    {"category":"Vissen & Zeeleven","name":"Draaiende dolfijn","emoji":"🐬","scientific":"Stenella longirostris",
     "habitat":"Warme kustwateren, open oceaan",
     "temperament":"Erg speels, surft graag op boegolven",
     "size":"1,3–2,0 m","weight":"50–80 kg",
     "spots":["Mirissa (vroeg ochtend)","Trincomalee","Kalpitiya"],
     "best_month":"Nov–Apr",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#2471a3","bg":"#d6eaf8",
     "fun_fact":"Duizenden draaiende dolfijnen reizen elke ochtend in scholen voor de kust van Mirissa."},
    {"category":"Vissen & Zeeleven","name":"Blauwe vinvis","emoji":"🐋","scientific":"Balaenoptera musculus",
     "habitat":"Diepe Indische Oceaan, kustwateren",
     "temperament":"Rustig, nieuwsgierig, majestueuze migrant",
     "size":"24–30 m","weight":"100.000–150.000 kg",
     "spots":["Mirissa (boot)","Trincomalee (boot)","Dondra Head"],
     "best_month":"Nov–Apr (Mirissa) | Apr–Sep (Trinco)",
     "status":"Bedreigd","status_color":"#c0392b","color":"#1a5276","bg":"#d6eaf8",
     "fun_fact":"Sri Lanka is een van de beste plaatsen ter wereld om de blauwe vinvis te spotten."},
    {"category":"Vissen & Zeeleven","name":"Indo-Pacifische bultdolfijn","emoji":"🐳","scientific":"Sousa chinensis",
     "habitat":"Ondiepe kustwateren, estuaria",
     "temperament":"Nieuwsgierig, mengt zich soms met draaiende dolfijnen",
     "size":"2,0–2,8 m","weight":"150–280 kg",
     "spots":["Kalpitiya","Trincomalee","Westkust"],
     "best_month":"Nov–Apr",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#2980b9","bg":"#d6eaf8",
     "fun_fact":"Herkenbaar aan zijn karakteristieke rugbult en roze-grijze tint."},
    {"category":"Zoogdieren (terrestrisch)","name":"Axis-hert (Spotted deer)","emoji":"🦌","scientific":"Axis axis",
     "habitat":"Open bossen, graslanden, parkranden",
     "temperament":"Schuchter en waakzaam — hoofdprooi van het luipaard",
     "size":"70–95 cm schofthoogte","weight":"30–75 kg",
     "spots":["Yala","Wilpattu","Fort Frederick (Trinco)"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#c8860a","bg":"#fef9e7",
     "fun_fact":"Zo talrijk in Yala dat het de favoriete prooi is van het Ceylon-luipaard."},
    {"category":"Zoogdieren (terrestrisch)","name":"Waterbuffel","emoji":"🐃","scientific":"Bubalus bubalis",
     "habitat":"Wetlands, rijstvelden, overstroomde graslanden",
     "temperament":"Krachtig en onvoorspelbaar — respecteer de afstand",
     "size":"1,5–1,9 m schofthoogte","weight":"700–1.200 kg",
     "spots":["Udawalawe","Bundala","Minneriya"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#555","bg":"#f0f0f0",
     "fun_fact":"De wilde buffels van Sri Lanka behoren tot de grootste van Azië."},
    {"category":"Zoogdieren (terrestrisch)","name":"Sambarhert","emoji":"🦌","scientific":"Rusa unicolor",
     "habitat":"Dichte bossen, bergen, wetlands",
     "temperament":"Discreet en nachtelijk, vlucht bij nadering",
     "size":"1,2–1,6 m schofthoogte","weight":"150–320 kg",
     "spots":["Horton Plains","Knuckles Range","Sinharaja"],
     "best_month":"Het hele jaar",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#7d5a3c","bg":"#f5ebe0",
     "fun_fact":"Het sambarhert is het zwaarste hert van Azië — zijn nachtroep is zeer herkenbaar."},

    # ── KATACHTIGEN ─────────────────────────────────────────────────────────────
    {"category":"Katachtigen","name":"Ceylon-luipaard","emoji":"🐆","scientific":"Panthera pardus kotiya",
     "habitat":"Dichte bossen, rotsgebieden, struiksavanne",
     "temperament":"Solitair, discreet, overdag zichtbaar in Yala",
     "size":"1,0–1,6 m (lichaam)","weight":"50–77 kg",
     "spots":["Yala (zone 1)","Wilpattu","Horton Plains"],
     "best_month":"Feb–Jul (droog seizoen)",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#d4a017","bg":"#fff8e1",
     "fun_fact":"Yala heeft de hoogste dichtheid aan wilde luipaarden ter wereld — endemische ondersoort."},
    {"category":"Katachtigen","name":"Viskat","emoji":"🐱","scientific":"Prionailurus viverrinus",
     "habitat":"Wetlands, mangroven, oevers van rivieren",
     "temperament":"Nachtelijk, uitstekende zwemmer, moeilijk te observeren",
     "size":"57–78 cm (lichaam)","weight":"5–16 kg",
     "spots":["Bundala","Muthurajawela","Yala"],
     "best_month":"Nov–Mar (droog seizoen wetlands)",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#5d6d7e","bg":"#eaf2f8",
     "fun_fact":"De viskat duikt onder water om vissen te vangen — uniek onder katachtigen."},
    {"category":"Katachtigen","name":"Bengaalse luipaardkat","emoji":"🐈","scientific":"Prionailurus bengalensis",
     "habitat":"Bossen, theeplantages, landelijke gebieden",
     "temperament":"Zeer discreet, strikt nachtelijk, zelden waargenomen",
     "size":"38–66 cm (lichaam)","weight":"0,5–7 kg",
     "spots":["Sinharaja","Knuckles","Plantages in het centrum"],
     "best_month":"Het hele jaar (nachtelijk)",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#c0392b","bg":"#fadbd8",
     "fun_fact":"De kleinste wilde kat van Sri Lanka, vaak verward met een huiskat."},

    # ── REPTIELEN ───────────────────────────────────────────────────────────────
    {"category":"Reptielen","name":"Moerasskrokodil","emoji":"🐊","scientific":"Crocodylus palustris",
     "habitat":"Rivieren, meren, mangroven, wetlands",
     "temperament":"Potentieel gevaarlijk — nooit naderen",
     "size":"3–4 m","weight":"150–250 kg",
     "spots":["Yala","Bundala","Maduganga (mangrove)"],
     "best_month":"Het hele jaar",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#2d6a4f","bg":"#d8f3dc",
     "fun_fact":"Al 65 miljoen jaar aanwezig in Sri Lanka, nauwelijks veranderd sinds de dinosaurussen."},
    {"category":"Reptielen","name":"Zeekrokodil","emoji":"🐊","scientific":"Crocodylus porosus",
     "habitat":"Estuaria, mangroven, zeekusten",
     "temperament":"Extreem gevaarlijk — grootste en agressiefste soort",
     "size":"4–6 m","weight":"200–1.000 kg",
     "spots":["Bentota-rivier","Pottuvil Lagoon","Mannar"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#1a5e3a","bg":"#d8f3dc",
     "fun_fact":"Het grootste levende reptiel ter wereld — kan honderden km op open zee zwemmen."},
    {"category":"Reptielen","name":"Groene zeeschildpad","emoji":"🐢","scientific":"Chelonia mydas",
     "habitat":"Open zee, zandige legstranden",
     "temperament":"Onverschillig tegenover duikers, laat zich benaderen",
     "size":"80–120 cm","weight":"70–190 kg",
     "spots":["Hikkaduwa (snorkelen)","Tangalle (eileg)","Rekawa"],
     "best_month":"Jan–Mar (eileg) | Heel jaar (snorkelen)",
     "status":"Bedreigd","status_color":"#c0392b","color":"#148f77","bg":"#d1f2eb",
     "fun_fact":"Vrouwtjes keren altijd terug naar het exacte strand waar ze geboren zijn om eieren te leggen."},
    {"category":"Reptielen","name":"Karetschildpad","emoji":"🐢","scientific":"Eretmochelys imbricata",
     "habitat":"Koraalriffen, kustlagunes",
     "temperament":"Schuchter, verstopt zich tussen koralen",
     "size":"60–95 cm","weight":"45–90 kg",
     "spots":["Pigeon Island","Hikkaduwa","Weligama"],
     "best_month":"Het hele jaar (snorkelen)",
     "status":"Ernstig bedreigd","status_color":"#922b21","color":"#d4ac0d","bg":"#fef9e7",
     "fun_fact":"Zijn valkachtige bek stelt hem in staat sponsen uit koraalriffen te halen."},
    {"category":"Reptielen","name":"Indische varaan","emoji":"🦎","scientific":"Varanus bengalensis",
     "habitat":"Bossen, rotsgebieden, oevers van waterlopen",
     "temperament":"Vluchtend en wantrouwig, bijt als in het nauw gedreven",
     "size":"1,0–1,75 m","weight":"5–20 kg",
     "spots":["Yala","Wilpattu","Nationale parken algemeen"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#5d4037","bg":"#efebe9",
     "fun_fact":"Uitstekend zwemmer en klimmer, speelt een sleutelrol door kadavers te consumeren."},
    {"category":"Reptielen","name":"Tokay-gekko","emoji":"🦎","scientific":"Gekko gecko",
     "habitat":"Tropische bossen, huizen, tempelmuren",
     "temperament":"Territoriaal en luidruchtig 's nachts, kan bijten",
     "size":"25–35 cm","weight":"100–300 g",
     "spots":["Overal op het eiland","Tempels","Landelijke huizen"],
     "best_month":"Het hele jaar (nachtelijk)",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#8e44ad","bg":"#f5eef8",
     "fun_fact":"Zijn roep 'to-kay' is een van de meest kenmerkende geluiden van tropische nachten in Sri Lanka."},

    # ── VOGELS ──────────────────────────────────────────────────────────────────
    {"category":"Vogels","name":"Indische pauw","emoji":"🦚","scientific":"Pavo cristatus",
     "habitat":"Open bossen, landelijk gebied, tuinen",
     "temperament":"Schuchter maar gewend aan mensen in parken",
     "size":"100–120 cm (+150 cm staart)","weight":"4–6 kg",
     "spots":["Yala","Wilpattu","Udawalawe","Tempels"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#1a6b3c","bg":"#d4efdf",
     "fun_fact":"Nationale vogel van Sri Lanka, overal te zien in parken en tempels."},
    {"category":"Vogels","name":"Flamingo","emoji":"🦩","scientific":"Phoenicopterus roseus",
     "habitat":"Zoute lagunes, mangroven, kustmoerassen",
     "temperament":"Groepsdier, leeft in grote kolonies, zeer schuw",
     "size":"120–145 cm","weight":"2–4 kg",
     "spots":["Bundala NP","Kumana","Mannar"],
     "best_month":"Nov–Mar (trek) | Apr–Jul (Kumana)",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#e91e8c","bg":"#fce4ec",
     "fun_fact":"Flamingo's moeten meters over water rennen voordat ze kunnen opstijgen."},
    {"category":"Vogels","name":"Pallas' zeearend","emoji":"🦅","scientific":"Haliaeetus leucoryphus",
     "habitat":"Grote meren, stuwmeren, kusten",
     "temperament":"Territoriaal en dominant, vist vanuit de lucht",
     "size":"72–84 cm (spanwijdte 180–200 cm)","weight":"2–3,7 kg",
     "spots":["Minneriya","Kaudulla","Gal Oya"],
     "best_month":"Nov–Mar",
     "status":"Bedreigd","status_color":"#c0392b","color":"#7f8c8d","bg":"#f2f3f4",
     "fun_fact":"Kan onder water vissen en een prooi grijpen die tot 3x zijn eigen gewicht weegt."},
    {"category":"Vogels","name":"Ceylon-neushoornvogel","emoji":"🦜","scientific":"Anthracoceros coronatus",
     "habitat":"Vochtige tropische bossen, beboste gebieden",
     "temperament":"Luidruchtig, vliegt in familiegroepen, indrukwekkend in vlucht",
     "size":"60–65 cm","weight":"0,6–1,2 kg",
     "spots":["Sinharaja","Kitulgala","Knuckles"],
     "best_month":"Het hele jaar",
     "status":"Bijna bedreigd","status_color":"#e8a020","color":"#2c3e50","bg":"#eaecee",
     "fun_fact":"Het vrouwtje metselt zich in het nest met modder tijdens het broeden — het mannetje voedt haar."},
    {"category":"Vogels","name":"Indische scharrelaar","emoji":"🦜","scientific":"Coracias benghalensis",
     "habitat":"Open landbouwgrond, beboste gebieden",
     "temperament":"Territoriaal, zit opvallend om insecten te vangen",
     "size":"26–27 cm","weight":"90–125 g",
     "spots":["Platteland noorden","Anuradhapura","Wegbermen"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#2980b9","bg":"#d6eaf8",
     "fun_fact":"Zijn elektrisch turquoise verenkleed is een van de mooiste van alle vogels in Sri Lanka."},
    {"category":"Vogels","name":"Kroeskoppelikaan","emoji":"🦢","scientific":"Pelecanus crispus",
     "habitat":"Grote meren, kustlagunes, estuaria",
     "temperament":"Groepsdier, vist in gecoördineerde groepen",
     "size":"160–183 cm (spanwijdte 270–310 cm)","weight":"7–15 kg",
     "spots":["Kumana","Bundala","Mannar"],
     "best_month":"Okt–Mar (wintermigratie)",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#85929e","bg":"#f2f3f4",
     "fun_fact":"Zijn keelzak kan tot 13 liter water bevatten tijdens het vissen."},
    {"category":"Vogels","name":"Purperreiger","emoji":"🦢","scientific":"Ardea purpurea",
     "habitat":"Rietvelden, moerassen, beboste rivieroeversen",
     "temperament":"Solitair en discreet, staat perfect gecamoufleerd stil",
     "size":"78–90 cm","weight":"0,6–1,4 kg",
     "spots":["Kumana","Bundala","Pottuvil Lagoon"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#922b21","bg":"#fadbd8",
     "fun_fact":"Hij kan urenlang roerloos staan, zijn silhouet gebruikend als camouflage in het riet."},
    {"category":"Vogels","name":"Bonte ijsvogel","emoji":"🐦","scientific":"Ceryle rudis",
     "habitat":"Rivieren, meren, zeekusten, kanalen",
     "temperament":"Territoriaal, duikt verticaal met grote snelheid",
     "size":"25–27 cm","weight":"68–108 g",
     "spots":["Alle wetlands","Kandy Lake","Rivieroeversen"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#1a5276","bg":"#d6eaf8",
     "fun_fact":"Hij zweeft boven water voor het duiken — een van de weinige ijsvogels die dit regelmatig doen."},

    # ── VISSEN & ZEELEVENS ──────────────────────────────────────────────────────
    {"category":"Vissen & Zeeleven","name":"Manta-rog","emoji":"🐟","scientific":"Mobula birostris",
     "habitat":"Oceaanwateren en diepe kustwateren",
     "temperament":"Volledig onschadelijk, nieuwsgierig naar duikers",
     "size":"3–7 m vleugelspanwijdte","weight":"1.350–3.000 kg",
     "spots":["Open zee bij Trinco","Kalpitiya"],
     "best_month":"Nov–Apr",
     "status":"Bedreigd","status_color":"#c0392b","color":"#1a3a5c","bg":"#d6eaf8",
     "fun_fact":"Manta-roggen springen uit het water en maken acrobatieën — de reden blijft een mysterie."},
    {"category":"Vissen & Zeeleven","name":"Walvishaai","emoji":"🐋","scientific":"Rhincodon typus",
     "habitat":"Tropische open wateren, planktonrijke zones",
     "temperament":"Volledig onschadelijk, voedt zich met plankton",
     "size":"5,5–14 m","weight":"5.000–21.000 kg",
     "spots":["Open zee bij Trincomalee","Mirissa","Kalpitiya"],
     "best_month":"Mrt–Jul",
     "status":"Bedreigd","status_color":"#c0392b","color":"#1f618d","bg":"#d6eaf8",
     "fun_fact":"De grootste vis ter wereld — zijn bek kan 1,5 m breed zijn."},
    {"category":"Vissen & Zeeleven","name":"Clownvis","emoji":"🐠","scientific":"Amphiprion ocellaris",
     "habitat":"Ondiepe koraalriffen, zeeanemonen",
     "temperament":"Territoriaal rondom zijn anemoon, onschadelijk",
     "size":"8–11 cm","weight":"150–250 g",
     "spots":["Pigeon Island","Hikkaduwa","Weligama"],
     "best_month":"Het hele jaar (snorkelen)",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#e67e22","bg":"#fdebd0",
     "fun_fact":"Alle clownvissen worden als mannetje geboren — de dominante verandert van geslacht."},
    {"category":"Vissen & Zeeleven","name":"Reuzenmoray","emoji":"🐍","scientific":"Gymnothorax javanicus",
     "habitat":"Koraalriffen, rotsachtige spleten",
     "temperament":"Onschadelijk als niet uitgelokt, krachtige beet",
     "size":"1,5–3 m","weight":"30 kg",
     "spots":["Pigeon Island","Hikkaduwa","Nilaveli"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#7d6608","bg":"#fef9e7",
     "fun_fact":"De moray ademt door zijn bek continu te openen — dit is geen dreigend gedrag."},
    {"category":"Vissen & Zeeleven","name":"Geelvintonijn","emoji":"🐟","scientific":"Thunnus albacares",
     "habitat":"Open oceaanwateren, stroomzones",
     "temperament":"Snel en krachtig, jaagt in gecoördineerde scholen",
     "size":"1,0–2,0 m","weight":"30–200 kg",
     "spots":["Open zee bij Trincomalee","Zuidkust","Visexcursies"],
     "best_month":"Apr–Sep (oostkust)",
     "status":"Bijna bedreigd","status_color":"#e8a020","color":"#f4d03f","bg":"#fefbd8",
     "fun_fact":"Tonijn heeft geen zwemblaas — hij moet voortdurend zwemmen of hij zinkt."},
    {"category":"Vissen & Zeeleven","name":"Koraalduivel","emoji":"🐡","scientific":"Pterois volitans",
     "habitat":"Koraalriffen, wrakken, rotsachtige bodem",
     "temperament":"Onschadelijk maar zijn stekels zijn giftig",
     "size":"25–40 cm","weight":"0,5–1,2 kg",
     "spots":["Hikkaduwa","Pigeon Island","Weligama"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#922b21","bg":"#fadbd8",
     "fun_fact":"Zijn 18 rugstekels injecteren een pijnlijk maar zelden dodelijk gif voor mensen."},
    {"category":"Vissen & Zeeleven","name":"Barracuda","emoji":"🐟","scientific":"Sphyraena barracuda",
     "habitat":"Heldere kustwateren, riffen, open wateren",
     "temperament":"Nieuwsgierig en indrukwekkend, zelden gevaarlijk voor mensen",
     "size":"1,0–2,0 m","weight":"2,5–50 kg",
     "spots":["Trincomalee","Nilaveli","Hikkaduwa"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#5d6d7e","bg":"#eaf2f8",
     "fun_fact":"De barracuda kan 45 km/u bereiken — een van de snelste roofdieren van het rif."},

    # ── PRIMATEN ────────────────────────────────────────────────────────────────
    {"category":"Primaten","name":"Toque-makaak","emoji":"🐒","scientific":"Macaca sinica",
     "habitat":"Droge bossen, tempelgebieden, stedelijke omgeving",
     "temperament":"Sociaal en brutaal, steelt voedsel van toeristen",
     "size":"42–53 cm (lichaam)","weight":"3,5–8,4 kg",
     "spots":["Dambulla","Polonnaruwa","Sigiriya"],
     "best_month":"Het hele jaar",
     "status":"Bedreigd","status_color":"#c0392b","color":"#c0392b","bg":"#fadbd8",
     "fun_fact":"Endemisch voor Sri Lanka — de naam komt van het stralende haarkuifje op de schedel."},
    {"category":"Primaten","name":"Ceylon-langur","emoji":"🐒","scientific":"Semnopithecus vetulus",
     "habitat":"Vochtige bossen, berggebieden, parken",
     "temperament":"Schuchter en teruggetrokken, leeft in hiërarchische groepen",
     "size":"55–75 cm (lichaam)","weight":"4–9 kg",
     "spots":["Sinharaja","Kitulgala","Kandy"],
     "best_month":"Het hele jaar",
     "status":"Kwetsbaar","status_color":"#e8a020","color":"#7f8c8d","bg":"#f2f3f4",
     "fun_fact":"Endemisch voor Sri Lanka — zijn zwart gezicht contrasteert met zijn zilvergrijs vacht."},
    {"category":"Primaten","name":"Hanuman-langur (entellus)","emoji":"🐵","scientific":"Semnopithecus priam",
     "habitat":"Droge bossen, tempelomgevingen, landbouwgebieden",
     "temperament":"Sociaal, rustig, beschouwd als heilig in de hindoeïstische traditie",
     "size":"50–78 cm (lichaam)","weight":"8–21 kg",
     "spots":["Jaffna","Polonnaruwa","Tempels in het noorden"],
     "best_month":"Het hele jaar",
     "status":"Niet bedreigd","status_color":"#27ae60","color":"#c8860a","bg":"#fef9e7",
     "fun_fact":"Vereerd als incarnatie van Hanuman — beschermd rondom alle hindoetempels."},
    {"category":"Primaten","name":"Ceylon-plompe loris","emoji":"🦥","scientific":"Loris tardigradus",
     "habitat":"Dichte vochtige bossen, hooggelegen gebieden",
     "temperament":"Strikt nachtelijk, solitair en heel langzaam",
     "size":"17–26 cm","weight":"85–350 g",
     "spots":["Sinharaja","Knuckles Range","Theeplantages 's nachts"],
     "best_month":"Het hele jaar (nachtelijk)",
     "status":"Bedreigd","status_color":"#c0392b","color":"#8e44ad","bg":"#f5eef8",
     "fun_fact":"Het enige giftige primaat ter wereld — het smeert gif van armsklieren op zich als bescherming."},
]

LANG = {
"FR": {
    # Mois & saisons
    "months": ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Aoû","Sep","Oct","Nov","Déc"],
    "months_full": ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
    "seasons_west_labels": ["☀️ Haute","☀️ Haute","☀️ Haute","🌦 Inter","🌧 Mousson","🌧 Mousson",
                            "🌧 Mousson","🌧 Mousson","🌦 Inter","🌦 Inter","☀️ Haute","☀️ Haute"],
    "seasons_east_labels": ["🌧 Mousson","🌧 Mousson","🌦 Inter","☀️ Haute","☀️ Haute","☀️ Haute",
                            "☀️ Haute","☀️ Haute","🌦 Inter","🌦 Inter","🌧 Mousson","🌧 Mousson"],
    # Sidebar
    "nav_title":"🌴 Navigation",
    "how_to":"📖 Comment utiliser ce guide",
    "how_to_steps":"1️⃣ Choisis ton <b>mois</b> de voyage<br>2️⃣ Explore les <b>sections</b> dans le menu<br>3️⃣ Consulte la <b>carte</b> pour visualiser les saisons<br>4️⃣ Découvre tout sur <b>Juin</b> — le mois du voyage !",
    "section_label":"📂 Section",
    "section_hint":"👆 Choisis une section à explorer",
    "pages":["🏠 Vue générale","🌤️ Météo & Saisons","🗺️ Carte du Sri Lanka","🐘 Faune sauvage","☀️ Juin au Sri Lanka"],
    "month_label":"📅 Mois de voyage",
    "month_selected":"Mois sélectionné",
    "coast_label":"🌊 Côte préférée",
    "coast_opts":["Côte Ouest","Côte Est","Les deux"],
    "footer":"Dashboard Sri Lanka • 2025",
    # Hero
    "hero_title":"Sri Lanka Explorer",
    "hero_sub":"Votre guide interactif pour planifier le voyage parfait dans la Perle de l'Océan Indien",
    # Stats
    "stats":[
        {"icon":"👥","value":"22M","label":"Population","color":"#1a6b3c"},
        {"icon":"📐","value":"65 610","label":"km² superficie","color":"#e8a020"},
        {"icon":"💰","value":"84 Mds$","label":"PIB (USD)","color":"#c0392b"},
        {"icon":"✈️","value":"2.1M","label":"Touristes/an","color":"#8e44ad"},
        {"icon":"🏖️","value":"1 340","label":"km de côtes","color":"#2980b9"},
        {"icon":"🐘","value":"5 879","label":"Éléphants sauvages","color":"#27ae60"},
        {"icon":"🍵","value":"300k t","label":"Production de thé","color":"#d35400"},
        {"icon":"🏛️","value":"8","label":"Sites UNESCO","color":"#16a085"},
    ],
    # Vue générale
    "key_figures":"Chiffres clés",
    "reco_for":"Recommandation pour",
    "west_coast":"Côte Ouest","east_coast":"Côte Est",
    "temp":"Température","rain":"Pluies","sea":"Mer",
    "best_activities":"Meilleures activités","avoid":"À éviter",
    "season_haute":"☀️ Haute saison","season_inter":"🌦 Inter-saison","season_mousson":"🌧 Mousson",
    "season_haute_desc":"Soleil garanti, idéal pour les plages",
    "season_inter_desc":"Conditions variables, quelques pluies",
    "season_mousson_desc":"Pluies fréquentes, mer agitée",
    # Météo
    "meteo_title":"Météo & Saisons au Sri Lanka",
    "meteo_west":"Côte Ouest — Colombo","meteo_east":"Côte Est — Trincomalee",
    "temp_label":"Température (°C)","rain_label":"Précipitations (mm)",
    "calendar_title":"Calendrier des saisons",
    "high":"Haute saison","inter":"Inter-saison","monsoon":"Mousson",
    # Carte
    "map_slider":"Mois affiché sur la carte",
    "legend_title":"Légende","region_status":"📍 Statut régions","top_spots":"⭐ Top lieux",
    "haute_saison":"☀️ Haute saison","haute_desc":"Grand cercle = prioritaire",
    "inter_saison":"🌤 Inter-saison","inter_desc":"Conditions variables",
    "mousson":"🌧 Mousson","mousson_desc":"Déconseillé",
    "nord":"Nord (Jaffna, Vanni)","cote_ouest":"Côte Ouest (Colombo → Galle)",
    "cote_est":"Côte Est (Trinco, Arugam Bay)","centre":"Centre (Kandy, Ella, N. Eliya)","sud":"Sud (Yala, Mirissa, Tangalle)",
    "cal_east":"📆 Côte Est","cal_west":"📆 Côte Ouest",
    "map_top_east":[
        ("🌊","Trincomalee","Snorkeling, dauphins"),("🏄","Arugam Bay","Surf de classe mondiale"),
        ("🏝️","Nilaveli","Plage immaculée"),("🐆","Yala","Safaris léopards & éléphants"),
        ("🐘","Minneriya","Rassemblement éléphants"),
    ],
    "map_top_west":[
        ("🏰","Sigiriya","Rocher forteresse, fresques"),("🏯","Kandy","Temple de la Dent"),
        ("🍵","Nuwara Eliya","Plantations de thé"),("🌿","Ella","Randonnées, Nine Arch Bridge"),
        ("🏛️","Anuradhapura","Cité sacrée millénaire"),
    ],
    # Faune
    "faune_title":"Faune sauvage du Sri Lanka 🐘",
    "faune_sub":"Découvrez les animaux emblématiques de l'île, leurs habitats et où les observer.",
    "filter_cat":"🔍 Filtrer par catégorie",
    "all_animals":"🌿 Tous les animaux",
    "where_to_see":"📍 Où voir","best_month_lbl":"🗓️ Meilleur mois",
    "weight_lbl":"Poids","height_lbl":"Taille","status_lbl":"Statut","fun_fact_lbl":"💡 Le saviez-vous ?",
    "wildlife": WILDLIFE_FR,
    # Juin
    "juin_title":"☀️ Juin au Sri Lanka — Côte Est",
    "juin_sub":"Juin = l'un des meilleurs mois pour la côte Est. Soleil, mer calme, surf en plein swing, safaris au top — pendant que la côte Ouest est en mousson.",
    "juin_tip_title":"💡 Stratégie juin :",
    "juin_tip":"Évitez la côte ouest (Colombo, Galle, Mirissa) en pleine mousson. Concentrez-vous sur la <b>côte est</b> (Trincomalee, Nilaveli, Uppuveli, Arugam Bay) et les <b>parcs naturels de l'est</b> (Kumana, Gal Oya). Le surf à Arugam Bay est en plein pic mai–septembre. Poson Poya le 29 juin — jour férié.",
    "juin_kpis":[
        ("🌡️","30°C","Température Est","#e8a020"),("☀️","8h/jour","Ensoleillement","#1a6b3c"),
        ("🌊","28°C","Mer côte Est","#2980b9"),("🌧️","Mousson","Côte Ouest","#c0392b"),
    ],
    "tab_beaches":"🏖️ Plages & Mer","tab_safari":"🐘 Safari & Nature",
    "tab_activities":"🎯 Activités","tab_itineraries":"🗺️ Itinéraires","tab_hotels":"🏨 Hôtels",
    "plages":[
        {"name":"Trincomalee + Uppuveli","emoji":"🌊","color":"#1a6b3c","note":"⭐⭐⭐⭐⭐","ambiance":"All-in-one parfait",
         "desc":"La meilleure base en juin. Baie naturelle magnifique, eaux cristallines, et accès à tout : Pigeon Island, baleines bleues, temple Koneswaram, sources Kanniya.",
         "pour":"Familles, couples, snorkeling","acces":"5h Colombo ou vol interne",
         "activites":["🤿 Snorkeling Pigeon Island","🐋 Baleines bleues (mars–juil)","🛕 Temple Koneswaram","♨️ Sources Kanniya","🐬 Dauphins"]},
        {"name":"Nilaveli","emoji":"🏝️","color":"#16a085","note":"⭐⭐⭐⭐⭐","ambiance":"Calme & préservée",
         "desc":"5 km de sable blanc quasi-désert, eaux turquoise parfaites. Meilleur accès à Pigeon Island. La plage la plus immaculée du Sri Lanka.",
         "pour":"Couples, snorkeling, tranquillité","acces":"15 min nord de Trincomalee",
         "activites":["🏊 Baignade en eaux calmes","🤿 Plongée corail","🐠 Pigeon Island NP","🎣 Pêche traditionnelle"]},
        {"name":"Arugam Bay","emoji":"🏄","color":"#2980b9","note":"⭐⭐⭐⭐⭐","ambiance":"Surf & fête",
         "desc":"Le spot surf n°1 du Sri Lanka. Mai–sept = pic de saison. Vagues parfaites à Main Point, Whiskey Point et Peanut Farm. Ambiance internationale.",
         "pour":"Surfeurs, backpackers, nightlife","acces":"3h de Colombo",
         "activites":["🏄 Surf Main Point / Whiskey Pt","🐊 Safari Pottuvil Lagoon","🦜 Kumana birds","🌅 Couchers de soleil"]},
        {"name":"Pasikuda + Kalkudah","emoji":"🐠","color":"#8e44ad","note":"⭐⭐⭐⭐","ambiance":"Resort & détente",
         "desc":"Lagon peu profond aux eaux calmes, idéal pour nager. Parfait pour se reposer entre deux aventures. Snorkeling et glass-bottom boat.",
         "pour":"Familles, détente, séjour resort","acces":"2h au sud de Trincomalee",
         "activites":["🏊 Nage en lagon calme","🐠 Snorkeling récifs","🚤 Glass-bottom boat","🌅 Plage tranquille"]},
    ],
    "ideal_for":"Idéal pour","access_lbl":"Accès","activities_lbl":"Activités",
    "safaris":[
        {"name":"Yala National Park","emoji":"🐆","color":"#d35400","note":"⭐⭐⭐⭐⭐",
         "best":"Meilleur mois pour les léopards !",
         "desc":"Saison sèche = animaux concentrés aux points d'eau. Yala = plus forte densité de léopards au monde. Zone 1 recommandée.",
         "animaux":["🐆 Léopards","🐘 Éléphants","🐊 Crocodiles","🦚 Paons","🐻 Ours lippu"],
         "conseils":"Safari jeep le matin (6h). Réservez à l'avance en juin.","tarif":"~50-80$/pers"},
        {"name":"Minneriya National Park","emoji":"🐘","color":"#8B4513","note":"⭐⭐⭐⭐⭐",
         "best":"Le grand rassemblement commence !",
         "desc":"The Gathering débute en juin — jusqu'à 200-300 éléphants autour du lac. Spectacle unique au monde.",
         "animaux":["🐘 200-300 éléphants","🦌 Sambars","🐊 Crocodiles","🦅 Aigles pêcheurs"],
         "conseils":"L'après-midi (15h-18h) est le meilleur moment pour le rassemblement.","tarif":"~40-60$/pers"},
        {"name":"Kumana National Park","emoji":"🦜","color":"#1a6b3c","note":"⭐⭐⭐⭐⭐",
         "best":"Nidification avr–juil = pic ornitho !",
         "desc":"Juin = saison active de nidification. Flamants roses, hérons, spatules, pélicans. Près d'Arugam Bay.",
         "animaux":["🦜 200+ espèces d'oiseaux","🦩 Flamants roses","🦅 Aigles","🐊 Crocodiles"],
         "conseils":"Combinez avec Arugam Bay (30 min). Guide ornithologue recommandé.","tarif":"~30-50$/pers"},
        {"name":"Gal Oya National Park","emoji":"🐘","color":"#2980b9","note":"⭐⭐⭐⭐",
         "best":"Safari bateau unique au Sri Lanka !",
         "desc":"Safari en bateau sur le réservoir. Les éléphants nagent entre les îles — une expérience impossible ailleurs.",
         "animaux":["🐘 Éléphants nageurs","🐊 Crocodiles","🦅 Aigle de Brahminy","🦌 Cerfs"],
         "conseils":"Réservez le boat safari tôt le matin. Moins connu = moins de monde.","tarif":"~40-60$/pers"},
        {"name":"Pottuvil Lagoon","emoji":"🐊","color":"#16a085","note":"⭐⭐⭐⭐",
         "best":"À faire depuis Arugam Bay !",
         "desc":"Safari lagune de 2h en bateau. Crocodiles garantis, mangroves, oiseaux, éléphants occasionnels.",
         "animaux":["🐊 Crocodiles","🦜 Oiseaux de mangroves","🐘 Éléphants (lisière)","🦩 Hérons"],
         "conseils":"Départ au lever du soleil pour lumière parfaite.","tarif":"~15-25$/pers"},
        {"name":"Udawalawe National Park","emoji":"🐘","color":"#e8a020","note":"⭐⭐⭐⭐",
         "best":"90% de chances de voir des éléphants",
         "desc":"Le meilleur parc pour les éléphants toute l'année. En juin les jeunes jouent dans les points d'eau.",
         "animaux":["🐘 Éléphants (troupeaux)","🐃 Buffles d'eau","🦅 Aigles","🦚 Paons"],
         "conseils":"Sur la route Colombo–Yala, parfait en transit.","tarif":"~40-60$/pers"},
    ],
    "best_lbl":"","animals_lbl":"","tips_lbl":"💡","price_lbl":"🎟️",
    "activites":[
        {"cat":"🤿 Mer & Snorkeling","color":"#2980b9","items":[
            ("Pigeon Island NP","Coraux, tortues, poissons tropicaux — bateau depuis Nilaveli","⭐⭐⭐⭐⭐"),
            ("Snorkeling Pasikuda","Lagon peu profond, idéal débutants et familles","⭐⭐⭐⭐"),
            ("Plongée Trincomalee","Sites variés, visibilité excellente en juin","⭐⭐⭐⭐"),
            ("Glass-bottom boat","Tour en bateau fond de verre, parfait sans équipement","⭐⭐⭐"),
        ]},
        {"cat":"🏄 Surf","color":"#e8a020","items":[
            ("Main Point","Le spot emblématique, vagues longues et régulières","⭐⭐⭐⭐⭐"),
            ("Whiskey Point","20 min d'Arugam, plus calme, idéal intermédiaires","⭐⭐⭐⭐"),
            ("Peanut Farm","Vagues creuses, pour surfers expérimentés","⭐⭐⭐⭐"),
            ("Cours de surf","Camps proposent cours tous niveaux sur place","⭐⭐⭐⭐"),
        ]},
        {"cat":"🐋 Faune marine","color":"#1a6b3c","items":[
            ("Baleines bleues Trinco","Mars–juillet = peak. Excursions depuis Trincomalee","⭐⭐⭐⭐⭐"),
            ("Dauphins","Très fréquents, souvent lors des sorties baleines","⭐⭐⭐⭐⭐"),
            ("Tortues marines","Nilaveli et Pasikuda, snorkeling ou observation","⭐⭐⭐⭐"),
        ]},
        {"cat":"🚣 Lagunes & Kayak","color":"#16a085","items":[
            ("Batticaloa Lagoon","Kayak, mangroves, oiseaux, coucher de soleil","⭐⭐⭐⭐"),
            ("Pottuvil Lagoon","Safari bateau : crocodiles, oiseaux, mangroves","⭐⭐⭐⭐⭐"),
            ("Gal Oya boat safari","Éléphants nageurs — expérience unique au monde","⭐⭐⭐⭐⭐"),
        ]},
        {"cat":"🛕 Culture & Histoire","color":"#8e44ad","items":[
            ("Koneswaram Temple","Temple hindou sur falaise, vue mer à 360°","⭐⭐⭐⭐⭐"),
            ("Fort Frederick","Fort colonial avec cerfs en liberté, Trincomalee","⭐⭐⭐⭐"),
            ("Kanniya Hot Springs","7 puits d'eau chaude sacrés, arrêt fascinant","⭐⭐⭐⭐"),
            ("Kallady Bridge","Légende des poissons chanteurs, coucher de soleil","⭐⭐⭐"),
        ]},
        {"cat":"🍵 Thé & 🌾 Rizières","color":"#5d4037","items":[
            ("Pedro Tea Estate","Plantation historique à Nuwara Eliya — visite guidée du processus complet, dégustation incluse","⭐⭐⭐⭐⭐"),
            ("Mackwoods Labookellie","Sur la route Nuwara Eliya–Kandy — arrêt iconique, dégustation gratuite avec vue sur les collines","⭐⭐⭐⭐⭐"),
            ("Blue Field Tea Gardens","Ella — visite intime de plantation + dégustation artisanale avec vue montagne panoramique","⭐⭐⭐⭐"),
            ("Rizières de Knuckles Range","Terrasses de riz sculptées dans les vallées de montagne — parmi les plus belles de l'île, juin = vert éclatant","⭐⭐⭐⭐⭐"),
            ("Rizières d'Ella & Bandarawela","Rizières en terrasses entre les collines — lumière dorée du matin idéale, buffles d'eau dans les champs","⭐⭐⭐⭐"),
        ]},
    ],
    "itins":[
        {"name":"Option 1 — 14 jours Plages & Détente","color":"#2980b9","emoji":"🏖️",
         "profil":"Couple, famille, snorkeling, repos total",
         "duree":"14 jours",
         "etapes":[
            ("4 nuits","Trincomalee / Nilaveli","🏖️ Plages + 🤿 Pigeon Island + 🐋 Baleines + 🛕 Koneswaram + ♨️ Kanniya",
             "🏨 NN Beach Resort (~65$) ou 108 Palms (~88$)"),
            ("3 nuits","Pasikuda","🐠 Snorkeling lagon + 🚤 Glass-bottom boat + repos total",
             "🏨 Amethyst Resort (~60$) ou Amaya Beach (~63$)"),
            ("4 nuits","Batticaloa","🚣 Kayak lagune + 🌴 Mangroves + coucher de soleil Kallady Bridge + marché local",
             "🏨 Guesthouse locale (~25-40$)"),
            ("3 nuits","Arugam Bay","🏄 Initiation surf + 🐊 Pottuvil Lagoon + 🌅 couchers de soleil",
             "🏨 Babar Point (~69$) ou Bay Vista (~65$)"),
         ]},
        {"name":"Option 2 — 14 jours Surf + Safari + Nature","color":"#1a6b3c","emoji":"🏄",
         "profil":"Aventuriers, surfeurs, amateurs de faune sauvage",
         "duree":"14 jours",
         "etapes":[
            ("3 nuits","Trincomalee","🐋 Excursion baleines + 🤿 Snorkeling + ♨️ Kanniya + 🛕 Koneswaram",
             "🏨 Uga Jungle Beach (~90$) ou 108 Palms (~88$)"),
            ("5 nuits","Arugam Bay","🏄 Surf Main Point & Whiskey Pt + 🐊 Pottuvil Lagoon + 🦜 Kumana birds",
             "🏨 Babar Point (~69$) ou Surf N'Sun (~20-45$)"),
            ("3 nuits","Pasikuda","🐠 Lagon calme + repos + snorkeling + glass-bottom boat",
             "🏨 Amethyst Resort (~60$) ou The Calm (~100$)"),
            ("3 nuits","Habarana","🐘 Safari Minneriya (rassemblement) + 🏰 Sigiriya + Polonnaruwa",
             "🏨 Gabaa Resort (~70$) ou Habarana Tree House (~72$)"),
         ]},
        {"name":"Option 3 — 14 jours Thé + Est + Safari","color":"#8e44ad","emoji":"🗺️",
         "profil":"Curieux, culture + nature + plages — voyage complet",
         "duree":"14 jours",
         "etapes":[
            ("4 nuits","Trincomalee / Nilaveli","🌊 Plages + 🤿 Pigeon Island + 🐋 Baleines + 🛕 Temples + ♨️ Kanniya",
             "🏨 NN Beach Resort (~65$) ou Uga Jungle Beach (~90$)"),
            ("3 nuits","Nuwara Eliya / Ella","🍵 Pedro Tea Estate + Mackwoods + 🌾 Rizières Knuckles + 🌿 Nine Arch Bridge",
             "🏨 Idyll Cottage Ella (~68$) ou Ella Moon Rock (~85$)"),
            ("4 nuits","Arugam Bay","🏄 Surf + 🐊 Pottuvil safari + 🦜 Kumana birds + 🌅 couchers de soleil",
             "🏨 Babar Point (~69$) ou Bay Vista (~65$)"),
            ("3 nuits","Yala / Udawalawe","🐆 Safari léopards Yala + 🐘 Éléphants Udawalawe",
             "🏨 Wild Coast Tented Lodge (~350$+) ou guesthouse (~40-60$)"),
         ]},
    ],
    "practical_tips":"⚡ Tips pratiques juin",
    "tips_list":[
        ("🏄","<b>Arugam Bay peut être bondé</b> — réservez surf camps à l'avance"),
        ("☀️","<b>Crème solaire + rash guard</b> pour snorkeling (soleil intense)"),
        ("📅","<b>Poson Poya 29 juin</b> — jour férié, animation et déplacements +"),
        ("🤿","<b>Ne pas marcher sur le corail</b> — toujours avec guide à Pigeon Island"),
        ("🚗","<b>Côte Est = routes longues</b> — prévoyez chauffeur ou van privé"),
        ("🐋","<b>Baleines bleues</b> — mai-juillet à Trincomalee, réservez excursion"),
    ],
    "luxury":"💎 Luxe (~200-500$/nuit)","midrange":"🌿 Confort (~60-100$/nuit)","budget":"🎒 Économique (~15-55$/nuit)",
    "cat_desc_luxury":"5 étoiles, services premium","cat_desc_mid":"Excellent rapport qualité-prix, bien noté","cat_desc_budget":"Budget voyageur, authenticité locale",
    "highlight_lbl":"Point fort","included_lbl":"Inclus",
    "hotels":{
        "luxury":{"color":"#8e44ad","bg":"#f5eef8","hotels":[
            {"name":"Wild Coast Tented Lodge","lieu":"Yala","prix":"~350-500$/nuit","emoji":"🐆",
             "fort":"Tentes de luxe en pleine jungle, léopards devant la terrasse","inclus":["Safari privé","Piscine","Spa","Cuisine gastronomique"]},
            {"name":"Uga Bay Resort","lieu":"Pasikuda","prix":"~250-400$/nuit","emoji":"🌊",
             "fort":"Bungalows face mer, plage privée turquoise côte Est","inclus":["Plage privée","Piscine infinity","Spa","Petit-déj"]},
            {"name":"Trinco Blu by Cinnamon","lieu":"Trincomalee","prix":"~200-320$/nuit","emoji":"🌅",
             "fort":"Vue mer depuis toutes les chambres, accès direct plage","inclus":["Plage privée","Snorkeling","Restaurant","Excursions"]},
        ]},
        "midrange":{"color":"#27ae60","bg":"#eafaf1","hotels":[
            # Ella
            {"name":"Idyll Cottage Ella","lieu":"Ella","prix":"~68$/nuit","emoji":"🍵",
             "fort":"Ambiance montagne sereine, très bien noté — parfait pour les randonnées Ella","inclus":["Terrasse vue montagnes","Petit-déj","Nine Arch Bridge à 10 min"]},
            {"name":"Green Nature Paradise","lieu":"Ella","prix":"~89$/nuit","emoji":"🌿",
             "fort":"Juste à côté du Nine Arch Bridge, vues nature à couper le souffle","inclus":["Vue pont iconique","Jardin tropical","Restaurant"]},
            {"name":"Ella Moon Rock","lieu":"Ella","prix":"~85$/nuit","emoji":"🌄",
             "fort":"Excellent rapport qualité-prix + vues panoramiques, accès facile aux sites","inclus":["Piscine","Vue collines","Terrasse"]},
            {"name":"Monaara Leisure","lieu":"Ella","prix":"~89$/nuit","emoji":"🏡",
             "fort":"Atmosphère boutique, notes élevées, calme et charme local","inclus":["Petit-déj inclus","Terrasse","Jardin"]},
            # Habarana (safaris éléphants)
            {"name":"Gabaa Resort & Spa","lieu":"Habarana","prix":"~70$/nuit","emoji":"🐘",
             "fort":"Meilleur confort-localisation pour base safari Minneriya & Kaudulla","inclus":["Piscine","Spa","Safaris organisés","Restaurant"]},
            {"name":"Habarana Tree House","lieu":"Habarana","prix":"~72$/nuit","emoji":"🌳",
             "fort":"Expérience cabane dans les arbres unique + très bien noté","inclus":["Chambre en hauteur","Piscine","Nature autour"]},
            {"name":"TANTOR Resort & Spa","lieu":"Habarana","prix":"~75$/nuit","emoji":"🦁",
             "fort":"Solide mid-range avec bons avis, idéal pour les safaris","inclus":["Piscine","Spa","Restaurant","Navette parc"]},
            {"name":"Woodland Sanctuary","lieu":"Habarana","prix":"~97$/nuit","emoji":"🌲",
             "fort":"Lodge nature très bien noté, ambiance forêt immersive","inclus":["Piscine naturelle","Excursions nature","Petit-déj"]},
            # Trincomalee / Nilaveli
            {"name":"108 Palms Beach Resort","lieu":"Trincomalee","prix":"~88$/nuit","emoji":"🌴",
             "fort":"Ambiance beach resort dans le budget, accès plage direct","inclus":["Piscine","Restaurant bord de mer","Snorkeling"]},
            {"name":"NN Beach Resort Nilaveli","lieu":"Nilaveli","prix":"~65$/nuit","emoji":"🏝️",
             "fort":"En bord de plage avec piscine — vibe vacances parfait à petit prix","inclus":["Piscine","Plage directe","Petit-déj","Excursion Pigeon Island"]},
            {"name":"Uga Jungle Beach","lieu":"Nilaveli","prix":"~90$/nuit","emoji":"🤿",
             "fort":"Jungle + plage + nature — très aligné avec activités snorkeling et faune","inclus":["Plage","Snorkeling","Kayaks","Restaurant"]},
            # Pasikuda
            {"name":"Amaya Beach Passikudah","lieu":"Pasikuda","prix":"~63$/nuit","emoji":"🐠",
             "fort":"Meilleur resort classique dans le budget, lagon calme idéal","inclus":["Piscine","Plage lagon","Sports nautiques","Restaurant"]},
            {"name":"Amethyst Resort Passikudah","lieu":"Pasikuda","prix":"~60$/nuit","emoji":"🌊",
             "fort":"En bord de plage, fiable et bien noté, excellent rapport qualité-prix","inclus":["Piscine","Accès plage","Restaurant","Petit-déj"]},
            {"name":"The Calm Resort & Spa","lieu":"Pasikuda","prix":"~100$/nuit","emoji":"🧘",
             "fort":"Haut de gamme de la catégorie — spa, détente totale face au lagon","inclus":["Spa","Piscine infinity","Plage privée","Yoga"]},
            # Arugam Bay
            {"name":"Babar Point","lieu":"Arugam Bay","prix":"~69$/nuit","emoji":"🏄",
             "fort":"Bungalows boutique + piscine, excellentes notes — meilleur pick Arugam","inclus":["Piscine","Bungalows","Conseils surf","Restaurant"]},
            {"name":"Bay Vista","lieu":"Arugam Bay","prix":"~65$/nuit","emoji":"🌅",
             "fort":"Vue mer, position centrale, bon rapport qualité-prix","inclus":["Vue océan","Terrasse","Accès surf spots"]},
        ]},
        "budget":{"color":"#e8a020","bg":"#fef9e7","hotels":[
            {"name":"Surf N'Sun Guesthouse","lieu":"Arugam Bay","prix":"~20-45$/nuit","emoji":"🏄",
             "fort":"Au cœur du village de surf, ambiance backpacker internationale","inclus":["Location planches","Petit-déj","Conseils surf"]},
            {"name":"Arugambay Alice Rest","lieu":"Arugam Bay","prix":"~30-45$/nuit","emoji":"🌿",
             "fort":"Propre et simple, excellent rapport qualité-prix, bien noté","inclus":["Chambre confortable","Petit-déj","Accès surf spots"]},
            {"name":"Uppuveli Beach Guesthouse","lieu":"Uppuveli (Trinco)","prix":"~25-50$/nuit","emoji":"🌊",
             "fort":"À 2 min de la plage, propriétaires locaux chaleureux","inclus":["Accès plage","Vélos","Petit-déj optionnel"]},
            {"name":"Ella Flower Garden","lieu":"Ella","prix":"~25-40$/nuit","emoji":"🌸",
             "fort":"Vue montagnes, jardin tropical, très bien noté","inclus":["Terrasse panoramique","Cuisine maison","Jardin"]},
            {"name":"Sunrise Pasikuda","lieu":"Pasikuda","prix":"~35-50$/nuit","emoji":"🌅",
             "fort":"Bon séjour plage à petit budget, calme et bien situé","inclus":["Accès plage","Chambre propre","Petit-déj"]},
        ]},
    },
    "itinerary_profile":"Profil",
},
"NL": {
    # Mois & saisons
    "months": ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Aug","Sep","Okt","Nov","Dec"],
    "months_full": ["Januari","Februari","Maart","April","Mei","Juni","Juli","Augustus","September","Oktober","November","December"],
    "seasons_west_labels": ["☀️ Hoogseizoen","☀️ Hoogseizoen","☀️ Hoogseizoen","🌦 Tussenseizoen","🌧 Moesson","🌧 Moesson",
                            "🌧 Moesson","🌧 Moesson","🌦 Tussenseizoen","🌦 Tussenseizoen","☀️ Hoogseizoen","☀️ Hoogseizoen"],
    "seasons_east_labels": ["🌧 Moesson","🌧 Moesson","🌦 Tussenseizoen","☀️ Hoogseizoen","☀️ Hoogseizoen","☀️ Hoogseizoen",
                            "☀️ Hoogseizoen","☀️ Hoogseizoen","🌦 Tussenseizoen","🌦 Tussenseizoen","🌧 Moesson","🌧 Moesson"],
    # Sidebar
    "nav_title":"🌴 Navigatie",
    "how_to":"📖 Hoe gebruik je deze gids",
    "how_to_steps":"1️⃣ Kies je <b>reismaand</b> hieronder<br>2️⃣ Verken de <b>secties</b> in het menu<br>3️⃣ Bekijk de <b>kaart</b> voor de seizoenen<br>4️⃣ Ontdek alles over <b>Juni</b> — de reismaand!",
    "section_label":"📂 Sectie",
    "section_hint":"👆 Kies een sectie om te verkennen",
    "pages":["🏠 Overzicht","🌤️ Weer & Seizoenen","🗺️ Kaart van Sri Lanka","🐘 Wilde dieren","☀️ Juni in Sri Lanka"],
    "month_label":"📅 Reismaand",
    "month_selected":"Geselecteerde maand",
    "coast_label":"🌊 Voorkeurskust",
    "coast_opts":["Westkust","Oostkust","Beide"],
    "footer":"Sri Lanka Dashboard • 2025",
    # Hero
    "hero_title":"Sri Lanka Explorer",
    "hero_sub":"Uw interactieve reisgids voor de perfecte vakantie in de Parel van de Indische Oceaan",
    # Stats
    "stats":[
        {"icon":"👥","value":"22M","label":"Bevolking","color":"#1a6b3c"},
        {"icon":"📐","value":"65 610","label":"km² oppervlak","color":"#e8a020"},
        {"icon":"💰","value":"84 Mrd$","label":"BBP (USD)","color":"#c0392b"},
        {"icon":"✈️","value":"2.1M","label":"Toeristen/jaar","color":"#8e44ad"},
        {"icon":"🏖️","value":"1 340","label":"km kustlijn","color":"#2980b9"},
        {"icon":"🐘","value":"5 879","label":"Wilde olifanten","color":"#27ae60"},
        {"icon":"🍵","value":"300k t","label":"Theeproductie","color":"#d35400"},
        {"icon":"🏛️","value":"8","label":"UNESCO-sites","color":"#16a085"},
    ],
    # Vue générale
    "key_figures":"Kerngetallen",
    "reco_for":"Aanbeveling voor",
    "west_coast":"Westkust","east_coast":"Oostkust",
    "temp":"Temperatuur","rain":"Neerslag","sea":"Zee",
    "best_activities":"Beste activiteiten","avoid":"Vermijden",
    "season_haute":"☀️ Hoogseizoen","season_inter":"🌦 Tussenseizoen","season_mousson":"🌧 Moesson",
    "season_haute_desc":"Gegarandeerd zon, ideaal voor stranden",
    "season_inter_desc":"Wisselvallig, enkele regenbuien",
    "season_mousson_desc":"Frequente regen, ruwe zee",
    # Météo
    "meteo_title":"Weer & Seizoenen in Sri Lanka",
    "meteo_west":"Westkust — Colombo","meteo_east":"Oostkust — Trincomalee",
    "temp_label":"Temperatuur (°C)","rain_label":"Neerslag (mm)",
    "calendar_title":"Seizoenskalender",
    "high":"Hoogseizoen","inter":"Tussenseizoen","monsoon":"Moesson",
    # Carte
    "map_slider":"Weergegeven maand op kaart",
    "legend_title":"Legenda","region_status":"📍 Status per regio","top_spots":"⭐ Top bestemmingen",
    "haute_saison":"☀️ Hoogseizoen","haute_desc":"Grote cirkel = prioriteit",
    "inter_saison":"🌤 Tussenseizoen","inter_desc":"Wisselvallige omstandigheden",
    "mousson":"🌧 Moesson","mousson_desc":"Afgeraden",
    "nord":"Noord (Jaffna, Vanni)","cote_ouest":"Westkust (Colombo → Galle)",
    "cote_est":"Oostkust (Trinco, Arugam Bay)","centre":"Centraal (Kandy, Ella, N. Eliya)","sud":"Zuid (Yala, Mirissa, Tangalle)",
    "cal_east":"📆 Oostkust","cal_west":"📆 Westkust",
    "map_top_east":[
        ("🌊","Trincomalee","Snorkelen, dolfijnen"),("🏄","Arugam Bay","Wereldklasse surfen"),
        ("🏝️","Nilaveli","Ongerept strand"),("🐆","Yala","Safari luipaarden & olifanten"),
        ("🐘","Minneriya","Olifantenverzameling"),
    ],
    "map_top_west":[
        ("🏰","Sigiriya","Rotsfort, fresco's"),("🏯","Kandy","Tempel van de Tand"),
        ("🍵","Nuwara Eliya","Theeplantages"),("🌿","Ella","Wandelen, Nine Arch Bridge"),
        ("🏛️","Anuradhapura","Heilige stad"),
    ],
    # Faune
    "faune_title":"Wilde dieren van Sri Lanka 🐘",
    "faune_sub":"Ontdek de iconische dieren van het eiland, hun habitats en waar je ze kunt zien.",
    "filter_cat":"🔍 Filteren op categorie",
    "all_animals":"🌿 Alle dieren",
    "where_to_see":"📍 Waar te zien","best_month_lbl":"🗓️ Beste maand",
    "weight_lbl":"Gewicht","height_lbl":"Grootte","status_lbl":"Status","fun_fact_lbl":"💡 Wist je dat?",
    "wildlife": WILDLIFE_NL,
    # Juin
    "juin_title":"☀️ Juni in Sri Lanka — Oostkust",
    "juin_sub":"Juni = een van de beste maanden voor de oostkust. Zon, kalme zee, surf op z'n best, geweldige safari's — terwijl de westkust moesson heeft.",
    "juin_tip_title":"💡 Juni-strategie:",
    "juin_tip":"Vermijd de westkust (Colombo, Galle, Mirissa) tijdens de moesson. Focus op de <b>oostkust</b> (Trincomalee, Nilaveli, Uppuveli, Arugam Bay) en de <b>oostelijke natuurparken</b> (Kumana, Gal Oya). Surfen bij Arugam Bay is in volle seizoen mei–september. Poson Poya 29 juni — feestdag.",
    "juin_kpis":[
        ("🌡️","30°C","Temperatuur Oost","#e8a020"),("☀️","8u/dag","Zonneschijn","#1a6b3c"),
        ("🌊","28°C","Zee oostkust","#2980b9"),("🌧️","Moesson","Westkust","#c0392b"),
    ],
    "tab_beaches":"🏖️ Stranden & Zee","tab_safari":"🐘 Safari & Natuur",
    "tab_activities":"🎯 Activiteiten","tab_itineraries":"🗺️ Reisroutes","tab_hotels":"🏨 Hotels",
    "plages":[
        {"name":"Trincomalee + Uppuveli","emoji":"🌊","color":"#1a6b3c","note":"⭐⭐⭐⭐⭐","ambiance":"Alles-in-één basis",
         "desc":"De beste uitvalsbasis in juni. Prachtige natuurlijke baai, kristalhelder water en toegang tot alles: Pigeon Island, blauwe vinvissen, Koneswaram-tempel, Kanniya-bronnen.",
         "pour":"Gezinnen, koppels, snorkelen","acces":"5u Colombo of binnenlandse vlucht",
         "activites":["🤿 Snorkelen Pigeon Island","🐋 Blauwe vinvissen (mrt–jul)","🛕 Koneswaram-tempel","♨️ Kanniya-bronnen","🐬 Dolfijnen"]},
        {"name":"Nilaveli","emoji":"🏝️","color":"#16a085","note":"⭐⭐⭐⭐⭐","ambiance":"Rustig & ongerept",
         "desc":"5 km bijna verlaten wit zand, turquoise water. Beste toegang tot Pigeon Island. Het meest ongerepte strand van Sri Lanka.",
         "pour":"Koppels, snorkelen, rust","acces":"15 min ten noorden van Trincomalee",
         "activites":["🏊 Zwemmen in rustig water","🤿 Koraalduiken","🐠 Pigeon Island NP","🎣 Traditioneel vissen"]},
        {"name":"Arugam Bay","emoji":"🏄","color":"#2980b9","note":"⭐⭐⭐⭐⭐","ambiance":"Surfen & feest",
         "desc":"Het nummer 1 surfspot van Sri Lanka. Mei–sep = piekseizoen. Perfecte golven bij Main Point, Whiskey Point en Peanut Farm. Internationale sfeer.",
         "pour":"Surfers, backpackers, nightlife","acces":"3u van Colombo",
         "activites":["🏄 Surfen Main Point / Whiskey Pt","🐊 Safari Pottuvil Lagoon","🦜 Kumana vogels","🌅 Zonsondergangen"]},
        {"name":"Pasikuda + Kalkudah","emoji":"🐠","color":"#8e44ad","note":"⭐⭐⭐⭐","ambiance":"Resort & ontspanning",
         "desc":"Ondiepe lagune met rustig water, ideaal voor lang zwemmen. Perfect om bij te komen tussen avonturen. Snorkelen en glasbodemboot.",
         "pour":"Gezinnen, ontspanning, resort verblijf","acces":"2u ten zuiden van Trincomalee",
         "activites":["🏊 Zwemmen in rustige lagune","🐠 Snorkelen op riffen","🚤 Glasbodemboot","🌅 Rustig strand"]},
    ],
    "ideal_for":"Ideaal voor","access_lbl":"Bereikbaarheid","activities_lbl":"Activiteiten",
    "safaris":[
        {"name":"Yala National Park","emoji":"🐆","color":"#d35400","note":"⭐⭐⭐⭐⭐",
         "best":"Beste maand voor luipaarden!",
         "desc":"Droog seizoen = dieren geconcentreerd bij waterbronnen. Yala = hoogste luipaardendichtheid ter wereld. Zone 1 aanbevolen.",
         "animaux":["🐆 Luipaarden","🐘 Olifanten","🐊 Krokodillen","🦚 Pauwen","🐻 Lippenberen"],
         "conseils":"Jeeepsafari vroeg ochtend (6u). Reserveer van tevoren in juni.","tarif":"~50-80$/pers"},
        {"name":"Minneriya National Park","emoji":"🐘","color":"#8B4513","note":"⭐⭐⭐⭐⭐",
         "best":"De grote verzameling begint!",
         "desc":"The Gathering begint in juni — tot 200-300 olifanten rond het meer. Uniek spektakel ter wereld.",
         "animaux":["🐘 200-300 olifanten","🦌 Sambarherten","🐊 Krokodillen","🦅 Visarenden"],
         "conseils":"Namiddag (15-18u) is het beste moment voor de verzameling.","tarif":"~40-60$/pers"},
        {"name":"Kumana National Park","emoji":"🦜","color":"#1a6b3c","note":"⭐⭐⭐⭐⭐",
         "best":"Nestseizoen apr–jul = vogelparadijs!",
         "desc":"Juni = actief nestseizoen. Flamingo's, reigers, lepelaars, pelikanen. Vlak bij Arugam Bay.",
         "animaux":["🦜 200+ vogelsoorten","🦩 Flamingo's","🦅 Arenden","🐊 Krokodillen"],
         "conseils":"Combineer met Arugam Bay (30 min). Ornithologische gids aanbevolen.","tarif":"~30-50$/pers"},
        {"name":"Gal Oya National Park","emoji":"🐘","color":"#2980b9","note":"⭐⭐⭐⭐",
         "best":"Unieke bootsafari in Sri Lanka!",
         "desc":"Bootsafari op het stuwmeer. Olifanten zwemmen tussen eilanden — een ervaring die nergens anders bestaat.",
         "animaux":["🐘 Zwemmende olifanten","🐊 Krokodillen","🦅 Brahminy-arend","🦌 Herten"],
         "conseils":"Reserveer de bootsafari vroeg in de ochtend. Minder bekend = minder drukte.","tarif":"~40-60$/pers"},
        {"name":"Pottuvil Lagoon","emoji":"🐊","color":"#16a085","note":"⭐⭐⭐⭐",
         "best":"Vanuit Arugam Bay te doen!",
         "desc":"2 uur bootsafari in de lagune. Krokodillen gegarandeerd, mangroven, vogels, incidentele olifanten.",
         "animaux":["🐊 Krokodillen","🦜 Mangrovevogels","🐘 Olifanten (rand)","🦩 Reigers"],
         "conseils":"Vertrek bij zonsopgang voor perfect licht.","tarif":"~15-25$/pers"},
        {"name":"Udawalawe National Park","emoji":"🐘","color":"#e8a020","note":"⭐⭐⭐⭐",
         "best":"90% kans om olifanten te zien",
         "desc":"Het beste park voor olifanten het hele jaar. In juni spelen jonge olifanten bij de waterplaatsen.",
         "animaux":["🐘 Olifanten (kuddes)","🐃 Waterbuffels","🦅 Arenden","🦚 Pauwen"],
         "conseils":"Op de route Colombo–Yala, perfect als tussenstop.","tarif":"~40-60$/pers"},
    ],
    "best_lbl":"","animals_lbl":"","tips_lbl":"💡","price_lbl":"🎟️",
    "activites":[
        {"cat":"🤿 Zee & Snorkelen","color":"#2980b9","items":[
            ("Pigeon Island NP","Koralen, schildpadden, tropische vissen — boot vanuit Nilaveli","⭐⭐⭐⭐⭐"),
            ("Snorkelen Pasikuda","Ondiepe lagune, ideaal voor beginners en gezinnen","⭐⭐⭐⭐"),
            ("Duiken Trincomalee","Gevarieerde sites, uitstekend zicht in juni","⭐⭐⭐⭐"),
            ("Glasbodemboot","Rondvaart met glazen bodem, perfect zonder uitrusting","⭐⭐⭐"),
        ]},
        {"cat":"🏄 Surfen","color":"#e8a020","items":[
            ("Main Point","Iconische spot, lange regelmatige golven","⭐⭐⭐⭐⭐"),
            ("Whiskey Point","20 min van Arugam, rustiger, ideaal voor gevorderden","⭐⭐⭐⭐"),
            ("Peanut Farm","Holle golven, voor ervaren surfers","⭐⭐⭐⭐"),
            ("Surflessen","Surfkampen bieden lessen voor alle niveaus","⭐⭐⭐⭐"),
        ]},
        {"cat":"🐋 Zeeleven","color":"#1a6b3c","items":[
            ("Blauwe vinvissen Trinco","Mrt–jul = piek. Excursies vanuit Trincomalee","⭐⭐⭐⭐⭐"),
            ("Dolfijnen","Zeer frequent, vaak tijdens walvisvaarten","⭐⭐⭐⭐⭐"),
            ("Zeeschildpadden","Nilaveli en Pasikuda, snorkelen of observatie","⭐⭐⭐⭐"),
        ]},
        {"cat":"🚣 Lagunes & Kajak","color":"#16a085","items":[
            ("Batticaloa Lagoon","Kajak, mangroven, vogels, zonsondergang","⭐⭐⭐⭐"),
            ("Pottuvil Lagoon","Bootsafari: krokodillen, vogels, mangroven","⭐⭐⭐⭐⭐"),
            ("Gal Oya bootsafari","Zwemmende olifanten — unieke ervaring ter wereld","⭐⭐⭐⭐⭐"),
        ]},
        {"cat":"🛕 Cultuur & Geschiedenis","color":"#8e44ad","items":[
            ("Koneswaram-tempel","Hindoetempel op klif, 360° zeezicht","⭐⭐⭐⭐⭐"),
            ("Fort Frederick","Koloniaal fort met vrije herten, Trincomalee","⭐⭐⭐⭐"),
            ("Kanniya Warmwaterbronnen","7 heilige warmwaterbronnen, fascinerende stop","⭐⭐⭐⭐"),
            ("Kallady Bridge","Legende van de zingende vissen, zonsondergang","⭐⭐⭐"),
        ]},
        {"cat":"🍵 Thee & 🌾 Rijstvelden","color":"#5d4037","items":[
            ("Pedro Tea Estate","Historische plantage in Nuwara Eliya — begeleide rondleiding volledig proces, proeverij inbegrepen","⭐⭐⭐⭐⭐"),
            ("Mackwoods Labookellie","Op de weg Nuwara Eliya–Kandy — iconische stop, gratis proeverij met uitzicht op de heuvels","⭐⭐⭐⭐⭐"),
            ("Blue Field Tea Gardens","Ella — intiem bezoek aan plantage + ambachtelijke proeverij met panoramisch bergzicht","⭐⭐⭐⭐"),
            ("Rijstvelden Knuckles Range","Rijstterrassen uitgehouwen in bergdalen — een van de mooiste van het eiland, juni = stralend groen","⭐⭐⭐⭐⭐"),
            ("Rijstvelden Ella & Bandarawela","Rijstterrassen tussen de heuvels — goudkleurig ochtendlicht ideaal, waterbuffels in de velden","⭐⭐⭐⭐"),
        ]},
    ],
    "itins":[
        {"name":"Optie 1 — 14 dagen Stranden & Ontspanning","color":"#2980b9","emoji":"🏖️",
         "profil":"Koppels, gezinnen, snorkelen, totale rust",
         "duree":"14 dagen",
         "etapes":[
            ("4 nachten","Trincomalee / Nilaveli","🏖️ Stranden + 🤿 Pigeon Island + 🐋 Walvissen + 🛕 Koneswaram + ♨️ Kanniya",
             "🏨 NN Beach Resort (~65$) of 108 Palms (~88$)"),
            ("3 nachten","Pasikuda","🐠 Snorkelen lagune + 🚤 Glasbodemboot + totale ontspanning",
             "🏨 Amethyst Resort (~60$) of Amaya Beach (~63$)"),
            ("4 nachten","Batticaloa","🚣 Kajak lagune + 🌴 Mangroven + zonsondergang Kallady Bridge + lokale markt",
             "🏨 Lokale guesthouse (~25-40$)"),
            ("3 nachten","Arugam Bay","🏄 Surf initiatie + 🐊 Pottuvil Lagoon + 🌅 zonsondergangen",
             "🏨 Babar Point (~69$) of Bay Vista (~65$)"),
         ]},
        {"name":"Optie 2 — 14 dagen Surfen + Safari + Natuur","color":"#1a6b3c","emoji":"🏄",
         "profil":"Avonturiers, surfers, natuurliefhebbers",
         "duree":"14 dagen",
         "etapes":[
            ("3 nachten","Trincomalee","🐋 Walvisexcursie + 🤿 Snorkelen + ♨️ Kanniya + 🛕 Koneswaram",
             "🏨 Uga Jungle Beach (~90$) of 108 Palms (~88$)"),
            ("5 nachten","Arugam Bay","🏄 Surfen Main Point & Whiskey Pt + 🐊 Pottuvil Lagoon + 🦜 Kumana vogels",
             "🏨 Babar Point (~69$) of Surf N\u2019Sun (~20-45$)"),
            ("3 nachten","Pasikuda","🐠 Rustige lagune + rust + snorkelen + glasbodemboot",
             "🏨 Amethyst Resort (~60$) of The Calm (~100$)"),
            ("3 nachten","Habarana","🐘 Safari Minneriya (verzameling) + 🏰 Sigiriya + Polonnaruwa",
             "🏨 Gabaa Resort (~70$) of Habarana Tree House (~72$)"),
         ]},
        {"name":"Optie 3 — 14 dagen Thee + Oost + Safari","color":"#8e44ad","emoji":"🗺️",
         "profil":"Nieuwsgierig, cultuur + natuur + stranden — complete reis",
         "duree":"14 dagen",
         "etapes":[
            ("4 nachten","Trincomalee / Nilaveli","🌊 Stranden + 🤿 Pigeon Island + 🐋 Walvissen + 🛕 Tempels + ♨️ Kanniya",
             "🏨 NN Beach Resort (~65$) of Uga Jungle Beach (~90$)"),
            ("3 nachten","Nuwara Eliya / Ella","🍵 Pedro Tea Estate + Mackwoods + 🌾 Rijstvelden Knuckles + 🌿 Nine Arch Bridge",
             "🏨 Idyll Cottage Ella (~68$) of Ella Moon Rock (~85$)"),
            ("4 nachten","Arugam Bay","🏄 Surfen + 🐊 Pottuvil safari + 🦜 Kumana vogels + 🌅 zonsondergangen",
             "🏨 Babar Point (~69$) of Bay Vista (~65$)"),
            ("3 nachten","Yala / Udawalawe","🐆 Luipaardensafari Yala + 🐘 Olifanten Udawalawe",
             "🏨 Wild Coast Tented Lodge (~350$+) of guesthouse (~40-60$)"),
         ]},
    ],
    "practical_tips":"⚡ Praktische tips voor juni",
    "tips_list":[
        ("🏄","<b>Arugam Bay kan druk zijn</b> — reserveer surfkampen van tevoren"),
        ("☀️","<b>Zonnebrand + rashguard</b> voor snorkelen (intense zon)"),
        ("📅","<b>Poson Poya 29 juni</b> — feestdag, meer drukte en activiteiten"),
        ("🤿","<b>Niet op koraal lopen</b> — altijd met gids bij Pigeon Island"),
        ("🚗","<b>Oostkust = lange wegen</b> — overweeg chauffeur of privébus"),
        ("🐋","<b>Blauwe vinvissen</b> — mei-juli in Trincomalee, reserveer excursie"),
    ],
    "luxury":"💎 Luxe (~200-500$/nacht)","midrange":"🌿 Comfortabel (~60-100$/nacht)","budget":"🎒 Economisch (~15-55$/nacht)",
    "cat_desc_luxury":"5 sterren, premium service","cat_desc_mid":"Uitstekende prijs-kwaliteit, goed beoordeeld","cat_desc_budget":"Budgetreizigers, lokale authenticiteit",
    "highlight_lbl":"Hoogtepunt","included_lbl":"Inbegrepen",
    "hotels":{
        "luxury":{"color":"#8e44ad","bg":"#f5eef8","hotels":[
            {"name":"Wild Coast Tented Lodge","lieu":"Yala","prix":"~350-500$/nacht","emoji":"🐆",
             "fort":"Luxe tenten midden in de jungle, luipaarden voor de veranda","inclus":["Privé safari","Zwembad","Spa","Gastronomisch restaurant"]},
            {"name":"Uga Bay Resort","lieu":"Pasikuda","prix":"~250-400$/nacht","emoji":"🌊",
             "fort":"Bungalows aan zee, privéstrand turquoise oostkust","inclus":["Privéstrand","Infinity-pool","Spa","Ontbijt"]},
            {"name":"Trinco Blu by Cinnamon","lieu":"Trincomalee","prix":"~200-320$/nacht","emoji":"🌅",
             "fort":"Zeezicht vanuit alle kamers, direct strandtoegang","inclus":["Privéstrand","Snorkelen","Restaurant","Excursies"]},
        ]},
        "midrange":{"color":"#27ae60","bg":"#eafaf1","hotels":[
            # Ella
            {"name":"Idyll Cottage Ella","lieu":"Ella","prix":"~68$/nacht","emoji":"🍵",
             "fort":"Rustige bergsfeer, uitstekend beoordeeld — perfect voor Ella-wandelingen","inclus":["Terras met bergzicht","Ontbijt","Nine Arch Bridge op 10 min"]},
            {"name":"Green Nature Paradise","lieu":"Ella","prix":"~89$/nacht","emoji":"🌿",
             "fort":"Vlak bij de Nine Arch Bridge, adembenemend natuurzicht","inclus":["Zicht op iconische brug","Tropische tuin","Restaurant"]},
            {"name":"Ella Moon Rock","lieu":"Ella","prix":"~85$/nacht","emoji":"🌄",
             "fort":"Uitstekende prijs-kwaliteit + panoramisch zicht, makkelijke toegang","inclus":["Zwembad","Heuvelpanorama","Terras"]},
            {"name":"Monaara Leisure","lieu":"Ella","prix":"~89$/nacht","emoji":"🏡",
             "fort":"Boutique-gevoel, hoge beoordelingen, rustig en charmant","inclus":["Ontbijt inbegrepen","Terras","Tuin"]},
            # Habarana (olifantensafari)
            {"name":"Gabaa Resort & Spa","lieu":"Habarana","prix":"~70$/nacht","emoji":"🐘",
             "fort":"Beste comfort-locatie voor safari Minneriya & Kaudulla","inclus":["Zwembad","Spa","Georganiseerde safari's","Restaurant"]},
            {"name":"Habarana Tree House","lieu":"Habarana","prix":"~72$/nacht","emoji":"🌳",
             "fort":"Unieke boomhuisservaring + hoog beoordeeld","inclus":["Kamer op hoogte","Zwembad","Omringende natuur"]},
            {"name":"TANTOR Resort & Spa","lieu":"Habarana","prix":"~75$/nacht","emoji":"🦁",
             "fort":"Solide middenklasse met goede reviews, ideaal voor safari's","inclus":["Zwembad","Spa","Restaurant","Shuttlebus naar park"]},
            {"name":"Woodland Sanctuary","lieu":"Habarana","prix":"~97$/nacht","emoji":"🌲",
             "fort":"Zeer goed beoordeelde natuur lodge, onderdompelende bossfeer","inclus":["Natuurlijk zwembad","Natuurexcursies","Ontbijt"]},
            # Trincomalee / Nilaveli
            {"name":"108 Palms Beach Resort","lieu":"Trincomalee","prix":"~88$/nacht","emoji":"🌴",
             "fort":"Beach resort gevoel binnen budget, direct strandtoegang","inclus":["Zwembad","Restaurant aan zee","Snorkelen"]},
            {"name":"NN Beach Resort Nilaveli","lieu":"Nilaveli","prix":"~65$/nacht","emoji":"🏝️",
             "fort":"Aan het strand met zwembad — perfecte vakantiesfeer voor weinig geld","inclus":["Zwembad","Direct strand","Ontbijt","Excursie Pigeon Island"]},
            {"name":"Uga Jungle Beach","lieu":"Nilaveli","prix":"~90$/nacht","emoji":"🤿",
             "fort":"Jungle + strand + natuur — perfect afgestemd op snorkelen en fauna","inclus":["Strand","Snorkelen","Kajaks","Restaurant"]},
            # Pasikuda
            {"name":"Amaya Beach Passikudah","lieu":"Pasikuda","prix":"~63$/nacht","emoji":"🐠",
             "fort":"Beste klassieke resort in het budget, kalme lagune ideaal voor zwemmen","inclus":["Zwembad","Lagonestrand","Watersport","Restaurant"]},
            {"name":"Amethyst Resort Passikudah","lieu":"Pasikuda","prix":"~60$/nacht","emoji":"🌊",
             "fort":"Aan het strand, betrouwbaar en goed beoordeeld, uitstekende prijs","inclus":["Zwembad","Strandtoegang","Restaurant","Ontbijt"]},
            {"name":"The Calm Resort & Spa","lieu":"Pasikuda","prix":"~100$/nacht","emoji":"🧘",
             "fort":"Topklas van de categorie — spa, totale ontspanning voor de lagune","inclus":["Spa","Infinity-pool","Privéstrand","Yoga"]},
            # Arugam Bay
            {"name":"Babar Point","lieu":"Arugam Bay","prix":"~69$/nacht","emoji":"🏄",
             "fort":"Boutique bungalows + zwembad, uitstekende reviews — beste keuze Arugam","inclus":["Zwembad","Bungalows","Surftips","Restaurant"]},
            {"name":"Bay Vista","lieu":"Arugam Bay","prix":"~65$/nacht","emoji":"🌅",
             "fort":"Zeezicht, centrale ligging, goede prijs-kwaliteit","inclus":["Oceaanzicht","Terras","Toegang surfspots"]},
        ]},
        "budget":{"color":"#e8a020","bg":"#fef9e7","hotels":[
            {"name":"Surf N'Sun Guesthouse","lieu":"Arugam Bay","prix":"~20-45$/nacht","emoji":"🏄",
             "fort":"In het hart van het surfdorp, internationale backpackersfeer","inclus":["Surfplankverhuur","Ontbijt","Surftips"]},
            {"name":"Arugambay Alice Rest","lieu":"Arugam Bay","prix":"~30-45$/nacht","emoji":"🌿",
             "fort":"Proper en eenvoudig, uitstekende prijs-kwaliteit, goed beoordeeld","inclus":["Comfortabele kamer","Ontbijt","Toegang surfspots"]},
            {"name":"Uppuveli Beach Guesthouse","lieu":"Uppuveli (Trinco)","prix":"~25-50$/nacht","emoji":"🌊",
             "fort":"2 min van het strand, hartelijke lokale eigenaren","inclus":["Strandtoegang","Fietsen","Optioneel ontbijt"]},
            {"name":"Ella Flower Garden","lieu":"Ella","prix":"~25-40$/nacht","emoji":"🌸",
             "fort":"Bergzicht, tropische tuin, zeer goed beoordeeld","inclus":["Panoramisch terras","Zelfgemaakte keuken","Tuin"]},
            {"name":"Sunrise Pasikuda","lieu":"Pasikuda","prix":"~35-50$/nacht","emoji":"🌅",
             "fort":"Goed strandverblijf voor klein budget, rustig en goed gelegen","inclus":["Strandtoegang","Schone kamer","Ontbijt"]},
        ]},
    },
    "itinerary_profile":"Profiel",
},
}


with st.sidebar:
    # ── Sélecteur de langue EN HAUT ──
    lang_choice = st.radio("🌐 Langue / Taal", ["🇫🇷 Français", "🇳🇱 Nederlands"], horizontal=True)
    L = LANG["NL"] if "Nederlands" in lang_choice else LANG["FR"]

    MONTHS        = L["months"]
    SEASONS_WEST  = L["seasons_west_labels"]
    SEASONS_EAST  = L["seasons_east_labels"]

    st.markdown("---")
    st.markdown(f"## {L['nav_title']}")
    st.markdown("---")

    st.markdown(f"""
<div style='background:rgba(255,255,255,0.12);border-radius:12px;padding:14px 16px;
            margin-bottom:16px;border-left:4px solid #f0b80a'>
  <p style='color:white;font-size:0.85rem;margin:0 0 8px 0;font-weight:700'>{L['how_to']}</p>
  <p style='color:rgba(255,255,255,0.85);font-size:0.78rem;margin:0;line-height:1.6'>
    {L['how_to_steps']}
  </p>
</div>""", unsafe_allow_html=True)

    page = st.selectbox("", L["pages"])
    st.markdown("---")
    st.markdown(f"### {L['month_label']}")
    selected_month = st.select_slider("", options=MONTHS, value=MONTHS[0])
    month_idx = MONTHS.index(selected_month)
    st.markdown("---")
    st.markdown("---")
    st.markdown(f"*{L['footer']}*")




# ─── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>{L['hero_title']}</h1>
  <p>{L['hero_sub']}</p>
</div>
""", unsafe_allow_html=True)

# ─── PAGE : VUE GÉNÉRALE ───────────────────────────────────────────────────────
if page == L["pages"][0]:

    st.markdown(f'<div class="section-title">{L["key_figures"]}</div>', unsafe_allow_html=True)
    STATS = L["stats"]
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

    st.markdown(f'<div class="section-title">{L["reco_for"]} {selected_month}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    season_w = SEASONS_WEST[month_idx]
    season_e = SEASONS_EAST[month_idx]
    temp_w   = TEMP_WEST[month_idx]
    temp_e   = TEMP_EAST[month_idx]
    rain_w   = RAIN_WEST[month_idx]
    rain_e   = RAIN_EAST[month_idx]

    def coast_advice(s, west=True):
        if "Haute" in s or "Hoog" in s:
            return f"✅ {L['season_haute_desc']}"
        elif "Inter" in s or "Tussen" in s:
            return f"⚠️ {L['season_inter_desc']}"
        else:
            return f"❌ {L['season_mousson_desc']}"

    with col_a:
        color_w = "#27ae60" if ("Haute" in season_w or "Hoog" in season_w) else ("#e8a020" if ("Inter" in season_w or "Tussen" in season_w) else "#c0392b")
        st.markdown(f"""
<div style="background:white;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border-left:6px solid {color_w}">
  <h3 style="margin:0 0 12px 0">🌅 {L['west_coast']}</h3>
  <p style="font-size:1.4rem;margin:4px 0">{season_w}</p>
  <p>🌡️ {L['temp']} : <b>{temp_w}°C</b></p>
  <p>🌧️ {L['rain']} : <b>{rain_w} mm</b></p>
  <p>{coast_advice(season_w)}</p>
</div>""", unsafe_allow_html=True)

    with col_b:
        color_e = "#27ae60" if ("Haute" in season_e or "Hoog" in season_e) else ("#e8a020" if ("Inter" in season_e or "Tussen" in season_e) else "#c0392b")
        st.markdown(f"""
<div style="background:white;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border-left:6px solid {color_e}">
  <h3 style="margin:0 0 12px 0">🌄 {L['east_coast']}</h3>
  <p style="font-size:1.4rem;margin:4px 0">{season_e}</p>
  <p>🌡️ {L['temp']} : <b>{temp_e}°C</b></p>
  <p>🌧️ {L['rain']} : <b>{rain_e} mm</b></p>
  <p>{coast_advice(season_e)}</p>
</div>""", unsafe_allow_html=True)

# ─── PAGE : MÉTÉO & SAISONS ────────────────────────────────────────────────────
elif page == L["pages"][1]:

    st.markdown(f'<div class="section-title">{L["meteo_title"]}</div>', unsafe_allow_html=True)

    coast_opts = L["coast_opts"]
    coast = st.radio(L["coast_label"], coast_opts, horizontal=True)
    st.markdown("---")
    if coast == coast_opts[0]:
        temps, rains = TEMP_WEST, RAIN_WEST
    elif coast == coast_opts[1]:
        temps, rains = TEMP_EAST, RAIN_EAST
    else:
        temps, rains = TEMP_WEST, RAIN_WEST

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=MONTHS, y=rains, name=L["rain_label"],
        marker_color=["#c0392b" if r > 250 else ("#e8a020" if r > 150 else "#27ae60") for r in rains],
        yaxis="y2", opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS, y=temps, name=L["temp_label"],
        line=dict(color="#1a3a2a", width=3), mode="lines+markers",
        marker=dict(size=8, color="#e8a020")
    ))
    if coast == coast_opts[2]:
        fig.add_trace(go.Scatter(
            x=MONTHS, y=TEMP_EAST, name=f"{L['temp_label']} ({L['east_coast']})",
            line=dict(color="#2980b9", width=3, dash="dash"), mode="lines+markers",
            marker=dict(size=8, color="#2980b9")
        ))

    fig.update_layout(
        paper_bgcolor="#FFF8F0", plot_bgcolor="white",
        font=dict(family="DM Sans"), height=420,
        yaxis=dict(title=L["temp_label"], range=[20,35], color="#1a3a2a"),
        yaxis2=dict(title=L["rain_label"], overlaying="y", side="right", color="#888"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=30), xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f'<div class="section-title">{L["calendar_title"]}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    def season_color(s):
        if "Haute" in s or "Hoog" in s: return "#27ae60"
        if "Inter" in s or "Tussen" in s: return "#e8a020"
        return "#c0392b"

    with col1:
        st.markdown(f"**🌅 {L['west_coast']} (Colombo, Mirissa, Galle)**")
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"
        for m, s in zip(MONTHS, SEASONS_WEST):
            bg = season_color(s)
            html += f"<div style='background:{bg};color:white;padding:8px 12px;border-radius:10px;font-size:0.85rem;font-weight:600'>{m}<br><span style='font-size:0.75rem'>{s}</span></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with col2:
        st.markdown(f"**🌄 {L['east_coast']} (Trincomalee, Arugam Bay)**")
        html2 = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"
        for m, s in zip(MONTHS, SEASONS_EAST):
            bg = season_color(s)
            html2 += f"<div style='background:{bg};color:white;padding:8px 12px;border-radius:10px;font-size:0.85rem;font-weight:600'>{m}<br><span style='font-size:0.75rem'>{s}</span></div>"
        html2 += "</div>"
        st.markdown(html2, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)
    for col, key, desc in [
        (col3, "season_haute", "season_haute_desc"),
        (col4, "season_inter", "season_inter_desc"),
        (col5, "season_mousson", "season_mousson_desc"),
    ]:
        color = "#27ae60" if "haute" in key else ("#e8a020" if "inter" in key else "#c0392b")
        with col:
            st.markdown(f"""
<div style='background:white;border-radius:14px;padding:18px;text-align:center;
            box-shadow:0 4px 16px rgba(0,0,0,0.07);border-top:5px solid {color}'>
  <div style='font-size:1.1rem;font-weight:700;color:{color};margin-bottom:6px'>{L[key]}</div>
  <div style='color:#555;font-size:0.88rem'>{L[desc]}</div>
</div>""", unsafe_allow_html=True)

# ─── PAGE : CARTE DU SRI LANKA ────────────────────────────────────────────────
elif page == L["pages"][2]:

    MONTHS_FULL = L["months_full"]
    map_month_full = st.select_slider(L["map_slider"], options=MONTHS_FULL, value=MONTHS_FULL[5], key="big_map_slider")
    map_month = MONTHS_FULL.index(map_month_full)
    month_label = MONTHS_FULL[map_month]

    sw = SEASONS_WEST[map_month]
    se = SEASONS_EAST[map_month]
    ep = "Haute" in se or "Hoog" in se
    wp = "Haute" in sw or "Hoog" in sw

    def region_color(west=True):
        s = sw if west else se
        if "Haute" in s or "Hoog" in s: return "#27ae60", L["haute_saison"]
        if "Inter" in s or "Tussen" in s: return "#f39c12", L["inter_saison"]
        return "#e74c3c", L["mousson"]

    LIEUX = {
        "Trincomalee":     {"lat":8.5874,  "lon":81.2152, "west":False, "emoji":"🌊", "desc_key":"trinco"},
        "Arugam Bay":      {"lat":6.8397,  "lon":81.8365, "west":False, "emoji":"🏄", "desc_key":"arugam"},
        "Nilaveli":        {"lat":8.7167,  "lon":81.2167, "west":False, "emoji":"🏝️", "desc_key":"nilaveli"},
        "Uppuveli":        {"lat":8.6167,  "lon":81.2167, "west":False, "emoji":"🏖️", "desc_key":"uppuveli"},
        "Pigeon Island":   {"lat":8.7300,  "lon":81.2400, "west":False, "emoji":"🤿", "desc_key":"pigeon"},
        "Koneswaram":      {"lat":8.5680,  "lon":81.2330, "west":False, "emoji":"🛕", "desc_key":"koneswaram"},
        "Kanniya":         {"lat":8.6350,  "lon":81.1780, "west":False, "emoji":"♨️", "desc_key":"kanniya"},
        "Passikuda":       {"lat":7.9260,  "lon":81.5540, "west":False, "emoji":"🐠", "desc_key":"passikuda"},
        "Batticaloa":      {"lat":7.7167,  "lon":81.6924, "west":False, "emoji":"🚣", "desc_key":"batticaloa"},
        "Pottuvil Lagoon": {"lat":6.9000,  "lon":81.8300, "west":False, "emoji":"🐊", "desc_key":"pottuvil"},
        "Kumana":          {"lat":6.5833,  "lon":81.7167, "west":False, "emoji":"🦜", "desc_key":"kumana"},
        "Gal Oya":         {"lat":7.1667,  "lon":81.3833, "west":False, "emoji":"🐘", "desc_key":"galoya"},
        "Yala":            {"lat":6.3719,  "lon":81.5215, "west":True,  "emoji":"🐆", "desc_key":"yala"},
        "Minneriya":       {"lat":8.0333,  "lon":80.8667, "west":True,  "emoji":"🐘", "desc_key":"minneriya"},
        "Udawalawe":       {"lat":6.4740,  "lon":80.8990, "west":True,  "emoji":"🐘", "desc_key":"udawalawe"},
        "Wilpattu":        {"lat":8.4579,  "lon":80.0197, "west":True,  "emoji":"🐾", "desc_key":"wilpattu"},
        "Sigiriya":        {"lat":7.9572,  "lon":80.7603, "west":True,  "emoji":"🏰", "desc_key":"sigiriya"},
        "Kandy":           {"lat":7.2906,  "lon":80.6337, "west":True,  "emoji":"🏯", "desc_key":"kandy"},
        "Anuradhapura":    {"lat":8.3114,  "lon":80.4037, "west":True,  "emoji":"🏛️", "desc_key":"anuradhapura"},
        "Polonnaruwa":     {"lat":7.9403,  "lon":81.0188, "west":False, "emoji":"🗿", "desc_key":"polonnaruwa"},
        "Nuwara Eliya":    {"lat":6.9497,  "lon":80.7891, "west":True,  "emoji":"🍵", "desc_key":"nuwara"},
        "Ella":            {"lat":6.8667,  "lon":81.0466, "west":True,  "emoji":"🌿", "desc_key":"ella"},
        "Colombo":         {"lat":6.9271,  "lon":79.8612, "west":True,  "emoji":"🏙️", "desc_key":"colombo"},
        "Mirissa":         {"lat":5.9449,  "lon":80.4716, "west":True,  "emoji":"🐋", "desc_key":"mirissa"},
        "Galle":           {"lat":6.0535,  "lon":80.2210, "west":True,  "emoji":"🏰", "desc_key":"galle"},
        "Jaffna":          {"lat":9.6615,  "lon":80.0255, "west":True,  "emoji":"🏛️", "desc_key":"jaffna"},
        "Kalpitiya":       {"lat":8.2333,  "lon":79.7667, "west":True,  "emoji":"🐬", "desc_key":"kalpitiya"},
    }

    # Descriptions in current language
    LIEU_DESCS = {
        "FR": {
            "trinco":"Snorkeling, dauphins, plages","arugam":"Surf de classe mondiale",
            "nilaveli":"Plage immaculée, corail","uppuveli":"Plage animée, fruits de mer",
            "pigeon":"Parc marin, coraux, tortues","koneswaram":"Temple hindou sur falaise",
            "kanniya":"Sources chaudes sacrées (7 puits)","passikuda":"Lagon turquoise, snorkeling",
            "batticaloa":"Kayak lagune, mangroves","pottuvil":"Safari : crocodiles, oiseaux",
            "kumana":"Parc ornitho, nidification avr–juil","galoya":"Éléphants nageurs, safari bateau",
            "yala":"Léopards, éléphants, crocodiles","minneriya":"Rassemblement éléphants",
            "udawalawe":"Éléphants, buffles, aigles","wilpattu":"Léopards, ours lippus",
            "sigiriya":"Rocher forteresse, fresques","kandy":"Temple de la Dent du Bouddha",
            "anuradhapura":"Cité sacrée, stupas millénaires","polonnaruwa":"Ancienne capitale royale",
            "nuwara":"Plantations de thé, frais","ella":"Randonnées, Nine Arch Bridge",
            "colombo":"Capitale, gastronomie","mirissa":"Baleines bleues, snorkeling",
            "galle":"Fort colonial hollandais","jaffna":"Culture tamoule, fort",
            "kalpitiya":"Dauphins, kitesurf",
        },
        "NL": {
            "trinco":"Snorkelen, dolfijnen, stranden","arugam":"Wereldklasse surfen",
            "nilaveli":"Ongerept strand, koraal","uppuveli":"Levendig strand, zeevruchten",
            "pigeon":"Marinepark, koralen, schildpadden","koneswaram":"Hindoetempel op klif",
            "kanniya":"Heilige warmwaterbronnen (7 putten)","passikuda":"Turquoise lagune, snorkelen",
            "batticaloa":"Kajak lagune, mangroven","pottuvil":"Safari: krokodillen, vogels",
            "kumana":"Vogelpark, nestseizoen apr–jul","galoya":"Zwemmende olifanten, bootsafari",
            "yala":"Luipaarden, olifanten, krokodillen","minneriya":"Olifantenverzameling",
            "udawalawe":"Olifanten, waterbuffels, arenden","wilpattu":"Luipaarden, lippenberen",
            "sigiriya":"Rotsfort, fresco's","kandy":"Tempel van de Tand",
            "anuradhapura":"Heilige stad, eeuwenoude stupa's","polonnaruwa":"Voormalige koninklijke hoofdstad",
            "nuwara":"Theeplantages, fris klimaat","ella":"Wandelen, Nine Arch Bridge",
            "colombo":"Hoofdstad, gastronomie","mirissa":"Blauwe vinvissen, snorkelen",
            "galle":"Nederlands koloniaal fort","jaffna":"Tamilse cultuur, fort",
            "kalpitiya":"Dolfijnen, kitesurfen",
        }
    }
    lang_key = "NL" if "Nederlands" in lang_choice else "FR"
    descs = LIEU_DESCS[lang_key]

    col_map, col_panel = st.columns([3, 2])

    with col_map:
        st.markdown(f'<div class="section-title">{L["legend_title"]} — {month_label}</div>', unsafe_allow_html=True)

        import folium
        from streamlit_folium import st_folium

        m = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB positron")

        for lieu, info in LIEUX.items():
            col_hex, saison_lbl = region_color(info["west"])
            prioritaire = (not info["west"] and ep) or (info["west"] and wp)
            desc_text = descs.get(info["desc_key"], "")
            emoji_size  = "28px" if prioritaire else "20px"
            badge_size  = "11px" if prioritaire else "9px"
            shadow      = "0 2px 8px rgba(0,0,0,0.45)" if prioritaire else "0 1px 4px rgba(0,0,0,0.3)"
            opacity     = "1.0" if prioritaire else "0.72"

            icon_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;opacity:{opacity};cursor:pointer;">
  <div style="font-size:{emoji_size};filter:drop-shadow({shadow});line-height:1;">{info['emoji']}</div>
  <div style="background:{col_hex};color:white;font-size:{badge_size};font-weight:700;
              font-family:sans-serif;padding:1px 5px;border-radius:6px;margin-top:2px;
              white-space:nowrap;box-shadow:{shadow};max-width:80px;text-align:center;
              overflow:hidden;text-overflow:ellipsis;">{lieu}</div>
</div>"""

            folium.Marker(
                location=[info["lat"], info["lon"]],
                icon=folium.DivIcon(html=icon_html,
                    icon_size=(90,52) if prioritaire else (75,38),
                    icon_anchor=(45,26) if prioritaire else (37,19)),
                popup=folium.Popup(f"""
<div style='font-family:sans-serif;min-width:190px;padding:6px'>
  <div style='font-size:1.3rem;font-weight:800;color:#1a3a2a'>{info['emoji']} {lieu}</div>
  <div style='margin:5px 0;padding:3px 10px;background:{col_hex};color:white;border-radius:8px;
              font-size:0.8rem;font-weight:700;display:inline-block'>{saison_lbl}</div>
  <div style='color:#444;font-size:0.88rem;margin-top:6px'>{desc_text}</div>
</div>""", max_width=230),
                tooltip=folium.Tooltip(
                    f"<b>{info['emoji']} {lieu}</b><br>"
                    f"<span style='color:{col_hex};font-weight:700'>{saison_lbl}</span>",
                    sticky=True)
            ).add_to(m)

        st_folium(m, width=None, height=560, returned_objects=[])

    with col_panel:
        st.markdown(f"""
<div style='background:linear-gradient(140deg,#0d2137,#1a3a5c);border-radius:16px;
            padding:18px;margin-bottom:14px'>
  <p style='color:white;font-weight:800;font-size:1.05rem;margin:0 0 12px 0'>{L['legend_title']} — {month_label}</p>
  <div style='display:flex;flex-direction:column;gap:8px'>
    <div style='display:flex;align-items:center;gap:10px'>
      <div style='width:32px;height:14px;background:#27ae60;border-radius:20px;flex-shrink:0'></div>
      <span style='color:white;font-size:0.85rem'><b>{L['haute_saison']}</b> — {L['haute_desc']}</span>
    </div>
    <div style='display:flex;align-items:center;gap:10px'>
      <div style='width:32px;height:14px;background:#f39c12;border-radius:20px;flex-shrink:0'></div>
      <span style='color:white;font-size:0.85rem'><b>{L['inter_saison']}</b> — {L['inter_desc']}</span>
    </div>
    <div style='display:flex;align-items:center;gap:10px'>
      <div style='width:32px;height:14px;background:#e74c3c;border-radius:20px;flex-shrink:0'></div>
      <span style='color:white;font-size:0.85rem'><b>{L['mousson']}</b> — {L['mousson_desc']}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"<p style='font-weight:800;font-size:1rem;margin:0 0 8px 0'>{L['region_status']}</p>", unsafe_allow_html=True)
        REGS = [
            (L["nord"],       True),
            (L["cote_ouest"], True),
            (L["cote_est"],   False),
            (L["centre"],     True),
            (L["sud"],        True),
        ]
        for rname, west in REGS:
            c, lbl = region_color(west)
            bg = "#e8fdf1" if "Haute" in lbl or "Hoog" in lbl else ("#fffbe6" if "Inter" in lbl or "Tussen" in lbl else "#fdf0ef")
            st.markdown(f"""
<div style='background:{bg};border-left:5px solid {c};border-radius:10px;
            padding:9px 14px;margin-bottom:6px'>
  <b style='color:{c};font-size:0.9rem'>{rname}</b>
  <span style='color:{c};font-size:0.8rem;font-weight:700;float:right'>{lbl}</span>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        top = L["map_top_east"] if ep else L["map_top_west"]
        st.markdown(f"<p style='font-weight:800;font-size:1rem;margin:0 0 8px 0'>{L['top_spots']} — {month_label}</p>", unsafe_allow_html=True)
        c_top = "#1a9e52" if ep else "#7d3cb5"
        bg_top = "#e6faf0" if ep else "#f5eeff"
        for emoji, nom, desc in top:
            st.markdown(f"""
<div style='background:{bg_top};border-left:4px solid {c_top};border-radius:8px;
            padding:8px 12px;margin-bottom:5px'>
  <span style='font-size:1rem'>{emoji}</span>
  <b style='color:#1a3a2a;font-size:0.88rem'> {nom}</b><br>
  <span style='color:#555;font-size:0.78rem'>{desc}</span>
</div>""", unsafe_allow_html=True)

        st.markdown(f"<br><p style='font-weight:800;font-size:0.9rem;margin:0 0 5px 0'>{L['cal_east']}</p>", unsafe_allow_html=True)
        h = "<div style='display:flex;flex-wrap:wrap;gap:3px'>"
        for i,(m2,s) in enumerate(zip(MONTHS, SEASONS_EAST)):
            bg2 = "#27ae60" if ("Haute" in s or "Hoog" in s) else ("#f0b80a" if ("Inter" in s or "Tussen" in s) else "#e74c3c")
            brd = "2.5px solid #1a3a2a" if i==map_month else "2.5px solid transparent"
            h += f"<div style='background:{bg2};color:white;padding:4px 4px;border-radius:5px;font-size:0.68rem;font-weight:700;border:{brd};min-width:28px;text-align:center'>{m2}</div>"
        st.markdown(h+"</div>", unsafe_allow_html=True)

        st.markdown(f"<p style='font-weight:800;font-size:0.9rem;margin:8px 0 5px 0'>{L['cal_west']}</p>", unsafe_allow_html=True)
        h2 = "<div style='display:flex;flex-wrap:wrap;gap:3px'>"
        for i,(m2,s) in enumerate(zip(MONTHS, SEASONS_WEST)):
            bg2 = "#27ae60" if ("Haute" in s or "Hoog" in s) else ("#f0b80a" if ("Inter" in s or "Tussen" in s) else "#e74c3c")
            brd = "2.5px solid #1a3a2a" if i==map_month else "2.5px solid transparent"
            h2 += f"<div style='background:{bg2};color:white;padding:4px 4px;border-radius:5px;font-size:0.68rem;font-weight:700;border:{brd};min-width:28px;text-align:center'>{m2}</div>"
        st.markdown(h2+"</div>", unsafe_allow_html=True)

# ─── PAGE : FAUNE SAUVAGE ─────────────────────────────────────────────────────
elif page == L["pages"][3]:

    st.markdown(f'<div class="section-title">{L["faune_title"]}</div>', unsafe_allow_html=True)
    st.markdown(L["faune_sub"])

    # ── CARTE FAUNE ─────────────────────────────────────────────────────────────
    # Données géo : animal → spots avec coordonnées
    # Build name lookup from actual wildlife data
    _name_by_emoji = {}
    for _a in L["wildlife"]:
        _name_by_emoji[_a["emoji"] + _a["scientific"][:8]] = _a["name"]

    is_fr = "Nederlands" not in lang_choice

    def _wname(emoji, scientific, fr_name, nl_name):
        return fr_name if is_fr else nl_name

    WILDLIFE_SPOTS = [
        # Mammifères terrestres
        {"name":_wname("🐘","Elephas","Éléphant d'Asie","Aziatische olifant"),
         "emoji":"🐘","color":"#8B4513",
         "locs":[("Minneriya",8.0353,80.8992),("Udawalawe",6.4742,80.8994),("Kaudulla",8.1667,80.9167),
                 ("Sigiriya",7.9800,80.7500),("Gal Oya",7.0800,81.5100)]},
        {"name":_wname("","","Léopard de Ceylan","Ceylon-luipaard"),
         "emoji":"🐆","color":"#d4a017",
         "locs":[("Yala",6.3729,81.5216),("Wilpattu",8.4557,80.0233)]},
        {"name":_wname("","","Ours lippu","Lippenbeer"),
         "emoji":"🐻","color":"#6e2c00",
         "locs":[("Yala",6.3900,81.5100),("Wilpattu",8.4400,80.0100)]},
        {"name":_wname("","","Cerf axis","Axis-hert"),
         "emoji":"🦌","color":"#c8860a",
         "locs":[("Yala",6.3600,81.5300),("Wilpattu",8.4600,80.0400),("Minneriya",8.0200,80.9100),
                 ("Arugam Bay",6.8400,81.8300)]},
        {"name":_wname("","","Buffle d'eau","Waterbuffel"),
         "emoji":"🐃","color":"#555",
         "locs":[("Udawalawe",6.4600,80.9100),("Bundala",6.1500,81.2500),
                 ("Kumana",6.5700,81.6800),("Arugam Bay (rizières)",6.8600,81.8100)]},
        {"name":_wname("","","Sambhar","Sambarhert"),
         "emoji":"🦌","color":"#7d5a3c",
         "locs":[("Horton Plains",6.8020,80.8070),("Knuckles",7.4000,80.7800)]},
        # Félins
        {"name":_wname("","","Chat pêcheur","Viskat"),
         "emoji":"🐱","color":"#5d6d7e",
         "locs":[("Bundala",6.1600,81.2600),("Muthurajawela",7.1800,79.8900),
                 ("Pottuvil Lagoon",6.8750,81.8350)]},
        # Reptiles
        {"name":_wname("","","Crocodile des marais","Moerasskrokodil"),
         "emoji":"🐊","color":"#2d6a4f",
         "locs":[("Yala",6.3800,81.5150),("Bundala",6.1700,81.2400),("Maduganga",6.2200,80.1500),
                 ("Pottuvil Lagoon",6.8800,81.8400),("Batticaloa Lagoon",7.7170,81.6970),
                 ("Trincomalee (Dutch Bay)",8.5750,81.2050)]},
        {"name":_wname("","","Crocodile marin","Zeekrokodil"),
         "emoji":"🐊","color":"#1a5e3a",
         "locs":[("Bentota River",6.4200,80.0000),("Pottuvil Lagoon",6.8700,81.8450),
                 ("Trincomalee (Mangroves)",8.5500,81.1900)]},
        {"name":_wname("","","Tortue marine","Zeeschildpad"),
         "emoji":"🐢","color":"#148f77",
         "locs":[("Hikkaduwa",6.1390,80.1050),("Pigeon Island",8.7300,81.2200),
                 ("Rekawa",6.0100,80.7500),("Nilaveli",8.7000,81.2100)]},
        {"name":_wname("","","Varan indien","Indische varaan"),
         "emoji":"🦎","color":"#5d4037",
         "locs":[("Yala",6.3700,81.5250),("Wilpattu",8.4500,80.0300),
                 ("Arugam Bay",6.8500,81.8200),("Gal Oya",7.0900,81.5000)]},
        # Oiseaux
        {"name":_wname("","","Paon bleu","Indische pauw"),
         "emoji":"🦚","color":"#1a6b3c",
         "locs":[("Yala",6.3850,81.5180),("Wilpattu",8.4650,80.0200),("Udawalawe",6.4800,80.8900),
                 ("Kumana",6.5900,81.6950)]},
        {"name":_wname("","","Flamant rose","Flamingo"),
         "emoji":"🦩","color":"#e91e8c",
         "locs":[("Bundala",6.1400,81.2700),("Kumana",6.5800,81.6900),("Mannar",8.9760,79.9045)]},
        {"name":_wname("","","Aigle pêcheur","Zeearend"),
         "emoji":"🦅","color":"#7f8c8d",
         "locs":[("Minneriya",8.0300,80.9000),("Gal Oya",7.1000,81.4900),
                 ("Batticaloa Lagoon",7.7100,81.7100)]},
        {"name":_wname("","","Calao de Ceylan","Neushoornvogel"),
         "emoji":"🦜","color":"#2c3e50",
         "locs":[("Sinharaja",6.4100,80.4700),("Kitulgala",6.9900,80.4200)]},
        {"name":_wname("","","Héron pourpré","Purperreiger"),
         "emoji":"🦢","color":"#922b21",
         "locs":[("Kumana",6.5600,81.7000),("Pottuvil Lagoon",6.8650,81.8500),
                 ("Batticaloa Lagoon",7.7200,81.7000)]},
        {"name":_wname("","","Pélican","Pelikaan"),
         "emoji":"🦅","color":"#85929e",
         "locs":[("Kumana",6.5500,81.7050),("Bundala",6.1300,81.2800),("Mannar",8.9800,79.8900)]},
        # Vie marine
        {"name":_wname("","","Baleine bleue","Blauwe vinvis"),
         "emoji":"🐋","color":"#1a5276",
         "locs":[("Mirissa (bateau)",5.9450,80.4590),("Trincomalee (bateau)",8.5870,81.2152)]},
        {"name":_wname("","","Dauphin fileur","Draaiende dolfijn"),
         "emoji":"🐬","color":"#2471a3",
         "locs":[("Mirissa",5.9400,80.4650),("Kalpitiya",8.2300,79.7600),("Trincomalee",8.5600,81.2300)]},
        {"name":_wname("","","Orque","Orka"),
         "emoji":"🐳","color":"#1a1a2e",
         "locs":[("Mirissa (rare)",5.9350,80.4700)]},
        {"name":_wname("","","Tortue snorkeling","Schildpad snorkelen"),
         "emoji":"🐢","color":"#17a589",
         "locs":[("Pigeon Island",8.7350,81.2250),("Hikkaduwa",6.1350,80.1000),
                 ("Nilaveli",8.6950,81.2150)]},
        {"name":_wname("","","Raie manta","Manta-rog"),
         "emoji":"🐟","color":"#1a3a5c",
         "locs":[("Trincomalee (large)",8.6000,81.2500),("Kalpitiya",8.2400,79.7500)]},
        # Primates
        {"name":_wname("","","Macaque à toque","Toque-makaak"),
         "emoji":"🐒","color":"#c0392b",
         "locs":[("Polonnaruwa",7.9403,81.0188),("Sigiriya",7.9572,80.7603),("Dambulla",7.8731,80.6514)]},
        {"name":_wname("","","Langur de Ceylan","Ceylon-langur"),
         "emoji":"🐒","color":"#7f8c8d",
         "locs":[("Sinharaja",6.4000,80.4800),("Kandy",7.2906,80.6337)]},
        {"name":_wname("","","Langur Hanuman","Hanuman-langur"),
         "emoji":"🐵","color":"#c8860a",
         "locs":[("Jaffna",9.6615,80.0255),("Polonnaruwa",7.9500,81.0300)]},
        {"name":_wname("","","Loris de Ceylan","Plompe loris"),
         "emoji":"🦥","color":"#8e44ad",
         "locs":[("Sinharaja (nuit)",6.3950,80.4750),("Knuckles (nuit)",7.4100,80.7900)]},
    ]

    # Labels
    map_label_wildlife = "🗺️ Carte des observations — cliquez sur un animal" if is_fr else "🗺️ Kaart waarnemingen — klik op een dier"
    st.markdown(f"**{map_label_wildlife}**")

    import folium
    from streamlit_folium import st_folium

    wm = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB positron")

    for animal in WILDLIFE_SPOTS:
        for (spot_name, lat, lon) in animal["locs"]:
            icon_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;cursor:pointer;">
  <div style="font-size:22px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.4));line-height:1;">{animal['emoji']}</div>
  <div style="background:{animal['color']};color:white;font-size:9px;font-weight:700;
              font-family:sans-serif;padding:1px 5px;border-radius:5px;margin-top:1px;
              white-space:nowrap;max-width:80px;text-align:center;overflow:hidden;text-overflow:ellipsis;">{spot_name}</div>
</div>"""
            popup_name = animal['name']
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=icon_html, icon_size=(85,42), icon_anchor=(42,21)),
                popup=folium.Popup(f"""
<div style='font-family:sans-serif;min-width:180px;padding:6px'>
  <div style='font-size:1.3rem;font-weight:800;color:#1a3a2a'>{animal['emoji']} {popup_name}</div>
  <div style='color:#666;font-size:0.85rem;margin-top:4px'>📍 {spot_name}</div>
</div>""", max_width=220),
                tooltip=folium.Tooltip(f"<b>{animal['emoji']} {popup_name}</b><br><small>📍 {spot_name}</small>", sticky=True)
            ).add_to(wm)

    st_folium(wm, width=None, height=520, returned_objects=[])
    st.markdown("---")

    # ── FICHES ANIMAUX ──────────────────────────────────────────────────────────
    WILDLIFE = L["wildlife"]
    all_statuses = list(dict.fromkeys([a["status"] for a in WILDLIFE]))
    all_cats = list(dict.fromkeys([a["category"] for a in WILDLIFE]))
    filter_opts = [L["all_animals"]] + all_cats
    selected_filter = st.selectbox(L["filter_cat"], filter_opts)

    filtered = WILDLIFE if selected_filter == L["all_animals"] else [a for a in WILDLIFE if a["category"] == selected_filter]

    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j >= len(filtered): break
            a = filtered[i+j]
            with col:
                spots_html = "".join([f"<span style='background:{a['color']}22;color:{a['color']};padding:2px 8px;border-radius:8px;font-size:0.78rem;margin:2px;display:inline-block;font-weight:600'>📍 {s}</span>" for s in a["spots"]])
                st.markdown(f"""
<div style='background:{a['bg']};border-radius:18px;padding:22px;margin-bottom:18px;
            box-shadow:0 6px 20px rgba(0,0,0,0.08);border-top:6px solid {a['color']}'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:14px'>
    <span style='font-size:3rem'>{a['emoji']}</span>
    <div>
      <div style='font-family:Playfair Display,serif;font-size:1.2rem;font-weight:900;color:#1a3a2a'>{a['name']}</div>
      <div style='color:#888;font-size:0.82rem;font-style:italic'>{a['scientific']}</div>
      <span style='background:{a["status_color"]};color:white;padding:2px 10px;border-radius:10px;font-size:0.75rem;font-weight:700'>{a['status']}</span>
    </div>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px'>
    <div style='background:white;border-radius:10px;padding:10px'>
      <div style='font-size:0.72rem;color:#888;text-transform:uppercase'>{L['height_lbl']}</div>
      <div style='font-weight:700;color:{a['color']};font-size:0.9rem'>{a['size']}</div>
    </div>
    <div style='background:white;border-radius:10px;padding:10px'>
      <div style='font-size:0.72rem;color:#888;text-transform:uppercase'>{L['weight_lbl']}</div>
      <div style='font-weight:700;color:{a['color']};font-size:0.9rem'>{a['weight']}</div>
    </div>
  </div>
  <p style='color:#444;font-size:0.85rem;margin-bottom:8px'><b>🏔️</b> {a['habitat']}</p>
  <p style='color:#444;font-size:0.85rem;margin-bottom:10px'><b>🧠</b> {a['temperament']}</p>
  <div style='margin-bottom:10px'>{spots_html}</div>
  <div style='background:white;border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:0.82rem;color:#555'>
    {L['best_month_lbl']} <b style='color:{a['color']}'>{a['best_month']}</b>
  </div>
  <div style='background:{a['color']}18;border-left:4px solid {a['color']};border-radius:8px;
              padding:8px 12px;font-size:0.82rem;color:#333;font-style:italic'>
    {L['fun_fact_lbl']} {a['fun_fact']}
  </div>
</div>""", unsafe_allow_html=True)

# ─── PAGE : JUIN AU SRI LANKA ─────────────────────────────────────────────────
elif page == L["pages"][4]:

    st.markdown(f"""
<div style='background:linear-gradient(135deg,#0d6e3f 0%,#1a8a52 40%,#2980b9 100%);
            border-radius:20px;padding:30px 40px;color:white;margin-bottom:24px;
            box-shadow:0 8px 32px rgba(0,0,0,0.15)'>
  <h2 style='color:white;margin:0;font-family:Playfair Display,serif;font-size:2rem'>{L['juin_title']}</h2>
  <p style='color:rgba(255,255,255,0.9);margin-top:8px;font-size:1.05rem'>{L['juin_sub']}</p>
</div>""", unsafe_allow_html=True)

    col1,col2,col3,col4 = st.columns(4)
    for col, (icon,val,lbl,color) in zip([col1,col2,col3,col4], L["juin_kpis"]):
        with col:
            st.markdown(f"""
<div style='background:white;border-radius:14px;padding:18px;text-align:center;
            box-shadow:0 4px 16px rgba(0,0,0,0.08);border-top:5px solid {color}'>
  <div style='font-size:1.8rem'>{icon}</div>
  <div style='font-family:Playfair Display,serif;font-size:1.4rem;font-weight:900;color:{color}'>{val}</div>
  <div style='font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-top:4px'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
<div style='background:#d4efdf;border-left:6px solid #1a6b3c;border-radius:12px;
            padding:16px 20px;margin-bottom:24px'>
  <b style='color:#1a6b3c'>{L['juin_tip_title']}</b>
  <span style='color:#1a3a2a'> {L['juin_tip']}</span>
</div>""", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5 = st.tabs([L["tab_beaches"],L["tab_safari"],L["tab_activities"],L["tab_itineraries"],L["tab_hotels"]])

    # ── TAB 1 : PLAGES ──
    with tab1:
        for i in range(0, len(L["plages"]), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i+j >= len(L["plages"]): break
                p = L["plages"][i+j]
                with col:
                    acts = "".join([f'<span style="background:{p["color"]}18;color:{p["color"]};padding:3px 9px;border-radius:12px;font-size:0.78rem;font-weight:600;margin:2px;display:inline-block">{a}</span>' for a in p["activites"]])
                    st.markdown(f"""
<div style='background:white;border-radius:18px;padding:22px;margin-bottom:16px;
            box-shadow:0 6px 20px rgba(0,0,0,0.08);border-top:6px solid {p["color"]}'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
    <span style='font-size:2.4rem'>{p["emoji"]}</span>
    <div>
      <div style='font-family:Playfair Display,serif;font-size:1.1rem;font-weight:900;color:#1a3a2a'>{p["name"]}</div>
      <div style='color:{p["color"]};font-size:0.8rem;font-weight:600'>{p["ambiance"]} • {p["note"]}</div>
    </div>
  </div>
  <p style='color:#444;font-size:0.87rem;line-height:1.5;margin-bottom:12px'>{p["desc"]}</p>
  <div style='font-size:0.78rem;color:#888;margin-bottom:8px'>✅ {L['ideal_for']}: {p["pour"]} &nbsp;|&nbsp; 🚗 {L['access_lbl']}: {p["acces"]}</div>
  <div style='display:flex;flex-wrap:wrap;gap:4px'>{acts}</div>
</div>""", unsafe_allow_html=True)

    # ── TAB 2 : SAFARI ──
    with tab2:
        for i in range(0, len(L["safaris"]), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i+j >= len(L["safaris"]): break
                s = L["safaris"][i+j]
                with col:
                    anim_html = "".join([f'<span style="background:{s["color"]}18;color:{s["color"]};padding:2px 8px;border-radius:10px;font-size:0.78rem;margin:2px;display:inline-block;font-weight:600">{a}</span>' for a in s["animaux"]])
                    st.markdown(f"""
<div style='background:white;border-radius:18px;padding:20px;margin-bottom:16px;
            box-shadow:0 6px 20px rgba(0,0,0,0.08);border-top:6px solid {s["color"]}'>
  <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
    <span style='font-size:2.2rem'>{s["emoji"]}</span>
    <div>
      <div style='font-family:Playfair Display,serif;font-size:1rem;font-weight:900;color:#1a3a2a'>{s["name"]}</div>
      <div style='font-size:0.78rem'>{s["note"]}</div>
    </div>
  </div>
  <div style='background:{s["color"]}18;border-radius:8px;padding:6px 10px;margin-bottom:8px;font-size:0.82rem;font-weight:700;color:{s["color"]}'>⭐ {s["best"]}</div>
  <p style='color:#444;font-size:0.85rem;line-height:1.5;margin-bottom:10px'>{s["desc"]}</p>
  <div style='display:flex;flex-wrap:wrap;gap:3px;margin-bottom:10px'>{anim_html}</div>
  <div style='background:#fffbf0;border-left:4px solid {s["color"]};border-radius:8px;padding:8px 12px;font-size:0.82rem;color:#555;margin-bottom:6px'>💡 {s["conseils"]}</div>
  <div style='font-size:0.82rem;color:{s["color"]};font-weight:700'>🎟️ {s["tarif"]}</div>
</div>""", unsafe_allow_html=True)

    # ── TAB 3 : ACTIVITÉS ──
    with tab3:
        for act in L["activites"]:
            rows = "".join([f"""
<div style='display:flex;justify-content:space-between;align-items:flex-start;padding:8px 0;border-bottom:1px solid #f0f0f0'>
  <div><span style='font-weight:700;color:#1a3a2a;font-size:0.9rem'>{n}</span><br>
  <span style='color:#666;font-size:0.82rem'>{d}</span></div>
  <span style='font-size:0.78rem;white-space:nowrap;margin-left:8px'>{r}</span>
</div>""" for n,d,r in act["items"]])
            st.markdown(f"""
<div style='background:white;border-radius:14px;padding:18px 20px;margin-bottom:14px;
            box-shadow:0 4px 16px rgba(0,0,0,0.07);border-left:5px solid {act["color"]}'>
  <div style='font-size:1rem;font-weight:800;color:{act["color"]};margin-bottom:12px'>{act["cat"]}</div>
  {rows}
</div>""", unsafe_allow_html=True)

    # ── TAB 4 : ITINÉRAIRES ──
    with tab4:
        for itin in L["itins"]:
            etapes_html = "".join([f"""
<div style='display:flex;gap:12px;margin-bottom:10px;align-items:flex-start'>
  <div style='background:{itin["color"]};color:white;border-radius:8px;padding:4px 10px;
              font-size:0.78rem;font-weight:700;white-space:nowrap;flex-shrink:0'>{dur}</div>
  <div style='flex:1'>
    <b style='color:#1a3a2a;font-size:0.92rem'>{lieu}</b><br>
    <span style='color:#555;font-size:0.82rem'>{desc}</span><br>
    <span style='color:#888;font-size:0.78rem;font-style:italic'>{hotel}</span>
  </div>
</div>""" for dur,lieu,desc,hotel in itin["etapes"]])
            st.markdown(f"""
<div style='background:white;border-radius:18px;padding:24px;margin-bottom:18px;
            box-shadow:0 6px 24px rgba(0,0,0,0.09);border-top:6px solid {itin["color"]}'>
  <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
    <span style='font-size:2rem'>{itin["emoji"]}</span>
    <div>
      <div style='font-family:Playfair Display,serif;font-size:1.1rem;font-weight:900;color:#1a3a2a'>{itin["name"]}</div>
      <div style='color:{itin["color"]};font-size:0.82rem;font-weight:600'>⏱️ {itin["duree"]} &nbsp;|&nbsp; 👤 {L['itinerary_profile']}: {itin["profil"]}</div>
    </div>
  </div>
  <hr style='border:none;border-top:1px solid #f0f0f0;margin:14px 0'>
  {etapes_html}
</div>""", unsafe_allow_html=True)

        tips_grid = "".join([f"<div style='font-size:0.85rem;color:#1a3a2a'>{ico} {txt}</div>" for ico,txt in L["tips_list"]])
        st.markdown(f"""
<div style='background:#e8f8f0;border-left:6px solid #1a6b3c;border-radius:14px;padding:20px 24px;margin-top:8px'>
  <p style='font-weight:800;color:#1a6b3c;font-size:1rem;margin:0 0 12px 0'>{L['practical_tips']}</p>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>{tips_grid}</div>
</div>""", unsafe_allow_html=True)

    # ── TAB 5 : HÔTELS ──
    with tab5:
        for tier_key, tier_label in [("luxury", L["luxury"]), ("midrange", L["midrange"]), ("budget", L["budget"])]:
            tier = L["hotels"][tier_key]
            desc_key = {"luxury": "cat_desc_luxury", "midrange": "cat_desc_mid", "budget": "cat_desc_budget"}[tier_key]
            st.markdown(f"""
<div style='background:{tier["bg"]};border-radius:14px;padding:14px 20px;margin-bottom:12px;
            border-left:6px solid {tier["color"]}'>
  <span style='font-family:Playfair Display,serif;font-size:1.15rem;font-weight:900;color:{tier["color"]}'>{tier_label}</span>
  <span style='color:#666;font-size:0.88rem;margin-left:10px'>{L[desc_key]}</span>
</div>""", unsafe_allow_html=True)
            hotels = tier["hotels"]
            for i in range(0, len(hotels), 3):
                hcols = st.columns(3)
                for j in range(3):
                    if i+j >= len(hotels): break
                    h = hotels[i+j]
                    with hcols[j]:
                        inclus_html = "".join([f"<div style='font-size:0.8rem;color:#555;padding:1px 0'>✓ {inc}</div>" for inc in h["inclus"]])
                        st.markdown(f"""
<div style='background:white;border-radius:16px;padding:18px;margin-bottom:16px;
            box-shadow:0 4px 16px rgba(0,0,0,0.08);border-top:4px solid {tier["color"]}'>
  <div style='font-size:2rem;margin-bottom:6px'>{h["emoji"]}</div>
  <div style='font-family:Playfair Display,serif;font-size:0.95rem;font-weight:900;color:#1a3a2a;margin-bottom:3px'>{h["name"]}</div>
  <div style='color:#888;font-size:0.8rem;margin-bottom:6px'>📍 {h["lieu"]}</div>
  <div style='color:{tier["color"]};font-size:1.05rem;font-weight:900;margin-bottom:8px'>{h["prix"]}</div>
  <div style='background:{tier["bg"]};border-radius:8px;padding:7px 9px;font-size:0.81rem;color:#1a3a2a;margin-bottom:8px'>✨ {L['highlight_lbl']}: {h["fort"]}</div>
  <div style='font-size:0.8rem;font-weight:600;color:#555;margin-bottom:4px'>{L['included_lbl']}:</div>
  {inclus_html}
</div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
