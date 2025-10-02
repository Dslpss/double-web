# 🎰 Integração Pragmatic Play Live Roulette

## ✅ Solução Implementada

Você **NÃO estava recebendo erro 401**! A requisição para a API da Pragmatic Play estava funcionando perfeitamente (HTTP 200 OK).

Criei uma integração completa para buscar resultados da roleta da Pragmatic Play automaticamente.

---

## 📦 Arquivos Criados

### 1. `pragmatic_play_integrator.py`
Classe principal para integrar com a API da Pragmatic Play:
- ✅ Busca histórico de resultados (até 500 jogos)
- ✅ Parseia resultados no formato "30 Red", "20 Black", "0 Green"
- ✅ Calcula estatísticas (% vermelho, preto, verde)
- ✅ Formata dados para o analyzer
- ✅ Detecta novos resultados automaticamente

### 2. Endpoints no `app.py`
Novos endpoints REST para Pragmatic Play:

#### `GET /api/pragmatic/status`
Status do integrador
```json
{
  "available": true,
  "initialized": true,
  "table_id": "rwbrzportrwa16rg",
  "statistics": {...}
}
```

#### `POST /api/pragmatic/fetch`
Buscar histórico de resultados
```json
{
  "table_id": "rwbrzportrwa16rg",  // opcional
  "session_id": "...",               // opcional
  "count": 50                        // opcional (padrão: 50, máx: 500)
}
```

**Resposta:**
```json
{
  "success": true,
  "count": 50,
  "results": [...],
  "statistics": {...}
}
```

#### `GET /api/pragmatic/results?count=20`
Obter últimos N resultados

#### `GET /api/pragmatic/new`
Buscar apenas novos resultados desde a última verificação

#### `GET /api/pragmatic/statistics`
Estatísticas completas dos resultados

---

## 🧪 Como Testar

### 1. Testar o Integrador Diretamente
```bash
python test_pragmatic_integration.py
```

Isso vai:
- ✅ Buscar últimos 100 jogos
- ✅ Mostrar últimos 10 resultados
- ✅ Calcular estatísticas
- ✅ Formatar dados para o analyzer
- ✅ Testar busca de novos resultados

### 2. Testar via API (com o app.py rodando)
```bash
# Iniciar servidor
python app.py

# Em outro terminal, testar endpoints:

# Buscar histórico
curl -X POST http://localhost:5001/api/pragmatic/fetch \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'

# Ver status
curl http://localhost:5001/api/pragmatic/status

# Ver resultados
curl http://localhost:5001/api/pragmatic/results?count=20

# Ver estatísticas
curl http://localhost:5001/api/pragmatic/statistics
```

---

## 📊 Formato dos Dados

### Resultado da API Pragmatic Play
```python
{
    'game_id': '10035674212',
    'number': 30,
    'color': 'red',
    'game_type': '0000000000000001',
    'bet_count': 0,
    'player_count': 0,
    'player_win_count': 0,
    'power_up_threshold_reached': False,
    'fortune_roulette': False,
    'power_up_roulette': False,
    'mega_roulette': False,
    'timestamp': 1696252306,
    'source': 'pragmatic_play_api'
}
```

### Formato para o Analyzer
```python
{
    'id': '10035674212',
    'roll': 30,
    'number': 30,
    'color': 'red',
    'timestamp': 1696252306
}
```

---

## 🔄 Fluxo de Integração

```
1. PragmaticPlayIntegrator.fetch_history()
   └── Faz requisição para API Pragmatic Play
       └── URL: https://games.pragmaticplaylive.net/api/ui/statisticHistory
       └── Params: tableId, numberOfGames, JSESSIONID, etc.

2. Processa resultados
   └── Parseia "30 Red" → {number: 30, color: 'red'}
   └── Adiciona metadados (game_id, timestamp, etc.)

3. Atualiza sistema
   └── Adiciona a last_results (global)
   └── Envia para analyzer (se disponível)
   └── Calcula estatísticas

4. Frontend pode buscar via:
   └── GET /api/results (resultados globais)
   └── GET /api/pragmatic/results (específico Pragmatic)
   └── GET /api/pragmatic/new (apenas novos)
```

---

## 🎯 Próximos Passos

### 1. Integração Automática
Adicionar polling automático para buscar novos resultados:

```python
# No app.py, adicionar:
def auto_fetch_pragmatic():
    """Thread para buscar novos resultados automaticamente."""
    global pragmatic_integrator
    
    while True:
        try:
            if pragmatic_integrator:
                new_results = pragmatic_integrator.get_new_results()
                if new_results:
                    print(f"🎰 {len(new_results)} novos resultados da Pragmatic Play")
        except Exception as e:
            print(f"Erro no auto-fetch: {e}")
        
        time.sleep(30)  # Verificar a cada 30 segundos

# Iniciar thread
if pragmatic_integrator:
    threading.Thread(target=auto_fetch_pragmatic, daemon=True).start()
```

### 2. Atualizar Frontend
Adicionar botões no dashboard para:
- 🔄 Buscar resultados Pragmatic Play
- 📊 Ver estatísticas
- ⚡ Ativar/desativar polling automático

### 3. Configuração Dinâmica
Permitir usuário configurar:
- `table_id` (mesa específica)
- `session_id` (autenticação)
- Intervalo de polling
- Quantidade de resultados

---

## 🔐 Autenticação

A API da Pragmatic Play usa JSESSIONID para autenticação. O valor atual no código é:
```
6Dyk5pcHZ940gAb7TIUV2F_fHQ06A9wOcRC1-JD-Qu8e95yDHxiQ!1928883527-df6535db
```

**⚠️ Importante:** Este token pode expirar. Se começar a receber erros, você precisa:
1. Acessar a roleta da Pragmatic Play no navegador
2. Abrir DevTools (F12) → Network
3. Fazer uma requisição para `statisticHistory`
4. Copiar o novo JSESSIONID dos parâmetros da URL
5. Atualizar no código ou passar via API

---

## 🐛 Troubleshooting

### Erro: "Nenhum resultado obtido"
- ✅ Verificar se o `table_id` está correto
- ✅ Verificar se o `session_id` está válido
- ✅ Verificar conexão com internet
- ✅ Ver logs da API para mais detalhes

### Erro: "Integrador não inicializado"
- ✅ Fazer requisição POST para `/api/pragmatic/fetch` primeiro
- ✅ Ou inicializar manualmente no código

### Resultados antigos/desatualizados
- ✅ Usar `/api/pragmatic/new` para buscar apenas novos
- ✅ Ativar polling automático
- ✅ Verificar timestamp dos resultados

---

## 📝 Exemplo Completo

```python
from pragmatic_play_integrator import PragmaticPlayIntegrator

# Criar integrador
integrator = PragmaticPlayIntegrator(
    table_id="rwbrzportrwa16rg",
    session_id="SEU_JSESSIONID_AQUI"
)

# Buscar histórico
results = integrator.fetch_history(100)
print(f"{len(results)} resultados obtidos")

# Ver últimos 10
for r in results[:10]:
    print(f"{r['number']} ({r['color']})")

# Estatísticas
stats = integrator.get_statistics()
print(f"Vermelho: {stats['red_percentage']}%")
print(f"Preto: {stats['black_percentage']}%")

# Formatar para analyzer
formatted = integrator.format_for_analyzer(results)
```

---

## ✅ Status

- ✅ Integrador criado e testado
- ✅ Endpoints API implementados
- ✅ Formatação de dados para analyzer
- ✅ Cálculo de estatísticas
- ✅ Detecção de novos resultados
- ✅ Script de teste criado
- ⏳ Polling automático (próximo passo)
- ⏳ Interface frontend (próximo passo)

---

**🎉 A integração está pronta para uso!** Execute `python test_pragmatic_integration.py` para testar.
