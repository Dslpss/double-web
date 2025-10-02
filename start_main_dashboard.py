#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inicializador do Dashboard Principal
Sistema integrado Double + Roleta Brasileira
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Inicia o dashboard principal."""
    
    print("🚀 Iniciando Dashboard Principal...")
    print("=" * 60)
    print("🎲 Sistema Integrado: Double (Blaze) + Roleta Brasileira")
    print("📊 Acesse: http://localhost:5000")
    print("=" * 60)
    
    try:
        # Verificar se os arquivos existem
        if not Path("main_dashboard.py").exists():
            print("❌ Erro: main_dashboard.py não encontrado!")
            return
        
        if not Path("templates/main_dashboard.html").exists():
            print("❌ Erro: templates/main_dashboard.html não encontrado!")
            return
        
        print("✅ Arquivos verificados")
        print("🔌 Iniciando servidor Flask...")
        
        # Executar o dashboard principal
        subprocess.run([sys.executable, "main_dashboard.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard interrompido pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        print("✅ Dashboard finalizado")

if __name__ == "__main__":
    main()
