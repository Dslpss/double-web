# Sistema de Controle de Alertas

## 📋 Descrição

Foi implementado um sistema de controle de alertas que permite ao usuário escolher que tipos de alertas deseja receber:

- **🤖 Alertas do Sistema**: Alertas automáticos gerados pelo sistema de análise
- **⚙️ Padrões Customizados**: Alertas baseados nos padrões personalizados criados pelo usuário

## 🎛️ Funcionalidades

### 1. Painel de Configuração

- Localizado na página `/custom-patterns`
- Switches para habilitar/desabilitar cada tipo de alerta
- Status visual mostrando quais alertas estão ativos
- Botão de teste para verificar configurações

### 2. Persistência de Configurações

- Configurações salvas automaticamente no navegador (localStorage)
- Sincronização com servidor via API REST
- Carregamento automático das configurações ao abrir a página

### 3. Integração com Sistema de Alertas

- O `AlertManager` verifica configurações antes de exibir alertas
- Alertas desabilitados não aparecem na interface
- Log no console para debugging

## 🔧 Como Usar

### Acessar Configurações

1. Vá para a página "Padrões Personalizados" (`/custom-patterns`)
2. Na seção "Configuração de Alertas", use os switches para:
   - ✅ Habilitar "Alertas do Sistema" para receber alertas automáticos
   - ✅ Habilitar "Padrões Customizados" para receber alertas dos seus padrões

### Testar Configurações

1. Clique no botão "🧪 Testar" ao lado dos switches
2. Será exibido um resumo das configurações ativas
3. Um alerta de exemplo aparecerá para demonstrar como funcionará

### Cenários de Uso

#### 🎯 Cenário 1: Todos os Alertas Ativos

- **Sistema**: ✅ Ativo
- **Custom**: ✅ Ativo
- **Resultado**: Recebe alertas automáticos E dos padrões customizados

#### 🤖 Cenário 2: Apenas Sistema

- **Sistema**: ✅ Ativo
- **Custom**: ❌ Inativo
- **Resultado**: Recebe apenas alertas automáticos do sistema

#### ⚙️ Cenário 3: Apenas Customizados

- **Sistema**: ❌ Inativo
- **Custom**: ✅ Ativo
- **Resultado**: Recebe apenas alertas dos padrões que você criou

#### 🚫 Cenário 4: Todos Desabilitados

- **Sistema**: ❌ Inativo
- **Custom**: ❌ Inativo
- **Resultado**: Nenhum alerta será exibido (modo silencioso)

## 🛠️ API Endpoints

### GET `/api/alert-settings`

Recupera configurações atuais do usuário.

**Resposta:**

```json
{
  "success": true,
  "settings": {
    "systemAlerts": true,
    "customAlerts": true,
    "timestamp": "2025-10-07T16:57:13.314166"
  }
}
```

### POST `/api/alert-settings`

Salva novas configurações do usuário.

**Payload:**

```json
{
  "systemAlerts": true,
  "customAlerts": false
}
```

**Resposta:**

```json
{
  "success": true,
  "message": "Configurações de alerta salvas com sucesso",
  "settings": {
    "systemAlerts": true,
    "customAlerts": false,
    "timestamp": "2025-10-07T16:57:15.390253"
  }
}
```

## 💡 Benefícios

1. **🎯 Controle Total**: Usuário decide quais alertas receber
2. **🔇 Modo Foco**: Pode silenciar alertas não desejados
3. **⚙️ Personalização**: Usar apenas padrões próprios se preferir
4. **🧪 Teste Fácil**: Botão de teste para verificar configurações
5. **💾 Persistente**: Configurações mantidas entre sessões

## 🔍 Debugging

Para verificar se os alertas estão funcionando:

1. Abra o console do navegador (F12)
2. Procure por logs como:
   - `"Alerta system desabilitado. Padrão não será exibido"`
   - `"Alerta custom desabilitado. Padrão não será exibido"`
3. Use o botão "Testar" para verificar configurações

## 📱 Interface Visual

O painel mostra diferentes status com cores:

- 🟢 **Verde**: Ambos os alertas ativos
- 🔵 **Azul**: Apenas alertas do sistema
- 🟡 **Amarelo**: Apenas padrões customizados
- 🔴 **Vermelho**: Todos os alertas desabilitados

---

**Desenvolvido em:** 07/10/2025  
**Versão:** 1.0.0
