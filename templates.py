# ============================================================================
# BASE TEMPLATE - Minimal global styles only
# ============================================================================
BASE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Advent+Pro:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
  /* ========== GLOBAL CSS VARIABLES ========== */
  :root {
    /* Colors - FIFA inspired */
    --primary-blue: #0055A4;
    --primary-blue-dark: #003d7a;
    --accent-gold: #FFB81C;
    --success-green: #00B140;
    --text-dark: #1a1a1a;
    --text-gray: #4a5568;
    --border-color: #e2e8f0;

    /* Font */
    --font-main: 'Advent Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  /* ========== GLOBAL RESET ========== */
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: var(--font-main);
    background: linear-gradient(135deg, #f8fafc 0%, #e8f0f7 100%);
    color: var(--text-dark);
  }

  /* ========== BASIC BUTTONS ========== */
  .button, button {
    font-family: var(--font-main);
    font-weight: 700;
    background: var(--primary-blue);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
  }

  .button:hover, button:hover {
    background: var(--primary-blue-dark);
  }

  /* ========== BASIC LINKS ========== */
  a {
    color: var(--primary-blue);
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }
</style>

<main>
  <header>
    <h1>Bolão Copa 2026</h1>
    {% if session.get('id') %}
      <small>Logado como {{ session.get('user_name') }}</small> · <a href="{{ url_for('logout') }}">Logout</a>
    {% endif %}
    {% for m in get_flashed_messages() %}<p>{{ m }}</p>{% endfor %}
  </header>

  {{ content|safe }}
</main>
"""


# ============================================================================
# RANKING TEMPLATE
# ============================================================================
RANKING = """
<style>
  /* Header styling */
  h2 {
    color: var(--primary-blue);
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  /* Table container */
  .table-wrap {
    overflow-x: auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 2rem 0;
  }

  /* Table styling */
  .table {
    width: 100%;
    border-collapse: collapse;
  }

  .table thead th {
    background: var(--primary-blue);
    color: white;
    padding: 14px 12px;
    text-align: center;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.85rem;
  }

  .table tbody td {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
    text-align: center;
  }

  .table tbody tr:hover {
    background: #f8fafc;
  }

  /* Highlight current user */
  .table .me td {
    background: #fef3c7;
    font-weight: 800;
  }

  /* Column alignment */
  .table .left {
    text-align: left;
  }

  .table .center {
    text-align: center;
  }

  /* Sortable columns */
  th.sortable {
    cursor: pointer;
    user-select: none;
  }

  th.sortable::after {
    content: "⇅";
    margin-left: 8px;
    opacity: 0.3;
  }

  th.sortable[data-order="asc"]::after {
    content: "↑";
    opacity: 1;
  }

  th.sortable[data-order="desc"]::after {
    content: "↓";
    opacity: 1;
  }
</style>

<h2>Ranking</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="table-wrap">
  <table id="rankTable" class="table">
    <thead>
      <tr>
        <th class="center">Pos</th>
        <th class="sortable left" data-type="text">Jogador</th>
        <th class="sortable center" data-type="num">Resultados Exatos</th>
        <th class="sortable center" data-type="num">Resultados Parciais</th>
        <th class="sortable center" data-type="num">Total Pontos</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
        <tr class="{% if r['user_id'] == current_id %}me{% endif %}">
          <td class="center">{{ loop.index }}</td>
          <td class="left">{{ r['user_name'] }}</td>
          <td class="center">{{ r['number_exact_matches'] }}</td>
          <td class="center">{{ r['number_result_matches'] }}</td>
          <td class="center">{{ r['total_points'] }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<script>
(function () {
  const table = document.getElementById('rankTable');
  if (!table) return;
  const tbody = table.tBodies[0];
  const headers = table.querySelectorAll('th.sortable');

  headers.forEach(th => {
    th.addEventListener('click', () => {
      const type = th.getAttribute('data-type') || 'text';
      const colIndex = Array.from(th.parentNode.children).indexOf(th);
      const order = th.getAttribute('data-order') === 'asc' ? 'desc' : 'asc';

      // Clear other headers
      headers.forEach(h => h.removeAttribute('data-order'));
      th.setAttribute('data-order', order);

      // Get rows
      const rows = Array.from(tbody.rows);

      // Sort
      rows.sort((a, b) => {
        const aVal = a.cells[colIndex].textContent.trim();
        const bVal = b.cells[colIndex].textContent.trim();

        let comparison = 0;
        if (type === 'num') {
          comparison = parseFloat(aVal || 0) - parseFloat(bVal || 0);
        } else {
          comparison = aVal.localeCompare(bVal);
        }

        return order === 'asc' ? comparison : -comparison;
      });

      // Re-append rows
      rows.forEach(row => tbody.appendChild(row));

      // Update position numbers
      rows.forEach((row, idx) => {
        row.cells[0].textContent = idx + 1;
      });
    });
  });
})();
</script>
"""


# ============================================================================
# HOME TEMPLATE
# ============================================================================
HOME = """
<style>
  /* Header styling */
  header {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    padding: 3rem 2rem;
    margin: -2rem -2rem 2rem -2rem;
    border-bottom: 4px solid var(--accent-gold);
    text-align: center;
  }

  header h1 {
    color: white;
    font-size: 2.5rem;
    margin: 0;
  }

  header small, header a {
    color: rgba(255, 255, 255, 0.9);
  }

  /* Navigation buttons */
  .nav-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 400px;
    margin: 0 auto;
  }

  .button.disabled {
    background: #999;
    cursor: not-allowed;
    opacity: 0.6;
  }
</style>

{% if not session.get('id') %}
  <p><a class="button" href="{{ url_for('login') }}">Login</a></p>
{% else %}
  <div class="nav-buttons">
    <a class="button" href="{{ url_for('ranking') }}">Ranking</a>
    <a class="button" href="{{ url_for('fase_page', phase_slug='groups') }}">Fase de Grupos</a>
    <a class="button" href="{{ url_for('palpites') }}">Palpites Gerais</a>

    {% if unlocks.decima_sexta %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='decima_sexta') }}">16-Avos de Final</a>
    {% else %}
      <span class="button disabled">16-Avos de Final</span>
    {% endif %}

    {% if unlocks.oitavas %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='oitavas') }}">Oitavas de Final</a>
    {% else %}
      <span class="button disabled">Oitavas de Final</span>
    {% endif %}

    {% if unlocks.quartas %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='quartas') }}">Quartas de Final</a>
    {% else %}
      <span class="button disabled">Quartas de Final</span>
    {% endif %}

    {% if unlocks.semis %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='semis') }}">Semifinais</a>
    {% else %}
      <span class="button disabled">Semifinais</span>
    {% endif %}

    {% if unlocks.terceiro %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='terceiro') }}">3º Lugar</a>
    {% else %}
      <span class="button disabled">3º Lugar</span>
    {% endif %}

    {% if unlocks.final %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='final') }}">Final</a>
    {% else %}
      <span class="button disabled">Final</span>
    {% endif %}
  </div>
{% endif %}
"""


# ============================================================================
# LOGIN TEMPLATE
# ============================================================================
LOGIN = """
<style>
  /* Form styling */
  form {
    max-width: 400px;
    margin: 2rem auto;
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  input {
    width: 100%;
    padding: 10px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    font-family: var(--font-main);
    margin-bottom: 1rem;
  }

  input:focus {
    outline: none;
    border-color: var(--primary-blue);
  }

  button {
    width: 100%;
  }
</style>

<h2>Login</h2>
<form method="post">
  <label>Usuário
    <input type="text" name="user_name">
  </label>
  <label>Senha
    <input type="password" name="password">
  </label>
  <button>Login</button>
</form>
"""


# ============================================================================
# MATCHES TEMPLATE - Fase de Grupos
# ============================================================================
MATCHES = """
<style>
  /* Page header */
  h2 {
    color: var(--primary-blue);
    font-size: 2rem;
  }

  /* Group filter */
  #groupFilter {
    margin: 1rem 0;
  }

  #groupFilter label {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  #groupFilter select {
    padding: 8px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    font-family: var(--font-main);
  }

  /* Layout: Sidebar + Main content */
  .layout-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  @media (min-width: 1024px) {
    .layout-grid {
      grid-template-columns: 350px 1fr;
    }
  }

  /* Standings table */
  .table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }

  .table thead th {
    background: var(--primary-blue);
    color: white;
    padding: 10px 8px;
    font-size: 0.85rem;
    text-align: center;
  }

  .table tbody td {
    padding: 8px;
    border-bottom: 1px solid var(--border-color);
    text-align: center;
  }

  .table .left {
    text-align: left;
  }

  /* Highlight top 2 teams */
  .table .top2 td {
    background: #d4f4dd;
    font-weight: 600;
    border-left: 3px solid var(--success-green);
  }

  /* Fixtures table */
  .fixtures {
    background: white;
    border-radius: 8px;
    padding: 1rem;
  }

  .fixture-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto 1fr;
    align-items: center;
    gap: 8px;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-color);
  }

  .fixture-row:last-child {
    border-bottom: none;
  }

  /* Team display */
  .team {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .team.left {
    justify-content: flex-end;
  }

  .team .name {
    font-weight: 700;
  }

  .flagbox {
    width: 32px;
    height: 21px;
    border-radius: 3px;
    overflow: hidden;
  }

  .flagbox img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* Score inputs */
  .score {
    width: 50px;
    height: 40px;
    text-align: center;
    font-size: 1.2rem;
    font-weight: 700;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    color: var(--primary-blue);
  }

  .score:focus {
    outline: none;
    border-color: var(--primary-blue);
  }

  .sep {
    font-weight: 700;
    color: var(--text-gray);
  }

  /* Date/time on mobile */
  .kick-mobile {
    display: none;
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-gray);
    margin-bottom: 0.5rem;
  }

  .kickoff {
    font-size: 0.9rem;
    color: var(--text-gray);
    text-align: center;
  }

  /* Mobile adjustments */
  @media (max-width: 600px) {
    .kick-col {
      display: none;
    }

    .kick-mobile {
      display: block;
    }

    .fixture-row {
      grid-template-columns: 1fr auto 1fr;
      gap: 6px;
    }

    .team .name {
      font-size: 0.85rem;
    }

    .flagbox {
      width: 24px;
      height: 16px;
    }

    .score {
      width: 40px;
      height: 35px;
      font-size: 1rem;
    }
  }

  /* Save button */
  .save-row {
    margin-top: 2rem;
    text-align: center;
  }

  .save-row button {
    width: 100%;
    max-width: 400px;
    padding: 1rem;
    font-size: 1.1rem;
  }
</style>

<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
  <h2>Fase de Grupos</h2>
  <a class="button" href="{{ url_for('index') }}">Home</a>
</div>

<!-- Group filter -->
<form id="groupFilter" method="get" action="{{ url_for('fase_page', phase_slug='groups') }}">
  <label>
    <span>Grupo:</span>
    <select name="group" onchange="document.getElementById('groupFilter').submit()">
      {% for g in group_order %}
        <option value="{{ g }}" {{ 'selected' if g == selected_group else '' }}>{{ g }}</option>
      {% endfor %}
    </select>
  </label>
</form>

<div class="layout-grid">
  <!-- Standings Sidebar -->
  <div class="layout-sidebar">
    {% if standings and standings|length >= 1 %}
      <h3>Classificação</h3>
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th class="left">Time</th>
            <th>J</th>
            <th>V</th>
            <th>E</th>
            <th>D</th>
            <th>GP</th>
            <th>GC</th>
            <th>SG</th>
            <th>Pts</th>
          </tr>
        </thead>
        <tbody>
          {% for r in standings %}
            <tr class="{% if r.rank <= 2 %}top2{% endif %}">
              <td>{{ r.rank }}</td>
              <td class="left">{{ r.team|translate_team }}</td>
              <td>{{ r.played }}</td>
              <td>{{ r.won }}</td>
              <td>{{ r.draw }}</td>
              <td>{{ r.lost }}</td>
              <td>{{ r.gf }}</td>
              <td>{{ r.ga }}</td>
              <td>{{ r.gd }}</td>
              <td>{{ r.pts }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}
  </div>

  <!-- Matches -->
  <div class="layout-main">
    {% set fixtures = groups.get(selected_group, []) %}
    {% if fixtures and fixtures|length > 0 %}
      <form method="post" action="{{ url_for('save_picks', phase_slug='groups') }}">
        <input type="hidden" name="group" value="{{ selected_group }}">

        <div class="fixtures">
          {% for m in fixtures %}
            {% set b = bets.get(m['id']) %}

            <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

            <div class="fixture-row">
              <!-- Date (desktop only) -->
              <div class="kick-col kickoff">{{ m['kickoff_utc']|fmtkick }}</div>

              <!-- Home team -->
              <div class="team left">
                <span class="name">{{ m['home']|translate_team }}</span>
                {% set fu = flag(m['home']) %}
                {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
              </div>

              <!-- Scores -->
              <input class="score" type="number" min="0" name="h_{{ m['id'] }}"
                     value="{{ b['home_goals'] if b else '' }}"
                     {{ 'disabled' if locked else '' }}>

              <span class="sep">×</span>

              <input class="score" type="number" min="0" name="a_{{ m['id'] }}"
                     value="{{ b['away_goals'] if b else '' }}"
                     {{ 'disabled' if locked else '' }}>

              <!-- Away team -->
              <div class="team right">
                {% set fu = flag(m['away']) %}
                {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                <span class="name">{{ m['away']|translate_team }}</span>
              </div>
            </div>
          {% endfor %}
        </div>

        <div class="save-row">
          <button type="submit" {{ 'disabled' if locked else '' }}>
            {{ 'Palpites Encerrados' if locked else 'Salvar Palpites' }}
          </button>
        </div>
      </form>
    {% else %}
      <p>Nenhum jogo encontrado.</p>
    {% endif %}
  </div>
</div>
"""


# ============================================================================
# PALPITES TEMPLATE
# ============================================================================
PALPITES = """
<style>
  h2 {
    color: var(--primary-blue);
  }

  form {
    max-width: 600px;
    margin: 2rem auto;
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .field {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  input, select {
    width: 100%;
    padding: 10px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    font-family: var(--font-main);
  }

  input:focus, select:focus {
    outline: none;
    border-color: var(--primary-blue);
  }

  button {
    width: 100%;
    margin-top: 1rem;
  }

  input[disabled], select[disabled], button[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

<h2>Palpites Gerais</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<form method="post" action="{{ url_for('palpites') }}">
  <div class="field">
    <label>Artilheiro</label>
    <input type="text" name="artilheiro"
           value="{{ (row['artilheiro'] if row else '') }}"
           {% if locked %}disabled{% endif %}>
  </div>

  <div class="field">
    <label>Melhor Jogador</label>
    <input type="text" name="melhor_jogador"
           value="{{ (row['melhor_jogador'] if row else '') }}"
           {% if locked %}disabled{% endif %}>
  </div>

  <div class="field">
    <label>Melhor Jogador Jovem</label>
    <input type="text" name="melhor_jogador_jovem"
           value="{{ (row['melhor_jogador_jovem'] if row else '') }}"
           {% if locked %}disabled{% endif %}>
  </div>

  <div class="field">
    <label>Campeão</label>
    <select name="campeao" {% if locked %}disabled{% endif %}>
      <option value=""></option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if (row and row['campeao']==t) else '' }}>
          {{ t|translate_team }}
        </option>
      {% endfor %}
    </select>
  </div>

  <div>
    {% if locked %}
      <button type="button" disabled>Palpites Encerrados</button>
    {% else %}
      <button>Salvar Palpites</button>
    {% endif %}
  </div>
</form>
"""


# ============================================================================
# FLAT_PHASE_PAGE TEMPLATE - Knockout stages
# ============================================================================
FLAT_PHASE_PAGE = """
<style>
  h2 {
    color: var(--primary-blue);
  }

  .fixtures {
    background: white;
    border-radius: 8px;
    padding: 1rem;
  }

  .fixture-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto 1fr;
    align-items: center;
    gap: 8px;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-color);
  }

  .team {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .team.left {
    justify-content: flex-end;
  }

  .team .name {
    font-weight: 700;
  }

  .flagbox {
    width: 32px;
    height: 21px;
    border-radius: 3px;
    overflow: hidden;
  }

  .flagbox img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .score {
    width: 50px;
    height: 40px;
    text-align: center;
    font-size: 1.2rem;
    font-weight: 700;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    color: var(--primary-blue);
  }

  .sep {
    font-weight: 700;
    color: var(--text-gray);
  }

  .kickoff {
    font-size: 0.9rem;
    color: var(--text-gray);
  }

  .save-row {
    margin-top: 2rem;
    text-align: center;
  }

  .save-row button {
    width: 100%;
    max-width: 400px;
    padding: 1rem;
  }
</style>

<h2>{{ title }}</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ action_url or url_for('save_picks', phase_slug=phase_slug) }}">
    {% for m in matches %}
      {% set b = bets.get(m['id']) %}

      <div class="fixture-row">
        <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>

        <div class="team left">
          <span class="name">{{ m['home']|translate_team }}</span>
          {% set fu = flag(m['home']) %}
          {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
        </div>

        <input class="score" type="number" min="0" name="h_{{ m['id'] }}"
               value="{{ b['home_goals'] if b else '' }}"
               {{ 'disabled' if locked else '' }}>

        <span class="sep">×</span>

        <input class="score" type="number" min="0" name="a_{{ m['id'] }}"
               value="{{ b['away_goals'] if b else '' }}"
               {{ 'disabled' if locked else '' }}>

        <div class="team right">
          {% set fu = flag(m['away']) %}
          {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
          <span class="name">{{ m['away']|translate_team }}</span>
        </div>
      </div>
    {% endfor %}

    <div class="save-row">
      <button type="submit" {{ 'disabled' if locked else '' }}>
        {{ 'Palpites Encerrados' if locked else 'Salvar Palpites' }}
      </button>
    </div>
  </form>
</div>
"""


# ============================================================================
# MATCH_BREAKDOWN TEMPLATE
# ============================================================================
MATCH_BREAKDOWN = """
<style>
  h2 {
    color: var(--primary-blue);
  }

  .match-info {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    margin: 1rem 0;
    text-align: center;
  }

  .match-info h3 {
    font-size: 1.5rem;
    margin: 0.5rem 0;
  }

  .table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }

  .table thead th {
    background: var(--primary-blue);
    color: white;
    padding: 12px;
    text-align: center;
  }

  .table tbody td {
    padding: 10px;
    border-bottom: 1px solid var(--border-color);
    text-align: center;
  }

  .table .left {
    text-align: left;
  }
</style>

<h2>Palpites do Jogo</h2>
<p><a class="button" href="{{ url_for('fase_page', phase_slug=phase_slug) }}">Voltar</a></p>

<div class="match-info">
  <h3>{{ match['home']|translate_team }} × {{ match['away']|translate_team }}</h3>
  <p>{{ match['kickoff_utc']|fmtkick }}</p>
  {% if match['home_goals'] is not none %}
    <p><strong>Resultado: {{ match['home_goals'] }} - {{ match['away_goals'] }}</strong></p>
  {% endif %}
</div>

<table class="table">
  <thead>
    <tr>
      <th class="left">Jogador</th>
      <th>Palpite</th>
      <th>Pontos</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
      <tr>
        <td class="left">{{ row['user_name'] }}</td>
        <td>
          {% if row['home_goals'] is not none %}
            {{ row['home_goals'] }} - {{ row['away_goals'] }}
          {% else %}
            -
          {% endif %}
        </td>
        <td>{{ row['points'] or '-' }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
"""
