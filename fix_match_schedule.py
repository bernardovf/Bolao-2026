#!/usr/bin/env python3
"""
Fix match schedule with proper World Cup-style spacing
Each team plays 3 matches with 4-5 days between them
"""

import sqlite3
from datetime import datetime, timedelta

def main():
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()

    print("🔄 Creating proper World Cup schedule...")
    print("=" * 70)

    # Get current fixtures
    cursor.execute("""
        SELECT id, phase, home, away
        FROM fixtures
        WHERE phase LIKE 'Group%'
        ORDER BY phase, id
    """)
    all_fixtures = cursor.fetchall()

    # Group them
    groups_data = {}
    for fix in all_fixtures:
        fix_id, phase, home, away = fix
        if phase not in groups_data:
            groups_data[phase] = []
        groups_data[phase].append({"id": fix_id, "home": home, "away": away})

    # World Cup schedule structure:
    # Matchday 1: Days 0-2 (June 11-13)
    # Matchday 2: Days 5-7 (June 16-18)
    # Matchday 3: Days 10-12 (June 21-23)

    start_date = datetime(2026, 6, 11)
    time_slots = [
        timedelta(hours=13),
        timedelta(hours=16),
        timedelta(hours=19),
        timedelta(hours=22),
    ]

    group_names = [f"Group {c}" for c in "ABCDEFGHIJKL"]

    print(f"\n📅 Updated schedule:\n")

    total_updates = 0

    for group_idx, group_name in enumerate(group_names):
        fixtures = groups_data.get(group_name, [])

        if len(fixtures) < 6:
            continue

        # Each group has 6 matches assigned to 3 matchdays
        # Matchday 1: Matches 0, 1
        # Matchday 2: Matches 2, 3
        # Matchday 3: Matches 4, 5

        matchday_info = [
            {"base_day": 0, "matches": [0, 1]},    # MD1: June 11-13
            {"base_day": 5, "matches": [2, 3]},    # MD2: June 16-18
            {"base_day": 10, "matches": [4, 5]},   # MD3: June 21-23
        ]

        for md_idx, md in enumerate(matchday_info):
            base_day = md["base_day"]
            matches = md["matches"]

            for match_offset, fixture_idx in enumerate(matches):
                fixture = fixtures[fixture_idx]

                # Distribute groups across 3 days per matchday
                # Groups A-D: Day 0, Groups E-H: Day 1, Groups I-L: Day 2
                day_in_md = group_idx // 4

                # Time slot within the day
                slot = group_idx % 4

                # For the second match of each matchday, add small offset
                # Either different time slot or next day
                if match_offset == 1:
                    # Second match: try different time or next day
                    if group_idx < 8:  # Groups A-H: same day, +3 hours
                        slot = (slot + 2) % 4  # Shift time slot
                        if slot < 2:  # If wrapped around, go to next day
                            day_in_md += 1
                            slot = group_idx % 2
                    else:  # Groups I-L: next day
                        day_in_md += 1

                final_day = base_day + day_in_md
                kickoff = start_date + timedelta(days=final_day) + time_slots[slot]

                # Update database
                cursor.execute(
                    "UPDATE fixtures SET kickoff_utc = ? WHERE id = ?",
                    (kickoff.isoformat(), fixture["id"])
                )
                total_updates += 1

                # Print first few
                if total_updates <= 15:
                    print(f"  {kickoff.strftime('%b %d, %H:%M')} - {group_name}: {fixture['home']} vs {fixture['away']}")

    conn.commit()

    print(f"\n  ... ({total_updates - 15} more matches)")

    # Verify a specific group
    print(f"\n{'=' * 70}")
    print(f"✅ Updated {total_updates} fixtures!")

    # Check Group A (Mexico)
    cursor.execute("""
        SELECT home, away, kickoff_utc
        FROM fixtures
        WHERE phase = 'Group A'
        ORDER BY datetime(kickoff_utc)
    """)

    print(f"\n🇲🇽 Group A schedule (in order):")
    for row in cursor.fetchall():
        dt = datetime.fromisoformat(row[2])
        print(f"  {dt.strftime('%b %d, %H:%M')} - {row[0]} vs {row[1]}")

    conn.close()

if __name__ == "__main__":
    main()
