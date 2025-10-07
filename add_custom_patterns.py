#!/usr/bin/env python3
"""
Script para adicionar padrões personalizados ao sistema
"""

import requests
import json
import time

# URL base da API
BASE_URL = "http://localhost:5000"

def wait_for_server():
    """Aguarda o servidor estar disponível"""
    print("🔄 Aguardando servidor estar disponível...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor disponível!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Tentativa {i+1}/30...")
    
    print("❌ Servidor não está disponível")
    return False

def add_pattern(pattern_data):
    """Adiciona um padrão personalizado"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/custom-patterns",
            json=pattern_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Padrão '{pattern_data['name']}' adicionado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao adicionar padrão: {result.get('error')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
    
    return False

def main():
    print("🎯 Adicionando Padrões Personalizados")
    print("=" * 50)
    
    # Aguardar servidor
    if not wait_for_server():
        return
    
    # Padrão 1: "1 red jogar depois red"
    pattern1 = {
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
    }
    
    # Padrão 2: "Black após Red"
    pattern2 = {
        "name": "Black Após Red",
        "description": "Quando red aparece, apostar em black na próxima rodada",
        "trigger_type": "color_after_color",
        "trigger_config": {
            "first_color": "red",
            "second_color": "black",
            "min_occurrences": 1
        },
        "action": "bet_color",
        "action_config": {
            "color": "black"
        },
        "confidence_threshold": 0.7,
        "cooldown_minutes": 5,
        "enabled": True
    }
    
    # Padrão 3: "Sequência Red-Red"
    pattern3 = {
        "name": "Red-Red → Black",
        "description": "Quando aparecem dois reds consecutivos, apostar em black",
        "trigger_type": "color_sequence",
        "trigger_config": {
            "sequence": ["red", "red"],
            "min_length": 2
        },
        "action": "bet_color",
        "action_config": {
            "color": "black"
        },
        "confidence_threshold": 0.8,
        "cooldown_minutes": 10,
        "enabled": True
    }
    
    # Padrão 4: "Número 0 (Branco) → Red"
    pattern4 = {
        "name": "Branco → Red",
        "description": "Quando o número 0 (branco) aparece, apostar em red",
        "trigger_type": "number_followed_by_color",
        "trigger_config": {
            "number": 0,
            "color": "white",
            "min_occurrences": 1
        },
        "action": "bet_color",
        "action_config": {
            "color": "red"
        },
        "confidence_threshold": 0.65,
        "cooldown_minutes": 5,
        "enabled": True
    }
    
    # Padrão 5: "Números Baixos → Red"
    pattern5 = {
        "name": "Números Baixos → Red",
        "description": "Quando números 1-3 aparecem, apostar em red",
        "trigger_type": "number_sequence",
        "trigger_config": {
            "sequence": [1, 2, 3],
            "min_length": 1
        },
        "action": "bet_color",
        "action_config": {
            "color": "red"
        },
        "confidence_threshold": 0.6,
        "cooldown_minutes": 3,
        "enabled": True
    }
    
    patterns = [pattern1, pattern2, pattern3, pattern4, pattern5]
    
    print(f"\n📝 Adicionando {len(patterns)} padrões personalizados...")
    print("-" * 50)
    
    success_count = 0
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['name']}")
        print(f"   {pattern['description']}")
        if add_pattern(pattern):
            success_count += 1
        time.sleep(1)  # Pequena pausa entre requisições
    
    print("\n" + "=" * 50)
    print(f"✅ {success_count}/{len(patterns)} padrões adicionados com sucesso!")
    
    if success_count > 0:
        print(f"\n🌐 Acesse: {BASE_URL}/custom-patterns")
        print("   para gerenciar seus padrões personalizados!")

if __name__ == "__main__":
    main()
