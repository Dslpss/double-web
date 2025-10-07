/**
 * Alert Manager - FASE 2
 * Gerencia exibição de alertas de padrões na interface
 */

class AlertManager {
  constructor(containerId = "pattern-alerts") {
    this.container = document.getElementById(containerId);
    this.activeAlerts = new Map(); // Mapa de alertas ativos (ID -> elemento)
    this.maxAlerts = 15; // Máximo de alertas visíveis (aumentado para permitir mais histórico)
    this.autoHideTimeout = 300000; // 5 minutos (300000ms) - alertas ficam visíveis por 5 minutos
    this.cooldownTime = 300000; // 5 minutos de cooldown
    this.lastAlertTimes = {};

    if (!this.container) {
      console.error("Container de alertas não encontrado:", containerId);
    }
  }

  /**
   * Verifica se o tipo de alerta está habilitado
   */
  isAlertTypeEnabled(alertType) {
    try {
      const settings = localStorage.getItem("alertSettings");
      if (settings) {
        const alertSettings = JSON.parse(settings);
        if (alertType === "system") {
          return alertSettings.systemAlerts !== false;
        } else if (alertType === "custom") {
          return alertSettings.customAlerts !== false;
        }
      }
      // Por padrão, ambos estão habilitados
      return true;
    } catch (error) {
      console.warn("Erro ao verificar configurações de alerta:", error);
      return true; // Em caso de erro, sempre mostrar
    }
  }

  /**
   * Exibe um padrão detectado como alerta
   */
  showPattern(pattern) {
    if (!this.container) return;

    // Verificar se o tipo de alerta está habilitado
    const alertType = pattern.isCustomPattern ? "custom" : "system";
    if (!this.isAlertTypeEnabled(alertType)) {
      console.log(
        `Alerta ${alertType} desabilitado. Padrão não será exibido:`,
        pattern.type || pattern.name
      );
      return;
    }

    const patternId = pattern.id || `pattern-${Date.now()}`;

    const now = Date.now();
    if (
      this.lastAlertTimes[patternId] &&
      now - this.lastAlertTimes[patternId] < this.cooldownTime
    ) {
      console.log(
        `Cooldown ativo para o padrão ${patternId}. Alerta não disparado.`
      );
      return;
    }
    this.lastAlertTimes[patternId] = now;

    // Adicionar hora de detecção para análise posterior
    pattern.detectedAt = new Date().toLocaleTimeString();

    // Se já existe, atualizar
    if (this.activeAlerts.has(patternId)) {
      this.updateAlert(patternId, pattern);
      return;
    }

    // Limpar alertas antigos se exceder o limite
    if (this.activeAlerts.size >= this.maxAlerts) {
      this.removeOldestAlert();
    }

    // Criar elemento do alerta
    const alertElement = this.createAlertElement(pattern);

    // Adicionar ao container (no topo)
    this.container.insertBefore(alertElement, this.container.firstChild);

    // Registrar
    this.activeAlerts.set(patternId, {
      element: alertElement,
      pattern: pattern,
      timestamp: Date.now(),
    });

    // Animação de entrada
    setTimeout(() => {
      alertElement.classList.add("alert-show");
      // Atualizar contador após animação
      this.updateCounter();
    }, 10);

    // Auto-hide após timeout (se configurado)
    // autoHideTimeout > 0 significa que alertas expiram automaticamente
    if (this.autoHideTimeout > 0 && pattern.type !== "critical") {
      setTimeout(() => {
        this.removeAlert(patternId);
        this.updateCounter();
      }, this.autoHideTimeout);
    }
  }

  /**
   * Cria o elemento HTML do alerta
   */
  createAlertElement(pattern) {
    const div = document.createElement("div");
    div.className = `pattern-alert alert-${this.getConfidenceLevel(
      pattern.confidence
    )}`;
    div.dataset.patternId = pattern.id;

    // Ícone e título
    const header = document.createElement("div");
    header.className = "alert-header";
    header.innerHTML = `
            <span class="alert-icon">${pattern.icon || "🎲"}</span>
            <span class="alert-title">${pattern.title} ${
      pattern.numero ? "- Número: " + pattern.numero : ""
    }</span>
            <span class="alert-confidence">${pattern.confidence}%</span>
            <button class="alert-close" onclick="window.alertManager.removeAlert('${
              pattern.id
            }')">&times;</button>
        `;

    // Descrição
    const description = document.createElement("div");
    description.className = "alert-description";
    description.textContent = pattern.description;

    // Sugestão
    const suggestion = document.createElement("div");
    suggestion.className = "alert-suggestion";
    suggestion.innerHTML = `<strong>💡 Sugestão:</strong> ${pattern.suggestion}`;

    // Dados estatísticos (se houver)
    let dataSection = "";
    if (pattern.data && Object.keys(pattern.data).length > 0) {
      dataSection = '<div class="alert-data">';
      for (const [key, value] of Object.entries(pattern.data)) {
        dataSection += `<div class="data-item"><span class="data-key">${key}:</span> <span class="data-value">${value}</span></div>`;
      }
      dataSection += "</div>";
    }

    // Montar
    div.appendChild(header);
    div.appendChild(description);
    div.appendChild(suggestion);
    if (dataSection) {
      div.innerHTML += dataSection;
    }

    // Exibe o número do resultado representado pelo alerta com estilo melhorado
    if (pattern.numero) {
      const resultBox = document.createElement("div");
      resultBox.className = "alert-result";

      // Determinar a classe CSS para a cor do resultado
      const colorClass =
        pattern.cor === "red"
          ? "result-red"
          : pattern.cor === "black"
          ? "result-black"
          : "result-green";

      resultBox.innerHTML = `
        <div class="result-header">Número da Jogada:</div>
        <div class="result-content">
          <div class="result-number ${colorClass}">${pattern.numero}</div>
          <div class="result-color">${
            pattern.cor === "red"
              ? "Vermelho"
              : pattern.cor === "black"
              ? "Preto"
              : "Verde"
          }</div>
        </div>
      `;
      div.appendChild(resultBox);
    }

    return div;
  }

  /**
   * Atualiza um alerta existente
   */
  updateAlert(patternId, newPattern) {
    const alertData = this.activeAlerts.get(patternId);
    if (!alertData) return;

    // Atualizar dados
    alertData.pattern = newPattern;
    alertData.timestamp = Date.now();

    // Recriar elemento
    const newElement = this.createAlertElement(newPattern);
    alertData.element.replaceWith(newElement);
    alertData.element = newElement;

    // Animação de atualização
    newElement.classList.add("alert-updated");
    setTimeout(() => {
      newElement.classList.remove("alert-updated");
    }, 500);
  }

  /**
   * Remove um alerta específico
   */
  removeAlert(patternId) {
    const alertData = this.activeAlerts.get(patternId);
    if (!alertData) return;

    // Animação de saída
    alertData.element.classList.remove("alert-show");
    alertData.element.classList.add("alert-hide");

    setTimeout(() => {
      if (alertData.element.parentNode) {
        alertData.element.parentNode.removeChild(alertData.element);
      }
      this.activeAlerts.delete(patternId);
      // Atualizar contador após remover
      this.updateCounter();
    }, 3000);
  }

  /**
   * Remove o alerta mais antigo
   */
  removeOldestAlert() {
    let oldestId = null;
    let oldestTime = Infinity;

    for (const [id, data] of this.activeAlerts.entries()) {
      if (data.timestamp < oldestTime) {
        oldestTime = data.timestamp;
        oldestId = id;
      }
    }

    if (oldestId) {
      this.removeAlert(oldestId);
    }
  }

  /**
   * Limpa todos os alertas
   */
  clearAlerts() {
    for (const patternId of this.activeAlerts.keys()) {
      this.removeAlert(patternId);
    }
  }

  /**
   * Limpa alertas antigos mantendo apenas os N mais recentes
   * @param {number} keepCount - Número de alertas mais recentes a manter
   */
  clearOldAlerts(keepCount = 3) {
    // Ordenar alertas por timestamp (mais recentes primeiro)
    const sortedAlerts = Array.from(this.activeAlerts.entries()).sort(
      (a, b) => b[1].timestamp - a[1].timestamp
    );

    // Remover alertas além do limite
    for (let i = keepCount; i < sortedAlerts.length; i++) {
      this.removeAlert(sortedAlerts[i][0]);
    }

    console.log(
      `🗑️ Alertas antigos removidos. Mantidos: ${Math.min(
        keepCount,
        this.activeAlerts.size
      )}`
    );
    this.updateCounter();
  }

  /**
   * Atualiza o contador de alertas na interface
   */
  updateCounter() {
    const countElement = document.getElementById("alert-count");
    if (countElement) {
      const count = this.activeAlerts.size;
      countElement.textContent = count;

      // Mudar cor do badge baseado na quantidade
      const counterBadge = document.getElementById("alert-counter");
      if (counterBadge) {
        if (count === 0) {
          counterBadge.style.background = "#9E9E9E"; // Cinza
        } else if (count < 5) {
          counterBadge.style.background = "#4CAF50"; // Verde
        } else if (count < 10) {
          counterBadge.style.background = "#FF9800"; // Laranja
        } else {
          counterBadge.style.background = "#f44336"; // Vermelho
        }
      }
    }
  }

  /**
   * Atualiza todos os alertas com novos padrões
   * NÃO remove alertas existentes - deixa expirar por timeout ou limite
   */
  updateAlerts(patterns) {
    // NÃO remover alertas antigos automaticamente
    // Deixar o timeout (5 minutos) ou limite (15 alertas) gerenciar
    // Isso mantém histórico visível dos padrões detectados

    // Adicionar ou atualizar padrões
    for (const pattern of patterns) {
      this.showPattern(pattern);
    }
  }

  /**
   * Determina o nível de confiança
   */
  getConfidenceLevel(confidence) {
    if (confidence >= 70) return "high";
    if (confidence >= 55) return "medium";
    return "low";
  }

  /**
   * Mostra notificação toast (temporária)
   */
  showToast(message, type = "info", duration = 3000) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("toast-show");
    }, 10);

    setTimeout(() => {
      toast.classList.remove("toast-show");
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, duration);
  }

  /**
   * Reproduz som de alerta
   */
  playAlertSound() {
    // Criar beep usando Web Audio API
    try {
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = "sine";

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + 0.5
      );

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
      console.log("Audio não disponível:", e);
    }
  }

  /**
   * Finaliza o ciclo de análise: exibe o padrão atual para a jogada seguinte e zera a análise.
   */
  completeCycle() {
    // Exibe os padrões avaliados (aqui, apenas um log para simular a exibição)
    this.activeAlerts.forEach((alertData, patternId) => {
      console.log(`Padrão avaliado para a próxima jogada: ${patternId}`);
    });
    // Zera a análise removendo todos os alertas ativos com animação
    for (const patternId of Array.from(this.activeAlerts.keys())) {
      this.removeAlert(patternId);
    }
  }
}

// CSS Styles (injetado dinamicamente)
const alertStyles = `
<style>
.pattern-alert {
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #ccc;
    opacity: 0;
    transform: translateX(-20px);
    transition: all 0.3s ease;
}

.pattern-alert.alert-show {
    opacity: 1;
    transform: translateX(0);
}

.pattern-alert.alert-hide {
    opacity: 0;
    transform: translateX(20px);
}

.pattern-alert.alert-updated {
    animation: pulse 0.5s ease;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.pattern-alert.alert-high {
    border-left-color: #e74c3c;
    background: linear-gradient(135deg, #fff 0%, #ffebee 100%);
}

.pattern-alert.alert-medium {
    border-left-color: #f39c12;
    background: linear-gradient(135deg, #fff 0%, #fff3e0 100%);
}

.pattern-alert.alert-low {
    border-left-color: #3498db;
    background: linear-gradient(135deg, #fff 0%, #e3f2fd 100%);
}

.alert-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    gap: 10px;
}

.alert-icon {
    font-size: 24px;
}

.alert-title {
    flex: 1;
    font-weight: bold;
    font-size: 16px;
    color: #2c3e50;
}

.alert-confidence {
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
}

.alert-high .alert-confidence {
    background: #e74c3c;
    color: white;
}

.alert-medium .alert-confidence {
    background: #f39c12;
    color: white;
}

.alert-low .alert-confidence {
    background: #3498db;
    color: white;
}

.alert-close {
    background: none;
    border: none;
    font-size: 24px;
    color: #95a5a6;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    line-height: 24px;
    transition: color 0.2s;
}

.alert-close:hover {
    color: #e74c3c;
}

.alert-description {
    font-size: 14px;
    color: #555;
    margin-bottom: 10px;
    line-height: 1.5;
}

.alert-suggestion {
    font-size: 14px;
    color: #27ae60;
    padding: 10px;
    background: #f0fff4;
    border-radius: 6px;
    margin-top: 10px;
}

.alert-data {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #ecf0f1;
    font-size: 13px;
}

.data-item {
    display: flex;
    padding: 4px 0;
}

.data-key {
    font-weight: 600;
    color: #7f8c8d;
    min-width: 120px;
}

.data-value {
    color: #2c3e50;
    font-weight: 500;
}

/* Toast notifications */
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    background: #2c3e50;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.3s ease;
    z-index: 10000;
}

.toast.toast-show {
    opacity: 1;
    transform: translateY(0);
}

.toast.toast-success {
    background: #27ae60;
}

.toast.toast-error {
    background: #e74c3c;
}

.toast.toast-warning {
    background: #f39c12;
}

.toast.toast-info {
    background: #3498db;
}
</style>
`;

// Injetar estilos
if (!document.getElementById("alert-manager-styles")) {
  const styleElement = document.createElement("div");
  styleElement.id = "alert-manager-styles";
  styleElement.innerHTML = alertStyles;
  document.head.appendChild(styleElement);
}

// Exportar para uso global
window.AlertManager = AlertManager;
