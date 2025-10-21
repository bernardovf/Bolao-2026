import os

LOCAL_TZ = os.environ.get("APP_TZ", "America/Sao_Paulo")

TEAM_COLOR_FALLBACKS = {
    # Americas
    "Brazil": "#046A38",
    "Argentina": "#75AADB",
    "Uruguay": "#5CBFEB",
    "Colombia": "#FCD116",
    "Chile": "#D52B1E",
    "Peru": "#D91023",
    "Paraguay": "#D52B1E",
    "Ecuador": "#FCD116",
    "Bolivia": "#007A33",
    "Venezuela": "#7F1734",
    "USA": "#3C3B6E",
    "Mexico": "#006847",
    "Canada": "#D80621",
    "Costa Rica": "#CE1126",
    "Panama": "#0055A4",
    "Honduras": "#0073CF",
    "Jamaica": "#009B3A",

    # Europe
    "France": "#0055A4",
    "England": "#CF142B",
    "Spain": "#AA151B",
    "Germany": "#000000",
    "Portugal": "#006600",
    "Italy": "#0066CC",
    "Netherlands": "#FF4F00",
    "Belgium": "#FCDD09",
    "Croatia": "#C8102E",
    "Switzerland": "#D52B1E",
    "Austria": "#ED2939",
    "Poland": "#DC143C",
    "Czechia": "#11457E",
    "Slovakia": "#0B4EA2",
    "Denmark": "#C60C30",
    "Norway": "#BA0C2F",
    "Sweden": "#006AA7",
    "Finland": "#003580",
    "Iceland": "#02529C",
    "Wales": "#00A650",
    "Scotland": "#003087",
    "Ireland": "#169B62",
    "Ukraine": "#0057B8",
    "Russia": "#0033A0",
    "Romania": "#FCD116",
    "Bulgaria": "#00966E",
    "Hungary": "#CE2939",
    "Greece": "#0D5EAF",
    "Serbia": "#C6363C",
    "Turkey": "#E30A17",
    "Switzerland": "#D52B1E",

    # Africa
    "Morocco": "#C1272D",
    "Algeria": "#006233",
    "Tunisia": "#E70013",
    "Egypt": "#CE1126",
    "Nigeria": "#008751",
    "Ghana": "#FCD116",
    "Senegal": "#00853F",
    "Cameroon": "#007A5E",
    "Ivory Coast": "#F77F00",
    "South Africa": "#007A4D",

    # Asia & Oceania
    "Japan": "#BC002D",
    "South Korea": "#C60C30",
    "Australia": "#006943",
    "Saudi Arabia": "#006C35",
    "Iran": "#239F40",
    "Qatar": "#8A1538",
    "United Arab Emirates": "#009A44",
    "China": "#DE2910",
    "India": "#FF9933",
    "Israel": "#0038B8",
    "Georgia": "#E41E20",
    "Turkey": "#E30A17",
    "Kazakhstan": "#00AEEF",
    "Uzbekistan": "#1EB53A",
    "Thailand": "#00247D",
    "Vietnam": "#DA251D",
    "Indonesia": "#CE1126",
    "Malaysia": "#0033A0",
    "New Zealand": "#00247D",
}

TEAM_TO_CODE = {
    "Qatar": "qa",
    "Ecuador": "ec",
    "Senegal": "sn",
    "Netherlands": "nl",
    "England": "gb-eng",
    "Iran": "ir",
    "USA": "us",
    "Wales": "gb-wls",
    "Argentina": "ar",
    "Saudi Arabia": "sa",
    "Mexico": "mx",
    "Poland": "pl",
    "Denmark": "dk",
    "Tunisia": "tn",
    "France": "fr",
    "Australia": "au",
    "Germany": "de",
    "Japan": "jp",
    "Spain": "es",
    "Costa Rica": "cr",
    "Morocco": "ma",
    "Croatia": "hr",
    "Belgium": "be",
    "Canada": "ca",
    "Switzerland": "ch",
    "Cameroon": "cm",
    "Brazil": "br",
    "Serbia": "rs",
    "Uruguay": "uy",
    "South Korea": "kr",
    "Portugal": "pt",
    "Ghana": "gh",
}

DB_PATH  = os.getenv("DB_PATH", "bolao_2026_dev.db")

PHASE_ROUTES = {
    "groups":        (["Group A", "Group B", "Group C", "Group D", "Group E", "Group F", "Group G", "Group H", "Group I", "Group J", "Group K", "Group L"], "fase_grupos"),
    "decima_sexta":  (["Round of 32"], "decima_sexta_final"),
    "oitavas":       (["Round of 16"], "oitavas_final"),
    "quartas":       (["Quarterfinals"], "quartas_final"),
    "semi":          (["Semifinals"], "semi_final"),
    "final":         (["Final","Third Place"], "final_terceiro"),
}

PHASE_PAGES = {
    "groups":  {"phases": [f"Group {c}" for c in "ABCDEFGHIJKL"], "template": "groups"},
    "decima_sexta": {"phases": ["Round of 32"], "template": "flat", "title": "16-AVOS DE FINAL", "button": "Salvar 16-avos de Final"},
    "oitavas": {"phases": ["Round of 16"], "template": "flat", "title": "OITAVAS", "button": "Salvar Oitavas"},
    "quartas": {"phases": ["Quarterfinals"], "template": "flat", "title": "QUARTAS", "button": "Salvar Quartas"},
    "semi":    {"phases": ["Semifinals"], "template": "flat", "title": "SEMI",    "button": "Salvar Semi"},
    "final":   {"phases": ["Third Place", "Final"], "template": "flat", "title": "FINAL E TERCEIRO", "button": "Salvar Final e Terceiro Lugar"},
}

# Phase is closed for bets (on going or passed)
PHASE_LOCKS = {
    "Groups": False,
    "Round of 32": False,
    "Round of 16": False,
    "Quarterfinals": False,
    "Semifinals":   False,
    "Final":        False,
    "General":      False
}

# Phase is still not open
unlocks = {
    "decima_sexta": True,
    "oitavas": False,
    "quartas": False,
    "semi": False,
    "final3": False,
}
