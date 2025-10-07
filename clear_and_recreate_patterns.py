#!/usr/bin/env python3
"""
Script para limpar e recriar padrões personalizados corretos
"""

import requests
import json
import time

# URL base da API
BASE_URL = "http://localhost:5000"

def clear_all_patterns():
    """Remove todos os padrões personalizados"""
    print("🗑️ Removendo todos os padrões personalizados...")
    
    try:
        # Buscar todos os padrões
        response = requests.get(f"{BASE_URL}/api/custom-patterns")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                patterns = data.get('patterns', [])
                print(f"📊 Encontrados {len(patterns)} padrões para remover")
                
                for pattern in patterns:
                    pattern_id = pattern['pattern_id']
                    name = pattern['name']
                    
                    # Remover padrão
                    delete_response = requests.delete(f"{BASE_URL}/api/custom-patterns/{pattern_id}")
                    if delete_response.status_code == 200:
                        print(f"  ✅ Removido: {name}")
                    else:
                        print(f"  ❌ Erro ao remover: {name}")
                
                print("✅ Limpeza concluída!")
                return True
            else:
                print(f"❌ Erro ao buscar padrões: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False

def add_correct_patterns():
    """Adiciona padrões personalizados corretos"""
    print("\n🎯 Adicionando padrões personalizados corretos...")
    
    patterns = [
        {
            "name": "1 Red → Jogar Red",
            "description": "Quando o número 1 (red) aparece, apostar na cor red na próxima rodada",
            "trigger_type": "number_followed_by_color",
            "trigger_config": {
                "number": 1,
                "color": "red",
                "min_occurrences": 1
            },
            "action": "bet_color",
            "action_config": {
                "color": "red"
            },
            "confidence_threshold": 0.6,
            "cooldown_minutes": 3,
            "enabled": True
        },
        {
            "name": "5 → Delay 5 → Red",
            "description": "Quando sair o número 5, aguardar 5 resultados e então alertar para jogar red",
            "trigger_type": "number_delay_alert",
            "trigger_config": {
                "trigger_number": 5,
                "delay_results": 5,
                "min_occurrences": 1
            },
            "action": "bet_color",
            "action_config": {
                "color": "red"
            },
            "confidence_threshold": 0.7,
            "cooldown_minutes": 3,
            "enabled": True
        },
        {
            "name": "Red Após Black",
            "description": "Quando black aparece, apostar em red na próxima rodada",
            "trigger_type": "color_after_color",
            "trigger_config": {
                "first_color": "black",
                "second_color": "red",
                "min_occurrences": 1
            },
            "action": "bet_color",
            "action_config": {
                "color": "red"
            },
            "confidence_threshold": 0.7,
            "cooldown_minutes": 5,
            "enabled": True
        }
    ]
    
    success_count = 0
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['name']}")
        print(f"   {pattern['description']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/custom-patterns",
                json=pattern,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"  ✅ Adicionado com sucesso!")
                    success_count += 1
                else:
                    print(f"  ❌ Erro: {result.get('error')}")
            else:
                print(f"  ❌ Erro HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(1)
    
    print(f"\n✅ {success_count}/{len(patterns)} padrões adicionados com sucesso!")
    return success_count > 0

def main():
    print("🔧 Limpando e Recriando Padrões Personalizados")
    print("=" * 60)
    
    # Limpar padrões existentes
    if clear_all_patterns():
        # Adicionar padrões corretos
        if add_correct_patterns():
            print("\n🎉 Processo concluído com sucesso!")
            print(f"🌐 Acesse: {BASE_URL}/custom-patterns")
        else:
            print("\n❌ Erro ao adicionar padrões corretos")
    else:
        print("\n❌ Erro ao limpar padrões existentes")

if __name__ == "__main__":
    main()
