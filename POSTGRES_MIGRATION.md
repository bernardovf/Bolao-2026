# 🐘 Migração para PostgreSQL - Completa!

## ✅ Mudanças Realizadas:

### 1. **requirements.txt**
- ✅ Adicionado `psycopg2-binary==2.9.9`

### 2. **app_v2.py**
- ✅ Suporte para PostgreSQL e SQLite
- ✅ Detecta automaticamente qual banco usar
- ✅ PostgreSQL em produção (Render)
- ✅ SQLite em desenvolvimento local

### 3. **render.yaml**
- ✅ Configurado banco PostgreSQL gratuito
- ✅ DATABASE_URL configurada automaticamente

### 4. **init_db.sql**
- ✅ Script para criar schema do PostgreSQL

## 🚀 Próximos Passos:

### Passo 1: Fazer Commit e Push
```bash
git add requirements.txt app_v2.py render.yaml init_db.sql POSTGRES_MIGRATION.md
git commit -m "Migrate to PostgreSQL"
git push origin claude/align-widen-country-form-AdDQn
```

### Passo 2: No Render Dashboard

#### A. O Render vai detectar o render.yaml e perguntar:
- "Create PostgreSQL database?"
- Clique **YES** ou **Create Database**

#### B. Ou crie manualmente:
1. Dashboard → **"New +"** → **"PostgreSQL"**
2. Name: `bolao-2026-db`
3. Database: `bolao_2026`
4. User: `bolao_user`
5. Region: Mesma do Web Service
6. Plan: **Free**
7. Clique **"Create Database"**

### Passo 3: Conectar Database ao Web Service

1. Vá no Web Service **"bolao-2026"**
2. **Environment** → **Add Environment Variable**
3. Key: `DATABASE_URL`
4. Value: Clique em "From Database"
5. Selecione: `bolao-2026-db`
6. Property: `Internal Database URL` ou `Connection String`
7. **Save**

### Passo 4: Inicializar o Schema

#### Opção A: Via Render Shell (Recomendado)
1. Database Dashboard → **Shell**
2. Cole o conteúdo de `init_db.sql`
3. Execute

#### Opção B: Via psql local
```bash
# Copie a External Database URL do Render
psql "sua-database-url-aqui" < init_db.sql
```

### Passo 5: Deploy
- O Render vai fazer deploy automaticamente
- Aguarde 3-5 minutos

## ✅ Como Verificar:

### 1. Logs do Render
Deve aparecer:
```
Successfully connected to PostgreSQL
```

### 2. Teste o App
- Cadastre um usuário
- Faça um palpite
- Faça um novo deploy (git push)
- **Os dados devem persistir!** 🎉

## 🔄 Migrar Dados Existentes (se tiver)

Se você já tem dados no SQLite do Render e quer migrar:

### Via Render Shell:
```bash
# No Web Service Shell
sqlite3 bolao_2026_dev.db .dump > backup.sql

# Edite backup.sql para converter SQLite → PostgreSQL
# (troque AUTOINCREMENT por SERIAL, etc)

# No PostgreSQL Shell
psql $DATABASE_URL < backup_convertido.sql
```

## ⚠️ Troubleshooting

### Erro: "relation users does not exist"
→ Você não executou o `init_db.sql`
→ Rode o script no PostgreSQL Shell

### Erro: "could not connect to database"
→ DATABASE_URL não está configurada
→ Vá em Environment e adicione a variável

### App ainda usa SQLite
→ Verifique se DATABASE_URL existe: `echo $DATABASE_URL`
→ Deve começar com `postgres://` ou `postgresql://`

## 🎯 Resultado Final:

- ✅ PostgreSQL grátis no Render
- ✅ Dados persistem entre deploys
- ✅ Desenvolvimento local continua com SQLite
- ✅ Produção usa PostgreSQL automaticamente
- ✅ Zero custo adicional

---

**Pronto para produção!** 🚀
