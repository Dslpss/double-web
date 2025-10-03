// ==================== PATTERN DETECTOR - FASE 1 (BÁSICO) ====================
// Detecção rápida de padrões no navegador para resposta instantânea

class RoulettePatternDetector {
  constructor() {
    this.ROULETTE_SECTORS = {
      voisins: [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25],
      tiers: [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33],
      orphelins: [17, 34, 6, 1, 20, 14, 31, 9],
    };

    this.WHEEL_ORDER = [
      0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
      24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
    ];
  }

  // ==================== DETECÇÃO DE PADRÕES ====================

  /**
   * Detecta todos os padrões básicos (Fase 1)
   * @param {Array} results - Array de resultados da roleta
   * @returns {Array} - Array de alertas detectados
   */
  detectAllPatterns(results) {
    if (!results || results.length < 10) {
      return [];
    }

    const alerts = [];

    // Detectar todos os padrões básicos
    alerts.push(this.detectColorSequence(results));
    alerts.push(this.detectAlternatingPattern(results));
    alerts.push(this.detectColorDominance(results));
    alerts.push(this.detectParityImbalance(results));
    alerts.push(this.detectHotNumbers(results));
    alerts.push(this.detectColdNumbers(results));
    alerts.push(this.detectHotDozen(results));
    alerts.push(this.detectHotColumn(results));
    alerts.push(this.detectRepeatPattern(results));
    alerts.push(this.detectNeighborsPattern(results));

    // Filtrar apenas os padrões encontrados
    return alerts.filter((alert) => alert !== null);
  }

  // ==================== 1. SEQUÊNCIA DE COR ====================

  detectColorSequence(results) {
    let streak = 1;
    let currentColor = results[0].color;

    for (let i = 1; i < Math.min(results.length, 10); i++) {
      if (results[i].color === currentColor) {
        streak++;
      } else {
        break;
      }
    }

    if (streak >= 6) {
      const colorName = this.getColorName(currentColor);
      const oppositeColor = this.getOppositeColor(currentColor);
      const confidence = Math.min(45 + (streak - 6) * 3, 60);

      return {
        id: "color-sequence",
        type: "basic",
        confidence: confidence,
        priority: streak * 2,
        icon: "🔴⚫",
        title: `Sequência de ${streak} ${colorName}s`,
        description: `Detectada sequência de ${streak} resultados ${colorName} consecutivos. Embora cada rodada seja independente, alguns jogadores apostam na cor oposta após longas sequências.`,
        suggestion: `Considere apostar em ${oppositeColor}`,
        data: {
          Sequência: `${streak} resultados`,
          Cor: colorName,
          "Ativo há": `${streak} rodadas`,
        },
      };
    }
    return null;
  }

  // ==================== 2. PADRÃO ALTERNADO ====================

  detectAlternatingPattern(results) {
    if (results.length < 6) return null;

    let alternating = true;
    let patternLength = 1;

    for (let i = 0; i < Math.min(results.length - 1, 8); i++) {
      if (results[i].color !== results[i + 1].color) {
        patternLength++;
      } else {
        alternating = false;
        break;
      }
    }

    if (alternating && patternLength >= 6) {
      const confidence = Math.min(45 + patternLength * 2, 58);
      const sequence = results
        .slice(0, patternLength)
        .map((r) => this.getColorSymbol(r.color))
        .join("-");

      return {
        id: "alternating-pattern",
        type: "basic",
        confidence: confidence,
        priority: patternLength * 1.5,
        icon: "🔄",
        title: `Padrão Alternado Detectado`,
        description: `Detectado padrão de alternância de cores por ${patternLength} rodadas consecutivas (${sequence}). Padrões alternados podem continuar ou quebrar a qualquer momento.`,
        suggestion: `Apostar na cor oposta à última se o padrão continuar`,
        data: {
          Comprimento: `${patternLength} rodadas`,
          Padrão: sequence,
          Tipo: "Alternância",
        },
      };
    }
    return null;
  }

  // ==================== 3. DOMINÂNCIA DE COR ====================

  detectColorDominance(results) {
    const last20 = results.slice(0, Math.min(20, results.length));
    if (last20.length < 15) return null;

    const colorCounts = { red: 0, black: 0, green: 0 };
    last20.forEach((r) => colorCounts[r.color]++);

    const total = last20.length;
    const redPerc = (colorCounts.red / total) * 100;
    const blackPerc = (colorCounts.black / total) * 100;

    if (redPerc >= 75 || blackPerc >= 75) {
      const dominantColor = redPerc > blackPerc ? "red" : "black";
      const percentage = Math.max(redPerc, blackPerc);
      const confidence = Math.min(50 + (percentage - 75) * 1.5, 70);
      const colorName = this.getColorName(dominantColor);

      return {
        id: "color-dominance",
        type: "basic",
        confidence: confidence,
        priority: percentage / 2,
        icon: "🎨",
        title: `Dominância de Cor: ${colorName}`,
        description: `Cor ${colorName} domina com ${
          colorCounts[dominantColor]
        } de ${total} resultados (${percentage.toFixed(
          1
        )}%). Isso representa um desvio significativo da distribuição esperada.`,
        suggestion: `Pode apostar em ${colorName} ou aguardar reversão`,
        data: {
          Cor: colorName,
          Aparições: `${colorCounts[dominantColor]}/${total}`,
          Porcentagem: `${percentage.toFixed(1)}%`,
        },
      };
    }
    return null;
  }

  // ==================== 4. DESEQUILÍBRIO DE PARIDADE ====================

  detectParityImbalance(results) {
    const last20 = results.slice(0, Math.min(20, results.length));
    if (last20.length < 15) return null;

    let evenCount = 0;
    let oddCount = 0;

    last20.forEach((r) => {
      if (r.number === 0) return;
      if (r.number % 2 === 0) evenCount++;
      else oddCount++;
    });

    const total = evenCount + oddCount;
    const evenPerc = (evenCount / total) * 100;
    const oddPerc = (oddCount / total) * 100;

    if (evenPerc >= 70 || oddPerc >= 70) {
      const dominant = evenPerc > oddPerc ? "Par" : "Ímpar";
      const count = Math.max(evenCount, oddCount);
      const percentage = Math.max(evenPerc, oddPerc);
      const confidence = Math.min(50 + (percentage - 70) * 1.5, 65);

      return {
        id: "parity-imbalance",
        type: "basic",
        confidence: confidence,
        priority: percentage / 3,
        icon: "⚖️",
        title: `Desequilíbrio: Números ${dominant}s`,
        description: `Números ${dominant.toLowerCase()}s dominam com ${count} de ${total} resultados (${percentage.toFixed(
          1
        )}%). Desvio da distribuição esperada de ~50/50.`,
        suggestion: `Considere apostar em números ${dominant.toLowerCase()}s`,
        data: {
          Dominante: dominant,
          Contagem: `${count}/${total}`,
          Porcentagem: `${percentage.toFixed(1)}%`,
        },
      };
    }
    return null;
  }

  // ==================== 5. NÚMEROS QUENTES ====================

  detectHotNumbers(results) {
    const last50 = results.slice(0, Math.min(50, results.length));
    if (last50.length < 30) return null;

    const frequency = {};
    last50.forEach((r) => {
      frequency[r.number] = (frequency[r.number] || 0) + 1;
    });

    const hotNums = Object.entries(frequency)
      .filter(([num, count]) => count >= 4)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    if (hotNums.length > 0) {
      const topNumber = hotNums[0];
      const expected = last50.length / 37;
      const deviation = ((topNumber[1] - expected) / expected) * 100;

      // Só alertar se o desvio for significativo (>100%)
      if (deviation < 100) return null;

      const confidence = Math.min(60 + deviation * 0.5, 78);

      return {
        id: "hot-numbers",
        type: "basic",
        confidence: confidence,
        priority: topNumber[1] * 2,
        icon: "🔥",
        title: `Números Quentes Detectados`,
        description: `O número ${topNumber[0]} apareceu ${
          topNumber[1]
        } vezes em ${last50.length} rodadas (esperado: ~${expected.toFixed(
          1
        )}). Top 5 números quentes: ${hotNums.map((n) => n[0]).join(", ")}.`,
        suggestion: `Apostar nos números: ${hotNums
          .map((n) => n[0])
          .join(", ")} (direto ou splits)`,
        data: {
          "Top 1": `${topNumber[0]} (${topNumber[1]}x)`,
          "Total quentes": hotNums.length,
          Janela: `${last50.length} rodadas`,
        },
      };
    }
    return null;
  }

  // ==================== 6. NÚMEROS FRIOS ====================

  detectColdNumbers(results) {
    const last50 = results.slice(0, Math.min(50, results.length));
    if (last50.length < 30) return null;

    const lastSeen = {};
    last50.forEach((r, index) => {
      if (!lastSeen[r.number]) {
        lastSeen[r.number] = last50.length - index;
      }
    });

    const coldNums = [];
    for (let num = 0; num <= 36; num++) {
      const rodadas = lastSeen[num] || last50.length;
      if (rodadas > 30) {
        coldNums.push({ number: num, rodadas: rodadas });
      }
    }

    if (coldNums.length > 0) {
      coldNums.sort((a, b) => b.rodadas - a.rodadas);
      const coldest = coldNums[0];
      const confidence = Math.min(35 + coldest.rodadas * 0.4, 55);

      return {
        id: "cold-numbers",
        type: "basic",
        confidence: confidence,
        priority: coldest.rodadas / 5,
        icon: "❄️",
        title: `Números Frios Detectados`,
        description: `O número ${coldest.number} não aparece há ${coldest.rodadas} rodadas. Total de ${coldNums.length} números "dormentes". Números frios eventualmente aparecem, mas cada rodada é independente.`,
        suggestion: `Alguns apostam em números frios esperando que "devem sair"`,
        data: {
          "Mais frio": `${coldest.number} (${coldest.rodadas} rodadas)`,
          "Total frios": coldNums.length,
          Limiar: "30+ rodadas",
        },
      };
    }
    return null;
  }

  // ==================== 7. DÚZIA QUENTE ====================

  detectHotDozen(results) {
    const last20 = results.slice(0, Math.min(20, results.length));
    if (last20.length < 15) return null;

    const dozens = { "1ª": 0, "2ª": 0, "3ª": 0 };

    last20.forEach((r) => {
      const num = r.number;
      if (num >= 1 && num <= 12) dozens["1ª"]++;
      else if (num >= 13 && num <= 24) dozens["2ª"]++;
      else if (num >= 25 && num <= 36) dozens["3ª"]++;
    });

    const hotDozen = Object.entries(dozens).reduce((max, curr) =>
      curr[1] > max[1] ? curr : max
    );

    const percentage = (hotDozen[1] / last20.length) * 100;

    if (percentage >= 45) {
      const confidence = Math.min(45 + (percentage - 45) * 1.5, 65);
      const ranges = { "1ª": "1-12", "2ª": "13-24", "3ª": "25-36" };

      return {
        id: "hot-dozen",
        type: "basic",
        confidence: confidence,
        priority: percentage / 2,
        icon: "📊",
        title: `Dúzia Dominante: ${hotDozen[0]}`,
        description: `A ${hotDozen[0]} dúzia (${
          ranges[hotDozen[0]]
        }) apareceu ${hotDozen[1]} de ${
          last20.length
        } vezes (${percentage.toFixed(
          1
        )}%). Esta dúzia está mais ativa que as outras.`,
        suggestion: `Continuar apostando na ${hotDozen[0]} dúzia (${
          ranges[hotDozen[0]]
        })`,
        data: {
          Dúzia: `${hotDozen[0]} (${ranges[hotDozen[0]]})`,
          Aparições: `${hotDozen[1]}/${last20.length}`,
          Porcentagem: `${percentage.toFixed(1)}%`,
        },
      };
    }
    return null;
  }

  // ==================== 8. COLUNA QUENTE ====================

  detectHotColumn(results) {
    const last20 = results.slice(0, Math.min(20, results.length));
    if (last20.length < 15) return null;

    const columns = { "1ª": 0, "2ª": 0, "3ª": 0 };

    last20.forEach((r) => {
      const num = r.number;
      if (num === 0) return;
      const col = ((num - 1) % 3) + 1;
      if (col === 1) columns["1ª"]++;
      else if (col === 2) columns["2ª"]++;
      else if (col === 3) columns["3ª"]++;
    });

    const hotColumn = Object.entries(columns).reduce((max, curr) =>
      curr[1] > max[1] ? curr : max
    );

    const percentage = (hotColumn[1] / last20.length) * 100;

    if (percentage >= 45) {
      const confidence = Math.min(45 + (percentage - 45) * 1.5, 65);

      return {
        id: "hot-column",
        type: "basic",
        confidence: confidence,
        priority: percentage / 2,
        icon: "📐",
        title: `Coluna Dominante: ${hotColumn[0]}`,
        description: `A ${hotColumn[0]} coluna apareceu ${hotColumn[1]} de ${
          last20.length
        } vezes (${percentage.toFixed(
          1
        )}%). Esta coluna está mais ativa que as outras.`,
        suggestion: `Continuar apostando na ${hotColumn[0]} coluna`,
        data: {
          Coluna: hotColumn[0],
          Aparições: `${hotColumn[1]}/${last20.length}`,
          Porcentagem: `${percentage.toFixed(1)}%`,
        },
      };
    }
    return null;
  }

  // ==================== 9. REPETIÇÃO DE NÚMERO ====================

  detectRepeatPattern(results) {
    if (results.length < 5) return null;

    const last5 = results.slice(0, 5);
    const firstNum = last5[0].number;

    for (let i = 1; i < last5.length; i++) {
      if (last5[i].number === firstNum) {
        const confidence = 50 - i * 5;
        return {
          id: "repeat-pattern",
          type: "basic",
          confidence: confidence,
          priority: 15 - i * 2,
          icon: "🔄",
          title: `Repetição: Número ${firstNum}`,
          description: `O número ${firstNum} apareceu 2 vezes nas últimas ${
            i + 1
          } rodadas. Repetições próximas ocorrem naturalmente, mas alguns jogadores as consideram significativas.`,
          suggestion: `Apostar no ${firstNum} direto ou em seus vizinhos`,
          data: {
            Número: firstNum,
            Intervalo: `${i + 1} rodadas`,
            Tipo: "Repetição próxima",
          },
        };
      }
    }
    return null;
  }

  // ==================== 10. VIZINHOS NA RODA ====================

  detectNeighborsPattern(results) {
    if (results.length < 3) return null;

    const last3 = results.slice(0, 3).map((r) => r.number);
    const positions = last3.map((num) => this.WHEEL_ORDER.indexOf(num));

    let areNeighbors = true;
    for (let i = 0; i < positions.length - 1; i++) {
      const diff = Math.abs(positions[i] - positions[i + 1]);
      if (diff > 5 && diff < this.WHEEL_ORDER.length - 5) {
        areNeighbors = false;
        break;
      }
    }

    if (areNeighbors) {
      return {
        id: "neighbors-pattern",
        type: "basic",
        confidence: 58,
        priority: 12,
        icon: "🎯",
        title: `Cluster de Vizinhos na Roda`,
        description: `Os últimos 3 números (${last3.join(
          ", "
        )}) estão próximos na roda física. Isso pode indicar que a bola está caindo em uma região específica.`,
        suggestion: `Apostar em números vizinhos aos últimos resultados`,
        data: {
          Números: last3.join(", "),
          Padrão: "Vizinhos na roda",
          Rodadas: "3 últimas",
        },
      };
    }
    return null;
  }

  // ==================== HELPERS ====================

  getColorName(color) {
    const names = { red: "Vermelho", black: "Preto", green: "Verde" };
    return names[color] || color;
  }

  getOppositeColor(color) {
    const opposites = {
      red: "Preto",
      black: "Vermelho",
      green: "Qualquer cor",
    };
    return opposites[color] || "Outra cor";
  }

  getColorSymbol(color) {
    const symbols = { red: "V", black: "P", green: "0" };
    return symbols[color] || "?";
  }
}

// Exportar para uso global
window.RoulettePatternDetector = RoulettePatternDetector;
window.PatternDetector = RoulettePatternDetector; // Alias para compatibilidade

console.log("✅ Pattern Detector loaded");
