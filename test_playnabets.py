#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste para verificar se o playnabets_integrator está funcionando
"""

print("🔍 Testando playnabets_integrator...")

try:
    import playnabets_integrator
    print("✅ playnabets_integrator importado com sucesso!")
    print(f"Config disponível: {hasattr(playnabets_integrator, 'CONFIG_AVAILABLE')}")
    print(f"CONFIG_AVAILABLE: {playnabets_integrator.CONFIG_AVAILABLE}")
except ImportError as e:
    print(f"❌ Erro ao importar playnabets_integrator: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

print("🔍 Testando config diretamente...")
try:
    import config
    print("✅ config importado com sucesso!")
    print(f"PLAYNABETS_WS_URL disponível: {hasattr(config, 'PLAYNABETS_WS_URL')}")
except ImportError as e:
    print(f"❌ Erro ao importar config: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
