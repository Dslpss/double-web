# 🧪 TESTE DO SISTEMA INTEGRADO

## ✅ **CONFIGURAÇÃO REALIZADA:**

### **🔧 Mudanças Feitas:**

1. **`main_dashboard.py`** - Dashboard principal na porta 5000
2. **`app.py`** - Sistema Double na porta 5001
3. **Redirecionamento** - Botão Double agora redireciona para `http://localhost:5001`
4. **`start_complete_system.py`** - Script para iniciar tudo automaticamente

### **🚀 COMO TESTAR:**

#### **Opção 1: Sistema Completo (Automático)**

```bash
python start_complete_system.py
```

#### **Opção 2: Manual (Passo a Passo)**

```bash
# Terminal 1 - Sistema Double
python app.py

# Terminal 2 - Dashboard Principal
python main_dashboard.py
```

### **🌐 ACESSAR:**

1. **Dashboard Principal:** http://localhost:5000
2. **Clicar no botão "Double"** → Redireciona para http://localhost:5001
3. **Sistema Double direto:** http://localhost:5001

### **✨ RESULTADO ESPERADO:**

- ✅ Dashboard principal carrega na porta 5000
- ✅ Sistema Double carrega na porta 5001
- ✅ Botão "Ir para Dashboard" do Double funciona
- ✅ Redirecionamento automático funciona

### **🐛 SE DER ERRO:**

1. **Verificar portas:**

   ```bash
   netstat -an | findstr :5000
   netstat -an | findstr :5001
   ```

2. **Iniciar manualmente:**

   ```bash
   # Primeiro o Double
   python app.py

   # Depois o Dashboard Principal
   python main_dashboard.py
   ```

3. **Testar URLs:**
   - http://localhost:5000 (Dashboard Principal)
   - http://localhost:5001 (Sistema Double)

---

**🎯 OBJETIVO ALCANÇADO:**
O botão Double agora redireciona corretamente para o sistema Double que já estava funcionando!
