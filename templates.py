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
  .kickoff  { font-size: 0.8rem; color: #6b7280; }
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
  .flagbox { flex: 0 0 auto; display: inline-block; width: 24px; height: 15px;
             line-height: 0; border-radius: 2px; background: #fff;
             box-shadow: 0 0 0 1px rgba(0,0,0,.06); }
  .flagbox > img { width: 100%; height: 100%; object-fit: fill; }

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
  .fixtures .flagbox { width: 37px; height: 25px; }
  

}




  /* Very narrow phones */
  @media (max-width: 360px) {
    .fixture-row {
      grid-template-columns:
        minmax(0, 3.4fr) auto 8px auto minmax(0, 3.4fr);
    }
    .team .name { font-size: clamp(0.70rem, 3.6vw, 0.90rem); }
    .score { width: 30px !important; height: 22px; font-size: 12.5px; }
    .flagbox { width: 48px; height: 32px; }
  }
</style>

<style>
  /* already added earlier */
  .table .top2 td{
    background:#ecfdf5;            /* soft green for 1st/2nd */
  }
  .table .top2 td:first-child{
    border-left:4px solid #34d399;
  }

  /* NEW: highlight 3rd place if among best eight third-placed teams */
  .table .best3 td{
    background:#ecfdf5;            /* soft blue */
  }
  .table .best3 td:first-child{
    border-left:4px solid #34d399;
  }
</style>

<style>
  /* highlight the logged-in user's row in Ranking */
  .table .me td{
    background:#ecfdf5;          /* soft green */
    font-weight:700;              /* bold text */
  }
  /* optional: subtle left border for emphasis */
  .table .me td:first-child{
    border-left:4px solid #34d399;
  }
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
  
  .stack-wrap{ margin:14px 0 8px; }
.stack-bar{
  height:14px; background:#eee; border-radius:999px; overflow:hidden;
  display:flex; box-shadow: inset 0 1px 1px rgba(0,0,0,.06);
}
.seg{ height:100%; }
.seg-home{ background:#6366f1; }   /* indigo */
.seg-draw{ background:#a3a3a3; }   /* neutral */
.seg-away{ background:#22c55e; }   /* green  */
.stack-legend{
  display:grid; grid-template-columns: repeat(3,1fr); gap:10px; margin-top:8px;
}
.legend-item{ display:flex; align-items:center; gap:8px; font-size:14px; }
.dot{
  width:10px; height:10px; border-radius:50%;
  display:inline-block;
}
.dot-home{ background:#6366f1; }
.dot-draw{ background:#a3a3a3; }
.dot-away{ background:#22c55e; }
.muted{ color:#666; }
@media (max-width: 640px){
  .stack-legend{ grid-template-columns: 1fr; }
}

.stack-legend{
  display:grid; grid-template-columns: repeat(3,1fr); gap:10px; margin-top:8px;
}
.legend-item{ display:flex; align-items:center; gap:8px; font-size:14px; }
.flag{ width:48px; height:32px; object-fit:cover; border:1px solid #ddd; border-radius:2px; }
.abbr{ font-weight:600; } /* fallback text if no flag URL */
.badge-draw{
  padding:2px 8px; border-radius:999px; border:1px solid #e5e7eb; background:#f9fafb;
  font-weight:600; font-size:13px;
}
@media (max-width: 640px){
  .stack-legend{ grid-template-columns: 1fr; }
}

</style>

<style>
.stack-wrap{ margin:14px 0 8px; }
.stack-bar{
  height:14px; background:#eee; border-radius:999px; overflow:hidden;
  display:flex; box-shadow: inset 0 1px 1px rgba(0,0,0,.06);
}
.seg{ height:100%; }

.stack-legend{
  display:grid; grid-template-columns: repeat(3,1fr); gap:10px; margin-top:8px;
}
.legend-item{ display:flex; align-items:center; gap:8px; font-size:16px; }
.flag{ width:48px; height:32px; object-fit:cover; border:1px solid #ddd; border-radius:2px; }
.abbr{ font-weight:600; }
.badge-draw{
  padding:2px 8px; border-radius:999px; border:1px solid #e5e7eb; background:#f9fafb;
  font-weight:600; font-size:13px;
}
.color-dot{
  width:10px; height:10px; border-radius:50%; display:inline-block; border:1px solid rgba(0,0,0,.06);
}
@media (max-width: 640px){
  .stack-legend{ grid-template-columns: 1fr; }
}
</style>

<style>
/* Horizontal slider container */
.table-hscroll{
  overflow-x: auto;
  -webkit-overflow-scrolling: touch; /* smooth iOS/Android swipe */
  scrollbar-width: thin;             /* Firefox */
}

/* Ensure content can overflow to trigger scroll */
.table-hscroll > table{
  min-width: 640px;   /* tweak if needed: 600–720px works well */
}

/* Optional: a subtle right-edge fade to hint scrollability */
.table-hscroll{
  position: relative;
}
.table-hscroll:after{
  content: "";
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 24px;
  pointer-events: none;
  background: linear-gradient(to left, rgba(255,255,255,0.9), rgba(255,255,255,0));
}

/* Tighten inputs on small screens so less overflow happens */
@media (max-width: 520px){
  .score{
    width: 2.2rem;   /* was larger; shrink slightly */
    padding: .25rem .35rem;
  }
  .sep{ margin: 0 .25rem; }
  .fixture-row .name{ font-size: .95rem; }
}

/* Keep “Ver palpites” readable but compact on mobile */
.button.small{
  padding: .35rem .55rem;
  font-size: .9rem;
}

</style>

<style>
/* Remove the thin white vertical line */
table {
  border-collapse: collapse;     /* unify background colors between cells */
  width: 100%;
}

tr, th, td {
  border: none;                  /* prevent tiny cell borders */
  background-clip: padding-box;  /* ensures background extends fully */
}

/* If your header uses a gradient or color */
th {
  background-color: #007BFF;     /* or your desired header color */
  color: white;
}

/* Optional: unify the background of alternating rows */
tbody tr:nth-child(even) {
  background-color: #f8f9fa;     /* light gray */
}
tbody tr:nth-child(odd) {
  background-color: #ffffff;
}
.fixture-row {
  background-color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
}

/* tables render consistently and no seams between cells */
.fixtures table { width: 100%; border-collapse: collapse; table-layout: fixed; }

/* columns */
th.kick-col, td.kick-col { width: 88px; white-space: nowrap; }
th.bets-col, td.bets-col { width: 120px; text-align: center; }
td.fixture-cell { width: auto; }  /* takes the remaining space */

/* make the middle cell actually fill */
.fixtures td.fixture-cell { display: table-cell; width: auto; }
.fixture-row  { display: flex; align-items: center; justify-content: space-between; gap: 8px; }

/* inputs compact on mobile so less spillover */
@media (max-width:520px){
  .score { width: 2.3rem; padding: .25rem .35rem; }
  .sep { margin: 0 .25rem; }
}

/* remove tiny borders/gaps some mobiles render */
.fixtures table td, .fixtures table th {
  border: 0;
  background-clip: padding-box;
}

</style>
<style>
    .fixture-row{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:8px; }
    .score-wrap{ display:flex; align-items:center; gap:6px; }
    .score{ width:44px; height:36px; line-height:36px; text-align:center; font-variant-numeric:tabular-nums; box-sizing:border-box; }
    .sep{ display:flex; align-items:center; justify-content:center; width:14px; height:36px; }
    input[type=number]::-webkit-outer-spin-button,
    input[type=number]::-webkit-inner-spin-button{ -webkit-appearance:none; margin:0; }
    input[type=number]{ -moz-appearance:textfield; }
    @media (max-width:520px){ .score{ width:38px; height:34px; line-height:34px; } .sep{ height:34px; } }
    
    /* Horizontal slider on mobile */

/* --- general: do NOT clip the table horizontally --- */
.fixtures, .table-wrap { overflow: visible; }      /* ensure parents don't clip */
.table-wrap{
  overflow-x: auto;                                /* horizontal slider on phones */
  -webkit-overflow-scrolling: touch;
}

/* desktop / default: let content decide widths */
.table-wrap > table{
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
  min-width: 0;
}

/* column model: compact sides, flexible middle */
.c-kick   { width: 96px; }
.c-bets   { width: 132px; }
.c-fixture{ width: 100%; }

th.kick-col, td.kick-col,
th.bets-col, td.bets-col { white-space: nowrap; }

/* prevent the middle cell from overflowing into the right one */
td.fixture-cell{ overflow: hidden; }

/* subtle zebra applied to the whole row (prevents seams) */
.fixtures table tbody tr:nth-child(even) td { background:#f6f9ff; }
.fixtures table tbody tr:nth-child(odd)  td { background:#fff; }

/* inner layout for scores (keeps inputs aligned) */
.fixture-row{
  display: grid;
  grid-template-columns: 1fr auto 1fr;  /* team | score | team */
  align-items: center;
  gap: 8px;
}
.score-wrap{ display:flex; align-items:center; gap:6px; }
.score{ width:44px; height:36px; line-height:36px; text-align:center; font-variant-numeric:tabular-nums; box-sizing:border-box; }
.sep{ display:flex; align-items:center; justify-content:center; width:14px; height:36px; }

/* tighter on small phones; keep scroll instead of squeezing */
@media (max-width: 500px){
  .table-wrap > table{
    table-layout: auto;     /* honor the colgroup widths */
    min-width: 350px;        /* force horizontal scroll; no overlap, nothing cut off */
  }
  .c-kick   { width: 100%; }
  .c-bets   { width: 100%; }
  .c-fixture   { width: 0px; }
  .score{ width:70px; height:4px; line-height:34px; }
  .sep{ height:34px; }
}

/* input spinner removal */
input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button{ -webkit-appearance:none; margin:0; }
input[type=number]{ -moz-appearance:textfield; }

.clickable{ cursor:pointer; }
.score-row.active{ outline:2px solid #2563eb; background: #eff6ff; }
.pick-row[style*="display: none"] { /* nothing; just to remind what's happening */ }

/* Row tint on ALL cells */
.score-row td,
.pick-row  td{
  background: var(--bg) !important;   /* light fill across the row */
}

/* Nice colored edge using a pseudo element (more reliable than border-left) */
.score-row,
.pick-row{
  position: relative;
}
.score-row::before,
.pick-row::before{
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 1px;
  background: var(--edge);
  border-top-left-radius: 0px;   /* match your table’s rounding if any */
  border-bottom-left-radius: 0px;
}

/* Keep hover/active without changing the background tint */
.score-row:hover{ filter: brightness(0.985); }
.score-row.active{
  box-shadow: 0 0 0 5px #2563eb inset;  /* focus ring, does not override bg */
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

RANKING = """
<h2>Ranking</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="table-wrap">
  <table id="rankTable" class="table">
    <thead>
      <tr>
        <th class="center" style="width:60px;">Pos</th>  {# no 'sortable' here #}
        <th class="sortable left"  data-type="text">Jogador</th>
        <th class="sortable center" data-type="num">Resultados Exatos</th>
        <th class="sortable center" data-type="num">Resultados Parciais</th>
        <th class="sortable center" data-type="num">Total Pontos</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
        <tr class="{% if r['user_id'] == current_id %}me{% endif %}">
          <td class="center" data-label="Pos" data-val="{{ loop.index }}">
            <span class="cell-value">{{ loop.index }}</span>
          </td>
          <td class="left" data-label="Jogador">
            <span class="cell-value">{{ r['user_name'] }}</span>
          </td>
          <td class="center" data-label="Resultados Exatos" data-val="{{ r['number_exact_matches'] }}">
            <span class="cell-value">{{ r['number_exact_matches'] }}</span>
          </td>
          <td class="center" data-label="Resultados Parciais" data-val="{{ r['number_result_matches'] }}">
            <span class="cell-value">{{ r['number_result_matches'] }}</span>
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

MATCHES_2 = """
<h2>Copa do Mundo 2026</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<!-- Toolbar -->
<div class="toolbar simple">
  <form id="groupFilter" method="get" action="{{ url_for('fase_page', phase_slug='groups') }}">
    <select id="groupSelect" name="group" onchange="this.form.submit()">
      {% for g in group_order %}
        <option value="{{ g }}" {{ 'selected' if g == selected_group else '' }}>{{ g }}</option>
      {% endfor %}
    </select>
  </form>
</div>

<div class="page-grid">
  <!-- LEFT: TABELA -->
  <aside class="left-card card">
    <h3 class="card-title">TABELA</h3>
    {% if standings and standings|length >= 1 %}
    <div class="table-wrap">
      <table class="table standings">
        <thead>
          <tr>
            <th class="center pos">#</th>
            <th class="left">Seleção</th>
            <th class="center">P</th>
            <th class="center">J</th>
            <th class="center">V</th>
            <th class="center">SG</th>
            <th class="center">GP</th>
          </tr>
        </thead>
        <tbody>
          {% for r in standings %}
          <tr class="{% if r.rank <= 2 %}top2{% elif r.rank == 3 and (best3 is defined and r.team in best3) %}best3{% endif %}">
            <td class="center pos"><span class="cell">{{ r.rank }}</span></td>
            <td class="left">
              <div class="team">
                {% set fu = flag(r.team) %}
                {% if fu %}<img class="crest" src="{{ fu }}" alt="">{% endif %}
                <span class="name">{{ r.team }}</span>
              </div>
            </td>
            <td class="center"><strong class="mono">{{ r.pts }}</strong></td>
            <td class="center mono">{{ r.played }}</td>
            <td class="center mono">{{ r.won }}</td>
            <td class="center mono">{{ r.gd }}</td>
            <td class="center mono">{{ r.gf }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
      <p>Sem classificação disponível.</p>
    {% endif %}
  </aside>

  <!-- RIGHT: MATCHES -->
  <section class="right-card card flat">
    <div class="matches-compact">
      {% if groups.get(selected_group) %}
      <form method="post" action="{{ url_for('save_picks', phase_slug='groups') }}">
        <input type="hidden" name="group" value="{{ selected_group }}">

        {% for m in groups[selected_group] %}
          {% set b = bets.get(m['id']) %}
          <div class="match-line">
            <!-- left meta -->
            <div class="meta">
              <div class="dow">{{ m.get('weekday','') }}</div>
                <div class="meta">
                  <span class="date">{{ m.kickoff_utc | fmt_kickoff_pt('America/Sao_Paulo') }}</span>
                </div>
              
              {% if m.get('stadium') %}
                <div class="stadium">{{ m['stadium'] }}</div>
              {% endif %}
            </div>

            <!-- teams + inputs -->
            <div class="fixture-flat">
              <!-- HOME -->
              <div class="side home">
                {% set fuh = flag(m['home']) %}
                <span class="abbr">{{ (m.get('home_abbr') or (m['home']|abbr3)) }}</span>
                {% if fuh %}<img class="crest" src="{{ fuh }}" alt="">{% endif %}
              </div>

              <!-- Inputs -->
              <div class="middle">
                <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                       name="h_{{ m['id'] }}"
                       value="{{ b['home_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                <span class="x">x</span>
                <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                       name="a_{{ m['id'] }}"
                       value="{{ b['away_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
              </div>

              <!-- AWAY -->
              <div class="side away">
                {% set fua = flag(m['away']) %}
                {% if fua %}<img class="crest" src="{{ fua }}" alt="">{% endif %}
                <span class="abbr">{{ (m.get('away_abbr') or (m['away']|abbr3)) }}</span>
              </div>
            </div>
          </div>
        {% endfor %}

        <div class="save-row right">
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
  </section>
</div>

<style>
/* ---- Design tokens (tweak here) ---- */
:root{
  --bg:#fff;
  --ink:#0f172a;
  --muted:#6b7280;
  --rule:#000000;
  --card:#ffffff;
  --radius:10px;
  --gap:28px;        /* space between the two columns */
  --colL: 380px;     /* min width standings column */
  --colBias: 30%;    /* % width for left column on wide screens */
  --metaW: 220px;    /* width of left meta inside match rows */
  --inputW: 24px;    /* score box width */
  --inputH: 20px;    /* score box height */
}

/* Layout grid (bias to the RIGHT column, like Globo) */
.page-grid{
  display:grid;
  grid-template-columns: minmax(var(--colL), var(--colBias)) minmax(0, calc(100% - var(--colBias)));
  gap: var(--gap);
  align-items:start;
}

/* Cards */
.card{
  background:var(--card);
  border-radius:var(--radius);
  border:1px solid rgba(3,7,18,0.05);
  box-shadow:0 6px 18px rgba(15,23,42,0.06);
  padding:20px 16px 12px;
}
.card.flat{ box-shadow:none; border:1px solid rgba(3,7,18,0.04); }
.card-title{ margin:0 0 10px; font-size:16px; color:var(--ink); }

/* Table (standings) */
.table{ width:100%; border-collapse:collapse; font-size:14px; color:var(--ink); }
.table th, .table td{ padding:8px 10px; border-bottom:1px solid var(--rule); }
.table th{ font-weight:600; text-transform:uppercase; font-size:12px; color:#8a8f99; letter-spacing:.04em; }
.center{text-align:center} .left{text-align:left}
.pos{ width:48px; }
.team{ display:flex; align-items:center; gap:8px; }
.crest{ width:22px; height:22px; border-radius:50%; background:#fff; object-fit:cover; }
.name{ overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.mono{ font-variant-numeric: tabular-nums; }

/* Highlighting for qualifiers (subtle, like interativos) */
tr.top2{ background:linear-gradient(90deg, rgba(0,128,0,.06), rgba(0,128,0,.02)); }
tr.best3{ background:linear-gradient(90deg, rgba(0,128,255,.06), rgba(0,128,255,.02)); }

/* Matches list (flat rows with a left meta band) */
.matches-compact{ padding-top:4px; }
/* STACK layout: date/time on top, match under it */
.match-line{
  display:grid;
  grid-template-columns: 1fr;
  row-gap: 6px;
  padding: 12px 4px;
  border-bottom: 1px solid var(--rule);
}
.match-line .meta{
  justify-content: center;   /* centers the flex row */
  text-align: center;        /* centers any wrapped text */
}

/* compact "date line" */
.meta{
  display:flex;
  align-items:center;
  gap: 10px;
  font-size: .85rem;
  color: var(--muted);
}
.meta .date{ font-variant-numeric: tabular-nums; }

.fixture-flat{
  display:grid;
  grid-template-columns: minmax(0,1fr) 120px minmax(0,1fr);
  align-items:center; column-gap: 20px; min-width:0;
}
.side{ display:flex; align-items:center; gap:6px; min-width:0; }
.side.home{ justify-content:flex-end; }
.abbr{ font-weight:800; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

/* Center inputs */
.middle{ display:flex; align-items:center; justify-content:center; gap:8px; }
.box{
  width:var(--inputW); height:var(--inputH); text-align:center;
  border:1px solid #d1d5db; border-radius:6px; background:#fff;
  font-variant-numeric: tabular-nums;
}
.box:focus{ outline:2px solid #93c5fd; outline-offset:1px; }
.box[disabled]{ background:#f3f4f6; color:#9ca3af; }

/* Buttons / selects to match vibe */
.button{
  display:inline-block; padding:8px 14px; border-radius:8px;
  background:#0ea5e9; color:white; border:0; cursor:pointer;
  font-weight:600; text-decoration:none;
}
.button[disabled]{ background:#9ca3af; cursor:not-allowed; }
select{ padding:6px 8px; border:1px solid #d1d5db; border-radius:8px; }

/* Utilities */
.save-row.right{ padding-top:12px; text-align:right; }

/* Responsive: collapse to single column */
@media (max-width: 900px){
  .page-grid{ grid-template-columns: 1fr; }
  .left-card{ order:2; }
  .right-card{ order:1; }
  :root{ --metaW: 140px; }
}
</style>
"""

MATCHES = """
<h2>Copa do Mundo 2026</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="page-grid">

  <!-- FILTER spans both columns -->
  <div class="filter-card">
    <form id="groupFilter" method="get" action="{{ url_for('fase_page', phase_slug='groups') }}">
      <select id="groupSelect" name="group" onchange="this.form.submit()">
        {% for g in group_order %}
          <option value="{{ g }}" {{ 'selected' if g == selected_group else '' }}>{{ g }}</option>
        {% endfor %}
      </select>
    </form>
  </div>

  <!-- LEFT: TABELA -->
  <aside class="left-card card">
    <h3 class="card-title">TABELA APOSTA</h3>
    {% if standings and standings|length >= 1 %}
    <div class="table-wrap">
      <table class="table standings">
        <thead>
          <tr>
            <th class="center pos">#</th>
            <th class="left">Seleção</th>
            <th class="center">P</th>
            <th class="center">J</th>
            <th class="center">V</th>
            <th class="center">SG</th>
            <th class="center">GP</th>
          </tr>
        </thead>
        <tbody>
          {% for r in standings %}
          <tr class="{% if r.rank <= 2 %}top2{% elif r.rank == 3 and (best3 is defined and r.team in best3) %}best3{% endif %}">
            <td class="center pos"><span class="cell">{{ r.rank }}</span></td>
            <td class="left">
              <div class="team">
                {% set fu = flag(r.team) %}
                {% if fu %}<img class="crest" src="{{ fu }}" alt="">{% endif %}
                <span class="name">{{ r.team }}</span>
              </div>
            </td>
            <td class="center"><strong class="mono">{{ r.pts }}</strong></td>
            <td class="center mono">{{ r.played }}</td>
            <td class="center mono">{{ r.won }}</td>
            <td class="center mono">{{ r.gd }}</td>
            <td class="center mono">{{ r.gf }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
      <p>Sem classificação disponível.</p>
    {% endif %}
    
    <h3 class="card-title">TABELA REAL</h3>
    {% if standings_real and standings_real|length >= 1 %}
    <div class="table-wrap">
      <table class="table standings">
        <thead>
          <tr>
            <th class="center pos">#</th>
            <th class="left">Seleção</th>
            <th class="center">P</th>
            <th class="center">J</th>
            <th class="center">V</th>
            <th class="center">SG</th>
            <th class="center">GP</th>
          </tr>
        </thead>
        <tbody>
          {% for r in standings_real %}
          <tr class="{% if r.rank <= 2 %}top2{% elif r.rank == 3 and (best3_real is defined and r.team in best3_real) %}best3_real{% endif %}">
            <td class="center pos"><span class="cell">{{ r.rank }}</span></td>
            <td class="left">
              <div class="team">
                {% set fu = flag(r.team) %}
                {% if fu %}<img class="crest" src="{{ fu }}" alt="">{% endif %}
                <span class="name">{{ r.team }}</span>
              </div>
            </td>
            <td class="center"><strong class="mono">{{ r.pts }}</strong></td>
            <td class="center mono">{{ r.played }}</td>
            <td class="center mono">{{ r.won }}</td>
            <td class="center mono">{{ r.gd }}</td>
            <td class="center mono">{{ r.gf }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
      <p>Sem classificação disponível.</p>
    {% endif %}

  </aside>

  <!-- RIGHT: MATCHES -->
  <section class="right-card card flat">
    <div class="matches-compact">
      {% if groups.get(selected_group) %}
      <form method="post" action="{{ url_for('save_picks', phase_slug='groups') }}">
        <input type="hidden" name="group" value="{{ selected_group }}">

        {% for m in groups[selected_group] %}
          {% set b = bets.get(m['id']) %}
          {% set fh = m.get('final_home_goals') %}
          {% set fa = m.get('final_away_goals') %}
          {% set pts = points.get(m['id']) %}

          <div class="match-line">
            <!-- date (centered) -->
            <div class="meta">
              <span class="date">{{ m.kickoff_utc | fmt_kickoff_pt('America/Sao_Paulo') }}</span>
              {% if m.get('stadium') %}
                <span class="stadium">• {{ m['stadium'] }}</span>
              {% endif %}
              {% if fh is not none and fa is not none %}
                {% if pts is not none %}
                    <span class="points-pill {{ 'p10' if pts==10 else 'p5' if pts==5 else 'p0' }}">+{{ pts }}</span>
                {% endif %}
              {% endif %}
            </div>

            <!-- teams + inputs -->
            <div class="fixture-flat">
              <!-- HOME -->
              <div class="side home">
                  {% set fuh = flag(m['home']) %}
                  <!-- full name (desktop) -->
                  <span class="team-name full">{{ m['home'] }}</span>
                  <!-- abbreviation (mobile) -->
                  <span class="team-name abbr">{{ m.get('home_abbr') or (m['home']|abbr3) }}</span>
                  {% if fuh %}<img class="crest" src="{{ fuh }}" alt="">{% endif %}
              </div>

              <!-- Inputs -->
              <div class="middle">
                <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                       name="h_{{ m['id'] }}"
                       value="{{ b['home_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                <span class="x">x</span>
                <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                       name="a_{{ m['id'] }}"
                       value="{{ b['away_goals'] if b else '' }}"
                       {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
              </div>

              <!-- AWAY -->
              <div class="side away">
                  {% set fua = flag(m['away']) %}
                  {% if fua %}<img class="crest" src="{{ fua }}" alt="">{% endif %}
                  <!-- full name (desktop) -->
                  <span class="team-name full">{{ m['away'] }}</span>
                  <!-- abbreviation (mobile) -->
                  <span class="team-name abbr">{{ m.get('away_abbr') or (m['away']|abbr3) }}</span>
              </div>
            </div>
            
            {% if m.get('final_home_goals') is not none and m.get('final_away_goals') is not none %}

              <div class="actual-line">
                <div class="middle">
                  <span class="box box-static">{{ m.final_home_goals }}</span>
                  <span class="x">x</span>
                  <span class="box box-static">{{ m.final_away_goals }}</span>
                </div>
              </div>

            {% endif %}


            {% if locked %}
              <div class="bets-row">
                <a class="button small"
                   href="{{ url_for('match_detail', match_id=m['id']) }}"
                   aria-label="Ver palpites de {{ m['home'] }} x {{ m['away'] }}">
                   Ver palpites
                </a>
              </div>
            {% endif %}

          </div>

        {% endfor %}
        
        <div class="save-row right">
          {% if locked %}
            <button type="button" class="button-submit" disabled title="Apostas encerradas">Salvar {{ selected_group }}</button>
          {% else %}
            <button class="button-submit">Salvar {{ selected_group }}</button>
          {% endif %}
        </div>
        
      </form>
      {% else %}
        <p>0 jogos encontrados para o grupo {{ selected_group }}.</p>
      {% endif %}
    </div>
  </section>
</div>

<style>
/* ---- Design tokens (tweak here) ---- */
:root{
  --bg:#fff;
  --ink:#0f172a;
  --muted:#6b7280;
  --rule:#e5e7eb;
  --card:#ffffff;
  --radius:10px;
  --gap:28px;        /* space between the two columns */
  --colL: 520px;     /* wider min width for standings */
  --colBias: 42%;    /* share of grid for left column */
  --metaW: 220px;
  --inputW: 40px;
  --inputH: 35px;
}

/* Full layout grid with filter spanning both columns */
.page-grid{
  display:grid;
  grid-template-columns: minmax(420px, 42%) 1fr;
  gap: 28px;
  align-items:start;
}

/* Make inner cards line up with each other */
.left-card{
  width: 100%;
},
.right-card{
  height: 100%;
},



/* Cards */
.card{
  background:var(--card);
  border-radius:var(--radius);
  border:1px solid rgba(3,7,18,0.05);
  box-shadow:0 6px 18px rgba(15,23,42,0.06);
  padding:20px 16px 12px;
}
.card.flat{ box-shadow:none; border:1px solid rgba(3,7,18,0.04); }
.card-title{ margin:0 0 10px; font-size:16px; color:var(--ink); }

/* Table (standings) */
.table{
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;                 /* columns fill space evenly */
  font-size: 14px;
  color: var(--ink);
}

/* even column widths: #, Seleção, P, J, V, SG, GP */
.table thead th{ width: calc(100% / 7); }

.table th, .table td{
  border-bottom: 1px solid var(--rule);  /* was 'solid var(--rule)' */
  padding: 6px 8px;
}


.table th{
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  color: #FFFFFF;
  letter-spacing: .04em;
}

.center{ text-align: center; }
.left{ text-align: left; }

/* let the # column be natural (no forced 100%) */
.pos{ /* no width here */ }

/* team cell layout */
.team{
  display: flex;
  align-items: center;
  gap: 12px;                             /* slightly tighter than 18px */
}

.crest{
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #fff;
  object-fit: cover;
}

.name{
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}


.mono{ font-variant-numeric: tabular-nums; }

/* Highlighting */
tr.top2{ background:linear-gradient(90deg, rgba(0,128,0,.06), rgba(0,128,0,.02)); }
tr.best3{ background:linear-gradient(90deg, rgba(0,128,255,.06), rgba(0,128,255,.02)); }

/* Matches list */
.matches-compact{ width:100%;}
.match-line{
  display:grid;
  grid-template-columns: 1fr;
  row-gap: 1px;
  padding: 12px 4px;
  border-bottom: 5px solid var(--rule);
}
.match-line .meta{
  justify-content: center;
  text-align: center;
}

/* Meta/date */
.meta{
  display:flex;
  align-items:center;
  gap: 10px;
  font-size: .85rem;
  color: var(--muted);
}
.meta .date{ font-variant-numeric: tabular-nums; }

/* Teams + inputs row */
.fixture-flat{
  display:grid;
  grid-template-columns: minmax(0,1fr) 120px minmax(0,1fr);
  align-items:center; 
  column-gap: 5px; 
  min-width:0;
}
.fixture-flat .middle{
  /*margin-top: 1px;  */        /* try 4–8px to taste */
  /* or: transform: translateY(4px);  */
  position: relative; top:3px;
}

.side{ display:flex; align-items:center; gap:6px; min-width:0; }
.side.home{ justify-content:flex-end; }
.team-name.full{ font-size: 1.05rem; font-weight:1000; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:inline; }
.team-name.abbr{ font-weight:1000; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:none; }

/* actual result sits exactly under the input boxes (center lane) */
.actual-line{
  display:grid;
  grid-template-columns: minmax(0,1fr) 120px minmax(0,1fr);
  align-items:center;
  column-gap:20px;
  margin-top:0;
}
.actual-line .middle{
  grid-column:2;               /* center column */
  display:flex;
  justify-content:center;
  align-items:center;
  gap:8px;
}

/* Score inputs */
.middle{ display:flex; align-items:center; justify-content:center; gap:8px; }

/* make both input + static span use the same box model */
.box,
.box.box-static{
  width: var(--inputW);
  height: var(--inputH);
  box-sizing: border-box;        /* include border in width/height */
  padding: 0 6px;                /* same inner padding */
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
  line-height: 3;                /* avoid extra height differences */
}

/* inputs are replaced elements; align text like the spans */
input.box{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* static result boxes (spans) */
.box.box-static{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #808080;          /* optional muted bg */
}

/* optional: remove number spinners which change sizing in some browsers */
input[type="number"].box {
  -moz-appearance: textfield;
}
input[type="number"].box::-webkit-outer-spin-button,
input[type="number"].box::-webkit-inner-spin-button{
  -webkit-appearance: none;
  margin: 0;
}

/* Buttons / selects */
.button-submit{
  display:inline-block; padding:8px 14px; border-radius:8px;
  background:#0ea5e9; color:white; border:0; cursor:pointer;
  font-weight:600; text-decoration:none;
}
.button-submit[disabled]{ background:#9ca3af; cursor:not-allowed; }
select{ padding:6px 8px; border:1px solid #d1d5db; border-radius:8px; }

/* Utilities */
.save-row.right{ padding-top:12px; text-align:right; }

.filter-card{
  grid-column: 1 / -1; /* full width */
  background: transparent;
  border: 0;
  box-shadow: none;
  padding: 0;          /* remove the ring of empty space */
  margin: 0;
}

/* Let the select breathe a little, but fill width */
.filter-card form{
  padding: 0;
  margin: 20px;
}

.filter-card select{
  width: 100%;
  box-sizing: border-box;
  height: 44px;
  padding: 0;
  margin: 0;  
}

.points-pill{
    display:inline-block; padding:.15rem .5rem; border-radius:999px;
    font-weight:900; font-variant-numeric:tabular-nums; white-space:nowrap;
    border:1px solid transparent;
    font-size: 1.0rem;
}
.points-pill.p10{ background:#90EE90; border-color:#90EE90; color:#008000; } /* green */
.points-pill.p5 { background:#FFFF8F; border-color:#FFFF8F; color:#FFAA33; } /* yellow */
.points-pill.p0 { background:#e5e7eb; border-color:#e5e7eb; color:#111827; } /* black */

/* Exactly the gap you highlighted: after the first standings table */
.left-card .table-wrap + .card-title {
  margin-top: 40px;   /* increase as needed */
}


/* Responsive */
@media (max-width: 900px){
  .page-grid{ grid-template-columns: 1fr; }
  .left-card{ order:2; }
  .right-card{ order:1; }
  :root{ --metaW: 140px; --colBias: 100%; }
  .team-name.full{ display:none; }
  .team-name.abbr{ display:inline; }
}
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
    {% for m in matches %}
      {% set b = bets.get(m['id']) %}
      {% set pts = points.get(m['id']) %}

      <div class="match-line">
        <!-- date (centered) -->
        <div class="meta">
          <span class="date">{{ m.kickoff_utc | fmt_kickoff_pt('America/Sao_Paulo') }}</span>
          {% if m.get('stadium') %}
            <span class="stadium">• {{ m['stadium'] }}</span>
          {% endif %}
          {% if fh is not none and fa is not none %}
            {% if pts is not none %}
              <span class="points-pill {{ 'p10' if pts==10 else 'p5' if pts==5 else 'p0' }}">+{{ pts }}</span>
            {% endif %}
          {% endif %}
        </div>

        <!-- teams + inputs -->
        <div class="fixture-flat">
          <!-- HOME -->
          <div class="side home">
            {% set fuh = flag(m['home']) %}
            <span class="team-name full">{{ m['home'] }}</span>
            <span class="team-name abbr">{{ m.get('home_abbr') or (m['home']|abbr3) }}</span>
            {% if fuh %}<img class="crest" src="{{ fuh }}" alt="">{% endif %}
          </div>

          <!-- Inputs -->
          <div class="middle">
            <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                   name="h_{{ m['id'] }}"
                   value="{{ b['home_goals'] if b else '' }}"
                   {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
            <span class="x">x</span>
            <input class="box" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                   name="a_{{ m['id'] }}"
                   value="{{ b['away_goals'] if b else '' }}"
                   {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
          </div>

          <!-- AWAY -->
          <div class="side away">
            {% set fua = flag(m['away']) %}
            {% if fua %}<img class="crest" src="{{ fua }}" alt="">{% endif %}
            <span class="team-name full">{{ m['away'] }}</span>
            <span class="team-name abbr">{{ m.get('away_abbr') or (m['away']|abbr3) }}</span>
          </div>
        </div>

        {% if m.get('final_home_goals') is not none and m.get('final_away_goals') is not none %}
          <div class="actual-line">
            <div class="middle">
              <span class="box box-static">{{ m.final_home_goals }}</span>
              <span class="x">x</span>
              <span class="box box-static">{{ m.final_away_goals }}</span>
            </div>
          </div>
        {% endif %}

        {% if locked %}
          <div class="bets-row">
            <a class="button small"
               href="{{ url_for('match_detail', match_id=m['id']) }}"
               aria-label="Ver palpites de {{ m['home'] }} x {{ m['away'] }}">
               Ver palpites
            </a>
          </div>
        {% endif %}
      </div> <!-- ✅ properly closes .match-line -->
    {% endfor %}

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
/* ---- Design tokens (tweak here) ---- */
:root{
  --bg:#fff;
  --ink:#0f172a;
  --muted:#6b7280;
  --rule:#e5e7eb;
  --card:#ffffff;
  --radius:10px;
  --gap:28px;        /* space between the two columns */
  --colL: 520px;     /* wider min width for standings */
  --colBias: 42%;    /* share of grid for left column */
  --metaW: 220px;
  --inputW: 40px;
  --inputH: 35px;
}

/* Full layout grid with filter spanning both columns */
.page-grid{
  display:grid;
  grid-template-columns: minmax(420px, 42%) 1fr;
  gap: 28px;
  align-items:start;
}

/* Make inner cards line up with each other */
.left-card{
  width: 100%;
},
.right-card{
  height: 100%;
},



/* Cards */
.card{
  background:var(--card);
  border-radius:var(--radius);
  border:1px solid rgba(3,7,18,0.05);
  box-shadow:0 6px 18px rgba(15,23,42,0.06);
  padding:20px 16px 12px;
}
.card.flat{ box-shadow:none; border:1px solid rgba(3,7,18,0.04); }
.card-title{ margin:0 0 10px; font-size:16px; color:var(--ink); }

/* Table (standings) */
.table{
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;                 /* columns fill space evenly */
  font-size: 14px;
  color: var(--ink);
}

/* even column widths: #, Seleção, P, J, V, SG, GP */
.table thead th{ width: calc(100% / 7); }

.table th, .table td{
  border-bottom: 1px solid var(--rule);  /* was 'solid var(--rule)' */
  padding: 6px 8px;
}


.table th{
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  color: #FFFFFF;
  letter-spacing: .04em;
}

.center{ text-align: center; }
.left{ text-align: left; }

/* let the # column be natural (no forced 100%) */
.pos{ /* no width here */ }

/* team cell layout */
.team{
  display: flex;
  align-items: center;
  gap: 12px;                             /* slightly tighter than 18px */
}

.crest{
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #fff;
  object-fit: cover;
}

.name{
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}


.mono{ font-variant-numeric: tabular-nums; }

/* Highlighting */
tr.top2{ background:linear-gradient(90deg, rgba(0,128,0,.06), rgba(0,128,0,.02)); }
tr.best3{ background:linear-gradient(90deg, rgba(0,128,255,.06), rgba(0,128,255,.02)); }

/* Matches list */
.matches-compact{ width:100%;}
.match-line{
  display:grid;
  grid-template-columns: 1fr;
  row-gap: 1px;
  padding: 12px 4px;
  border-bottom: 5px solid var(--rule);
}
.match-line .meta{
  justify-content: center;
  text-align: center;
}

/* Meta/date */
.meta{
  display:flex;
  align-items:center;
  gap: 10px;
  font-size: .85rem;
  color: var(--muted);
}
.meta .date{ font-variant-numeric: tabular-nums; }

/* Teams + inputs row */
.fixture-flat{
  display:grid;
  grid-template-columns: minmax(0,1fr) 120px minmax(0,1fr);
  align-items:center; 
  column-gap: 5px; 
  min-width:0;
}
.fixture-flat .middle{
  /*margin-top: 1px;  */        /* try 4–8px to taste */
  /* or: transform: translateY(4px);  */
  position: relative; top:3px;
}

.side{ display:flex; align-items:center; gap:6px; min-width:0; }
.side.home{ justify-content:flex-end; }
.team-name.full{ font-size: 1.05rem; font-weight:1000; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:inline; }
.team-name.abbr{ font-weight:1000; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:none; }

/* actual result sits exactly under the input boxes (center lane) */
.actual-line{
  display:grid;
  grid-template-columns: minmax(0,1fr) 120px minmax(0,1fr);
  align-items:center;
  column-gap:20px;
  margin-top:0;
}
.actual-line .middle{
  grid-column:2;               /* center column */
  display:flex;
  justify-content:center;
  align-items:center;
  gap:8px;
}

/* Score inputs */
.middle{ display:flex; align-items:center; justify-content:center; gap:8px; }

/* make both input + static span use the same box model */
.box,
.box.box-static{
  width: var(--inputW);
  height: var(--inputH);
  box-sizing: border-box;        /* include border in width/height */
  padding: 0 6px;                /* same inner padding */
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
  line-height: 3;                /* avoid extra height differences */
}

/* inputs are replaced elements; align text like the spans */
input.box{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* static result boxes (spans) */
.box.box-static{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #808080;          /* optional muted bg */
}

/* optional: remove number spinners which change sizing in some browsers */
input[type="number"].box {
  -moz-appearance: textfield;
}
input[type="number"].box::-webkit-outer-spin-button,
input[type="number"].box::-webkit-inner-spin-button{
  -webkit-appearance: none;
  margin: 0;
}

/* Buttons / selects */
.button-submit{
  display:inline-block; padding:8px 14px; border-radius:8px;
  background:#0ea5e9; color:white; border:0; cursor:pointer;
  font-weight:600; text-decoration:none;
}
.button-submit[disabled]{ background:#9ca3af; cursor:not-allowed; }
select{ padding:6px 8px; border:1px solid #d1d5db; border-radius:8px; }

/* Utilities */
.save-row.right{ padding-top:12px; text-align:right; }

.filter-card{
  grid-column: 1 / -1; /* full width */
  background: transparent;
  border: 0;
  box-shadow: none;
  padding: 0;          /* remove the ring of empty space */
  margin: 0;
}

/* Let the select breathe a little, but fill width */
.filter-card form{
  padding: 0;
  margin: 20px;
}

.filter-card select{
  width: 100%;
  box-sizing: border-box;
  height: 44px;
  padding: 0;
  margin: 0;  
}

.points-pill{
    display:inline-block; padding:.15rem .5rem; border-radius:999px;
    font-weight:900; font-variant-numeric:tabular-nums; white-space:nowrap;
    border:1px solid transparent;
    font-size: 1.0rem;
}
.points-pill.p10{ background:#90EE90; border-color:#90EE90; color:#008000; } /* green */
.points-pill.p5 { background:#FFFF8F; border-color:#FFFF8F; color:#FFAA33; } /* yellow */
.points-pill.p0 { background:#e5e7eb; border-color:#e5e7eb; color:#111827; } /* black */

/* Exactly the gap you highlighted: after the first standings table */
.left-card .table-wrap + .card-title {
  margin-top: 40px;   /* increase as needed */
}


/* Responsive */
@media (max-width: 900px){
  .page-grid{ grid-template-columns: 1fr; }
  .left-card{ order:2; }
  .right-card{ order:1; }
  :root{ --metaW: 140px; --colBias: 100%; }
  .team-name.full{ display:none; }
  .team-name.abbr{ display:inline; }
}

"""

MATCH_BREAKDOWN = """
<div class="section">
      <h2 style="margin: 0 0 6px 0;">{{ fixture['home'] }} x {{ fixture['away'] }}</h2>
      <div style="color:#666; font-size:14px; margin-bottom:10px;"></div>
    
      {% if total_bets == 0 %}
        <p style="color:#666">No bets for this match yet.</p>
      {% else %}
        <!-- Stacked bar -->
        <div class="stack-wrap" aria-label="Distribuição de palpites">
          <div class="stack-bar" role="img"
               aria-label="{{ fixture['home'] }} {{ stack.home_pct }} por cento, Empate {{ stack.draw_pct }} por cento, {{ fixture['away'] }} {{ stack.away_pct }} por cento">
            <div class="seg" style="width: {{ stack.home_pct }}%; background: {{ colors.home }};"
                 title="{{ fixture['home'] }}: {{ stack.home_cnt }} ({{ stack.home_pct }}%)"></div>
            <div class="seg" style="width: {{ stack.draw_pct }}%; background: {{ colors.draw }};"
                 title="Empate: {{ stack.draw_cnt }} ({{ stack.draw_pct }}%)"></div>
            <div class="seg" style="width: {{ stack.away_pct }}%; background: {{ colors.away }};"
                 title="{{ fixture['away'] }}: {{ stack.away_cnt }} ({{ stack.away_pct }}%)"></div>
          </div>
    
          <!-- Legend with flags -->
          <div class="stack-legend">
            <div class="legend-item">
              {% set fhome = flag(fixture['home']) %}
              {% if fhome %}<img class="flag" src="{{ fhome }}" alt="{{ fixture['home'] }}">{% else %}<span class="abbr">{{ fixture['home'] }}</span>{% endif %}
              <span class="color-dot" style="background: {{ colors.home }};"></span>
              <span class="muted">{{ stack.home_pct }}%</span>
            </div>
            <div class="legend-item">
              <span class="badge-draw">Empate</span>
              <span class="color-dot" style="background: {{ colors.draw }};"></span>
              <span class="muted">{{ stack.draw_pct }}%</span>
            </div>
            <div class="legend-item">
              {% set faway = flag(fixture['away']) %}
              {% if faway %}<img class="flag" src="{{ faway }}" alt="{{ fixture['away'] }}">{% else %}<span class="abbr">{{ fixture['away'] }}</span>{% endif %}
              <span class="color-dot" style="background: {{ colors.away }};"></span>
              <span class="muted">{{ stack.away_pct }}%</span>
            </div>
          </div>
        </div>
      {% endif %}

    <h3 style="margin-top:30px;">
    </h3>

    <!-- Top exact-score picks -->
    <table class="table" id="top-scores">
        <thead>
            <tr><th>Placar</th><th>#</th><th>%</th></tr>
        </thead>
        <tbody>
          {% for r in top_scores %}
            {% set score = r['home_goals'] ~ '-' ~ r['away_goals'] %}
            {% set outcome = 'draw' if r['home_goals'] == r['away_goals'] else ('home' if r['home_goals'] > r['away_goals'] else 'away') %}
            <tr class="score-row clickable o-{{ outcome }}"
                data-score="{{ score }}"
                style="--bg: {{ bg[outcome] }}; --edge: {{ edge[outcome] }};"
                title="Mostrar quem apostou {{ score }}">
              <td>{{ r['home_goals'] }}–{{ r['away_goals'] }}</td>
              <td>{{ r['cnt'] }}</td>
              <td>{{ (100 * r['cnt'] / total_bets) | int }}%</td>
            </tr>
          {% endfor %}
        </tbody>
    </table>

    <h3 style="margin-top:18px;">
      All picks
      <small id="filter-chip" style="display:none; margin-left:.5rem;"></small>
    </h3>

    <table class="table" id="all-picks">
        <thead>
            <tr><th>Jogador</th><th>Palpite</th></tr>
        </thead>
        <tbody>
          {% for p in picks %}
            {% set score = p['home_goals'] ~ '-' ~ p['away_goals'] %}
            {% set outcome = 'draw' if p['home_goals'] == p['away_goals']
                             else ('home' if p['home_goals'] > p['away_goals'] else 'away') %}
            <tr class="pick-row o-{{ outcome }}" data-score="{{ score }}"
                style="--bg: {{ bg[outcome] }}; --edge: {{ edge[outcome] }};">
              <td>{{ p['user_name'] }}</td>
              <td>{{ p['home_goals'] }}–{{ p['away_goals'] }}</td>
            </tr>
          {% endfor %}
        </tbody>
    </table>

<script>
(function(){
  const scoreRows = Array.from(document.querySelectorAll('#top-scores .score-row'));
  const pickRows  = Array.from(document.querySelectorAll('#all-picks .pick-row'));

  // Create the chip if missing to avoid null errors
  let chip = document.getElementById('filter-chip');
  if (!chip) {
    const h3 = document.querySelector('h3 + table#all-picks')?.previousElementSibling;
    chip = document.createElement('small');
    chip.id = 'filter-chip'; chip.style.display = 'none'; chip.style.marginLeft = '.5rem';
    if (h3) h3.appendChild(chip);
  }

  let active = null; // e.g. "2-1"

  function updateChip(){
    if (!chip) return;
    if (!active){
      chip.style.display = 'none';
      chip.textContent = '';
      return;
    }
    const visible = pickRows.filter(tr => tr.style.display !== 'none').length;
    chip.style.display = '';
    chip.innerHTML = `Filtro: <strong>${active}</strong> • ${visible} usuário(s)
      <a href="#" id="clear-filter" style="margin-left:.4rem;">limpar</a>`;
    chip.querySelector('#clear-filter').addEventListener('click', function(e){
      e.preventDefault(); clearFilter();
    }, {once:true});
  }

  function applyFilter(score){
    active = score;
    scoreRows.forEach(tr => tr.classList.toggle('active', tr.dataset.score === score));
    pickRows.forEach(tr => { tr.style.display = (tr.dataset.score === score) ? '' : 'none'; });
    updateChip();
    document.getElementById('all-picks').scrollIntoView({behavior:'smooth', block:'start'});
  }

  function clearFilter(){
    active = null;
    scoreRows.forEach(tr => tr.classList.remove('active'));
    pickRows.forEach(tr => { tr.style.display = ''; });
    updateChip();
  }

  // Hook up events
  scoreRows.forEach(tr => {
    tr.addEventListener('click', () => (active === tr.dataset.score) ? clearFilter() : applyFilter(tr.dataset.score));
    tr.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tr.click(); }});
    tr.tabIndex = 0;
  });
})();
</script>

  <div style="margin-top:16px;">
    <a href="{{ back_url }}">&larr; Voltar</a>
  </div>
  
</div>
"""
