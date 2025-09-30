#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialização para o Blaze Web
"""

import os
import sys
import subprocess

def main():
    print("Iniciando Blaze Web...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('backend/app.py'):
        print("ERRO: Execute este script do diretorio blaze-web/")
        return
    
    # Verificar se as dependências estão instaladas
    try:
        import flask
        import flask_socketio
        print("OK: Dependencias encontradas")
    except ImportError:
        print("Instalando dependencias...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
            print("OK: Dependencias instaladas")
        except subprocess.CalledProcessError:
            print("ERRO: Erro ao instalar dependencias")
            return
    
    # Iniciar servidor
    print("Iniciando servidor...")
    print("Acesse: http://localhost:5000")
    print("Para parar: Ctrl+C")
    print("-" * 50)
    
    os.chdir('backend')
    subprocess.run([sys.executable, 'polling_app.py'])

if __name__ == '__main__':
    main()
