#!/bin/bash

# 🚀 Script de Deploy para Railway - Correção Erro 500 Roleta
# Execute este script para fazer o deploy das correções

echo "============================================================"
echo "🚀 DEPLOY - Correção Erro 500 Roleta"
echo "============================================================"
echo ""

# 1. Verificar status do git
echo "1️⃣ Verificando status do repositório..."
git status
echo ""

# 2. Adicionar arquivos modificados
echo "2️⃣ Adicionando arquivos ao git..."
git add app.py
git add test_env_vars.py
git add CORRECAO_ERRO_500_ROLETA.md
git add RESUMO_MUDANCAS_ROLETA.md
git add GUIA_DEPLOY_RAILWAY.sh
echo "✅ Arquivos adicionados"
echo ""

# 3. Commit
echo "3️⃣ Fazendo commit..."
git commit -m "fix: Corrigir erro 500 na inicialização da roleta

- Move load_dotenv() para início do app.py
- Adiciona logging detalhado em init_roulette_integrator()
- Melhora tratamento de erros no endpoint /api/roulette/start
- Remove inicialização automática do endpoint /api/roulette/status
- Adiciona verificação de credenciais com logs
- Cria script de teste de variáveis de ambiente
- Adiciona documentação completa das correções

Refs: #railway #roleta #error500"
echo ""

# 4. Push para Railway
echo "4️⃣ Fazendo push para o Railway (branch deploy)..."
echo "⚠️  O Railway detectará automaticamente e iniciará o deploy"
echo ""
read -p "Pressione ENTER para continuar com o push ou CTRL+C para cancelar..."
git push origin deploy
echo ""

echo "============================================================"
echo "✅ DEPLOY INICIADO COM SUCESSO!"
echo "============================================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Acesse o Railway Dashboard:"
echo "   https://railway.app/dashboard"
echo ""
echo "2. Verifique as variáveis de ambiente:"
echo "   - PRAGMATIC_USERNAME"
echo "   - PRAGMATIC_PASSWORD"
echo ""
echo "3. Monitore os logs do deploy:"
echo "   Dashboard → Seu Projeto → Logs"
echo ""
echo "4. Procure por estas mensagens nos logs:"
echo "   ✅ '🎰 [ROULETTE START] Requisição recebida'"
echo "   ✅ '✅ Integrador inicializado com sucesso'"
echo ""
echo "5. Teste no browser:"
echo "   - Acesse: https://baze-double-web-production.up.railway.app/roulette"
echo "   - Clique em 'Iniciar Monitoramento'"
echo "   - Verifique se não há erro 500"
echo ""
echo "============================================================"
echo ""
echo "🔍 TROUBLESHOOTING:"
echo ""
echo "Se continuar dando erro 500:"
echo ""
echo "1. Verifique os logs do Railway:"
echo "   Procure por mensagens com ❌ ou ⚠️"
echo ""
echo "2. Confirme as credenciais no Railway Dashboard:"
echo "   Variables → PRAGMATIC_USERNAME e PRAGMATIC_PASSWORD"
echo ""
echo "3. Teste o endpoint de status:"
echo "   curl https://baze-double-web-production.up.railway.app/api/roulette/status"
echo ""
echo "4. Consulte a documentação:"
echo "   - CORRECAO_ERRO_500_ROLETA.md"
echo "   - RESUMO_MUDANCAS_ROLETA.md"
echo ""
echo "============================================================"
