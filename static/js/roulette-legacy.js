/**
 * Roulette Legacy Functions - Compatibilidade com HTML existente
 * Mantém as funções que ainda são chamadas inline no HTML
 */

let colorChart = null;
let updateInterval = null;
let isMonitoring = false;
let customPatternsInterval = null;

// Funções de verificação de configuração de alertas
function isSystemAlertsEnabled() {
  try {
    const settings = JSON.parse(
      localStorage.getItem("alertSettings") || '{"systemAlerts": true}'
    );
    return settings.systemAlerts !== false;
  } catch (error) {
    console.error(
      "Erro ao verificar configuração de alertas do sistema:",
      error
    );
    return true; // Default para ativo em caso de erro
  }
}

function isCustomAlertsEnabled() {
  try {
    const settings = JSON.parse(
      localStorage.getItem("alertSettings") || '{"customAlerts": true}'
    );
    return settings.customAlerts !== false;
  } catch (error) {
    console.error(
      "Erro ao verificar configuração de alertas personalizados:",
      error
    );
    return true; // Default para ativo em caso de erro
  }
}

// Inicializar ao carregar a página
window.addEventListener("DOMContentLoaded", () => {
  checkStatus();
  initColorChart();
});

// Verificar status do monitoramento
async function checkStatus() {
  try {
    const response = await fetch("/api/roulette/status");
    const data = await response.json();

    const isActive = data.connected && data.available;
    isMonitoring = isActive;
    updateStatusUI(isActive);

    if (isActive) {
      // Se foi inicializado automaticamente, notificar usuário
      if (data.auto_started) {
        console.log("✅ Sistema inicializado automaticamente!");
        showNotification(
          "✅ Sistema conectado automaticamente à Roleta Brasileira",
          "success"
        );
      }

      loadResults();
      startAutoUpdate();

      // Iniciar detecção de padrões se disponível
      if (window.roulettePatterns) {
        window.roulettePatterns.startDetection();
      }

      // Iniciar verificação de padrões personalizados
      startCustomPatternsCheck();
    } else if (data.auto_start_failed && data.auto_start_enabled) {
      // Só mostra erro se auto-start estava habilitado
      console.warn("⚠️ Falha ao inicializar automaticamente:", data.message);
      showNotification(
        `⚠️ Auto-start falhou. Clique em "Iniciar Monitoramento"`,
        "warning"
      );
    } else if (!data.connected) {
      // Sistema não conectado, mas sem erros - modo normal
      console.log("ℹ️ Sistema aguardando inicialização manual");
    }
  } catch (error) {
    console.error("Erro ao verificar status:", error);
    updateStatusUI(false);
  }
}

// Atualizar interface de status
function updateStatusUI(monitoring) {
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");

  if (monitoring) {
    statusDot.classList.remove("offline");
    statusText.textContent = "Monitoramento Ativo";
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else {
    statusDot.classList.add("offline");
    statusText.textContent = "Monitoramento Inativo";
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

// Iniciar monitoramento (chamado pelo botão)
async function startMonitoring() {
  try {
    const response = await fetch("/api/roulette/start", {
      method: "POST",
    });
    const data = await response.json();

    if (data.success) {
      isMonitoring = true;
      updateStatusUI(true);
      loadResults();
      startAutoUpdate();
      alert("✅ Monitoramento iniciado com sucesso!");

      // Iniciar detecção de padrões se disponível
      if (window.roulettePatterns) {
        window.roulettePatterns.startDetection();
      }
    } else {
      alert("❌ Erro ao iniciar: " + (data.error || data.message));
    }
  } catch (error) {
    console.error("Erro ao iniciar monitoramento:", error);
    alert("❌ Erro ao conectar com o servidor");
  }
}

// Parar monitoramento (chamado pelo botão)
async function stopMonitoring() {
  try {
    const response = await fetch("/api/roulette/stop", {
      method: "POST",
    });
    const data = await response.json();

    if (data.success) {
      isMonitoring = false;
      updateStatusUI(false);
      stopAutoUpdate();

      // Parar verificação de padrões personalizados
      stopCustomPatternsCheck();

      alert("✅ Monitoramento parado!");

      // Parar detecção de padrões se disponível
      if (window.roulettePatterns) {
        window.roulettePatterns.stopDetection();
      }
    } else {
      alert("❌ Erro ao parar: " + (data.error || data.message));
    }
  } catch (error) {
    console.error("Erro ao parar monitoramento:", error);
    alert("❌ Erro ao conectar com o servidor");
  }
}

// Iniciar atualizações automáticas
function startAutoUpdate() {
  if (updateInterval) clearInterval(updateInterval);
  updateInterval = setInterval(loadResults, 3000); // A cada 3 segundos
}

// Parar atualizações automáticas
function stopAutoUpdate() {
  if (updateInterval) {
    clearInterval(updateInterval);
    updateInterval = null;
  }
}

// Carregar resultados
async function loadResults() {
  try {
    const response = await fetch("/api/roulette/results");
    const data = await response.json();

    if (data.success && data.results) {
      displayResults(data.results);
      updateStats(data.results);
      updatePatterns(data.results);
      updateAlerts(data.results);
      updateLastUpdate();
    }
  } catch (error) {
    console.error("Erro ao carregar resultados:", error);
  }
}

// Exibir resultados
function displayResults(results) {
  const container = document.getElementById("resultsContainer");
  if (!container) return;

  if (!results || results.length === 0) {
    container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎲</div>
                <p>Aguardando resultados...</p>
            </div>
        `;
    return;
  }

  // Mostrar últimos 20 resultados
  const last20 = results.slice(0, 20);
  container.innerHTML = "";

  last20.forEach((result) => {
    const item = document.createElement("div");
    item.className = `result-item ${result.color}`;

    const time = result.timestamp
      ? new Date(result.timestamp * 1000).toLocaleTimeString("pt-BR")
      : "";

    item.innerHTML = `
            <div class="result-number">${result.number}</div>
            <div class="result-time">${time}</div>
        `;

    container.appendChild(item);
  });
}

// Atualizar estatísticas
function updateStats(results) {
  if (!results || results.length === 0) return;

  const colors = { red: 0, black: 0, green: 0 };

  results.forEach((r) => {
    if (colors.hasOwnProperty(r.color)) {
      colors[r.color]++;
    }
  });

  const total = results.length;

  // Atualizar contadores
  document.getElementById("redCount").textContent = colors.red;
  document.getElementById("blackCount").textContent = colors.black;
  document.getElementById("greenCount").textContent = colors.green;

  // Atualizar percentuais
  document.getElementById("redPercent").textContent = `${(
    (colors.red / total) *
    100
  ).toFixed(1)}%`;
  document.getElementById("blackPercent").textContent = `${(
    (colors.black / total) *
    100
  ).toFixed(1)}%`;
  document.getElementById("greenPercent").textContent = `${(
    (colors.green / total) *
    100
  ).toFixed(1)}%`;

  // Atualizar gráfico
  updateColorChart(colors);
}

// Inicializar gráfico
function initColorChart() {
  const canvas = document.getElementById("colorChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  colorChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Vermelho", "Preto", "Verde"],
      datasets: [
        {
          data: [0, 0, 0],
          backgroundColor: ["#e74c3c", "#2c3e50", "#27ae60"],
          borderWidth: 2,
          borderColor: "#fff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

// Atualizar gráfico
function updateColorChart(colors) {
  if (!colorChart) return;

  colorChart.data.datasets[0].data = [colors.red, colors.black, colors.green];
  colorChart.update();
}

// Atualizar padrões
function updatePatterns(results) {
  const container = document.getElementById("patternsList");
  if (!container || !results || results.length < 5) return;

  const patterns = [];

  // Detectar sequências de cores
  let currentColor = null;
  let count = 0;

  for (let i = 0; i < Math.min(results.length, 20); i++) {
    const color = results[i].color;
    if (color === currentColor) {
      count++;
    } else {
      if (count >= 3) {
        patterns.push({
          type: "sequence",
          message: `Sequência de ${count} ${
            currentColor === "red"
              ? "vermelhos"
              : currentColor === "black"
              ? "pretos"
              : "verdes"
          }`,
          priority: count,
        });
      }
      currentColor = color;
      count = 1;
    }
  }

  if (patterns.length === 0) {
    container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔎</div>
                <p>Nenhum padrão detectado</p>
            </div>
        `;
    return;
  }

  patterns.sort((a, b) => b.priority - a.priority);

  container.innerHTML = "";
  patterns.forEach((pattern) => {
    const item = document.createElement("div");
    item.className = "pattern-item";

    // Adicionar o número do último resultado ao padrão
    pattern.numero = results[0].number;
    pattern.cor = results[0].color;

    // HTML base do padrão
    let patternHTML = `<span class="pattern-message">${pattern.message}</span>`;

    // Adicionar o número do resultado
    const colorClass =
      pattern.cor === "red"
        ? "result-red"
        : pattern.cor === "black"
        ? "result-black"
        : "result-green";

    patternHTML += `
      <div class="pattern-result">
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

    item.innerHTML = patternHTML;
    container.appendChild(item);
  });
}

// Atualizar alertas
function updateAlerts(results) {
  // Verificar se alertas do sistema estão habilitados
  if (!isSystemAlertsEnabled()) {
    const container = document.getElementById("alertsContainer");
    if (container) {
      container.innerHTML =
        '<div class="empty-state"><p>Alertas do sistema desabilitados</p></div>';
    }
    return;
  }

  const container = document.getElementById("alertsContainer");
  if (!container || !results || results.length < 10) return;

  const alerts = [];
  const last10 = results.slice(0, 10);

  // Detectar sequência de vermelho
  const redInLast10 = last10.filter((r) => r.color === "red").length;
  if (redInLast10 >= 7) {
    alerts.push({
      type: "hot-color",
      message: `🔥 Vermelho quente: ${redInLast10}/10 últimos giros`,
      priority: 5,
      numero: last10[0].number,
      cor: last10[0].color,
    });
  }

  // Detectar sequência de preto
  const blackInLast10 = last10.filter((r) => r.color === "black").length;
  if (blackInLast10 >= 7) {
    alerts.push({
      type: "hot-color",
      message: `🔥 Preto quente: ${blackInLast10}/10 últimos giros`,
      priority: 5,
      numero: last10[0].number,
      cor: last10[0].color,
    });
  }

  // Detectar ausência de verde
  const greenInLast10 = last10.filter((r) => r.color === "green").length;
  if (greenInLast10 === 0 && results.length >= 20) {
    const last20 = results.slice(0, 20);
    const greenInLast20 = last20.filter((r) => r.color === "green").length;
    if (greenInLast20 === 0) {
      alerts.push({
        type: "cold-number",
        message: `❄️ Verde (0) não aparece há ${last20.length} giros`,
        priority: 3,
        numero: last10[0].number,
        cor: last10[0].color,
      });
    }
  }

  // Mostrar alertas
  if (alerts.length === 0) {
    container.innerHTML =
      '<div class="empty-state"><p>Nenhum alerta no momento</p></div>';
    return;
  }

  alerts.sort((a, b) => b.priority - a.priority);

  container.innerHTML = "";
  alerts.forEach((alert) => {
    const item = document.createElement("div");
    item.className = `alert-item ${alert.type}`;

    // HTML base do alerta
    let alertHTML = `
            <span>${alert.message}</span>
            <span>⚡</span>
        `;

    // Adicionar o número do resultado se disponível
    if (alert.numero !== undefined) {
      const colorClass =
        alert.cor === "red"
          ? "result-red"
          : alert.cor === "black"
          ? "result-black"
          : "result-green";

      alertHTML += `
        <div class="alert-result">
          <div class="result-header">Número da Jogada:</div>
          <div class="result-content">
            <div class="result-number ${colorClass}">${alert.numero}</div>
            <div class="result-color">${
              alert.cor === "red"
                ? "Vermelho"
                : alert.cor === "black"
                ? "Preto"
                : "Verde"
            }</div>
          </div>
        </div>
      `;
    }

    item.innerHTML = alertHTML;
    container.appendChild(item);
  });
}

// Atualizar timestamp da última atualização
function updateLastUpdate() {
  const lastUpdate = document.getElementById("lastUpdate");
  if (lastUpdate) {
    const now = new Date().toLocaleTimeString("pt-BR");
    lastUpdate.textContent = `Última atualização: ${now}`;
  }
}

// Mostrar notificação temporária
function showNotification(message, type = "info") {
  // Criar elemento de notificação
  const notification = document.createElement("div");
  notification.className = `auto-start-notification ${type}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    background: ${
      type === "success"
        ? "#10b981"
        : type === "warning"
        ? "#f59e0b"
        : "#3b82f6"
    };
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    z-index: 10000;
    font-weight: 500;
    animation: slideIn 0.3s ease-out;
  `;
  notification.textContent = message;

  // Adicionar ao body
  document.body.appendChild(notification);

  // Remover após 5 segundos
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-in";
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 5000);
}

// ===== PADRÕES PERSONALIZADOS =====

function startCustomPatternsCheck() {
  if (customPatternsInterval) {
    clearInterval(customPatternsInterval);
  }

  // Verificar padrões personalizados a cada 10 segundos
  customPatternsInterval = setInterval(checkCustomPatterns, 10000);
  console.log("🔍 Verificação de padrões personalizados iniciada");
}

function stopCustomPatternsCheck() {
  if (customPatternsInterval) {
    clearInterval(customPatternsInterval);
    customPatternsInterval = null;
    console.log("🛑 Verificação de padrões personalizados parada");
  }
}

async function checkCustomPatterns() {
  try {
    // Verificar se alertas customizados estão habilitados
    if (!isCustomAlertsEnabled()) {
      console.log(
        "⏸️ Alertas customizados desabilitados - pulando verificação"
      );
      return;
    }

    const response = await fetch("/api/custom-patterns/check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success && data.triggered_patterns.length > 0) {
      console.log(
        `🎯 ${data.triggered_patterns.length} padrão(ões) personalizado(s) ativado(s)`
      );

      // Processar cada padrão ativado
      data.triggered_patterns.forEach((pattern) => {
        showCustomPatternAlert(pattern);
      });
    }
  } catch (error) {
    console.error("Erro ao verificar padrões personalizados:", error);
  }
}

function showCustomPatternAlert(pattern) {
  // ALERTA ABSOLUTO - PRIORIDADE MÁXIMA
  const alertHtml = `
    <div class="custom-pattern-alert ABSOLUTE-PRIORITY" style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
      color: white;
      padding: 25px;
      border-radius: 15px;
      box-shadow: 0 15px 50px rgba(255,107,107,0.5);
      z-index: 99999;
      max-width: 400px;
      animation: customPatternPulse 0.8s ease-out;
      border: 3px solid #ff4757;
    ">
      <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <div style="font-size: 32px; margin-right: 15px; animation: bounce 1s infinite;">🚨</div>
        <div>
          <h3 style="margin: 0; font-size: 20px; font-weight: bold;">PADRÃO PERSONALIZADO!</h3>
          <small style="opacity: 0.9; font-size: 14px;">${pattern.name}</small>
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        <div style="margin-bottom: 10px;">
          <strong style="font-size: 16px;">🎯 SUGESTÃO:</strong> 
          <span style="font-size: 18px; font-weight: bold; text-transform: uppercase;">${
            pattern.suggestion
          }</span>
        </div>

        <div style="margin-bottom: 10px;">
          <strong>📊 Confiança:</strong> 
          <span style="color: #ffd700; font-weight: bold;">${Math.round(
            pattern.confidence * 100
          )}%</span>
        </div>

        <div>
          <strong>💡 Razão:</strong> ${pattern.reasoning}
        </div>
      </div>

      <div style="display: flex; gap: 12px;">
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: rgba(255,255,255,0.3);
          border: 2px solid white;
          color: white;
          padding: 10px 20px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: bold;
          transition: all 0.3s;
        " onmouseover="this.style.background='rgba(255,255,255,0.5)'" 
           onmouseout="this.style.background='rgba(255,255,255,0.3)'">Fechar</button>

        <button onclick="window.open('/custom-patterns', '_blank')" style="
          background: #ffd700;
          border: 2px solid #ffd700;
          color: #333;
          padding: 10px 20px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: bold;
          transition: all 0.3s;
        " onmouseover="this.style.background='#ffed4e'" 
           onmouseout="this.style.background='#ffd700'">Gerenciar</button>
      </div>
    </div>
  `;

  // Adicionar CSS da animação se não existir
  if (!document.getElementById("custom-pattern-styles")) {
    const style = document.createElement("style");
    style.id = "custom-pattern-styles";
    style.textContent = `
      @keyframes slideInRight {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      
      @keyframes customPatternPulse {
        0% {
          transform: scale(0.8) translateX(100%);
          opacity: 0;
        }
        50% {
          transform: scale(1.05) translateX(0);
          opacity: 1;
        }
        100% {
          transform: scale(1) translateX(0);
          opacity: 1;
        }
      }
      
      @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
          transform: translateY(0);
        }
        40% {
          transform: translateY(-10px);
        }
        60% {
          transform: translateY(-5px);
        }
      }
      
      .ABSOLUTE-PRIORITY {
        animation: customPatternPulse 0.8s ease-out !important;
        z-index: 99999 !important;
      }
      
      .ABSOLUTE-PRIORITY:hover {
        transform: scale(1.02);
        transition: transform 0.3s ease;
      }
    `;
    document.head.appendChild(style);
  }

  // Adicionar alerta ao DOM
  document.body.insertAdjacentHTML("beforeend", alertHtml);

  // Reproduzir som de alerta especial
  playCustomPatternAlertSound();

  // Remover automaticamente após 30 segundos (mais tempo para padrões personalizados)
  setTimeout(() => {
    const alert = document.querySelector(
      ".custom-pattern-alert.ABSOLUTE-PRIORITY"
    );
    if (alert) {
      alert.style.animation = "customPatternPulse 0.5s ease-in reverse";
      setTimeout(() => alert.remove(), 500);
    }
  }, 30000);
}

// Função para reproduzir som especial de padrão personalizado
function playCustomPatternAlertSound() {
  try {
    // Criar contexto de áudio
    const audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();

    // Frequências para um som de alerta especial
    const frequencies = [800, 1000, 1200, 800]; // Sequência de tons
    let currentFreq = 0;

    function playTone(frequency, duration) {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
      oscillator.type = "sine";

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + duration
      );

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration);
    }

    // Reproduzir sequência de tons
    frequencies.forEach((freq, index) => {
      setTimeout(() => {
        playTone(freq, 0.2);
      }, index * 200);
    });
  } catch (error) {
    console.log("Som de alerta personalizado não disponível:", error);
  }
}

// Parar verificação quando a página for fechada
window.addEventListener("beforeunload", () => {
  stopCustomPatternsCheck();
});

console.log("✅ Roulette Legacy Functions loaded");
