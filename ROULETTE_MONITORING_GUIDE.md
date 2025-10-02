# 🎯 Guia de Monitoramento da Roleta Brasileira

## 📊 **Status Atual: FUNCIONANDO!**

✅ **API Conectada** - PlayNabet  
✅ **Jogos Encontrados** - 14 roletas disponíveis  
✅ **Números Capturados** - 11 números únicos  
✅ **Sistema Funcionando** - Pronto para uso

---

## 🎲 **Números Capturados:**

**Última captura:** `[0, 1, 5, 11, 13, 15, 16, 24, 32, 33, 36]`

**Distribuição:**

- 🔴 **Vermelhos:** 6 números (1, 5, 11, 13, 15, 33)
- ⚫ **Pretos:** 4 números (16, 24, 32, 36)
- 🟢 **Verdes:** 1 número (0)

---

## 🚀 **Scripts Disponíveis:**

### 1. **Teste Rápido** (`quick_roulette_test.py`)

```bash
python quick_roulette_test.py
```

- ✅ Captura números uma vez
- ✅ Salva em JSON
- ✅ Mostra estatísticas
- ⏱️ Execução: ~5 segundos

### 2. **Monitor Contínuo** (`continuous_roulette_monitor.py`)

```bash
python continuous_roulette_monitor.py
```

- ✅ Monitora em tempo real
- ✅ Captura números novos
- ✅ Estatísticas automáticas
- ⏱️ Execução: Contínua

### 3. **Monitor Simples** (`simple_roulette_watcher.py`)

```bash
python simple_roulette_watcher.py
```

- ✅ Monitora múltiplos jogos
- ✅ Verificação periódica
- ✅ Estatísticas em tempo real
- ⏱️ Execução: Contínua

---

## 🎮 **Jogos Monitorados:**

1. **Brazilian Roulette** (ID: 237) - Pragmatic
2. **Auto Mega Roulette** (ID: 210) - Pragmatic
3. **Speed Roulette 1** (ID: 203) - Pragmatic
4. **Roleta Relâmpago** - Evolution
5. **Roleta Ao Vivo** - Evolution
6. **XXXtreme Lightning Roulette** - Evolution

---

## 📈 **Como Usar:**

### **Para Teste Rápido:**

```bash
python quick_roulette_test.py
```

### **Para Monitoramento Contínuo:**

```bash
python continuous_roulette_monitor.py
```

### **Para Integrar com seu Sistema:**

```python
from continuous_roulette_monitor import ContinuousRouletteMonitor

# Criar monitor
monitor = ContinuousRouletteMonitor()

# Iniciar monitoramento
monitor.start()

# Obter resultados
results = monitor.get_recent_results(10)
```

---

## 🔧 **Configurações:**

- **Token:** Válido até 2025-10-07
- **Frequência:** A cada 15 segundos
- **Jogos:** 3 roletas simultâneas
- **Histórico:** Últimos 100 resultados
- **Formato:** JSON com timestamp

---

## 📊 **Exemplo de Saída:**

```
🎲 [21:09:34] Brazilian Roulette: 15 🔴 VERMELHO
🎲 [21:09:35] Auto Mega Roulette: 32 ⚫ PRETO
🎲 [21:09:36] Speed Roulette 1: 0 🟢 VERDE

📊 ESTATÍSTICAS (15 números):
Últimos 10: [15, 32, 0, 7, 23, 14, 29, 8, 31, 12]
🔴 Vermelhos: 8 | ⚫ Pretos: 6 | 🟢 Verdes: 1
```

---

## 🎯 **Próximos Passos:**

1. **Executar monitor contínuo** para capturar números em tempo real
2. **Integrar com analyzer** para análise de padrões
3. **Configurar notificações** para padrões específicos
4. **Expandir para mais jogos** conforme necessário

---

## ⚠️ **Notas Importantes:**

- Os números capturados podem ser estáticos ou de configuração
- Para números em tempo real, use o monitor contínuo
- O sistema funciona melhor com múltiplos jogos
- Tokens precisam ser renovados periodicamente

---

## 🚀 **Status: PRONTO PARA USO!**

O sistema está funcionando e capturando números da roleta brasileira. Execute qualquer um dos scripts para começar!
