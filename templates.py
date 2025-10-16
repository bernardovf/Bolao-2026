
# ---------- Templates ----------
BASE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/mvp.css">

<style>
  :root { --pad: 12px; }
  * { -webkit-tap-highlight-color: transparent; }
  body { margin: 0; }

  /* shared widgets */
  .result-line{
    display:flex; align-items:center; justify-content:center; gap:.5rem;
    margin-top:.35rem;
  }
  .final-pill{
    display:inline-block; padding:.15rem .45rem;
    border-radius:999px; font-weight:600; font-variant-numeric:tabular-nums;
    background:#eef2ff; border:1px solid #c7d2fe; color:#1f2937; white-space:nowrap;
  }
  .points-pill{
    display:inline-block; padding:.15rem .5rem; border-radius:999px;
    font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap;
    border:1px solid transparent;
  }
  .points-pill.p10{ background:transparent; border-color:transparent; color:#008000; } /* green */
  .points-pill.p5 { background:transparent; border-color:transparent; color:#FFAA33; } /* yellow */
  .points-pill.p0 { background:transparent; border-color:transparent; color:#111827; } /* black */

  /* inputs/buttons disabled look */
  input[disabled]{opacity:.6; cursor:not-allowed;}
  button[disabled]{opacity:.6; cursor:not-allowed;}

  @media (max-width: 520px){
    .result-line{ margin-top:.25rem; }
  }

  /* Container */
  .fixtures { max-width: 920px; margin: 0 auto; padding: 0 var(--pad); }

  /* Sticky toolbar (group filter) */
  .toolbar {
    position: sticky; top: 0; z-index: 5;
    backdrop-filter: saturate(180%) blur(6px);
    background: rgba(255,255,255,.85);
    padding: 8px var(--pad);
    border-bottom: 1px solid #eee;
  }
  .toolbar form { display: flex; gap: 8px; align-items: center; }
  .toolbar select { font-size: 16px; padding: 10px; }

  /* Table */
  .fixtures table { width: 100%; border-collapse: separate; border-spacing: 0; }
  .fixture-cell { padding: .55rem .6rem; overflow: visible; }

  /* Desktop/Tablet: two columns (Date/Time + Fixture) */
  .kick-col { width: 150px; text-align: center; white-space: nowrap; }
  .kickoff  { font-size: 0.95rem; color: #6b7280; }
  .kick-mobile { display: none; } /* hidden on desktop */

  /* Fixture row grid */
  .fixture-row {
    display: grid;
    grid-template-columns:
      minmax(0, 2.4fr)  /* left team */
      auto              /* left score */
      12px              /* "x" */
      auto              /* right score */
      minmax(0, 2.4fr); /* right team */
    align-items: center;
    column-gap: 8px;
  }

  /* Team: single line name + flag, no truncation; font scales to fit */
  .team {
    display: flex; align-items: center; gap: 6px; min-width: 0;
  }
  .team.left  { justify-content: flex-end; text-align: right; }
  .team.right { justify-content: flex-start; text-align: left; }
  .team .name { white-space: nowrap; font-weight: 600; line-height: 1.1;
                font-size: clamp(0.78rem, 2.3vw, 1.0rem); }

  .sep { text-align: center; }

  /* Compact scores so names get space */
  .score {
    display: inline-block !important;
    width: 36px !important; max-width: 36px !important;
    height: 26px; line-height: 26px;
    text-align: center; font-size: 14.5px; padding: 0 4px; margin: 0;
    border-radius: 6px;
  }

  /* Consistent, compact flags */
  .flagbox { flex: 0 0 auto; display: inline-block; width: 18px; height: 12px;
             line-height: 0; border-radius: 2px; background: #fff;
             box-shadow: 0 0 0 1px rgba(0,0,0,.06); }
  .flagbox > img { width: 100%; height: 100%; object-fit: contain; }

  /* Sticky Save bar */
  .save-row {
    position: sticky; bottom: 0; z-index: 4;
    background: rgba(255,255,255,.9);
    padding: 10px var(--pad);
    border-top: 1px solid #eee;
  }
  .save-row button { width: 100%; padding: 14px; font-size: 16px; border-radius: 12px; }

  /* Hide number spinners */
  input[type=number].score::-webkit-outer-spin-button,
  input[type=number].score::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
  input[type=number].score { -moz-appearance: textfield; }

/* ---------- Mobile layout for fixtures ONLY ---------- */
@media (max-width: 600px) {
  /* limit to fixtures tables so ranking is unaffected */
  .fixtures .kick-col { display: none; }
  .fixtures thead th:first-child { display: none; }
  .fixtures .kick-mobile {
    display: block;
    text-align: center;
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0 0 6px 0;
  }

  .fixtures .fixture-row {
    grid-template-columns:
      minmax(0, 3fr) auto 10px auto minmax(0, 3fr);
    column-gap: 6px;
  }
  .fixtures .team .name { font-size: clamp(0.74rem, 3.2vw, 0.95rem); }
  .fixtures .score { width: 32px !important; height: 24px; font-size: 13.5px; }
  .fixtures .flagbox { width: 16px; height: 10px; }
}

  /* Very narrow phones */
  @media (max-width: 360px) {
    .fixture-row {
      grid-template-columns:
        minmax(0, 3.4fr) auto 8px auto minmax(0, 3.4fr);
    }
    .team .name { font-size: clamp(0.70rem, 3.6vw, 0.90rem); }
    .score { width: 30px !important; height: 22px; font-size: 12.5px; }
    .flagbox { width: 15px; height: 10px; }
  }
</style>

<style>
  .left   { text-align: left; }
  .center { text-align: center; }
</style>

<style>
  /* --- Generic responsive table support (for Ranking etc.) --- */
  .table-wrap{ width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .table{ width:100%; min-width:480px; }
  @media (max-width:480px){
    .table{ min-width:480px; }
    th, td{ padding:8px 10px; }
  }

  /* Card layout under 420px (tables with class="responsive") */
  @media (max-width: 420px){
    table.responsive{ display:block; border-collapse:separate; border-spacing:0; }
    table.responsive thead{ display:none; }
    table.responsive tbody{ display:block; }
    table.responsive tr{
      display:block;
      background:#fff;
      border:1px solid #e5e7eb;
      border-radius:12px;
      margin:10px 0;
      padding:8px 10px;
      box-shadow:0 1px 2px rgba(0,0,0,.04);
    }
    table.responsive td{
      display:flex;
      justify-content:space-between;
      align-items:center;
      padding:6px 4px;
      border:0;
    }
    table.responsive td::before{
      content: attr(data-label);
      color:#6b7280;
      font-weight:500;
      margin-right:12px;
      text-align:left;
    }
    table.responsive td.left{ justify-content:flex-start; }
    table.responsive td.center{ justify-content:space-between; }
    table.responsive td[data-label="Jogador"]{ font-weight:600; }
  }

  /* optional: global styles for sortable headers */
  th.sortable { cursor:pointer; user-select:none; position:relative; padding-right:1.1rem; }
  th.sortable::after { content:"⇅"; position:absolute; right:.35rem; opacity:.35; font-size:.85em; }
  th.sortable[data-order="asc"]::after  { content:"↑"; opacity:.85; }
  th.sortable[data-order="desc"]::after { content:"↓"; opacity:.85; }
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

RANKING = """
<h2>Ranking</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="table-wrap">
  <table id="rankTable" class="table">
    <thead>
      <tr>
        <th class="sortable center" data-type="num"  style="width:60px;">Pos</th>
        <th class="sortable left"  data-type="text">Jogador</th>
        <th class="sortable center" data-type="num">Total Pontos</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
        <tr>
          <td class="center" data-label="Pos" data-val="{{ loop.index }}">
            <span class="cell-value">{{ loop.index }}</span>
          </td>
          <td class="left" data-label="Jogador">
            <span class="cell-value">{{ r['user_name'] }}</span>
          </td>
          <td class="center" data-label="Total Pontos" data-val="{{ r['total_points'] }}">
            <span class="cell-value">{{ r['total_points'] }}</span>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<style>
  th.sortable { cursor: pointer; user-select: none; position: relative; padding-right: 1.1rem; }
  th.sortable::after { content: "⇅"; position: absolute; right: .35rem; opacity: .35; font-size: .85em; }
  th.sortable[data-order="asc"]::after  { content: "↑"; opacity: .85; }
  th.sortable[data-order="desc"]::after { content: "↓"; opacity: .85; }
</style>

<script>
(function () {
  const table = document.getElementById('rankTable');
  if (!table) return;
  const tbody = table.tBodies[0];

  const getCellVal = (row, idx) => {
    const cell = row.children[idx];
    return (cell.dataset && cell.dataset.val !== undefined)
      ? cell.dataset.val
      : cell.textContent.trim();
  };
  const toNum = (v) => {
    const n = parseFloat(String(v).replace(/[^0-9.\\-]/g, ''));
    return isNaN(n) ? Number.NEGATIVE_INFINITY : n;
  };

  table.querySelectorAll('th.sortable').forEach((th, idx) => {
    th.addEventListener('click', () => {
      const type = th.dataset.type || 'text';
      const nextOrder = th.dataset.order === 'asc' ? 'desc' : 'asc';
      table.querySelectorAll('th.sortable').forEach(h => h.removeAttribute('data-order'));
      th.setAttribute('data-order', nextOrder);

      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {
        let A = getCellVal(a, idx), B = getCellVal(b, idx);
        if (type === 'num') { A = toNum(A); B = toNum(B); }
        else { A = String(A).toLowerCase(); B = String(B).toLowerCase(); }
        if (A < B) return nextOrder === 'asc' ? -1 : 1;
        if (A > B) return nextOrder === 'asc' ? 1 : -1;
        return 0;
      });
      rows.forEach(r => tbody.appendChild(r));
      // re-number Pos after sort
      Array.from(tbody.querySelectorAll('tr')).forEach((tr, i) => {
        tr.children[0].textContent = i + 1;
        tr.children[0].dataset.val = i + 1;
      });
    });
  });
})();
</script>
"""

HOME = """
{% if not session.get('id') %}
  <p>
    <a class="button" href="{{ url_for('login') }}">Login</a>
  </p>
{% else %}
  <div style="display:flex; flex-direction:column; gap:.6rem; max-width:320px;">
    <style>
      .button.disabled { pointer-events:none; color:#9aa0a6; opacity:.6; cursor:not-allowed; text-decoration:none; }
    </style>

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

    {% if unlocks.semi %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='semi') }}">Semi Final</a>
    {% else %}
      <span class="button disabled">Semi Final</span>
    {% endif %}

    {% if unlocks.final3 %}
      <a class="button" href="{{ url_for('fase_page', phase_slug='final') }}">Final e Terceiro Lugar</a>
    {% else %}
      <span class="button disabled">Final e Terceiro Lugar</span>
    {% endif %}

    <a class="button" href="{{ url_for('logout') }}">Sair</a>
  </div>
{% endif %}
"""

LOGIN = """
<h2>Login</h2>
<form method="post" action="{{ url_for('login') }}">
  <label>Usuário
    <input type="text" name="user_name">
  </label>
  <label>Senha
    <input type="password" name="password">
  </label>
  <button>Login</button>
</form>
"""

MATCHES = """
<h2>Copa do Mundo 2026</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">

  <!-- Sticky group selector -->
  <div class="toolbar">
    <form id="groupFilter" method="get" action="{{ url_for('fase_page', phase_slug='groups') }}">
      <label>Group:&nbsp;
        <select name="group" onchange="document.getElementById('groupFilter').submit()">
          {% for g in group_order %}
            <option value="{{ g }}" {{ 'selected' if g == selected_group else '' }}>{{ g }}</option>
          {% endfor %}
        </select>
      </label>
    </form>
  </div>

  {% if groups.get(selected_group) %}
    <h3>{{ selected_group }}</h3>

    <form method="post" action="{{ url_for('save_picks', phase_slug='groups') }}">
      <!-- keep user on the same group after saving -->
      <input type="hidden" name="group" value="{{ selected_group }}">

      <table>
        <thead>
          <tr>
            <th class="kick-col">Data</th>
            <th>Jogo</th>
          </tr>
        </thead>
        <tbody>
        {% for m in groups[selected_group] %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <!-- Desktop/Tablet: Data column -->
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>

            <!-- Fixture column -->
            <td class="fixture-cell">
              <!-- Mobile-only Data -->
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <!-- HOME -->
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <!-- Scores -->
                <input class="score" type="number" min="0" name="h_{{ m['id'] }}"
                       value="{{ b['home_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}"
                       value="{{ b['away_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>

                <!-- AWAY -->
                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>

              {# Official result below, centered #}
              {% set fh = m.get('final_home_goals') %}
              {% set fa = m.get('final_away_goals') %}
            {# NEW: points pill (shows only if we can score this pick) #}
            {% set pts = points.get(m['id']) %}
            {# Show result line only if there is an official result #}
                {% if fh is not none and fa is not none %}
                  <div class="result-line">
                    <span class="final-pill" title="Resultado oficial">{{ fh }}–{{ fa }}</span>
                
                    {# points to the right of the result #}
                    {% if pts is not none %}
                      <span class="points-pill {{ 'p10' if pts==10 else 'p5' if pts==5 else 'p0' }}">+{{ pts }}</span>
                    {% endif %}
                  </div>
                {% endif %}

            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>

      <div class="save-row">
        {% if locked %}
          <button type="button" class="button" disabled title="Apostas encerradas">Salvar {{ selected_group }}</button>
        {% else %}
          <button class="button">Salvar {{ selected_group }}</button>
        {% endif %}
      </div>
    </form>
  {% else %}
    <p>0 jogos encontrados para o grupo {{ selected_group }}.</p>
  {% endif %}
</div>

<style>
  input[disabled]{opacity:.6; cursor:not-allowed;}
  button[disabled]{opacity:.6; cursor:not-allowed;}

  .official-result{
    display:flex;
    justify-content:center;
    margin-top:.35rem;     /* puts it just below the inputs */
  }
  .final-pill{
    display:inline-block; margin-left:.0rem; padding:.15rem .45rem;
    border-radius:999px; font-weight:600; font-variant-numeric:tabular-nums;
    background:#eef2ff; border:1px solid #c7d2fe; color:#1f2937;
    white-space:nowrap;
  }
  @media (max-width: 520px){
    .official-result{ margin-top:.25rem; }
  }
</style>
"""

PALPITES = """
<h2>Palpites Gerais</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<form method="post" action="{{ url_for('palpites') }}">
  <div class="field">
    <label>Artilheiro</label>
    <input type="text" name="artilheiro"
           value="{{ (row['artilheiro'] if row else '') }}"
           {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
  </div>

  <div class="field">
    <label>Melhor Jogador</label>
    <input type="text" name="melhor_jogador"
           value="{{ (row['melhor_jogador'] if row else '') }}"
           {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
  </div>

  <div class="field">
    <label>Melhor Jogador Jovem</label>
    <input type="text" name="melhor_jogador_jovem"
           value="{{ (row['melhor_jogador_jovem'] if row else '') }}"
           {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
  </div>

  <div class="field">
    <label>Campeão</label>
    <select name="campeao" {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
      <option value=""></option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row['campeao']==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </div>

  <div class="field">
    <label>Vice-Campeão</label>
    <select name="vice_campeao" {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
      <option value=""></option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row['vice_campeao']==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </div>

  <div class="field">
    <label>Terceiro Colocado</label>
    <select name="terceiro_colocado" {% if locked %}disabled aria-disabled="true" title="Palpites encerrados"{% endif %}>
      <option value=""></option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row['terceiro_colocado']==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </div>

  <div class="save-row">
    {% if locked %}
      <button type="button" class="button" disabled title="Palpites encerrados">Salvar Palpites</button>
    {% else %}
      <button class="button">Salvar Palpites</button>
    {% endif %}
  </div>
</form>

<style>
  input[disabled], select[disabled], button[disabled] { opacity:.6; cursor:not-allowed; }
</style>
"""

FLAT_PHASE_PAGE = """
<h2>{{ title }}</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ action_url or url_for('save_picks', phase_slug=phase_slug) }}">
    <table>
      <thead>
        <tr><th class="kick-col">Data</th><th>Jogo</th></tr>
      </thead>
      <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <td class="kick-col"><div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div></td>
            <td class="fixture-cell">
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <!-- HOME -->
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <!-- Scores -->
                <input class="score" type="number" min="0" name="h_{{ m['id'] }}"
                       value="{{ b['home_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}"
                       value="{{ b['away_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>

                <!-- AWAY -->
                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>

              {# Official result below, centered #}
              {% set fh = m.get('final_home_goals') %}
              {% set fa = m.get('final_away_goals') %}
              {% set pts = points.get(m['id']) %}
                {% if fh is not none and fa is not none %}
                  <div class="result-line">
                    <span class="final-pill" title="Resultado oficial">{{ fh }}–{{ fa }}</span>
                    {% if pts is not none %}
                      <span class="points-pill {{ 'p10' if pts==10 else 'p5' if pts==5 else 'p0' }}">+{{ pts }}</span>
                    {% endif %}
                  </div>
                {% endif %}
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="save-row">
      {% if locked %}
        <button type="button" class="button" disabled title="Apostas encerradas">{{ button_label }}</button>
      {% else %}
        <button class="button">{{ button_label }}</button>
      {% endif %}
    </div>
  </form>
</div>

<style>
  input[disabled]{opacity:.6; cursor:not-allowed;}
  button[disabled]{opacity:.6; cursor:not-allowed;}

  .official-result{
    display:flex;
    justify-content:center;
    margin-top:.35rem;
  }
  .final-pill{
    display:inline-block; padding:.15rem .45rem;
    border-radius:999px; font-weight:600; font-variant-numeric:tabular-nums;
    background:#eef2ff; border:1px solid #c7d2fe; color:#1f2937;
    white-space:nowrap;
  }
  @media (max-width: 520px){
    .official-result{ margin-top:.25rem; }
  }
</style>
"""