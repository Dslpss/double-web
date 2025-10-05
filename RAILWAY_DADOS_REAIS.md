# 🚂 GUIA: COMO OBTER DADOS REAIS DA PRAGMATIC PLAY NO RAILWAY

## 🎯 OBJETIVO
Fazer o Railway usar dados REAIS da API Pragmatic Play em vez de dados simulados.

## 📋 MÉTODOS DISPONÍVEIS

### 🔥 MÉTODO 1: ENVIO MANUAL (MAIS FÁCIL)

**1. Execute localmente o script:**
```bash
python send_jsessionid_to_railway.py
```

**2. Cole seu JSESSIONID que funciona localmente**
   - Abra DevTools no browser (F12)
   - Vá em Application > Cookies > site da Pragmatic Play
   - Copie o valor do JSESSIONID

**3. O script enviará automaticamente para o Railway**

### 🌐 MÉTODO 2: VARIÁVEL DE AMBIENTE

**1. No Railway Dashboard:**
   - Vá em Variables
   - Adicione: `PRAGMATIC_JSESSIONID=seu_jsessionid_aqui`
   - Redeploy o projeto

**2. Configure o webhook secret:**
   - Adicione: `JSESSIONID_WEBHOOK_SECRET=railway_secret_2024`

### 🔄 MÉTODO 3: WEBHOOK AUTOMÁTICO

**1. Configure um sistema externo** que envia POST para:
```
POST https://baze-double-web-production.up.railway.app/api/jsessionid/update
Authorization: Bearer railway_secret_2024
Content-Type: application/json

{
  "jsessionid": "seu_jsessionid_aqui"
}
```

### 🤖 MÉTODO 4: AUTO-LOGIN (AVANÇADO)

**⚠️ ATENÇÃO: Pode violar ToS da Pragmatic Play**

**1. Configure variáveis no Railway:**
   - `PRAGMATIC_USERNAME=seu_usuario`
   - `PRAGMATIC_PASSWORD=sua_senha`

**2. O sistema tentará fazer login automático**

## 🧪 COMO TESTAR

### 1. Verificar Status do JSESSIONID:
```
GET https://baze-double-web-production.up.railway.app/api/jsessionid/status
```

### 2. Testar Interface:
```
https://baze-double-web-production.up.railway.app/roulette/api-test
```

### 3. Verificar se dados são reais:
- Se `"simulated": false` → Dados REAIS! ✅
- Se `"simulated": true` → Ainda simulados ❌

## 🔧 ENDPOINTS NOVOS

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/jsessionid/update` | POST | Recebe JSESSIONID via webhook |
| `/api/jsessionid/status` | GET | Verifica status do JSESSIONID |

## 📱 SCRIPT PARA TESTAR LOCALMENTE

```python
import requests

# Testar se Railway está com dados reais
response = requests.get("https://baze-double-web-production.up.railway.app/api/roulette/statistics/enhanced")
data = response.json()

if not data.get('simulated'):
    print("🎉 DADOS REAIS FUNCIONANDO!")
else:
    print("⚠️ Ainda usando dados simulados")
```

## ⚡ PASSOS RÁPIDOS PARA USAR AGORA

1. **Copie seu JSESSIONID local** (DevTools > Application > Cookies)
2. **Execute:** `python send_jsessionid_to_railway.py`
3. **Cole o JSESSIONID** quando solicitado
4. **Teste:** Acesse `/roulette/api-test` no Railway
5. **Verifique:** Se `simulated: false` = SUCESSO! 🎉

## 🔒 SEGURANÇA

- JSESSIONID é salvo temporariamente (24h)
- Webhook protegido por Bearer token
- Não expõe credenciais em logs
- Sistema de fallback sempre ativo

## 🚨 IMPORTANTE

- JSESSIONID pode expirar (geralmente 24h)
- Você precisará renovar periodicamente
- Sistema sempre funciona mesmo sem JSESSIONID real
- Dados simulados são realistas e funcionais

---

**🎯 OBJETIVO FINAL:** Railway com dados reais da Pragmatic Play mantendo fallback robusto!