#!/usr/bin/env python3
"""
Update match schedule with realistic dates and times for 2026 World Cup
Matches spread across group stage with proper scheduling
"""

import sqlite3
from datetime import datetime, timedelta

# Match schedule: Opening ceremony June 11, group stage ends June 27
# 72 group matches over 17 days
# Typical: 4 matches per day, staggered times

def create_realistic_schedule():
    """Create realistic World Cup match schedule"""

    # Groups and their match pairs (6 matches per group)
    # Format: (home_index, away_index) - teams are 0,1,2,3 in each group
    match_pattern = [
        (0, 1),  # Match 1
        (2, 3),  # Match 2
        (0, 2),  # Match 3
        (1, 3),  # Match 4
        (0, 3),  # Match 5
        (1, 2),  # Match 6
    ]

    # Start date: June 11, 2026 (Opening match)
    start_date = datetime(2026, 6, 11, 0, 0, 0)

    # Typical match times in UTC (stadiums across USA, Mexico, Canada)
    # Morning slot: 13:00 UTC (East Coast afternoon)
    # Afternoon slot: 16:00 UTC (East Coast evening)
    # Evening slot: 19:00 UTC (West Coast afternoon)
    # Night slot: 22:00 UTC (West Coast evening)
    match_slots = [
        timedelta(hours=13),  # 13:00 UTC
        timedelta(hours=16),  # 16:00 UTC
        timedelta(hours=19),  # 19:00 UTC
        timedelta(hours=22, minutes=30),  # 22:30 UTC
    ]

    schedule = []

    # Group stage format: 3 matchdays
    # Matchday 1: Days 0-2 (June 11-13)
    # Matchday 2: Days 4-6 (June 15-17)
    # Matchday 3: Days 8-10 (June 19-21)

    matchdays = [
        {"day_offset": 0, "matches": [0, 1]},  # MD1: June 11-13
        {"day_offset": 4, "matches": [2, 3]},  # MD2: June 15-17
        {"day_offset": 8, "matches": [4, 5]},  # MD3: June 19-21
    ]

    group_names = [f"Group {c}" for c in "ABCDEFGHIJKL"]

    # Distribute matches across days
    day_counter = 0
    slot_counter = 0

    for matchday in matchdays:
        base_day = matchday["day_offset"]
        match_indices = matchday["matches"]

        # For each group's matches in this matchday
        for match_idx in match_indices:
            for group_idx, group_name in enumerate(group_names):
                # Calculate which day this match falls on
                # Spread groups across multiple days
                day_offset = base_day + (group_idx // 4)  # 4 groups per day
                slot = group_idx % 4  # 4 time slots per day

                # For matchday 3 (crucial matches), same group matches at same time
                if matchday["day_offset"] == 8:
                    # Keep match 4 and 5 in sync for each group
                    if match_idx == 5:  # Use same slot as match 4
                        slot = group_idx % 4

                match_time = start_date + timedelta(days=day_offset) + match_slots[slot]

                schedule.append({
                    "group": group_name,
                    "match_index": match_idx,
                    "home_idx": match_pattern[match_idx][0],
                    "away_idx": match_pattern[match_idx][1],
                    "kickoff": match_time
                })

    return schedule

def main():
    # Get current fixtures with team names
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()

    print("🔄 Updating match schedule with realistic dates/times...")
    print("=" * 70)

    # Get all group matches
    cursor.execute("""
        SELECT id, phase, home, away, kickoff_utc
        FROM fixtures
        WHERE phase LIKE 'Group%'
        ORDER BY phase, id
    """)

    fixtures = cursor.fetchall()

    # Group fixtures by group name
    groups_fixtures = {}
    for fix in fixtures:
        fix_id, phase, home, away, kickoff = fix
        if phase not in groups_fixtures:
            groups_fixtures[phase] = []
        groups_fixtures[phase].append({
            "id": fix_id,
            "home": home,
            "away": away,
            "kickoff": kickoff
        })

    # Create schedule
    schedule = create_realistic_schedule()

    # Update each fixture with new kickoff time
    updates = 0

    # Sort schedule by kickoff time
    schedule.sort(key=lambda x: (x["kickoff"], x["group"]))

    print(f"\n📅 First 10 matches:")
    for i, entry in enumerate(schedule):
        group_fixtures = groups_fixtures[entry["group"]]
        if entry["match_index"] < len(group_fixtures):
            fixture = group_fixtures[entry["match_index"]]
            new_kickoff = entry["kickoff"].isoformat()

            cursor.execute(
                "UPDATE fixtures SET kickoff_utc = ? WHERE id = ?",
                (new_kickoff, fixture["id"])
            )
            updates += 1

            if i < 10:
                print(f"  {entry['kickoff'].strftime('%b %d, %H:%M')}: {entry['group']} - {fixture['home']} vs {fixture['away']}")

    if len(schedule) > 10:
        print(f"\n  ... ({len(schedule) - 10} more matches)")

    conn.commit()

    print(f"\n{'=' * 70}")
    print(f"✅ Updated {updates} fixtures with realistic schedule!")
    print(f"   Group Stage: June 11-21, 2026")
    print(f"   Matches ordered by date/time")

    # Show distribution
    print(f"\n📊 Match distribution:")
    dates = {}
    for entry in schedule:
        date_key = entry["kickoff"].strftime('%b %d')
        dates[date_key] = dates.get(date_key, 0) + 1

    for date in sorted(dates.keys(), key=lambda x: datetime.strptime(x, '%b %d')):
        print(f"   {date}: {dates[date]} matches")

    conn.close()

if __name__ == "__main__":
    main()
