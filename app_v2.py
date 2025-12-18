"""
Bolão Copa 2026 - Fresh Modern Redesign
Clean Flask application with Tailwind CSS
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database path
DB_PATH = 'bolao_2026_dev.db'

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute a query and return results"""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute a write query"""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    rowcount = cur.rowcount
    conn.close()
    return rowcount

# ============================================================================
# HELPERS
# ============================================================================

def get_flag_url(team_name):
    """Get flag URL for a team"""
    # FIFA country codes mapping
    flag_map = {
        'Argentina': 'ar', 'Australia': 'au', 'Belgium': 'be', 'Brazil': 'br',
        'Cameroon': 'cm', 'Canada': 'ca', 'Costa Rica': 'cr', 'Croatia': 'hr',
        'Denmark': 'dk', 'Ecuador': 'ec', 'England': 'gb-eng', 'France': 'fr',
        'Germany': 'de', 'Ghana': 'gh', 'Iran': 'ir', 'Japan': 'jp',
        'Mexico': 'mx', 'Morocco': 'ma', 'Netherlands': 'nl', 'Poland': 'pl',
        'Portugal': 'pt', 'Qatar': 'qa', 'Saudi Arabia': 'sa', 'Senegal': 'sn',
        'Serbia': 'rs', 'South Korea': 'kr', 'Spain': 'es', 'Switzerland': 'ch',
        'Tunisia': 'tn', 'Uruguay': 'uy', 'USA': 'us', 'Wales': 'gb-wls',
        'Korea Republic': 'kr', 'South Africa': 'za', 'Scotland': 'gb-sct',
        'Haiti': 'ht', 'Paraguay': 'py', 'Curacao': 'cw', 'Curaçao': 'cw',
        'Ivory Coast': 'ci', 'Côte d\'Ivoire': 'ci', 'Cote d\'Ivoire': 'ci',
        'Colombia': 'co', 'Chile': 'cl', 'Peru': 'pe', 'Venezuela': 've',
        'Bolivia': 'bo', 'Panama': 'pa', 'Honduras': 'hn', 'Jamaica': 'jm',
        'Trinidad and Tobago': 'tt', 'El Salvador': 'sv', 'Guatemala': 'gt',
        'Algeria': 'dz', 'Nigeria': 'ng', 'Egypt': 'eg', 'Burkina Faso': 'bf',
        'New Zealand': 'nz', 'Cabo Verde': 'cv', 'Norway': 'no', 'Austria': 'at',
        'Jordan': 'jo', 'Uzbekistan': 'uz',
        # Playoffs (use generic flag)
        'UEFA Playoff A': 'eu', 'UEFA Playoff B': 'eu', 'UEFA Playoff C': 'eu', 'UEFA Playoff D': 'eu',
        'FIFA Playoff 1': 'eu', 'FIFA Playoff 2': 'eu', 'OFC Playoff': 'nz',
    }

    code = flag_map.get(team_name, '')
    if code:
        return f'https://flagcdn.com/w40/{code}.png'
    return None


def get_team_abbr(team_name):
    """Return a 3-letter abbreviation for a team name."""
    abbr_map = {
        'Argentina': 'ARG', 'Australia': 'AUS', 'Belgium': 'BEL', 'Brazil': 'BRA',
        'Cameroon': 'CMR', 'Canada': 'CAN', 'Costa Rica': 'CRC', 'Croatia': 'CRO',
        'Denmark': 'DEN', 'Ecuador': 'ECU', 'England': 'ENG', 'France': 'FRA',
        'Germany': 'GER', 'Ghana': 'GHA', 'Iran': 'IRN', 'Japan': 'JPN',
        'Mexico': 'MEX', 'Morocco': 'MAR', 'Netherlands': 'NED', 'Poland': 'POL',
        'Portugal': 'POR', 'Qatar': 'QAT', 'Saudi Arabia': 'KSA', 'Senegal': 'SEN',
        'Serbia': 'SRB', 'South Korea': 'KOR', 'Spain': 'ESP', 'Switzerland': 'SUI',
        'Tunisia': 'TUN', 'Uruguay': 'URU', 'USA': 'USA', 'Wales': 'WAL',
        'Korea Republic': 'KOR', 'South Africa': 'RSA', 'Scotland': 'SCO',
        'Haiti': 'HAI', 'Paraguay': 'PAR', 'Curacao': 'CUW', 'Curaçao': 'CUW',
        "Ivory Coast": 'CIV', "Côte d'Ivoire": 'CIV', "Cote d'Ivoire": 'CIV',
        'Colombia': 'COL', 'Chile': 'CHI', 'Peru': 'PER', 'Venezuela': 'VEN',
        'Bolivia': 'BOL', 'Panama': 'PAN', 'Honduras': 'HON', 'Jamaica': 'JAM',
        'Trinidad and Tobago': 'TRI', 'El Salvador': 'SLV', 'Guatemala': 'GUA',
        'Algeria': 'ALG', 'Nigeria': 'NGA', 'Egypt': 'EGY', 'Burkina Faso': 'BFA',
        'New Zealand': 'NZL', 'Cabo Verde': 'CPV', 'Norway': 'NOR', 'Austria': 'AUT',
        'Jordan': 'JOR', 'Uzbekistan': 'UZB', 'UEFA Playoff A': 'UPA',
        'UEFA Playoff B': 'UPB', 'UEFA Playoff C': 'UPC', 'UEFA Playoff D': 'UPD',
        'FIFA Playoff 1': 'FP1', 'FIFA Playoff 2': 'FP2', 'OFC Playoff': 'OFC',
    }

    if team_name in abbr_map:
        return abbr_map[team_name]

    cleaned = ''.join(ch for ch in team_name.upper() if ch.isalnum())
    if len(cleaned) >= 3:
        return cleaned[:3]
    return cleaned.ljust(3, 'X')

def calculate_match_points(bet_home, bet_away, final_home, final_away):
    """
    Calculate points for a single match
    Returns: points (int), match_type (str: 'exact', 'partial', 'miss')
    """
    if bet_home is None or bet_away is None or final_home is None or final_away is None:
        return 0, 'none'

    # Exact match: 5 points
    if bet_home == final_home and bet_away == final_away:
        return 5, 'exact'

    # Correct winner: 3 points
    bet_diff = bet_home - bet_away
    final_diff = final_home - final_away

    # Same sign (both positive, both negative, or both zero) means correct winner/draw
    if (bet_diff > 0 and final_diff > 0) or (bet_diff < 0 and final_diff < 0) or (bet_diff == 0 and final_diff == 0):
        return 3, 'partial'

    # Wrong: 0 points
    return 0, 'miss'


def translate_team_name(team_name):
    """Return Portuguese display name for a given team."""
    translations = {
        'Argentina': 'Argentina',
        'Australia': 'Austrália',
        'Belgium': 'Bélgica',
        'Brazil': 'Brasil',
        'Cameroon': 'Camarões',
        'Canada': 'Canadá',
        'Costa Rica': 'Costa Rica',
        'Croatia': 'Croácia',
        'Denmark': 'Dinamarca',
        'Ecuador': 'Equador',
        'England': 'Inglaterra',
        'France': 'França',
        'Germany': 'Alemanha',
        'Ghana': 'Gana',
        'Iran': 'Irã',
        'Japan': 'Japão',
        'Mexico': 'México',
        'Morocco': 'Marrocos',
        'Netherlands': 'Países Baixos',
        'Poland': 'Polônia',
        'Portugal': 'Portugal',
        'Qatar': 'Catar',
        'Saudi Arabia': 'Arábia Saudita',
        'Senegal': 'Senegal',
        'Serbia': 'Sérvia',
        'South Korea': 'Coreia do Sul',
        'Spain': 'Espanha',
        'Switzerland': 'Suíça',
        'Tunisia': 'Tunísia',
        'Uruguay': 'Uruguai',
        'USA': 'Estados Unidos',
        'Wales': 'País de Gales',
        'Korea Republic': 'Coreia do Sul',
        'South Africa': 'África do Sul',
        'Scotland': 'Escócia',
        'Haiti': 'Haiti',
        'Paraguay': 'Paraguai',
        'Curacao': 'Curaçao',
        'Curaçao': 'Curaçao',
        "Ivory Coast": 'Costa do Marfim',
        "Côte d'Ivoire": 'Costa do Marfim',
        "Cote d'Ivoire": 'Costa do Marfim',
        'Colombia': 'Colômbia',
        'Chile': 'Chile',
        'Peru': 'Peru',
        'Venezuela': 'Venezuela',
        'Bolivia': 'Bolívia',
        'Panama': 'Panamá',
        'Honduras': 'Honduras',
        'Jamaica': 'Jamaica',
        'Trinidad and Tobago': 'Trinidad e Tobago',
        'El Salvador': 'El Salvador',
        'Guatemala': 'Guatemala',
        'Algeria': 'Argélia',
        'Nigeria': 'Nigéria',
        'Egypt': 'Egito',
        'Burkina Faso': 'Burkina Faso',
        'New Zealand': 'Nova Zelândia',
        'Cabo Verde': 'Cabo Verde',
        'Norway': 'Noruega',
        'Austria': 'Áustria',
        'Jordan': 'Jordânia',
        'Uzbekistan': 'Uzbequistão',
        'UEFA Playoff A': 'UEFA A',
        'UEFA Playoff B': 'UEFA B',
        'UEFA Playoff C': 'UEFA C',
        'UEFA Playoff D': 'UEFA D',
        'FIFA Playoff 1': 'UEFA 1',
        'FIFA Playoff 2': 'UEFA 2',
        'OFC Playoff': 'OFC',
    }

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

# ============================================================================
# AUTHENTICATION
# ============================================================================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para continuar', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = query_db('SELECT * FROM users WHERE user_name = ? AND password = ?',
                       (username, password), one=True)

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['user_name']
            flash(f'Bem-vindo, {user["user_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos', 'error')

    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Você saiu com sucesso', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    user_name = session['user_name']

    # Get user stats
    conn = get_db()

    # Total bets
    total_bets = conn.execute(
        'SELECT COUNT(*) as count FROM bet WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']

    # Points
    points_query = '''
        SELECT
            SUM(CASE
                WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
                WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                     OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                     OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                THEN 5
                ELSE 0
            END) as total_points,
            COUNT(CASE WHEN b.home_goals = f.final_home_goals
                       AND b.away_goals = f.final_away_goals THEN 1 END) as exact_matches,
            COUNT(CASE WHEN f.final_home_goals IS NOT NULL THEN 1 END) as matches_finished
        FROM bet b
        JOIN fixtures f ON b.match_id = f.id
        WHERE b.user_id = ? AND f.final_home_goals IS NOT NULL
    '''

    stats = conn.execute(points_query, (user_id,)).fetchone()
    conn.close()

    total_points = stats['total_points'] or 0
    exact_matches = stats['exact_matches'] or 0
    matches_finished = stats['matches_finished'] or 0

    return render_template_string(DASHBOARD_TEMPLATE,
                                 user_name=user_name,
                                 total_bets=total_bets,
                                 total_points=total_points,
                                 exact_matches=exact_matches,
                                 matches_finished=matches_finished)

@app.route('/ranking')
@login_required
def ranking():
    """Rankings page"""
    conn = get_db()

    rankings = conn.execute('''
        SELECT
            u.id,
            u.user_name,
            COUNT(CASE WHEN b.home_goals = f.final_home_goals
                       AND b.away_goals = f.final_away_goals THEN 1 END) as exact_matches,
            COUNT(CASE WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                         OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                         OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                    THEN 1 END) as partial_matches,
            SUM(CASE
                WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
                WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                     OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                     OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                THEN 5
                ELSE 0
            END) as total_points
        FROM users u
        LEFT JOIN bet b ON u.id = b.user_id
        LEFT JOIN fixtures f ON b.match_id = f.id AND f.final_home_goals IS NOT NULL
        GROUP BY u.id, u.user_name
        ORDER BY total_points DESC, exact_matches DESC, u.user_name ASC
    ''').fetchall()

    conn.close()

    return render_template_string(RANKING_TEMPLATE,
                                 rankings=rankings,
                                 current_user_id=session['user_id'])

@app.route('/matches')
@login_required
def matches():
    """View and edit matches/bets"""
    conn = get_db()

    # Get all phases
    phases = conn.execute('''
        SELECT DISTINCT phase FROM fixtures ORDER BY id
    ''').fetchall()

    # Determine active phase (default to first phase)
    phase_filter = request.args.get('phase')
    if not phase_filter:
        phase_filter = phases[0]['phase'] if phases else ''

    # Get matches
    fixtures = conn.execute('''
        SELECT * FROM fixtures
        WHERE phase = ?
        ORDER BY id
    ''', (phase_filter,)).fetchall()

    # Get user's bets
    user_bets = {}
    if fixtures:
        fixture_ids = [f['id'] for f in fixtures]
        placeholders = ','.join('?' * len(fixture_ids))
        bets = conn.execute(f'''
            SELECT * FROM bet
            WHERE user_id = ? AND match_id IN ({placeholders})
        ''', [session['user_id']] + fixture_ids).fetchall()

        # Convert rows to plain dictionaries so Jinja can safely call .get()
        user_bets = {bet['match_id']: dict(bet) for bet in bets}

    # Calculate group standings if viewing group stage
    group_standings = {}
    best_third_qualifiers = set()
    if 'Group' in phase_filter:
        # Group fixtures by their specific group (e.g., "Group A", "Group B")
        from collections import defaultdict
        groups = defaultdict(list)
        for fixture in fixtures:
            groups[fixture['phase']].append(fixture)

        # Calculate standings for each group from the user's bets
        for group_name, group_fixtures in groups.items():
            group_standings[group_name] = calculate_group_standings(group_fixtures, user_bets)

        # Rank third-placed teams across all groups
        third_place_candidates = []
        for group_name, standings in group_standings.items():
            if len(standings) >= 3:
                third = standings[2].copy()
                third['group'] = group_name
                third_place_candidates.append(third)

        third_place_candidates.sort(key=lambda x: (x['points'], x['gd'], x['gf']), reverse=True)
        best_third_qualifiers = {team['team'] for team in third_place_candidates[:8]}

    conn.close()

    return render_template_string(MATCHES_TEMPLATE,
                                 fixtures=fixtures,
                                 user_bets=user_bets,
                                 phases=phases,
                                 current_phase=phase_filter,
                                 get_flag_url=get_flag_url,
                                 get_team_abbr=get_team_abbr,
                                 translate_team_name=translate_team_name,
                                 calculate_match_points=calculate_match_points,
                                 format_match_datetime=format_match_datetime,
                                 group_standings=group_standings,
                                 best_third_qualifiers=best_third_qualifiers)

@app.route('/save-bets', methods=['POST'])
@login_required
def save_bets():
    """Save user bets"""
    user_id = session['user_id']
    conn = get_db()

    saved_count = 0
    for key, value in request.form.items():
        if key.startswith('h_'):
            match_id = int(key[2:])
            away_key = f'a_{match_id}'

            if away_key in request.form:
                home_goals = request.form[key].strip()
                away_goals = request.form[away_key].strip()

                if home_goals and away_goals:
                    try:
                        home_goals = int(home_goals)
                        away_goals = int(away_goals)

                        # Insert or update
                        conn.execute('''
                            INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(user_id, match_id)
                            DO UPDATE SET home_goals=?, away_goals=?
                        ''', (user_id, match_id, home_goals, away_goals, home_goals, away_goals))

                        saved_count += 1
                    except ValueError:
                        continue

    conn.commit()
    conn.close()

    flash(f'✓ {saved_count} palpites salvos com sucesso!', 'success')

    phase = request.args.get('phase')
    if phase:
        return redirect(url_for('matches', phase=phase))
    return redirect(url_for('matches'))

# ============================================================================
# TEMPLATES
# ============================================================================

BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bolão Copa 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    {% block content %}{% endblock %}
</body>
</html>
'''

LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <div class="min-h-screen flex items-center justify-center px-4">
        <div class="max-w-md w-full">
            <!-- Logo/Title -->
            <div class="text-center mb-8">
                <h1 class="text-5xl font-black text-blue-600 mb-2">⚽ Bolão</h1>
                <p class="text-2xl font-bold text-slate-700">Copa do Mundo 2026</p>
            </div>

            <!-- Login Card -->
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <h2 class="text-2xl font-bold text-slate-800 mb-6">Entrar</h2>

                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="mb-4 p-4 rounded-lg {% if category == 'error' %}bg-red-50 text-red-800 border border-red-200{% elif category == 'success' %}bg-green-50 text-green-800 border border-green-200{% else %}bg-blue-50 text-blue-800 border border-blue-200{% endif %}">
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                <form method="POST" class="space-y-6">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Usuário</label>
                        <input type="text" name="username" required
                               class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition"
                               placeholder="Digite seu usuário">
                    </div>

                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Senha</label>
                        <input type="password" name="password" required
                               class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition"
                               placeholder="Digite sua senha">
                    </div>

                    <button type="submit"
                            class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 transition transform hover:scale-[1.02] active:scale-[0.98]">
                        Entrar
                    </button>
                </form>

                <div class="mt-6 pt-6 border-t border-slate-200">
                    <p class="text-sm text-slate-600 text-center">
                        Senha de teste: <span class="font-mono font-semibold">senha123</span>
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# More templates to continue...

DASHBOARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-2 md:space-x-3">
                    <span class="text-2xl md:text-3xl">⚽</span>
                    <span class="text-base md:text-xl font-black text-blue-600">Bolão 2026</span>
                </div>
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-semibold text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <!-- Welcome Header -->
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Olá, {{ user_name }}! 👋</h1>
            <p class="text-base md:text-lg text-slate-600">Bem-vindo ao seu painel do Bolão Copa 2026</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-6 p-4 rounded-xl {% if category == 'success' %}bg-green-50 text-green-800 border-2 border-green-200{% elif category == 'error' %}bg-red-50 text-red-800 border-2 border-red-200{% else %}bg-blue-50 text-blue-800 border-2 border-blue-200{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            <!-- Total Points -->
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6 text-white">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs md:text-sm font-semibold uppercase tracking-wide opacity-90">Total de Pontos</span>
                    <span class="text-xl md:text-2xl">🏆</span>
                </div>
                <div class="text-3xl md:text-4xl font-black">{{ total_points }}</div>
                <div class="text-xs md:text-sm opacity-75 mt-1">pontos acumulados</div>
            </div>

            <!-- Exact Matches -->
            <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6 text-white">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs md:text-sm font-semibold uppercase tracking-wide opacity-90">Palpites Exatos</span>
                    <span class="text-xl md:text-2xl">🎯</span>
                </div>
                <div class="text-3xl md:text-4xl font-black">{{ exact_matches }}</div>
                <div class="text-xs md:text-sm opacity-75 mt-1">placares corretos</div>
            </div>

            <!-- Total Bets -->
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6 text-white">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs md:text-sm font-semibold uppercase tracking-wide opacity-90">Total Palpites</span>
                    <span class="text-xl md:text-2xl">📝</span>
                </div>
                <div class="text-3xl md:text-4xl font-black">{{ total_bets }}</div>
                <div class="text-xs md:text-sm opacity-75 mt-1">jogos palpitados</div>
            </div>

            <!-- Matches Finished -->
            <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6 text-white">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs md:text-sm font-semibold uppercase tracking-wide opacity-90">Jogos Finalizados</span>
                    <span class="text-xl md:text-2xl">⚡</span>
                </div>
                <div class="text-3xl md:text-4xl font-black">{{ matches_finished }}</div>
                <div class="text-xs md:text-sm opacity-75 mt-1">resultados disponíveis</div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Make Predictions Card -->
            <a href="{{ url_for('matches') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02]">
                <div class="flex items-center space-x-4">
                    <div class="bg-blue-100 rounded-full p-4">
                        <span class="text-4xl">🎲</span>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-slate-800 mb-1">Fazer Palpites</h3>
                        <p class="text-slate-600">Aposte nos próximos jogos</p>
                    </div>
                </div>
            </a>

            <!-- View Ranking Card -->
            <a href="{{ url_for('ranking') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02]">
                <div class="flex items-center space-x-4">
                    <div class="bg-yellow-100 rounded-full p-4">
                        <span class="text-4xl">📊</span>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-slate-800 mb-1">Ver Ranking</h3>
                        <p class="text-slate-600">Confira sua posição</p>
                    </div>
                </div>
            </a>
        </div>
    </div>
</body>
</html>
'''

RANKING_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ranking - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-2 md:space-x-3">
                    <span class="text-2xl md:text-3xl">⚽</span>
                    <span class="text-base md:text-xl font-black text-blue-600">Bolão 2026</span>
                </div>
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('ranking') }}" class="font-semibold text-blue-600">Ranking</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-5xl mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">🏆 Ranking Geral</h1>
            <p class="text-base md:text-lg text-slate-600">Classificação de todos os participantes</p>
        </div>

        <!-- Ranking Table -->
        <div class="bg-white rounded-xl md:rounded-2xl shadow-xl overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                        <tr>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-left text-xs md:text-sm font-bold uppercase tracking-wider">Pos</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-left text-xs md:text-sm font-bold uppercase tracking-wider">Jogador</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-center text-xs md:text-sm font-bold uppercase tracking-wider">Exatos</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-center text-xs md:text-sm font-bold uppercase tracking-wider hidden sm:table-cell">Parciais</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-center text-xs md:text-sm font-bold uppercase tracking-wider">Pts</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        {% for rank in rankings %}
                            <tr class="{% if rank.id == current_user_id %}bg-yellow-50 border-l-4 border-yellow-500{% else %}hover:bg-slate-50{% endif %} transition">
                                <td class="px-3 md:px-6 py-3 md:py-4">
                                    <div class="flex items-center space-x-1 md:space-x-2">
                                        {% if loop.index == 1 %}
                                            <span class="text-xl md:text-2xl">🥇</span>
                                        {% elif loop.index == 2 %}
                                            <span class="text-xl md:text-2xl">🥈</span>
                                        {% elif loop.index == 3 %}
                                            <span class="text-xl md:text-2xl">🥉</span>
                                        {% else %}
                                            <span class="text-base md:text-lg font-bold text-slate-400">#{{ loop.index }}</span>
                                        {% endif %}
                                    </div>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4">
                                    <div class="font-bold text-sm md:text-base text-slate-800 truncate">
                                        {{ rank.user_name }}
                                        {% if rank.id == current_user_id %}
                                            <span class="ml-1 md:ml-2 text-xs font-semibold bg-yellow-200 text-yellow-800 px-1.5 md:px-2 py-0.5 md:py-1 rounded-full">Você</span>
                                        {% endif %}
                                    </div>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4 text-center">
                                    <span class="inline-flex items-center justify-center w-8 h-8 md:w-10 md:h-10 bg-green-100 text-green-800 text-sm md:text-base font-bold rounded-full">
                                        {{ rank.exact_matches or 0 }}
                                    </span>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4 text-center hidden sm:table-cell">
                                    <span class="inline-flex items-center justify-center w-8 h-8 md:w-10 md:h-10 bg-blue-100 text-blue-800 text-sm md:text-base font-bold rounded-full">
                                        {{ rank.partial_matches or 0 }}
                                    </span>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4 text-center">
                                    <span class="text-xl md:text-2xl font-black text-blue-600">{{ rank.total_points or 0 }}</span>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="{{ url_for('dashboard') }}" class="text-blue-600 hover:text-blue-700 font-semibold">
                ← Voltar ao Início
            </a>
        </div>
    </div>
</body>
</html>
'''

MATCHES_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palpites - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        /* Hide number input spinners */
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        input[type=number] {
            -moz-appearance: textfield;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-2 md:space-x-3">
                    <span class="text-2xl md:text-3xl">⚽</span>
                    <span class="text-base md:text-xl font-black text-blue-600">Bolão 2026</span>
                </div>
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-semibold text-blue-600">Palpites</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-6xl mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">🎲 Seus Palpites</h1>
            <p class="text-base md:text-lg text-slate-600">Aposte nos placares dos jogos</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-6 p-4 rounded-xl {% if category == 'success' %}bg-green-50 text-green-800 border-2 border-green-200{% elif category == 'error' %}bg-red-50 text-red-800 border-2 border-red-200{% else %}bg-blue-50 text-blue-800 border-2 border-blue-200{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Phase Filter -->
        <div class="mb-6">
            <label class="block text-sm font-bold text-slate-700 mb-2">Filtrar por fase ou grupo:</label>
            <select onchange="window.location.href='{{ url_for('matches') }}?phase=' + this.value"
                    class="px-4 py-2 border-2 border-slate-300 rounded-lg font-semibold focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none">
                {% for phase in phases %}
                    <option value="{{ phase.phase }}" {% if current_phase == phase.phase %}selected{% endif %}>
                        {{ phase.phase }}
                    </option>
                {% endfor %}
            </select>
        </div>

        <div class="flex flex-col md:flex-row md:items-start gap-6 md:gap-8">
            {% if group_standings %}
                <div class="md:w-5/12 lg:w-1/3">
                    {% for group_name, standings in group_standings.items()|sort %}
                        <div class="bg-white rounded-lg md:rounded-xl shadow-lg overflow-hidden">
                            <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
                                <h3 class="text-base font-black text-white">{{ group_name }}</h3>
                            </div>

                            <div class="overflow-x-auto">
                                <table class="w-full text-xs md:text-sm">
                                    <thead class="bg-slate-100 border-b-2 border-slate-200">
                                        <tr>
                                            <th class="px-2 md:px-3 py-2 text-left font-bold text-slate-700">#</th>
                                            <th class="px-2 md:px-3 py-2 text-left font-bold text-slate-700">Equipe</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">J</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">GP</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">SG</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">Pts</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-slate-200">
                                        {% for team in standings %}
                                            {% set qualifies_top = loop.index <= 2 %}
                                            {% set qualifies_third = loop.index == 3 and team.team in best_third_qualifiers %}
                                            {% set is_qualified = qualifies_top or qualifies_third %}
                                            {% set row_class = 'bg-green-50' if is_qualified else '' %}
                                            <tr class="hover:bg-slate-50 transition {{ row_class }}">
                                                <td class="px-2 md:px-3 py-2 font-bold text-slate-600">{{ loop.index }}</td>
                                                <td class="px-2 md:px-3 py-2">
                                                    <div class="flex items-center gap-1 md:gap-2">
                                                        {% set team_flag = get_flag_url(team.team) %}
                                                        {% if team_flag %}
                                                            <img src="{{ team_flag }}" alt="{{ translate_team_name(team.team) }}" class="w-4 h-3 md:w-5 md:h-4 rounded border border-slate-200 flex-shrink-0">
                                                        {% endif %}
                                                        <span class="font-semibold text-slate-800 truncate text-xs md:text-sm">{{ translate_team_name(team.team) }}</span>
                                                    </div>
                                                </td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.played }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.gf }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.gd }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.points }}</td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}

            <!-- Matches Form -->
            <div class="md:flex-1">
                <form method="POST" action="{{ url_for('save_bets', phase=current_phase) }}">
                    <div class="space-y-3 md:space-y-4">
                        {% for match in fixtures %}
                            <div class="bg-white rounded-lg md:rounded-xl shadow-md p-3 md:p-5 hover:shadow-lg transition">
                                <!-- Match Date/Time -->
                                {% set match_time = format_match_datetime(match.kickoff_utc) %}
                                {% if match_time %}
                                    <div class="text-[11px] md:text-xs text-slate-500 mb-2 md:mb-3 font-semibold">
                                        📅 {{ match_time }} 
                                    </div>
                                {% endif %}

                                <!-- Mobile: Vertical Layout, Desktop: Horizontal Layout -->
                                <div class="grid grid-cols-1 md:grid-cols-[1.1fr_0.9fr] md:items-center gap-3 md:gap-4">

                                    <!-- Teams and Inputs Section -->
                                    <div class="flex-1">
                                        <div class="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 md:gap-3">
                                            <!-- Home Team (Now inline on mobile) -->
                                            <div class="flex items-center gap-2 min-w-0 justify-end">
                                                <span class="font-extrabold text-sm text-slate-800 truncate md:hidden tracking-wide">{{ get_team_abbr(match.home) }}</span>
                                                <span class="font-bold text-sm md:text-base text-slate-800 hidden md:inline md:whitespace-normal md:leading-tight">{{ translate_team_name(match.home) }}</span>
                                                {% set home_flag = get_flag_url(match.home) %}
                                                {% if home_flag %}
                                                    <img src="{{ home_flag }}" alt="{{ translate_team_name(match.home) }}" class="w-6 h-5 md:w-7 md:h-5 rounded shadow-sm border border-slate-200 flex-shrink-0">
                                                {% endif %}
                                            </div>

                                            <!-- Score Inputs Row (Centered, stays inline on mobile) -->
                                            <div class="flex items-center justify-center gap-2 md:gap-3 mx-auto flex-shrink-0">
                                                <input type="number" name="h_{{ match.id }}" min="0" max="20"
                                                       value="{% if match.id in user_bets %}{{ user_bets[match.id]['home_goals'] }}{% endif %}"
                                                       class="w-11 h-11 md:w-14 md:h-14 text-center text-base md:text-lg font-black border-3 md:border-4 border-blue-300 rounded-lg md:rounded-xl focus:border-blue-500 focus:ring-2 md:focus:ring-3 focus:ring-blue-200 outline-none transition"
                                                       placeholder="0">

                                                <div class="flex items-center justify-center w-2 h-12 md:w-8 md:h-14">
                                                    <span class="text-base md:text-2xl font-black text-slate-400 leading-none" style="line-height: 1;">×</span>
                                                </div>

                                                <input type="number" name="a_{{ match.id }}" min="0" max="20"
                                                       value="{% if match.id in user_bets %}{{ user_bets[match.id]['away_goals'] }}{% endif %}"
                                                       class="w-11 h-11 md:w-14 md:h-14 text-center text-base md:text-lg font-black border-3 md:border-4 border-blue-300 rounded-lg md:rounded-xl focus:border-blue-500 focus:ring-2 md:focus:ring-3 focus:ring-blue-200 outline-none transition"
                                                       placeholder="0">
                                            </div>

                                            <!-- Away Team (Now inline on mobile) -->
                                            <div class="flex items-center gap-2 min-w-0 flex-shrink-0">
                                                {% set away_flag = get_flag_url(match.away) %}
                                                {% if away_flag %}
                                                    <img src="{{ away_flag }}" alt="{{ translate_team_name(match.away) }}" class="w-6 h-5 md:w-7 md:h-5 rounded shadow-sm border border-slate-200 flex-shrink-0">
                                                {% endif %}
                                                <span class="font-extrabold text-sm text-slate-800 truncate md:hidden tracking-wide">{{ get_team_abbr(match.away) }}</span>
                                                <span class="font-bold text-sm md:text-base text-slate-800 hidden md:inline md:whitespace-normal md:leading-tight">{{ translate_team_name(match.away) }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Result & Points Badges (Mobile: Full Width Below, Desktop: Right Side) -->
                                    {% set bet = user_bets.get(match.id) %}
                                    {% set points, match_type = calculate_match_points(bet.get('home_goals') if bet else None,
                                                                                      bet.get('away_goals') if bet else None,
                                                                                      match.final_home_goals, match.final_away_goals) %}
                                    <div class="w-full">
                                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 md:gap-3 items-stretch bg-white/60 md:bg-transparent">
                                            <!-- Result Badge -->
                                            <div class="flex items-center justify-between sm:justify-start gap-2 bg-gradient-to-r from-green-50 to-green-100 px-3 py-2 rounded-lg border border-green-200 shadow-sm">
                                                <div class="flex flex-col leading-tight">
                                                    <span class="text-[10px] md:text-xs font-bold text-green-700 uppercase whitespace-nowrap">Resultado</span>
                                                    <span class="text-[10px] text-green-600 font-semibold">Oficial</span>
                                                </div>
                                                {% if match.final_home_goals is not none %}
                                                    <div class="flex items-center gap-1">
                                                        <span class="text-base md:text-lg font-black text-green-800">{{ match.final_home_goals }}</span>
                                                        <span class="text-sm md:text-base font-bold text-green-600">×</span>
                                                        <span class="text-base md:text-lg font-black text-green-800">{{ match.final_away_goals }}</span>
                                                    </div>
                                                {% else %}
                                                    <span class="text-[11px] font-bold text-green-700">Aguardando</span>
                                                {% endif %}
                                            </div>

                                            <!-- Points Badge -->
                                            {% set points_classes = {
                                                'exact': 'bg-emerald-50 border-emerald-200 text-emerald-900',
                                                'partial': 'bg-amber-50 border-amber-200 text-amber-900'
                                            } %}
                                            {% set badge_class = points_classes.get(match_type, 'bg-slate-100 border-slate-200 text-slate-900') %}
                                            <div class="flex items-center justify-between sm:justify-start gap-2 px-3 py-2 rounded-lg border {{ badge_class }} shadow-sm">
                                                <div class="flex flex-col leading-tight">
                                                    <span class="text-[10px] md:text-xs font-bold uppercase whitespace-nowrap">Pontos</span>
                                                    <span class="text-[10px] text-slate-500 font-semibold">Atualizados</span>
                                                </div>
                                                {% if match.final_home_goals is not none %}
                                                    <span class="text-base md:text-lg font-black">{{ points }}</span>
                                                {% else %}
                                                    <span class="text-[11px] font-bold text-slate-600">Em breve</span>
                                                {% endif %}
                                            </div>

                                            <!-- User Bet Badge -->
                                            <div class="flex items-center justify-between sm:justify-start gap-2 bg-blue-50 px-3 py-2 rounded-lg border border-blue-200 shadow-sm">
                                                <div class="flex flex-col leading-tight">
                                                    <span class="text-[10px] md:text-xs font-bold text-blue-700 uppercase whitespace-nowrap">Seu palpite</span>
                                                    <span class="text-[10px] text-blue-500 font-semibold">Memorizado</span>
                                                </div>
                                                {% if bet %}
                                                    <div class="flex items-center gap-1 text-blue-900">
                                                        <span class="text-base md:text-lg font-black">{{ bet.get('home_goals') }}</span>
                                                        <span class="text-sm md:text-base font-bold">×</span>
                                                        <span class="text-base md:text-lg font-black">{{ bet.get('away_goals') }}</span>
                                                    </div>
                                                {% else %}
                                                    <span class="text-[11px] font-bold text-blue-600">Sem palpite</span>
                                                {% endif %}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>

                    <div class="sticky bottom-4 md:static mt-4 md:mt-6">
                        <button type="submit"
                                class="w-full md:w-auto px-6 md:px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-200 hover:shadow-blue-300 transition">
                            💾 Salvar Palpites
                        </button>
                    </div>
                </form>
            </div>
        </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

