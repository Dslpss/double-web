# 🚀 Comandos Rápidos - Deploy Railway

## 📦 Deploy Completo

```bash
# 1. Adicionar todos os arquivos modificados
git add app.py test_env_vars.py *.md GUIA_DEPLOY_RAILWAY.sh

# 2. Commit
git commit -m "fix: Corrigir erro 500 na inicialização da roleta"

# 3. Push para Railway
git push origin deploy
```

## 🧪 Testes Rápidos

### Teste Local de Variáveis

```bash
python test_env_vars.py
```

### Teste Endpoint de Status (Produção)

```bash
curl https://baze-double-web-production.up.railway.app/api/roulette/status
```

### Teste com Pretty Print (JSON formatado)

```bash
curl https://baze-double-web-production.up.railway.app/api/roulette/status | python -m json.tool
```

## 📊 Monitoramento

### Ver logs em tempo real no Railway

1. Acesse: https://railway.app/dashboard
2. Clique no seu projeto
3. Clique em "Logs"
4. Use filtro para buscar: `ROULETTE START`

### Grep nos logs (se tiver Railway CLI)

```bash
railway logs | grep "ROULETTE"
railway logs | grep "❌"
railway logs | grep "✅"
```

## 🔍 Diagnóstico

### Verificar todas as variáveis configuradas

No Railway Dashboard → Variables, deve ter:

- `PRAGMATIC_USERNAME`
- `PRAGMATIC_PASSWORD`
- `SECRET_KEY`
- `PORT`
- `FLASK_ENV`

### Testar integrador manualmente (Python REPL)

```python
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv('PRAGMATIC_USERNAME')
password = os.getenv('PRAGMATIC_PASSWORD')

print(f"Username: {username}")
print(f"Password: {'***' if password else 'NOT SET'}")
```

### Verificar importação do módulo

```python
try:
    from integrators.pragmatic_brazilian_roulette import PragmaticBrazilianRoulette
    print("✅ Módulo importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
```

## 🐛 Troubleshooting

### Se der erro de módulo não encontrado

```bash
# Verificar se arquivo existe
ls -la integrators/pragmatic_brazilian_roulette.py

# Verificar requirements.txt
cat requirements.txt | grep -E "(requests|dotenv)"
```

### Se der erro de credenciais

```bash
# No Railway Dashboard
# 1. Vá em Variables
# 2. Adicione:
PRAGMATIC_USERNAME=dennisemannuel93@gmail.com
PRAGMATIC_PASSWORD=Flamengo.019

# 3. Salve e aguarde redeploy automático
```

### Se logs não aparecerem

```bash
# Verificar se app está rodando
curl -I https://baze-double-web-production.up.railway.app/

# Deve retornar: HTTP/2 200
```

## 🔄 Rollback (se necessário)

### Voltar para commit anterior

```bash
# Ver últimos commits
git log --oneline -5

# Voltar para commit específico
git reset --hard COMMIT_HASH

# Force push (cuidado!)
git push -f origin deploy
```

### Criar branch de backup antes do deploy

```bash
git checkout -b backup-antes-fix-500
git push origin backup-antes-fix-500
git checkout deploy
```

## 📱 Testes no Browser

### Abrir página da roleta

```
https://baze-double-web-production.up.railway.app/roulette
```

### Console do browser (F12 → Console)

Comandos úteis:

```javascript
// Ver status atual
fetch("/api/roulette/status")
  .then((r) => r.json())
  .then(console.log);

// Tentar iniciar
fetch("/api/roulette/start", { method: "POST" })
  .then((r) => r.json())
  .then(console.log);

// Ver resultados
fetch("/api/roulette/results")
  .then((r) => r.json())
  .then(console.log);
```

## 📸 Evidências para Documentar

### Screenshots necessários:

1. [ ] Railway Dashboard mostrando deploy bem-sucedido
2. [ ] Variables configuradas no Railway
3. [ ] Logs mostrando "✅ Integrador inicializado"
4. [ ] Console do browser sem erro 500
5. [ ] Interface mostrando "Monitoramento Ativo"

### Logs para salvar:

```bash
# Salvar logs completos do deploy
railway logs > logs_deploy_$(date +%Y%m%d_%H%M%S).txt

# Ou copiar manualmente do Dashboard
```

## 🎯 Checklist Rápido

Antes do deploy:

- [x] ✅ Código testado localmente
- [x] ✅ Variáveis de ambiente verificadas
- [x] ✅ Documentação criada
- [ ] ⏳ Commit feito
- [ ] ⏳ Push para Railway

Após o deploy:

- [ ] ⏳ Variáveis verificadas no Railway
- [ ] ⏳ Logs monitorados
- [ ] ⏳ Endpoint /status testado
- [ ] ⏳ Botão "Iniciar" testado
- [ ] ⏳ Sem erro 500
- [ ] ⏳ Interface funcionando

## 📞 Suporte

Se precisar de ajuda:

1. Consulte `CORRECAO_ERRO_500_ROLETA.md`
2. Consulte `CHECKLIST_DEPLOY.md`
3. Verifique logs do Railway
4. Teste endpoints individualmente

---

## 🎉 Deploy Bem-Sucedido!

Se tudo funcionou:

```bash
# Criar tag de release
git tag -a v1.0.1-fix-roulette-500 -m "Fix: Corrigido erro 500 na inicialização da roleta"
git push origin v1.0.1-fix-roulette-500

# Comemorar! 🎉
echo "✅ Deploy bem-sucedido! 🚀"
```

---

**Última atualização**: 03/10/2025  
**Arquivo**: `COMANDOS_RAPIDOS.md`
