BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bolão Copa 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    {% block content %}{% endblock %}
</body>
</html>
'''

LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <div class="min-h-screen flex items-center justify-center px-4">
        <div class="max-w-md w-full">
            <!-- Logo/Title -->
            <div class="text-center mb-8">
                <h1 class="text-5xl font-black text-blue-600 mb-2">Bolão</h1>
                <p class="text-2xl font-bold text-slate-700">Copa do Mundo 2026</p>
            </div>

            <!-- Login Card -->
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <h2 class="text-2xl font-bold text-slate-800 mb-6">Entrar</h2>

                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="mb-4 p-4 rounded-lg {% if category == 'error' %}bg-red-50 text-red-800 border border-red-200{% elif category == 'success' %}bg-green-50 text-green-800 border border-green-200{% else %}bg-blue-50 text-blue-800 border border-blue-200{% endif %}">
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                <form method="POST" class="space-y-6">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Usuário</label>
                        <input type="text" name="username" required
                               class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition"
                               placeholder="Digite seu usuário">
                    </div>

                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Senha</label>
                        <input type="password" name="password" required
                               class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition"
                               placeholder="Digite sua senha">
                    </div>

                    <button type="submit"
                            class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 transition transform hover:scale-[1.02] active:scale-[0.98]">
                        Entrar
                    </button>
                </form>

                <div class="mt-6 pt-6 border-t border-slate-200">
                    <p class="text-sm text-slate-600 text-center">
                        Senha de teste: <span class="font-mono font-semibold">senha123</span>
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <!-- Welcome Header -->
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Olá, {{ user_name }}!</h1>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-6 p-4 rounded-xl {% if category == 'success' %}bg-green-50 text-green-800 border-2 border-green-200{% elif category == 'error' %}bg-red-50 text-red-800 border-2 border-red-200{% else %}bg-blue-50 text-blue-800 border-2 border-blue-200{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            <!-- Total Points -->
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6 text-white">
                <div class="mb-2">
                    <span class="text-xs md:text-sm font-semibold uppercase tracking-wide opacity-90">Total de Pontos</span>
                </div>
                <div class="text-3xl md:text-4xl font-black">{{ total_points }}</div>
                <div class="text-xs md:text-sm opacity-75 mt-1">pontos acumulados</div>
            </div>

        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-1 gap-6">

            <!-- View Regras Card -->
            <a href="{{ url_for('regras') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02] md:col-span-2 border-l-4 border-blue-500">
                <div>
                    <h3 class="text-xl font-bold text-slate-800 mb-1">Regras</h3>
                </div>
            </a>

            <!-- View Ranking Card -->
            <a href="{{ url_for('ranking') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02] md:col-span-2 border-l-4 border-blue-500">
                <div>
                    <h3 class="text-xl font-bold text-slate-800 mb-1">Ranking</h3>
                </div>
            </a>

            <!-- Make Predictions Card -->
            <a href="{{ url_for('matches') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02] md:col-span-2 border-l-4 border-blue-500">
                <div>
                    <h3 class="text-xl font-bold text-slate-800 mb-1">Fazer Palpites</h3>
                </div>
            </a>

            <!-- Extras Card -->
            <a href="{{ url_for('palpites_gerais') }}" class="block bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition transform hover:scale-[1.02] md:col-span-2 border-l-4 border-blue-500">
                <div>
                    <h3 class="text-xl font-bold text-slate-800 mb-1">Extras</h3>
                </div>
            </a>
        </div>
    </div>
</body>
</html>
'''

RANKING_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-medium text-slate-600 hover:text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-semibold text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-medium text-slate-600 hover:text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-[1400px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Ranking Geral</h1>
            <p class="text-base md:text-lg text-slate-600">Classificação de todos os participantes</p>
        </div>

        <!-- Ranking Table -->
        <div class="bg-white rounded-xl md:rounded-2xl shadow-xl overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                        <tr>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-center text-xs md:text-sm font-bold uppercase tracking-wider w-20">Pos</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-left text-xs md:text-sm font-bold uppercase tracking-wider">Jogador</th>
                            <th class="px-3 md:px-6 py-3 md:py-4 text-center text-xs md:text-sm font-bold uppercase tracking-wider w-32">Pontos</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        {% for rank in rankings %}
                            <tr class="{% if rank.id == current_user_id %}bg-yellow-50 border-l-4 border-yellow-500{% else %}hover:bg-slate-50{% endif %} transition cursor-pointer" onclick="window.location.href='{{ url_for('jogador_detail', user_id=rank.id) }}'">
                                <td class="px-3 md:px-6 py-3 md:py-4 text-center">
                                    <span class="text-lg md:text-xl font-black {% if loop.index <= 3 %}text-blue-600{% else %}text-slate-400{% endif %}">#{{ loop.index }}</span>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4">
                                    <a href="{{ url_for('jogador_detail', user_id=rank.id) }}" class="font-bold text-base md:text-lg text-slate-800 hover:text-blue-600 transition">
                                        {{ rank.user_name }}
                                        {% if rank.id == current_user_id %}
                                            <span class="ml-2 text-xs font-semibold bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full">Você</span>
                                        {% endif %}
                                    </a>
                                </td>
                                <td class="px-3 md:px-6 py-3 md:py-4 text-center">
                                    <span class="text-2xl md:text-3xl font-black text-blue-600">{{ rank.total_points or 0 }}</span>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="{{ url_for('dashboard') }}" class="text-blue-600 hover:text-blue-700 font-semibold">
                ← Voltar ao Início
            </a>
        </div>
    </div>
</body>
</html>
'''

MATCHES_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palpites - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
        /* Hide number input spinners */
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        input[type=number] {
            -moz-appearance: textfield;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-semibold text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-medium text-slate-600 hover:text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-medium text-slate-600 hover:text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Seus Palpites</h1>
            <p class="text-base md:text-lg text-slate-600">Aposte nos placares dos jogos</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-6 p-4 rounded-xl {% if category == 'success' %}bg-green-50 text-green-800 border-2 border-green-200{% elif category == 'error' %}bg-red-50 text-red-800 border-2 border-red-200{% else %}bg-blue-50 text-blue-800 border-2 border-blue-200{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Phase Filter -->
        <div class="mb-6">
            <label class="block text-sm font-bold text-slate-700 mb-2">Filtrar por fase ou grupo:</label>
            <select onchange="window.location.href='{{ url_for('matches') }}?phase=' + this.value"
                    class="px-4 py-2 border-2 border-slate-300 rounded-lg font-semibold focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none">
                {% for phase in phases %}
                    <option value="{{ phase.phase }}" {% if current_phase == phase.phase %}selected{% endif %}>
                        {{ phase.phase }}
                    </option>
                {% endfor %}
            </select>
        </div>

        <div class="flex flex-col md:flex-row md:items-start gap-6 md:gap-8">
            {% if group_standings %}
                <div class="md:w-5/12 lg:w-1/3">
                    {% for group_name, standings in group_standings.items()|sort %}
                        <div class="bg-white rounded-lg md:rounded-xl shadow-lg overflow-hidden">
                            <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
                                <h3 class="text-base font-black text-white">{{ group_name }}</h3>
                            </div>

                            <div class="overflow-x-auto">
                                <table class="w-full text-xs md:text-sm">
                                    <thead class="bg-slate-100 border-b-2 border-slate-200">
                                        <tr>
                                            <th class="px-2 md:px-3 py-2 text-left font-bold text-slate-700">#</th>
                                            <th class="px-2 md:px-3 py-2 text-left font-bold text-slate-700">Equipe</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">J</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">GP</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">SG</th>
                                            <th class="px-2 md:px-3 py-2 text-center font-bold text-slate-700">Pts</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-slate-200">
                                        {% for team in standings %}
                                            {% set qualifies_top = loop.index <= 2 %}
                                            {% set qualifies_third = loop.index == 3 and team.team in best_third_qualifiers %}
                                            {% set is_qualified = qualifies_top or qualifies_third %}
                                            {% set row_class = 'bg-green-50' if is_qualified else '' %}
                                            <tr class="hover:bg-slate-50 transition {{ row_class }}">
                                                <td class="px-2 md:px-3 py-2 font-bold text-slate-600">{{ loop.index }}</td>
                                                <td class="px-2 md:px-3 py-2">
                                                    <div class="flex items-center gap-1 md:gap-2">
                                                        {% set team_flag = get_flag_url(team.team) %}
                                                        {% if team_flag %}
                                                            <img src="{{ team_flag }}" alt="{{ translate_team_name(team.team) }}" class="w-4 h-3 md:w-5 md:h-4 rounded border border-slate-200 flex-shrink-0">
                                                        {% endif %}
                                                        <span class="font-semibold text-slate-800 truncate text-xs md:text-sm">{{ translate_team_name(team.team) }}</span>
                                                    </div>
                                                </td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.played }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.gf }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.gd }}</td>
                                                <td class="px-2 md:px-3 py-2 text-center text-slate-600">{{ team.points }}</td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}

            <!-- Matches Form -->
            <div class="md:flex-1">
                <form method="POST" action="{{ url_for('save_bets', phase=current_phase) }}">
                    <div class="space-y-3 md:space-y-4">
                        {% for match in fixtures %}
                            <div class="bg-white rounded-lg md:rounded-xl shadow-md p-3 md:p-5 hover:shadow-lg transition border border-slate-200 relative">
                                <!-- Stats Link -->
                                <a href="{{ url_for('match_stats', match_id=match.id) }}"
                                   class="absolute top-3 right-3 px-2 py-1 text-xs font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition border border-blue-200"
                                   title="Ver estatísticas">
                                    📊 Stats
                                </a>

                                {% set match_time = format_match_datetime(match.kickoff_utc) %}
                                {% if match_time %}
                                    <div class="text-[11px] md:text-xs text-slate-500 mb-3 font-semibold tracking-wide">
                                        {{ match_time }}
                                    </div>
                                {% endif %}

                                {% set bet = user_bets.get(match.id) %}
                                {% set points, match_type = calculate_match_points(bet.get('home_goals') if bet else None,
                                                                                  bet.get('away_goals') if bet else None,
                                                                                  match.final_home_goals, match.final_away_goals) %}

                                <div class="grid md:grid-cols-[1fr_auto] items-start gap-4 md:gap-6">
                                    <!-- Teams + Inputs -->
                                    <div class="flex-1 min-w-0">
                                        <div class="grid grid-cols-[minmax(100px,1fr)_auto_auto_auto_minmax(100px,1fr)] items-center gap-2 md:gap-3">
                                            <!-- Home team (flag + name) -->
                                            <div class="flex items-center gap-2 min-w-0 justify-end">
                                                {% set home_flag = get_flag_url(match.home) %}
                                                {% set home_abbr = get_team_abbr(match.home) %}
                                                <span class="font-bold text-sm md:text-base text-slate-900 truncate text-right hidden sm:inline">{{ translate_team_name(match.home) }}</span>
                                                <span class="font-bold text-sm md:text-base text-slate-900 truncate text-right sm:hidden">{{ home_abbr }}</span>
                                                {% if home_flag %}
                                                    <img src="{{ home_flag }}" alt="{{ translate_team_name(match.home) }}" class="w-8 h-6 rounded-md border border-slate-200 shadow-sm flex-shrink-0">
                                                {% else %}
                                                    <div class="w-8 h-6 rounded-md border border-slate-200 bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-700 flex-shrink-0">{{ home_abbr }}</div>
                                                {% endif %}
                                            </div>

                                            <!-- Home input -->
                                            <input type="number" name="h_{{ match.id }}" min="0" max="20"
                                                   value="{% if match.id in user_bets %}{{ user_bets[match.id]['home_goals'] }}{% endif %}"
                                                   class="w-12 h-12 md:w-14 md:h-14 text-center text-lg md:text-xl font-black border-2 md:border-[3px] border-blue-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none shadow-[0_2px_0_rgba(59,130,246,0.15)]"
                                                   placeholder="0">

                                            <!-- Divider -->
                                            <div class="text-lg md:text-2xl font-black text-slate-400 px-1 text-center">×</div>

                                            <!-- Away input -->
                                            <input type="number" name="a_{{ match.id }}" min="0" max="20"
                                                   value="{% if match.id in user_bets %}{{ user_bets[match.id]['away_goals'] }}{% endif %}"
                                                   class="w-12 h-12 md:w-14 md:h-14 text-center text-lg md:text-xl font-black border-2 md:border-[3px] border-blue-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none shadow-[0_2px_0_rgba(59,130,246,0.15)]"
                                                   placeholder="0">

                                            <!-- Away team (flag + name) -->
                                            <div class="flex items-center gap-2 min-w-0 justify-start">
                                                {% set away_flag = get_flag_url(match.away) %}
                                                {% set away_abbr = get_team_abbr(match.away) %}
                                                {% if away_flag %}
                                                    <img src="{{ away_flag }}" alt="{{ translate_team_name(match.away) }}" class="w-8 h-6 rounded-md border border-slate-200 shadow-sm flex-shrink-0">
                                                {% else %}
                                                    <div class="w-8 h-6 rounded-md border border-slate-200 bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-700 flex-shrink-0">{{ away_abbr }}</div>
                                                {% endif %}
                                                <span class="font-bold text-sm md:text-base text-slate-900 truncate hidden sm:inline">{{ translate_team_name(match.away) }}</span>
                                                <span class="font-bold text-sm md:text-base text-slate-900 truncate sm:hidden">{{ away_abbr }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Result & Points -->
                                    <div class="flex flex-col sm:flex-row md:flex-col lg:flex-row gap-2 md:gap-3 w-full sm:w-auto md:flex-none">
                                        <div class="flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg border border-emerald-200 bg-emerald-50 shadow-sm md:min-w-[160px]">
                                            <span class="text-[11px] md:text-xs font-black uppercase text-emerald-700 tracking-wide">Resultado</span>
                                            {% if match.final_home_goals is not none %}
                                                <span class="text-base md:text-lg font-black text-emerald-800">{{ match.final_home_goals }} × {{ match.final_away_goals }}</span>
                                            {% else %}
                                                <span class="text-[11px] font-semibold text-emerald-700">Aguardando</span>
                                            {% endif %}
                                        </div>

                                        {% set points_classes = {
                                            'exact': 'border-amber-300 bg-amber-100 text-amber-900',
                                            'partial': 'border-blue-200 bg-blue-50 text-blue-900'
                                        } %}
                                        {% set badge_class = points_classes.get(match_type, 'border-slate-200 bg-slate-50 text-slate-900') %}
                                        <div class="flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg border shadow-sm md:min-w-[160px] {{ badge_class }}">
                                            <span class="text-[11px] md:text-xs font-black uppercase tracking-wide">Pts</span>
                                            {% if match.final_home_goals is not none %}
                                                <span class="text-base md:text-lg font-black">+{{ points }} pts</span>
                                            {% else %}
                                                <span class="text-[11px] font-semibold">Em breve</span>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>

                    <div class="sticky bottom-4 md:static mt-4 md:mt-6">
                        <button type="submit"
                                class="w-full md:w-auto px-6 md:px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-200 hover:shadow-blue-300 transition">
                            Salvar Palpites
                        </button>
                    </div>
                </form>
            </div>
        </div>
</body>
</html>
'''

PALPITES_GERAIS_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extras - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-semibold text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-medium text-slate-600 hover:text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-5xl mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Extras</h1>
            <p class="text-base md:text-lg text-slate-600">Suas apostas sobre o torneio inteiro</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-6 p-4 rounded-xl {% if category == 'success' %}bg-green-50 text-green-800 border-2 border-green-200{% else %}bg-blue-50 text-blue-800 border-2 border-blue-200{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" class="space-y-5">
            <!-- Champion -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Campeão</label>
                <select name="campeao"
                        class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800 bg-white">
                    <option value="">-- Selecione --</option>
                    {% for code, name in translated_teams %}
                        <option value="{{ code }}" {% if row.get('campeao') == code %}selected{% endif %}>{{ name }}</option>
                    {% endfor %}
                </select>
            </div>

            <!-- Top Scorer -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Artilheiro</label>
                <input type="text" name="artilheiro"
                       value="{{ row.get('artilheiro', '') }}"
                       placeholder="Nome do jogador"
                       class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800">
            </div>

            <!-- Best Player -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Melhor Jogador</label>
                <input type="text" name="melhor_jogador"
                       value="{{ row.get('melhor_jogador', '') }}"
                       placeholder="Nome do jogador"
                       class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800">
            </div>

            <!-- Underdog That Went Furthest -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Zebra que vai mais longe</label>
                <select name="zebra_longe"
                        class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800 bg-white">
                    <option value="">-- Selecione --</option>
                    <option value="Haiti" {% if row.get('zebra_longe') == 'Haiti' %}selected{% endif %}>Haiti</option>
                    <option value="Curaçao" {% if row.get('zebra_longe') == 'Curaçao' %}selected{% endif %}>Curaçao</option>
                    <option value="New Zealand" {% if row.get('zebra_longe') == 'New Zealand' %}selected{% endif %}>Nova Zelândia</option>
                    <option value="Cabo Verde" {% if row.get('zebra_longe') == 'Cabo Verde' %}selected{% endif %}>Cabo Verde</option>
                    <option value="Iraq" {% if row.get('zebra_longe') == 'Iraq' %}selected{% endif %}>Iraque</option>
                    <option value="Jordan" {% if row.get('zebra_longe') == 'Jordan' %}selected{% endif %}>Jordânia</option>
                    <option value="DR Congo" {% if row.get('zebra_longe') == 'DR Congo' %}selected{% endif %}>DR Congo</option>
                    <option value="Uzbekistan" {% if row.get('zebra_longe') == 'Uzbekistan' %}selected{% endif %}>Uzbequistão</option>
                    <option value="Panama" {% if row.get('zebra_longe') == 'Panama' %}selected{% endif %}>Panamá</option>
                </select>
            </div>

            <!-- Favorite That Fell Early -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Favorito que vai cair antes</label>
                <select name="favorito_caiu"
                        class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800 bg-white">
                    <option value="">-- Selecione --</option>
                    <option value="Brazil" {% if row.get('favorito_caiu') == 'Brazil' %}selected{% endif %}>Brasil</option>
                    <option value="Argentina" {% if row.get('favorito_caiu') == 'Argentina' %}selected{% endif %}>Argentina</option>
                    <option value="Germany" {% if row.get('favorito_caiu') == 'Germany' %}selected{% endif %}>Alemanha</option>
                    <option value="Netherlands" {% if row.get('favorito_caiu') == 'Netherlands' %}selected{% endif %}>Holanda</option>
                    <option value="Spain" {% if row.get('favorito_caiu') == 'Spain' %}selected{% endif %}>Espanha</option>
                    <option value="France" {% if row.get('favorito_caiu') == 'France' %}selected{% endif %}>França</option>
                    <option value="Portugal" {% if row.get('favorito_caiu') == 'Portugal' %}selected{% endif %}>Portugal</option>
                    <option value="England" {% if row.get('favorito_caiu') == 'England' %}selected{% endif %}>Inglaterra</option>
                </select>
            </div>

            <!-- Anfitrião que vai mais longe -->
            <div class="bg-white rounded-xl shadow-md p-5 border border-slate-200">
                <label class="block text-sm font-bold text-slate-700 mb-2">Anfitrião que vai mais longe</label>
                <select name="anfitriao_longe"
                        class="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition font-semibold text-slate-800 bg-white">
                    <option value="">-- Selecione --</option>
                    <option value="USA" {% if row.get('anfitriao_longe') == 'USA' %}selected{% endif %}>Estados Unidos</option>
                    <option value="Canada" {% if row.get('anfitriao_longe') == 'Argentina' %}selected{% endif %}>Canadá</option>
                    <option value="Mexico" {% if row.get('anfitriao_longe') == 'Mexico' %}selected{% endif %}>México</option>
                </select>
            </div>

            <button type="submit"
                    class="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold text-lg rounded-xl shadow-lg shadow-blue-200 hover:from-blue-700 hover:to-blue-800 transition">
                Salvar Extras
            </button>
        </form>
    </div>
</body>
</html>
'''

JOGADOR_DETAIL_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ player.user_name }} - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-medium text-slate-600 hover:text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-medium text-slate-600 hover:text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">{{ player.user_name }}</h1>
            <p class="text-base md:text-lg text-slate-600">Total: <span class="font-bold text-blue-600">{{ total_points }} pontos</span></p>
        </div>

        <!-- Palpites Gerais -->
        {% if palpites_gerais %}
        <div class="bg-white rounded-xl shadow-lg p-4 md:p-6 mb-6 border border-slate-200">
            <h2 class="text-lg md:text-xl font-bold text-slate-800 mb-4">Palpites Gerais</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                    <p class="text-xs text-slate-500 mb-1">Campeão</p>
                    <p class="font-semibold text-slate-800">{{ translate_team_name(palpites_gerais.campeao) if palpites_gerais.campeao else '-' }}</p>
                </div>
                <div>
                    <p class="text-xs text-slate-500 mb-1">Artilheiro</p>
                    <p class="font-semibold text-slate-800">{{ palpites_gerais.artilheiro or '-' }}</p>
                </div>
                <div>
                    <p class="text-xs text-slate-500 mb-1">Melhor Jogador</p>
                    <p class="font-semibold text-slate-800">{{ palpites_gerais.melhor_jogador or '-' }}</p>
                </div>
                <div>
                    <p class="text-xs text-slate-500 mb-1">Zebra que foi mais longe</p>
                    <p class="font-semibold text-slate-800">{{ translate_team_name(palpites_gerais.zebra_longe) if palpites_gerais.zebra_longe else '-' }}</p>
                </div>
                <div>
                    <p class="text-xs text-slate-500 mb-1">Favorito que caiu antes</p>
                    <p class="font-semibold text-slate-800">{{ translate_team_name(palpites_gerais.favorito_caiu) if palpites_gerais.favorito_caiu else '-' }}</p>
                </div>
                <div>
                    <p class="text-xs text-slate-500 mb-1">Anfitrião que vai mais longe</p>
                    <p class="font-semibold text-slate-800">{{ palpites_gerais.anfitriao_longe or '-' }}</p>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Phase Filter -->
        <div class="mb-6">
            <div class="flex items-center gap-3">
                <label for="phase-filter" class="font-semibold text-slate-700">Fase:</label>
                <select id="phase-filter"
                        onchange="window.location.href='{{ url_for('jogador_detail', user_id=player.id) }}?phase=' + this.value"
                        class="px-4 py-2 rounded-lg border border-slate-300 bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {% for phase in phases %}
                        <option value="{{ phase }}" {% if phase == phase_filter %}selected{% endif %}>
                            {{ phase }}
                        </option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <!-- Bets Table -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden border border-slate-200">
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-slate-100 border-b-2 border-slate-300">
                        <tr>
                            <th class="px-3 py-3 text-left font-bold text-slate-700">Jogo</th>
                            <th class="px-3 py-3 text-center font-bold text-slate-700">Palpite</th>
                            <th class="px-3 py-3 text-center font-bold text-slate-700">Resultado</th>
                            <th class="px-3 py-3 text-center font-bold text-slate-700">Pontos</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        {% for bet in bets %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="px-3 py-3">
                                    <div class="flex items-center gap-2">
                                        <span class="font-semibold truncate">{{ translate_team_name(bet.home) }}</span>
                                        <span class="text-slate-400">×</span>
                                        <span class="font-semibold truncate">{{ translate_team_name(bet.away) }}</span>
                                    </div>
                                </td>
                                <td class="px-3 py-3 text-center">
                                    {% if bet.bet_home is not none and bet.bet_away is not none %}
                                        <span class="font-bold text-blue-600">{{ bet.bet_home }} - {{ bet.bet_away }}</span>
                                    {% else %}
                                        <span class="text-slate-400 text-xs">Sem palpite</span>
                                    {% endif %}
                                </td>
                                <td class="px-3 py-3 text-center">
                                    {% if bet.final_home_goals is not none and bet.final_away_goals is not none %}
                                        <span class="font-bold text-slate-700">{{ bet.final_home_goals }} - {{ bet.final_away_goals }}</span>
                                    {% else %}
                                        <span class="text-slate-400 text-xs">Aguardando</span>
                                    {% endif %}
                                </td>
                                <td class="px-3 py-3 text-center">
                                    {% if bet.points is not none %}
                                        <span class="inline-flex items-center justify-center px-3 py-1 rounded-full font-bold
                                            {% if bet.points == 10 %}bg-green-100 text-green-800
                                            {% elif bet.points == 5 %}bg-blue-100 text-blue-800
                                            {% else %}bg-slate-100 text-slate-600{% endif %}">
                                            +{{ bet.points }}
                                        </span>
                                    {% else %}
                                        <span class="text-slate-400 text-xs">-</span>
                                    {% endif %}
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="{{ url_for('ranking') }}" class="text-blue-600 hover:text-blue-700 font-semibold">
                ← Voltar ao Ranking
            </a>
        </div>
    </div>
</body>
</html>
'''

REGRAS_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regras - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-medium text-slate-600 hover:text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-medium text-slate-600 hover:text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-semibold text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-[1400px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <div class="mb-6 md:mb-8">
            <h1 class="text-2xl md:text-4xl font-black text-slate-800 mb-2">Regras do Bolão</h1>
            <p class="text-base md:text-lg text-slate-600">Sistema de pontuação e regras gerais</p>
        </div>

        <!-- Pontos por Fase -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6 border border-slate-200">
            <h2 class="text-xl font-bold text-slate-800 mb-4">Pontos por Fase</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm md:text-base">
                    <thead class="bg-slate-100 border-b-2 border-slate-300">
                        <tr>
                            <th class="px-4 py-3 text-left font-bold text-slate-700">Fase</th>
                            <th class="px-4 py-3 text-center font-bold text-slate-700">Pontos por jogo</th>
                            <th class="px-4 py-3 text-center font-bold text-slate-700">Total Pontos</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Grupos</td>
                            <td class="px-4 py-3 text-center">6</td>
                            <td class="px-4 py-3 text-center font-bold">432</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">16 avos</td>
                            <td class="px-4 py-3 text-center">18</td>
                            <td class="px-4 py-3 text-center font-bold">288</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Oitavas</td>
                            <td class="px-4 py-3 text-center">24</td>
                            <td class="px-4 py-3 text-center font-bold">192</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Quartas</td>
                            <td class="px-4 py-3 text-center">36</td>
                            <td class="px-4 py-3 text-center font-bold">144</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Semi</td>
                            <td class="px-4 py-3 text-center">48</td>
                            <td class="px-4 py-3 text-center font-bold">96</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Terceiro Lugar</td>
                            <td class="px-4 py-3 text-center">48</td>
                            <td class="px-4 py-3 text-center font-bold">48</td>
                        </tr>
                        <tr class="hover:bg-slate-50">
                            <td class="px-4 py-3 font-semibold">Final</td>
                            <td class="px-4 py-3 text-center">72</td>
                            <td class="px-4 py-3 text-center font-bold">72</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Regras de Pontuação -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6 border border-slate-200">
            <h2 class="text-xl font-bold text-slate-800 mb-4">Regras de Pontuação por Jogo</h2>
            <ul class="space-y-3 text-sm md:text-base">
                <li class="flex items-start">
                    <span class="font-bold text-blue-600 mr-2">•</span>
                    <span><strong>Acerto de placar exato:</strong> 100% dos pontos</span>
                </li>
                <li class="flex items-start">
                    <span class="font-bold text-blue-600 mr-2">•</span>
                    <span><strong>Acerto coluna e saldo de gols (exceto empate):</strong> 66% dos pontos</span>
                </li>
                <li class="flex items-start">
                    <span class="font-bold text-blue-600 mr-2">•</span>
                    <span><strong>Acerto coluna (empate):</strong> 50% dos pontos</span>
                </li>
                <li class="flex items-start">
                    <span class="font-bold text-blue-600 mr-2">•</span>
                    <span><strong>Acerto coluna (exceto empate):</strong> 33% dos pontos</span>
                </li>
            </ul>
        </div>

        <!-- Extras -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6 border border-slate-200">
            <h2 class="text-xl font-bold text-slate-800 mb-4">Extras</h2>

            <!-- Zebra -->
            <div class="mb-6">
                <h3 class="text-lg font-bold text-slate-700 mb-3">30 pontos: Zebra que for mais longe, opções fechadas:</h3>
                <p class="text-sm italic mb-2">Haiti, Curaçao, Nova Zelândia, Cabo Verde, Iraque, Jordânia, DR Congo, Uzbequistão, Panamá</p>
                <ul class="ml-6 space-y-2 text-sm">
                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>Se todos forem eliminados na fase de grupos, ninguém pontua.</span>
                    </li>

                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>
                            Se o último eliminado for até as oitavas de final (inclusive), vence quem apostou no time que chegou mais longe.
                            Em caso de empate (eliminação na mesma fase), o desempate será definido por:
                            (1) saldo de gols no jogo eliminatório (tempo normal) e,
                            (2) persistindo empate, pela campanha na fase de grupos.
                            Apenas um vencedor.
                        </span>
                    </li>

                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>
                            Se o último eliminado sair a partir das quartas de final (quartas, semifinal ou final),
                            todos que apostaram em times que chegaram pelo menos às quartas pontuam o total.
                        </span>
                    </li>

                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>
                            Exemplos:
                        </span>
                    </li>

                    <li class="ml-4 space-y-1 text-xs list-none">
                        <ul class="space-y-1">
                            <li>◦ Se Haiti cair nas oitavas, Cabo Verde nas quartas e os demais na fase de grupos:</li>
                            <li class="ml-6">▪ Apenas quem apostou em Cabo Verde ganha</li>

                            <li>◦ Se Haiti e Cabo Verde caírem nas quartas e os demais na fase de grupos (ou nas oitavas):</li>
                            <li class="ml-6">▪ Quem apostou em Haiti ou Cabo Verde ganha</li>

                            <li>◦ Se Haiti e Cabo Verde caírem nas oitavas, ambos eliminados nos pênaltis e os demais na fase de grupos:</li>
                            <li class="ml-6">▪ Vence quem tiver melhor campanha na fase de grupos</li>
                        </ul>
                    </li>
                </ul>            
                </div>

            <!-- Favorito -->
            <div class="mb-6">
                <h3 class="text-lg font-bold text-slate-700 mb-3">30 pontos: Favorito que cair antes, opções fechadas:</h3>
                <p class="text-sm italic mb-2">Brasil, Argentina, Alemanha, Holanda, Espanha, França, Portugal, Inglaterra</p>
                <ul class="ml-6 space-y-2 text-sm">
                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>Se todos caírem na primeira fase, ninguém pontua</span>
                    </li>
                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>Se os primeiros caírem na fase de grupos, não há desempate, todos que apostaram nesses ganham os pontos</span>
                    </li>
                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>Se os primeiros caírem nos 16 avos de final em diante, usar critério de desempate como acima</span>
                    </li>
                </ul>
            </div>

            <!-- Anfitrião -->
            <div class="mb-6">
                <h3 class="text-lg font-bold text-slate-700 mb-3">15 pontos: Anfitrião que for mais longe:</h3>
                <p class="text-sm italic mb-2">EUA, México e Canadá</p>
                <ul class="ml-6 space-y-2 text-sm">
                    <li class="flex items-start">
                        <span class="mr-2">◦</span>
                        <span>Quem chegar mais longe ganha. 
                        Em caso de empate (eliminação na mesma fase), o desempate será definido por:
                            (1) saldo de gols no jogo eliminatório (tempo normal) e,
                            (2) persistindo empate, pela campanha na fase de grupos.
                            Apenas um vencedor.
                        </span>
                    </li>
                </ul>
            </div>


            <!-- Outros Extras -->
            <div class="space-y-2 text-sm md:text-base">
                <p><strong>30 pontos: Campeão</strong></p>
                <p><strong>30 pontos: Artilheiro</strong></p>
                <p><strong>30 pontos: Melhor Jogador</strong></p>
                <p><strong>2 pontos por classificado certo na fase de grupos</strong></p>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="{{ url_for('dashboard') }}" class="text-blue-600 hover:text-blue-700 font-semibold">
                ← Voltar ao Início
            </a>
        </div>
    </div>
</body>
</html>
'''

MATCH_STATS_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estatísticas - Bolão 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        body { font-family: 'IBM Plex Mono', monospace; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-3 md:py-4">
                <div class="flex items-center space-x-3 md:space-x-6 text-sm md:text-base">
                    <a href="{{ url_for('dashboard') }}" class="font-medium text-slate-600 hover:text-blue-600">Início</a>
                    <a href="{{ url_for('matches') }}" class="font-semibold text-blue-600">Palpites</a>
                    <a href="{{ url_for('palpites_gerais') }}" class="font-medium text-slate-600 hover:text-blue-600">Extras</a>
                    <a href="{{ url_for('ranking') }}" class="font-medium text-slate-600 hover:text-blue-600">Ranking</a>
                    <a href="{{ url_for('regras') }}" class="font-medium text-slate-600 hover:text-blue-600">Regras</a>
                    <a href="{{ url_for('logout') }}" class="font-medium text-slate-600 hover:text-red-600">Sair</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 py-4 md:py-8">
        <!-- Match Header -->
        <div class="mb-6 md:mb-8">
            <div class="bg-white rounded-xl shadow-lg p-4 md:p-6 border border-slate-200">
                <p class="text-xs text-slate-500 mb-2">{{ match.phase }}</p>
                <div class="flex items-center justify-center gap-4 mb-4">
                    <div class="text-center flex-1">
                        <p class="text-lg md:text-2xl font-bold text-slate-800">{{ translate_team_name(match.home) }}</p>
                    </div>
                    <div class="text-center px-4">
                        {% if match.final_home_goals is not none %}
                            <p class="text-2xl md:text-4xl font-black text-slate-800">
                                {{ match.final_home_goals }} - {{ match.final_away_goals }}
                            </p>
                            <p class="text-xs text-slate-500 mt-1">Resultado Final</p>
                        {% else %}
                            <p class="text-xl md:text-3xl font-black text-slate-400">× - ×</p>
                            <p class="text-xs text-slate-500 mt-1">Aguardando</p>
                        {% endif %}
                    </div>
                    <div class="text-center flex-1">
                        <p class="text-lg md:text-2xl font-bold text-slate-800">{{ translate_team_name(match.away) }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Statistics Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white rounded-xl shadow-lg p-4 border border-slate-200">
                <p class="text-xs text-slate-500 mb-1">Total de Palpites</p>
                <p class="text-2xl font-bold text-slate-800">{{ stats.total_bets }}</p>
            </div>
            <div class="bg-white rounded-xl shadow-lg p-4 border border-slate-200">
                <p class="text-xs text-slate-500 mb-1">Vitória {{ translate_team_name(match.home) }}</p>
                <p class="text-2xl font-bold text-blue-600">{{ stats.home_wins }}</p>
                {% if stats.total_bets > 0 %}
                    <p class="text-xs text-slate-500 mt-1">{{ "%.1f"|format((stats.home_wins / stats.total_bets * 100)) }}%</p>
                {% endif %}
            </div>
            <div class="bg-white rounded-xl shadow-lg p-4 border border-slate-200">
                <p class="text-xs text-slate-500 mb-1">Empate</p>
                <p class="text-2xl font-bold text-slate-600">{{ stats.draws }}</p>
                {% if stats.total_bets > 0 %}
                    <p class="text-xs text-slate-500 mt-1">{{ "%.1f"|format((stats.draws / stats.total_bets * 100)) }}%</p>
                {% endif %}
            </div>
            <div class="bg-white rounded-xl shadow-lg p-4 border border-slate-200">
                <p class="text-xs text-slate-500 mb-1">Vitória {{ translate_team_name(match.away) }}</p>
                <p class="text-2xl font-bold text-green-600">{{ stats.away_wins }}</p>
                {% if stats.total_bets > 0 %}
                    <p class="text-xs text-slate-500 mt-1">{{ "%.1f"|format((stats.away_wins / stats.total_bets * 100)) }}%</p>
                {% endif %}
            </div>
        </div>

        <!-- All Bets Table -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden border border-slate-200">
            <div class="px-4 py-3 bg-slate-100 border-b border-slate-300">
                <h2 class="text-lg font-bold text-slate-800">Todos os Palpites</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th class="px-4 py-3 text-left font-bold text-slate-700">Jogador</th>
                            <th class="px-4 py-3 text-center font-bold text-slate-700">Palpite</th>
                            {% if match.final_home_goals is not none %}
                                <th class="px-4 py-3 text-center font-bold text-slate-700">Pontos</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
                        {% for bet in bets %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="px-4 py-3">
                                    <a href="{{ url_for('jogador_detail', user_id=bet.user_id) }}"
                                       class="font-semibold text-blue-600 hover:text-blue-700">
                                        {{ bet.user_name }}
                                    </a>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    {% if bet.home_goals is not none %}
                                        <span class="font-bold text-slate-700">{{ bet.home_goals }} - {{ bet.away_goals }}</span>
                                    {% else %}
                                        <span class="text-slate-400 text-xs">Sem palpite</span>
                                    {% endif %}
                                </td>
                                {% if match.final_home_goals is not none %}
                                    <td class="px-4 py-3 text-center">
                                        {% if bet.points is not none %}
                                            <span class="inline-flex items-center justify-center px-3 py-1 rounded-full font-bold
                                                {% if bet.points == 6 %}bg-green-100 text-green-800
                                                {% elif bet.points == 4 %}bg-blue-100 text-blue-800
                                                {% elif bet.points == 3 %}bg-purple-100 text-purple-800
                                                {% elif bet.points == 2 %}bg-yellow-100 text-yellow-800
                                                {% else %}bg-slate-100 text-slate-600{% endif %}">
                                                +{{ bet.points }}
                                            </span>
                                        {% elif bet.home_goals is not none %}
                                            <span class="inline-flex items-center justify-center px-3 py-1 rounded-full font-bold bg-slate-100 text-slate-600">
                                                +0
                                            </span>
                                        {% else %}
                                            <span class="text-slate-400 text-xs">-</span>
                                        {% endif %}
                                    </td>
                                {% endif %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="{{ url_for('matches') }}" class="text-blue-600 hover:text-blue-700 font-semibold">
                ← Voltar aos Palpites
            </a>
        </div>
    </div>
</body>
</html>
'''
