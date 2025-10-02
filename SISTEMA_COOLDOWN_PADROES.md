# Sistema de Cooldown para Padrões - Blaze Double Analyzer

## Problema Identificado

O sistema estava enviando alertas para **todas as próximas jogadas** após detectar um padrão, causando spam de notificações. Isso é incorreto porque:

- Um padrão detectado deve gerar **apenas uma recomendação**
- Não deve repetir o mesmo alerta para jogadas subsequentes
- O sistema precisa "esfriar" antes de detectar o mesmo tipo de padrão novamente

## Solução Implementada

### Sistema de Cooldown por Tipo de Padrão

Cada tipo de padrão tem seu próprio cooldown independente:

```python
pattern_cooldowns = {
    'dominance': 300,      # 5 minutos para padrões de dominância
    'sequence': 180,      # 3 minutos para sequências
    'alternation': 120,   # 2 minutos para alternância
    'hot_cold': 240,      # 4 minutos para números quentes/frios
    'default': 300        # 5 minutos para outros padrões
}
```

### Como Funciona

1. **Detecção de Padrão**: Quando um padrão é detectado
2. **Verificação de Cooldown**: Sistema verifica se já foi notificado recentemente
3. **Bloqueio ou Envio**: Se em cooldown, bloqueia; senão, envia notificação
4. **Atualização de Cooldown**: Após enviar, atualiza o tempo da última notificação

### Fluxo de Funcionamento

```
Padrão Detectado → Verificar Cooldown → Em Cooldown? → SIM: Bloquear
                                    ↓
                                   NÃO: Enviar Notificação → Atualizar Cooldown
```

## Configuração

### Tempos de Cooldown Recomendados

- **Padrões de Dominância**: 5 minutos (padrões mais importantes)
- **Sequências**: 3 minutos (padrões de média importância)
- **Alternância**: 2 minutos (padrões mais frequentes)
- **Números Quentes/Frios**: 4 minutos (padrões de análise)

### Personalização

```python
# No arquivo de configuração
cooldown_duration = 300  # Cooldown global padrão (segundos)
pattern_cooldowns = {
    'dominance': 300,     # Personalizar por tipo
    'sequence': 180,
    # ... outros padrões
}
```

## API Endpoints

### Verificar Status dos Cooldowns

```http
GET /api/notifications/cooldown/status
```

**Resposta:**

```json
{
  "success": true,
  "cooldown_status": {
    "active_cooldowns": {
      "dominance": {
        "remaining_time": 120.5,
        "cooldown_duration": 300,
        "last_notification": 1640995200.0
      }
    },
    "total_active": 1,
    "cooldown_config": {
      "dominance": 300,
      "sequence": 180,
      "default": 300
    }
  }
}
```

### Limpar Cooldowns

```http
POST /api/notifications/cooldown/clear
Content-Type: application/json

{
    "pattern_type": "dominance"  // Opcional - None limpa todos
}
```

**Resposta:**

```json
{
  "success": true,
  "message": "Cooldown limpo",
  "pattern_type": "dominance"
}
```

## Benefícios

### ✅ Problemas Resolvidos

1. **Fim do Spam**: Não mais alertas repetitivos
2. **Recomendações Precisas**: Uma recomendação por padrão detectado
3. **Sistema Inteligente**: Cooldowns específicos por tipo de padrão
4. **Controle Manual**: API para gerenciar cooldowns

### ✅ Melhorias na Experiência

1. **Notificações Relevantes**: Apenas quando necessário
2. **Menos Ruído**: Interface mais limpa
3. **Maior Confiança**: Usuário confia mais nas recomendações
4. **Flexibilidade**: Configurável por tipo de padrão

## Monitoramento

### Logs do Sistema

```
🔔 PatternNotifier inicializado - Cooldown: 300s
⏰ Padrão 'dominance' em cooldown - 120s restantes
✅ Cooldown limpo para padrão: dominance
```

### Status em Tempo Real

O sistema mostra:

- Quais padrões estão em cooldown
- Tempo restante para cada cooldown
- Configurações ativas

## Exemplo de Uso

### Cenário: Padrão de Dominância Detectado

1. **Detecção**: Sistema detecta dominância de vermelho (8/10 últimas jogadas)
2. **Notificação**: Envia alerta "Aposte em preto - regressão à média"
3. **Cooldown**: Bloqueia novos alertas de dominância por 5 minutos
4. **Próximas Jogadas**: Sistema continua analisando mas não envia alertas de dominância
5. **Liberação**: Após 5 minutos, pode detectar nova dominância

### Resultado

- ✅ **Antes**: 10 alertas de dominância em 5 minutos
- ✅ **Depois**: 1 alerta de dominância a cada 5 minutos

## Configuração Avançada

### Cooldowns Dinâmicos

```python
# Baseado na confiança do padrão
def get_dynamic_cooldown(pattern_type, confidence):
    base_cooldown = pattern_cooldowns.get(pattern_type, 300)

    # Padrões com alta confiança têm cooldown maior
    if confidence > 0.8:
        return base_cooldown * 1.5
    elif confidence < 0.5:
        return base_cooldown * 0.7

    return base_cooldown
```

### Cooldowns por Contexto

```python
# Cooldowns baseados no contexto do jogo
def get_contextual_cooldown(pattern_type, game_context):
    if game_context.get('high_volatility'):
        return pattern_cooldowns[pattern_type] * 0.5  # Cooldown menor em alta volatilidade

    return pattern_cooldowns[pattern_type]
```

## Conclusão

O sistema de cooldown resolve completamente o problema de spam de alertas, tornando o sistema mais inteligente e confiável. Agora cada padrão detectado gera apenas uma recomendação relevante, melhorando significativamente a experiência do usuário.

---

**Implementado em**: `shared/src/notifications/pattern_notifier.py`  
**API Endpoints**: `/api/notifications/cooldown/*`  
**Status**: ✅ **FUNCIONANDO**
