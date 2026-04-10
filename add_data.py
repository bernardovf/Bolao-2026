import sqlite3
from faker import Faker
import unicodedata

fake = Faker('pt_BR')

def random_simple_name():
    # Generate a full name
    name = fake.name()

    # Remove prefixes like "Sr.", "Sra.", etc.
    for prefix in ["Sr.", "Sra.", "Dr.", "Dra."]:
        name = name.replace(prefix, "").strip()

    # Normalize (remove accents)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()

    # Keep only two words (first + last)
    parts = name.split()
    if len(parts) >= 2:
        name = f"{parts[0]} {parts[-1]}"
    else:
        name = parts[0]

    return name


DB_PATH = "bolao_2026_dev.db"   # adjust path if needed
conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()
cur.execute("""
INSERT INTO "bet" (id, user_id, match_id, home_goals, away_goals)
SELECT
  NULL,                      -- let SQLite generate the id
  u.id,
  f.id,
  abs(random()) % 4,
  abs(random()) % 4
FROM "users" AS u
CROSS JOIN "fixtures" AS f
WHERE u.id BETWEEN 1 AND 39
  AND f.id BETWEEN 1 AND 72;    """)
conn.commit()
conn.close()


exit()
rows = []
for i in range(3, 40):
    name = random_simple_name()
    rows.append((name, '1234', i))

with sqlite3.connect(DB_PATH) as con:
    cur = con.cursor()
    cur.executemany("""
        INSERT INTO users (user_name, password, id)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          user_name=excluded.user_name,
          password=excluded.password,
          id=excluded.id;
    """, rows)
    con.commit()


exit()


rows = [
    # id, phase, home, away, kickoff_utc
    (1,  "Group A","Qatar","Ecuador","2022-11-20T12:00:00Z"),
    (2,  "Group A","Senegal","Netherlands","2022-11-20T15:00:00Z"),
    (3,  "Group A","Qatar","Senegal","2022-11-20T18:00:00Z"),
    (4,  "Group A","Netherlands","Ecuador","2022-11-20T21:00:00Z"),
    (5,  "Group A","Netherlands","Qatar","2022-11-21T12:00:00Z"),
    (6,  "Group A","Ecuador","Senegal","2022-11-21T15:00:00Z"),

    (7,  "Group B","England","Iran","2022-11-21T18:00:00Z"),
    (8,  "Group B","USA","Wales","2022-11-21T21:00:00Z"),
    (9,  "Group B","Wales","Iran","2022-11-22T12:00:00Z"),
    (10, "Group B","England","USA","2022-11-22T15:00:00Z"),
    (11, "Group B","Wales","England","2022-11-22T18:00:00Z"),
    (12, "Group B","Iran","USA","2022-11-22T21:00:00Z"),

    (13, "Group C","Argentina","Saudi Arabia","2022-11-23T12:00:00Z"),
    (14, "Group C","Mexico","Poland","2022-11-23T15:00:00Z"),
    (15, "Group C","Poland","Saudi Arabia","2022-11-23T18:00:00Z"),
    (16, "Group C","Argentina","Mexico","2022-11-23T21:00:00Z"),
    (17, "Group C","Poland","Argentina","2022-11-24T12:00:00Z"),
    (18, "Group C","Saudi Arabia","Mexico","2022-11-24T15:00:00Z"),

    (19, "Group D","Denmark","Tunisia","2022-11-24T18:00:00Z"),
    (20, "Group D","France","Australia","2022-11-24T21:00:00Z"),
    (21, "Group D","Tunisia","Australia","2022-11-25T12:00:00Z"),
    (22, "Group D","France","Denmark","2022-11-25T15:00:00Z"),
    (23, "Group D","Australia","Denmark","2022-11-25T18:00:00Z"),
    (24, "Group D","Tunisia","France","2022-11-25T21:00:00Z"),

    (25, "Group E","Germany","Japan","2022-11-26T12:00:00Z"),
    (26, "Group E","Spain","Costa Rica","2022-11-26T15:00:00Z"),
    (27, "Group E","Japan","Costa Rica","2022-11-26T18:00:00Z"),
    (28, "Group E","Spain","Germany","2022-11-26T21:00:00Z"),
    (29, "Group E","Japan","Spain","2022-11-27T12:00:00Z"),
    (30, "Group E","Costa Rica","Germany","2022-11-27T15:00:00Z"),

    (31, "Group F","Morocco","Croatia","2022-11-27T18:00:00Z"),
    (32, "Group F","Belgium","Canada","2022-11-27T21:00:00Z"),
    (33, "Group F","Belgium","Morocco","2022-11-28T12:00:00Z"),
    (34, "Group F","Croatia","Canada","2022-11-28T15:00:00Z"),
    (35, "Group F","Croatia","Belgium","2022-11-28T18:00:00Z"),
    (36, "Group F","Canada","Morocco","2022-11-28T21:00:00Z"),

    (37, "Group G","Switzerland","Cameroon","2022-11-29T12:00:00Z"),
    (38, "Group G","Brazil","Serbia","2022-11-29T15:00:00Z"),
    (39, "Group G","Cameroon","Serbia","2022-11-29T18:00:00Z"),
    (40, "Group G","Brazil","Switzerland","2022-11-29T21:00:00Z"),
    (41, "Group G","Serbia","Switzerland","2022-11-30T12:00:00Z"),
    (42, "Group G","Cameroon","Brazil","2022-11-30T15:00:00Z"),

    (43, "Group H","Uruguay","South Korea","2022-11-30T18:00:00Z"),
    (44, "Group H","Portugal","Ghana","2022-11-30T21:00:00Z"),
    (45, "Group H","South Korea","Ghana","2022-12-01T12:00:00Z"),
    (46, "Group H","Portugal","Uruguay","2022-12-01T15:00:00Z"),
    (47, "Group H","South Korea","Portugal","2022-12-01T18:00:00Z"),
    (48, "Group H","Ghana","Uruguay","2022-12-01T21:00:00Z"),

    (49, "Round of 32", "Netherlands", "USA", "2022-12-03T15:00:00Z"),
    (50, "Round of 32", "Argentina", "Australia", "2022-12-03T19:00:00Z"),
    (51, "Round of 32", "France", "Poland", "2022-12-04T15:00:00Z"),
    (52, "Round of 32", "England", "Senegal", "2022-12-04T19:00:00Z"),
    (53, "Round of 32", "Japan", "Croatia", "2022-12-05T15:00:00Z"),
    (54, "Round of 32", "Brazil", "South Korea", "2022-12-05T19:00:00Z"),
    (55, "Round of 32", "Morocco", "Spain", "2022-12-06T15:00:00Z"),
    (56, "Round of 32", "Portugal", "Switzerland", "2022-12-06T19:00:00Z"),
    (57, "Round of 32", "Netherlands", "USA", "2022-12-03T15:00:00Z"),
    (58, "Round of 32", "Argentina", "Australia", "2022-12-03T19:00:00Z"),
    (59, "Round of 32", "France", "Poland", "2022-12-04T15:00:00Z"),
    (60, "Round of 32", "England", "Senegal", "2022-12-04T19:00:00Z"),
    (61, "Round of 32", "Japan", "Croatia", "2022-12-05T15:00:00Z"),
    (62, "Round of 32", "Brazil", "South Korea", "2022-12-05T19:00:00Z"),
    (63, "Round of 32", "Morocco", "Spain", "2022-12-06T15:00:00Z"),
    (64, "Round of 32", "Portugal", "Switzerland", "2022-12-06T19:00:00Z"),

    (65, "Round of 16","Netherlands","USA",          "2022-12-03T15:00:00Z"),
    (66, "Round of 16","Argentina","Australia",      "2022-12-03T19:00:00Z"),
    (67, "Round of 16","France","Poland",            "2022-12-04T15:00:00Z"),
    (68, "Round of 16","England","Senegal",          "2022-12-04T19:00:00Z"),
    (69, "Round of 16","Japan","Croatia",            "2022-12-05T15:00:00Z"),
    (70, "Round of 16","Brazil","South Korea",       "2022-12-05T19:00:00Z"),
    (71, "Round of 16","Morocco","Spain",            "2022-12-06T15:00:00Z"),
    (72, "Round of 16","Portugal","Switzerland",     "2022-12-06T19:00:00Z"),

    (73, "Quarterfinals","Croatia","Brazil",         "2022-12-09T15:00:00Z"),
    (74, "Quarterfinals","Netherlands","Argentina",  "2022-12-09T19:00:00Z"),
    (75, "Quarterfinals","Morocco","Portugal",       "2022-12-10T15:00:00Z"),
    (76, "Quarterfinals","England","France",         "2022-12-10T19:00:00Z"),

    (77, "Semifinals","Argentina","Croatia",         "2022-12-13T19:00:00Z"),
    (78, "Semifinals","France","Morocco",            "2022-12-14T19:00:00Z"),

    (79, "Third Place","Croatia","Morocco",          "2022-12-17T15:00:00Z"),
    (80, "Final","Argentina","France",               "2022-12-18T15:00:00Z"),
]

rows = [(49, "Group I","Germany","Japan","2022-11-26T12:00:00Z"),
    (50, "Group I","Spain","Costa Rica","2022-11-26T15:00:00Z"),
    (51, "Group I","Japan","Costa Rica","2022-11-26T18:00:00Z"),
    (52, "Group I","Spain","Germany","2022-11-26T21:00:00Z"),
    (53, "Group I","Japan","Spain","2022-11-27T12:00:00Z"),
    (54, "Group I","Costa Rica","Germany","2022-11-27T15:00:00Z"),

    (55, "Group J","Morocco","Croatia","2022-11-27T18:00:00Z"),
    (56, "Group J","Belgium","Canada","2022-11-27T21:00:00Z"),
    (57, "Group J","Belgium","Morocco","2022-11-28T12:00:00Z"),
    (58, "Group J","Croatia","Canada","2022-11-28T15:00:00Z"),
    (59, "Group J","Croatia","Belgium","2022-11-28T18:00:00Z"),
    (60, "Group J","Canada","Morocco","2022-11-28T21:00:00Z"),

    (61, "Group K","Switzerland","Cameroon","2022-11-29T12:00:00Z"),
    (62, "Group K","Brazil","Serbia","2022-11-29T15:00:00Z"),
    (63, "Group K","Cameroon","Serbia","2022-11-29T18:00:00Z"),
    (64, "Group K","Brazil","Switzerland","2022-11-29T21:00:00Z"),
    (65, "Group K","Serbia","Switzerland","2022-11-30T12:00:00Z"),
    (66, "Group K","Cameroon","Brazil","2022-11-30T15:00:00Z"),

    (67, "Group L","Uruguay","South Korea","2022-11-30T18:00:00Z"),
    (68, "Group L","Portugal","Ghana","2022-11-30T21:00:00Z"),
    (69, "Group L","South Korea","Ghana","2022-12-01T12:00:00Z"),
    (70, "Group L","Portugal","Uruguay","2022-12-01T15:00:00Z"),
    (71, "Group L","South Korea","Portugal","2022-12-01T18:00:00Z"),
    (72, "Group L","Ghana","Uruguay","2022-12-01T21:00:00Z"),

    (73, "Round of 32", "Netherlands", "USA", "2022-12-03T15:00:00Z"),
    (74, "Round of 32", "Argentina", "Australia", "2022-12-03T19:00:00Z"),
    (75, "Round of 32", "France", "Poland", "2022-12-04T15:00:00Z"),
    (76, "Round of 32", "England", "Senegal", "2022-12-04T19:00:00Z"),
    (77, "Round of 32", "Japan", "Croatia", "2022-12-05T15:00:00Z"),
    (78, "Round of 32", "Brazil", "South Korea", "2022-12-05T19:00:00Z"),
    (79, "Round of 32", "Morocco", "Spain", "2022-12-06T15:00:00Z"),
    (80, "Round of 32", "Portugal", "Switzerland", "2022-12-06T19:00:00Z"),
    (81, "Round of 32", "Netherlands", "USA", "2022-12-03T15:00:00Z"),
    (82, "Round of 32", "Argentina", "Australia", "2022-12-03T19:00:00Z"),
    (83, "Round of 32", "France", "Poland", "2022-12-04T15:00:00Z"),
    (84, "Round of 32", "England", "Senegal", "2022-12-04T19:00:00Z"),
    (85, "Round of 32", "Japan", "Croatia", "2022-12-05T15:00:00Z"),
    (86, "Round of 32", "Brazil", "South Korea", "2022-12-05T19:00:00Z"),
    (87, "Round of 32", "Morocco", "Spain", "2022-12-06T15:00:00Z"),
    (88, "Round of 32", "Portugal", "Switzerland", "2022-12-06T19:00:00Z"),

    (89, "Round of 16", "Netherlands", "USA", "2022-12-03T15:00:00Z"),
    (90, "Round of 16", "Argentina", "Australia", "2022-12-03T19:00:00Z"),
    (91, "Round of 16", "France", "Poland", "2022-12-04T15:00:00Z"),
    (92, "Round of 16", "England", "Senegal", "2022-12-04T19:00:00Z"),
    (93, "Round of 16", "Japan", "Croatia", "2022-12-05T15:00:00Z"),
    (94, "Round of 16", "Brazil", "South Korea", "2022-12-05T19:00:00Z"),
    (95, "Round of 16", "Morocco", "Spain", "2022-12-06T15:00:00Z"),
    (96, "Round of 16", "Portugal", "Switzerland", "2022-12-06T19:00:00Z"),

    (97, "Quarterfinals", "Croatia", "Brazil", "2022-12-09T15:00:00Z"),
    (98, "Quarterfinals", "Netherlands", "Argentina", "2022-12-09T19:00:00Z"),
    (99, "Quarterfinals", "Morocco", "Portugal", "2022-12-10T15:00:00Z"),
    (100, "Quarterfinals", "England", "France", "2022-12-10T19:00:00Z"),

    (101, "Semifinals", "Argentina", "Croatia", "2022-12-13T19:00:00Z"),
    (102, "Semifinals", "France", "Morocco", "2022-12-14T19:00:00Z"),

    (103, "Third Place", "Croatia", "Morocco", "2022-12-17T15:00:00Z"),
    (104, "Final", "Argentina", "France", "2022-12-18T15:00:00Z"),

    ]

rows = [
    # id, phase, home, away, kickoff_utc
    ('bernardo',  "Group A","Qatar","Ecuador","2022-11-20T12:00:00Z"),
    (2,  "Group A","Senegal","Netherlands","2022-11-20T15:00:00Z"),
    (3,  "Group A","Qatar","Senegal","2022-11-20T18:00:00Z"),
    (4,  "Group A","Netherlands","Ecuador","2022-11-20T21:00:00Z")]

with sqlite3.connect(DB_PATH) as con:
    cur = con.cursor()
    cur.executemany("""
        INSERT INTO fixtures (id, phase, home, away, kickoff_utc)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          phase=excluded.phase,
          home=excluded.home,
          away=excluded.away,
          kickoff_utc=excluded.kickoff_utc;
    """, rows)
    con.commit()

print("Knockout fixtures inserted/updated with ids 49–64.")


