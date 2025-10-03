# 🎯 Guia de Uso - Sistema de Detecção de Padrões

## 📖 Como Usar o Sistema

### 1️⃣ **Iniciar o Servidor**

```bash
cd /d/Projetos/double-web
python app.py
```

### 2️⃣ **Acessar a Interface**

Abra seu navegador em:

```
http://localhost:5000/roulette
```

### 3️⃣ **Iniciar Monitoramento**

1. Na interface, clique no botão **"▶ Iniciar Monitoramento"**
2. O sistema começará a coletar resultados da Roleta Brasileira
3. Aguarde alguns segundos até os primeiros resultados aparecerem

### 4️⃣ **Observar Alertas de Padrões**

Os alertas aparecerão automaticamente no card:

```
🎯 Alertas de Padrões em Tempo Real
```

**Tipos de Alertas:**

#### 🔴 **Alta Confiança (70%+)** - Vermelho

- Padrões muito fortes
- Som de alerta automático
- Exemplos:
  - Setor quente com teste chi-square significativo
  - Bias de roda detectado
  - Cluster espacial muito concentrado

#### 🟠 **Média Confiança (55-70%)** - Laranja

- Padrões moderados
- Alertas visuais
- Exemplos:
  - Dominância de dúzia
  - Desequilíbrio par/ímpar
  - Números quentes

#### 🔵 **Baixa Confiança (45-55%)** - Azul

- Padrões fracos
- Apenas informativo
- Exemplos:
  - Sequências curtas de cor
  - Números frios
  - Tendências iniciais

---

## 🎛️ **Configurações**

Clique no botão **"⚙️ Config"** para ajustar:

### Opções Disponíveis:

1. **🔊 Alertas Sonoros**

   - Ativa/desativa som para alertas de alta confiança
   - Padrão: Ativado

2. **🔔 Notificações do Navegador**

   - Ativa/desativa notificações do browser para padrões críticos (80%+)
   - Padrão: Ativado
   - **Nota**: Primeira vez pedirá permissão

3. **⏱️ Intervalo Análise Básica**

   - Frequência de análise JavaScript (padrões simples)
   - Padrão: 5 segundos
   - Recomendado: 3-10 segundos

4. **⏱️ Intervalo Análise Avançada**
   - Frequência de análise Python (estatística complexa)
   - Padrão: 30 segundos
   - Recomendado: 20-60 segundos

---

## 📊 **Entendendo os Padrões**

### 🎨 **PADRÕES BÁSICOS** (JavaScript - Detecção Instantânea)

#### 1. **Sequência de Cor** 🔴🔴🔴🔴🔴

```
Descrição: 5 ou mais resultados da mesma cor consecutivos
Confiança: 50-70%
Sugestão: Apostar na cor contrária (Martingale reverso)
```

#### 2. **Números Quentes** 🔥

```
Descrição: Número apareceu 3+ vezes em 50 rodadas
Confiança: 55-75%
Sugestão: Apostar nos números mais frequentes
Exemplo: "Número 7 apareceu 5 vezes em 50 giros"
```

#### 3. **Números Frios** ❄️

```
Descrição: Número não aparece há 30+ rodadas
Confiança: 40-65%
Sugestão: Considerar apostar (Lei dos Grandes Números)
Exemplo: "Número 32 não aparece há 45 giros"
```

#### 4. **Dominância de Dúzia** 🎲

```
Descrição: Uma dúzia (1-12, 13-24, 25-36) representa 45%+ dos resultados
Confiança: 55-75%
Sugestão: Apostar na dúzia dominante
Exemplo: "1ª Dúzia: 9/20 resultados (45%)"
```

#### 5. **Desequilíbrio Par/Ímpar** ⚖️

```
Descrição: 65%+ de pares ou ímpares em 20 rodadas
Confiança: 55-75%
Sugestão: Apostar no tipo dominante ou aguardar correção
Exemplo: "Par: 14/20 (70%)"
```

#### 6. **Repetições** 🔁

```
Descrição: Número repetido imediatamente ou dentro de 5 rodadas
Confiança: 50-70%
Sugestão: Observar padrão de repetições
Exemplo: "Número 18 repetiu após 2 giros"
```

#### 7. **Cluster de Vizinhos** 🎪

```
Descrição: 3 números adjacentes na roda física saíram próximos
Confiança: 60-80%
Sugestão: Apostar em vizinhos do cluster
Exemplo: "Números 32, 15, 19 (vizinhos) em sequência"
```

---

### 🔬 **PADRÕES AVANÇADOS** (Python - Análise Estatística)

#### 1. **Setor Quente** 🎯

```
Descrição: Setor da roda (Voisins/Tiers/Orphelins) com 45%+ dos resultados
Teste: Chi-square (p < 0.05)
Confiança: 55-80%
Sugestão: Apostar nos números do setor
Setores:
  • Voisins du Zero: 22,18,29,7,28,12,35,3,26,0,32,15,19,4,21,2,25
  • Tiers du Cylindre: 27,13,36,11,30,8,23,10,5,24,16,33
  • Orphelins: 17,34,6,1,20,14,31,9
```

#### 2. **BIAS DE RODA** ⚠️ (CRÍTICO)

```
Descrição: Números com desvio estatístico >50% do esperado
Teste: Chi-square (p < 0.01)
Confiança: 70-90%
Sugestão: APOSTAR PESADO nos números com bias
Nota: Requer 100+ resultados para confiabilidade
Exemplo: "Número 7 apareceu 8 vezes (esperado: 4.05)"
```

#### 3. **Cluster Espacial** 🎡

```
Descrição: Resultados concentrados em região específica da roda
Análise: Distância média entre números < 60% do esperado
Confiança: 60-78%
Sugestão: Apostar em região quente da roda
Exemplo: "Distância média: 11 posições (esperado: 18.5)"
```

#### 4. **Tendência Temporal** 📈📉

```
Descrição: Tendência crescente/decrescente de vermelho ao longo do tempo
Análise: Regressão linear em blocos de 10 rodadas
Confiança: 50-68%
Sugestão: Seguir a tendência
Exemplo: "Vermelho crescendo +6% por bloco"
```

---

## 🎮 **Estratégias Sugeridas**

### 🏆 **Para Padrões de Alta Confiança (70%+)**

1. **Setor Quente + Chi-square**

   ```
   ✅ Cobrir todos os números do setor
   ✅ Apostar fichas maiores
   ✅ Manter por 10-20 rodadas
   ```

2. **Bias de Roda**

   ```
   ✅ FOCO TOTAL nos números com bias
   ✅ Sistema Martingale moderado
   ✅ Continuar até bias desaparecer
   ```

3. **Cluster de Vizinhos**
   ```
   ✅ Apostar nos 3 vizinhos detectados
   ✅ Adicionar vizinhos imediatos (±1 na roda)
   ✅ Cobrir 7-9 números
   ```

### 🎲 **Para Padrões de Média Confiança (55-70%)**

1. **Números Quentes**

   ```
   ⚠️ Apostar pequenas fichas nos top 3
   ⚠️ Combinar com setor
   ⚠️ Máximo 5 números simultâneos
   ```

2. **Dominância de Dúzia**
   ```
   ⚠️ Apostar na dúzia dominante
   ⚠️ Proteção na segunda dúzia mais frequente
   ⚠️ Progressão conservadora
   ```

### 📊 **Para Padrões de Baixa Confiança (45-55%)**

```
ℹ️ OBSERVAR apenas
ℹ️ Não aumentar apostas
ℹ️ Aguardar confirmação com alta confiança
```

---

## ⚠️ **AVISOS IMPORTANTES**

### 🎰 **Sobre a Roleta**

1. **Aleatoriedade**

   - Roletas honestas são ALEATÓRIAS
   - Padrões passados NÃO garantem futuros
   - Casa SEMPRE tem vantagem (2.7% na europeia)

2. **Uso do Sistema**

   - Ferramenta ANALÍTICA e EDUCACIONAL
   - NÃO é garantia de lucro
   - Use para ESTUDO de padrões

3. **Jogo Responsável**
   - Aposte apenas o que pode perder
   - Defina limites de perda
   - Nunca tente "recuperar" perdas

### 🔬 **Sobre Estatísticas**

1. **Significância Estatística**

   - P-value < 0.05 = 95% de confiança
   - P-value < 0.01 = 99% de confiança
   - Quanto menor o p-value, mais significativo

2. **Tamanho da Amostra**

   - Bias: Requer 100+ resultados
   - Setores: Mínimo 20 resultados
   - Tendências: Mínimo 50 resultados

3. **Variância**
   - Desvios são NORMAIS em amostras pequenas
   - Lei dos Grandes Números atua no LONGO PRAZO
   - Evite conclusões precipitadas

---

## 🆘 **Solução de Problemas**

### ❌ **Sistema não detecta padrões**

```
Possíveis causas:
1. Poucos resultados coletados (aguarde 20+)
2. Resultados muito aleatórios (normal)
3. Integrador offline (verificar status)

Solução:
→ Aguardar mais tempo
→ Verificar botão "Iniciar Monitoramento"
→ Verificar console do navegador (F12)
```

### 🔇 **Sons não tocam**

```
Solução:
→ Verificar se navegador permite som
→ Ativar nas configurações (⚙️)
→ Aumentar volume do sistema
```

### 🔔 **Notificações não aparecem**

```
Solução:
→ Permitir notificações no navegador
→ Verificar configurações do sistema
→ Ativar nas configurações (⚙️)
```

### 🐌 **Sistema lento**

```
Solução:
→ Aumentar intervalos de atualização
→ Fechar outras abas do navegador
→ Verificar uso de CPU/Memória
```

---

## 📱 **Atalhos de Teclado**

```
Ctrl + C     → Limpar alertas
Ctrl + ,     → Abrir configurações
Esc          → Fechar modal
F5           → Recarregar (perde histórico)
F12          → Console do desenvolvedor (debug)
```

---

## 🎓 **Dicas Avançadas**

### 1. **Combine Múltiplos Padrões**

```
✅ Setor Quente + Números Quentes do setor
✅ Cluster + Bias no mesmo número
✅ Tendência Temporal + Dominância de Cor
```

### 2. **Use Stop-Loss e Stop-Win**

```
Stop-Loss:  Pare se perder 30% do bankroll
Stop-Win:   Pare se ganhar 50% do bankroll inicial
```

### 3. **Monitore por Sessão**

```
Sessão = 1-2 horas de jogo
Reinicie análise a cada nova sessão
Bias pode mudar entre sessões
```

### 4. **Registre Seus Resultados**

```
Anote padrões que funcionaram
Calcule ROI (Return on Investment)
Ajuste estratégia baseado em dados
```

---

## 📞 **Suporte**

**Problemas técnicos:**

- Verifique console do navegador (F12 → Console)
- Verifique logs do Flask no terminal
- Leia `PATTERN_DETECTION_SYSTEM.md`

**Dúvidas sobre estratégias:**

- Sistema é apenas analítico
- Busque conhecimento sobre gestão de banca
- Estude probabilidade e estatística

---

## 🎉 **Resumo Rápido**

```
1. Iniciar servidor:     python app.py
2. Abrir navegador:      http://localhost:5000/roulette
3. Clicar:               ▶ Iniciar Monitoramento
4. Observar:             🎯 Alertas de Padrões
5. Configurar:           ⚙️ Config (opcional)
6. Apostar:              Seguir sugestões de alta confiança
7. Parar:                ⏹ Parar
```

---

**Boa sorte e jogue com responsabilidade! 🍀🎰**
