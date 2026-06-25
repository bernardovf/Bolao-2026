from constants import flag_map, abbr_map, translations, PLAYER_ALIASES
from datetime import datetime, timedelta
import unicodedata

def normalize_player_name(name):
    if not name:
        return name

    # remove leading/trailing spaces
    name = name.strip()

    # remove accents for matching
    key = unicodedata.normalize("NFKD", name)
    key = "".join(c for c in key if not unicodedata.combining(c))

    # lowercase
    key = key.lower()

    # collapse multiple spaces
    key = " ".join(key.split())

    return PLAYER_ALIASES.get(key, name)

def get_flag_url(team_name):
    """Get flag URL for a team"""
    # FIFA country codes mapping
    code = flag_map.get(team_name, '')
    if code:
        return f'https://flagcdn.com/w160/{code}.png'
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
    """Format match datetime for display in Brazilian timezone (BRT - UTC-3)"""
    if not kickoff_utc:
        return None
    try:
        # Parse UTC datetime
        dt = datetime.fromisoformat(kickoff_utc.replace('Z', '+00:00'))
        # Convert to Brazilian timezone (BRT - UTC-3)
        dt_brt = dt - timedelta(hours=3)
        # Format as: "21/06 14:00"
        return dt_brt.strftime('%d/%m %H:%M')
    except:
        return None

def get_match_result(match, user_bets):
    bet = user_bets.get(match['id'])
    if not bet:
        return None

    if (bet['home_goals'] is None or bet['away_goals'] is None or
        bet['home_goals'] == 'NULL' or bet['away_goals'] == 'NULL'):
        return None

    return int(bet['home_goals']), int(bet['away_goals'])

def head_to_head_stats(teams, fixtures, user_bets):
    h2h = {
        team: {'points': 0, 'gd': 0, 'gf': 0}
        for team in teams
    }

    teams_set = set(teams)

    for match in fixtures:
        home = match['home']
        away = match['away']

        if home not in teams_set or away not in teams_set:
            continue

        result = get_match_result(match, user_bets)
        if result is None:
            continue

        home_goals, away_goals = result

        h2h[home]['gf'] += home_goals
        h2h[home]['gd'] += home_goals - away_goals

        h2h[away]['gf'] += away_goals
        h2h[away]['gd'] += away_goals - home_goals

        if home_goals > away_goals:
            h2h[home]['points'] += 3
        elif home_goals < away_goals:
            h2h[away]['points'] += 3
        else:
            h2h[home]['points'] += 1
            h2h[away]['points'] += 1

    return h2h

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

        # Skip if goals are None or 'NULL'
        if (bet['home_goals'] is None or bet['away_goals'] is None or
            bet['home_goals'] == 'NULL' or bet['away_goals'] == 'NULL'):
            continue

        # Convert to int in case SQLite returns strings
        home_goals = int(bet['home_goals'])
        away_goals = int(bet['away_goals'])

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

    sorted_standings = sort_group_standings(
        list(standings.values()),
        fixtures,
        user_bets
    )

    return sorted_standings

def sort_group_standings(standings_list, fixtures, user_bets):
    standings_by_team = {x['team']: x for x in standings_list}

    def resolve_tie(team_names):
        """
        FIFA-style recursive tie resolution:
        - apply H2H criteria among the currently tied teams
        - if some teams are separated but others remain tied,
          re-apply the same process only to the still-tied subset
        """

        if len(team_names) <= 1:
            return team_names

        h2h = head_to_head_stats(team_names, fixtures, user_bets)

        criteria = [
            lambda t: h2h[t]['points'],
            lambda t: h2h[t]['gd'],
            lambda t: h2h[t]['gf'],
            lambda t: standings_by_team[t]['gd'],
            lambda t: standings_by_team[t]['gf'],
        ]

        for criterion in criteria:
            groups = {}

            for team in team_names:
                value = criterion(team)
                groups.setdefault(value, []).append(team)

            # If this criterion separates at least something
            if len(groups) > 1:
                ordered_values = sorted(groups.keys(), reverse=True)
                resolved_order = []

                for value in ordered_values:
                    subgroup = groups[value]

                    if len(subgroup) == 1:
                        resolved_order.extend(subgroup)
                    else:
                        # Re-apply FIFA criteria only to the still-tied teams
                        resolved_order.extend(resolve_tie(subgroup))

                return resolved_order

        # If still completely tied after all available criteria
        # You can replace this later with fair play / drawing lots
        return sorted(team_names)

    # First group by total points
    points_groups = {}

    for team in standings_list:
        points_groups.setdefault(team['points'], []).append(team['team'])

    final_order_names = []

    for points in sorted(points_groups.keys(), reverse=True):
        tied_team_names = points_groups[points]

        if len(tied_team_names) == 1:
            final_order_names.extend(tied_team_names)
        else:
            final_order_names.extend(resolve_tie(tied_team_names))

    return [standings_by_team[team] for team in final_order_names]

def calculate_qualified_teams(db_execute_fn, conn, user_id=None, use_real_results=False):
    """
    Calculate which teams qualified from group stage (top 2 from each group + best 8 thirds).

    Args:
        db_execute_fn: function to execute database queries
        conn: database connection
        user_id: user ID to calculate based on their bets (ignored if use_real_results=True)
        use_real_results: if True, use real results instead of user bets

    Returns:
        set of team names that qualified
    """
    from collections import defaultdict

    # Get all group stage fixtures
    group_fixtures = db_execute_fn(conn, '''
        SELECT id, phase, home, away, final_home_goals, final_away_goals
        FROM fixtures
        WHERE phase LIKE 'Grupo %'
        ORDER BY phase, id
    ''').fetchall()

    # Group fixtures by group name
    groups = defaultdict(list)
    for fixture in group_fixtures:
        groups[fixture['phase']].append(dict(fixture))

    # Get user bets or use real results
    if use_real_results:
        # Use real results - build a dict matching bet structure
        user_bets = {}
        for fixture in group_fixtures:
            if fixture['final_home_goals'] is not None and fixture['final_away_goals'] is not None:
                user_bets[fixture['id']] = {
                    'home_goals': fixture['final_home_goals'],
                    'away_goals': fixture['final_away_goals']
                }
    else:
        # Get user's bets
        if user_id is None:
            return set()

        bets_raw = db_execute_fn(conn, '''
            SELECT match_id, home_goals, away_goals
            FROM bet
            WHERE user_id = ?
        ''', (user_id,)).fetchall()

        user_bets = {bet['match_id']: {'home_goals': bet['home_goals'], 'away_goals': bet['away_goals']}
                     for bet in bets_raw}

    # Calculate standings for each group
    qualified = set()
    all_thirds = []

    for group_name, group_fixtures in groups.items():
        standings = calculate_group_standings(group_fixtures, user_bets)

        # Top 2 from each group qualify directly
        if len(standings) >= 2:
            qualified.add(standings[0]['team'])
            qualified.add(standings[1]['team'])

        # Collect third place for best thirds comparison
        if len(standings) >= 3:
            third = standings[2]
            all_thirds.append({
                'team': third['team'],
                'points': third['points'],
                'gd': third['gd'],
                'gf': third['gf']
            })

    # Sort thirds by points, goal difference, goals for
    all_thirds.sort(key=lambda x: (x['points'], x['gd'], x['gf']), reverse=True)

    # Add best 8 thirds
    for third in all_thirds[:8]:
        qualified.add(third['team'])

    return qualified
