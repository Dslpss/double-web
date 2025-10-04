# Configuração de Proxies para APIs Externas

Este documento explica como configurar proxies para melhorar a resiliência das APIs externas no ambiente de produção do Railway.

## Por que usar proxies?

Quando a aplicação é implantada no Railway, ela pode enfrentar os seguintes problemas:

1. **Restrições de IP:** Algumas APIs externas (como a Pragmatic Play) podem bloquear solicitações de IPs de datacenters ou serviços de hospedagem em nuvem.
2. **Rate Limiting:** APIs podem limitar o número de solicitações de um único IP, especialmente quando compartilhado entre várias instâncias do Railway.
3. **Bloqueios Geográficos:** Certas APIs podem restringir o acesso com base na localização geográfica do IP.

## Configuração de Proxies no Railway

### Variáveis de Ambiente

O cliente aprimorado de estatísticas suporta o uso de proxies através das seguintes variáveis de ambiente:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `PRAGMATIC_PROXY_ENABLED` | Habilita o uso de proxies (true/false) | `true` |
| `PRAGMATIC_PROXY_LIST` | Lista de proxies separados por vírgulas | `http://user:pass@proxy1.com:8080,http://user:pass@proxy2.com:8080` |
| `PRAGMATIC_PROXY_ROTATION` | Método de rotação de proxies (random, sequential) | `random` |
| `PRAGMATIC_PROXY_RETRY` | Número máximo de tentativas com diferentes proxies | `3` |

### Como Adicionar no Railway

1. Acesse o painel do Railway para seu projeto
2. Vá para a seção "Variables"
3. Adicione as variáveis de ambiente conforme necessário
4. Reimplante a aplicação ou reinicie o serviço

## Provedores de Proxy Recomendados

Existem vários serviços que oferecem proxies HTTP/HTTPS que podem ser utilizados:

- [Bright Data](https://brightdata.com/) - Oferece proxies residenciais e de datacenter
- [Smartproxy](https://smartproxy.com/) - Proxies residenciais com boa cobertura global
- [Oxylabs](https://oxylabs.io/) - Serviço de proxy com opções de rotação automática
- [ProxyMesh](https://proxymesh.com/) - Solução simples com bom custo-benefício

## Formato de URL de Proxy

O formato correto para configurar a URL do proxy é:

```
http://[usuário]:[senha]@[host]:[porta]
```

Para proxies sem autenticação:

```
http://[host]:[porta]
```

## Exemplos de Configuração

### Exemplo Básico

```
PRAGMATIC_PROXY_ENABLED=true
PRAGMATIC_PROXY_LIST=http://user:pass@proxy1.example.com:8080
PRAGMATIC_PROXY_ROTATION=random
PRAGMATIC_PROXY_RETRY=3
```

### Múltiplos Proxies

```
PRAGMATIC_PROXY_ENABLED=true
PRAGMATIC_PROXY_LIST=http://user1:pass1@proxy1.example.com:8080,http://user2:pass2@proxy2.example.com:8081
PRAGMATIC_PROXY_ROTATION=sequential
PRAGMATIC_PROXY_RETRY=5
```

## Como Testar a Conexão

Para verificar se a configuração de proxy está funcionando corretamente:

1. Acesse a rota `/api/roulette/statistics` após configurar os proxies
2. Verifique se a resposta inclui `"is_real_data": true`, o que indica que os dados estão sendo obtidos diretamente da API
3. Monitore os logs do Railway para mensagens relacionadas ao uso de proxies

## Solução de Problemas

- **Erro "Cannot connect to proxy"**: Verifique se o endereço e porta do proxy estão corretos
- **Erro "Proxy Authentication Required"**: Confirme se as credenciais do proxy estão corretas
- **Nenhum dado real retornado**: Pode indicar que todos os proxies configurados estão sendo bloqueados

---

**Importante**: Mantenha suas credenciais de proxy seguras e não as inclua em arquivos de código-fonte ou repositórios públicos.