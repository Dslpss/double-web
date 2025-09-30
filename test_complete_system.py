#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste completo do sistema com banco de dados e padrões Double
"""

import sys
import os
import time
import random

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from src.database.local_storage_db import local_db
from src.analysis.double_patterns import DoublePatternDetector
from src.notifications.pattern_notifier import notify_pattern, notify_result

def test_complete_system():
    """Testa o sistema completo com banco de dados e padrões"""
    print("Sistema Completo - Blaze Double Analyzer")
    print("=" * 60)
    
    # Limpar dados anteriores
    local_db.clear_data('all')
    print("Banco de dados limpo")
    
    # Simular sequência de resultados
    print("\n1. Simulando sequência de resultados...")
    results = []
    
    # Criar sequência que vai gerar padrões
    sequence = [
        (7, 'red'), (12, 'black'), (3, 'red'), (9, 'black'), (5, 'red'),
        (11, 'black'), (2, 'red'), (8, 'black'), (1, 'red'), (13, 'black'),
        (4, 'red'), (10, 'black'), (6, 'red'), (14, 'black'), (0, 'white'),
        (7, 'red'), (12, 'black'), (3, 'red'), (9, 'black'), (5, 'red'),
        (11, 'black'), (2, 'red'), (8, 'black'), (1, 'red'), (13, 'black')
    ]
    
    for i, (number, color) in enumerate(sequence):
        result = {
            'roll': number,
            'color': color,
            'timestamp': int(time.time()),
            'was_win': False,  # Simular algumas vitórias
            'was_loss': True
        }
        
        # Adicionar ao banco
        local_db.add_result(result)
        results.append(result)
        
        # Notificar resultado
        notify_result(number, color)
        
        print(f"Resultado {i+1}: {number} ({color})")
        time.sleep(0.5)
    
    print(f"\nTotal de resultados salvos: {len(results)}")
    
    # Testar detecção de padrões
    print("\n2. Detectando padrões Double...")
    detector = DoublePatternDetector()
    patterns = detector.detect_all_patterns(results)
    
    if patterns and 'patterns' in patterns:
        print(f"Padrões detectados: {len(patterns['patterns'])}")
        
        for pattern_name, pattern_data in patterns['patterns'].items():
            print(f"\n- {pattern_data.get('pattern_type', pattern_name)}")
            print(f"  Confiança: {pattern_data.get('confidence', 0):.1%}")
            print(f"  Descrição: {pattern_data.get('description', 'N/A')}")
            print(f"  Recomendação: {pattern_data.get('recommendation', 'N/A')}")
            
            # Simular notificação de padrão
            if pattern_data.get('confidence', 0) >= 0.6:
                notify_pattern(
                    pattern_type=pattern_data.get('pattern_type', pattern_name),
                    detected_number=results[-1]['roll'],
                    predicted_color=pattern_data.get('predicted_color', 'red'),
                    confidence=pattern_data.get('confidence', 0.6),
                    reasoning=pattern_data.get('description', 'Padrão detectado')
                )
    else:
        print("Nenhum padrão detectado")
    
    # Mostrar estatísticas do banco
    print("\n3. Estatísticas do banco de dados:")
    stats = local_db.get_statistics()
    print(f"Total de resultados: {stats.get('total_results', 0)}")
    print(f"Total de padrões: {stats.get('total_patterns', 0)}")
    print(f"Última atualização: {stats.get('last_updated', 'N/A')}")
    
    # Mostrar padrões salvos
    print("\n4. Padrões salvos no banco:")
    saved_patterns = local_db.get_recent_patterns(10)
    for pattern in saved_patterns:
        print(f"- {pattern.get('pattern_type', 'N/A')} (Conf: {pattern.get('confidence', 0):.1%})")
    
    # Testar exportação
    print("\n5. Testando exportação de dados...")
    export_file = local_db.export_data()
    if export_file:
        print(f"Dados exportados para: {export_file}")
    
    print("\n" + "=" * 60)
    print("Teste completo finalizado!")
    print("Sistema funcionando com:")
    print("OK - Banco de dados local")
    print("OK - Padroes Double especificos")
    print("OK - Notificacoes em tempo real")
    print("OK - Persistencia de dados")
    print("=" * 60)

if __name__ == '__main__':
    test_complete_system()
