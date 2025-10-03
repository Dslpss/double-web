# 🔐 Configuração de Credenciais - Pragmatic Play

## ✅ Configuração Atual

As credenciais da Roleta Brasileira agora são armazenadas de forma segura no arquivo `.env` (que NÃO é commitado no Git).

## 📝 Como Configurar

### 1. Copie o arquivo de exemplo:

```bash
cp env.example .env
```

### 2. Edite o arquivo `.env` e configure suas credenciais:

```bash
# Pragmatic Play - Roleta Brasileira
PRAGMATIC_USERNAME=seu_email@exemplo.com
PRAGMATIC_PASSWORD=sua_senha
```

### 3. Pronto! Os scripts vão carregar automaticamente do `.env`

## 🔒 Arquivos de Credenciais

### ✅ Commitados no Git:

- `env.example` - Template com exemplos (SEM credenciais reais)
- `*.py` - Códigos que leem do `.env`

### ❌ NÃO Commitados no Git:

- `.env` - Suas credenciais reais (protegido pelo `.gitignore`)

## 🚀 Como Usar

Agora todos os scripts carregam credenciais do `.env` automaticamente:

```bash
# Teste rápido
python test_pragmatic_brazilian.py

# Monitoramento
python test_pragmatic_brazilian.py monitor

# Sincronização
python integrators/pragmatic_brazilian_sync.py --interval 30
```

## ⚠️ Importante

- ✅ O arquivo `.env` está no `.gitignore` e nunca será commitado
- ✅ Suas credenciais ficam apenas no seu computador
- ✅ Em produção, use variáveis de ambiente do sistema
- ✅ `python-dotenv` foi adicionado ao `requirements.txt`

## 🔄 Produção / CI/CD

Em servidores de produção, configure as variáveis de ambiente:

```bash
export PRAGMATIC_USERNAME="seu_email@exemplo.com"
export PRAGMATIC_PASSWORD="sua_senha"
```

Ou no Railway/Heroku/Vercel:

- Adicione as variáveis no painel de configuração
- Não precisa do arquivo `.env`

---

**✅ Agora está seguro para commitar!** 🎉🔒
