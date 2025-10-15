# ---------- Templates ----------
BASE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/mvp.css">

<style>
  :root { --pad: 12px; }
  * { -webkit-tap-highlight-color: transparent; }
  body { margin: 0; }

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

  /* ---------- Mobile layout ---------- */
  @media (max-width: 600px) {
    /* Hide the Date/Time table column; show it inside the row instead */
    .kick-col { display: none; }
    thead th:first-child { display: none; }
    .kick-mobile {
      display: block;
      text-align: center;
      font-size: 0.9rem;
      color: #6b7280;
      margin: 0 0 6px 0;
    }

    /* Give teams even more space; slightly shrink inputs/flags */
    .fixture-row {
      grid-template-columns:
        minmax(0, 3fr) auto 10px auto minmax(0, 3fr);
      column-gap: 6px;
    }
    .team .name { font-size: clamp(0.74rem, 3.2vw, 0.95rem); }
    .score { width: 32px !important; height: 24px; font-size: 13.5px; }
    .flagbox { width: 16px; height: 10px; }
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

HOME = """
{% if not session.get('id') %}
  <p>
    <a class="button" href="{{ url_for('login') }}">Login</a>
  </p>
{% else %}
  <div style="display:flex; flex-direction:column; gap:.6rem; max-width:320px;">
    <a class="button" href="{{ url_for('fase_grupos') }}">Fase de Grupos</a>
    <a class="button" href="{{ url_for('palpites') }}">Palpites Gerais</a>
    <a class="button" href="{{ url_for('oitavas_final') }}">Oitavas de Final</a>
    <a class="button" href="{{ url_for('quartas_final') }}">Quartas de Final</a>
    <a class="button" href="{{ url_for('semi_final') }}">Semi Final</a>
    <a class="button" href="{{ url_for('final_terceiro') }}">Final e Terceiro Lugar</a>
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
    <form id="groupFilter" method="get" action="{{ url_for('fase_grupos') }}">
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

    <form method="post" action="{{ url_for('save_group', group=selected_group) }}">
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
                <!-- HOME (flag after name) -->
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <!-- Scores -->
                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">

                <!-- AWAY (flag before name) -->
                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>

      <div class="save-row">
        <button>Salvar {{ selected_group }}</button>
      </div>
    </form>
  {% else %}
    <p>0 jogos encontrados para o grupo {{ selected_group }}.</p>
  {% endif %}
</div>
"""

OITAVAS_PAGE = """
<h2>OITAVAS</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ url_for('salvar_oitavas') }}">
    <table>
      <thead>
        <tr>
          <th class="kick-col">Data</th>
          <th>Jogo</th>
        </tr>
      </thead>
      <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>
            <td class="fixture-cell">
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">

                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="save-row">
      <button>Salvar Oitavas</button>
    </div>
  </form>
</div>
"""

QUARTAS_PAGE = """
<h2>QUARTAS</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ url_for('salvar_quartas') }}">
    <table>
      <thead>
        <tr>
          <th class="kick-col">Data</th>
          <th>Jogo</th>
        </tr>
      </thead>
      <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>
            <td class="fixture-cell">
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">

                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="save-row">
      <button>Salvar Quartas</button>
    </div>
  </form>
</div>
"""

SEMI_PAGE = """
<h2>SEMI</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ url_for('salvar_semi') }}">
    <table>
      <thead>
        <tr>
          <th class="kick-col">Data</th>
          <th>Jogo</th>
        </tr>
      </thead>
      <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>
            <td class="fixture-cell">
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">

                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="save-row">
      <button>Salvar Semi</button>
    </div>
  </form>
</div>
"""

FINAL_PAGE = """
<h2>FINAL</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
  <form method="post" action="{{ url_for('salvar_final') }}">
    <table>
      <thead>
        <tr>
          <th class="kick-col">Data</th>
          <th>Jogo</th>
        </tr>
      </thead>
      <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>
            <td class="fixture-cell">
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                </div>

                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">

                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt=""></span>{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="save-row">
      <button>Salvar Final e Terceiro Lugar</button>
    </div>
  </form>
</div>
"""

PALPITES = """
<h2>Palpites Gerais</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<form method="post" action="{{ url_for('palpites') }}" class="card" style="max-width:720px;">
  <label>
    Artilheiro
    <input type="text" name="artilheiro" value="{{ (row.artilheiro if row else '')|e }}" autocomplete="off">
  </label>

  <label>
    Melhor Jogador
    <input type="text" name="melhor_jogador" value="{{ (row.melhor_jogador if row else '')|e }}" autocomplete="off">
  </label>

  <label>
    Melhor Jogador Jovem
    <input type="text" name="melhor_jogador_jovem" value="{{ (row.melhor_jogador_jovem if row else '')|e }}" autocomplete="off">
  </label>

  <label>
    Campeão
    <select name="campeao" required>
      <option value="">-- Selecione --</option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row.campeao==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </label>

  <label>
    Vice-Campeão
    <select name="vice_campeao" required>
      <option value="">-- Selecione --</option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row.vice_campeao==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </label>

  <label>
    Terceiro Colocado
    <select name="terceiro_colocado" required>
      <option value="">-- Selecione --</option>
      {% for t in teams %}
        <option value="{{ t }}" {{ 'selected' if row and row.terceiro_colocado==t else '' }}>{{ t }}</option>
      {% endfor %}
    </select>
  </label>

  <div style="margin-top:1rem;">
    <button>Salvar Palpites</button>
    <a class="button" href="{{ url_for('fase_grupos') }}" style="margin-left:.5rem;">Cancelar</a>
  </div>
</form>
"""
