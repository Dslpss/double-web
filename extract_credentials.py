#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para extrair credenciais do navegador para usar na roleta
Execute este script depois de fazer login no Blaze
"""

import sys
import os

def main():
    print("🔑 EXTRATOR DE CREDENCIAIS DO BLAZE")
    print("="*50)
    print()
    print("📋 INSTRUÇÕES:")
    print("1. Faça login no Blaze no seu navegador")
    print("2. Acesse o jogo Double ou Roleta")
    print("3. Execute este script")
    print()
    print("🔍 Procurando credenciais...")
    
    try:
        from auth_extractor import extract_and_save_credentials
        
        credentials = extract_and_save_credentials()
        
        print()
        print("✅ SUCESSO!")
        print("🎯 As credenciais foram extraídas e salvas.")
        print("🔄 Agora reinicie o sistema da roleta para usar as credenciais.")
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("1. Pare o sistema atual (Ctrl+C)")
        print("2. Execute: python start_complete_system.py")
        print("3. Teste a roleta - deve funcionar com dados reais!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro: Módulo não encontrado - {e}")
        print("💡 Certifique-se de que auth_extractor.py está no mesmo diretório")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao extrair credenciais: {e}")
        print()
        print("🔧 POSSÍVEIS SOLUÇÕES:")
        print("1. Certifique-se de que fez login no Blaze")
        print("2. Feche o navegador e tente novamente")
        print("3. Execute como administrador")
        print("4. Verifique se o Chrome/Firefox está instalado")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print()
        print("⚠️  Se o problema persistir, o sistema continuará")
        print("   funcionando com dados simulados.")
    
    input("\nPressione Enter para continuar...")
