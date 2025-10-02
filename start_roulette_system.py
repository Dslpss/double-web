#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialização do Sistema Completo de Roleta
"""

import time
import subprocess
import sys
import os

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    try:
        import flask
        import flask_socketio
        import aiohttp
        import sqlite3
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def start_system():
    """Inicia o sistema completo."""
    print("🚀 SISTEMA COMPLETO DE ROLETA BRASILEIRA")
    print("=" * 60)
    
    if not check_dependencies():
        print("Por favor, instale as dependências:")
        print("pip install flask flask-socketio aiohttp")
        return
    
    print("🔧 Iniciando componentes do sistema...")
    
    try:
        # Importar e iniciar o sistema
        from roulette_system_complete import PragmaticAPIMonitor
        
        print("📊 Iniciando monitor da API...")
        monitor = PragmaticAPIMonitor()
        monitor.start()
        
        print("✅ Sistema iniciado com sucesso!")
        print()
        print("📈 FUNCIONALIDADES ATIVAS:")
        print("✅ Monitor em tempo real da API Pragmatic Play")
        print("✅ Banco de dados SQLite para armazenamento")
        print("✅ Análise estatística avançada")
        print("✅ Sistema de notificações inteligentes")
        print("✅ Cache de resultados em memória")
        print()
        print("🎯 DADOS CAPTURADOS:")
        print("• Números da roleta (0-36)")
        print("• Cores (Vermelho, Preto, Verde)")
        print("• IDs únicos dos jogos")
        print("• Timestamps precisos")
        print("• Análise de padrões")
        print()
        print("🔔 NOTIFICAÇÕES ATIVAS:")
        print("• Número 0 (Verde)")
        print("• Sequências de mesma cor (5+)")
        print("• Números repetidos")
        print("• Sequências de números altos")
        print()
        print("Pressione Ctrl+C para parar o sistema")
        
        # Manter o sistema rodando
        while True:
            time.sleep(1)
            
            # Mostrar estatísticas a cada 60 segundos
            if hasattr(monitor, 'results_cache') and len(monitor.results_cache) > 0:
                if int(time.time()) % 60 == 0:
                    print(f"\n📊 Status: {len(monitor.results_cache)} resultados em cache")
    
    except KeyboardInterrupt:
        print("\n🛑 Parando sistema...")
        if 'monitor' in locals():
            monitor.stop()
        print("✅ Sistema parado com sucesso!")
    
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_system()
