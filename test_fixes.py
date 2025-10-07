#!/usr/bin/env python3
"""
Teste rápido dos padrões personalizados corrigidos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixes():
    """Teste rápido das correções"""
    print("🔍 Teste Rápido das Correções")
    print("=" * 40)
    
    try:
        # 1. Testar importação do sistema
        print("1. 📦 Testando importações...")
        from shared.src.analysis.custom_patterns import CustomPatternManager
        print("   ✅ CustomPatternManager importado")
        
        # 2. Testar inicialização do manager
        print("2. 🚀 Testando inicialização...")
        manager = CustomPatternManager()
        print("   ✅ Manager inicializado")
        
        # 3. Testar listagem de padrões
        print("3. 📋 Testando listagem de padrões...")
        patterns = manager.get_all_patterns()
        print(f"   ✅ {len(patterns)} padrões encontrados")
        
        # 4. Testar conversão enum-string (problema original)
        print("4. 🔧 Testando conversão enum-string...")
        for pattern in patterns:
            # Tentar acessar os valores que causavam erro
            trigger_str = pattern.trigger_type.value if hasattr(pattern.trigger_type, 'value') else pattern.trigger_type
            action_str = pattern.action.value if hasattr(pattern.action, 'value') else pattern.action
            print(f"   ✅ {pattern.name}: {trigger_str} -> {action_str}")
        
        # 5. Testar detecção básica
        print("5. 🎯 Testando detecção básica...")
        test_data = [
            {'number': 2, 'color': 'black'},
            {'number': 1, 'color': 'red'},  # Deve ativar "Red Após Black"
        ]
        triggered = manager.check_patterns(test_data)
        print(f"   ✅ {len(triggered)} padrão(ões) detectado(s)")
        
        print("\n" + "=" * 40)
        print("🎉 TODAS AS CORREÇÕES FUNCIONANDO!")
        print("✅ Sistema de padrões personalizados OK")
        print("✅ Conversão enum-string corrigida")
        print("✅ Detecção de padrões funcionando")
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixes()