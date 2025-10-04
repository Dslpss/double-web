# Integração GS12 Pragmatic Play

## Visão Geral

Esta integração permite acessar diretamente a API GS12 da Pragmatic Play para obter resultados da roleta em tempo real.

## Funcionalidades

1. **Cliente Especializado**: `pragmatic_gs12_client.py` implementa um cliente com técnicas anti-detecção
2. **Endpoint de API**: `/api/pragmatic/gs12` fornece acesso aos dados em formato JSON
3. **Página de Teste**: `/gs12-test` permite testar a integração diretamente no navegador
4. **Autenticação**: Utiliza a mesma JSESSIONID do integrador principal da roleta

## Configurações (Railway)

Adicione as seguintes variáveis de ambiente no Railway:

```
PRAGMATIC_GS12_URL=https://gs12.pragmaticplaylive.net/game
PRAGMATIC_REQUIRE_AUTH=true
PRAGMATIC_BYPASS_DETECTION=true
PRAGMATIC_ROTATE_USER_AGENTS=true
PRAGMATIC_USE_COOKIES=true
PRAGMATIC_EMULATE_BROWSER=true
PRAGMATIC_DEBUG=true
```

## Como Usar

### 1. Acessar a API diretamente:

```
GET /api/pragmatic/gs12
```

### 2. Usar a página de teste:

Acesse `/gs12-test` no seu navegador e clique em "Testar API GS12".

## Resolução de Problemas

### Erro 401 Unauthorized

Se você receber erro 401, verifique:

1. Se o usuário está autenticado na aplicação
2. Se o roulette_integrator está inicializado e possui JSESSIONID válido

Para forçar uma nova autenticação, clique no botão "Limpar Autenticação" na página de teste.

### Erro 403 Forbidden

Pode indicar que a API da Pragmatic Play está bloqueando suas requisições. Verifique:

1. Se as configurações anti-detecção estão ativadas
2. Se você está usando um IP diferente do ambiente de desenvolvimento

### Logs e Depuração

Para ver logs detalhados, defina `PRAGMATIC_DEBUG=true` nas variáveis de ambiente.

## Técnicas Anti-Detecção

O cliente implementa várias técnicas para evitar bloqueios:

- Rotação de User-Agents
- Headers realistas de navegador
- Simulação de comportamento de navegador
- Delays aleatórios entre requisições
- Gestão de cookies
- Emulação de sessão completa