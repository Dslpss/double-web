#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste para verificar se o blaze_analyzer_enhanced está funcionando
"""

print("🔍 Testando blaze_analyzer_enhanced...")

try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
    
    from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
    print("✅ BlazeAnalyzerEnhanced importado com sucesso!")
    
    # Tentar criar uma instância
    analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
    print("✅ BlazeAnalyzerEnhanced instanciado com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar BlazeAnalyzerEnhanced: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
