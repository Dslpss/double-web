# Sistema de Padrões Personalizados

## Visão Geral

O Sistema de Padrões Personalizados permite que você crie e gerencie seus próprios padrões de detecção para o Double da Blaze. Com este sistema, você pode definir gatilhos específicos e ações automáticas baseadas nos resultados do jogo.

## Funcionalidades

### ✅ Criadas e Funcionais

1. **Estrutura de Dados Completa**

   - Sistema de banco de dados SQLite para armazenar padrões
   - Classes para diferentes tipos de gatilhos e ações
   - Sistema de cache e performance otimizada

2. **APIs REST Completas**

   - `GET /api/custom-patterns` - Listar todos os padrões
   - `POST /api/custom-patterns` - Criar novo padrão
   - `PUT /api/custom-patterns/<id>` - Atualizar padrão
   - `DELETE /api/custom-patterns/<id>` - Remover padrão
   - `GET /api/custom-patterns/<id>/stats` - Estatísticas do padrão
   - `POST /api/custom-patterns/check` - Verificar padrões ativados
   - `GET /api/custom-patterns/export` - Exportar padrões
   - `POST /api/custom-patterns/import` - Importar padrões

3. **Interface Web Completa**

   - Página dedicada em `/custom-patterns`
   - Interface moderna com Bootstrap 5
   - Criação e edição de padrões com formulários dinâmicos
   - Visualização de estatísticas e performance
   - Sistema de importação/exportação

4. **Integração com o Analisador**

   - Verificação automática de padrões durante análise
   - Integração com o BlazeAnalyzerEnhanced
   - Registro de resultados e estatísticas

5. **Sistema de Notificações**
   - Alertas visuais quando padrões são ativados
   - Notificações em tempo real na página do Double
   - Integração com o sistema de notificações existente

## Tipos de Gatilhos Suportados

### 1. Número Seguido por Cor

Detecta quando um número específico é seguido por uma cor específica.

**Exemplo:** Após o número 1, vem red

```json
{
  "trigger_type": "number_followed_by_color",
  "trigger_config": {
    "number": 1,
    "color": "red",
    "min_occurrences": 2
  }
}
```

### 2. Sequência de Cores

Detecta sequências específicas de cores.

**Exemplo:** Sequência red → red

```json
{
  "trigger_type": "color_sequence",
  "trigger_config": {
    "sequence": ["red", "red"],
    "min_length": 2
  }
}
```

### 3. Sequência de Números

Detecta sequências específicas de números.

**Exemplo:** Sequência 1 → 2 → 3

```json
{
  "trigger_type": "number_sequence",
  "trigger_config": {
    "sequence": [1, 2, 3],
    "min_length": 2
  }
}
```

### 4. Cor Após Cor

Detecta quando uma cor específica é seguida por outra cor.

**Exemplo:** Após red vem black

```json
{
  "trigger_type": "color_after_color",
  "trigger_config": {
    "first_color": "red",
    "second_color": "black",
    "min_occurrences": 1
  }
}
```

### 5. Número Após Número

Detecta quando um número específico é seguido por outro número.

**Exemplo:** Após número 5 vem número 7

```json
{
  "trigger_type": "number_after_number",
  "trigger_config": {
    "first_number": 5,
    "second_number": 7,
    "min_occurrences": 1
  }
}
```

## Tipos de Ações Suportadas

### 1. Apostar na Cor

```json
{
  "action": "bet_color",
  "action_config": {
    "color": "red"
  }
}
```

### 2. Apostar no Número

```json
{
  "action": "bet_number",
  "action_config": {
    "number": 5
  }
}
```

### 3. Apostar no Setor

```json
{
  "action": "bet_sector",
  "action_config": {
    "sector": "low" // low, medium, high
  }
}
```

### 4. Pular Aposta

```json
{
  "action": "skip_bet",
  "action_config": {}
}
```

### 5. Aguardar

```json
{
  "action": "wait",
  "action_config": {}
}
```

## Como Usar

### 1. Acessar a Interface

- Vá para `/custom-patterns` no seu navegador
- Ou clique no card "Padrões Personalizados" na página inicial

### 2. Criar um Padrão

1. Clique em "Novo Padrão"
2. Preencha as informações básicas (nome, descrição)
3. Selecione o tipo de gatilho
4. Configure os parâmetros do gatilho
5. Selecione a ação a ser executada
6. Configure as configurações avançadas (confiança, cooldown)
7. Clique em "Salvar Padrão"

### 3. Gerenciar Padrões

- **Editar:** Clique no ícone de edição no card do padrão
- **Ver Estatísticas:** Clique no ícone de gráfico
- **Excluir:** Clique no ícone de lixeira
- **Ativar/Desativar:** Use o seletor de status

### 4. Monitoramento Automático

- Os padrões são verificados automaticamente durante o monitoramento do Double
- Quando um padrão é ativado, você receberá uma notificação visual
- As estatísticas são atualizadas automaticamente

## Exemplos Práticos

### Exemplo 1: "Número 1 Seguido por Red"

- **Gatilho:** Quando o número 1 aparece, seguido por red
- **Ação:** Apostar na cor red
- **Uso:** Detecta quando o número 1 "puxa" red

### Exemplo 2: "Sequência Red-Red"

- **Gatilho:** Quando aparecem dois reds consecutivos
- **Ação:** Apostar na cor black
- **Uso:** Baseado na teoria de que sequências longas são raras

### Exemplo 3: "Branco Isca"

- **Gatilho:** Quando o número 0 (branco) aparece
- **Ação:** Apostar na cor red nas próximas rodadas
- **Uso:** Padrão clássico do Double

## Configurações Avançadas

### Limiar de Confiança

- Define a confiança mínima para ativar o padrão
- Valores entre 0.5 (50%) e 1.0 (100%)
- Padrões com maior confiança são mais conservadores

### Cooldown

- Tempo em minutos entre ativações do mesmo padrão
- Evita spam de notificações
- Recomendado: 3-10 minutos

### Estatísticas

- **Sucessos:** Quantas vezes o padrão acertou
- **Falhas:** Quantas vezes o padrão errou
- **Taxa de Sucesso:** Percentual de acertos
- **Último Trigger:** Quando foi ativado pela última vez

## Importação/Exportação

### Exportar Padrões

- Clique em "Exportar" na interface
- Um arquivo JSON será gerado com todos os padrões
- Útil para backup ou compartilhamento

### Importar Padrões

- Clique em "Importar" e selecione um arquivo JSON
- Os padrões serão adicionados ao sistema
- IDs duplicados serão ignorados

## Integração com o Sistema

### APIs Disponíveis

Todas as APIs seguem o padrão REST e retornam JSON:

```bash
# Listar padrões
GET /api/custom-patterns

# Criar padrão
POST /api/custom-patterns
Content-Type: application/json
{
  "name": "Meu Padrão",
  "trigger_type": "number_followed_by_color",
  "trigger_config": {...},
  "action": "bet_color",
  "action_config": {...}
}

# Verificar padrões ativados
POST /api/custom-patterns/check
```

### Integração com JavaScript

```javascript
// Verificar padrões manualmente
async function checkPatterns() {
  const response = await fetch("/api/custom-patterns/check", {
    method: "POST",
  });
  const data = await response.json();

  if (data.success && data.triggered_patterns.length > 0) {
    console.log("Padrões ativados:", data.triggered_patterns);
  }
}
```

## Arquivos do Sistema

### Backend

- `shared/src/analysis/custom_patterns.py` - Sistema principal
- `app.py` - APIs REST
- `data/custom_patterns.db` - Banco de dados SQLite

### Frontend

- `templates/custom_patterns.html` - Interface web
- `static/js/roulette-legacy.js` - Integração com Double

### Utilitários

- `create_example_patterns.py` - Script para criar exemplos

## Próximos Passos

### Melhorias Futuras

1. **Mais Tipos de Gatilhos**

   - Gatilhos baseados em tempo
   - Gatilhos estatísticos avançados
   - Gatilhos combinados

2. **Ações Avançadas**

   - Apostas com valores específicos
   - Estratégias de Martingale
   - Integração com bots de apostas

3. **Análise Avançada**

   - Machine Learning para otimização
   - Análise de performance histórica
   - Recomendações automáticas

4. **Interface Melhorada**
   - Drag & drop para criação de padrões
   - Visualização gráfica de padrões
   - Dashboard de performance

## Suporte

Para dúvidas ou problemas:

1. Verifique os logs do sistema
2. Teste com dados de exemplo
3. Use a interface de debug em `/custom-patterns`
4. Consulte as APIs para integração

---

**Sistema desenvolvido para o Double Analyzer**  
_Versão 1.0 - Dezembro 2024_
