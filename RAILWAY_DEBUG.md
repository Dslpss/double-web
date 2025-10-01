# 🚀 Debug do Railway - Blaze Web

## ❌ Problema Identificado

A aplicação mostrava "Erro: Integrador PlayNabets não disponível" no Railway.

## ✅ Correções Aplicadas

### 1. Arquivos `__init__.py` Adicionados

O problema principal era que o Python não reconhecia `shared/src` como um pacote:

- `shared/src/__init__.py`
- `shared/src/analysis/__init__.py`
- `shared/src/api/__init__.py`
- `shared/src/database/__init__.py`
- `shared/src/ml/__init__.py`
- `shared/src/models/__init__.py`
- `shared/src/notifications/__init__.py`
- `shared/src/utils/__init__.py`
- E outros módulos...

### 2. Logs Melhorados

- ✅ Logs detalhados na inicialização do analyzer
- ✅ Logs detalhados na inicialização do PlayNabets
- ✅ Nova rota `/api/diagnostics` para debug completo
- ✅ Melhores mensagens de erro com stack trace

### 3. Rota de Diagnóstico

**Nova rota**: `/api/diagnostics`

Acesse `https://seu-dominio.railway.app/api/diagnostics` para ver:

- ✅ Status das importações de todos os módulos
- ✅ Arquivos existentes no filesystem
- ✅ Variáveis de ambiente
- ✅ Erros detalhados com traceback

### 4. Requirements.txt Atualizado

- ✅ Versões flexíveis para evitar conflitos de build
- ✅ Gunicorn incluído para produção

## 🔍 Como Testar

### 1. Verificar Status Básico

```bash
curl https://seu-dominio.railway.app/api/status
```

### 2. Verificar Diagnósticos Completos

```bash
curl https://seu-dominio.railway.app/api/diagnostics
```

### 3. Verificar Página Principal

```bash
curl https://seu-dominio.railway.app/
```

## 📊 Próximos Passos de Deploy

### Opção 1: Deploy Gradual (Recomendado)

1. **Teste com App Simples**:

   ```
   # Procfile temporário
   web: python simple_app.py
   ```

2. **Se funcionar, usar App Completo**:

   ```
   # Procfile final
   web: python app.py
   ```

3. **Para produção, usar Gunicorn**:
   ```
   # Procfile produção
   web: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

### Opção 2: Deploy Direto

```
# Procfile atual
web: python app.py
```

## 🛠️ Comandos de Debug no Railway

### Acessar Logs do Railway:

1. Railway Dashboard → Seu Projeto → Deployments → View Logs

### Verificar Rotas de Debug:

- `/api/diagnostics` - Diagnóstico completo do sistema
- `/api/status` - Status dos módulos principais
- `/` - Página principal da aplicação

## 🔧 Variáveis de Ambiente Necessárias

No Railway Dashboard → Settings → Variables:

```bash
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_segura_aqui
PORT=5000  # (Railway define automaticamente)
```

## 🐛 Troubleshooting

### Se ainda aparecer "Integrador PlayNabets não disponível":

1. **Verificar logs do Railway** para erros de importação
2. **Acessar `/api/diagnostics`** para ver quais módulos falharam
3. **Verificar se todos os arquivos foram enviados** com `git status`

### Comandos para re-deploy:

```bash
git add .
git commit -m "Fix: Railway deployment corrections"
git push origin deploy
```

### Se precisar reverter para teste simples:

1. Alterar Procfile para: `web: python simple_app.py`
2. Commit e push
3. Verificar se `https://seu-dominio.railway.app/health` responde

## ✨ Status Atual

- ✅ Imports corrigidos localmente
- ✅ App funcionando localmente
- ✅ Arquivos `__init__.py` criados
- ✅ Logs melhorados
- ✅ Rota de diagnóstico criada
- ✅ Requirements.txt atualizado
- ✅ Commit enviado para o GitHub

**Próximo passo**: Verificar se o deploy no Railway agora funciona!
