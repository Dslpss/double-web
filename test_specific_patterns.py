#!/usr/bin/env python3
"""
Script para testar especificamente os padrões personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.src.analysis.custom_patterns import CustomPatternManager
import json

def test_specific_patterns():
    """Teste específico dos padrões"""
    print("🔍 Teste Específico dos Padrões Personalizados")
    print("=" * 50)
    
    try:
        # Inicializar manager
        manager = CustomPatternManager()
        print("✅ Manager inicializado com sucesso")
        
        # Testar padrão "Red Após Black"
        print("\n🧪 Testando padrão 'Red Após Black'...")
        test_data_black_red = [
            {'number': 2, 'color': 'black', 'timestamp': 1633024800},
            {'number': 1, 'color': 'red', 'timestamp': 1633024860},  # Black → Red (deve ativar)
            {'number': 4, 'color': 'black', 'timestamp': 1633024920},
            {'number': 3, 'color': 'red', 'timestamp': 1633024980},  # Black → Red (deve ativar)
        ]
        
        print("Dados de teste:")
        for i, item in enumerate(test_data_black_red):
            print(f"  {i+1}. Número: {item['number']}, Cor: {item['color']}")
        
        triggered = manager.check_patterns(test_data_black_red)
        print(f"🎯 Padrões ativados: {len(triggered)}")
        
        for pattern_info in triggered:
            pattern = pattern_info.get('pattern')
            print(f"   ✅ {pattern.name if pattern else 'Padrão desconhecido'}")
            print(f"      Confiança: {pattern_info.get('confidence', 'N/A')}")
            print(f"      Razão: {pattern_info.get('reasoning', 'N/A')}")
            print(f"      Sugestão: {pattern_info.get('suggestion', 'N/A')}")
        
        # Testar padrão "1 Red → Jogar Red"
        print("\n🧪 Testando padrão '1 Red → Jogar Red'...")
        test_data_1_red = [
            {'number': 1, 'color': 'red', 'timestamp': 1633024800},
            {'number': 3, 'color': 'red', 'timestamp': 1633024860},  # 1 → Red (deve ativar)
            {'number': 1, 'color': 'red', 'timestamp': 1633024920},
            {'number': 5, 'color': 'red', 'timestamp': 1633024980},  # 1 → Red (deve ativar)
            {'number': 1, 'color': 'red', 'timestamp': 1633025040},
            {'number': 7, 'color': 'red', 'timestamp': 1633025100},  # 1 → Red (deve ativar)
            {'number': 1, 'color': 'red', 'timestamp': 1633025160},
            {'number': 9, 'color': 'red', 'timestamp': 1633025220},  # 1 → Red (deve ativar)
            {'number': 1, 'color': 'red', 'timestamp': 1633025280},
            {'number': 12, 'color': 'red', 'timestamp': 1633025340}, # 1 → Red (deve ativar)
        ]
        
        print("Dados de teste:")
        for i, item in enumerate(test_data_1_red):
            print(f"  {i+1}. Número: {item['number']}, Cor: {item['color']}")
        
        triggered = manager.check_patterns(test_data_1_red)
        print(f"🎯 Padrões ativados: {len(triggered)}")
        
        for pattern_info in triggered:
            pattern = pattern_info.get('pattern')
            print(f"   ✅ {pattern.name if pattern else 'Padrão desconhecido'}")
            print(f"      Confiança: {pattern_info.get('confidence', 'N/A')}")
            print(f"      Razão: {pattern_info.get('reasoning', 'N/A')}")
            print(f"      Sugestão: {pattern_info.get('suggestion', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_patterns()