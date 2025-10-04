# Manutenção Programada da Pragmatic Play

## Detecção

A Pragmatic Play ocasionalmente realiza manutenções programadas em seus serviços, incluindo a API GS12. Durante esses períodos, as requisições são redirecionadas para uma página de manutenção com a seguinte resposta:

```html
<script>
window.location.href = "https://client.pragmaticplaylive.net/gsstatic/scheduled-maintenance.html";
</script>
```

## Como nossa aplicação lida com isso

Nossa aplicação foi adaptada para detectar automaticamente quando a API está em manutenção e responder de forma adequada:

1. **Detecção de Redirecionamento**: O cliente GS12 identifica o padrão de redirecionamento para a página de manutenção
2. **Resposta Estruturada**: A API retorna um JSON com `status: 'maintenance'` e uma mensagem explicativa
3. **Interface Visual**: A página de teste exibe um aviso formatado sobre a manutenção
4. **Logging**: Informações detalhadas são registradas no log da aplicação

## O que fazer durante uma manutenção

Quando a API da Pragmatic Play estiver em manutenção:

1. **Aguarde**: A maioria das manutenções programadas tem duração anunciada previamente
2. **Verifique o Status**: Use a página de teste `/gs12-test` para verificar se a manutenção ainda está em andamento
3. **Notifique os Usuários**: Se sua aplicação depende desta API, exiba uma notificação adequada para os usuários

## Retomada de Serviço

Quando a manutenção for concluída:

1. A detecção automática identificará o retorno do serviço
2. A API voltará a retornar os resultados normalmente
3. Não é necessário reiniciar a aplicação ou limpar caches

## Verificação Manual

Para verificar manualmente se a manutenção foi concluída, você pode:

1. Acessar diretamente `https://gs12.pragmaticplaylive.net/game` (normalmente requer autenticação)
2. Usar a página de teste `/gs12-test` em nossa aplicação
3. Verificar os logs da aplicação para mensagens relacionadas à manutenção

## Contorno (Caso Necessário)

Se for absolutamente necessário obter dados durante uma manutenção:

1. Considere usar APIs alternativas da Pragmatic Play (se disponíveis)
2. Utilize dados em cache da aplicação para operações críticas
3. Implemente um mecanismo de fallback para outra fonte de dados

## Recuperação de Sessão

Após uma manutenção, pode ser necessário reautenticar. Nossa aplicação tenta isso automaticamente, mas você também pode:

1. Clicar em "Limpar Autenticação" na página de teste
2. Reiniciar o serviço para forçar uma nova autenticação
3. Verificar o status da autenticação nos logs da aplicação