# 🚀 Guia de Deploy no Render.com

## Passo a Passo

### 1. Preparar o Repositório

Os arquivos já estão prontos:
- ✅ `requirements.txt` - Dependências Python
- ✅ `render.yaml` - Configuração do Render
- ✅ `.env.example` - Exemplo de variáveis de ambiente

### 2. Fazer Push para o GitHub

```bash
git add requirements.txt render.yaml .env.example DEPLOY.md
git commit -m "Add Render deployment configuration"
git push origin claude/align-widen-country-form-AdDQn
```

### 3. Criar Conta no Render

1. Acesse: https://render.com
2. Clique em "Get Started"
3. Conecte sua conta do GitHub

### 4. Criar Novo Web Service

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório do GitHub (bernardovf/Bolao-2026)
3. Selecione a branch: `claude/align-widen-country-form-AdDQn`
4. O Render vai detectar automaticamente o `render.yaml`

### 5. Configurações Automáticas

O `render.yaml` já configura:
- ✅ Nome do serviço: `bolao-2026`
- ✅ Ambiente: Python
- ✅ Build Command: `pip install -r requirements.txt`
- ✅ Start Command: `gunicorn app_v2:app --bind 0.0.0.0:$PORT`
- ✅ SECRET_KEY: Gerada automaticamente

### 6. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (2-3 minutos)
3. Seu app estará disponível em: `https://bolao-2026.onrender.com`

## ⚠️ IMPORTANTE: Banco de Dados

### Problema do SQLite no Render

O Render usa **sistema de arquivos efêmero** no tier gratuito, o que significa:
- ❌ O banco de dados SQLite será **apagado** a cada novo deploy
- ❌ Após 15 minutos de inatividade, o serviço "dorme" e pode perder dados

### Soluções:

#### Opção 1: Migrar para PostgreSQL (Recomendado para produção)
```bash
# Adicionar ao requirements.txt:
psycopg2-binary

# Modificar app_v2.py para usar PostgreSQL
# (Posso ajudar com isso se quiser)
```

#### Opção 2: Usar Render Disk (Tier Pago - $7/mês)
No Render dashboard:
1. Settings → Disks
2. Add Disk
3. Mount Path: `/home/user/Bolao-2026`
4. Size: 1GB

#### Opção 3: Backup Manual do SQLite
Fazer download do `bolao_2026_dev.db` periodicamente e re-upload após deploys.

## 🔧 Variáveis de Ambiente

O Render configura automaticamente:
- `SECRET_KEY` - Chave de sessão (gerada automaticamente)
- `PORT` - Porta do servidor (definida pelo Render)

Para adicionar mais:
1. Dashboard → Service → Environment
2. Add Environment Variable

## 🌐 URL do App

Após o deploy:
- URL padrão: `https://bolao-2026.onrender.com`
- Você pode configurar um domínio customizado nas Settings

## 🐛 Troubleshooting

### App não inicia:
1. Verifique os logs: Dashboard → Logs
2. Confirme que `gunicorn` está no `requirements.txt`

### Erro 502:
- O serviço pode estar "dormindo" (tier gratuito)
- Aguarde 30-60 segundos e recarregue

### Dados perdidos:
- Tier gratuito não persiste SQLite
- Migre para PostgreSQL ou use Render Disk

## 📊 Monitoramento

No dashboard do Render você pode ver:
- Logs em tempo real
- CPU e memória
- Número de requisições
- Tempo de resposta

## 💰 Custos

### Tier Gratuito:
- ✅ 750 horas/mês
- ❌ "Dorme" após 15 min de inatividade
- ❌ Dados efêmeros (SQLite é apagado)

### Tier Starter ($7/mês):
- ✅ Sempre ativo
- ✅ Disco persistente disponível
- ✅ Melhor performance

## 🔄 Re-deploy

Automaticamente em cada push:
```bash
git add .
git commit -m "Update app"
git push
```

O Render detecta mudanças e faz deploy automaticamente!

## 📞 Próximos Passos

1. ✅ Deploy inicial
2. ⚠️ Decidir sobre persistência de dados (PostgreSQL ou Render Disk)
3. 🔐 Configurar domínio customizado (opcional)
4. 📧 Configurar notificações de deploy

---

**Precisa de ajuda?** 
- Documentação: https://render.com/docs
- Ou me pergunte! 😊
