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

# Portuguese translations for team names
TEAM_TRANSLATIONS = {
    # Americas
    "Mexico": "México",
    "USA": "Estados Unidos",
    "Canada": "Canadá",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "Uruguay": "Uruguai",
    "Colombia": "Colômbia",
    "Ecuador": "Equador",
    "Paraguay": "Paraguai",
    "Chile": "Chile",
    "Peru": "Peru",
    "Bolivia": "Bolívia",
    "Venezuela": "Venezuela",
    "Costa Rica": "Costa Rica",
    "Panama": "Panamá",
    "Jamaica": "Jamaica",
    "Haiti": "Haiti",

    # Europe
    "England": "Inglaterra",
    "France": "França",
    "Germany": "Alemanha",
    "Spain": "Espanha",
    "Portugal": "Portugal",
    "Italy": "Itália",
    "Netherlands": "Holanda",
    "Belgium": "Bélgica",
    "Croatia": "Croácia",
    "Switzerland": "Suíça",
    "Austria": "Áustria",
    "Poland": "Polônia",
    "Denmark": "Dinamarca",
    "Norway": "Noruega",
    "Sweden": "Suécia",
    "Scotland": "Escócia",
    "Wales": "País de Gales",
    "Czechia": "Tchéquia",
    "Slovakia": "Eslováquia",
    "Romania": "Romênia",
    "Ukraine": "Ucrânia",
    "Serbia": "Sérvia",
    "Greece": "Grécia",
    "Turkey": "Turquia",
    "Türkiye": "Turquia",
    "Ireland": "Irlanda",
    "Republic of Ireland": "República da Irlanda",
    "Northern Ireland": "Irlanda do Norte",
    "Iceland": "Islândia",
    "Finland": "Finlândia",
    "Albania": "Albânia",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "North Macedonia": "Macedônia do Norte",
    "Kosovo": "Kosovo",

    # Africa
    "Morocco": "Marrocos",
    "Algeria": "Argélia",
    "Tunisia": "Tunísia",
    "Egypt": "Egito",
    "Senegal": "Senegal",
    "Ghana": "Gana",
    "Cameroon": "Camarões",
    "Nigeria": "Nigéria",
    "South Africa": "África do Sul",
    "Cabo Verde": "Cabo Verde",
    "Côte d'Ivoire": "Costa do Marfim",
    "Ivory Coast": "Costa do Marfim",
    "DR Congo": "RD Congo",

    # Asia & Middle East
    "Japan": "Japão",
    "Korea Republic": "Coreia do Sul",
    "South Korea": "Coreia do Sul",
    "Australia": "Austrália",
    "Iran": "Irã",
    "Saudi Arabia": "Arábia Saudita",
    "Qatar": "Catar",
    "Jordan": "Jordânia",
    "Iraq": "Iraque",
    "Uzbekistan": "Uzbequistão",
    "China": "China",
    "Israel": "Israel",
    "UAE": "Emirados Árabes",
    "United Arab Emirates": "Emirados Árabes",

    # Caribbean & Others
    "Curaçao": "Curaçao",
    "Suriname": "Suriname",
    "New Zealand": "Nova Zelândia",
    "New Caledonia": "Nova Caledônia",

    # Playoffs
    "UEFA Playoff A": "Repescagem UEFA A",
    "UEFA Playoff B": "Repescagem UEFA B",
    "UEFA Playoff C": "Repescagem UEFA C",
    "UEFA Playoff D": "Repescagem UEFA D",
    "FIFA Playoff 1": "Repescagem FIFA 1",
    "FIFA Playoff 2": "Repescagem FIFA 2",
}

# FIFA 3-letter country codes for mobile display
FIFA_CODES = {
    # Americas
    "Mexico": "MEX",
    "USA": "USA",
    "Canada": "CAN",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Uruguay": "URU",
    "Colombia": "COL",
    "Ecuador": "ECU",
    "Paraguay": "PAR",
    "Chile": "CHI",
    "Peru": "PER",
    "Bolivia": "BOL",
    "Venezuela": "VEN",
    "Costa Rica": "CRC",
    "Panama": "PAN",
    "Jamaica": "JAM",
    "Haiti": "HAI",

    # Europe
    "England": "ENG",
    "France": "FRA",
    "Germany": "GER",
    "Spain": "ESP",
    "Portugal": "POR",
    "Italy": "ITA",
    "Netherlands": "NED",
    "Belgium": "BEL",
    "Croatia": "CRO",
    "Switzerland": "SUI",
    "Austria": "AUT",
    "Poland": "POL",
    "Denmark": "DEN",
    "Norway": "NOR",
    "Sweden": "SWE",
    "Scotland": "SCO",
    "Wales": "WAL",
    "Czechia": "CZE",
    "Slovakia": "SVK",
    "Romania": "ROU",
    "Ukraine": "UKR",
    "Serbia": "SRB",
    "Greece": "GRE",
    "Turkey": "TUR",
    "Türkiye": "TUR",
    "Ireland": "IRL",
    "Republic of Ireland": "IRL",
    "Northern Ireland": "NIR",
    "Iceland": "ISL",
    "Finland": "FIN",
    "Albania": "ALB",
    "Bosnia and Herzegovina": "BIH",
    "North Macedonia": "MKD",
    "Kosovo": "KOS",

    # Africa
    "Morocco": "MAR",
    "Algeria": "ALG",
    "Tunisia": "TUN",
    "Egypt": "EGY",
    "Senegal": "SEN",
    "Ghana": "GHA",
    "Cameroon": "CMR",
    "Nigeria": "NGA",
    "South Africa": "RSA",
    "Cabo Verde": "CPV",
    "Côte d'Ivoire": "CIV",
    "Ivory Coast": "CIV",
    "DR Congo": "COD",

    # Asia & Middle East
    "Japan": "JPN",
    "Korea Republic": "KOR",
    "South Korea": "KOR",
    "Australia": "AUS",
    "Iran": "IRN",
    "Saudi Arabia": "KSA",
    "Qatar": "QAT",
    "Jordan": "JOR",
    "Iraq": "IRQ",
    "Uzbekistan": "UZB",
    "China": "CHN",
    "Israel": "ISR",
    "UAE": "UAE",
    "United Arab Emirates": "UAE",

    # Caribbean & Others
    "Curaçao": "CUW",
    "Suriname": "SUR",
    "New Zealand": "NZL",
    "New Caledonia": "NCL",

    # Playoffs (abbreviated)
    "UEFA Playoff A": "UPA",
    "UEFA Playoff B": "UPB",
    "UEFA Playoff C": "UPC",
    "UEFA Playoff D": "UPD",
    "FIFA Playoff 1": "FP1",
    "FIFA Playoff 2": "FP2",
}

TEAM_TO_CODE = {
    # 2026 World Cup Teams - Group Stage
    # Group A
    "Mexico": "mx",
    "South Africa": "za",
    "Korea Republic": "kr",
    "UEFA Playoff D": "eu",  # Czechia, Denmark, North Macedonia or Republic of Ireland

    # Group B
    "Canada": "ca",
    "UEFA Playoff A": "eu",  # Bosnia and Herzegovina, Italy, Northern Ireland or Wales
    "Qatar": "qa",
    "Switzerland": "ch",

    # Group C
    "Brazil": "br",
    "Morocco": "ma",
    "Haiti": "ht",
    "Scotland": "gb-sct",

    # Group D
    "USA": "us",
    "Paraguay": "py",
    "Australia": "au",
    "UEFA Playoff C": "eu",  # Kosovo, Romania, Slovakia or Türkiye

    # Group E
    "Germany": "de",
    "Curaçao": "cw",
    "Côte d'Ivoire": "ci",
    "Ecuador": "ec",

    # Group F
    "Netherlands": "nl",
    "Japan": "jp",
    "UEFA Playoff B": "eu",  # Albania, Poland, Sweden or Ukraine
    "Tunisia": "tn",

    # Group G
    "Belgium": "be",
    "Egypt": "eg",
    "Iran": "ir",
    "New Zealand": "nz",

    # Group H
    "Spain": "es",
    "Cabo Verde": "cv",
    "Saudi Arabia": "sa",
    "Uruguay": "uy",

    # Group I
    "France": "fr",
    "Senegal": "sn",
    "FIFA Playoff 2": "xx",  # Bolivia, Iraq or Suriname
    "Norway": "no",

    # Group J
    "Argentina": "ar",
    "Algeria": "dz",
    "Austria": "at",
    "Jordan": "jo",

    # Group K
    "Portugal": "pt",
    "FIFA Playoff 1": "xx",  # DR Congo, Jamaica or New Caledonia
    "Uzbekistan": "uz",
    "Colombia": "co",

    # Group L
    "England": "gb-eng",
    "Croatia": "hr",
    "Ghana": "gh",
    "Panama": "pa",

    # Legacy teams (kept for backwards compatibility if referenced elsewhere)
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
    "decima_sexta": False,
    "oitavas": False,
    "quartas": False,
    "semi": False,
    "final3": False,
}
