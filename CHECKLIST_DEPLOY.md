# ✅ Checklist de Deploy - Correção Erro 500 Roleta

## 📋 Fase 1: Preparação (Local)

- [x] ✅ Identificar causa do erro 500
- [x] ✅ Mover `load_dotenv()` para início do `app.py`
- [x] ✅ Adicionar logging detalhado em `init_roulette_integrator()`
- [x] ✅ Melhorar tratamento de erros no endpoint `/api/roulette/start`
- [x] ✅ Atualizar endpoint `/api/roulette/status`
- [x] ✅ Criar script de teste `test_env_vars.py`
- [x] ✅ Testar carregamento de variáveis localmente
- [x] ✅ Criar documentação `CORRECAO_ERRO_500_ROLETA.md`
- [x] ✅ Criar resumo `RESUMO_MUDANCAS_ROLETA.md`
- [x] ✅ Criar guia de deploy `GUIA_DEPLOY_RAILWAY.sh`

## 🚀 Fase 2: Deploy no Railway

### 2.1 Git e Push

- [ ] Fazer commit das mudanças
  ```bash
  git add .
  git commit -m "fix: Corrigir erro 500 na inicialização da roleta"
  ```
- [ ] Push para o Railway
  ```bash
  git push origin deploy
  ```
- [ ] Aguardar deploy automático (Railway detecta o push)

### 2.2 Verificar Variáveis de Ambiente

- [ ] Acessar Railway Dashboard
- [ ] Ir em `Variables`
- [ ] Confirmar que `PRAGMATIC_USERNAME` está configurado
- [ ] Confirmar que `PRAGMATIC_PASSWORD` está configurado
- [ ] Se não estiverem, adicionar:
  ```
  PRAGMATIC_USERNAME=dennisemannuel93@gmail.com
  PRAGMATIC_PASSWORD=Flamengo.019
  ```

### 2.3 Monitorar Logs do Deploy

- [ ] Abrir `Logs` no Railway Dashboard
- [ ] Verificar se não há erros de importação
- [ ] Procurar por: `✅ BlazeAnalyzerEnhanced importado com sucesso`
- [ ] Procurar por: `Aviso: Módulo Roleta Brasileira não disponível` (NÃO deve aparecer)

## 🧪 Fase 3: Testes no Ambiente de Produção

### 3.1 Teste do Endpoint de Status

- [ ] Abrir terminal
- [ ] Executar:
  ```bash
  curl https://baze-double-web-production.up.railway.app/api/roulette/status
  ```
- [ ] Verificar resposta esperada:
  ```json
  {
    "available": true,
    "connected": false,
    "monitoring": false,
    "has_credentials": true,
    "message": "Integrador não inicializado..."
  }
  ```

### 3.2 Teste no Browser - Console

- [ ] Acessar: `https://baze-double-web-production.up.railway.app/roulette`
- [ ] Abrir DevTools (F12)
- [ ] Ir na aba `Console`
- [ ] Verificar mensagens:
  ```
  ✅ Roulette Legacy Functions loaded
  ✅ Pattern Detector loaded
  ✅ Sistema inicializado
  ```

### 3.3 Teste do Botão "Iniciar Monitoramento"

- [ ] Clicar no botão "Iniciar Monitoramento"
- [ ] **NÃO deve aparecer erro 500 no console**
- [ ] Verificar se aparece alerta: "✅ Monitoramento iniciado com sucesso!"
- [ ] OU verificar mensagem de erro descritiva (se houver problema)

### 3.4 Verificar Logs do Railway Após Clicar

- [ ] Voltar aos logs do Railway
- [ ] Procurar por:
  ```
  🎰 [ROULETTE START] Requisição recebida
  🔧 Inicializando integrador...
  🔍 Verificando credenciais...
     Username: ✅ Configurado
     Password: ✅ Configurado
  ✅ Integrador inicializado com sucesso
  ```

## 🎯 Fase 4: Validação Final

### 4.1 Funcionalidade da Roleta

- [ ] Verificar se resultados aparecem na interface
- [ ] Verificar se o histórico carrega
- [ ] Verificar se a detecção de padrões funciona
- [ ] Verificar se os cartões de hot/cold numbers aparecem

### 4.2 Monitoramento Contínuo

- [ ] Deixar monitorando por 5 minutos
- [ ] Verificar se não há erros nos logs
- [ ] Verificar se resultados continuam atualizando

## 🐛 Troubleshooting

### Se erro 500 continuar:

#### Cenário 1: Credenciais não configuradas

**Sintoma nos logs:**

```
❌ Username: ❌ NÃO configurado
❌ Password: ❌ NÃO configurado
```

**Solução:**

- [ ] Adicionar variáveis no Railway Dashboard
- [ ] Fazer redeploy (pode ser necessário)

#### Cenário 2: Módulo não importado

**Sintoma nos logs:**

```
Aviso: Módulo Roleta Brasileira não disponível: ...
```

**Solução:**

- [ ] Verificar se `integrators/pragmatic_brazilian_roulette.py` existe
- [ ] Verificar `requirements.txt` tem `requests` e `python-dotenv`
- [ ] Verificar estrutura de pastas no repositório

#### Cenário 3: Erro de login

**Sintoma nos logs:**

```
❌ Falha ao fazer login na Roleta Brasileira
```

**Solução:**

- [ ] Verificar se credenciais estão corretas
- [ ] Testar login manualmente no site
- [ ] Verificar se conta não está bloqueada

#### Cenário 4: Erro de JSESSIONID

**Sintoma nos logs:**

```
❌ JSESSIONID não encontrado na resposta
```

**Solução:**

- [ ] Verificar se API da Pragmatic não mudou
- [ ] Verificar logs completos do erro
- [ ] Pode ser problema temporário - tentar novamente

## 📊 Critérios de Sucesso

### ✅ Deploy bem-sucedido se:

1. [ ] Sem erro 500 ao clicar em "Iniciar Monitoramento"
2. [ ] Logs mostram "✅ Integrador inicializado com sucesso"
3. [ ] JSESSIONID obtido com sucesso
4. [ ] Interface mostra "Monitoramento Ativo"
5. [ ] Resultados aparecem na tela
6. [ ] Padrões são detectados corretamente

### ⚠️ Sucesso parcial se:

- [ ] Deploy funcionou mas há erros de API
- [ ] Integrador inicializa mas não obtém dados
- [ ] Interface funciona mas dados não atualizam

### ❌ Falha se:

- [ ] Ainda há erro 500
- [ ] Módulo não carrega
- [ ] Credenciais não são reconhecidas
- [ ] JSESSIONID não é obtido

## 📝 Notas

### Logs Importantes para Guardar

Se houver problemas, salve cópias dos logs:

- [ ] Logs do deploy completo
- [ ] Logs do primeiro "Iniciar Monitoramento"
- [ ] Output do teste de curl do endpoint /status

### Documentação de Referência

- `CORRECAO_ERRO_500_ROLETA.md` - Explicação detalhada
- `RESUMO_MUDANCAS_ROLETA.md` - Lista de mudanças
- `test_env_vars.py` - Script de teste local

---

**Data Criação**: 03/10/2025  
**Versão**: 1.0  
**Status Atual**: ⏳ Aguardando deploy

---

## 🎉 Após Deploy Bem-Sucedido

- [ ] Marcar este checklist como completo
- [ ] Atualizar README.md com informações de deploy
- [ ] Criar tag de release no git
- [ ] Documentar tempo de funcionamento sem erros
- [ ] Testar em diferentes horários
- [ ] Monitorar por 24h para garantir estabilidade
