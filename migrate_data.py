#!/usr/bin/env python3
"""
Script de migração SQLite → PostgreSQL
Uso: python migrate_data.py
"""

import sqlite3
import psycopg2
import os
import sys

# Configuração
SQLITE_DB = 'bolao_2026_dev.db'
POSTGRES_URL = os.environ.get('DATABASE_URL')

if not POSTGRES_URL:
    print("❌ Erro: DATABASE_URL não encontrada!")
    print("Configure: export DATABASE_URL='sua-url-postgresql'")
    sys.exit(1)

# Fix Render postgres:// → postgresql://
if POSTGRES_URL.startswith('postgres://'):
    POSTGRES_URL = POSTGRES_URL.replace('postgres://', 'postgresql://', 1)

print("🔄 Iniciando migração SQLite → PostgreSQL...")

# Conectar aos bancos
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
pg_conn = psycopg2.connect(POSTGRES_URL)
pg_cursor = pg_conn.cursor()

# Migrar tabelas
tables = ['users', 'fixtures', 'bet', 'palpites_gerais']

for table in tables:
    print(f"\n📊 Migrando tabela: {table}")

    # Ler do SQLite
    sqlite_cursor = sqlite_conn.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  ⚠️  Tabela {table} vazia, pulando...")
        continue

    # Obter nomes das colunas
    columns = [description[0] for description in sqlite_cursor.description]
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))

    # Inserir no PostgreSQL
    count = 0
    for row in rows:
        try:
            values = tuple(row)
            pg_cursor.execute(
                f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                values
            )
            count += 1
        except Exception as e:
            print(f"  ⚠️  Erro ao inserir linha: {e}")
            continue

    print(f"  ✅ {count} registros migrados")

# Commit e fechar
pg_conn.commit()
pg_cursor.close()
pg_conn.close()
sqlite_conn.close()

print("\n✅ Migração completa!")
print("\n🔍 Verificar dados:")
print("   SELECT COUNT(*) FROM users;")
print("   SELECT COUNT(*) FROM bet;")
print("   SELECT COUNT(*) FROM palpites_gerais;")
