BASE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/mvp.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&family=Montserrat:wght@600;700;800;900&display=swap" rel="stylesheet">

<style>
  :root {
    --pad: 12px;
    --font-body: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-heading: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

    /* FIFA-inspired color palette */
    --primary-blue: #0055A4;
    --primary-blue-dark: #003d7a;
    --primary-blue-light: #1a6bb8;
    --accent-gold: #FFB81C;
    --accent-gold-dark: #E5A419;
    --accent-red: #E31E24;
    --success-green: #00B140;
    --success-green-light: #e8f5e9;
    --text-dark: #1a1a1a;
    --text-gray: #4a5568;
    --text-light: #6b7280;
    --bg-light: #f8fafc;
    --bg-white: #ffffff;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }

  * {
    -webkit-tap-highlight-color: transparent;
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: var(--font-body);
    letter-spacing: 0.01em;
    background: linear-gradient(135deg, #f8fafc 0%, #e8f0f7 100%);
    min-height: 100vh;
    color: var(--text-dark);
    overflow-x: hidden; /* Prevent horizontal scroll */
    -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
  }

  /* Prevent horizontal overflow on all containers */
  html {
    overflow-x: hidden;
  }

  /* Ensure all major containers don't overflow */
  main, header, .fixtures, .table-wrap {
    max-width: 100vw;
    overflow-x: hidden;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading);
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-dark);
  }

  h1 {
    font-weight: 900;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  h2 {
    color: var(--primary-blue);
    font-weight: 800;
  }

  /* Enhanced buttons */
  .button, button {
    font-family: var(--font-heading);
    font-weight: 700;
    letter-spacing: -0.01em;
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-sm);
    text-decoration: none;
    display: inline-block;
    text-align: center;
    min-height: 44px; /* iOS minimum touch target */
    line-height: 1.4;
  }

  .button:hover, button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, var(--primary-blue-light) 0%, var(--primary-blue) 100%);
  }

  .button:active, button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
  }

  /* Better touch targets for mobile */
  @media (hover: none) and (pointer: coarse) {
    .button:hover, button:hover {
      transform: none; /* Disable hover transform on touch devices */
    }

    .fixtures tbody tr:hover {
      transform: none; /* Disable row hover on touch */
    }
  }

  /* shared widgets */
  .result-line{
    display:flex; align-items:center; justify-content:center; gap:.5rem;
    margin-top:.35rem;
  }
  .final-pill{
    display:inline-block;
    padding:.25rem .6rem;
    border-radius:999px;
    font-weight:700;
    font-variant-numeric:tabular-nums;
    background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 100%);
    border:1px solid #93c5fd;
    color: var(--primary-blue);
    white-space:nowrap;
    box-shadow: var(--shadow-sm);
    font-size: 0.9rem;
  }
  .points-pill{
    display:inline-block;
    padding:.25rem .6rem;
    border-radius:999px;
    font-weight:800;
    font-variant-numeric:tabular-nums;
    white-space:nowrap;
    border:2px solid;
    box-shadow: var(--shadow-sm);
    font-size: 0.85rem;
    transition: all 0.2s ease;
  }
  .points-pill.p10{
    background: linear-gradient(135deg, var(--success-green) 0%, #00953d 100%);
    border-color: var(--success-green);
    color: white;
  }
  .points-pill.p5 {
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dark) 100%);
    border-color: var(--accent-gold-dark);
    color: var(--text-dark);
  }
  .points-pill.p0 {
    background: #e5e7eb;
    border-color: #9ca3af;
    color: var(--text-gray);
  }

  /* inputs/buttons disabled look */
  input[disabled]{opacity:.6; cursor:not-allowed;}
  button[disabled]{opacity:.6; cursor:not-allowed;}

  @media (max-width: 520px){
    .result-line{ margin-top:.25rem; }
  }

  /* Main container */
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--pad);
  }

  /* Enhanced header */
  header {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    padding: 24px var(--pad);
    margin-bottom: 32px;
    box-shadow: var(--shadow-lg);
    border-bottom: 4px solid var(--accent-gold);
  }

  header h1 {
    margin: 0 0 8px 0;
    color: white;
    background: none;
    -webkit-text-fill-color: white;
  }

  header small, header a {
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
  }

  header a {
    text-decoration: underline;
    transition: color 0.2s ease;
  }

  header a:hover {
    color: var(--accent-gold);
  }

  header p {
    background: rgba(255, 255, 255, 0.15);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 4px solid var(--accent-gold);
    backdrop-filter: blur(10px);
  }

  /* Container */
  .fixtures {
    max-width: 980px;
    margin: 0 auto;
    padding: 0 var(--pad);
  }

  /* Sticky toolbar (group filter) */
  .toolbar {
    position: sticky;
    top: 0;
    z-index: 5;
    backdrop-filter: saturate(180%) blur(10px);
    background: rgba(255, 255, 255, 0.95);
    padding: 12px var(--pad);
    border-bottom: 2px solid var(--border-color);
    box-shadow: var(--shadow-sm);
    margin-bottom: 16px;
  }

  .toolbar form {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .toolbar select {
    font-size: 16px;
    padding: 10px 14px;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    background: white;
    font-family: var(--font-heading);
    font-weight: 600;
    color: var(--text-dark);
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .toolbar select:hover {
    border-color: var(--primary-blue);
  }

  .toolbar select:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(0, 85, 164, 0.1);
  }

  .toolbar label {
    font-family: var(--font-heading);
    font-weight: 700;
    color: var(--text-dark);
  }

  /* Table - Enhanced styling */
  .fixtures table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
    margin-top: -8px;
  }

  .fixtures tbody tr {
    background: white;
    box-shadow: var(--shadow-sm);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .fixtures tbody tr:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }

  .fixtures tbody tr td:first-child {
    border-top-left-radius: 12px;
    border-bottom-left-radius: 12px;
  }

  .fixtures tbody tr td:last-child {
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
  }

  .fixture-cell {
    padding: 16px 12px;
    overflow: visible;
    background: white;
  }

  /* Table headers */
  .fixtures thead th {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    color: white;
    padding: 12px 16px;
    font-family: var(--font-heading);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    border: none;
  }

  .fixtures thead th:first-child {
    border-top-left-radius: 8px;
  }

  .fixtures thead th:last-child {
    border-top-right-radius: 8px;
  }

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
  .team .name {
    white-space: nowrap;
    font-family: var(--font-heading);
    font-weight: 700;
    line-height: 1.1;
    font-size: clamp(0.78rem, 2.3vw, 1.0rem);
    letter-spacing: -0.01em;
  }

  .sep { text-align: center; }

  /* Enhanced score inputs */
  .score {
    display: inline-block !important;
    width: 40px !important;
    max-width: 40px !important;
    height: 36px;
    line-height: 36px;
    text-align: center;
    font-size: 16px;
    font-family: var(--font-heading);
    font-weight: 700;
    padding: 0 4px;
    margin: 0;
    border-radius: 8px;
    border: 2px solid var(--border-color);
    background: white;
    transition: all 0.2s ease;
    color: var(--primary-blue);
  }

  .score:hover:not([disabled]) {
    border-color: var(--primary-blue-light);
    box-shadow: 0 0 0 3px rgba(0, 85, 164, 0.1);
  }

  .score:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 4px rgba(0, 85, 164, 0.15);
  }

  /* Separator styling */
  .sep {
    text-align: center;
    font-weight: 700;
    color: var(--text-light);
    font-size: 18px;
  }

  /* Enhanced flags */
  .flagbox {
    flex: 0 0 auto;
    display: inline-block;
    width: 28px;
    height: 18px;
    line-height: 0;
    border-radius: 4px;
    background: #fff;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    overflow: hidden;
  }
  .flagbox > img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* Enhanced Sticky Save bar */
  .save-row {
    position: sticky;
    bottom: 0;
    z-index: 4;
    background: linear-gradient(to top, white 0%, rgba(255, 255, 255, 0.98) 100%);
    padding: 16px var(--pad);
    border-top: 2px solid var(--border-color);
    box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
  }

  .save-row button {
    width: 100%;
    padding: 16px 24px;
    font-size: 17px;
    font-weight: 800;
    border-radius: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dark) 100%);
    color: var(--text-dark);
    box-shadow: var(--shadow-md);
  }

  .save-row button:hover:not([disabled]) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }

  /* Hide number spinners */
  input[type=number].score::-webkit-outer-spin-button,
  input[type=number].score::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
  input[type=number].score { -moz-appearance: textfield; }

/* ---------- Mobile layout optimizations ---------- */
@media (max-width: 768px) {
  /* Reduce header padding */
  header {
    padding: 16px var(--pad);
    margin-bottom: 20px;
  }

  header h1 {
    font-size: 1.5rem;
  }

  /* Better spacing for mobile */
  main {
    padding: 0 8px;
  }

  h2, h3 {
    margin-top: 20px;
    margin-bottom: 12px;
    font-size: 1.3rem;
  }

  /* Optimize toolbar for mobile */
  .toolbar {
    padding: 10px 8px;
  }

  .toolbar label {
    font-size: 0.9rem;
  }

  .toolbar select {
    font-size: 14px;
    padding: 8px 12px;
  }

  /* Better button sizing on mobile */
  .button, button {
    padding: 10px 18px;
    font-size: 0.9rem;
  }

  /* Fixtures table mobile adjustments */
  .fixtures {
    padding: 0 4px;
  }

  .fixtures tbody tr {
    border-radius: 10px;
    margin-bottom: 8px;
  }

  .fixture-cell {
    padding: 12px 8px;
  }

  .fixtures thead th {
    padding: 10px 8px;
    font-size: 0.75rem;
  }
}

@media (max-width: 600px) {
  /* Hide date column, show it inline */
  .fixtures .kick-col { display: none; }
  .fixtures thead th:first-child { display: none; }
  .fixtures .kick-mobile {
    display: block;
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-light);
    margin: 0 0 8px 0;
    font-weight: 600;
  }

  /* Tighter grid for mobile */
  .fixtures .fixture-row {
    grid-template-columns: minmax(0, 1fr) auto 8px auto minmax(0, 1fr);
    column-gap: 4px;
    row-gap: 4px;
  }

  /* Adjust team names and flags */
  .fixtures .team {
    gap: 4px;
  }

  .fixtures .team .name {
    font-size: clamp(0.75rem, 3vw, 0.9rem);
  }

  .fixtures .flagbox {
    width: 24px;
    height: 16px;
  }

  /* Optimize score inputs for mobile */
  .fixtures .score {
    width: 36px !important;
    max-width: 36px !important;
    height: 32px !important;
    line-height: 32px !important;
    font-size: 14px !important;
    padding: 0 2px !important;
  }

  .fixtures .sep {
    font-size: 14px;
  }

  /* Better pills on mobile */
  .final-pill, .points-pill {
    font-size: 0.75rem;
    padding: 0.2rem 0.4rem;
  }

  /* Optimize save button for mobile */
  .save-row {
    padding: 12px 8px;
  }

  .save-row button {
    padding: 14px 20px;
    font-size: 15px;
  }

  /* Better table cards on mobile */
  .table {
    font-size: 0.85rem;
  }

  .table thead th {
    padding: 10px 6px;
    font-size: 0.7rem;
  }

  .table tbody td {
    padding: 8px 6px;
  }

  /* Optimize home page buttons */
  .button {
    font-size: 0.9rem;
    padding: 12px 16px;
  }

  /* Better form inputs on mobile */
  input[type="text"],
  input[type="password"],
  input[type="email"],
  select,
  textarea {
    font-size: 16px; /* Prevents zoom on iOS */
    padding: 10px 12px;
  }
}




/* Very narrow phones (iPhone SE, small Android) */
@media (max-width: 400px) {
  /* Further reduce spacing */
  header {
    padding: 12px 8px;
  }

  header h1 {
    font-size: 1.3rem;
  }

  main {
    padding: 0 4px;
  }

  h2 {
    font-size: 1.2rem;
  }

  h3 {
    font-size: 1rem;
  }

  /* Ultra-compact fixture rows */
  .fixtures .fixture-row {
    grid-template-columns: minmax(0, 1fr) auto 6px auto minmax(0, 1fr);
    column-gap: 3px;
  }

  .fixtures .team .name {
    font-size: clamp(0.7rem, 3.5vw, 0.85rem);
  }

  .fixtures .flagbox {
    width: 20px;
    height: 14px;
  }

  .fixtures .score {
    width: 32px !important;
    max-width: 32px !important;
    height: 30px !important;
    line-height: 30px !important;
    font-size: 13px !important;
  }

  .fixtures .sep {
    font-size: 12px;
  }

  /* Smaller pills */
  .final-pill, .points-pill {
    font-size: 0.7rem;
    padding: 0.15rem 0.35rem;
  }

  /* Compact table */
  .table {
    font-size: 0.75rem;
  }

  .table thead th {
    padding: 8px 4px;
    font-size: 0.65rem;
  }

  .table tbody td {
    padding: 6px 4px;
  }

  /* Smaller buttons */
  .button.small {
    padding: 6px 10px;
    font-size: 0.75rem;
  }

  .save-row button {
    padding: 12px 16px;
    font-size: 14px;
  }

  /* Toolbar compact */
  .toolbar {
    padding: 8px 4px;
  }

  .toolbar select {
    font-size: 13px;
    padding: 6px 10px;
  }
}
</style>

<style>
  /* Enhanced table styling for rankings and standings */
  .table {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-md);
  }

  .table thead th {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    color: white;
    padding: 14px 12px;
    font-family: var(--font-heading);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
  }

  .table tbody td {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s ease;
  }

  .table tbody tr:last-child td {
    border-bottom: none;
  }

  .table tbody tr:hover {
    background: var(--bg-light);
  }

  /* Highlight top 2 teams */
  .table .top2 td {
    background: linear-gradient(135deg, var(--success-green-light) 0%, #d4f4dd 100%);
    font-weight: 600;
  }

  .table .top2 td:first-child {
    border-left: 4px solid var(--success-green);
  }

  /* Highlight 3rd place if qualified */
  .table .best3 td {
    background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
    font-weight: 600;
  }

  .table .best3 td:first-child {
    border-left: 4px solid #0ea5e9;
  }
</style>

<style>
  /* Highlight the logged-in user's row in Ranking */
  .table .me td {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    font-weight: 800;
    color: var(--text-dark);
  }

  .table .me td:first-child {
    border-left: 4px solid var(--accent-gold);
  }

  /* Enhanced form inputs */
  input[type="text"],
  input[type="password"],
  input[type="email"],
  select,
  textarea {
    font-family: var(--font-body);
    padding: 12px 14px;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    font-size: 15px;
    transition: all 0.2s ease;
    background: white;
    color: var(--text-dark);
  }

  input[type="text"]:hover,
  input[type="password"]:hover,
  input[type="email"]:hover,
  select:hover,
  textarea:hover {
    border-color: var(--primary-blue-light);
  }

  input[type="text"]:focus,
  input[type="password"]:focus,
  input[type="email"]:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(0, 85, 164, 0.1);
  }

  label {
    font-family: var(--font-heading);
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 6px;
    display: block;
  }

  /* Small buttons for "Ver palpites" etc */
  .button.small {
    padding: 8px 14px;
    font-size: 0.85rem;
    font-weight: 700;
    border-radius: 6px;
    letter-spacing: 0;
  }

  /* Smooth page animations */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  main {
    animation: fadeIn 0.4s ease-out;
  }

  /* Link styling */
  a {
    color: var(--primary-blue);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
  }

  a:hover {
    color: var(--primary-blue-light);
    text-decoration: underline;
  }

  /* Improved section spacing */
  h2, h3 {
    margin-top: 32px;
    margin-bottom: 16px;
  }

  /* Better kickoff time styling */
  .kickoff {
    font-size: 0.8rem;
    color: var(--text-light);
    font-weight: 500;
  }
</style>

<style>
  /* --- Generic responsive table support (for Ranking etc.) --- */
  .table-wrap {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    position: relative;
    margin-bottom: 16px;
  }

  /* Visual indicator for scrollable content on mobile */
  @media (max-width: 768px) {
    .table-wrap::after {
      content: '← Arraste para ver mais →';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      text-align: center;
      font-size: 0.7rem;
      color: var(--text-light);
      background: linear-gradient(to top, rgba(255,255,255,0.95), transparent);
      padding: 8px 4px 4px;
      pointer-events: none;
      opacity: 0.8;
    }

    .table-wrap.scrolled::after {
      display: none; /* Hide hint after user scrolls */
    }
  }

  .table {
    width: 100%;
    min-width: 480px;
  }

  @media (max-width: 480px) {
    .table {
      min-width: 320px; /* Allow table to be narrower on mobile */
      font-size: 0.8rem;
    }

    th, td {
      padding: 6px 4px;
    }
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
.legend-item{ display:flex; align-items:center; gap:8px; font-size:14px; }
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
      <div class="table-wrap">
      <table>
      {% set show_bets_col = locked %}

    <colgroup>
      <col class="c-kick">
      <col class="c-fixture">
      {% if show_bets_col %}<col class="c-bets">{% endif %}
    </colgroup>

<thead>
  <tr>
    <th class="kick-col">Data</th>
    <th>Jogo</th>
    {% if show_bets_col %}<th class="bets-col">Palpites</th>{% endif %}
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

            <div class="score-wrap" role="group" aria-label="Palpite de placar">
              <input class="score" type="number" min="0" step="1" inputmode="numeric" pattern="\d*"
                     name="h_{{ m['id'] }}"
                     value="{{ b['home_goals'] if b else '' }}"
                     {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
              <span class="sep" aria-hidden="true">x</span>
              <input class="score" type="number" min="0" step="1" inputmode="numeric" pattern="\d*"
                     name="a_{{ m['id'] }}"
                     value="{{ b['away_goals'] if b else '' }}"
                     {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
            </div>

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

          {% if show_bets_col %}
            <td class="bets-col">
              <a class="button small"
                 href="{{ url_for('match_detail', match_id=m['id']) }}"
                 aria-label="Ver palpites de {{ m['home'] }} x {{ m['away'] }}">
                Ver palpites
              </a>
            </td>
          {% endif %}
            
          </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>

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

{% if standings and standings|length >= 1 %}
  <h3 style="margin-top:1rem;">Classificação (meu palpite)</h3>
  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th class="center" style="width:60px;">Pos</th>
          <th class="left">Seleção</th>
          <th class="center">J</th>
          <th class="center">V</th>
          <th class="center">E</th>
          <th class="center">D</th>
          <th class="center">GP</th>
          <th class="center">GC</th>
          <th class="center">SG</th>
          <th class="center">Pts</th>
        </tr>
      </thead>
    <tbody>
      {% for r in standings %}
        <tr class="{% if r.rank <= 2 %}top2{% elif r.rank == 3 and r.team in best3 %}best3{% endif %}">
          <td class="center">{{ r.rank }}</td>
          <td class="left">{{ r.team }}</td>
          <td class="center">{{ r.played }}</td>
          <td class="center">{{ r.won }}</td>
          <td class="center">{{ r.draw }}</td>
          <td class="center">{{ r.lost }}</td>
          <td class="center">{{ r.gf }}</td>
          <td class="center">{{ r.ga }}</td>
          <td class="center">{{ r.gd }}</td>
          <td class="center"><strong>{{ r.pts }}</strong></td>
        </tr>
      {% endfor %}
    </tbody>
    </table>
  </div>
{% endif %}

<style>
  input[disabled]{opacity:.6; cursor:not-allowed;}
  button[disabled]{opacity:.6; cursor:not-allowed;}
  .button.small{ padding:.3rem .6rem; font-size:.9rem; }

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

    <div class="table-wrap">
      <table>
        <colgroup>
          <col class="c-kick">     <!-- date/time -->
          <col class="c-fixture">  <!-- match (flexes) -->
          <col class="c-bets">     <!-- button -->
        </colgroup>

        <thead>
          <tr>
            <th class="kick-col">Data</th>
            <th>Jogo</th>
            <th class="bets-col">Palpites</th>
          </tr>
        </thead>

        <tbody>
        {% for m in matches %}
          {% set b = bets.get(m['id']) %}
          <tr>
            <!-- Data -->
            <td class="kick-col">
              <div class="kickoff">{{ m['kickoff_utc']|fmtkick }}</div>
            </td>

            <!-- Fixture -->
            <td class="fixture-cell">
              <!-- Mobile-only date -->
              <div class="kick-mobile">{{ m['kickoff_utc']|fmtkick }}</div>

              <div class="fixture-row">
                <!-- HOME -->
                <div class="team left">
                  <span class="name">{{ m['home'] }}</span>
                  {% set fu = flag(m['home']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt="">{% endif %}
                </div>

                <!-- Scores (aligned) -->
                <div class="score-wrap" role="group" aria-label="Palpite de placar">
                  <input class="score" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                         name="h_{{ m['id'] }}"
                         value="{{ b['home_goals'] if b else '' }}"
                         {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                  <span class="sep" aria-hidden="true">x</span>
                  <input class="score" type="number" min="0" step="1" inputmode="numeric" pattern="\\d*"
                         name="a_{{ m['id'] }}"
                         value="{{ b['away_goals'] if b else '' }}"
                         {% if locked %}disabled aria-disabled="true" title="Apostas encerradas"{% endif %}>
                </div>

                <!-- AWAY -->
                <div class="team right">
                  {% set fu = flag(m['away']) %}
                  {% if fu %}<span class="flagbox"><img src="{{ fu }}" alt="">{% endif %}
                  <span class="name">{{ m['away'] }}</span>
                </div>
              </div>

              {# Official result + points #}
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

            <!-- Bets link -->
            <td class="bets-col">
              <a class="button small"
                 href="{{ url_for('match_detail', match_id=m['id']) }}"
                 aria-label="Ver palpites de {{ m['home'] }} x {{ m['away'] }}">
                 Ver palpites
              </a>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="save-row">
      {% if locked %}
        <button type="button" class="button" disabled title="Apostas encerradas">{{ button_label }}</button>
      {% else %}
        <button class="button">{{ button_label }}</button>
      {% endif %}
    </div>
  </form>
</div>
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

<!-- Top exact-score picks -->
<table class="table" id="top-scores">
  <thead>
    <tr><th>Score</th><th>Picks</th><th>%</th></tr>
  </thead>
<tbody>
  {% for r in top_scores %}
    {% set score = r['home_goals'] ~ '-' ~ r['away_goals'] %}
    {% set outcome = 'draw' if r['home_goals'] == r['away_goals']
                     else ('home' if r['home_goals'] > r['away_goals'] else 'away') %}
    <tr class="score-row clickable o-{{ outcome }}"
        data-score="{{ score }}"
        style="--bg: {{ bg[outcome] }}; --edge: {{ edge[outcome] }};"
        title="Mostrar quem apostou {{ score }}">
      <td>{{ r['home_goals'] }}–{{ r['away_goals'] }}</td>
      <td>{{ r['cnt'] }}</td>
      <td>{{ (100.0 * r['cnt'] / total_bets) | round(1) }}%</td>
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
