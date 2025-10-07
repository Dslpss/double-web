#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar padrões personalizados de exemplo
Demonstra como usar o sistema de padrões personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.src.analysis.custom_patterns import CustomPatternManager, CustomPattern, PatternTrigger, PatternAction

def create_example_patterns():
    """Cria padrões personalizados de exemplo."""
    
    manager = CustomPatternManager()
    
    # Padrão 1: Número 1 seguido por Red
    pattern1 = CustomPattern(
        pattern_id="example_1_red",
        name="Número 1 Seguido por Red",
        description="Detecta quando após o número 1 vem red",
        trigger_type=PatternTrigger.NUMBER_FOLLOWED_BY_COLOR,
        trigger_config={
            'number': 1,
            'color': 'red',
            'min_occurrences': 2
        },
        action=PatternAction.BET_COLOR,
        action_config={'color': 'red'},
        confidence_threshold=0.8,
        cooldown_minutes=3
    )
    
    # Padrão 2: Sequência Red-Red
    pattern2 = CustomPattern(
        pattern_id="example_red_sequence",
        name="Sequência Red-Red",
        description="Detecta sequência de dois reds consecutivos",
        trigger_type=PatternTrigger.COLOR_SEQUENCE,
        trigger_config={
            'sequence': ['red', 'red'],
            'min_length': 2
        },
        action=PatternAction.BET_COLOR,
        action_config={'color': 'black'},
        confidence_threshold=0.7,
        cooldown_minutes=5
    )
    
    # Padrão 3: Black Após Red
    pattern3 = CustomPattern(
        pattern_id="example_black_after_red",
        name="Black Após Red",
        description="Detecta quando após red vem black",
        trigger_type=PatternTrigger.COLOR_AFTER_COLOR,
        trigger_config={
            'first_color': 'red',
            'second_color': 'black',
            'min_occurrences': 1
        },
        action=PatternAction.BET_COLOR,
        action_config={'color': 'black'},
        confidence_threshold=0.75,
        cooldown_minutes=4
    )
    
    # Padrão 4: Número 0 (Branco) seguido por Red
    pattern4 = CustomPattern(
        pattern_id="example_white_red",
        name="Branco Seguido por Red",
        description="Detecta quando após o número 0 (branco) vem red",
        trigger_type=PatternTrigger.NUMBER_FOLLOWED_BY_COLOR,
        trigger_config={
            'number': 0,
            'color': 'red',
            'min_occurrences': 1
        },
        action=PatternAction.BET_COLOR,
        action_config={'color': 'red'},
        confidence_threshold=0.8,
        cooldown_minutes=2
    )
    
    # Padrão 5: Sequência de números baixos
    pattern5 = CustomPattern(
        pattern_id="example_low_numbers",
        name="Sequência de Números Baixos",
        description="Detecta quando aparecem números baixos (1-3) consecutivos",
        trigger_type=PatternTrigger.NUMBER_SEQUENCE,
        trigger_config={
            'sequence': [1, 2, 3],
            'min_length': 2
        },
        action=PatternAction.BET_COLOR,
        action_config={'color': 'red'},
        confidence_threshold=0.7,
        cooldown_minutes=6
    )
    
    # Adicionar padrões
    patterns = [pattern1, pattern2, pattern3, pattern4, pattern5]
    
    print("🎯 Criando padrões personalizados de exemplo...")
    
    for pattern in patterns:
        if manager.add_pattern(pattern):
            print(f"✅ Padrão criado: {pattern.name}")
        else:
            print(f"❌ Erro ao criar padrão: {pattern.name}")
    
    print(f"\n📊 Total de padrões criados: {len(patterns)}")
    
    # Listar padrões existentes
    all_patterns = manager.get_all_patterns()
    print(f"\n📋 Padrões existentes no sistema: {len(all_patterns)}")
    
    for pattern in all_patterns:
        print(f"  - {pattern.name} ({pattern.trigger_type.value})")
    
    return len(patterns)

def test_patterns():
    """Testa os padrões com dados de exemplo."""
    
    manager = CustomPatternManager()
    
    # Dados de exemplo que ativariam alguns padrões
    test_data = [
        {'number': 1, 'color': 'red', 'timestamp': 1000},
        {'number': 1, 'color': 'red', 'timestamp': 2000},
        {'number': 1, 'color': 'red', 'timestamp': 3000},  # Ativa padrão 1
        {'number': 2, 'color': 'red', 'timestamp': 4000},
        {'number': 3, 'color': 'red', 'timestamp': 5000},  # Ativa padrão 2
        {'number': 4, 'color': 'black', 'timestamp': 6000},  # Ativa padrão 3
        {'number': 0, 'color': 'white', 'timestamp': 7000},
        {'number': 1, 'color': 'red', 'timestamp': 8000},  # Ativa padrão 4
    ]
    
    print("\n🧪 Testando padrões com dados de exemplo...")
    
    triggered_patterns = manager.check_patterns(test_data)
    
    if triggered_patterns:
        print(f"🎯 {len(triggered_patterns)} padrão(ões) ativado(s):")
        
        for trigger in triggered_patterns:
            pattern = trigger['pattern']
            print(f"  ✅ {pattern.name}")
            print(f"     Confiança: {trigger['confidence']:.1%}")
            print(f"     Razão: {trigger['reasoning']}")
            print(f"     Sugestão: {trigger['suggestion']}")
            print()
    else:
        print("❌ Nenhum padrão foi ativado com os dados de teste")

def main():
    """Função principal."""
    print("🚀 Sistema de Padrões Personalizados - Exemplo")
    print("=" * 50)
    
    try:
        # Criar padrões de exemplo
        count = create_example_patterns()
        
        # Testar padrões
        test_patterns()
        
        print("\n✅ Exemplo concluído com sucesso!")
        print("\n📝 Como usar:")
        print("1. Acesse /custom-patterns para gerenciar padrões")
        print("2. Os padrões são verificados automaticamente durante o monitoramento")
        print("3. Quando um padrão é ativado, você receberá uma notificação")
        print("4. Use a API /api/custom-patterns/check para verificar manualmente")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
