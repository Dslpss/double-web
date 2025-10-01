#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste para verificar se o config.py está sendo encontrado
"""

import os
import sys

print("🔍 Testando config.py...")
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivos no diretório: {os.listdir('.')}")

try:
    import config
    print("✅ config.py importado com sucesso!")
    print(f"Config disponível: {hasattr(config, 'PLAYNABETS_WS_URL')}")
except ImportError as e:
    print(f"❌ Erro ao importar config: {e}")
    print(f"Python path: {sys.path}")
