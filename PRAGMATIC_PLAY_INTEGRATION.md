# 🎰 Integração Pragmatic Play - Roleta Brasileira

Sistema completo para capturar resultados da **Roleta Brasileira** da Pragmatic Play via Playnabets, com WebSocket robusto e interface em tempo real.

## 🚀 Características

✅ **Playwright para Contornar Bloqueios** - Usa navegador headless para evitar detecção  
✅ **WebSocket Robusto** - Reconexão automática e tratamento de erros  
✅ **Flask-SocketIO** - Interface em tempo real com Chart.js  
✅ **Deploy Railway** - Configuração completa para produção  
✅ **Monitoramento 24/7** - Sistema autônomo com auto-renovação de sessão

## 📁 Arquivos Criados

```
shared/
├── pragmatic_analyzer.py          # Analisador principal com Playwright

backend/
├── websocket_app.py               # Aplicação Flask-SocketIO

templates/
├── pragmatic_websocket.html       # Interface web com Chart.js

scripts/
├── install_playwright.sh          # Script de instalação do Playwright

Configuração Railway:
├── Procfile                       # Comando de start atualizado
├── railway.toml                   # Configuração Railway
├── requirements.txt               # Dependências atualizadas
├── env.example                    # Exemplo de variáveis de ambiente

Testes:
├── test_pragmatic_integration.py  # Script de teste completo
└── PRAGMATIC_PLAY_INTEGRATION.md  # Este arquivo
```

## 🔧 Instalação

### 1. Instalar Dependências

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Instalar Playwright e navegador
pip install playwright
playwright install chromium

# Ou usar o script automatizado
chmod +x scripts/install_playwright.sh
./scripts/install_playwright.sh
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp env.example .env
```

Edite o `.env` com suas credenciais:

```env
# Credenciais Playnabets (OBRIGATÓRIO)
PLAYNABETS_USER=seu_email@exemplo.com
PLAYNABETS_PASS=sua_senha_aqui

# Configurações da aplicação
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development
PORT=5000
```

## 🚀 Como Usar

### 1. Teste Local

```bash
# Executar teste completo
python test_pragmatic_integration.py

# Iniciar aplicação WebSocket
python backend/websocket_app.py
```

Acesse: `http://localhost:5000`

### 2. Interface Web

A interface inclui:

- **Status em Tempo Real** - Conexão, monitoramento, resultados
- **Controles** - Iniciar/parar monitoramento
- **Últimos Resultados** - Grid visual com cores
- **Gráfico de Cores** - Chart.js com estatísticas
- **Alertas** - Notificações de status

### 3. API REST

```bash
# Status da aplicação
GET /api/status

# Últimos resultados
GET /api/results?limit=20

# Iniciar monitoramento
POST /api/start
Body: {"username": "email", "password": "senha"}

# Parar monitoramento
POST /api/stop
```

### 4. WebSocket Events

```javascript
// Conectar
const socket = io();

// Escutar resultados
socket.on("new_result", function (result) {
  console.log("Novo resultado:", result);
});

// Escutar status
socket.on("status_update", function (status) {
  console.log("Status atualizado:", status);
});

// Entrar na sala da roleta
socket.emit("join_roulette");
```

## 🚀 Deploy no Railway

### 1. Configuração Automática

O projeto já está configurado para Railway:

- `Procfile` - Comando de start
- `railway.toml` - Configuração Railway
- `requirements.txt` - Dependências com Playwright

### 2. Deploy

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login no Railway
railway login

# Deploy
railway up
```

### 3. Configurar Variáveis no Railway

No dashboard do Railway, configure:

```
PLAYNABETS_USER=seu_email@exemplo.com
PLAYNABETS_PASS=sua_senha_aqui
SECRET_KEY=sua_chave_secreta_forte
FLASK_ENV=production
PRAGMATIC_AUTO_START=false
```

### 4. Verificar Deploy

```bash
# Verificar logs
railway logs

# Verificar status
curl https://seu-app.railway.app/api/status
```

## 🔍 Solução de Problemas

### 1. Erro de Playwright

```bash
# Reinstalar Playwright
pip uninstall playwright
pip install playwright
playwright install chromium

# Verificar instalação
python -c "import playwright; print('OK')"
```

### 2. Erro de WebSocket no Railway

O sistema inclui:

- **Reconexão automática** a cada 30 minutos
- **Ping/pong** para manter conexão ativa
- **Headers corretos** para evitar bloqueios
- **Fallback** em caso de falha

### 3. Erro de Login

Verifique:

- Credenciais corretas no `.env`
- Conta ativa na Playnabets
- Sem bloqueios de IP
- Playwright funcionando localmente

### 4. Logs de Debug

```bash
# Ativar logs detalhados
export LOG_LEVEL=DEBUG

# Ver logs em tempo real
tail -f flask.log
```

## 📊 Estrutura de Dados

### Resultado Padronizado

```json
{
  "number": 7,
  "color": "red",
  "multiplier": 2.0,
  "timestamp": 1703123456,
  "time": "2023-12-21T10:30:56.123Z",
  "source": "pragmatic_play",
  "received_at": "2023-12-21T10:30:56.456Z",
  "id": "pragmatic_1703123456123"
}
```

### Status da Aplicação

```json
{
  "app_running": true,
  "monitoring": true,
  "results_count": 150,
  "start_time": 1703120000,
  "uptime": 3600,
  "analyzer": {
    "connected": true,
    "monitoring": true,
    "has_session": true,
    "last_result_time": 1703123456,
    "reconnect_attempts": 0,
    "playwright_available": true
  },
  "pragmatic_available": true
}
```

## 🔧 Configurações Avançadas

### 1. Intervalos de Reconexão

```env
WEBSOCKET_PING_INTERVAL=30
WEBSOCKET_PING_TIMEOUT=10
WEBSOCKET_RECONNECT_INTERVAL=1800
```

### 2. Auto-inicialização

```env
# Para iniciar automaticamente no Railway
PRAGMATIC_AUTO_START=true
```

### 3. Logs Personalizados

```env
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🎯 Próximos Passos

1. **Teste Local** - Execute `python test_pragmatic_integration.py`
2. **Configure Credenciais** - Edite o `.env` com suas credenciais
3. **Teste WebSocket** - Execute `python backend/websocket_app.py`
4. **Deploy Railway** - Execute `railway up`
5. **Monitor Produção** - Acesse a interface web

## 🆘 Suporte

- **Logs** - Verifique logs para identificar problemas
- **Teste** - Use `test_pragmatic_integration.py` para diagnóstico
- **Status** - Acesse `/api/status` para verificar estado
- **WebSocket** - Use interface web para monitoramento visual

---

**🎰 Sistema Pragmatic Play - Roleta Brasileira**  
_Captura resultados em tempo real com Playwright e WebSocket robusto_
