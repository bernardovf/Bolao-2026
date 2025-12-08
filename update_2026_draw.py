#!/usr/bin/env python3
"""
Update database with 2026 World Cup draw results
Draw held on December 5, 2025 in Washington, DC
"""

import sqlite3
from datetime import datetime, timedelta

# 2026 World Cup groups based on official draw (December 5, 2025)
GROUPS_2026 = {
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

# Placeholder notes for playoff winners
PLAYOFF_NOTES = {
    "UEFA Playoff A": "Bosnia and Herzegovina, Italy, Northern Ireland or Wales",
    "UEFA Playoff B": "Albania, Poland, Sweden or Ukraine",
    "UEFA Playoff C": "Kosovo, Romania, Slovakia or Türkiye",
    "UEFA Playoff D": "Czechia, Denmark, North Macedonia or Republic of Ireland",
    "FIFA Playoff 1": "DR Congo, Jamaica or New Caledonia",
    "FIFA Playoff 2": "Bolivia, Iraq or Suriname",
}

def generate_group_fixtures(group_name, teams):
    """Generate all fixtures for a group (round-robin)"""
    fixtures = []
    # Each team plays every other team once
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            fixtures.append((teams[i], teams[j]))
    return fixtures

def main():
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()

    print("🔄 Updating database with 2026 World Cup draw results...")
    print("=" * 60)

    # Delete existing group stage fixtures
    cursor.execute("DELETE FROM fixtures WHERE phase LIKE 'Group%'")
    deleted_count = cursor.rowcount
    print(f"✓ Deleted {deleted_count} old group stage fixtures")

    # Also delete any bets for group stage fixtures
    cursor.execute("DELETE FROM bet WHERE match_id NOT IN (SELECT id FROM fixtures)")
    deleted_bets = cursor.rowcount
    if deleted_bets > 0:
        print(f"✓ Deleted {deleted_bets} obsolete bets")

    # Tournament starts June 11, 2026
    # We'll space out matches over the group stage (typically 2 weeks)
    start_date = datetime(2026, 6, 11, 12, 0, 0)  # June 11, 2026, 12:00 UTC

    total_fixtures = 0

    # Insert new fixtures for each group
    for group_name in sorted(GROUPS_2026.keys()):
        teams = GROUPS_2026[group_name]
        fixtures = generate_group_fixtures(group_name, teams)

        print(f"\n{group_name}:")
        for i, team in enumerate(teams, 1):
            note = f" ({PLAYOFF_NOTES[team]})" if team in PLAYOFF_NOTES else ""
            print(f"  {i}. {team}{note}")

        # Insert fixtures for this group
        for idx, (home, away) in enumerate(fixtures):
            # Spread matches across group stage
            # Typically 3 match days, with matches staggered
            match_day = idx // 2  # 2 matches per day roughly
            kickoff = start_date + timedelta(days=match_day * 3, hours=(idx % 2) * 4)
            kickoff_str = kickoff.isoformat()

            cursor.execute(
                "INSERT INTO fixtures (phase, home, away, kickoff_utc) VALUES (?, ?, ?, ?)",
                (group_name, home, away, kickoff_str)
            )
            total_fixtures += 1

    conn.commit()
    print(f"\n{'=' * 60}")
    print(f"✅ Successfully added {total_fixtures} group stage fixtures!")
    print(f"   Tournament starts: June 11, 2026")
    print(f"   Final on: July 19, 2026")
    print(f"\n📝 Note: Playoff matches will be played in March 2026")
    print(f"   Update playoff teams after March 31, 2026")

    conn.close()

if __name__ == "__main__":
    main()
