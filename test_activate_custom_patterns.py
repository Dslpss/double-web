#!/usr/bin/env python3
"""
Script para ativar especificamente os padrões personalizados
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def add_specific_data():
    """Adiciona dados específicos para ativar padrões personalizados"""
    print("🎯 Adicionando dados para ativar padrões personalizados...")
    
    # Sequência para ativar "1 Red → Jogar Red"
    sequence_1 = [
        {"number": 1, "color": "red", "timestamp": int(time.time())},
    ]
    
    # Sequência para ativar "5 → Delay 5 → Red" 
    sequence_5 = [
        {"number": 5, "color": "black", "timestamp": int(time.time()) + 10},
        {"number": 2, "color": "black", "timestamp": int(time.time()) + 20},
        {"number": 8, "color": "black", "timestamp": int(time.time()) + 30},
        {"number": 11, "color": "black", "timestamp": int(time.time()) + 40},
        {"number": 13, "color": "black", "timestamp": int(time.time()) + 50},
        {"number": 4, "color": "red", "timestamp": int(time.time()) + 60},  # 5 resultados depois do 5
    ]
    
    # Sequência para ativar "Red Após Black"
    sequence_black_red = [
        {"number": 2, "color": "black", "timestamp": int(time.time()) + 70},
        {"number": 6, "color": "red", "timestamp": int(time.time()) + 80},  # Red após black
    ]
    
    all_sequences = sequence_1 + sequence_5 + sequence_black_red
    
    for i, data in enumerate(all_sequences):
        try:
            response = requests.post(
                f"{BASE_URL}/api/add_result",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"  ✅ Dados {i+1}: {data['number']} ({data['color']})")
            else:
                print(f"  ❌ Erro: {response.text}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(2)  # Pausa entre adições

def check_custom_patterns():
    """Verifica padrões personalizados"""
    print("\n🔍 Verificando padrões personalizados...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/custom-patterns/check",
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                triggered = result.get('triggered_patterns', [])
                if triggered:
                    print(f"🎯 {len(triggered)} PADRÃO(ÕES) PERSONALIZADO(S) ATIVADO(S)!")
                    for pattern in triggered:
                        print(f"  🚨 {pattern.get('name', 'Padrão')}")
                        print(f"     Sugestão: {pattern.get('suggestion', 'N/A')}")
                        print(f"     Confiança: {pattern.get('confidence', 0):.1%}")
                        print(f"     Razão: {pattern.get('reasoning', 'N/A')}")
                        print("  " + "="*50)
                else:
                    print("  ℹ️ Nenhum padrão personalizado ativado ainda")
            else:
                print(f"  ❌ Erro: {result.get('error')}")
        else:
            print(f"  ❌ Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

def main():
    print("🎯 Ativando Padrões Personalizados Específicos")
    print("=" * 60)
    
    # Adicionar dados específicos
    add_specific_data()
    
    # Aguardar processamento
    print("\n⏳ Aguardando processamento...")
    time.sleep(5)
    
    # Verificar padrões
    check_custom_patterns()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("🌐 Verifique o navegador para ver os alertas ABSOLUTOS!")

if __name__ == "__main__":
    main()
