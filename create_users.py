#!/usr/bin/env python3
"""
Criar usuários iniciais
Uso: python create_users.py
"""

import psycopg2
import sqlite3
import os

# DATABASE_URL do Render ou local
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # SQLite local
    conn = sqlite3.connect('bolao_2026_dev.db')
    cursor = conn.cursor()
    print("📍 Usando SQLite local")
    placeholder = "?"
else:
    # PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("📍 Usando PostgreSQL")
    placeholder = "%s"

# Usuários para criar
# FORMATO: (user_name, password)
usuarios = [
    ('Bernardo', 'senha123'),
    ('João', 'senha123'),
    ('Maria', 'senha123'),
    ('Pedro', 'senha123'),
    # Adicione mais usuários aqui
]

print(f"\n👥 Criando {len(usuarios)} usuários...")

for user_name, password in usuarios:
    try:
        query = f"INSERT INTO users (user_name, password) VALUES ({placeholder}, {placeholder})"
        cursor.execute(query, (user_name, password))
        print(f"   ✅ {user_name}")
    except Exception as e:
        print(f"   ⚠️  {user_name} - Erro: {e}")

conn.commit()

# Criar palpites_gerais vazios para cada usuário
print("\n📋 Criando registros de palpites_gerais...")
cursor.execute("SELECT id FROM users")
users = cursor.fetchall()

for user in users:
    user_id = user[0]
    try:
        query = f"INSERT INTO palpites_gerais (user_id) VALUES ({placeholder}) ON CONFLICT DO NOTHING"
        cursor.execute(query, (user_id,))
    except:
        pass  # Pode já existir

conn.commit()

# Mostrar resultado
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"\n✅ Total de usuários: {count}")

cursor.execute("SELECT user_name FROM users")
print("\n👥 Usuários cadastrados:")
for row in cursor.fetchall():
    if DATABASE_URL:
        print(f"   - {row[0]}")
    else:
        print(f"   - {row['user_name']}")

conn.close()
print("\n✅ Pronto! Os usuários podem fazer login agora.")
print("🔐 Senha padrão: senha123")
