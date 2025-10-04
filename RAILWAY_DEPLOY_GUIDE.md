# ��� Railway Deploy Guide - Pragmatic Play

## ✅ CORREÇÕES APLICADAS

### 1. **Procfile Atualizado**
```bash
web: python app.py
```

### 2. **railway.toml Otimizado**
- ✅ Start command: `python app.py`
- ✅ Health check: `/api/pragmatic/status`
- ✅ Playwright configurado
- ✅ Python 3.12

### 3. **requirements.txt Simplificado**
- ✅ Removido `eventlet` (problema SSL)
- ✅ Removido `websocket-client` (conflito)
- ✅ Mantido apenas dependências essenciais
- ✅ Playwright incluído

### 4. **railway.env Criado**
- ✅ Configurações de produção
- ✅ Variáveis de ambiente
- ✅ Credenciais template

## ��� COMO FAZER DEPLOY

### **Passo 1: Configurar Railway**
1. Acesse [Railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Selecione este projeto

### **Passo 2: Configurar Variáveis**
No Railway Dashboard, adicione:
```
PLAYNABETS_USER=seu_email_real@exemplo.com
PLAYNABETS_PASS=sua_senha_real
SECRET_KEY=sua_chave_secreta_forte
```

### **Passo 3: Deploy Automático**
- Railway vai detectar `Procfile`
- Instalar dependências do `requirements.txt`
- Instalar Playwright automaticamente
- Executar `python app.py`

## ✅ VERIFICAÇÕES PÓS-DEPLOY

### **1. Health Check**
```bash
curl https://seu-app.railway.app/api/pragmatic/status
```

### **2. Interface Web**
- URL: `https://seu-app.railway.app`
- Dashboard: `https://seu-app.railway.app/roulette`
- Pragmatic: `https://seu-app.railway.app/pragmatic`

### **3. Logs Railway**
- Verifique logs no Railway Dashboard
- Deve mostrar: "PragmaticAnalyzer importado com sucesso"
- Deve mostrar: "Credenciais configuradas"

## ��� FUNCIONALIDADES DISPONÍVEIS

### **APIs Pragmatic Play:**
- `GET /api/pragmatic/status` - Status do sistema
- `POST /api/pragmatic/start` - Iniciar monitoramento
- `POST /api/pragmatic/stop` - Parar monitoramento
- `GET /api/pragmatic/results` - Últimos resultados

### **APIs PlayNabets:**
- `GET /api/roulette/status` - Status da roleta
- `POST /api/roulette/start` - Iniciar roleta
- `POST /api/roulette/stop` - Parar roleta

## ��� TROUBLESHOOTING

### **Problema: Playwright não instala**
```bash
# Solução: Adicionar no Railway Dashboard
PLAYWRIGHT_BROWSERS=chromium
```

### **Problema: Credenciais não reconhecidas**
```bash
# Verificar no Railway Dashboard:
PLAYNABETS_USER=seu_email@exemplo.com
PLAYNABETS_PASS=sua_senha
```

### **Problema: Porta não configurada**
```bash
# Railway usa PORT automaticamente
# Não precisa configurar manualmente
```

## ��� RESULTADO ESPERADO

Após o deploy, você terá:
- ✅ Servidor funcionando 24/7
- ✅ Pragmatic Play integrado
- ✅ PlayNabets funcionando
- ✅ Interface web acessível
- ✅ APIs funcionais
- ✅ Monitoramento automático

**PRONTO PARA DEPLOY!** ���✨
