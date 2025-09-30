#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar se o PlayNabets Integrator está funcionando
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Testa se todos os imports estão funcionando."""
    print("Testando imports...")
    
    try:
        from playnabets_integrator import PlayNabetsIntegrator
        print("OK - PlayNabetsIntegrator importado com sucesso")
    except ImportError as e:
        print(f"ERRO - Erro ao importar PlayNabetsIntegrator: {e}")
        return False
    
    try:
        from config import PLAYNABETS_WS_URL, get_playnabets_headers
        print("OK - Config importado com sucesso")
        print(f"   URL: {PLAYNABETS_WS_URL}")
    except ImportError as e:
        print(f"ERRO - Erro ao importar config: {e}")
        return False
    
    try:
        import aiohttp
        print("OK - aiohttp disponivel")
    except ImportError as e:
        print(f"ERRO - aiohttp nao disponivel: {e}")
        return False
    
    return True

def test_integrator_creation():
    """Testa criação do integrador."""
    print("\nTestando criacao do integrador...")
    
    try:
        from playnabets_integrator import PlayNabetsIntegrator
        
        # Criar integrador sem analyzer
        integrator = PlayNabetsIntegrator()
        print("OK - Integrador criado sem analyzer")
        
        # Verificar propriedades
        print(f"   URL: {integrator.ws_url}")
        print(f"   Conectado: {integrator.connected}")
        print(f"   Rodando: {integrator.running}")
        
        # Testar status
        status = integrator.get_status()
        print(f"   Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"ERRO - Erro ao criar integrador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrator_with_analyzer():
    """Testa integrador com analyzer."""
    print("\nTestando integrador com analyzer...")
    
    try:
        from playnabets_integrator import PlayNabetsIntegrator
        
        # Simular analyzer
        class MockAnalyzer:
            def __init__(self):
                self.manual_data = []
            
            def add_manual_result(self, number, color):
                self.manual_data.append({
                    'number': number,
                    'color': color,
                    'timestamp': 1234567890
                })
                print(f"   Mock analyzer: adicionado {number} ({color})")
        
        analyzer = MockAnalyzer()
        integrator = PlayNabetsIntegrator(analyzer)
        
        print("OK - Integrador criado com analyzer")
        
        # Testar processamento de resultado
        test_data = {
            'value': 7,
            'round_id': 'test_round'
        }
        
        result = integrator.process_result(test_data)
        if result:
            print(f"OK - Resultado processado: {result}")
        else:
            print("ERRO - Falha ao processar resultado")
        
        return True
        
    except Exception as e:
        print(f"ERRO - Erro ao testar integrador com analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_functions():
    """Testa funções de configuração."""
    print("\nTestando funcoes de configuracao...")
    
    try:
        from config import get_playnabets_headers, get_playnabets_url, extract_result_from_payload
        
        # Testar headers
        headers = get_playnabets_headers()
        print(f"OK - Headers: {headers}")
        
        # Testar URL
        url = get_playnabets_url()
        print(f"OK - URL: {url}")
        
        # Testar extração de resultado
        test_data = {'value': 5, 'round_id': 'test'}
        result = extract_result_from_payload(test_data)
        if result:
            print(f"OK - Extracao de resultado: {result}")
        else:
            print("ERRO - Falha na extracao de resultado")
        
        return True
        
    except Exception as e:
        print(f"ERRO - Erro ao testar configuracao: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testando PlayNabets Integrator...")
    print("=" * 50)
    
    success = True
    
    # Executar testes
    success &= test_imports()
    success &= test_config_functions()
    success &= test_integrator_creation()
    success &= test_integrator_with_analyzer()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCESSO - Todos os testes passaram! PlayNabets Integrator esta funcionando.")
    else:
        print("ERRO - Alguns testes falharam. Verifique os erros acima.")
    
    print("\nSe ainda houver problemas:")
    print("   1. Verifique se todas as dependencias estao instaladas")
    print("   2. Execute: pip install -r backend/requirements.txt")
    print("   3. Verifique se o arquivo config.py existe no diretorio backend")
