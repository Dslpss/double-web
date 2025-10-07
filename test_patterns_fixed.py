#!/usr/bin/env python3
"""
Script para testar se os padrões personalizados estão funcionando
"""

import requests
import json

def test_patterns():
    """Testa se os padrões personalizados estão funcionando"""
    print("🎯 Testando Padrões Personalizados Corrigidos")
    print("=" * 50)
    
    try:
        # Verificar padrões
        print("📋 Listando padrões personalizados...")
        response = requests.get("http://localhost:5000/api/custom-patterns")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                patterns = data.get('patterns', [])
                print(f"✅ {len(patterns)} padrões encontrados:")
                
                for pattern in patterns:
                    print(f"  - {pattern['name']} ({pattern['trigger_type']})")
                
                # Testar verificação de padrões
                print("\n🔍 Testando verificação de padrões...")
                check_response = requests.post("http://localhost:5000/api/custom-patterns/check")
                
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    if check_data.get('success'):
                        triggered = check_data.get('triggered_patterns', [])
                        print(f"✅ Verificação funcionando - {len(triggered)} padrão(ões) ativado(s)")
                        
                        for pattern in triggered:
                            print(f"  🎯 {pattern['name']}: {pattern['suggestion']}")
                    else:
                        print(f"❌ Erro na verificação: {check_data.get('error')}")
                else:
                    print(f"❌ Erro HTTP na verificação: {check_response.status_code}")
            else:
                print(f"❌ Erro ao buscar padrões: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_patterns()
