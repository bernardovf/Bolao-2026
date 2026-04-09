from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
import os
from utils import get_flag_url, get_team_abbr, translate_team_name, format_match_datetime, calculate_group_standings, calculate_qualified_teams
from constants import translations
from calculate_points import calculate_match_points
from templates import *
import psycopg2
import psycopg2.extras

POSTGRES_AVAILABLE = True

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ============================================================================
# CONFIGURAÇÕES DO BOLÃO
# ============================================================================

# Flag para controlar se os palpites estão fechados
#
# BETTING_CLOSED = False (Palpites ABERTOS)
#   - Botões "📊 Stats" ficam ESCONDIDOS em todas as páginas
#   - Nomes no Ranking NÃO são clicáveis
#   - Jogadores não podem ver palpites dos outros
#
# BETTING_CLOSED = True (Palpites FECHADOS)
#   - Botões "📊 Stats" ficam VISÍVEIS
#   - Nomes no Ranking são clicáveis
#   - Todos podem ver estatísticas e palpites dos outros
#
# IMPORTANTE: Altere para True um dia antes do início das partidas!
BETTING_CLOSED = True

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database URL - usa PostgreSQL em produção, SQLite local para desenvolvimento
DATABASE_URL = os.environ.get('DATABASE_URL')

# Se DATABASE_URL existe (Render), usa PostgreSQL
# Se não existe (desenvolvimento local), usa SQLite
if DATABASE_URL:
    # Render/PostgreSQL
    # Fix: Render usa postgres:// mas psycopg2 precisa de postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    DB_PATH = None
else:
    # Local/SQLite
    DB_PATH = 'bolao_2026_dev.db'
    DATABASE_URL = None

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db():
    """Get database connection - PostgreSQL ou SQLite"""
    if DATABASE_URL and POSTGRES_AVAILABLE:
        # PostgreSQL (produção)
        return psycopg2.connect(DATABASE_URL)
    else:
        # SQLite (desenvolvimento local)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def _is_postgres_connection(conn):
    """Check if connection is PostgreSQL"""
    return DATABASE_URL and POSTGRES_AVAILABLE and isinstance(conn, psycopg2.extensions.connection)

def _adapt_query_for_postgres(query):
    """Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)."""
    return query.replace('?', '%s')

def db_execute(conn, query, args=()):
    """Execute query in a backend-agnostic way (SQLite/PostgreSQL)."""
    if _is_postgres_connection(conn):
        query = _adapt_query_for_postgres(query)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, args)
        return cur

    return conn.execute(query, args)

def query_db(query, args=(), one=False):
    """Execute a query and return results"""
    conn = get_db()
    cur = db_execute(conn, query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute a write query"""
    conn = get_db()
    cur = db_execute(conn, query, args)
    conn.commit()
    rowcount = cur.rowcount
    conn.close()
    return rowcount

def migrate_palpites_gerais():
    """Add new columns to palpites_gerais table if they don't exist"""
    # Skip migrations for PostgreSQL (schema is created from init_db.sql)
    if DATABASE_URL:
        return

    conn = get_db()
    cols = [row[1] for row in db_execute(conn, "PRAGMA table_info(palpites_gerais)").fetchall()]

    if 'zebra_longe' not in cols:
        db_execute(conn, "ALTER TABLE palpites_gerais ADD COLUMN zebra_longe TEXT")

    if 'favorito_caiu' not in cols:
        db_execute(conn, "ALTER TABLE palpites_gerais ADD COLUMN favorito_caiu TEXT")

    if 'anfitriao_longe' not in cols:
        db_execute(conn, "ALTER TABLE palpites_gerais ADD COLUMN anfitriao_longe TEXT")

    conn.commit()
    conn.close()

def migrate_bet_table():
    """Recreate bet table without foreign key constraints"""
    # Skip migrations for PostgreSQL (schema is created from init_db.sql)
    if DATABASE_URL:
        return

    conn = get_db()

    # Check if we need to migrate (check if foreign keys exist)
    cursor = db_execute(conn, "PRAGMA foreign_key_list(bet)")
    foreign_keys = cursor.fetchall()

    # If foreign keys reference 'user' or 'match' tables, we need to migrate
    needs_migration = any(fk[2] in ('user', 'match') for fk in foreign_keys)

    if needs_migration:
        print("Migrating bet table...")

        # Backup existing data
        db_execute(conn, "CREATE TABLE bet_backup AS SELECT * FROM bet")

        # Drop old table
        db_execute(conn, "DROP TABLE bet")

        # Create new table without problematic foreign keys
        db_execute(conn, '''
            CREATE TABLE bet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                match_id INTEGER NOT NULL,
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                UNIQUE(user_id, match_id)
            )
        ''')

        # Restore data
        db_execute(conn, '''
            INSERT INTO bet (id, user_id, match_id, home_goals, away_goals)
            SELECT id, user_id, match_id, home_goals, away_goals FROM bet_backup
        ''')

        # Drop backup table
        db_execute(conn, "DROP TABLE bet_backup")

        conn.commit()
        print("Bet table migration completed")

    conn.close()

# Run migrations on startup
migrate_palpites_gerais()
migrate_bet_table()

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
    total_bets = db_execute(conn, 
        'SELECT COUNT(*) as count FROM bet WHERE user_id = ?',
        (user_id,)
    ).fetchone()['count']

    # Get all user bets with results
    user_bets = db_execute(conn, '''
        SELECT b.home_goals as bet_home, b.away_goals as bet_away,
               f.final_home_goals, f.final_away_goals
        FROM bet b
        JOIN fixtures f ON b.match_id = f.id
        WHERE b.user_id = ? AND f.final_home_goals IS NOT NULL
    ''', (user_id,)).fetchall()

    conn.close()

    # Calculate points and stats using calculate_match_points
    total_points = 0
    exact_matches = 0
    matches_finished = len(user_bets)

    for bet in user_bets:
        points, match_type = calculate_match_points(
            bet['bet_home'], bet['bet_away'],
            bet['final_home_goals'], bet['final_away_goals']
        )
        total_points += points
        if match_type == 'exact':
            exact_matches += 1

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

    # Get all users
    users = db_execute(conn, 'SELECT id, user_name FROM users ORDER BY user_name').fetchall()

    # Get all bets with fixture results
    bets_data = db_execute(conn, '''
        SELECT b.user_id, b.home_goals as bet_home, b.away_goals as bet_away,
               f.final_home_goals, f.final_away_goals
        FROM bet b
        JOIN fixtures f ON b.match_id = f.id
        WHERE f.final_home_goals IS NOT NULL AND f.final_away_goals IS NOT NULL
    ''').fetchall()

    conn.close()

    # Calculate points for each user using calculate_match_points
    user_points = {}
    for bet in bets_data:
        points, _ = calculate_match_points(
            bet['bet_home'], bet['bet_away'],
            bet['final_home_goals'], bet['final_away_goals']
        )
        user_id = bet['user_id']
        user_points[user_id] = user_points.get(user_id, 0) + points

    # Build rankings list
    rankings = []
    for user in users:
        rankings.append({
            'id': user['id'],
            'user_name': user['user_name'],
            'total_points': user_points.get(user['id'], 0)
        })

    # Sort by points descending, then by name
    rankings.sort(key=lambda x: (-x['total_points'], x['user_name']))

    return render_template_string(RANKING_TEMPLATE,
                                 rankings=rankings,
                                 current_user_id=session['user_id'],
                                 betting_closed=BETTING_CLOSED)

@app.route('/jogador/<int:user_id>')
@login_required
def jogador_detail(user_id):
    """Player detail page with all their bets"""
    conn = get_db()

    # Get player info
    player = db_execute(conn, 'SELECT id, user_name FROM users WHERE id = ?', (user_id,)).fetchone()
    if not player:
        conn.close()
        flash('Jogador não encontrado', 'error')
        return redirect(url_for('ranking'))

    # Get all phases
    phases = db_execute(conn, '''
        SELECT phase
        FROM fixtures
        GROUP BY phase
        ORDER BY MIN(id)
    ''').fetchall()

    # Determine active phase filter
    phase_filter = request.args.get('phase')
    if not phase_filter and phases:
        phase_filter = phases[0]['phase']

    # Get all player bets with match info (no points in SQL), filtered by phase
    if phase_filter:
        bets_raw = db_execute(conn, '''
            SELECT
                f.id as match_id,
                f.phase,
                f.home,
                f.away,
                f.kickoff_utc,
                f.final_home_goals,
                f.final_away_goals,
                b.home_goals as bet_home,
                b.away_goals as bet_away
            FROM fixtures f
            LEFT JOIN bet b ON f.id = b.match_id AND b.user_id = ?
            WHERE f.phase = ?
            ORDER BY f.id
        ''', (user_id, phase_filter)).fetchall()
    else:
        bets_raw = db_execute(conn, '''
            SELECT
                f.id as match_id,
                f.phase,
                f.home,
                f.away,
                f.kickoff_utc,
                f.final_home_goals,
                f.final_away_goals,
                b.home_goals as bet_home,
                b.away_goals as bet_away
            FROM fixtures f
            LEFT JOIN bet b ON f.id = b.match_id AND b.user_id = ?
            ORDER BY f.id
        ''', (user_id,)).fetchall()

    # Get palpites gerais
    palpites_gerais = db_execute(conn, '''
        SELECT campeao, artilheiro, melhor_jogador, zebra_longe, favorito_caiu, anfitriao_longe
        FROM palpites_gerais
        WHERE user_id = ?
    ''', (user_id,)).fetchone()

    # Calculate qualified teams based on user bets
    user_qualified = calculate_qualified_teams(db_execute, conn, user_id=user_id, use_real_results=False)

    # Calculate qualified teams based on real results
    real_qualified = calculate_qualified_teams(db_execute, conn, user_id=None, use_real_results=True)

    conn.close()

    # Calculate points using calculate_match_points
    bets = []
    total_points = 0

    for bet in bets_raw:
        points, _ = calculate_match_points(
            bet['bet_home'], bet['bet_away'],
            bet['final_home_goals'], bet['final_away_goals']
        )

        # Convert Row to dict and add points
        bet_dict = dict(bet)
        bet_dict['points'] = points if bet['final_home_goals'] is not None else None
        bets.append(bet_dict)

        if bet_dict['points'] is not None:
            total_points += bet_dict['points']

    # Calculate qualification stats
    correct_qualified = user_qualified & real_qualified
    qualification_points = len(correct_qualified) * 2

    # Sort for display
    user_qualified_sorted = sorted(user_qualified)
    real_qualified_sorted = sorted(real_qualified)
    correct_qualified_sorted = sorted(correct_qualified)

    return render_template_string(
        JOGADOR_DETAIL_TEMPLATE,
        player=player,
        bets=bets,
        total_points=total_points,
        phases=[p['phase'] for p in phases],
        phase_filter=phase_filter,
        palpites_gerais=palpites_gerais,
        translate_team_name=translate_team_name,
        user_qualified=user_qualified_sorted,
        real_qualified=real_qualified_sorted,
        correct_qualified=correct_qualified_sorted,
        qualification_points=qualification_points,
    )

@app.route('/matches')
@login_required
def matches():
    """View and edit matches/bets"""
    conn = get_db()

    # Get all phases
    phases = db_execute(conn, '''
        SELECT phase
        FROM fixtures
        GROUP BY phase
        ORDER BY MIN(id)
    ''').fetchall()

    # Determine active phase (default to first phase)
    phase_filter = request.args.get('phase')
    if not phase_filter:
        phase_filter = phases[0]['phase'] if phases else ''

    # Get matches
    fixtures = db_execute(conn, '''
        SELECT * FROM fixtures
        WHERE phase = ?
        ORDER BY id
    ''', (phase_filter,)).fetchall()

    # Get user's bets
    user_bets = {}
    if fixtures:
        fixture_ids = [f['id'] for f in fixtures]
        placeholders = ','.join('?' * len(fixture_ids))
        bets = db_execute(conn, f'''
            SELECT * FROM bet
            WHERE user_id = ? AND match_id IN ({placeholders})
        ''', [session['user_id']] + fixture_ids).fetchall()

        # Convert rows to plain dictionaries so Jinja can safely call .get()
        user_bets = {bet['match_id']: dict(bet) for bet in bets}

    # Calculate group standings if viewing group stage
    group_standings = {}
    best_third_qualifiers = set()
    if 'Grupo' in phase_filter:
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
                                 best_third_qualifiers=best_third_qualifiers,
                                 betting_closed=BETTING_CLOSED)

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

                        # Check if bet exists
                        existing_bet = db_execute(conn, '''
                            SELECT id FROM bet WHERE user_id = ? AND match_id = ?
                        ''', (user_id, match_id)).fetchone()

                        if existing_bet:
                            # Update existing bet
                            db_execute(conn, '''
                                UPDATE bet SET home_goals = ?, away_goals = ?
                                WHERE user_id = ? AND match_id = ?
                            ''', (home_goals, away_goals, user_id, match_id))
                        else:
                            # Insert new bet
                            db_execute(conn, '''
                                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                                VALUES (?, ?, ?, ?)
                            ''', (user_id, match_id, home_goals, away_goals))

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

@app.route('/match/<int:match_id>/stats')
@login_required
def match_stats(match_id):
    """Match statistics showing all users' bets"""
    conn = get_db()

    # Get match info
    match = db_execute(conn, 'SELECT * FROM fixtures WHERE id = ?', (match_id,)).fetchone()
    if not match:
        conn.close()
        flash('Jogo não encontrado', 'error')
        return redirect(url_for('matches'))

    # Get all bets for this match with user names
    bets = db_execute(conn, '''
        SELECT u.id as user_id, u.user_name, b.home_goals, b.away_goals
        FROM users u
        LEFT JOIN bet b ON u.id = b.user_id AND b.match_id = ?
        ORDER BY u.user_name
    ''', (match_id,)).fetchall()

    # Calculate statistics and organize scores by result type
    total_bets = sum(1 for b in bets if b['home_goals'] is not None)

    home_win_scores = {}
    draw_scores = {}
    away_win_scores = {}

    for bet in bets:
        if bet['home_goals'] is not None and bet['away_goals'] is not None:
            score = f"{bet['home_goals']}-{bet['away_goals']}"

            if bet['home_goals'] > bet['away_goals']:
                home_win_scores[score] = home_win_scores.get(score, 0) + 1
            elif bet['home_goals'] == bet['away_goals']:
                draw_scores[score] = draw_scores.get(score, 0) + 1
            else:
                away_win_scores[score] = away_win_scores.get(score, 0) + 1

    # Sort each category by count
    home_win_scores = sorted(home_win_scores.items(), key=lambda x: x[1], reverse=True)
    draw_scores = sorted(draw_scores.items(), key=lambda x: x[1], reverse=True)
    away_win_scores = sorted(away_win_scores.items(), key=lambda x: x[1], reverse=True)

    conn.close()

    stats = {
        'total_bets': total_bets,
        'home_wins': sum(count for _, count in home_win_scores),
        'draws': sum(count for _, count in draw_scores),
        'away_wins': sum(count for _, count in away_win_scores),
        'home_win_scores': home_win_scores,
        'draw_scores': draw_scores,
        'away_win_scores': away_win_scores,
    }

    return render_template_string(
        MATCH_STATS_TEMPLATE,
        match=match,
        bets=[dict(b) for b in bets],
        stats=stats,
        translate_team_name=translate_team_name,
        get_flag_url=get_flag_url,
    )

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
        cur = db_execute(conn, 
            '''UPDATE palpites_gerais
               SET campeao=?, artilheiro=?, melhor_jogador=?,
                   zebra_longe=?, favorito_caiu=?, anfitriao_longe=?, updated_at=?
               WHERE user_id=?''',
            (data['campeao'], data['artilheiro'], data['melhor_jogador'],
             data['zebra_longe'], data['favorito_caiu'], data['anfitriao_longe'],
             datetime.utcnow().isoformat(timespec='seconds'), user_id)
        )
        if cur.rowcount == 0:
            db_execute(conn, 
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

    row = db_execute(conn, 'SELECT * FROM palpites_gerais WHERE user_id=?', (user_id,)).fetchone()
    teams = db_execute(conn, '''
        SELECT home
        FROM fixtures
        GROUP BY home
        ORDER BY MIN(id)
    ''').fetchall()
    conn.close()

    team_names = []
    for team_row in teams:
        team_name = team_row['home'] if isinstance(team_row, dict) else team_row[0]
        if not team_name.startswith(('UEFA', 'FIFA')):
            team_names.append(team_name)

    teams = team_names
    translated_teams = sorted(
        [(t, translations.get(t, t)) for t in teams],
        key=lambda x: x[1]
    )

    return render_template_string(
        PALPITES_GERAIS_TEMPLATE,
        row=dict(row) if row else {},
        translated_teams=translated_teams,
        betting_closed=BETTING_CLOSED,
    )

@app.route('/extras/<category>/stats')
@login_required
def extras_stats(category):
    """Statistics for a specific extras category"""
    conn = get_db()

    # Valid categories
    valid_categories = {
        'campeao': 'Campeão',
        'artilheiro': 'Artilheiro',
        'melhor_jogador': 'Melhor Jogador',
        'zebra_longe': 'Zebra que vai mais longe',
        'favorito_caiu': 'Favorito que vai cair antes',
        'anfitriao_longe': 'Anfitrião que vai mais longe',
    }

    if category not in valid_categories:
        flash('Categoria não encontrada', 'error')
        return redirect(url_for('palpites_gerais'))

    # Get all predictions for this category
    all_predictions = db_execute(conn, 
        f'SELECT u.id as user_id, u.user_name, p.{category} FROM users u LEFT JOIN palpites_gerais p ON u.id = p.user_id ORDER BY u.user_name'
    ).fetchall()

    # Calculate statistics
    option_counts = {}
    for pred in all_predictions:
        value = pred[category]
        if value and value.strip():
            option_counts[value] = option_counts.get(value, 0) + 1

    sorted_options = sorted(option_counts.items(), key=lambda x: x[1], reverse=True)
    total_predictions = sum(count for _, count in sorted_options)

    # Check if this category uses team names
    is_team_category = category in ['campeao', 'zebra_longe', 'favorito_caiu', 'anfitriao_longe']

    conn.close()

    return render_template_string(
        EXTRAS_STATS_TEMPLATE,
        category=category,
        category_title=valid_categories[category],
        predictions=all_predictions,
        options=sorted_options,
        total_predictions=total_predictions,
        is_team_category=is_team_category,
        translate_team_name=translate_team_name,
        get_flag_url=get_flag_url,
    )

@app.route('/regras')
@login_required
def regras():
    """Rules and scoring system"""
    return render_template_string(REGRAS_TEMPLATE)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
