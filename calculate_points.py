"""
Points calculation for Bolão 2026
"""

def get_phase_multiplier(phase):
    """
    Get points multiplier based on phase.
    Base points (Grupos) = 6, 4, 3, 2
    """
    if not phase:
        return 1

    phase_lower = phase.lower()

    if 'grupo' in phase_lower:
        return 1  # Grupos: 6, 4, 3, 2
    elif '16 avos' in phase_lower or '16avos' in phase_lower:
        return 3  # 16 avos: 18, 12, 9, 6
    elif 'oitavas' in phase_lower:
        return 4  # Oitavas: 24, 16, 12, 8
    elif 'quartas' in phase_lower:
        return 6  # Quartas: 36, 24, 18, 12
    elif 'semifinal' in phase_lower:
        return 8  # Semi: 48, 32, 24, 16
    elif 'terceiro' in phase_lower or '3o' in phase_lower:
        return 8  # Terceiro Lugar: 48, 32, 24, 16
    elif 'final' in phase_lower:
        return 12  # Final: 72, 48, 36, 24

    return 1  # Default to grupo multiplier

def calculate_match_points(bet_home, bet_away, final_home, final_away, phase=None):
    """
    Calculate points for a match bet.

    Args:
        bet_home: User's predicted home goals
        bet_away: User's predicted away goals
        final_home: Actual home goals
        final_away: Actual away goals
        phase: Match phase (e.g., "Grupo A", "16 Avos Final", "Oitavas", etc.)

    Returns:
        tuple: (points, match_type)
    """
    # Check for None or string 'NULL'
    if (bet_home is None or bet_away is None or final_home is None or final_away is None or
        bet_home == 'NULL' or bet_away == 'NULL' or final_home == 'NULL' or final_away == 'NULL'):
        return 0, 'none'

    # Convert to int in case SQLite returns strings
    bet_home = int(bet_home)
    bet_away = int(bet_away)
    final_home = int(final_home)
    final_away = int(final_away)

    # Get phase multiplier
    multiplier = get_phase_multiplier(phase)

    # Calculate base points
    if bet_home == final_home and bet_away == final_away:
        return 6 * multiplier, 'exact'

    bet_diff = bet_home - bet_away
    final_diff = final_home - final_away

    if (bet_diff == 0 and final_diff == 0):
        return 3 * multiplier, 'draw'

    if bet_diff == final_diff:
        return 4 * multiplier, 'saldo'

    if (bet_diff > 0 and final_diff > 0) or (bet_diff < 0 and final_diff < 0):
        return 2 * multiplier, 'partial'

    # Wrong: 0 points
    return 0, 'miss'
