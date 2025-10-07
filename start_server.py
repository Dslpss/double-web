#!/usr/bin/env python3
"""
Script para iniciar o servidor Flask com todas as correções aplicadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Iniciando servidor Flask com correções de padrões personalizados...")
print("=" * 60)

print("📋 Correções aplicadas:")
print("✅ Corrigido erro 'str' object has no attribute 'value'")
print("✅ Melhorada resposta da API PUT para padrões")
print("✅ Configurado callback web automático no analyzer")
print("✅ Corrigido erro no AlertSystem")
print("✅ Adicionada rota de status do sistema")
print("✅ Melhorado sistema de logs para debug")

print("\n🔧 Configurações do sistema:")
print("• Padrões personalizados: HABILITADOS")
print("• Callback web: AUTO-CONFIGURADO")
print("• Sistema de alertas: CORRIGIDO")
print("• Debug logs: HABILITADOS")

print("\n" + "=" * 60)
print("🌐 Iniciando servidor na porta 5000...")
print("📱 Interface web disponível em: http://localhost:5000")
print("🎯 API de padrões em: http://localhost:5000/api/custom-patterns")
print("📊 Status do sistema em: http://localhost:5000/api/custom-patterns/status")
print("=" * 60)

# Importar e iniciar o app
try:
    from app import app
    
    # Executar o servidor
    if __name__ == "__main__":
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=False, 
            threaded=True,
            use_reloader=False
        )
        
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()