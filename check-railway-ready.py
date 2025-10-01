#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de verificação para deploy no Railway
Verifica se todos os arquivos necessários estão presentes e corretos
"""

import os
import sys

def check_file_exists(filepath, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - ARQUIVO NÃO ENCONTRADO")
        return False

def check_file_content(filepath, required_content, description):
    """Verifica se um arquivo contém conteúdo específico"""
    if not os.path.exists(filepath):
        print(f"❌ {description}: {filepath} - ARQUIVO NÃO ENCONTRADO")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {description}: {filepath}")
                return True
            else:
                print(f"❌ {description}: {filepath} - CONTEÚDO INCORRETO")
                return False
    except Exception as e:
        print(f"❌ {description}: {filepath} - ERRO AO LER: {e}")
        return False

def main():
    print("🚀 Verificação de Preparação para Railway Deploy")
    print("=" * 50)
    
    checks = []
    
    # Verificar arquivos essenciais
    checks.append(check_file_exists("Procfile", "Procfile"))
    checks.append(check_file_exists("railway.json", "Configuração Railway"))
    checks.append(check_file_exists("backend/requirements.txt", "Requirements Python"))
    checks.append(check_file_exists("backend/polling_app.py", "App Principal"))
    
    # Verificar conteúdo do Procfile
    checks.append(check_file_content("Procfile", "web:", "Comando web no Procfile"))
    
    # Verificar conteúdo do railway.json
    checks.append(check_file_content("railway.json", "startCommand", "Comando de start no railway.json"))
    
    # Verificar requirements.txt
    checks.append(check_file_content("backend/requirements.txt", "Flask", "Flask no requirements"))
    checks.append(check_file_content("backend/requirements.txt", "gunicorn", "Gunicorn no requirements"))
    
    # Verificar configuração de porta no app
    checks.append(check_file_content("backend/polling_app.py", "os.environ.get('PORT'", "Configuração de porta dinâmica"))
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 TUDO PRONTO PARA DEPLOY NO RAILWAY!")
        print("\n📋 Próximos passos:")
        print("1. npm install -g @railway/cli")
        print("2. railway login")
        print("3. railway link")
        print("4. git add . && git commit -m 'Deploy to Railway'")
        print("5. git push origin main")
        print("\n🌐 Seu app estará disponível em: https://seu-projeto.railway.app")
    else:
        print("❌ ALGUNS PROBLEMAS ENCONTRADOS!")
        print("Verifique os itens marcados com ❌ antes de fazer deploy.")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
