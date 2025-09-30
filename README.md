# 🔥 Blaze Double Analyzer - Web

Versão web completa do Blaze Double Analyzer com interface moderna, autenticação e comunicação em tempo real.

## 🚀 Características

- **Interface Web Moderna**: Design responsivo com gradientes e efeitos visuais
- **Dashboard Avançado**: Gráficos, métricas e visualizações em tempo real
- **Sistema de Autenticação**: Login, registro e controle de acesso
- **Tempo Real**: WebSocket para atualizações instantâneas
- **API REST Completa**: Endpoints para integração e controle
- **Reutilização Total**: Usa 100% da lógica do projeto original
- **Validação de Alertas**: Sistema completo de validação de predições
- **Gráficos Interativos**: Chart.js para visualizações avançadas

## 📁 Estrutura do Projeto

```
blaze-web/
├── backend/                 # Servidor Flask + WebSocket
│   ├── app.py              # Aplicação principal
│   ├── requirements.txt    # Dependências Python
│   └── templates/         # Templates HTML
│       └── index.html     # Interface principal
├── frontend/               # Frontend (futuro)
├── shared/                 # Código compartilhado
│   ├── src/               # Módulos do projeto original
│   └── blaze_analyzer_enhanced.py
└── README.md
```

## 🛠️ Instalação e Execução

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Executar Servidor

#### Versão Simples (sem WebSocket):

```bash
python simple_app.py
```

#### Versão Completa (com WebSocket):

```bash
python websocket_app.py
```

### 3. Acessar Interface

- **Página Principal**: http://localhost:5000
- **Login**: http://localhost:5000/login
- **Dashboard**: http://localhost:5000/dashboard

### 4. Credenciais de Teste

⚠️ **IMPORTANTE**: Altere essas senhas antes de usar em produção!

- **Admin**: `admin` / `admin123` (ALTERE EM PRODUÇÃO!)
- **Usuário**: `user` / `user123` (ALTERE EM PRODUÇÃO!)

### 5. Configuração de Segurança

```bash
# 1. Copie o arquivo de configuração
cp env.example .env

# 2. Edite as configurações sensíveis
nano .env

# 3. Gere uma nova chave secreta
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Leia o arquivo [SECURITY.md](SECURITY.md) para instruções completas de segurança.**

## 🔧 Funcionalidades

### ✅ Implementadas

- **Interface Web Responsiva**: Design moderno com CSS Grid e Flexbox
- **Dashboard Avançado**: Gráficos interativos com Chart.js
- **Sistema de Autenticação**: Login, registro e controle de acesso
- **WebSocket em Tempo Real**: Atualizações instantâneas
- **API REST Completa**: Endpoints para todos os dados
- **Reutilização Total**: 100% da lógica do projeto original
- **Validação de Alertas**: Sistema completo de validação
- **Métricas em Tempo Real**: Precisão, confiança, padrões ativos
- **Gráficos Dinâmicos**: Distribuição de cores e tendências

### 🔄 Em Desenvolvimento

- **Conexão Real com Blaze**: WebSocket real (atualmente simulado)
- **Notificações Push**: Alertas no navegador
- **Cache e Performance**: Otimizações avançadas
- **Deploy na Nuvem**: Hospedagem profissional

## 📡 API Endpoints

### Páginas Web

- `GET /` - Página principal
- `GET /login` - Página de login
- `GET /dashboard` - Dashboard avançado

### Status

- `GET /api/status` - Status do sistema

### Autenticação

- `POST /api/auth/login` - Realizar login
- `POST /api/auth/logout` - Realizar logout
- `POST /api/auth/register` - Registrar usuário
- `GET /api/auth/me` - Informações do usuário atual

### Resultados

- `GET /api/results` - Últimos resultados
- `POST /api/add_result` - Adicionar resultado manual (requer auth)

### Análise

- `GET /api/analysis` - Análise atual
- `GET /api/predictions` - Predições ativas

### Admin (requer admin)

- `GET /api/admin/users` - Listar usuários

## 🔌 WebSocket Events

### Cliente → Servidor

- `request_analysis` - Solicitar análise
- `request_results` - Solicitar resultados

### Servidor → Cliente

- `new_result` - Novo resultado
- `analysis_update` - Análise atualizada
- `results_update` - Resultados atualizados
- `error` - Erro no sistema

## Tecnologias

### Backend

- **Flask**: Framework web Python
- **Flask-SocketIO**: WebSocket para tempo real
- **Flask-CORS**: CORS para integração
- **Eventlet**: Servidor assíncrono

### Frontend

- **HTML5**: Estrutura semântica
- **CSS3**: Estilos modernos com gradientes
- **JavaScript**: Lógica da interface
- **Socket.IO**: Cliente WebSocket

## 🔄 Reutilização do Código Original

O projeto web reutiliza **100%** da lógica do projeto original:

- ✅ **Análise de Padrões**: `src/analysis/`
- ✅ **Sistema de ML**: `src/ml/`
- ✅ **Validação de Predições**: `src/ml/prediction_validator.py`
- ✅ **Banco de Dados**: `src/database/db_manager.py`
- ✅ **Sistema de Alertas**: `src/notifications/alert_system.py`
- ✅ **Analyzer Principal**: `blaze_analyzer_enhanced.py`

## Próximos Passos

1. **Conexão Real com Blaze**: Implementar WebSocket real
2. **Autenticação**: Sistema de usuários
3. **Dashboard Avançado**: Gráficos e métricas
4. **Mobile App**: Versão para dispositivos móveis
5. **Deploy**: Hospedagem na nuvem

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório original.

---

**Desenvolvido com ❤️ reutilizando toda a lógica do projeto original!**
