"""
Points calculation for Bolão 2026
"""

def calculate_match_points(bet_home, bet_away, final_home, final_away):
    """
    Calculate points for a single match

    Args:
        bet_home: User's bet for home team goals
        bet_away: User's bet for away team goals
        final_home: Actual home team goals
        final_away: Actual away team goals

    Returns:
        tuple: (points, match_type)
            - points (int): Points earned (10, 5, or 0)
            - match_type (str): 'exact', 'partial', 'miss', or 'none'
    """
    if bet_home is None or bet_away is None or final_home is None or final_away is None:
        return 0, 'none'

    # Exact match: 10 points
    if bet_home == final_home and bet_away == final_away:
        return 10, 'exact'

    # Correct winner/draw: 5 points
    bet_diff = bet_home - bet_away
    final_diff = final_home - final_away

    # Same sign (both positive, both negative, or both zero) means correct winner/draw
    if (bet_diff > 0 and final_diff > 0) or (bet_diff < 0 and final_diff < 0) or (bet_diff == 0 and final_diff == 0):
        return 5, 'partial'

    # Wrong: 0 points
    return 0, 'miss'
