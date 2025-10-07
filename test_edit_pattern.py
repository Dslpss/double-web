#!/usr/bin/env python3
"""
Script para testar a edição de padrões personalizados
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_edit_pattern():
    """Testa a edição de um padrão personalizado"""
    print("🔧 Testando edição de padrão personalizado...")
    
    # Pegar o primeiro padrão
    try:
        response = requests.get(f"{BASE_URL}/api/custom-patterns")
        if response.status_code == 200:
            patterns = response.json().get('patterns', [])
            if patterns:
                pattern = patterns[0]
                pattern_id = pattern['pattern_id']
                print(f"📝 Editando padrão: {pattern['name']} (ID: {pattern_id})")
                
                # Dados de edição
                updated_data = {
                    "name": f"{pattern['name']} - EDITADO",
                    "description": f"{pattern['description']} - Modificado em {time.strftime('%H:%M:%S')}",
                    "confidence_threshold": 0.8,
                    "cooldown_minutes": 5,
                    "enabled": True
                }
                
                # Fazer a requisição de edição
                edit_response = requests.put(
                    f"{BASE_URL}/api/custom-patterns/{pattern_id}",
                    json=updated_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if edit_response.status_code == 200:
                    result = edit_response.json()
                    if result.get('success'):
                        print("✅ Padrão editado com sucesso!")
                        print(f"   Nome: {result.get('pattern', {}).get('name', 'N/A')}")
                        print(f"   Descrição: {result.get('pattern', {}).get('description', 'N/A')}")
                        print(f"   Confiança: {result.get('pattern', {}).get('confidence_threshold', 'N/A')}")
                        print(f"   Cooldown: {result.get('pattern', {}).get('cooldown_minutes', 'N/A')} min")
                    else:
                        print(f"❌ Erro na edição: {result.get('error')}")
                else:
                    print(f"❌ Erro HTTP {edit_response.status_code}: {edit_response.text}")
            else:
                print("❌ Nenhum padrão encontrado para editar")
        else:
            print(f"❌ Erro ao buscar padrões: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_list_patterns():
    """Lista os padrões após edição"""
    print("\n📋 Listando padrões após edição...")
    try:
        response = requests.get(f"{BASE_URL}/api/custom-patterns")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                patterns = result.get('patterns', [])
                print(f"✅ {len(patterns)} padrões encontrados:")
                for i, pattern in enumerate(patterns, 1):
                    print(f"  {i}. {pattern['name']}")
                    print(f"     ID: {pattern['pattern_id']}")
                    print(f"     Confiança: {pattern['confidence_threshold']}")
                    print(f"     Cooldown: {pattern['cooldown_minutes']} min")
                    print(f"     Ativo: {pattern['enabled']}")
                    print()
            else:
                print(f"❌ Erro: {result.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🔧 Teste de Edição de Padrões Personalizados")
    print("=" * 50)
    
    # Testar edição
    test_edit_pattern()
    
    # Listar padrões após edição
    test_list_patterns()
    
    print("=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main()
