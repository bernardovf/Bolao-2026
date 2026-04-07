from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
import os
from utils import get_flag_url, get_team_abbr, translate_team_name, format_match_datetime, calculate_group_standings
from constants import translations
from calculate_points import calculate_match_points
from templates import *

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

def migrate_palpites_gerais():
    """Add new columns to palpites_gerais table if they don't exist"""
    conn = get_db()
    cols = [row[1] for row in conn.execute("PRAGMA table_info(palpites_gerais)").fetchall()]

    if 'zebra_longe' not in cols:
        conn.execute("ALTER TABLE palpites_gerais ADD COLUMN zebra_longe TEXT")

    if 'favorito_caiu' not in cols:
        conn.execute("ALTER TABLE palpites_gerais ADD COLUMN favorito_caiu TEXT")

    if 'anfitriao_longe' not in cols:
        conn.execute("ALTER TABLE palpites_gerais ADD COLUMN anfitriao_longe TEXT")

    conn.commit()
    conn.close()

# Run migration on startup
migrate_palpites_gerais()

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
            COALESCE(SUM(CASE
                WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
                WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                     OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                     OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                THEN 5
                ELSE 0
            END), 0) as total_points
        FROM users u
        LEFT JOIN bet b ON u.id = b.user_id
        LEFT JOIN fixtures f ON b.match_id = f.id AND f.final_home_goals IS NOT NULL
        GROUP BY u.id, u.user_name
        ORDER BY total_points DESC, u.user_name ASC
    ''').fetchall()

    conn.close()

    return render_template_string(RANKING_TEMPLATE,
                                 rankings=rankings,
                                 current_user_id=session['user_id'])

@app.route('/jogador/<int:user_id>')
@login_required
def jogador_detail(user_id):
    """Player detail page with all their bets"""
    conn = get_db()

    # Get player info
    player = conn.execute('SELECT id, user_name FROM users WHERE id = ?', (user_id,)).fetchone()
    if not player:
        conn.close()
        flash('Jogador não encontrado', 'error')
        return redirect(url_for('ranking'))

    # Get all player bets with match info and points
    bets = conn.execute('''
        SELECT
            f.id as match_id,
            f.phase,
            f.home,
            f.away,
            f.kickoff_utc,
            f.final_home_goals,
            f.final_away_goals,
            b.home_goals as bet_home,
            b.away_goals as bet_away,
            CASE
                WHEN f.final_home_goals IS NULL OR f.final_away_goals IS NULL THEN NULL
                WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
                WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                     OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                     OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                THEN 5
                ELSE 0
            END as points
        FROM fixtures f
        LEFT JOIN bet b ON f.id = b.match_id AND b.user_id = ?
        ORDER BY f.id
    ''', (user_id,)).fetchall()

    # Calculate total points
    total_points = sum(bet['points'] for bet in bets if bet['points'] is not None)

    conn.close()

    return render_template_string(
        JOGADOR_DETAIL_TEMPLATE,
        player=player,
        bets=bets,
        total_points=total_points,
        translate_team_name=translate_team_name,
    )

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

@app.route('/palpites-gerais', methods=['GET', 'POST'])
@login_required
def palpites_gerais():
    """General predictions: top scorer, champion, etc."""
    user_id = session['user_id']
    conn = get_db()

    if request.method == 'POST':
        data = {
            'campeao': (request.form.get('campeao') or '').strip(),
            'artilheiro': (request.form.get('artilheiro') or '').strip(),
            'melhor_jogador': (request.form.get('melhor_jogador') or '').strip(),
            'zebra_longe': (request.form.get('zebra_longe') or '').strip(),
            'favorito_caiu': (request.form.get('favorito_caiu') or '').strip(),
            'anfitriao_longe': (request.form.get('anfitriao_longe') or '').strip(),
        }
        cur = conn.execute(
            '''UPDATE palpites_gerais
               SET campeao=?, artilheiro=?, melhor_jogador=?,
                   zebra_longe=?, favorito_caiu=?, anfitriao_longe=?, updated_at=?
               WHERE user_id=?''',
            (data['campeao'], data['artilheiro'], data['melhor_jogador'],
             data['zebra_longe'], data['favorito_caiu'], data['anfitriao_longe'],
             datetime.utcnow().isoformat(timespec='seconds'), user_id)
        )
        if cur.rowcount == 0:
            conn.execute(
                '''INSERT INTO palpites_gerais
                   (user_id, campeao, artilheiro, melhor_jogador,
                    zebra_longe, favorito_caiu, anfitriao_longe, updated_at)
                   VALUES (?,?,?,?,?,?,?)''',
                (user_id, data['campeao'], data['artilheiro'], data['melhor_jogador'],
                 data['zebra_longe'], data['favorito_caiu'], data['anfitriao_longe'],
                 datetime.utcnow().isoformat(timespec='seconds'))
            )
        conn.commit()
        conn.close()
        flash('✓ Extras salvos com sucesso!', 'success')
        return redirect(url_for('palpites_gerais'))

    row = conn.execute('SELECT * FROM palpites_gerais WHERE user_id=?', (user_id,)).fetchone()
    teams = conn.execute(
        'SELECT DISTINCT home FROM fixtures UNION SELECT DISTINCT away FROM fixtures ORDER BY 1'
    ).fetchall()
    conn.close()

    teams = [t[0] for t in teams if not t[0].startswith(('UEFA', 'FIFA'))]
    translated_teams = sorted(
        [(t, translations.get(t, t)) for t in teams],
        key=lambda x: x[1]
    )

    return render_template_string(
        PALPITES_GERAIS_TEMPLATE,
        row=dict(row) if row else {},
        translated_teams=translated_teams,
    )

@app.route('/regras')
@login_required
def regras():
    """Rules and scoring system"""
    return render_template_string(REGRAS_TEMPLATE)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

