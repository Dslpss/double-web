#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de todas as importações para identificar problemas
"""

import sys
import os

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

def test_imports():
    """Testa todas as importações críticas"""
    print("🔍 Testando importações...")
    
    # Teste 1: Módulos básicos
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
    
    try:
        import pandas as pd
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib")
    except ImportError as e:
        print(f"❌ matplotlib: {e}")
    
    try:
        import numpy as np
        print("✅ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
    
    # Teste 2: Módulos locais
    try:
        from config import PLAYNABETS_WS_URL
        print("✅ config")
    except ImportError as e:
        print(f"❌ config: {e}")
    
    try:
        from auth import require_auth
        print("✅ auth")
    except ImportError as e:
        print(f"❌ auth: {e}")
    
    try:
        from playnabets_integrator import PlayNabetsIntegrator
        print("✅ playnabets_integrator")
    except ImportError as e:
        print(f"❌ playnabets_integrator: {e}")
    
    # Teste 3: Módulos do shared
    try:
        from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
        print("✅ blaze_analyzer_enhanced")
    except ImportError as e:
        print(f"❌ blaze_analyzer_enhanced: {e}")
    
    try:
        from src.notifications.pattern_notifier import get_notifier
        print("✅ pattern_notifier")
    except ImportError as e:
        print(f"❌ pattern_notifier: {e}")
    
    try:
        from src.database.local_storage_db import local_db
        print("✅ local_storage_db")
    except ImportError as e:
        print(f"❌ local_storage_db: {e}")

if __name__ == "__main__":
    test_imports()
