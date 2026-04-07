from constants import flag_map, abbr_map, translations
from datetime import datetime

def get_flag_url(team_name):
    """Get flag URL for a team"""
    # FIFA country codes mapping
    code = flag_map.get(team_name, '')
    if code:
        return f'https://flagcdn.com/w40/{code}.png'
    return None

def get_team_abbr(team_name):
    """Return a 3-letter abbreviation for a team name."""

    if team_name in abbr_map:
        return abbr_map[team_name]

    cleaned = ''.join(ch for ch in team_name.upper() if ch.isalnum())
    if len(cleaned) >= 3:
        return cleaned[:3]
    return cleaned.ljust(3, 'X')

def translate_team_name(team_name):
    """Return Portuguese display name for a given team."""
    return translations.get(team_name, team_name)

def format_match_datetime(kickoff_utc):
    """Format match datetime for display"""
    if not kickoff_utc:
        return None
    try:
        # Parse UTC datetime
        dt = datetime.fromisoformat(kickoff_utc.replace('Z', '+00:00'))
        # Format as: "21/06 14:00"
        return dt.strftime('%d/%m %H:%M')
    except:
        return None

def calculate_group_standings(fixtures, user_bets):
    """
    Calculate standings for teams in fixtures based on the user's bets.
    Returns: list of dicts with team stats sorted by points.
    """

    def ensure_team(team_name):
        if team_name not in standings:
            standings[team_name] = {
                'team': team_name,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'gf': 0,
                'ga': 0,
                'gd': 0,
                'points': 0
            }

    standings = {}

    for match in fixtures:
        home = match['home']
        away = match['away']
        ensure_team(home)
        ensure_team(away)

        bet = user_bets.get(match['id'])
        if not bet:
            # No bet for this match: don't count stats yet
            continue

        home_goals = bet['home_goals']
        away_goals = bet['away_goals']

        standings[home]['played'] += 1
        standings[away]['played'] += 1
        standings[home]['gf'] += home_goals
        standings[home]['ga'] += away_goals
        standings[away]['gf'] += away_goals
        standings[away]['ga'] += home_goals

        if home_goals > away_goals:  # Home win
            standings[home]['won'] += 1
            standings[home]['points'] += 3
            standings[away]['lost'] += 1
        elif home_goals < away_goals:  # Away win
            standings[away]['won'] += 1
            standings[away]['points'] += 3
            standings[home]['lost'] += 1
        else:  # Draw
            standings[home]['drawn'] += 1
            standings[away]['drawn'] += 1
            standings[home]['points'] += 1
            standings[away]['points'] += 1

        standings[home]['gd'] = standings[home]['gf'] - standings[home]['ga']
        standings[away]['gd'] = standings[away]['gf'] - standings[away]['ga']

    sorted_standings = sorted(
        standings.values(),
        key=lambda x: (x['points'], x['gd'], x['gf']),
        reverse=True
    )

    return sorted_standings
