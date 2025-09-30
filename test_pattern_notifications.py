#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste focado para demonstrar o sistema de notificações de padrões
"""

import sys
import os
import time
import random

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from src.notifications.pattern_notifier import notify_pattern, notify_result

def test_pattern_notifications():
    """Testa o sistema de notificações com foco em padrões práticos"""
    print("Sistema de Notificações de Padrões - Blaze Double")
    print("=" * 60)
    print("Este sistema detecta padrões e te diz qual cor apostar!")
    print("=" * 60)
    print()
    
    # Simular sequência de resultados
    print("Simulando sequência de resultados...")
    results = [
        (7, 'red'),
        (12, 'black'), 
        (3, 'red'),
        (9, 'black'),
        (5, 'red'),
        (11, 'black'),
        (2, 'red'),
        (8, 'black'),
        (1, 'red'),
        (13, 'black'),
        (4, 'red'),
        (10, 'black'),
        (6, 'red'),
        (14, 'black'),
        (0, 'white')
    ]
    
    for i, (number, color) in enumerate(results):
        print(f"\n--- Rodada {i+1} ---")
        notify_result(number, color)
        time.sleep(1)
        
        # Simular detecção de padrão a cada 3-4 rodadas
        if i > 2 and i % 3 == 0:
            # Simular diferentes tipos de padrões
            patterns = [
                {
                    'type': 'Sequencia de Vermelhos',
                    'confidence': 0.85,
                    'reasoning': 'Sequencia de 3 vermelhos consecutivos detectada'
                },
                {
                    'type': 'Padrao Alternado',
                    'confidence': 0.78,
                    'reasoning': 'Padrao alternado vermelho-preto detectado'
                },
                {
                    'type': 'Números Quentes',
                    'confidence': 0.92,
                    'reasoning': 'Número 5 apareceu 6 vezes nas últimas 15 rodadas'
                },
                {
                    'type': 'Branco Isca',
                    'confidence': 0.68,
                    'reasoning': 'Branco seguido de preto em 70% dos casos'
                }
            ]
            
            pattern = random.choice(patterns)
            predicted_color = random.choice(['red', 'black', 'white'])
            
            print(f"\n🔍 Analisando padrões...")
            time.sleep(1)
            
            notify_pattern(
                pattern_type=pattern['type'],
                detected_number=number,
                predicted_color=predicted_color,
                confidence=pattern['confidence'],
                reasoning=pattern['reasoning'],
                pattern_id=f"pattern_{int(time.time())}"
            )
    
    print("\n" + "="*60)
    print("Teste concluído!")
    print("O sistema detecta padrões e te orienta sobre qual cor apostar!")
    print("="*60)

def test_single_pattern():
    """Testa uma notificação individual"""
    print("Teste de notificação individual:")
    print("-" * 40)
    
    notify_pattern(
        pattern_type="Sequencia de Vermelhos",
        detected_number=7,
        predicted_color="red",
        confidence=0.88,
        reasoning="Sequencia de 4 vermelhos consecutivos detectada",
        pattern_id="test_001"
    )

if __name__ == '__main__':
    print("Escolha o tipo de teste:")
    print("1. Teste completo com sequência")
    print("2. Teste de notificação individual")
    
    choice = input("Digite 1 ou 2: ").strip()
    
    if choice == '1':
        test_pattern_notifications()
    elif choice == '2':
        test_single_pattern()
    else:
        print("Opção inválida")
