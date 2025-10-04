# Testando a Integração Aprimorada no Railway

Este documento orienta sobre como testar a integração aprimorada do cliente de estatísticas da Pragmatic Play no ambiente Railway.

## Pré-requisitos

1. Aplicação implantada no Railway
2. Acesso ao CLI do Railway
3. (Opcional) Proxies configurados conforme [Configuração de Proxies](./PROXY_CONFIGURATION.md)

## Passo a Passo para Testes

### 1. Verificar se a aplicação está usando o cliente aprimorado

Acesse o endpoint de estatísticas da sua aplicação:

```
https://[seu-domínio-railway]/api/roulette/statistics
```

Na resposta JSON, verifique os campos:

- `client_type`: Deve mostrar "enhanced" se estiver usando o cliente aprimorado
- `is_real_data`: `true` indica dados reais da API, `false` indica dados simulados

### 2. Testar com diferentes configurações de proxy

Você pode modificar as variáveis de ambiente no Railway para testar diferentes configurações:

1. Acesse o painel do Railway para seu projeto
2. Vá para a seção "Variables"
3. Adicione/modifique as variáveis:
   - `PRAGMATIC_PROXY_ENABLED` (true/false)
   - `PRAGMATIC_PROXY_LIST` (lista de proxies)
   - `PRAGMATIC_PROXY_ROTATION` (random/sequential)
   - `PRAGMATIC_PROXY_RETRY` (número de tentativas)
4. Após salvar, reimplante a aplicação ou reinicie o serviço
5. Teste novamente o endpoint de estatísticas

### 3. Monitorar logs para verificar comportamento

Para visualizar os logs do Railway:

```bash
railway logs
```

Procure por:
- Mensagens de inicialização do cliente aprimorado: `✅ PragmaticStatisticsClientEnhanced importado com sucesso`
- Tentativas de conexão via proxy: `Tentando conexão via proxy...`
- Falhas e retentativas: `Tentativa X falhou, tentando novamente...`
- Fallback para dados simulados: `Usando dados simulados como fallback`

### 4. Teste de desempenho

Para verificar o tempo de resposta:

1. Use ferramentas como [curl](https://curl.se/) ou [Postman](https://www.postman.com/) para medir o tempo de resposta
2. Compare o desempenho com e sem proxies habilitados
3. Teste em diferentes momentos do dia para verificar consistência

Exemplo com curl:
```bash
curl -w "\nTempo total: %{time_total}s\n" https://[seu-domínio-railway]/api/roulette/statistics
```

### 5. Teste o script dedicado (local ou no Railway)

Para testes mais detalhados, você pode executar o script de teste no Railway:

```bash
# Conectar ao shell do Railway
railway shell

# Executar o script de teste
cd /app
python scripts/test_statistics_client.py --games 50 --output test_results.json
```

### 6. Verifique a integração com outros componentes

Teste outras funcionalidades da aplicação que dependem dos dados de estatísticas:
1. Visualizações de dashboard que mostram estatísticas
2. Funcionalidades de análise que usam histórico de resultados
3. Alertas ou notificações baseados em padrões detectados

## Resolução de Problemas Comuns

### Dados sempre simulados mesmo com proxy

Possíveis causas:
- Proxies bloqueados ou inacessíveis
- JSESSIONID inválido ou expirado
- API da Pragmatic Play em manutenção

Soluções:
- Verifique os logs para erros específicos
- Teste outros proxies
- Confirme que o integrador principal está conseguindo autenticar corretamente

### Erros de conexão com proxies

Possíveis causas:
- URL do proxy mal formatada
- Credenciais inválidas
- Proxy offline ou com problemas

Soluções:
- Verifique a formatação da URL: `http://[usuário]:[senha]@[host]:[porta]`
- Teste o proxy localmente antes de configurá-lo no Railway
- Use um serviço de proxy confiável e com boa disponibilidade

### Desempenho lento

Possíveis causas:
- Proxies com alta latência
- Muitas retentativas configuradas
- Problema na rede do Railway

Soluções:
- Use proxies geograficamente mais próximos do usuário final ou da API
- Ajuste o valor de `PRAGMATIC_PROXY_RETRY` para um número menor
- Configure o cache para dados de estatísticas (eles não mudam tão frequentemente)

## Próximos Passos

Após confirmar que a integração está funcionando corretamente:

1. **Monitore regularmente**: Verifique os logs periodicamente para detectar problemas
2. **Rotação de proxies**: Atualize a lista de proxies regularmente para evitar bloqueios
3. **Cache**: Considere implementar cache para reduzir chamadas à API e melhorar o desempenho
4. **Alertas**: Configure alertas para ser notificado quando a aplicação precisar fazer fallback para dados simulados