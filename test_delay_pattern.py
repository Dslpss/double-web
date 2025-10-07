#!/usr/bin/env python3
"""
Script para testar o novo padrão de delay
"""

import requests
import json
import time

# URL base da API
BASE_URL = "http://localhost:5000"

def test_delay_pattern():
    """Testa o novo padrão de delay"""
    print("🎯 Testando Padrão de Delay")
    print("=" * 50)
    
    # Dados do padrão: "Saiu 5, 5 resultados depois alertar pra jogar red"
    pattern_data = {
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
    }
    
    try:
        # Adicionar padrão
        print("📝 Adicionando padrão de delay...")
        response = requests.post(
            f"{BASE_URL}/api/custom-patterns",
            json=pattern_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Padrão de delay adicionado com sucesso!")
                print(f"   ID: {result.get('pattern_id')}")
            else:
                print(f"❌ Erro ao adicionar padrão: {result.get('error')}")
                return
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return
        
        # Verificar padrões
        print("\n🔍 Verificando padrões ativados...")
        response = requests.post(f"{BASE_URL}/api/custom-patterns/check")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                triggered = result.get('triggered_patterns', [])
                print(f"📊 {len(triggered)} padrão(ões) ativado(s)")
                
                for pattern in triggered:
                    print(f"\n🎯 Padrão Ativado: {pattern['name']}")
                    print(f"   Sugestão: {pattern['suggestion']}")
                    print(f"   Confiança: {pattern['confidence']:.1%}")
                    print(f"   Razão: {pattern['reasoning']}")
            else:
                print(f"❌ Erro ao verificar padrões: {result.get('error')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_delay_pattern()
