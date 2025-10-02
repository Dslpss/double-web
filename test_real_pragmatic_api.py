#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste da API real da Pragmatic Play
Usando os parâmetros exatos fornecidos pelo usuário
"""

import asyncio
import aiohttp
import json
import time

async def test_real_pragmatic_api():
    """Testa a API real da Pragmatic Play."""
    print("🎮 TESTANDO API REAL PRAGMATIC PLAY")
    print("=" * 60)
    
    # Parâmetros exatos fornecidos pelo usuário
    api_url = "https://games.pragmaticplaylive.net/api/ui/statisticHistory"
    
    params = {
        'tableId': 'rwbrzportrwa16rg',
        'numberOfGames': 500,
        'JSESSIONID': 'TT-i7kAu6dD9JsG4ubagYrmYNH7jpmTCQitHDfOsC5QMKWdaX7PB!1928883527-12b99c5a',
        'ck': str(int(time.time() * 1000)),
        'game_mode': 'lobby_desktop'
    }
    
    # Headers exatos fornecidos pelo usuário
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://client.pragmaticplaylive.net',
        'Referer': 'https://client.pragmaticplaylive.net/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Te': 'trailers'
    }
    
    print(f"🔗 URL: {api_url}")
    print(f"🎲 Table ID: {params['tableId']}")
    print(f"🔑 JSESSIONID: {params['JSESSIONID'][:30]}...")
    print(f"⏰ Timestamp: {params['ck']}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Fazendo requisição...")
            async with session.get(api_url, headers=headers, params=params) as response:
                print(f"📊 Status: {response.status}")
                print(f"📋 Headers de resposta: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ JSON recebido!")
                        print(f"🔑 Chaves: {list(data.keys())}")
                        
                        if 'errorCode' in data:
                            print(f"📊 Error Code: {data['errorCode']}")
                            print(f"📝 Description: {data.get('description', 'N/A')}")
                        
                        if 'history' in data:
                            history = data['history']
                            print(f"🎲 Histórico: {len(history)} jogos")
                            
                            if history:
                                print(f"\n🎯 Últimos 5 resultados:")
                                for i, game in enumerate(history[:5], 1):
                                    game_id = game.get('gameId', 'N/A')
                                    result = game.get('gameResult', 'N/A')
                                    print(f"   {i}. ID: {game_id} | Resultado: {result}")
                                
                                return True
                        else:
                            print(f"📋 Estrutura completa:")
                            print(json.dumps(data, indent=2)[:1000] + "...")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Erro ao decodificar JSON: {e}")
                        text = await response.text()
                        print(f"📝 Resposta (texto): {text[:500]}...")
                        
                elif response.status == 401:
                    print(f"🔑 Erro 401: Não autorizado")
                    print(f"💡 JSESSIONID pode ter expirado")
                    
                elif response.status == 403:
                    print(f"🚫 Erro 403: Proibido")
                    print(f"💡 Pode precisar de headers adicionais")
                    
                else:
                    print(f"❌ Erro HTTP: {response.status}")
                    text = await response.text()
                    print(f"📝 Resposta: {text[:300]}...")
                    
    except Exception as e:
        print(f"💥 Erro na requisição: {e}")
        return False
    
    return False

async def test_multiple_requests():
    """Testa múltiplas requisições para verificar consistência."""
    print(f"\n🔄 TESTANDO MÚLTIPLAS REQUISIÇÕES")
    print("-" * 40)
    
    for i in range(3):
        print(f"\n📡 Requisição #{i+1}:")
        success = await test_real_pragmatic_api()
        if success:
            print(f"✅ Sucesso!")
        else:
            print(f"❌ Falha")
        
        if i < 2:  # Não esperar na última iteração
            print("⏳ Aguardando 5 segundos...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(test_multiple_requests())
