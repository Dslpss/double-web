/**
 * Roulette Pattern Detection System - MAIN INTEGRATION
 * Sistema híbrido: JavaScript (básico) + Python (avançado)
 */

// ==================== VARIÁVEIS GLOBAIS ====================

let patternDetector = null; // Detector de padrões básicos
let alertManager = null; // Gerenciador de alertas
let patternUpdateInterval = null; // Intervalo de atualização automática (renomeado para evitar conflito)
let advancedUpdateInterval = null; // Intervalo para análise avançada
let lastResults = []; // Cache de resultados
let lastResultId = null; // ID do último resultado processado
let currentAlerts = []; // Alertas atuais (não atualizar até novo resultado)

// Configurações
const CONFIG = {
  basicUpdateInterval: 5000, // 5 segundos para análise básica
  advancedUpdateInterval: 30000, // 30 segundos para análise avançada
  maxResults: 100, // Máximo de resultados para análise
  soundEnabled: true,
  notificationsEnabled: true,
};

// ==================== INICIALIZAÇÃO ====================

window.addEventListener("DOMContentLoaded", () => {
  console.log("🎰 Inicializando Sistema de Detecção de Padrões...");

  // Inicializar componentes
  initializeComponents();

  // Verificar status do integrador
  checkRouletteStatus();

  // Configurar event listeners
  setupEventListeners();

  console.log("✅ Sistema inicializado");
});

/**
 * Inicializa todos os componentes necessários
 */
function initializeComponents() {
  // Inicializar detector de padrões básicos
  if (window.PatternDetector) {
    patternDetector = new window.PatternDetector();
    console.log("✅ Pattern Detector inicializado");
  } else {
    console.error(
      "❌ PatternDetector não encontrado! Certifique-se de incluir pattern-detector.js"
    );
  }

  // Inicializar gerenciador de alertas
  if (window.AlertManager) {
    alertManager = new window.AlertManager("pattern-alerts");
    console.log("✅ Alert Manager inicializado");
  } else {
    console.error(
      "❌ AlertManager não encontrado! Certifique-se de incluir alert-manager.js"
    );
  }
}

/**
 * Configura event listeners de botões e controles
 */
function setupEventListeners() {
  // Botão de limpar alertas
  const clearBtn = document.getElementById("clearAlertsBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (alertManager) {
        alertManager.clearAlerts();
        alertManager.showToast("Alertas limpos!", "success");
      }
    });
  }

  // Botão de configurações
  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", () => {
      showSettingsModal();
    });
  }
}

// ==================== CONTROLE DO INTEGRADOR ====================

/**
 * Verifica status do integrador de roleta
 */
async function checkRouletteStatus() {
  try {
    console.log("🔍 Verificando status da roleta...");
    const response = await fetch("/api/roulette/status");
    const data = await response.json();

    console.log("📡 Resposta do status:", data);

    const isActive = data.connected && data.available;
    console.log(
      `🎯 Status: ${isActive ? "ATIVO" : "INATIVO"} (connected: ${
        data.connected
      }, available: ${data.available})`
    );

    updateStatusDisplay(isActive);

    if (isActive) {
      console.log("🟢 Integrador ativo - iniciando detecção de padrões");
      startPatternDetection();
    } else {
      console.log("🔴 Integrador inativo - parando detecção de padrões");
      console.log("💡 Motivo:", data.message || data.error || "Desconhecido");
      stopPatternDetection();
    }

    return isActive;
  } catch (error) {
    console.error("❌ Erro ao verificar status:", error);
    updateStatusDisplay(false);
    return false;
  }
}

/**
 * Atualiza display de status
 */
function updateStatusDisplay(isActive) {
  const statusElement = document.getElementById("pattern-status");
  if (statusElement) {
    statusElement.textContent = isActive ? "🟢 Ativo" : "🔴 Inativo";
    statusElement.className = isActive ? "status-active" : "status-inactive";
  }
}

// ==================== DETECÇÃO DE PADRÕES ====================

/**
 * Inicia detecção de padrões (básico + avançado)
 */
function startPatternDetection() {
  console.log("🔍 Iniciando detecção de padrões...");

  // Parar intervalos existentes
  stopPatternDetection();

  // Verificar se os componentes estão inicializados
  if (!patternDetector) {
    console.error("❌ PatternDetector não inicializado!");
    return;
  }

  if (!alertManager) {
    console.error("❌ AlertManager não inicializado!");
    return;
  }

  console.log("✅ Componentes OK - configurando intervalos...");

  // Detecção básica (rápida - JavaScript)
  patternUpdateInterval = setInterval(() => {
    detectBasicPatterns();
  }, CONFIG.basicUpdateInterval);

  // Detecção avançada (lenta - Python)
  advancedUpdateInterval = setInterval(() => {
    detectAdvancedPatterns();
  }, CONFIG.advancedUpdateInterval);

  console.log(
    `⏰ Intervalos configurados: básico=${CONFIG.basicUpdateInterval}ms, avançado=${CONFIG.advancedUpdateInterval}ms`
  );

  // Executar imediatamente
  console.log("🚀 Executando primeira análise...");
  detectBasicPatterns();
  detectAdvancedPatterns();
}

/**
 * Para detecção de padrões
 */
function stopPatternDetection() {
  if (patternUpdateInterval) {
    clearInterval(patternUpdateInterval);
    patternUpdateInterval = null;
  }

  if (advancedUpdateInterval) {
    clearInterval(advancedUpdateInterval);
    advancedUpdateInterval = null;
  }

  console.log("⏸️ Detecção de padrões pausada");
}

/**
 * Detecta padrões básicos usando JavaScript (FASE 1)
 */
async function detectBasicPatterns() {
  console.log("🔍 detectBasicPatterns() iniciada...");
  try {
    // Buscar resultados da API
    const response = await fetch("/api/roulette/patterns/basic");
    const data = await response.json();

    console.log("📡 Resposta da API /patterns/basic:", data);

    if (!data.success || !data.results || data.results.length === 0) {
      console.log("⚠️ Nenhum resultado disponível para análise básica");
      return;
    }

    // Verificar se há um novo resultado
    const currentFirstResult = data.results[0];
    const currentResultId = `${currentFirstResult.number}-${currentFirstResult.color}-${currentFirstResult.timestamp}`;

    if (lastResultId === currentResultId) {
      console.log("🔄 Mesmo resultado - não atualizando alertas");
      return;
    }

    console.log(
      `🆕 Novo resultado detectado: ${currentFirstResult.number} ${currentFirstResult.color}`
    );
    lastResultId = currentResultId;
    lastResults = data.results;

    console.log(
      `📊 Analisando ${lastResults.length} resultados (básico):`,
      lastResults
    );

    // Usar detector JavaScript
    if (!patternDetector) {
      console.error("❌ PatternDetector não inicializado");
      return;
    }

    console.log("✅ PatternDetector OK, chamando detectAllPatterns()...");

    const patterns = patternDetector.detectAllPatterns(lastResults);
    console.log(`✅ Detectados ${patterns.length} padrões básicos:`, patterns);

    // Limpar alertas antigos e exibir novos padrões
    if (alertManager) {
      alertManager.clearAlerts();
      console.log("🗑️ Alertas antigos limpos");
    }

    currentAlerts = patterns;
    displayPatterns(patterns, "basic");
  } catch (error) {
    console.error("❌ Erro na detecção básica:", error);
  }
}

/**
 * Detecta padrões avançados usando Python (FASE 2)
 */
async function detectAdvancedPatterns() {
  console.log("🔬 detectAdvancedPatterns() iniciada...");
  try {
    // Buscar análise avançada da API Python
    const response = await fetch("/api/roulette/patterns/advanced");
    const data = await response.json();

    console.log("📡 Resposta da API /patterns/advanced:", data);

    if (!data.success) {
      console.log("⚠️ Análise avançada não disponível:", data.message);
      return;
    }

    const patterns = data.patterns || [];
    console.log(
      `✅ Detectados ${patterns.length} padrões avançados:`,
      patterns
    );

    // Só exibir padrões avançados se não há alertas básicos ativos
    // ou se os padrões avançados são mais significativos
    if (currentAlerts.length === 0 || patterns.length > 0) {
      console.log("🎯 Exibindo padrões avançados");
      displayPatterns(patterns, "advanced");
    } else {
      console.log("⏸️ Mantendo alertas básicos ativos");
    }

    // Atualizar estatísticas se disponíveis
    if (data.statistics) {
      updateStatisticsDisplay(data.statistics);
    }
  } catch (error) {
    console.error("❌ Erro na detecção avançada:", error);
  }
}

/**
 * Exibe padrões na interface
 */
function displayPatterns(patterns, type) {
  console.log(
    `🎯 displayPatterns() chamada - tipo: ${type}, padrões:`,
    patterns
  );

  if (!alertManager) {
    console.error("❌ AlertManager não inicializado");
    return;
  }

  console.log("✅ AlertManager OK:", alertManager);

  if (!patterns || patterns.length === 0) {
    console.log(`⚠️ Nenhum padrão ${type} detectado`);
    return;
  }

  // Filtrar apenas padrões com confiança suficiente
  const significantPatterns = patterns.filter((p) => p.confidence >= 45);

  if (significantPatterns.length === 0) {
    console.log(`Nenhum padrão ${type} significativo (confiança < 45%)`);
    return;
  }

  console.log(`📢 Exibindo ${significantPatterns.length} padrões ${type}`);

  // Exibir cada padrão (sem limpar os existentes)
  for (const pattern of significantPatterns) {
    alertManager.showPattern(pattern);

    // Tocar som para padrões de alta confiança
    if (pattern.confidence >= 70 && CONFIG.soundEnabled) {
      alertManager.playAlertSound();
    }

    // Enviar notificação para padrões críticos
    if (pattern.confidence >= 80 && CONFIG.notificationsEnabled) {
      sendBrowserNotification(pattern);
    }
  }
}

/**
 * Atualiza display de estatísticas
 */
function updateStatisticsDisplay(stats) {
  // Atualizar contadores
  if (stats.total_spins) {
    const totalElement = document.getElementById("total-spins");
    if (totalElement) {
      totalElement.textContent = stats.total_spins;
    }
  }

  // Atualizar números quentes
  if (stats.hot_numbers) {
    const hotElement = document.getElementById("hot-numbers");
    if (hotElement) {
      const numbers = stats.hot_numbers
        .map((n) => `${n.number} (${n.count})`)
        .join(", ");
      hotElement.textContent = numbers;
    }
  }

  // Atualizar números frios
  if (stats.cold_numbers) {
    const coldElement = document.getElementById("cold-numbers");
    if (coldElement) {
      const numbers = stats.cold_numbers
        .map((n) => `${n.number} (${n.count})`)
        .join(", ");
      coldElement.textContent = numbers;
    }
  }

  // Atualizar setores
  if (stats.sectors) {
    updateSectorDisplay(stats.sectors);
  }
}

/**
 * Atualiza display de setores
 */
function updateSectorDisplay(sectors) {
  for (const [sector, data] of Object.entries(sectors)) {
    const element = document.getElementById(`sector-${sector}`);
    if (element) {
      element.textContent = `${data.count} (${data.percentage}%)`;
    }
  }
}

// ==================== NOTIFICAÇÕES DO NAVEGADOR ====================

/**
 * Envia notificação do navegador
 */
function sendBrowserNotification(pattern) {
  if (!("Notification" in window)) {
    return;
  }

  if (Notification.permission === "granted") {
    new Notification("🎰 Padrão Detectado!", {
      body: `${pattern.title}\nConfiança: ${pattern.confidence}%`,
      icon: "/static/images/roulette-icon.png",
      badge: "/static/images/badge.png",
    });
  } else if (Notification.permission !== "denied") {
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        sendBrowserNotification(pattern);
      }
    });
  }
}

// ==================== MODAL DE CONFIGURAÇÕES ====================

/**
 * Mostra modal de configurações
 */
function showSettingsModal() {
  const modal = document.getElementById("settings-modal");
  if (modal) {
    modal.style.display = "flex";
  }
}

/**
 * Fecha modal de configurações
 */
function closeSettingsModal() {
  const modal = document.getElementById("settings-modal");
  if (modal) {
    modal.style.display = "none";
  }
}

/**
 * Salva configurações
 */
function saveSettings() {
  // Obter valores dos inputs
  const soundCheckbox = document.getElementById("sound-enabled");
  const notificationCheckbox = document.getElementById("notification-enabled");
  const basicIntervalInput = document.getElementById("basic-interval");
  const advancedIntervalInput = document.getElementById("advanced-interval");

  if (soundCheckbox) CONFIG.soundEnabled = soundCheckbox.checked;
  if (notificationCheckbox)
    CONFIG.notificationsEnabled = notificationCheckbox.checked;
  if (basicIntervalInput)
    CONFIG.basicUpdateInterval = parseInt(basicIntervalInput.value) * 1000;
  if (advancedIntervalInput)
    CONFIG.advancedUpdateInterval =
      parseInt(advancedIntervalInput.value) * 1000;

  // Salvar no localStorage
  localStorage.setItem("roulette-pattern-config", JSON.stringify(CONFIG));

  // Reiniciar detecção com novas configurações
  if (patternUpdateInterval) {
    stopPatternDetection();
    startPatternDetection();
  }

  closeSettingsModal();

  if (alertManager) {
    alertManager.showToast("Configurações salvas!", "success");
  }
}

/**
 * Carrega configurações salvas
 */
function loadSettings() {
  const saved = localStorage.getItem("roulette-pattern-config");
  if (saved) {
    Object.assign(CONFIG, JSON.parse(saved));
    console.log("⚙️ Configurações carregadas:", CONFIG);
  }
}

// Carregar configurações ao iniciar
loadSettings();

// ==================== EXPORTAÇÕES GLOBAIS ====================

window.roulettePatterns = {
  startDetection: startPatternDetection,
  stopDetection: stopPatternDetection,
  checkStatus: checkRouletteStatus,
  getLastResults: () => lastResults,
  getConfig: () => CONFIG,
  showSettings: showSettingsModal,
  closeSettings: closeSettingsModal,
  saveSettings: saveSettings,
};

console.log("✅ Roulette Pattern System loaded");
