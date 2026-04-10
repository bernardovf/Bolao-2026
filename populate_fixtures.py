#!/usr/bin/env python3
"""
Popular fixtures (jogos) da Copa 2026
Uso: python populate_fixtures.py
"""

import psycopg2
import os

# DATABASE_URL do Render ou local
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Fallback para SQLite local
    import sqlite3
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()
    print("📍 Usando SQLite local")
else:
    # PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("📍 Usando PostgreSQL")

# Limpar fixtures existentes (opcional)
cursor.execute("DELETE FROM fixtures")
print("🗑️  Fixtures antigas removidas")

# Fixtures da Copa 2026 - EXEMPLO
# Você precisa preencher com os jogos reais!
fixtures = [
    # Grupo A
    ('Grupo A', 'Mexico', 'Jamaica', '2026-06-11T19:00:00Z'),
    ('Grupo A', 'USA', 'Canada', '2026-06-12T19:00:00Z'),
    ('Grupo A', 'Canada', 'Jamaica', '2026-06-15T19:00:00Z'),
    ('Grupo A', 'USA', 'Mexico', '2026-06-16T19:00:00Z'),
    ('Grupo A', 'Jamaica', 'USA', '2026-06-19T19:00:00Z'),
    ('Grupo A', 'Canada', 'Mexico', '2026-06-19T19:00:00Z'),

    # Grupo B
    ('Grupo B', 'England', 'Iran', '2026-06-12T16:00:00Z'),
    ('Grupo B', 'USA', 'Wales', '2026-06-12T19:00:00Z'),
    # ... adicione mais grupos aqui

    # Oitavas de Final (placeholders)
    ('Oitavas', 'TBD', 'TBD', '2026-07-01T19:00:00Z'),
    ('Oitavas', 'TBD', 'TBD', '2026-07-02T19:00:00Z'),
    # ... adicione todas as fases
]

# Inserir fixtures
if DATABASE_URL:
    # PostgreSQL
    cursor.executemany(
        "INSERT INTO fixtures (phase, home, away, kickoff_utc) VALUES (%s, %s, %s, %s)",
        fixtures
    )
else:
    # SQLite
    cursor.executemany(
        "INSERT INTO fixtures (phase, home, away, kickoff_utc) VALUES (?, ?, ?, ?)",
        fixtures
    )

conn.commit()
print(f"✅ {len(fixtures)} jogos inseridos!")

# Verificar
cursor.execute("SELECT COUNT(*) FROM fixtures")
count = cursor.fetchone()[0]
print(f"📊 Total de jogos no banco: {count}")

# Mostrar alguns jogos
cursor.execute("SELECT phase, home, away FROM fixtures LIMIT 5")
print("\n🎮 Primeiros jogos:")
for row in cursor.fetchall():
    if DATABASE_URL:
        print(f"   {row[0]}: {row[1]} × {row[2]}")
    else:
        print(f"   {row['phase']}: {row['home']} × {row['away']}")

conn.close()
print("\n✅ Pronto!")
