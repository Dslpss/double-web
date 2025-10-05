# 🤖 Modo Bot Telegram - Double Analyzer

## 📋 Visão Geral

O **Modo Bot Telegram** replica a lógica simples e eficaz dos bots de sinal populares do Telegram. Ao invés de usar 68 padrões complexos, ele foca em **sequências claras** e **sinais frequentes**.

## ✨ Características

### 🎯 Lógica Simplificada
- **Sequências**: 3+ da mesma cor → Apostar na oposta
- **Predominância**: 7+ de uma cor em 10 → Continuar na mesma
- **Alternância**: R-B-R-B-R-B → Seguir o padrão

### ⚡ Sinais Rápidos
- **Cooldown**: 2 minutos (vs 3 minutos do modo avançado)
- **Dados mínimos**: 3 resultados (vs 8 do modo avançado)
- **Sinais frequentes**: Mais oportunidades de entrada

### 💰 Sistema de Gale
- **Gale ativo** por padrão
- **Até 2 tentativas** de recuperação
- **Proteção**: Mensagem clara sobre quantas tentativas

## 🚀 Como Usar

### 1. Ativar Modo Bot (API)

```bash
# Ativar modo bot
curl -X POST http://localhost:5000/api/bot/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "telegram_bot"}'

# Resposta:
{
  "success": true,
  "mode": "telegram_bot",
  "bot_active": true
}
```

### 2. Configurar Parâmetros

```bash
# Configurar cooldown e gale
curl -X POST http://localhost:5000/api/bot/config \
  -H "Content-Type: application/json" \
  -d '{
    "cooldown": 120,
    "gale_enabled": true,
    "max_gales": 2
  }'
```

### 3. Ver Estatísticas

```bash
# Ver stats do bot
curl http://localhost:5000/api/bot/stats

# Resposta:
{
  "total_signals": 15,
  "cooldown_seconds": 120,
  "last_signal_time": 1696789012,
  "gale_enabled": true,
  "max_gales": 2,
  "mode": "telegram_bot",
  "bot_active": true
}
```

## 🎮 Usando na Interface

### JavaScript Example

```javascript
// Ativar modo bot
async function activateBotMode() {
  const response = await fetch('/api/bot/mode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: 'telegram_bot' })
  });
  const data = await response.json();
  console.log('Bot ativado:', data);
}

// Configurar bot
async function configurateBot(cooldown = 120, maxGales = 2) {
  const response = await fetch('/api/bot/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cooldown: cooldown,
      gale_enabled: true,
      max_gales: maxGales
    })
  });
  const data = await response.json();
  console.log('Bot configurado:', data);
}

// Ver estatísticas
async function getBotStats() {
  const response = await fetch('/api/bot/stats');
  const stats = await response.json();
  console.log('Estatísticas:', stats);
  return stats;
}
```

## 📊 Tipos de Sinal

### 1. Sequência (Mais Comum)

```
🎯 SINAL DETECTADO! 🎯

⚫ ENTRE EM PRETO ⚫

📊 Padrão: 4x RED
💰 Proteção: Até 2 GALES
⚡ Confiança: 70%

🔄 Sequência de 4 REDs - Apostar na reversão
```

**Lógica**: Após 3+ vermelhos consecutivos, apostar em preto (martingale reverso)

### 2. Predominância

```
🎯 SINAL DETECTADO! 🎯

🔴 ENTRE EM VERMELHO 🔴

📊 Padrão: 7/10 RED
💰 Proteção: Até 2 GALES
⚡ Confiança: 75%

🔄 7 REDs nos últimos 10 - Apostar na continuação
```

**Lógica**: Se uma cor domina 70%+ dos últimos 10, continuar apostando nela (hot hand)

### 3. Alternância

```
🎯 SINAL DETECTADO! 🎯

⚫ ENTRE EM PRETO ⚫

📊 Padrão: Alternância R-B-R-B
💰 Proteção: Até 2 GALES
⚡ Confiança: 75%

🔄 Padrão de alternância detectado - Seguir sequência
```

**Lógica**: Padrão R-B-R-B-R-B detectado, seguir alternando

## ⚙️ Configurações

### Cooldown (Tempo entre Sinais)

```python
# Padrão: 120 segundos (2 minutos)
# Mínimo: 60 segundos (1 minuto)
# Máximo: 300 segundos (5 minutos)

analyzer.set_bot_cooldown(120)
```

### Sistema de Gale

```python
# Ativar/desativar Gale
# max_gales: 1-3 tentativas

analyzer.set_bot_gale(enabled=True, max_gales=2)
```

### Sequência Mínima

```python
# Definido em telegram_bot_logic.py
self.min_sequence_for_signal = 3  # Padrão: 3 cores iguais
```

## 🔄 Modos Disponíveis

| Modo | Descrição | Cooldown | Dados Mín | Padrões |
|------|-----------|----------|-----------|---------|
| **telegram_bot** | 🤖 Lógica simples dos bots | 2 min | 3 | 3 tipos |
| opposite | Apostar na cor oposta | 3 min | 8 | 68 tipos |
| continue | Apostar na mesma cor | 3 min | 8 | 68 tipos |

### Trocar de Modo

```python
# Via API
POST /api/bot/mode
{ "mode": "telegram_bot" }  # ou "opposite", "continue"

# Via código Python
analyzer.set_prediction_mode('telegram_bot')
```

## 🎯 Vantagens do Modo Bot

✅ **Sinais mais frequentes** (a cada 2 min vs 3 min)  
✅ **Lógica mais simples** (3 padrões vs 68)  
✅ **Mais fácil de entender** (sequências claras)  
✅ **Sistema de Gale integrado** (proteção automática)  
✅ **Menos dados necessários** (3 vs 8 resultados)  
✅ **Estilo familiar** (igual aos bots do Telegram)

## 📈 Quando Usar Cada Modo

### Use **Modo Bot** quando:
- ✅ Quer sinais simples e frequentes
- ✅ Prefere lógica direta (sequências)
- ✅ Gosta do estilo dos bots do Telegram
- ✅ Quer usar sistema de Gale

### Use **Modo Avançado** quando:
- ✅ Quer análise profunda (68 padrões)
- ✅ Prefere sinais mais conservadores
- ✅ Quer confiança maior (72%+)
- ✅ Não quer sinais tão frequentes

## 🐛 Troubleshooting

### Bot não envia sinais

1. **Verifique se está ativo**:
```bash
curl http://localhost:5000/api/bot/stats
# Deve mostrar "bot_active": true
```

2. **Verifique cooldown**:
- Bot precisa aguardar 2 minutos entre sinais
- Veja `last_signal_time` nas stats

3. **Adicione mais resultados**:
- Bot precisa de pelo menos 3 resultados
- Adicione via `/api/add_result`

### Sinais muito frequentes

```bash
# Aumente o cooldown para 3-5 minutos
curl -X POST http://localhost:5000/api/bot/config \
  -d '{"cooldown": 180}'  # 3 minutos
```

### Quer desativar Gale

```bash
curl -X POST http://localhost:5000/api/bot/config \
  -d '{"gale_enabled": false}'
```

## 📝 Exemplo Completo

```python
# 1. Ativar modo bot
analyzer.set_prediction_mode('telegram_bot')

# 2. Configurar
analyzer.set_bot_cooldown(120)  # 2 minutos
analyzer.set_bot_gale(True, 2)  # Até 2 gales

# 3. Adicionar resultados
analyzer.add_manual_result(5, 'red')
analyzer.add_manual_result(7, 'red')
analyzer.add_manual_result(3, 'red')
# Bot detecta 3 vermelhos → Sinal para apostar em PRETO

# 4. Ver stats
stats = analyzer.get_bot_stats()
print(f"Sinais enviados: {stats['total_signals']}")
```

## 🔗 Referências

- **Código**: `shared/src/analysis/telegram_bot_logic.py`
- **Integração**: `shared/blaze_analyzer_enhanced.py`
- **API**: `app.py` (endpoints `/api/bot/*`)

---

**🤖 Modo Bot ativo! Sinais simples e eficazes como os bots do Telegram.**
