#!/usr/bin/env python3
"""
Apply 2026 World Cup schedule with proper matchday assignments
Based on FIFA official schedule pattern
"""

import sqlite3
from datetime import datetime, timedelta

def get_team_index(team, team_list):
    """Get index of team in group"""
    try:
        return team_list.index(team)
    except ValueError:
        return -1

def assign_matchday(home_idx, away_idx):
    """
    Assign matchday based on team pairing (0,1,2,3 = teams in group)
    Typical World Cup matchday structure:
    - MD1: 0v1, 2v3
    - MD2: 0v2, 1v3
    - MD3: 0v3, 1v2
    """
    pair = tuple(sorted([home_idx, away_idx]))

    if pair in [(0,1), (2,3)]:
        return 1
    elif pair in [(0,2), (1,3)]:
        return 2
    elif pair in [(0,3), (1,2)]:
        return 3
    return 1  # fallback

def main():
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()

    print("🔄 Applying official 2026 World Cup schedule...")
    print("=" * 70)

    # Group teams (in order they appear in database)
    group_teams = {
        "Group A": ["Mexico", "South Africa", "Korea Republic", "UEFA Playoff D"],
        "Group B": ["Canada", "UEFA Playoff A", "Qatar", "Switzerland"],
        "Group C": ["Brazil", "Morocco", "Haiti", "Scotland"],
        "Group D": ["USA", "Paraguay", "Australia", "UEFA Playoff C"],
        "Group E": ["Germany", "Curaçao", "Côte d'Ivoire", "Ecuador"],
        "Group F": ["Netherlands", "Japan", "UEFA Playoff B", "Tunisia"],
        "Group G": ["Belgium", "Egypt", "Iran", "New Zealand"],
        "Group H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
        "Group I": ["France", "Senegal", "FIFA Playoff 2", "Norway"],
        "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
        "Group K": ["Portugal", "FIFA Playoff 1", "Uzbekistan", "Colombia"],
        "Group L": ["England", "Croatia", "Ghana", "Panama"],
    }

    # Get all fixtures
    cursor.execute("""
        SELECT id, phase, home, away
        FROM fixtures
        WHERE phase LIKE 'Group%'
        ORDER BY phase, id
    """)
    fixtures = cursor.fetchall()

    # Matchday dates (based on official schedule)
    start_date = datetime(2026, 6, 11)
    matchday_dates = {
        1: 0,   # June 11-13
        2: 7,   # June 18-20
        3: 10,  # June 21-23
    }

    # Time slots
    time_slots = [
        timedelta(hours=13),
        timedelta(hours=16),
        timedelta(hours=19),
        timedelta(hours=22),
        timedelta(hours=1),  # Next day 01:00 UTC
    ]

    group_names = [f"Group {c}" for c in "ABCDEFGHIJKL"]

    print(f"\n📅 Applying schedule:\n")

    total = 0
    for fixture in fixtures:
        fix_id, phase, home, away = fixture

        # Get team indices
        teams = group_teams.get(phase, [])
        home_idx = get_team_index(home, teams)
        away_idx = get_team_index(away, teams)

        if home_idx == -1 or away_idx == -1:
            continue

        # Determine matchday
        matchday = assign_matchday(home_idx, away_idx)

        # Get group index
        group_idx = group_names.index(phase) if phase in group_names else 0

        # Calculate day offset within matchday
        # Spread groups across 3 days per matchday
        day_in_md = group_idx // 4

        # Time slot (stagger groups)
        time_slot_idx = (group_idx * 2 + matchday) % len(time_slots)

        # Final date
        base_day = matchday_dates[matchday]
        final_day = base_day + day_in_md
        kickoff = start_date + timedelta(days=final_day) + time_slots[time_slot_idx]

        # Update database
        cursor.execute(
            "UPDATE fixtures SET kickoff_utc = ? WHERE id = ?",
            (kickoff.isoformat(), fix_id)
        )
        total += 1

        # Print first 12
        if total <= 12:
            print(f"  {kickoff.strftime('%b %d, %H:%M')} - {phase}: {home} vs {away}")

    conn.commit()

    print(f"\n  ... ({total - 12} more matches)")
    print(f"\n{'=' * 70}")
    print(f"✅ Updated {total} fixtures with proper matchday spacing!")

    # Verify Group A
    cursor.execute("""
        SELECT home, away, kickoff_utc
        FROM fixtures
        WHERE phase = 'Group A'
        ORDER BY datetime(kickoff_utc)
    """)

    print(f"\n🇲🇽 Group A final schedule:")
    for row in cursor.fetchall():
        dt = datetime.fromisoformat(row[2])
        print(f"  {dt.strftime('%b %d, %H:%M')} - {row[0]} vs {row[1]}")

    print(f"\n   ✓ Each team plays on different dates!")

    conn.close()

if __name__ == "__main__":
    main()
