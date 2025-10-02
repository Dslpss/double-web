# 🎲 COMO USAR O DASHBOARD PRINCIPAL

## 🚀 **INICIAR O SISTEMA**

### **🆕 Método 1: Sistema Completo (RECOMENDADO)**

```bash
python start_complete_system.py
```

**✨ Inicia tudo automaticamente: Dashboard Principal + Sistema Double + Roleta**

### **Método 2: Apenas Dashboard Principal**

```bash
python main_dashboard.py
```

**⚠️ Para usar o Double, você precisa iniciar também: `python app.py`**

### **Método 3: Script de Inicialização Antigo**

```bash
python start_main_dashboard.py
```

## 🌐 **ACESSAR O DASHBOARD**

1. **Abra seu navegador**
2. **Acesse:** http://localhost:5000
3. **Escolha seu sistema:**
   - 🔥 **Double (Blaze)** - Clique para ir ao sistema Double (porta 5001)
   - 🎲 **Roleta Brasileira** - Monitor Pragmatic Play integrado

### **🔗 URLs Diretas:**

- **Dashboard Principal:** http://localhost:5000
- **Sistema Double:** http://localhost:5001
- **Sistema Roleta:** http://localhost:5000/roulette

### **🔑 Para Dados Reais da Roleta:**

1. **Faça login no Blaze** no navegador
2. **Execute:** `python extract_credentials.py`
3. **Reinicie o sistema** para usar credenciais reais
4. **Veja:** `USAR_CREDENCIAIS_BLAZE.md` para detalhes

## 🎮 **COMO USAR**

### **Na Página Principal:**

#### **🔄 Controles dos Sistemas:**

- **▶️ Iniciar** - Liga o sistema escolhido
- **⏹️ Parar** - Desliga o sistema
- **📊 Dashboard** - Vai para interface específica

#### **📊 Informações em Tempo Real:**

- **Status:** ON/OFF de cada sistema
- **Resultados:** Quantidade capturada
- **Indicador:** Verde = Ativo | Vermelho = Inativo

### **Sistemas Disponíveis:**

#### **🔥 Double (Blaze):**

- Monitor do jogo Double da Blaze
- Análise de padrões e sequências
- Estatísticas em tempo real
- Notificações de tendências

#### **🎲 Roleta Brasileira (Pragmatic Play):**

- Monitor oficial da API Pragmatic Play
- Números 0-36 em tempo real
- Detecção de números quentes/frios
- Alertas de sequências especiais
- Banco de dados SQLite

## 🔧 **FUNCIONALIDADES**

### **⚡ Atualizações Automáticas:**

- Status atualizado a cada 5 segundos
- Não precisa recarregar a página
- Indicador de conexão no canto superior direito

### **🎯 Controle Individual:**

- Cada sistema funciona independente
- Pode rodar ambos ao mesmo tempo
- Controle total via interface web

### **📱 Interface Responsiva:**

- Funciona em desktop e mobile
- Design moderno com animações
- Notificações toast para feedback

## ⚠️ **IMPORTANTE**

### **🔌 Conexão:**

- Mantenha a página aberta para receber atualizações
- Se desconectar, recarregue a página
- Indicador mostra status da conexão

### **🎲 Sistemas:**

- **Double:** Requer integração com sistema Blaze
- **Roleta:** Funciona direto com API Pragmatic Play
- Pode demorar alguns segundos para iniciar

### **💾 Dados:**

- Roleta salva resultados em banco SQLite
- Dados persistem entre sessões
- Histórico completo disponível

## 🆘 **RESOLUÇÃO DE PROBLEMAS**

### **❌ Erro ao Iniciar:**

```bash
# Se der erro de dependências:
pip install flask requests aiohttp

# Se der erro de porta ocupada:
# Feche outros programas na porta 5000
```

### **🔄 Sistema Não Inicia:**

- Verifique se tem internet
- Tente parar e iniciar novamente
- Recarregue a página do navegador

### **📊 Dados Não Aparecem:**

- Aguarde alguns segundos após iniciar
- Verifique se o sistema está "ON"
- Recarregue a página se necessário

## 🎯 **DICAS DE USO**

1. **🚀 Inicie pelo Dashboard Principal** - É mais fácil controlar tudo
2. **📊 Use as Estatísticas** - Acompanhe tendências e padrões
3. **🔔 Fique Atento às Notificações** - Alertas importantes aparecem
4. **💾 Dados Salvos** - Histórico fica guardado no banco
5. **🔄 Reinicie se Travar** - Pare e inicie o sistema novamente

---

**🎉 PRONTO PARA USAR!**

Agora você tem controle total dos sistemas Double e Roleta Brasileira em uma interface moderna e fácil de usar! 🚀✨
