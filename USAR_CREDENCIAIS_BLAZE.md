# 🔑 USAR CREDENCIAIS DO BLAZE NA ROLETA

## 🎯 **OBJETIVO:**

Usar as mesmas credenciais (cookies/tokens) do sistema Double para acessar a API da roleta e obter dados reais.

## 🚀 **COMO FAZER:**

### **1. Fazer Login no Blaze**

1. Abra seu navegador (Chrome ou Firefox)
2. Acesse https://blaze.bet.br
3. **Faça login** com sua conta
4. Acesse o jogo **Double** ou **Roleta**
5. **Deixe a aba aberta** (importante!)

### **2. Extrair Credenciais**

```bash
python extract_credentials.py
```

**✅ O que acontece:**

- 🔍 Procura cookies do Blaze no navegador
- 📋 Extrai tokens de autenticação
- 💾 Salva em `blaze_credentials.json`
- 🔑 Configura headers para API

### **3. Reiniciar Sistema**

```bash
# Parar sistema atual (Ctrl+C)
python start_complete_system.py
```

### **4. Testar Roleta**

1. Acesse http://localhost:5000
2. Clique em **"Roleta"**
3. Verifique se recebe **dados reais** (não simulados)

## 🔧 **COMO FUNCIONA:**

### **Antes (Sem Credenciais):**

```
❌ Erro HTTP: 401
🔄 Tentando continuar com dados simulados...
🎲 Resultado simulado: 15 ⚫ PRETO
```

### **Depois (Com Credenciais):**

```
🔑 Usando headers com autenticação do navegador
✅ API respondeu com sucesso
🎲 Novo resultado real: 7 🔴 VERMELHO
```

## 📁 **ARQUIVOS CRIADOS:**

- **`auth_extractor.py`** - Extrai credenciais do navegador
- **`extract_credentials.py`** - Script fácil de usar
- **`blaze_credentials.json`** - Credenciais salvas (criado automaticamente)

## ⚠️ **IMPORTANTE:**

### **Segurança:**

- ✅ Credenciais ficam **apenas no seu computador**
- ✅ **Não são enviadas** para nenhum servidor
- ✅ Usadas apenas para **acessar APIs do Blaze**

### **Validade:**

- 🕐 Credenciais **expiram** após algumas horas
- 🔄 **Re-execute** `extract_credentials.py` se parar de funcionar
- 💡 Mantenha o **navegador aberto** com login ativo

## 🐛 **RESOLUÇÃO DE PROBLEMAS:**

### **"Nenhum cookie encontrado":**

1. Certifique-se de estar **logado no Blaze**
2. **Feche o navegador** completamente
3. **Abra novamente** e faça login
4. Execute `extract_credentials.py` novamente

### **"Erro ao extrair credenciais":**

1. Execute como **administrador**
2. Verifique se Chrome/Firefox está **instalado**
3. Tente com **navegador diferente**

### **"API ainda retorna 401":**

1. **Re-extraia** as credenciais
2. Verifique se está **logado** no navegador
3. Tente **acessar o jogo** no navegador primeiro

## 🎉 **RESULTADO ESPERADO:**

Com as credenciais corretas, o sistema da roleta deve:

- ✅ **Conectar** na API real do Pragmatic Play
- ✅ **Receber dados reais** da roleta
- ✅ **Salvar no banco** resultados verdadeiros
- ✅ **Mostrar estatísticas** precisas
- ✅ **Funcionar** como o sistema Double

---

**💡 DICA:** Execute `extract_credentials.py` sempre que o sistema parar de receber dados reais!
