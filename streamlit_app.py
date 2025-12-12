"""
Bolão Copa 2026 - Streamlit Application
Converted from Flask to Streamlit
"""

import streamlit as st
import sqlite3
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
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Bolão Copa 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS - FIFA THEME
# ============================================================================
def load_custom_css():
    """Load custom CSS styling to match the Flask app's FIFA theme"""
    st.markdown("""
    <style>
        /* Import FIFA font */
        @import url('https://fonts.googleapis.com/css2?family=Advent+Pro:wght@400;500;600;700;800;900&display=swap');

        /* Root variables */
        :root {
            --primary-blue: #0055A4;
            --primary-blue-dark: #003d7a;
            --primary-blue-light: #1a6bb8;
            --accent-gold: #FFB81C;
            --accent-gold-dark: #E5A419;
            --success-green: #00B140;
            --text-dark: #1a1a1a;
            --text-gray: #4a5568;
        }

        /* Apply FIFA font globally */
        html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, div {
            font-family: 'Advent Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* Main header styling */
        .main-header {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
            padding: 3rem 2rem;
            margin: -5rem -5rem 2rem -5rem;
            border-bottom: 6px solid var(--accent-gold);
            text-align: center;
        }

        .main-header h1 {
            color: white;
            font-size: 3rem;
            font-weight: 900;
            margin: 0;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .main-header p {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.1rem;
            margin-top: 1rem;
        }

        /* Streamlit button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }

        /* Table styling */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Input styling */
        .stNumberInput > div > div > input {
            border-radius: 10px;
            border: 3px solid #e2e8f0;
            text-align: center;
            font-weight: 800;
            font-size: 1.1rem;
            color: var(--primary-blue);
        }

        .stNumberInput > div > div > input:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(0, 85, 164, 0.2);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #e8f0f7 100%);
        }

        /* Success message */
        .stSuccess {
            background: linear-gradient(135deg, var(--success-green) 0%, #00953d 100%);
            color: white;
            border-radius: 8px;
            padding: 1rem;
        }

        /* Warning message */
        .stWarning {
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dark) 100%);
            border-radius: 8px;
            padding: 1rem;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'page' not in st.session_state:
    st.session_state.page = 'Home'


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def translate_team(team):
    """Translate team name to Portuguese"""
    return TEAM_TRANSLATIONS.get(team, team)


def fifa_code(team):
    """Get FIFA 3-letter code for team"""
    return FIFA_CODES.get(team, team[:3].upper())


def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.user_id is not None


def logout():
    """Logout user"""
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.page = 'Home'
    st.rerun()


# ============================================================================
# AUTHENTICATION PAGES
# ============================================================================
def show_login():
    """Show login page"""
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Bolão Copa 2026</h1>
        <p>Faça login para fazer seus palpites</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Login")

    with st.form("login_form"):
        username = st.text_input("Usuário", key="login_username").strip().lower()
        password = st.text_input("Senha", type="password", key="login_password")
        submit = st.form_submit_button("Entrar", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("Por favor, preencha todos os campos.")
                return

            with get_conn() as conn:
                row = conn.execute(
                    "SELECT id, password_hash FROM user WHERE LOWER(user_name) = ?",
                    (username,)
                ).fetchone()

            if not row:
                st.error("Usuário não encontrado.")
                return

            if not check_password(password, row["password_hash"]):
                st.error("Senha incorreta.")
                return

            # Login successful
            st.session_state.user_id = row["id"]
            st.session_state.user_name = username
            st.session_state.page = 'Home'
            st.success(f"Bem-vindo, {username}!")
            st.rerun()


# ============================================================================
# HOME PAGE
# ============================================================================
def show_home():
    """Show home page with navigation"""
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Bolão Copa 2026</h1>
        <p>Faça seus palpites para a Copa do Mundo 2026</p>
    </div>
    """, unsafe_allow_html=True)

    if not is_logged_in():
        st.info("Por favor, faça login para acessar os palpites.")
        if st.button("Ir para Login", use_container_width=True):
            st.session_state.page = 'Login'
            st.rerun()
        return

    st.write(f"**Logado como:** {st.session_state.user_name}")

    st.subheader("Menu Principal")

    # Main navigation buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Ranking", use_container_width=True, key="btn_ranking"):
            st.session_state.page = 'Ranking'
            st.rerun()

        if st.button("⚽ Fase de Grupos", use_container_width=True, key="btn_groups"):
            st.session_state.page = 'Grupos'
            st.rerun()

        if st.button("🎯 Palpites Gerais", use_container_width=True, key="btn_palpites"):
            st.session_state.page = 'Palpites'
            st.rerun()

    with col2:
        # Knockout stage buttons
        if unlocks.get('decima_sexta', False):
            if st.button("🏆 16-Avos de Final", use_container_width=True, key="btn_r32"):
                st.session_state.page = 'R32'
                st.rerun()
        else:
            st.button("🔒 16-Avos de Final", disabled=True, use_container_width=True, key="btn_r32_disabled")

        if unlocks.get('oitavas', False):
            if st.button("🏆 Oitavas de Final", use_container_width=True, key="btn_r16"):
                st.session_state.page = 'R16'
                st.rerun()
        else:
            st.button("🔒 Oitavas de Final", disabled=True, use_container_width=True, key="btn_r16_disabled")

        if unlocks.get('quartas', False):
            if st.button("🏆 Quartas de Final", use_container_width=True, key="btn_quarters"):
                st.session_state.page = 'Quarters'
                st.rerun()
        else:
            st.button("🔒 Quartas de Final", disabled=True, use_container_width=True, key="btn_quarters_disabled")

        if unlocks.get('semis', False):
            if st.button("🏆 Semifinais", use_container_width=True, key="btn_semis"):
                st.session_state.page = 'Semis'
                st.rerun()
        else:
            st.button("🔒 Semifinais", disabled=True, use_container_width=True, key="btn_semis_disabled")

        if unlocks.get('terceiro', False):
            if st.button("🥉 3º Lugar", use_container_width=True, key="btn_third"):
                st.session_state.page = 'Third'
                st.rerun()
        else:
            st.button("🔒 3º Lugar", disabled=True, use_container_width=True, key="btn_third_disabled")

        if unlocks.get('final', False):
            if st.button("🏆 Final", use_container_width=True, key="btn_final"):
                st.session_state.page = 'Final'
                st.rerun()
        else:
            st.button("🔒 Final", disabled=True, use_container_width=True, key="btn_final_disabled")


# ============================================================================
# RANKING PAGE
# ============================================================================
def show_ranking():
    """Show ranking page"""
    st.title("📊 Ranking")

    if st.button("← Voltar para Home"):
        st.session_state.page = 'Home'
        st.rerun()

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

    # Convert to list of dicts
    ranking_data = []
    for idx, row in enumerate(rows, 1):
        ranking_data.append({
            'Pos': idx,
            'Jogador': row['user_name'],
            'Exatos': row['number_exact_matches'],
            'Parciais': row['number_result_matches'],
            'Pontos': row['total_points']
        })

    if ranking_data:
        import pandas as pd
        df = pd.DataFrame(ranking_data)

        # Highlight current user's row
        def highlight_user(row):
            if st.session_state.user_name and row['Jogador'] == st.session_state.user_name:
                return ['background-color: #fef3c7; font-weight: bold'] * len(row)
            return [''] * len(row)

        styled_df = df.style.apply(highlight_user, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado de ranking disponível.")


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application entry point"""
    load_custom_css()

    # Sidebar navigation
    with st.sidebar:
        st.title("🏠 Navegação")

        if is_logged_in():
            st.success(f"👤 {st.session_state.user_name}")
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        else:
            st.info("Faça login para continuar")

        st.divider()

        # Navigation menu
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'Home'
            st.rerun()

        if is_logged_in():
            if st.button("📊 Ranking", use_container_width=True):
                st.session_state.page = 'Ranking'
                st.rerun()

            if st.button("⚽ Fase de Grupos", use_container_width=True):
                st.session_state.page = 'Grupos'
                st.rerun()

            if st.button("🎯 Palpites Gerais", use_container_width=True):
                st.session_state.page = 'Palpites'
                st.rerun()

    # Route to appropriate page
    if not is_logged_in() and st.session_state.page != 'Home':
        st.session_state.page = 'Login'

    if st.session_state.page == 'Login':
        show_login()
    elif st.session_state.page == 'Home':
        show_home()
    elif st.session_state.page == 'Ranking':
        show_ranking()
    elif st.session_state.page == 'Grupos':
        st.info("Página de Grupos em construção...")
        if st.button("← Voltar"):
            st.session_state.page = 'Home'
            st.rerun()
    elif st.session_state.page == 'Palpites':
        st.info("Página de Palpites Gerais em construção...")
        if st.button("← Voltar"):
            st.session_state.page = 'Home'
            st.rerun()
    else:
        show_home()


if __name__ == "__main__":
    main()
