# ��� Railway Deploy Checklist - TUDO PRONTO!

## ✅ **ARQUIVOS CONFIGURADOS:**

### 1. **Procfile** ✅
```bash
web: python app.py
```

### 2. **railway.toml** ✅
- ✅ Start command: `python app.py`
- ✅ Health check: `/api/pragmatic/status`
- ✅ Python 3.12
- ✅ Playwright configurado
- ✅ Build command com dependências

### 3. **requirements.txt** ✅
- ✅ Flask>=2.3.0
- ✅ Flask-CORS>=4.0.0
- ✅ requests>=2.31.0
- ✅ python-dotenv>=1.0.0
- ✅ playwright>=1.40.0
- ✅ gunicorn>=21.0.0
- ✅ Dependências científicas (pandas, numpy, etc.)

### 4. **railway.env** ✅
- ✅ FLASK_ENV=production
- ✅ PORT=5000
- ✅ HOST=0.0.0.0
- ✅ SECRET_KEY configurado
- ✅ Template para credenciais PlayNabets

## ��� **VARIÁVEIS DE AMBIENTE NECESSÁRIAS:**

### **Obrigatórias no Railway Dashboard:**
```env
PLAYNABETS_USER=seu_email_real@exemplo.com
PLAYNABETS_PASS=sua_senha_real
SECRET_KEY=sua_chave_secreta_forte
```

### **Opcionais (já configuradas):**
```env
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
PRAGMATIC_AUTO_START=false
PLAYWRIGHT_BROWSERS=chromium
```

## ��� **COMANDOS PARA DEPLOY:**

### **1. Instalar Railway CLI:**
```bash
npm install -g @railway/cli
```

### **2. Login no Railway:**
```bash
railway login
```

### **3. Deploy:**
```bash
railway up
```

### **4. Configurar Variáveis:**
```bash
railway variables set PLAYNABETS_USER=seu_email@exemplo.com
railway variables set PLAYNABETS_PASS=sua_senha
railway variables set SECRET_KEY=sua_chave_secreta
```

## ✅ **VERIFICAÇÕES FINAIS:**

- ✅ **app.py** importa sem erros
- ✅ **PragmaticAnalyzer** disponível
- ✅ **Credenciais** corrigidas (PLAYNABETS_USER/PASS)
- ✅ **Playwright** configurado
- ✅ **Health check** funcionando
- ✅ **Templates** sem problemas de encoding

## ��� **APÓS O DEPLOY:**

### **URLs Disponíveis:**
- **Principal:** `https://seu-app.railway.app/`
- **Status:** `https://seu-app.railway.app/api/pragmatic/status`
- **Roleta:** `https://seu-app.railway.app/roulette`
- **Pragmatic:** `https://seu-app.railway.app/pragmatic`

### **Testes:**
```bash
# Health check
curl https://seu-app.railway.app/api/pragmatic/status

# Página principal
curl https://seu-app.railway.app/
```

## ��� **RESULTADO ESPERADO:**

✅ **Servidor funcionando 24/7**
✅ **Pragmatic Play integrado**
✅ **PlayNabets funcionando**
✅ **Interface web acessível**
✅ **APIs funcionais**
✅ **Monitoramento automático**

**TUDO PRONTO PARA DEPLOY!** ���✨
