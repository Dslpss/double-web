#!/usr/bin/env python3
"""
Script para debugar padrões personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.src.analysis.custom_patterns import CustomPatternManager
import json

def debug_custom_patterns():
    """Debug dos padrões personalizados"""
    print("🔍 Debug dos Padrões Personalizados")
    print("=" * 50)
    
    try:
        # Inicializar manager
        manager = CustomPatternManager()
        print("✅ Manager inicializado com sucesso")
        
        # Listar todos os padrões
        patterns = manager.get_all_patterns()
        print(f"📋 Total de padrões encontrados: {len(patterns)}")
        
        if patterns:
            for i, pattern in enumerate(patterns, 1):
                print(f"\n{i}. {pattern.name}")
                print(f"   ID: {pattern.pattern_id}")
                print(f"   Tipo: {pattern.trigger_type}")
                print(f"   Ação: {pattern.action}")
                print(f"   Habilitado: {pattern.enabled}")
                print(f"   Confiança: {pattern.confidence_threshold}")
                print(f"   Cooldown: {pattern.cooldown_minutes} min")
                print(f"   Config Gatilho: {pattern.trigger_config}")
                print(f"   Config Ação: {pattern.action_config}")
        else:
            print("❌ Nenhum padrão encontrado!")
            
        # Testar com dados simulados
        print("\n🧪 Testando com dados simulados...")
        test_data = [
            {'number': 1, 'color': 'red', 'timestamp': 1633024800},
            {'number': 2, 'color': 'black', 'timestamp': 1633024860},
            {'number': 3, 'color': 'red', 'timestamp': 1633024920},
            {'number': 4, 'color': 'black', 'timestamp': 1633024980},
            {'number': 5, 'color': 'red', 'timestamp': 1633025040},
        ]
        
        triggered = manager.check_patterns(test_data)
        print(f"🎯 Padrões ativados com dados de teste: {len(triggered)}")
        
        for pattern in triggered:
            print(f"   ✅ {pattern.get('name', 'Padrão')}: {pattern.get('suggestion', 'Alerta')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_custom_patterns()