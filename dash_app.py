"""
Bolão Copa 2026 - Dash Application
Modern web app using Dash and Bootstrap components
No custom CSS/HTML required - all using Dash components
"""

import dash
from dash import Dash, html, dcc, callback, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os

from utils import (
    flag_url, fmt_kickoff, check_password, get_conn, list_teams,
    _fetch_user_bets, _fetch_phase_rows, _select_match_ids,
    _calc_points, _compute_group_table_from_bets, phase_locked,
    rank_best_thirds, team_color, DRAW_COLOR
)
from constants import unlocks, PHASE_ROUTES, PHASE_PAGES, TEAM_TRANSLATIONS, FIFA_CODES


# ============================================================================
# APP INITIALIZATION
# ============================================================================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Bolão Copa 2026"
)
server = app.server
server.secret_key = os.environ.get("SECRET_KEY", "dev-secret")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def translate_team(team):
    """Translate team name to Portuguese"""
    return TEAM_TRANSLATIONS.get(team, team)


def fifa_code(team):
    """Get FIFA 3-letter code for team"""
    return FIFA_CODES.get(team, team[:3].upper())


def create_flag_img(team, size=24):
    """Create flag image component"""
    url = flag_url(team)
    if url:
        return html.Img(src=url, style={'height': f'{size}px', 'marginRight': '8px', 'borderRadius': '3px'})
    return None


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================
def create_navbar(user_name=None):
    """Create navigation bar"""
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Ranking", href="/ranking", active="exact")),
            dbc.NavItem(dbc.NavLink("Fase de Grupos", href="/grupos", active="exact")),
            dbc.NavItem(dbc.NavLink("Palpites Gerais", href="/palpites", active="exact")),
            dbc.NavItem(
                dbc.Button(
                    [html.I(className="fas fa-sign-out-alt me-2"), "Logout"],
                    color="danger",
                    size="sm",
                    id="logout-btn",
                    className="ms-2"
                ) if user_name else dbc.NavLink("Login", href="/login")
            ),
        ],
        brand="⚽ Bolão Copa 2026",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    )


def create_hero_section(title, subtitle):
    """Create hero section at top of page"""
    return dbc.Card(
        dbc.CardBody([
            html.H1(title, className="display-4 text-center text-white mb-3"),
            html.P(subtitle, className="lead text-center text-white")
        ]),
        className="mb-4",
        style={
            'background': 'linear-gradient(135deg, #0055A4 0%, #003d7a 100%)',
            'borderRadius': '12px',
            'padding': '2rem'
        }
    )


# ============================================================================
# LOGIN PAGE
# ============================================================================
def login_layout():
    """Login page layout"""
    return dbc.Container([
        create_hero_section("Bolão Copa 2026", "Faça login para fazer seus palpites"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Login", className="mb-0")),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Label("Usuário", html_for="login-username"),
                            dbc.Input(
                                id="login-username",
                                type="text",
                                placeholder="Digite seu usuário",
                                className="mb-3"
                            ),

                            dbc.Label("Senha", html_for="login-password"),
                            dbc.Input(
                                id="login-password",
                                type="password",
                                placeholder="Digite sua senha",
                                className="mb-3"
                            ),

                            dbc.Button(
                                "Entrar",
                                id="login-submit",
                                color="primary",
                                className="w-100",
                                size="lg"
                            ),
                        ])
                    ])
                ])
            ], width=12, md=6, lg=4, className="mx-auto")
        ]),

        html.Div(id="login-output", className="mt-3")
    ], fluid=True)


# ============================================================================
# HOME PAGE
# ============================================================================
def home_layout(user_name=None):
    """Home page layout with navigation cards"""
    if not user_name:
        return dbc.Container([
            create_hero_section("Bolão Copa 2026", "Faça seus palpites para a Copa do Mundo 2026"),
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "Por favor, faça login para acessar os palpites."
            ], color="info"),
            dbc.Button("Ir para Login", href="/login", color="primary", size="lg")
        ], fluid=True)

    # Create navigation cards
    cards = [
        {
            'title': '📊 Ranking',
            'description': 'Veja a classificação geral',
            'href': '/ranking',
            'color': 'primary'
        },
        {
            'title': '⚽ Fase de Grupos',
            'description': 'Faça seus palpites para a fase de grupos',
            'href': '/grupos',
            'color': 'success'
        },
        {
            'title': '🎯 Palpites Gerais',
            'description': 'Artilheiro, campeão e mais',
            'href': '/palpites',
            'color': 'warning'
        },
    ]

    # Add knockout stages
    knockout_stages = [
        ('decima_sexta', '🏆 16-Avos de Final', '/fase/decima_sexta'),
        ('oitavas', '🏆 Oitavas de Final', '/fase/oitavas'),
        ('quartas', '🏆 Quartas de Final', '/fase/quartas'),
        ('semis', '🏆 Semifinais', '/fase/semis'),
        ('terceiro', '🥉 3º Lugar', '/fase/terceiro'),
        ('final', '🏆 Final', '/fase/final'),
    ]

    for key, title, href in knockout_stages:
        if unlocks.get(key, False):
            cards.append({
                'title': title,
                'description': 'Clique para fazer seus palpites',
                'href': href,
                'color': 'info'
            })
        else:
            cards.append({
                'title': f'🔒 {title[2:]}',  # Remove emoji and add lock
                'description': 'Ainda não disponível',
                'href': '#',
                'color': 'secondary',
                'disabled': True
            })

    # Create card grid
    card_components = []
    for card in cards:
        card_body = dbc.Card([
            dbc.CardBody([
                html.H4(card['title'], className="card-title"),
                html.P(card['description'], className="card-text"),
                dbc.Button(
                    "Acessar" if not card.get('disabled') else "Bloqueado",
                    href=card['href'] if not card.get('disabled') else None,
                    color=card['color'],
                    disabled=card.get('disabled', False),
                    className="w-100"
                )
            ])
        ], className="mb-3 h-100")

        card_components.append(
            dbc.Col(card_body, width=12, md=6, lg=4)
        )

    return dbc.Container([
        create_hero_section("Bolão Copa 2026", f"Bem-vindo, {user_name}!"),

        dbc.Row(card_components)
    ], fluid=True)


# ============================================================================
# RANKING PAGE
# ============================================================================
def ranking_layout():
    """Ranking page with sortable table"""
    # Fetch ranking data
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT u.id as user_id, u.user_name,
                   COUNT(CASE WHEN b.points = 10 THEN 1 END) as number_exact_matches,
                   COUNT(CASE WHEN b.points = 5 THEN 1 END) as number_result_matches,
                   COALESCE(SUM(b.points), 0) as total_points
            FROM user u
            LEFT JOIN bet b ON u.id = b.user_id
            GROUP BY u.id, u.user_name
            ORDER BY total_points DESC, number_exact_matches DESC, number_result_matches DESC, u.user_name
        """).fetchall()

    # Convert to DataFrame
    data = []
    for idx, row in enumerate(rows, 1):
        data.append({
            'Posição': idx,
            'Jogador': row['user_name'],
            'Resultados Exatos': row['number_exact_matches'],
            'Resultados Parciais': row['number_result_matches'],
            'Total de Pontos': row['total_points']
        })

    df = pd.DataFrame(data) if data else pd.DataFrame(columns=[
        'Posição', 'Jogador', 'Resultados Exatos', 'Resultados Parciais', 'Total de Pontos'
    ])

    # Create Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='#0055A4',
            font=dict(color='white', size=14, family='Advent Pro'),
            align='center',
            height=40
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[['#f8fafc', 'white'] * len(df)],
            font=dict(size=13, family='Advent Pro'),
            align=['center', 'left', 'center', 'center', 'center'],
            height=35
        )
    )])

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=max(400, len(df) * 35 + 40)
    )

    return dbc.Container([
        create_hero_section("Ranking", "Classificação geral dos jogadores"),

        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Voltar para Home"],
                    href="/",
                    color="secondary",
                    className="mb-3"
                )
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={'displayModeBar': False})
                    ])
                ])
            ])
        ])
    ], fluid=True)


# ============================================================================
# GRUPOS PAGE
# ============================================================================
def grupos_layout(user_id=None):
    """Grupos page with group selector, standings, and betting"""
    if not user_id:
        return dbc.Container([
            dbc.Alert("Por favor, faça login para acessar esta página.", color="warning")
        ])

    # Get all groups
    groups = ["Group A", "Group B", "Group C", "Group D", "Group E", "Group F",
              "Group G", "Group H", "Group I", "Group J", "Group K", "Group L"]

    return dbc.Container([
        create_hero_section("Fase de Grupos", "Faça seus palpites para a fase de grupos"),

        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Voltar"],
                    href="/",
                    color="secondary",
                    className="mb-3"
                )
            ], width="auto"),
            dbc.Col([
                dbc.Select(
                    id="group-selector",
                    options=[{'label': g, 'value': g} for g in groups],
                    value="Group A",
                    className="mb-3"
                )
            ], width="auto")
        ]),

        html.Div(id="group-content")
    ], fluid=True)


def create_group_content(group_name, user_id):
    """Create content for a specific group"""
    # Fetch matches
    with get_conn() as conn:
        matches = conn.execute("""
            SELECT id, phase, home, away, kickoff_utc, home_goals, away_goals
            FROM fixtures
            WHERE phase = ?
            ORDER BY kickoff_utc
        """, (group_name,)).fetchall()

        # Fetch user bets
        user_bets = _fetch_user_bets(conn, user_id, [group_name])

        # Compute standings
        standings = _compute_group_table_from_bets(conn, group_name, user_id)

    locked = phase_locked(group_name)

    # Create standings table
    standings_data = []
    for rank, row in enumerate(standings, 1):
        standings_data.append({
            '#': rank,
            'Time': translate_team(row.team),
            'J': row.played,
            'V': row.won,
            'E': row.draw,
            'D': row.lost,
            'GP': row.gf,
            'GC': row.ga,
            'SG': row.gd,
            'Pts': row.pts
        })

    standings_df = pd.DataFrame(standings_data)

    standings_table = dbc.Table.from_dataframe(
        standings_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        className="mb-4"
    )

    # Create matches form
    match_rows = []
    for match in matches:
        bet = user_bets.get(match['id'], {})

        match_row = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Date/Time
                    dbc.Col([
                        html.Small(
                            fmt_kickoff(match['kickoff_utc']),
                            className="text-muted d-block text-center"
                        )
                    ], width=12, md=2, className="mb-2 mb-md-0"),

                    # Home team
                    dbc.Col([
                        html.Div([
                            create_flag_img(match['home']),
                            html.Span(translate_team(match['home']))
                        ], className="d-flex align-items-center justify-content-end")
                    ], width=5, md=3),

                    # Score inputs
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(
                                    id={'type': 'home-score', 'match': match['id']},
                                    type="number",
                                    min=0,
                                    value=bet.get('home_goals', ''),
                                    disabled=locked,
                                    size="sm",
                                    style={'textAlign': 'center', 'fontWeight': 'bold'}
                                )
                            ], width=5),
                            dbc.Col([
                                html.Div("×", className="text-center fw-bold")
                            ], width=2),
                            dbc.Col([
                                dbc.Input(
                                    id={'type': 'away-score', 'match': match['id']},
                                    type="number",
                                    min=0,
                                    value=bet.get('away_goals', ''),
                                    disabled=locked,
                                    size="sm",
                                    style={'textAlign': 'center', 'fontWeight': 'bold'}
                                )
                            ], width=5)
                        ], className="g-1")
                    ], width=12, md=3, className="mb-2 mb-md-0"),

                    # Away team
                    dbc.Col([
                        html.Div([
                            create_flag_img(match['away']),
                            html.Span(translate_team(match['away']))
                        ], className="d-flex align-items-center")
                    ], width=5, md=3),

                    # Official result (if available)
                    dbc.Col([
                        dbc.Badge(
                            f"{match['home_goals']} - {match['away_goals']}",
                            color="info",
                            className="w-100"
                        ) if match['home_goals'] is not None else None
                    ], width=12, md=1, className="mt-2 mt-md-0")
                ], align="center")
            ])
        ], className="mb-2")

        match_rows.append(match_row)

    # Save button
    save_btn = dbc.Button(
        "Salvar Palpites",
        id="save-bets-btn",
        color="success",
        size="lg",
        className="w-100 mt-3",
        disabled=locked
    )

    if locked:
        lock_alert = dbc.Alert(
            [html.I(className="fas fa-lock me-2"), "Palpites encerrados para este grupo."],
            color="warning",
            className="mb-3"
        )
    else:
        lock_alert = None

    return [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Classificação", className="mb-0")),
                    dbc.CardBody([standings_table])
                ])
            ], width=12, lg=5, className="mb-3"),

            dbc.Col([
                lock_alert,
                html.Div(match_rows),
                save_btn,
                html.Div(id="save-feedback", className="mt-3")
            ], width=12, lg=7)
        ])
    ]


# ============================================================================
# PALPITES GERAIS PAGE
# ============================================================================
def palpites_layout(user_id=None):
    """Palpites gerais page"""
    if not user_id:
        return dbc.Container([
            dbc.Alert("Por favor, faça login para acessar esta página.", color="warning")
        ])

    # Fetch user's general predictions
    with get_conn() as conn:
        row = conn.execute("""
            SELECT artilheiro, melhor_jogador, melhor_jogador_jovem, campeao
            FROM palpites_gerais
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        teams = list_teams(conn)

    locked = phase_locked("Groups")  # Lock with groups

    return dbc.Container([
        create_hero_section("Palpites Gerais", "Artilheiro, campeão e muito mais"),

        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Voltar"],
                    href="/",
                    color="secondary",
                    className="mb-3"
                )
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Label("Artilheiro", html_for="artilheiro-input"),
                            dbc.Input(
                                id="artilheiro-input",
                                type="text",
                                value=row['artilheiro'] if row else '',
                                placeholder="Nome do jogador",
                                disabled=locked,
                                className="mb-3"
                            ),

                            dbc.Label("Melhor Jogador", html_for="melhor-jogador-input"),
                            dbc.Input(
                                id="melhor-jogador-input",
                                type="text",
                                value=row['melhor_jogador'] if row else '',
                                placeholder="Nome do jogador",
                                disabled=locked,
                                className="mb-3"
                            ),

                            dbc.Label("Melhor Jogador Jovem", html_for="melhor-jovem-input"),
                            dbc.Input(
                                id="melhor-jovem-input",
                                type="text",
                                value=row['melhor_jogador_jovem'] if row else '',
                                placeholder="Nome do jogador",
                                disabled=locked,
                                className="mb-3"
                            ),

                            dbc.Label("Campeão", html_for="campeao-select"),
                            dbc.Select(
                                id="campeao-select",
                                options=[{'label': '', 'value': ''}] +
                                        [{'label': translate_team(t), 'value': t} for t in teams],
                                value=row['campeao'] if row else '',
                                disabled=locked,
                                className="mb-3"
                            ),

                            dbc.Button(
                                "Salvar Palpites",
                                id="save-palpites-btn",
                                color="success",
                                className="w-100",
                                size="lg",
                                disabled=locked
                            )
                        ])
                    ])
                ]),

                html.Div(id="palpites-feedback", className="mt-3")
            ], width=12, md=8, lg=6, className="mx-auto")
        ])
    ], fluid=True)


# ============================================================================
# MAIN LAYOUT
# ============================================================================
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    html.Div(id='navbar-container'),
    html.Div(id='page-content', className="mt-4")
], fluid=True, className="p-0")


# ============================================================================
# CALLBACKS
# ============================================================================
@callback(
    Output('navbar-container', 'children'),
    Input('session-store', 'data')
)
def update_navbar(session_data):
    """Update navbar based on session"""
    user_name = session_data.get('user_name') if session_data else None
    return create_navbar(user_name)


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('session-store', 'data')
)
def display_page(pathname, session_data):
    """Route to appropriate page"""
    user_id = session_data.get('user_id') if session_data else None
    user_name = session_data.get('user_name') if session_data else None

    if pathname == '/login' or pathname == '/' and not user_id:
        return login_layout()
    elif pathname == '/':
        return home_layout(user_name)
    elif pathname == '/ranking':
        return ranking_layout()
    elif pathname == '/grupos':
        return grupos_layout(user_id)
    elif pathname == '/palpites':
        return palpites_layout(user_id)
    else:
        return dbc.Alert("Página não encontrada", color="danger")


@callback(
    [Output('session-store', 'data'),
     Output('login-output', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    Input('login-submit', 'n_clicks'),
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Handle login"""
    if not n_clicks:
        raise PreventUpdate

    if not username or not password:
        return dash.no_update, dbc.Alert("Preencha todos os campos", color="danger"), dash.no_update

    username = username.strip().lower()

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM user WHERE LOWER(user_name) = ?",
            (username,)
        ).fetchone()

    if not row:
        return dash.no_update, dbc.Alert("Usuário não encontrado", color="danger"), dash.no_update

    if not check_password(password, row["password_hash"]):
        return dash.no_update, dbc.Alert("Senha incorreta", color="danger"), dash.no_update

    # Login successful
    session_data = {'user_id': row['id'], 'user_name': username}
    return session_data, dbc.Alert(f"Bem-vindo, {username}!", color="success"), '/'


@callback(
    Output('group-content', 'children'),
    [Input('group-selector', 'value'),
     Input('session-store', 'data')]
)
def update_group_content(group_name, session_data):
    """Update group content when selector changes"""
    if not session_data:
        return dbc.Alert("Por favor, faça login", color="warning")

    user_id = session_data.get('user_id')
    if not user_id or not group_name:
        raise PreventUpdate

    return create_group_content(group_name, user_id)


@callback(
    Output('save-feedback', 'children'),
    Input('save-bets-btn', 'n_clicks'),
    [State({'type': 'home-score', 'match': ALL}, 'value'),
     State({'type': 'away-score', 'match': ALL}, 'value'),
     State({'type': 'home-score', 'match': ALL}, 'id'),
     State('group-selector', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def save_group_bets(n_clicks, home_scores, away_scores, match_ids, group_name, session_data):
    """Save group bets"""
    if not n_clicks or not session_data:
        raise PreventUpdate

    user_id = session_data.get('user_id')
    if not user_id:
        return dbc.Alert("Por favor, faça login", color="danger")

    if phase_locked(group_name):
        return dbc.Alert("Palpites encerrados para este grupo", color="warning")

    # Save bets
    saved = 0
    with get_conn() as conn:
        for i, match_id_dict in enumerate(match_ids):
            match_id = match_id_dict['match']
            h_score = home_scores[i]
            a_score = away_scores[i]

            if h_score is None or a_score is None or h_score == '' or a_score == '':
                continue

            try:
                h_score = int(h_score)
                a_score = int(a_score)
                if h_score < 0 or a_score < 0:
                    continue
            except (ValueError, TypeError):
                continue

            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (user_id, match_id, h_score, a_score))
            saved += 1

        conn.commit()

    return dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), f"{saved} palpite(s) salvos com sucesso!"],
        color="success"
    )


@callback(
    Output('palpites-feedback', 'children'),
    Input('save-palpites-btn', 'n_clicks'),
    [State('artilheiro-input', 'value'),
     State('melhor-jogador-input', 'value'),
     State('melhor-jovem-input', 'value'),
     State('campeao-select', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def save_palpites_gerais(n_clicks, artilheiro, melhor_jogador, melhor_jovem, campeao, session_data):
    """Save general predictions"""
    if not n_clicks or not session_data:
        raise PreventUpdate

    user_id = session_data.get('user_id')
    if not user_id:
        return dbc.Alert("Por favor, faça login", color="danger")

    if phase_locked("Groups"):
        return dbc.Alert("Palpites encerrados", color="warning")

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO palpites_gerais (user_id, artilheiro, melhor_jogador, melhor_jogador_jovem, campeao)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              artilheiro = excluded.artilheiro,
              melhor_jogador = excluded.melhor_jogador,
              melhor_jogador_jovem = excluded.melhor_jogador_jovem,
              campeao = excluded.campeao
        """, (user_id, artilheiro or None, melhor_jogador or None, melhor_jovem or None, campeao or None))
        conn.commit()

    return dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Palpites salvos com sucesso!"],
        color="success"
    )


@callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)],
    Input('logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if not n_clicks:
        raise PreventUpdate
    return {}, '/login'


# ============================================================================
# RUN SERVER
# ============================================================================
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
