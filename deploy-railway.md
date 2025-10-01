# 🚀 Deploy no Railway - Guia Completo

## 📋 Pré-requisitos

1. **Conta no Railway**: https://railway.app
2. **Railway CLI**: `npm install -g @railway/cli`
3. **Git configurado** no projeto

## 🔧 Passos para Deploy

### 1. Instalar Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login no Railway

```bash
railway login
```

### 3. Conectar Projeto

```bash
# Na raiz do projeto
railway link
```

### 4. Configurar Variáveis de Ambiente

```bash
# No dashboard Railway ou via CLI
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=sua_chave_secreta_aqui
railway variables set BLAZE_WEBSOCKET_URL=wss://play.soline.bet:5903/Game
railway variables set ANALYZER_ENABLED=true
railway variables set NOTIFICATIONS_ENABLED=false
```

### 5. Deploy

```bash
# Commit e push
git add .
git commit -m "Deploy to Railway"
git push origin main

# Railway faz deploy automático!
```

## 📁 Arquivos Criados

- ✅ `Procfile` - Comando de inicialização
- ✅ `railway.json` - Configurações do Railway
- ✅ `railway.env` - Variáveis de ambiente
- ✅ `backend/requirements.txt` - Atualizado com gunicorn

## 🌐 URLs Após Deploy

- **App**: https://seu-projeto.railway.app
- **Dashboard**: https://railway.app/dashboard
- **Logs**: Disponível no dashboard Railway

## 🔍 Verificação

1. Acesse a URL do Railway
2. Teste `/api/status`
3. Verifique logs no dashboard
4. Teste funcionalidades principais

## 🆘 Troubleshooting

### Erro de Porta

- Railway define automaticamente a porta via `PORT` env var
- Código já configurado para usar `os.environ.get('PORT', 5000)`

### Erro de Dependências

- Verifique `requirements.txt`
- Railway usa Nixpacks para detectar Python

### Erro de Banco de Dados

- Railway oferece PostgreSQL gratuito
- SQLite funciona para desenvolvimento

## 📞 Suporte

- **Railway Docs**: https://docs.railway.app
- **Status**: https://status.railway.app
