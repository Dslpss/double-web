#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do novo token JWT do PlayNaBets
Verifica se o token está funcionando corretamente
"""

import asyncio
import jwt
import time
from datetime import datetime
from pragmatic_roulette_api_monitor import PragmaticRouletteAPIMonitor

def decode_token_info(token_str):
    """Decodifica e mostra informações do token JWT."""
    try:
        # Decodificar sem verificar assinatura
        decoded = jwt.decode(token_str, options={"verify_signature": False})
        
        print("🔑 INFORMAÇÕES DO TOKEN JWT:")
        print(f"   User ID: {decoded.get('user', {}).get('id')}")
        
        # Timestamps
        iat = decoded.get('iat')  # Issued at
        exp = decoded.get('exp')  # Expires at
        
        if iat:
            iat_date = datetime.fromtimestamp(iat)
            print(f"   Emitido em: {iat_date.strftime('%d/%m/%Y %H:%M:%S')}")
        
        if exp:
            exp_date = datetime.fromtimestamp(exp)
            current_time = time.time()
            time_left = exp - current_time
            
            print(f"   Expira em: {exp_date.strftime('%d/%m/%Y %H:%M:%S')}")
            
            if time_left > 0:
                hours_left = int(time_left / 3600)
                minutes_left = int((time_left % 3600) / 60)
                print(f"   ⏰ Tempo restante: {hours_left}h {minutes_left}m")
                print(f"   ✅ Status: VÁLIDO")
            else:
                print(f"   ❌ Status: EXPIRADO há {abs(int(time_left/3600))} horas")
        
        return decoded
        
    except Exception as e:
        print(f"❌ Erro ao decodificar token: {e}")
        return None

async def test_token_with_api():
    """Testa o token com a API da Pragmatic Play."""
    print("\n🧪 TESTANDO TOKEN COM A API:")
    print("-" * 40)
    
    monitor = PragmaticRouletteAPIMonitor()
    
    # Testar acesso à API
    print("1. Verificando validade do token...")
    is_valid = monitor.check_token_validity()
    
    print("2. Testando acesso à API...")
    data = await monitor.fetch_api_data()
    
    if data:
        history = data.get('history', [])
        print(f"✅ Sucesso! API retornou {len(history)} jogos")
        
        if history:
            latest = history[0]
            print(f"   Último resultado: {latest.get('gameResult')} (ID: {latest.get('gameId')})")
        
        return True
    else:
        print("❌ Falha ao acessar API")
        return False

async def main():
    """Função principal do teste."""
    print("🔑 TESTE DO TOKEN JWT PLAYNABETS")
    print("=" * 50)
    
    # Token fornecido pelo usuário
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkzNzE2NzMsImV4cCI6MTc1OTk3NjQ3MywidXNlciI6eyJpZCI6NjMzMTR9fQ.mc98Vco9SO3NLY2bur9aeUzPluiC_6Mu8NMUfiq4McA"
    
    # Decodificar informações do token
    decoded = decode_token_info(token)
    
    if decoded:
        # Testar com a API
        api_success = await test_token_with_api()
        
        if api_success:
            print("\n🎉 TOKEN FUNCIONANDO PERFEITAMENTE!")
            print("✅ O sistema pode usar este token para acessar a API")
        else:
            print("\n⚠️ Token válido mas API não respondeu")
            print("💡 Pode ser necessário atualizar outros parâmetros")
    else:
        print("\n❌ Erro ao processar token")

if __name__ == "__main__":
    asyncio.run(main())
