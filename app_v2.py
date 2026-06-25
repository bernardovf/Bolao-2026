from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
import os
from werkzeug.security import check_password_hash, generate_password_hash
from utils import get_flag_url, get_team_abbr, translate_team_name, format_match_datetime, calculate_group_standings, calculate_qualified_teams, normalize_player_name
from constants import translations, CAMPEAO, ARTILHEIRO, MELHOR_JOGADOR, ZEBRA, FAVORITO, ANFITRIAO
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

# Configuração de fechamento de apostas por fase
#
# Para cada fase, defina True (FECHADO) ou False (ABERTO)
#
# Quando FECHADO:
#   - Botões "📊 Stats" ficam VISÍVEIS
#   - Nomes no Ranking são clicáveis
#   - Todos podem ver estatísticas e palpites dos outros
#   - Apostas não podem mais ser feitas/editadas
#
# Quando ABERTO:
#   - Botões "📊 Stats" ficam ESCONDIDOS
#   - Nomes no Ranking NÃO são clicáveis
#   - Jogadores não podem ver palpites dos outros
#   - Apostas podem ser feitas/editadas
#
# IMPORTANTE: Altere para True um dia antes do início de cada fase!

BETTING_CLOSED_PHASES = {
    'Grupo': True,           # Grupo A, Grupo B, etc.
    '16 Avos Final': False,
    'Oitavas de Final': False,
    'Quartas de Final': False,
    'Semifinal': False,
    'Final': False,
}

# Fallback: se a fase não estiver na lista acima, usa este valor
BETTING_CLOSED_DEFAULT = True

# Backward compatibility
BETTING_CLOSED = True  # Used for general UI elements not tied to specific phases
GRUPOS_CLOSED = False

def is_betting_closed_for_phase(phase):
    """Check if betting is closed for a specific phase"""
    if not phase:
        return BETTING_CLOSED_DEFAULT

    for phase_key, is_closed in BETTING_CLOSED_PHASES.items():
        if phase_key in phase:
            return is_closed

    return BETTING_CLOSED_DEFAULT

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database URL - usa PostgreSQL em produção, SQLite local para desenvolvimento
DATABASE_URL = os.environ.get('DATABASE_URL')
#DATABASE_URL = "postgresql://bolao_user:Y6DhyjbBLilYQWh72yhoJqNKLXGfNr9v@dpg-d7b9oa2dbo4c73ctntq0-a.oregon-postgres.render.com/bolao_2026"

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
    DB_PATH = r"G:\My Drive\Bolao-2026\bolao_2026_dev_2.db"
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
    """Convert SQLite placeholders (?) to PostgreSQL placeholders (%s).
    Also escape existing % signs in LIKE clauses by doubling them."""
    # First, escape existing % signs (but not in comments)
    # Replace % with %% so PostgreSQL doesn't treat them as placeholders
    query = query.replace('%', '%%')
    # Then convert SQLite placeholders ? to PostgreSQL placeholders %s
    query = query.replace('?', '%s')
    return query

def get_brt_date_expression(conn):
    """Get SQL expression for extracting date in BRT timezone (UTC-3)"""
    if _is_postgres_connection(conn):
        # PostgreSQL: subtract 3 hours interval
        return "DATE(kickoff_utc::timestamp - INTERVAL '3 hours')"
    else:
        # SQLite: use datetime function with modifier
        return "DATE(datetime(kickoff_utc, '-3 hours'))"

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

        # Get user by username only
        user = query_db('SELECT * FROM users WHERE user_name = ?',
                       (username,), one=True)

        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['user_name']
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

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('change_password'))

        # Get current user
        user = query_db('SELECT * FROM users WHERE id = ?',
                       (session['user_id'],), one=True)

        # Verify current password
        if not check_password_hash(user['password'], current_password):
            flash('Senha atual incorreta', 'error')
            return redirect(url_for('change_password'))

        # Verify new passwords match
        if new_password != confirm_password:
            flash('As novas senhas não coincidem', 'error')
            return redirect(url_for('change_password'))

        # Verify new password is different
        if current_password == new_password:
            flash('A nova senha deve ser diferente da senha atual', 'error')
            return redirect(url_for('change_password'))

        # Update password
        hashed_password = generate_password_hash(new_password)
        execute_db('UPDATE users SET password = ? WHERE id = ?',
                  (hashed_password, session['user_id']))

        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template_string(CHANGE_PASSWORD_TEMPLATE)

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
               f.final_home_goals, f.final_away_goals, f.phase
        FROM bet b
        JOIN fixtures f ON b.match_id = f.id
        WHERE b.user_id = ? AND f.final_home_goals IS NOT NULL
    ''', (user_id,)).fetchall()

    # Calculate match points and stats using calculate_match_points
    total_match_points = 0
    exact_matches = 0
    matches_finished = len(user_bets)

    for bet in user_bets:
        points, match_type = calculate_match_points(
            bet['bet_home'], bet['bet_away'],
            bet['final_home_goals'], bet['final_away_goals'],
            bet['phase']
        )
        total_match_points += points
        if match_type == 'exact':
            exact_matches += 1

    # Calculate qualification points
    qualification_points = 0
    if GRUPOS_CLOSED:
        real_qualified = calculate_qualified_teams(db_execute, conn, user_id=None, use_real_results=True)
        user_qualified = calculate_qualified_teams(db_execute, conn, user_id=user_id, use_real_results=False)
        correct_qualified = user_qualified & real_qualified
        qualification_points = len(correct_qualified) * 2

    # Get user's palpites gerais
    palpites_gerais = db_execute(conn, '''
        SELECT campeao, artilheiro, melhor_jogador, zebra_longe, favorito_caiu, anfitriao_longe
        FROM palpites_gerais
        WHERE user_id = ?
    ''', (user_id,)).fetchone()

    conn.close()

    # Calculate extras points
    extras_points = 0
    if palpites_gerais:
        if CAMPEAO and palpites_gerais['campeao'] == CAMPEAO:
            extras_points += 30
        if ARTILHEIRO and normalize_player_name(palpites_gerais['artilheiro']) == ARTILHEIRO:
            extras_points += 30
        if MELHOR_JOGADOR and normalize_player_name(palpites_gerais['melhor_jogador']) == MELHOR_JOGADOR:
            extras_points += 30
        if ZEBRA and palpites_gerais['zebra_longe'] == ZEBRA:
            extras_points += 30
        if FAVORITO and palpites_gerais['favorito_caiu'] == FAVORITO:
            extras_points += 30
        if ANFITRIAO and palpites_gerais['anfitriao_longe'] == ANFITRIAO:
            extras_points += 15

    # Calculate total points (matching ranking calculation)
    total_points = total_match_points + qualification_points + extras_points

    return render_template_string(DASHBOARD_TEMPLATE,
                                 user_name=user_name,
                                 total_bets=total_bets,
                                 total_points=total_points,
                                 exact_matches=exact_matches,
                                 matches_finished=matches_finished,
                                 betting_closed=BETTING_CLOSED)

@app.route('/ranking')
@login_required
def ranking():
    """Rankings page"""
    # Hide ranking when betting is open
    if not BETTING_CLOSED:
        flash('O ranking estará disponível após o encerramento das apostas.', 'info')
        return redirect(url_for('dashboard'))

    conn = get_db()

    # Get all users
    users = db_execute(conn, 'SELECT id, user_name FROM users ORDER BY user_name').fetchall()

    # Get all bets with fixture results
    bets_data = db_execute(conn, '''
        SELECT b.user_id, b.home_goals as bet_home, b.away_goals as bet_away,
               f.final_home_goals, f.final_away_goals, f.phase
        FROM bet b
        JOIN fixtures f ON b.match_id = f.id
        WHERE f.final_home_goals IS NOT NULL AND f.final_away_goals IS NOT NULL
    ''').fetchall()

    # Calculate qualified teams based on real results (once for all users)
    real_qualified = calculate_qualified_teams(db_execute, conn, user_id=None, use_real_results=True)

    # Count total finished matches for percentage calculation
    total_finished_matches = db_execute(conn, '''
        SELECT COUNT(*) as count
        FROM fixtures
        WHERE final_home_goals IS NOT NULL AND final_away_goals IS NOT NULL
    ''').fetchone()['count']

    palpites_gerais = {
        row['user_id']: dict(row)
        for row in db_execute(conn, '''
            SELECT user_id, campeao, artilheiro, melhor_jogador,
                   zebra_longe, favorito_caiu, anfitriao_longe
            FROM palpites_gerais
        ''').fetchall()
    }

    # Calculate points and statistics for each user
    user_stats = {}
    for bet in bets_data:
        points, match_type = calculate_match_points(
            bet['bet_home'], bet['bet_away'],
            bet['final_home_goals'], bet['final_away_goals'],
            bet['phase']
        )
        user_id = bet['user_id']

        if user_id not in user_stats:
            user_stats[user_id] = {
                'pts_grupos': 0,    # group stage points
                'pts_extras': 0,    # qualification points
                'pts_campeao': 0,  # campeao
                'pts_artilheiro': 0,  # artilheiro
                'pts_melhor_jogador': 0,  # melhor jogador
                'pts_zebra': 0,  # zebra
                'pts_favorito': 0,  # favorito
                'pts_anfitriao': 0,  # anfritrião
                'cravadas': 0,      # exact matches (6 points)
                'saldo': 0,         # goal difference matches (4 points)
                'empates': 0,       # correct draws (3 points)
                'colunas': 0        # partial/correct result (2 points)
            }

        user_stats[user_id]['pts_grupos'] += points
        if match_type == 'exact':
            user_stats[user_id]['cravadas'] += 1
        elif match_type == 'saldo':
            user_stats[user_id]['saldo'] += 1
        elif match_type == 'draw':
            user_stats[user_id]['empates'] += 1
        elif match_type == 'partial':
            user_stats[user_id]['colunas'] += 1

    # Calculate qualification points for each user
    for user in users:
        user_id = user['id']
        # Initialize stats if user hasn't bet yet
        if user_id not in user_stats:
            user_stats[user_id] = {
                'pts_grupos': 0,
                'pts_extras': 0,
                'pts_campeao': 0,  # campeao
                'pts_artilheiro': 0,  # artilheiro
                'pts_melhor_jogador': 0,  # melhor jogador
                'pts_zebra': 0,  # zebra
                'pts_favorito': 0,  # favorito
                'pts_anfitriao': 0,  # anfritrião
                'cravadas': 0,
                'saldo': 0,
                'empates': 0,
                'colunas': 0
            }

        # Calculate user's qualified teams
        user_qualified = calculate_qualified_teams(db_execute, conn, user_id=user_id, use_real_results=False)
        # Calculate correct predictions
        correct_qualified = user_qualified & real_qualified
        # Add qualification points (2 points per correct qualified team)
        if GRUPOS_CLOSED:
            qualification_points = len(correct_qualified) * 2
            user_stats[user_id]['pts_extras'] = qualification_points

    # Build rankings list with all statistics
    rankings = []
    max_possible_points = total_finished_matches * 6 if total_finished_matches > 0 else 1
    for user in users:
        user_id = user['id']
        stats = user_stats.get(user_id, {'pts_grupos': 0, 'pts_extras': 0, 'pts_campeao': 0, 'pts_artilheiro': 0,
                                         'pts_melhor_jogador': 0, 'pts_zebra': 0, 'pts_favorito': 0, 'pts_anfitriao': 0,
                                         'cravadas': 0, 'saldo': 0, 'empates': 0, 'colunas': 0})
        if CAMPEAO == "":
            stats['pts_campeao'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('campeao') == CAMPEAO:
                stats['pts_campeao'] = 30

        if ARTILHEIRO == "":
            stats['pts_artilheiro'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('artilheiro') and normalize_player_name(palpites_gerais[user_id]['artilheiro']) == ARTILHEIRO:
                stats['pts_artilheiro'] = 30

        if MELHOR_JOGADOR == "":
            stats['pts_melhor_jogador'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('melhor_jogador') and normalize_player_name(palpites_gerais[user_id]['melhor_jogador']) == MELHOR_JOGADOR:
                stats['pts_melhor_jogador'] = 30

        if ZEBRA == "":
            stats['pts_zebra'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('zebra_longe') == ZEBRA:
                stats['pts_zebra'] = 30

        if FAVORITO == "":
            stats['pts_favorito'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('favorito_caiu') == FAVORITO:
                stats['pts_favorito'] = 30

        if ANFITRIAO == "":
            stats['pts_anfitriao'] = 0
        else:
            if user_id in palpites_gerais and palpites_gerais[user_id].get('anfitriao_longe') == ANFITRIAO:
                stats['pts_anfitriao'] = 15

        pts_grupos = stats['pts_grupos']
        pts_extras = stats['pts_extras']

        pts_campeao = stats['pts_campeao']
        pts_artilheiro = stats['pts_artilheiro']
        pts_melhor_jogador = stats['pts_melhor_jogador']
        pts_zebra = stats['pts_zebra']
        pts_favorito = stats['pts_favorito']
        pts_anfitriao = stats['pts_anfitriao']

        total_points = pts_grupos + pts_extras + pts_campeao + pts_artilheiro + pts_melhor_jogador + pts_zebra + pts_favorito + pts_anfitriao

        # Calculate percentage
        percentage = (total_points / max_possible_points * 100) if max_possible_points > 0 else 0

        rankings.append({
            'id': user_id,
            'user_name': user['user_name'],
            'total_points': total_points,
            'pts_grupos': pts_grupos,
            'pts_extras': pts_extras,
            'pts_campeao': pts_campeao,
            'pts_artilheiro': pts_artilheiro,
            'pts_melhor_jogador': pts_melhor_jogador,
            'pts_zebra': pts_zebra,
            'pts_favorito': pts_favorito,
            'pts_anfitriao': pts_anfitriao,
            'percentage': int(round(percentage)),
            'cravadas': stats['cravadas'],
            'saldo': stats['saldo'],
            'empates': stats['empates'],
            'colunas': stats['colunas']
        })

    # Sort by points descending, then by name
    rankings.sort(key=lambda x: (-x['total_points'], x['user_name']))

    # Calculate points history data for chart
    from datetime import datetime, timedelta

    # Get all matches with results, ordered by date
    matches = db_execute(conn, '''
        SELECT id, home, away, kickoff_utc, final_home_goals, final_away_goals, phase
        FROM fixtures
        WHERE final_home_goals IS NOT NULL AND final_away_goals IS NOT NULL
        ORDER BY kickoff_utc
    ''').fetchall()

    # Get all bets
    all_bets = db_execute(conn, '''
        SELECT user_id, match_id, home_goals, away_goals
        FROM bet
    ''').fetchall()

    conn.close()

    # Organize bets by user
    user_bets_dict = {}
    for bet in all_bets:
        if bet['user_id'] not in user_bets_dict:
            user_bets_dict[bet['user_id']] = {}
        user_bets_dict[bet['user_id']][bet['match_id']] = {
            'home_goals': bet['home_goals'],
            'away_goals': bet['away_goals']
        }

    # Get BRT dates
    dates_set = set()
    for match in matches:
        dt = datetime.fromisoformat(match['kickoff_utc'].replace('Z', '+00:00'))
        dt_brt = dt - timedelta(hours=3)
        dates_set.add(dt_brt.date())

    dates = sorted(dates_set)
    dates_str = [d.strftime('%d/%m') for d in dates]

    # Calculate points for each user by date
    history_data = []
    for user in users:
        user_id = user['id']
        cumulative_points = []
        total = 0

        for date in dates:
            # Find all matches on this date
            for match in matches:
                dt = datetime.fromisoformat(match['kickoff_utc'].replace('Z', '+00:00'))
                dt_brt = dt - timedelta(hours=3)

                if dt_brt.date() == date:
                    # Check if user has a bet for this match
                    if user_id in user_bets_dict and match['id'] in user_bets_dict[user_id]:
                        bet = user_bets_dict[user_id][match['id']]
                        points, _ = calculate_match_points(
                            bet['home_goals'],
                            bet['away_goals'],
                            match['final_home_goals'],
                            match['final_away_goals'],
                            match['phase']
                        )
                        total += points

            cumulative_points.append(total)

        history_data.append({
            'name': user['user_name'],
            'points': cumulative_points
        })

    return render_template_string(RANKING_TEMPLATE,
                                 rankings=rankings,
                                 current_user_id=session['user_id'],
                                 betting_closed=BETTING_CLOSED,
                                 history_dates=dates_str,
                                 history_users=history_data)

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
    phases_raw = db_execute(conn, '''
        SELECT phase
        FROM fixtures
        GROUP BY phase
        ORDER BY MIN(id)
    ''').fetchall()

    # Consolidate all "Grupo X" phases into "Fase de Grupos" and ensure proper order
    phases = []
    other_phases = []
    has_grupos = False

    for phase_row in phases_raw:
        phase = phase_row['phase']
        if 'Grupo' in phase:
            has_grupos = True
        else:
            other_phases.append({'phase': phase})

    # Add "Fase de Grupos" first if there are any group phases
    if has_grupos:
        phases.append({'phase': 'Fase de Grupos'})

    # Then add all other phases in order
    phases.extend(other_phases)

    # Determine active phase filter
    phase_filter = request.args.get('phase')
    if not phase_filter and phases:
        phase_filter = phases[0]['phase']

    # Get all player bets with match info (no points in SQL), filtered by phase
    if phase_filter == 'Fase de Grupos':
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
            WHERE f.phase LIKE ?
            ORDER BY f.id
        ''', (user_id, '%Grupo%')).fetchall()
    elif phase_filter:
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
            bet['final_home_goals'], bet['final_away_goals'],
            bet['phase']
        )

        # Convert Row to dict and add points
        bet_dict = dict(bet)
        bet_dict['points'] = points if bet['final_home_goals'] is not None else None
        bets.append(bet_dict)

        if bet_dict['points'] is not None:
            total_points += bet_dict['points']

    if GRUPOS_CLOSED:
        # Calculate qualification stats
        correct_qualified = user_qualified & real_qualified
        qualification_points = len(correct_qualified) * 2

        # Sort for display
        user_qualified_sorted = sorted(user_qualified)
        real_qualified_sorted = sorted(real_qualified)
        correct_qualified_sorted = sorted(correct_qualified)
    else:
        correct_qualified = set()
        qualification_points = 0

        user_qualified_sorted = set()
        real_qualified_sorted = set()
        correct_qualified_sorted = set()

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
        betting_closed=BETTING_CLOSED,
    )

@app.route('/matches')
@login_required
def matches():
    """View and edit matches/bets"""
    conn = get_db()

    # Get all phases
    phases_raw = db_execute(conn, '''
        SELECT phase
        FROM fixtures
        GROUP BY phase
        ORDER BY MIN(id)
    ''').fetchall()

    # Consolidate all "Grupo X" phases into "Fase de Grupos" and ensure proper order
    phases = []
    other_phases = []
    has_grupos = False

    for phase_row in phases_raw:
        phase = phase_row['phase']
        if 'Grupo' in phase:
            has_grupos = True
        else:
            other_phases.append({'phase': phase})

    # Add "Fase de Grupos" first if there are any group phases
    if has_grupos:
        phases.append({'phase': 'Fase de Grupos'})

    # Then add all other phases in order
    phases.extend(other_phases)

    # Determine active phase (default to "Todos" to show all phases)
    phase_filter = request.args.get('phase')
    if not phase_filter:
        # Default to "Todos" to show all matches
        phase_filter = 'Todos'

    # Get BRT date expression for this database
    brt_date_expr = get_brt_date_expression(conn)

    # Get today's date in BRT timezone (UTC-3) for default filter
    from datetime import datetime, timedelta
    today_brt = (datetime.utcnow() - timedelta(hours=3)).strftime('%Y-%m-%d')

    # Get available dates for the current phase filter (in BRT timezone) - FIRST
    if phase_filter == 'Todos':
        dates = db_execute(conn, f'''
            SELECT DISTINCT {brt_date_expr} as match_date
            FROM fixtures
            ORDER BY match_date
        ''').fetchall()
    elif phase_filter == 'Fase de Grupos':
        dates = db_execute(conn, f'''
            SELECT DISTINCT {brt_date_expr} as match_date
            FROM fixtures
            WHERE phase LIKE ?
            ORDER BY match_date
        ''', ('%Grupo%',)).fetchall()
    else:
        dates = db_execute(conn, f'''
            SELECT DISTINCT {brt_date_expr} as match_date
            FROM fixtures
            WHERE phase = ?
            ORDER BY match_date
        ''', (phase_filter,)).fetchall()

    # Format dates with Portuguese day names and dd/mm/yyyy
    weekday_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    formatted_dates = []
    available_dates = []
    for date_row in dates:
        date_str = date_row['match_date']
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = date_str  # already a datetime or date object
        day_name = weekday_pt[date_obj.weekday()]
        formatted = f"{day_name} {date_obj.strftime('%d/%m/%Y')}"
        formatted_dates.append({
            'value': str(date_str) if not isinstance(date_str, str) else date_str,  # ISO format for filtering
            'label': formatted   # Pretty format for display
        })
        available_dates.append(str(date_str) if not isinstance(date_str, str) else date_str)

    # Get date filter from request or set default
    date_filter = request.args.get('date')
    if not date_filter:
        # Default to today if it exists in available dates, otherwise 'Todas'
        if today_brt in available_dates:
            date_filter = today_brt
        else:
            date_filter = 'Todas'
    elif date_filter != 'Todas' and date_filter not in available_dates:
        # Date doesn't exist in this phase - add it to the list so it stays selected
        # but it will show 0 matches (which is fine)
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d')
            day_name = weekday_pt[date_obj.weekday()]
            formatted = f"{day_name} {date_obj.strftime('%d/%m/%Y')}"
            formatted_dates.append({
                'value': date_filter,
                'label': formatted
            })
            available_dates.append(date_filter)
        except:
            # Invalid date format, reset to 'Todas'
            date_filter = 'Todas'

    # Now build query based on filters
    if phase_filter == 'Todos':
        # Show all matches
        if date_filter == 'Todas':
            fixtures = db_execute(conn, '''
                SELECT * FROM fixtures
                ORDER BY phase, kickoff_utc
            ''').fetchall()
        else:
            fixtures = db_execute(conn, f'''
                SELECT * FROM fixtures
                WHERE {brt_date_expr} = ?
                ORDER BY phase, kickoff_utc
            ''', (date_filter,)).fetchall()
    elif phase_filter == 'Fase de Grupos':
        # Show all group matches
        if date_filter == 'Todas':
            fixtures = db_execute(conn, '''
                SELECT * FROM fixtures
                WHERE phase LIKE ?
                ORDER BY phase, kickoff_utc
            ''', ('%Grupo%',)).fetchall()
        else:
            fixtures = db_execute(conn, f'''
                SELECT * FROM fixtures
                WHERE phase LIKE ?
                  AND {brt_date_expr} = ?
                ORDER BY phase, kickoff_utc
            ''', ('%Grupo%', date_filter)).fetchall()
    else:
        # Show specific phase
        if date_filter == 'Todas':
            fixtures = db_execute(conn, '''
                SELECT * FROM fixtures
                WHERE phase = ?
                ORDER BY kickoff_utc
            ''', (phase_filter,)).fetchall()
        else:
            fixtures = db_execute(conn, f'''
                SELECT * FROM fixtures
                WHERE phase = ?
                  AND {brt_date_expr} = ?
                ORDER BY kickoff_utc
            ''', (phase_filter, date_filter)).fetchall()

    # Get user's bets
    # Get user's bets for filtered fixtures (for display)
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

    # Add phase-specific betting_closed flag to each fixture
    fixtures_with_betting_status = []
    for fixture in fixtures:
        fixture_dict = dict(fixture)
        fixture_dict['betting_closed'] = is_betting_closed_for_phase(fixture['phase'])
        fixtures_with_betting_status.append(fixture_dict)
    fixtures = fixtures_with_betting_status

    # Calculate group standings if viewing group stage
    # Always use ALL group matches for standings, regardless of date filter
    group_standings = {}
    best_third_qualifiers = set()
    if phase_filter == 'Todos' or phase_filter == 'Fase de Grupos' or 'Grupo' in phase_filter:
        from collections import defaultdict

        # Get ALL group matches for standings calculation (ignore date filter)
        if phase_filter == 'Todos' or phase_filter == 'Fase de Grupos':
            all_group_fixtures = db_execute(conn, '''
                SELECT * FROM fixtures
                WHERE phase LIKE ?
                ORDER BY phase, kickoff_utc
            ''', ('%Grupo%',)).fetchall()
        else:
            # Specific group - get all matches from that group
            all_group_fixtures = db_execute(conn, '''
                SELECT * FROM fixtures
                WHERE phase = ?
                ORDER BY kickoff_utc
            ''', (phase_filter,)).fetchall()

        # Get ALL user bets for group stage matches (for standings calculation)
        if all_group_fixtures:
            all_fixture_ids = [f['id'] for f in all_group_fixtures]
            all_placeholders = ','.join('?' * len(all_fixture_ids))
            all_bets = db_execute(conn, f'''
                SELECT * FROM bet
                WHERE user_id = ? AND match_id IN ({all_placeholders})
            ''', [session['user_id']] + all_fixture_ids).fetchall()

            # Create a complete bets dictionary for standings calculation
            all_user_bets = {bet['match_id']: dict(bet) for bet in all_bets}
        else:
            all_user_bets = {}

        # Group fixtures by their specific group (e.g., "Grupo A", "Grupo B")
        groups = defaultdict(list)
        for fixture in all_group_fixtures:
            groups[fixture['phase']].append(fixture)

        # Calculate standings for each group from the user's bets
        for group_name, group_fixtures in groups.items():
            if "Grupo" in group_name:
                group_standings[group_name] = calculate_group_standings(group_fixtures, all_user_bets)

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

    # Check if any fixture has betting open
    any_betting_open = any(not f['betting_closed'] for f in fixtures)

    return render_template_string(MATCHES_TEMPLATE,
                                 fixtures=fixtures,
                                 user_bets=user_bets,
                                 phases=phases,
                                 current_phase=phase_filter,
                                 dates=formatted_dates,
                                 current_date=date_filter,
                                 get_flag_url=get_flag_url,
                                 get_team_abbr=get_team_abbr,
                                 translate_team_name=translate_team_name,
                                 calculate_match_points=calculate_match_points,
                                 format_match_datetime=format_match_datetime,
                                 group_standings=group_standings,
                                 best_third_qualifiers=best_third_qualifiers,
                                 betting_closed=BETTING_CLOSED,
                                 any_betting_open=any_betting_open)

@app.route('/save-bets', methods=['POST'])
@login_required
def save_bets():
    """Save user bets"""
    user_id = session['user_id']
    conn = get_db()

    saved_count = 0
    blocked_count = 0
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

                        # Get match phase to check if betting is closed for this phase
                        match = db_execute(conn, '''
                            SELECT phase FROM fixtures WHERE id = ?
                        ''', (match_id,)).fetchone()

                        if match and is_betting_closed_for_phase(match['phase']):
                            blocked_count += 1
                            continue

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

    if saved_count > 0:
        flash(f'✓ {saved_count} palpites salvos com sucesso!', 'success')
    if blocked_count > 0:
        flash(f'⚠ {blocked_count} palpites não foram salvos (apostas encerradas para esta fase)', 'warning')

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
        ORDER BY b.home_goals DESC, b.away_goals DESC, u.user_name
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
        betting_closed=BETTING_CLOSED,
    )

@app.route('/palpites-gerais', methods=['GET', 'POST'])
@login_required
def palpites_gerais():
    """General predictions: top scorer, champion, etc."""
    user_id = session['user_id']
    conn = get_db()

    if request.method == 'POST':
        # Block if betting is closed
        if BETTING_CLOSED:
            flash('Apostas encerradas! Não é mais possível fazer ou alterar palpites gerais.', 'error')
            return redirect(url_for('palpites_gerais'))

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
                   VALUES (?,?,?,?,?,?,?,?)''',
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

    if category in ["artilheiro", "melhor_jogador"]:
        all_predictions = [
            {
                **dict(row),
                category: normalize_player_name(dict(row).get(category))
            }
            for row in all_predictions
        ]

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
        betting_closed=BETTING_CLOSED,
    )

@app.route('/regras')
@login_required
def regras():
    """Rules and scoring system"""
    return render_template_string(REGRAS_TEMPLATE, betting_closed=BETTING_CLOSED)

@app.route('/points-history')
@login_required
def points_history():
    """Points progression chart over time"""
    # Only show when betting is closed
    if not BETTING_CLOSED:
        flash('O histórico de pontos estará disponível após o encerramento das apostas.', 'info')
        return redirect(url_for('dashboard'))

    conn = get_db()

    # Get all users
    users = db_execute(conn, 'SELECT id, user_name FROM users ORDER BY user_name').fetchall()

    # Get all matches with results, ordered by date
    matches = db_execute(conn, '''
        SELECT id, home, away, kickoff_utc, final_home_goals, final_away_goals, phase
        FROM fixtures
        WHERE final_home_goals IS NOT NULL AND final_away_goals IS NOT NULL
        ORDER BY kickoff_utc
    ''').fetchall()

    # Get all bets
    all_bets = db_execute(conn, '''
        SELECT user_id, match_id, home_goals, away_goals
        FROM bet
    ''').fetchall()

    # Organize bets by user
    user_bets = {}
    for bet in all_bets:
        if bet['user_id'] not in user_bets:
            user_bets[bet['user_id']] = {}
        user_bets[bet['user_id']][bet['match_id']] = {
            'home_goals': bet['home_goals'],
            'away_goals': bet['away_goals']
        }

    conn.close()

    # Calculate cumulative points by date for each user
    from collections import defaultdict
    from datetime import datetime, timedelta

    # Get BRT dates (convert UTC to BRT)
    dates_set = set()
    for match in matches:
        dt = datetime.fromisoformat(match['kickoff_utc'].replace('Z', '+00:00'))
        dt_brt = dt - timedelta(hours=3)
        dates_set.add(dt_brt.date())

    dates = sorted(dates_set)
    dates_str = [d.strftime('%d/%m') for d in dates]

    # Calculate points for each user by date
    user_data = []
    for user in users:
        user_id = user['id']
        cumulative_points = []
        total = 0

        for date in dates:
            # Find all matches on this date
            for match in matches:
                dt = datetime.fromisoformat(match['kickoff_utc'].replace('Z', '+00:00'))
                dt_brt = dt - timedelta(hours=3)

                if dt_brt.date() == date:
                    # Check if user has a bet for this match
                    if user_id in user_bets and match['id'] in user_bets[user_id]:
                        bet = user_bets[user_id][match['id']]
                        points, _ = calculate_match_points(
                            bet['home_goals'],
                            bet['away_goals'],
                            match['final_home_goals'],
                            match['final_away_goals'],
                            match['phase']
                        )
                        total += points

            cumulative_points.append(total)

        user_data.append({
            'name': user['user_name'],
            'points': cumulative_points
        })

    return render_template_string(
        POINTS_HISTORY_TEMPLATE,
        dates=dates_str,
        users=user_data,
        betting_closed=BETTING_CLOSED
    )

@app.route('/bet-patterns')
@login_required
def bet_patterns():
    """Matrix showing bet patterns by user"""
    # Only show when betting is closed
    if not BETTING_CLOSED:
        flash('Os padrões de apostas estarão disponíveis após o encerramento das apostas.', 'info')
        return redirect(url_for('dashboard'))

    conn = get_db()

    # Get all users
    users = db_execute(conn, 'SELECT id, user_name FROM users ORDER BY user_name').fetchall()

    # Get all bets
    all_bets = db_execute(conn, '''
        SELECT user_id, home_goals, away_goals
        FROM bet
        WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
    ''').fetchall()

    conn.close()

    # Normalize scores (1-0 and 0-1 become the same)
    def normalize_score(home, away):
        # Always put smaller number first
        return f"{min(home, away)}-{max(home, away)}"

    # Count patterns for each user and calculate total frequency
    from collections import defaultdict
    user_patterns = defaultdict(lambda: defaultdict(int))
    score_frequency = defaultdict(int)

    for bet in all_bets:
        score = normalize_score(bet['home_goals'], bet['away_goals'])
        user_patterns[bet['user_id']][score] += 1
        score_frequency[score] += 1

    # Sort scores by frequency (most common first)
    sorted_scores = sorted(score_frequency.keys(), key=lambda s: score_frequency[s], reverse=True)

    # Build user data
    user_data = []
    for user in users:
        user_id = user['id']
        counts = [user_patterns[user_id].get(score, 0) for score in sorted_scores]
        total = sum(counts)
        user_data.append({
            'id': user_id,
            'name': user['user_name'],
            'counts': counts,
            'total': total
        })

    # Sort users by name
    user_data.sort(key=lambda x: x['name'])

    return render_template_string(
        BET_PATTERNS_TEMPLATE,
        users=user_data,
        scores=sorted_scores,
        betting_closed=BETTING_CLOSED
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)