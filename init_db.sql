-- Schema para PostgreSQL do Bolão 2026
-- Este script cria as tabelas necessárias

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_name TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Tabela de fixtures/jogos
CREATE TABLE IF NOT EXISTS fixtures (
    id SERIAL PRIMARY KEY,
    phase TEXT NOT NULL,
    home TEXT NOT NULL,
    away TEXT NOT NULL,
    kickoff_utc TEXT,
    final_home_goals INTEGER,
    final_away_goals INTEGER
);

-- Tabela de apostas
CREATE TABLE IF NOT EXISTS bet (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    match_id INTEGER NOT NULL REFERENCES fixtures(id),
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    UNIQUE(user_id, match_id)
);

-- Tabela de palpites gerais
CREATE TABLE IF NOT EXISTS palpites_gerais (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) UNIQUE,
    campeao TEXT,
    artilheiro TEXT,
    melhor_jogador TEXT,
    zebra_longe TEXT,
    favorito_caiu TEXT,
    anfitriao_longe TEXT,
    updated_at TEXT
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_bet_user_id ON bet(user_id);
CREATE INDEX IF NOT EXISTS idx_bet_match_id ON bet(match_id);
CREATE INDEX IF NOT EXISTS idx_palpites_gerais_user_id ON palpites_gerais(user_id);
