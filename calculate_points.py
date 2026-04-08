"""
Points calculation for Bolão 2026
"""

def calculate_match_points(bet_home, bet_away, final_home, final_away):

    if bet_home is None or bet_away is None or final_home is None or final_away is None:
        return 0, 'none'

    if bet_home == final_home and bet_away == final_away:
        return 6, 'exact'

    bet_diff = bet_home - bet_away
    final_diff = final_home - final_away

    if (bet_diff == 0 and final_diff == 0):
        return 3, 'draw'

    if bet_diff == final_diff:
        return 4, 'saldo'

    if (bet_diff > 0 and final_diff > 0) or (bet_diff < 0 and final_diff < 0):
        return 2, 'partial'

    # Wrong: 0 points
    return 0, 'miss'
