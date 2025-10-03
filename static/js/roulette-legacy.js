/**
 * Roulette Legacy Functions - Compatibilidade com HTML existente
 * Mantém as funções que ainda são chamadas inline no HTML
 */

let colorChart = null;
let updateInterval = null;
let isMonitoring = false;

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
    item.textContent = pattern.message;
    container.appendChild(item);
  });
}

// Atualizar alertas
function updateAlerts(results) {
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
    });
  }

  // Detectar sequência de preto
  const blackInLast10 = last10.filter((r) => r.color === "black").length;
  if (blackInLast10 >= 7) {
    alerts.push({
      type: "hot-color",
      message: `🔥 Preto quente: ${blackInLast10}/10 últimos giros`,
      priority: 5,
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
    item.innerHTML = `
            <span>${alert.message}</span>
            <span>⚡</span>
        `;
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

console.log("✅ Roulette Legacy Functions loaded");
