# 🔒 Guia de Segurança - Blaze Web

## ⚠️ AÇÕES OBRIGATÓRIAS ANTES DO DEPLOY

### 1. **Alterar Credenciais Padrão**

```bash
# As senhas padrão DEVEM ser alteradas:
# admin / admin123  →  admin / sua_senha_segura
# user / user123    →  user / sua_senha_segura
```

### 2. **Configurar Variáveis de Ambiente**

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

### 3. **Gerar Nova Chave Secreta**

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. **Configurar Banco de Dados Real**

- Substitua o sistema de usuários em memória por um banco real
- Use PostgreSQL ou MySQL em produção
- Configure backup automático

## 🛡️ Configurações de Segurança

### Variáveis de Ambiente Obrigatórias

```env
SECRET_KEY=sua_chave_secreta_aqui
DB_PASSWORD=sua_senha_do_banco
SMTP_PASSWORD=sua_senha_do_email
```

### Arquivos que NUNCA devem ser commitados

- `.env`
- `config.py` (use `config_example.py`)
- `*.db`
- `logs/`
- `data/`

## 🔐 Melhorias de Segurança Implementadas

### ✅ Implementado

- [x] Arquivo `.gitignore` criado
- [x] Arquivo `env.example` criado
- [x] Chave secreta configurável via env
- [x] Senhas hasheadas com SHA-256
- [x] Tokens seguros com `secrets.token_urlsafe()`
- [x] Sistema de autenticação com JWT

### 🔄 Recomendado para Produção

- [ ] Usar bcrypt em vez de SHA-256
- [ ] Implementar rate limiting
- [ ] Adicionar HTTPS obrigatório
- [ ] Configurar CORS adequadamente
- [ ] Implementar logs de auditoria
- [ ] Adicionar validação de entrada
- [ ] Configurar backup automático

## 🚨 Avisos Importantes

1. **NUNCA** commite o arquivo `.env`
2. **SEMPRE** altere as senhas padrão
3. **SEMPRE** use HTTPS em produção
4. **SEMPRE** configure backup do banco
5. **SEMPRE** monitore logs de acesso

## 📞 Suporte de Segurança

Para reportar vulnerabilidades de segurança, entre em contato através de:

- Email: security@seudominio.com
- GitHub Issues (privado)

---

**⚠️ LEMBRE-SE: Este é um projeto de demonstração. Para uso em produção, implemente todas as medidas de segurança recomendadas.**
