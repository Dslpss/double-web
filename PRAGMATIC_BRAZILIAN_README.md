# Integrador da Roleta Brasileira - Pragmatic Play

Sistema completo para capturar resultados da **Roleta Brasileira** da Pragmatic Play com **renovação automática de JSESSIONID**.

## 🎯 Características

✅ **Renovação Automática de Sessão** - JSESSIONID é renovado automaticamente quando expira  
✅ **Login Automático** - Faz login usando suas credenciais quando necessário  
✅ **Monitoramento Contínuo** - Busca novos resultados em intervalos configuráveis  
✅ **Integração com Banco de Dados** - Salva resultados no DatabaseManager do sistema  
✅ **Tratamento de Erros** - Recupera automaticamente de erros de conexão

## 📁 Arquivos

```
integrators/
├── pragmatic_brazilian_roulette.py  # Classe principal do integrador
└── pragmatic_brazilian_sync.py      # Sincronizador com o sistema

test_pragmatic_brazilian.py          # Script de teste
PRAGMATIC_BRAZILIAN_README.md        # Este arquivo
```

## 🚀 Como Usar

### 1. Teste Rápido

Teste o integrador para verificar se tudo está funcionando:

```bash
python test_pragmatic_brazilian.py
```

Este comando irá:

- Fazer login
- Obter JSESSIONID
- Buscar últimos 20 resultados
- Mostrar estatísticas
- Testar renovação automática de sessão

### 2. Teste de Monitoramento Contínuo

Para testar o monitoramento em tempo real:

```bash
python test_pragmatic_brazilian.py monitor
```

Isso irá monitorar continuamente e mostrar novos resultados conforme aparecem.

### 3. Sincronização com Banco de Dados

#### Sincronização Única

```bash
python integrators/pragmatic_brazilian_sync.py \
    --username "seu_email@exemplo.com" \
    --password "sua_senha" \
    --once
```

#### Monitoramento Contínuo

```bash
python integrators/pragmatic_brazilian_sync.py \
    --username "seu_email@exemplo.com" \
    --password "sua_senha" \
    --interval 30
```

Parâmetros:

- `--username`: Seu email de login
- `--password`: Sua senha
- `--interval`: Intervalo entre buscas em segundos (padrão: 30)
- `--once`: Sincronizar apenas uma vez e sair
- `--db`: Caminho do banco de dados (padrão: pragmatic_roulette.db)

## 💻 Uso no Código

### Exemplo Básico

```python
from integrators.pragmatic_brazilian_roulette import PragmaticBrazilianRoulette

# Criar integrador
integrator = PragmaticBrazilianRoulette(
    username="seu_email@exemplo.com",
    password="sua_senha"
)

# Fazer login (obtém JSESSIONID automaticamente)
if integrator.login():
    # Buscar histórico
    history = integrator.get_history(num_games=100)

    for result in history:
        print(f"{result['number']} {result['color']}")
```

### Monitoramento com Callback

```python
def on_new_result(result):
    print(f"Novo: {result['number']} {result['color']}")

# Monitorar continuamente
integrator.monitor_continuous(
    callback=on_new_result,
    interval=30  # Checar a cada 30 segundos
)
```

### Com Sincronização ao Banco

```python
from integrators.pragmatic_brazilian_sync import PragmaticBrazilianSync

# Criar sincronizador
sync = PragmaticBrazilianSync(
    username="seu_email@exemplo.com",
    password="sua_senha",
    db_path="pragmatic_roulette.db"
)

# Sincronizar uma vez
count = sync.sync_once()
print(f"{count} novos resultados")

# Ou monitorar continuamente
sync.monitor_continuous(interval=30)
```

## 🔄 Como Funciona a Renovação Automática

1. **Login Inicial**: Ao fazer login, o sistema obtém:

   - `tokenCassino` da API de autenticação
   - `JSESSIONID` ao lançar o jogo

2. **Verificação Automática**: Antes de cada requisição, verifica:

   - Se JSESSIONID existe
   - Se ainda não expirou (padrão: 1 hora)

3. **Renovação**: Se necessário, faz:

   - Novo login para obter token atualizado
   - Novo lançamento do jogo para obter JSESSIONID novo

4. **Tentativa Automática**: Se uma requisição falha:
   - Remove JSESSIONID atual
   - Tenta novamente (fazendo login automaticamente)

## 📊 Formato dos Resultados

```python
{
    'id': '10041463312',                    # ID do jogo
    'number': 6,                            # Número que saiu (0-36)
    'color': 'black',                       # Cor (red, black, green)
    'raw_result': '6  Black',               # Resultado bruto da API
    'game_type': '0000000000000001',        # Tipo do jogo
    'bet_count': 0,                         # Número de apostas
    'player_count': 0,                      # Número de jogadores
    'timestamp': '2025-10-03T12:32:17',     # Timestamp
    'source': 'pragmatic_brazilian_roulette' # Fonte dos dados
}
```

## 🗄️ Integração com Banco de Dados

O sincronizador converte os resultados para o formato do sistema:

```python
{
    'id': '10041463312',
    'created_at': '2025-10-03T12:32:17',
    'color': 'black',           # Convertido para formato Blaze
    'roll': 8,                  # Número convertido (0-14)
    'server_seed': 'pragmatic_10041463312',
    'timestamp': 1696337537.123,
    'source': 'pragmatic_brazilian_roulette',
    'original_number': 6,       # Número original (0-36)
    'original_color': 'black'   # Cor original
}
```

## ⚙️ Configurações

No arquivo `pragmatic_brazilian_roulette.py`, você pode ajustar:

```python
# Duração da sessão (em segundos)
self.session_duration = 3600  # 1 hora

# ID da mesa
self.table_id = "rwbrzportrwa16rg"  # Roleta Brasileira

# URLs
self.login_url = "https://loki1.weebet.tech/auth/login"
self.game_launch_base = "https://games.pragmaticplaylive.net"
```

## 🔍 Logs

O sistema usa logging do Python. Para ver logs detalhados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Níveis de log:

- `INFO`: Operações normais (login, busca de histórico)
- `WARNING`: Alertas (sem resultados novos)
- `ERROR`: Erros (falha no login, erro na API)
- `DEBUG`: Detalhes técnicos

## 🛠️ Solução de Problemas

### "Erro no login"

- Verifique suas credenciais
- Confirme que a conta está ativa
- Tente fazer login manual no site

### "JSESSIONID não encontrado"

- Pode ser um problema temporário da API
- Aguarde alguns minutos e tente novamente

### "Nenhum resultado obtido"

- Verifique sua conexão com a internet
- Confirme que o jogo está ativo (horário de funcionamento)

### Sessão expira muito rápido

- Ajuste `session_duration` no código
- Reduza o intervalo de monitoramento

## 📝 Notas Importantes

1. **Credenciais**: Nunca commite suas credenciais no Git
2. **Rate Limiting**: Não faça requisições muito frequentes (mínimo 10s)
3. **Horário**: A roleta pode ter horários específicos de funcionamento
4. **Manutenção**: Em caso de manutenção do site, o integrador irá falhar

## 🎲 Próximos Passos

1. ✅ Testar o integrador
2. ✅ Configurar monitoramento contínuo
3. 📊 Integrar com seu sistema de análise
4. 🤖 Adicionar análise de padrões
5. 🔔 Configurar alertas para padrões detectados

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs
2. Teste com o script de teste
3. Confirme que o site está funcionando
4. Ajuste os parâmetros conforme necessário

---

**Desenvolvido para captura confiável de resultados da Roleta Brasileira Pragmatic Play com renovação automática de sessão! 🎰**
