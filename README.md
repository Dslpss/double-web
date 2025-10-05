# 🎰 Blaze Double Analyzer

Sistema inteligente de análise de padrões para Blaze Double com integração PlayNabets e Pragmatic Play Brazilian Roulette.

## 🚀 Funcionalidades

- 🎯 **Análise de Padrões em Tempo Real**: Detecta 68 padrões diferentes no Double
- 🔔 **Sistema de Alertas Inteligente**: Notificações visuais apenas para padrões fortes (60%+ confiança)
- 📊 **Dashboard Completo**: Interface web moderna para monitoramento
- 🎲 **Multi-Jogos**: Suporte para Double, PlayNabets e Brazilian Roulette
- 🤖 **Aprendizado Adaptativo**: Sistema melhora com o tempo
- 📈 **Estatísticas Avançadas**: Análise de performance e taxa de acerto
- 🔐 **Sistema de Autenticação**: Login e controle de acesso

## 📡 Integrações

### Blaze Double
- Análise manual de resultados
- Sistema de predição com 68 padrões
- Alertas em tempo real

### PlayNaBets
- Conexão WebSocket automática
- Monitoramento em tempo real
- Autenticação e gestão de sessão

### Pragmatic Play (Brazilian Roulette)
- Integração completa com API GS12
- Estatísticas aprimoradas com fallback
- Detecção automática de manutenção
- Suporte a proxies

Para mais detalhes:
- [Integração GS12](./docs/GS12_INTEGRATION.md)
- [Manutenções](./docs/PRAGMATIC_MAINTENANCE.md)
- [Configuração de Proxies](./docs/PROXY_CONFIGURATION.md)

## 📋 Requisitos

- Python 3.12+
- SQLite3
- Navegador moderno (Chrome, Firefox, Edge)

## 🔧 Instalação

1. **Clone o repositório**
2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente**:
```bash
cp env.example .env
# Edite .env com suas credenciais
```

4. **Execute o servidor**:
```bash
python app.py
```

5. **Acesse**: `http://localhost:5000`

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# PlayNabets
PLAYNABETS_USER=seu_usuario
PLAYNABETS_PASS=sua_senha

# Pragmatic Play
PRAGMATIC_API_URL=https://api.pragmaticplay.net
PRAGMATIC_CASINO_ID=seu_casino_id

# Auto-start
ROULETTE_AUTO_START=true

# Segurança
SECRET_KEY=sua_chave_secreta_aqui
```

**⚠️ IMPORTANTE**: Altere as credenciais padrão antes de usar em produção! Leia [SECURITY.md](SECURITY.md) para mais informações.

## 🔔 Sistema de Alertas

### Proteções Anti-Spam

O sistema possui múltiplas proteções para evitar alertas falsos:

- ✅ **Cooldown de 3 minutos** entre alertas
- ✅ **Mínimo de 8 rodadas** para análise
- ✅ **Threshold de 60%+** de confiança para notificações
- ✅ **Threshold de 72%+** para padrões Double
- ✅ **Validação de qualidade** dos dados
- ✅ **Bloqueio por previsão pendente**

### Como Funciona

1. Sistema analisa resultados continuamente
2. Detecta padrão forte (72%+ confiança)
3. Verifica proteções (cooldown, dados suficientes, etc.)
4. Se todas as verificações passam, **envia alerta**
5. Aguarda 3 minutos antes do próximo sinal

## 📊 Padrões Detectados

### Tipos Principais

- **Sequências**: Mesma cor 6+ vezes consecutivas
- **Predominância**: Uma cor 75%+ em 8 rodadas
- **Martingale**: Progressão após perdas
- **Fibonacci**: Sequências numéricas
- **Hot/Cold**: Números quentes e frios
- **Red After Red**: Vermelho após vermelho
- **Number Patterns**: Padrões específicos (1→Red, 14→Black, etc.)
- **E mais 60+ padrões**

## 📁 Estrutura do Projeto

```
double-web/
├── app.py                    # Servidor Flask principal
├── auth.py                   # Autenticação
├── config.py                 # Configurações
├── playnabets_integrator.py # Integração PlayNabets
├── data/                     # Bancos de dados
├── shared/                   # Módulos compartilhados
│   ├── blaze_analyzer_enhanced.py
│   └── src/
│       ├── analysis/        # Detectores de padrão
│       ├── ml/              # Machine Learning
│       ├── notifications/   # Sistema de alertas
│       └── database/        # Gerenciamento de dados
├── integrators/             # Integradores de jogos
├── frontend/                # Interface web
├── templates/               # Templates HTML
├── static/                  # CSS, JS, imagens
└── docs/                    # Documentação
```

## 📡 API Endpoints Principais

### Páginas Web
- `GET /` - Página inicial (Double)
- `GET /login` - Login
- `GET /dashboard` - Dashboard
- `GET /playnabets` - PlayNabets
- `GET /roulette` - Brazilian Roulette

### Resultados
- `POST /api/add_result` - Adicionar resultado manual
- `GET /api/poll/results` - Obter resultados recentes
- `GET /api/poll/analysis` - Obter análise atual

### Double
- `GET /api/double/history` - Histórico
- `GET /api/double/patterns` - Padrões detectados
- `GET /api/double/stats` - Estatísticas

### Roleta Pragmatic
- `POST /api/roulette/start` - Iniciar monitoramento
- `POST /api/roulette/stop` - Parar monitoramento
- `GET /api/roulette/status` - Status da conexão

### PlayNabets
- `POST /api/playnabets/connect` - Conectar WebSocket
- `POST /api/playnabets/disconnect` - Desconectar
- `GET /api/playnabets/status` - Status

Para documentação completa da API, consulte [GUIA_DE_USO.md](docs/GUIA_DE_USO.md)

## 🚀 Deploy (Railway)

1. Conecte o repositório ao Railway
2. Configure variáveis de ambiente no dashboard
3. Deploy automático a cada push
4. Monitore logs: `railway logs -f`

## 🐛 Troubleshooting

### Alertas não aparecem
1. Verifique se há predições pendentes no banco
2. Confira se cooldown não está ativo (3 min)
3. Verifique logs para mensagens de bloqueio

### Conexão PlayNabets falha
1. Verifique credenciais no `.env`
2. Teste login manualmente
3. Verifique logs de erro

### Erro 500 na API
1. Verifique logs do servidor
2. Confirme banco de dados acessível
3. Valide configurações no `.env`

## 📚 Documentação Adicional

- [Guia de Uso Completo](docs/GUIA_DE_USO.md)
- [Sistema de Detecção de Padrões](docs/PATTERN_DETECTION_SYSTEM.md)
- [Configuração de Proxy](docs/PROXY_CONFIGURATION.md)
- [Manutenção Pragmatic](docs/PRAGMATIC_MAINTENANCE.md)
- [Segurança](SECURITY.md)

## 🔐 Segurança

- ✅ Autenticação JWT
- ✅ Variáveis de ambiente para credenciais
- ✅ Rate limiting
- ✅ Validação de dados
- ✅ Sanitização de inputs

**⚠️ Nunca commite credenciais no código!**

## 📝 Licença

Uso pessoal apenas.

---

**Versão**: 2.0  
**Última Atualização**: Outubro 2025
