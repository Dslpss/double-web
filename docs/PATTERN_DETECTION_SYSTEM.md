# 🎰 Sistema de Detecção de Padrões - Roleta Brasileira

## 📋 Visão Geral

Sistema híbrido profissional de detecção de padrões em tempo real para Roleta Brasileira, implementando análise em **duas fases**:

- **FASE 1 (JavaScript)**: Detecção básica instantânea no navegador
- **FASE 2 (Python)**: Análise avançada com testes estatísticos no servidor

---

## 🏗️ Arquitetura Implementada

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                        │
├─────────────────────────────────────────────────────────────┤
│  pattern-detector.js  →  Análise básica (5s)               │
│  alert-manager.js     →  Exibição de alertas               │
│  roulette-patterns.js →  Integração e controle             │
└─────────────────────────────────────────────────────────────┘
                              ↕
                         API REST
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                          │
├─────────────────────────────────────────────────────────────┤
│  roulette_analyzer.py →  Análise avançada (30s)           │
│  app.py               →  Rotas API                         │
│  Pragmatic Integrator →  Fonte de dados                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Arquivos Criados/Modificados

### ✅ ARQUIVOS CRIADOS

#### 1. **`static/js/pattern-detector.js`** (FASE 1 - JavaScript)

Detector de padrões básicos executado no navegador.

**Padrões Detectados:**

- ✅ **Sequências de Cor**: 5+ mesma cor consecutiva
- ✅ **Números Quentes**: 3+ aparições em 50 rodadas
- ✅ **Números Frios**: 30+ rodadas sem aparecer
- ✅ **Dominância de Dúzia**: 45%+ em uma dúzia (20 rodadas)
- ✅ **Desequilíbrio Par/Ímpar**: 65%+ em 20 rodadas
- ✅ **Repetições**: Número repetido imediatamente ou em 5 rodadas
- ✅ **Cluster de Vizinhos**: 3 números adjacentes na roda

**Classe Principal:**

```javascript
class PatternDetector {
    detectColorSequence(results, minLength=5)
    detectHotColdNumbers(results, lookback=50)
    detectDozenDominance(results, lookback=20)
    detectParityImbalance(results, lookback=20)
    detectRepetitions(results)
    detectNeighborCluster(results)
    getAllPatterns(results) // Interface unificada
}
```

---

#### 2. **`static/js/alert-manager.js`** (Sistema de Alertas)

Gerenciador visual de alertas de padrões.

**Funcionalidades:**

- ✅ Exibição de alertas com níveis de confiança (Low/Medium/High)
- ✅ Sistema de cores por confiança
- ✅ Auto-hide após 30 segundos
- ✅ Limite de 8 alertas simultâneos
- ✅ Animações de entrada/saída
- ✅ Notificações toast
- ✅ Som de alerta para alta confiança
- ✅ Estilos CSS injetados dinamicamente

**Classe Principal:**

```javascript
class AlertManager {
    showPattern(pattern)
    updateAlert(patternId, newPattern)
    removeAlert(patternId)
    clearAlerts()
    updateAlerts(patterns)
    showToast(message, type, duration)
    playAlertSound()
}
```

---

#### 3. **`static/js/roulette-patterns.js`** (Integração Principal)

Orquestrador do sistema híbrido.

**Responsabilidades:**

- ✅ Inicialização de componentes
- ✅ Polling de resultados (básico: 5s, avançado: 30s)
- ✅ Integração com APIs Flask
- ✅ Gerenciamento de configurações
- ✅ Notificações do navegador
- ✅ Modal de configurações

**API Pública:**

```javascript
window.roulettePatterns = {
    startDetection()
    stopDetection()
    checkStatus()
    getLastResults()
    showSettings()
    saveSettings()
}
```

---

#### 4. **`analyzers/roulette_analyzer.py`** (FASE 2 - Python)

Análise estatística avançada no servidor.

**Análises Implementadas:**

- ✅ **Análise de Setores**: Voisins, Tiers, Orphelins (teste chi-square)
- ✅ **Detecção de Bias**: Teste chi-square com 100+ resultados
- ✅ **Clusters Espaciais**: Análise de distância na roda física
- ✅ **Tendências Temporais**: Regressão linear em blocos de resultados
- ✅ **Estatísticas Completas**: Hot/cold numbers, setores, cores

**Classe Principal:**

```python
class RouletteAdvancedAnalyzer:
    analyze_sectors(results)          # Setor quente (p<0.05)
    detect_bias(results)              # Bias de roda (p<0.01)
    analyze_spatial_clusters(results) # Clusters físicos
    analyze_temporal_trends(results)  # Tendências temporais
    analyze_all_advanced_patterns(results)
    get_comprehensive_stats(results)
```

---

#### 5. **`app.py`** (Novas Rotas API)

**Rotas Criadas:**

```python
GET /api/roulette/patterns/basic
    → Retorna resultados formatados (cache 5s)
    → Usado pelo detector JavaScript

GET /api/roulette/patterns/advanced
    → Executa análise Python avançada (cache 30s)
    → Retorna padrões + estatísticas

GET /api/roulette/patterns/all
    → Consolida basic + advanced
    → Interface unificada
```

---

#### 6. **`templates/roulette.html`** (HTML Limpo)

**Mudanças:**

- ❌ **REMOVIDO**: Todo JavaScript inline (>400 linhas)
- ✅ **ADICIONADO**: Card de alertas de padrões
- ✅ **ADICIONADO**: Modal de configurações
- ✅ **ADICIONADO**: CSS para sistema de padrões
- ✅ **ADICIONADO**: Imports de scripts externos

**Novo Card:**

```html
<div class="card card-full-width">
  <h2>🎯 Alertas de Padrões em Tempo Real</h2>
  <div id="pattern-alerts">
    <!-- Alertas inseridos dinamicamente -->
  </div>
</div>
```

---

#### 7. **`analyzers/__init__.py`**

Arquivo de inicialização do módulo.

---

#### 8. **`requirements.txt`**

- ✅ Adicionado: `scipy>=1.10.0` (testes estatísticos)

---

## 🔍 Padrões Detectados

### 📊 FASE 1 - Básico (JavaScript)

| Padrão                      | Descrição         | Confiança | Lookback   |
| --------------------------- | ----------------- | --------- | ---------- |
| **Sequência de Cor**        | 5+ mesma cor      | 50-70%    | Últimos N  |
| **Números Quentes**         | 3+ aparições      | 55-75%    | 50 rodadas |
| **Números Frios**           | 30+ sem aparecer  | 40-65%    | Todas      |
| **Dominância Dúzia**        | 45%+ em uma dúzia | 55-75%    | 20 rodadas |
| **Desequilíbrio Par/Ímpar** | 65%+ mesmo tipo   | 55-75%    | 20 rodadas |
| **Repetições**              | Repetido em ≤5    | 50-70%    | Últimas 10 |
| **Cluster Vizinhos**        | 3 adjacentes      | 60-80%    | Últimas 15 |

### 🔬 FASE 2 - Avançado (Python)

| Padrão                 | Descrição       | Teste Estatístico   | Confiança |
| ---------------------- | --------------- | ------------------- | --------- |
| **Setor Quente**       | 45%+ em setor   | Chi-square (p<0.05) | 55-80%    |
| **Bias de Roda**       | Desvio >50%     | Chi-square (p<0.01) | 70-90%    |
| **Cluster Espacial**   | Distância <60%  | Análise distância   | 60-78%    |
| **Tendência Temporal** | Slope >5%/bloco | Regressão linear    | 50-68%    |

---

## ⚙️ Configurações

**Intervalos de Atualização:**

- Análise Básica (JS): **5 segundos** (ajustável: 3-30s)
- Análise Avançada (Python): **30 segundos** (ajustável: 10-120s)

**Alertas:**

- Som: Padrões com confiança ≥70%
- Notificação Browser: Padrões com confiança ≥80%
- Auto-hide: 30 segundos (exceto críticos)
- Máximo simultâneo: 8 alertas

---

## 🎨 Interface

**Níveis de Confiança:**

- 🔴 **Alta (70%+)**: Vermelho, borda vermelha
- 🟠 **Média (55-70%)**: Laranja, borda laranja
- 🔵 **Baixa (45-55%)**: Azul, borda azul

**Card de Alerta:**

```
┌─────────────────────────────────────────┐
│ 🎯 Setor Quente: Vizinhos do Zero  [75%]│
│ ─────────────────────────────────────── │
│ Descrição do padrão detectado...        │
│ 💡 Sugestão: Apostar nos números: ...   │
│ ─────────────────────────────────────── │
│ Chi-square: 12.34 | P-value: 0.0023     │
└─────────────────────────────────────────┘
```

---

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar Servidor

```bash
python app.py
```

### 3. Acessar Interface

```
http://localhost:5000/roulette
```

### 4. Iniciar Monitoramento

- Clicar em "▶ Iniciar Monitoramento"
- Sistema começa a detectar padrões automaticamente
- Alertas aparecem no card "🎯 Alertas de Padrões"

---

## 🔄 Fluxo de Dados

```
1. Pragmatic Integrator coleta resultados
           ↓
2. Flask armazena em banco de dados
           ↓
3. API /patterns/basic fornece dados (5s)
           ↓
4. JavaScript detecta padrões básicos
           ↓
5. AlertManager exibe alertas
           ↓
6. API /patterns/advanced analisa (30s)
           ↓
7. Python detecta padrões avançados
           ↓
8. AlertManager exibe alertas avançados
```

---

## 📈 Próximas Fases (FASE 3 - ML)

**Planejado para futuro:**

- 🔮 **Predição ML**: Usar histórico para prever próximo número
- 🧠 **Modelos**: Random Forest, LSTM, XGBoost
- 📊 **Features**: Padrões históricos + tendências
- ⏱️ **Atualização**: 2 minutos
- 🎯 **Confiança**: 30-60% (limitação inerente da roleta)

---

## ✅ Status de Implementação

- [x] **Fase 1**: Detecção básica JavaScript (✅ COMPLETO)
- [x] **Fase 2**: Análise avançada Python (✅ COMPLETO)
- [x] **Sistema de Alertas** (✅ COMPLETO)
- [x] **Integração Híbrida** (✅ COMPLETO)
- [x] **Interface Visual** (✅ COMPLETO)
- [x] **Rotas API** (✅ COMPLETO)
- [x] **Configurações** (✅ COMPLETO)
- [ ] **Fase 3**: Machine Learning (❌ PENDENTE)

---

## 🎯 Resultado Final

✅ **Sistema profissional híbrido** sem JavaScript inline  
✅ **Arquitetura escalável** e manutenível  
✅ **Detecção em tempo real** com análise estatística  
✅ **Interface moderna** com alertas visuais  
✅ **Código limpo** separado por responsabilidade

**Total de arquivos criados**: 6  
**Total de linhas de código**: ~2.500+  
**Tecnologias**: JavaScript ES6, Python 3.x, Flask, NumPy, SciPy

---

## 📝 Observações Importantes

1. **Limitações da Roleta**:

   - Roletas honestas são aleatórias
   - Padrões passados NÃO garantem resultados futuros
   - Sistema é para análise, não garantia

2. **Uso Responsável**:

   - Ferramenta educacional e analítica
   - Não substitui estratégia de jogo responsável
   - Sempre aposte com consciência

3. **Performance**:
   - JavaScript é instantâneo
   - Python executa análises pesadas em background
   - Cache evita sobrecarga do servidor

---

**Desenvolvido com ❤️ por GitHub Copilot**
