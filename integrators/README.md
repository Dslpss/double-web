# Integrators - Sistema de Integração com Roletas

Este diretório contém os integradores modulares para diferentes plataformas de roleta.

## 📦 Integradores Disponíveis

### 🎰 Pragmatic Play Integrator

**Arquivo:** `pragmatic_play_integrator.py`

Integrador completo para a Roleta Brasileira da Pragmatic Play com auto-renovação de sessão.

#### ✨ Funcionalidades

- ✅ **Auto-renovação de JSESSIONID**: Nunca mais erro 401!
- ✅ **Monitoramento em tempo real**: Refresh automático a cada 3-5 segundos
- ✅ **Parse inteligente**: Extrai número, cor e gameId automaticamente
- ✅ **Thread em background**: Operação contínua sem bloquear
- ✅ **Funciona sem navegador**: Sistema autônomo 24/7

#### 🚀 Como Usar

```python
from integrators.pragmatic_play_integrator import PragmaticPlayIntegrator

# Inicializar com token do Playnabet
token = "seu_token_jwt_aqui"
integrator = PragmaticPlayIntegrator(playnabet_token=token)

# Iniciar monitoramento (refresh a cada 5 segundos)
integrator.start(refresh_interval=5)

# Obter últimos resultados parseados
results = integrator.get_latest(limit=10)
for result in results:
    print(f"Número: {result['number']}, Cor: {result['color']}")

# Parar quando necessário
integrator.stop()
```

#### 🔌 API REST Endpoints

```bash
# Iniciar integrador
POST /api/pragmatic/start
Body: {"token": "jwt_token", "refresh_interval": 5}

# Parar integrador
POST /api/pragmatic/stop

# Obter últimos resultados
GET /api/pragmatic/latest?limit=10
```

#### 🛠️ Scripts Auxiliares

**Monitor em Tempo Real:**

```bash
python scripts/monitor_pragmatic_realtime.py
```

Mostra resultados chegando ao vivo com emojis coloridos:

- 🔴 Números vermelhos
- ⚫ Números pretos
- ⚪ Zero (verde)

**Extração Manual:**

```bash
python scripts/extract_pragmatic_from_iframe.py --token "seu_token"
```

### 🔍 Pragmatic Comparator

**Arquivo:** `pragmatic_comparator.py`

Compara resultados do integrador com a fonte autoritativa para validação.

#### 🚀 Como Usar

```python
from integrators.pragmatic_comparator import PragmaticComparator
from integrators.pragmatic_play_integrator import PragmaticPlayIntegrator

# Criar integrador
integrator = PragmaticPlayIntegrator(playnabet_token="token")
integrator.start()

# Criar comparador
comparator = PragmaticComparator(integrator, playnabet_token="token")
comparator.start(check_interval=10)  # Verifica a cada 10 segundos

# Obter divergências
mismatches = comparator.get_mismatches()
print(f"Encontradas {len(mismatches)} divergências")

# Parar
comparator.stop()
integrator.stop()
```

#### 🔌 API REST Endpoints

```bash
# Iniciar comparador
POST /api/pragmatic/comparator/start
Body: {"check_interval": 10}

# Parar comparador
POST /api/pragmatic/comparator/stop

# Obter divergências
GET /api/pragmatic/comparator/mismatches
```

## 🏗️ Arquitetura

```
integrators/
├── README.md                          # Este arquivo
├── pragmatic_play_integrator.py       # Integrador principal
├── pragmatic_comparator.py            # Comparador de resultados
└── __init__.py                        # Exportações
```

## 🔐 Autenticação

O integrador usa token JWT do Playnabet para renovar automaticamente o JSESSIONID:

1. **Token JWT** → Chama `/casino/games/url` no Playnabet
2. **Redirect URL** → Extrai JSESSIONID do redirect
3. **JSESSIONID** → Usa para chamar API da Pragmatic Play
4. **Auto-renew** → Quando expira (401), renova automaticamente

## 📊 Formato dos Resultados

```json
{
  "game_id": "10036123112",
  "number": 29,
  "color": "black",
  "timestamp": "2025-10-02T11:36:41Z"
}
```

## 🧪 Testes

```bash
# Testar integrador
python -m pytest tests/test_pragmatic_integration.py -v

# Monitorar em tempo real (60 segundos)
timeout 60 python scripts/monitor_pragmatic_realtime.py
```

## 🐛 Debug

Se encontrar erro 401:

1. ✅ Verifique se o token JWT está válido
2. ✅ O integrador deve renovar automaticamente
3. ✅ Veja os logs para mensagens de renovação

Se não receber resultados:

1. ✅ Verifique conexão com internet
2. ✅ Confirme que o token tem acesso ao jogo
3. ✅ Use `monitor_pragmatic_realtime.py` para ver visualmente

## 📝 Notas

- Todos os arquivos `.db` (bancos) são ignorados pelo git
- Arquivos JSON temporários são ignorados pelo git
- Warnings SSL (`InsecureRequestWarning`) são normais em dev (usar `verify=False`)
- Para produção, configurar certificados SSL adequados

## 🤝 Contribuindo

Para adicionar novo integrador:

1. Criar arquivo `nome_plataforma_integrator.py`
2. Implementar métodos: `start()`, `stop()`, `get_latest()`
3. Adicionar testes em `tests/test_nome_plataforma.py`
4. Documentar neste README
5. Adicionar endpoints REST em `app.py`

## 📜 Licença

Este código é parte do projeto double-web.

