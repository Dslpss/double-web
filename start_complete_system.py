#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para iniciar o sistema completo:
- Dashboard Principal (porta 5000)
- Sistema Double (porta 5001)
"""

import subprocess
import time
import sys
import os
import threading

def run_script_in_background(script_name, script_args=None):
    """Executa um script Python em segundo plano."""
    cmd = [sys.executable, script_name]
    if script_args:
        cmd.extend(script_args)
    
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_CONSOLE
        process = subprocess.Popen(cmd, creationflags=creation_flags)
    else:
        process = subprocess.Popen(cmd)
    return process

def main():
    print("🚀 Iniciando Sistema Completo (Dashboard Principal + Double + Roleta)...")
    print()
    
    processes = []
    
    try:
        # 1. Iniciar Sistema Double (porta 5001)
        print("1️⃣ Iniciando Sistema Double (porta 5001)...")
        double_process = run_script_in_background("app.py")
        processes.append(("Double", double_process))
        time.sleep(3)  # Aguardar inicialização
        
        # 2. Iniciar Dashboard Principal (porta 5000)
        print("2️⃣ Iniciando Dashboard Principal (porta 5000)...")
        main_process = run_script_in_background("main_dashboard.py")
        processes.append(("Dashboard Principal", main_process))
        time.sleep(2)
        
        print()
        print("✅ Sistema Completo Iniciado!")
        print("📊 Dashboard Principal: http://localhost:5000")
        print("🔥 Sistema Double: http://localhost:5001")
        print("🎲 Sistema Roleta: Integrado no Dashboard Principal")
        print()
        print("💡 COMO USAR:")
        print("   1. Acesse http://localhost:5000")
        print("   2. Clique em 'Double' para ir ao sistema Double")
        print("   3. Clique em 'Roleta' para usar o sistema de Roleta")
        print()
        print("⚠️  Pressione Ctrl+C para parar todos os sistemas")
        
        # Manter o script rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Parando todos os sistemas...")
        
        for name, process in processes:
            try:
                print(f"   Parando {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Forçando parada do {name}...")
                process.kill()
            except Exception as e:
                print(f"   Erro ao parar {name}: {e}")
        
        print("✅ Todos os sistemas foram parados!")

if __name__ == "__main__":
    main()
