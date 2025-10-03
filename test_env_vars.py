#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar se as variáveis de ambiente estão sendo carregadas
"""

import os
from dotenv import load_dotenv

print("=" * 60)
print("🔍 TESTE DE VARIÁVEIS DE AMBIENTE")
print("=" * 60)

# Carregar .env
print("\n1. Carregando .env...")
load_dotenv()
print("✅ load_dotenv() executado")

# Verificar variáveis
print("\n2. Verificando variáveis de ambiente:")
print("-" * 60)

env_vars = {
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'DEBUG': os.getenv('DEBUG'),
    'PORT': os.getenv('PORT'),
    'PRAGMATIC_USERNAME': os.getenv('PRAGMATIC_USERNAME'),
    'PRAGMATIC_PASSWORD': os.getenv('PRAGMATIC_PASSWORD'),
}

for key, value in env_vars.items():
    if value:
        # Mostrar apenas parte do valor por segurança
        display_value = value[:20] + "..." if len(value) > 20 else value
        if 'PASSWORD' in key:
            display_value = "***"
        print(f"✅ {key:25s} = {display_value}")
    else:
        print(f"❌ {key:25s} = NÃO CONFIGURADO")

print("\n" + "=" * 60)

# Verificar se .env existe
print("\n3. Verificando arquivo .env:")
if os.path.exists('.env'):
    print("✅ Arquivo .env encontrado")
    # Ler conteúdo do .env (sem mostrar senhas)
    with open('.env', 'r') as f:
        lines = f.readlines()
        print(f"   Linhas: {len(lines)}")
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0].strip()
                print(f"   - {key}")
else:
    print("❌ Arquivo .env NÃO encontrado")

print("\n" + "=" * 60)
print("✅ Teste concluído")
print("=" * 60)
