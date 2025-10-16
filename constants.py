import os

LOCAL_TZ = os.environ.get("APP_TZ", "America/Sao_Paulo")

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
    "Groups": True,
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
