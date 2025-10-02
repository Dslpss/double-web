#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste específico do endpoint /casino/games
"""

import asyncio
import aiohttp
import json
from weebet_api_integrator import WeeBetAPI

async def test_casino_games():
    """Testa o endpoint /casino/games com diferentes métodos e payloads."""
    print("🎰 TESTANDO ENDPOINT /casino/games")
    print("=" * 50)
    
    api = WeeBetAPI()
    credentials = await api.login()
    
    if not credentials:
        print("❌ Falha no login")
        return
    
    print(f"✅ Logado como: {credentials.user_name}")
    
    url = f"{api.base_url}/casino/games"
    headers = credentials.get_auth_headers()
    
    # Diferentes payloads para testar
    test_payloads = [
        {},  # Vazio
        {"limit": 50},
        {"category": "roulette"},
        {"type": "live"},
        {"provider": "pragmatic"},
        {"game_type": "roulette"},
        {"live": True},
        {"page": 1, "limit": 20},
        {"filters": {"category": "live"}},
        {"search": "roulette"},
        {"action": "list"},
        {"method": "get_games"},
        {"request": "games_list"}
    ]
    
    async with aiohttp.ClientSession() as session:
        print("\n🔄 Testando método POST com diferentes payloads:")
        
        for i, payload in enumerate(test_payloads, 1):
            print(f"\n[{i:2d}] Payload: {json.dumps(payload)}")
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    print(f"    Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"    ✅ JSON Response: {json.dumps(data, indent=2)}")
                        except:
                            text = await response.text()
                            print(f"    ✅ Text Response: {text[:200]}...")
                    elif response.status == 400:
                        try:
                            error = await response.json()
                            print(f"    ⚠️ Bad Request: {error}")
                        except:
                            print("    ⚠️ Bad Request (no details)")
                    elif response.status == 422:
                        try:
                            error = await response.json()
                            print(f"    📋 Validation Error: {error}")
                        except:
                            print("    📋 Validation Error (no details)")
                    else:
                        print(f"    ❌ Error: {response.status}")
                        
            except Exception as e:
                print(f"    💥 Exception: {e}")
        
        # Testar outros métodos HTTP
        print(f"\n🔄 Testando outros métodos HTTP:")
        
        methods = ['PUT', 'PATCH', 'DELETE']
        for method in methods:
            print(f"\n{method} /casino/games")
            try:
                async with session.request(method, url, headers=headers, json={}) as response:
                    print(f"    Status: {response.status}")
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"    ✅ Response: {data}")
                        except:
                            text = await response.text()
                            print(f"    ✅ Text: {text[:100]}...")
            except Exception as e:
                print(f"    💥 Exception: {e}")

async def test_other_promising_endpoints():
    """Testa outros endpoints que podem existir."""
    print("\n\n🔍 TESTANDO OUTROS ENDPOINTS PROMISSORES")
    print("=" * 50)
    
    api = WeeBetAPI()
    if not api.credentials:
        await api.login()
    
    headers = api.credentials.get_auth_headers()
    
    # Endpoints baseados na estrutura que já conhecemos
    promising_endpoints = [
        "/user/account-verification",  # Já sabemos que funciona
        "/user/balance-info",
        "/user/game-history", 
        "/user/transactions-history",
        "/casino/game-list",
        "/casino/live-games",
        "/casino/game-providers",
        "/game/list",
        "/game/providers",
        "/live/games-list",
        "/live/roulette-tables",
        "/betting/history",
        "/betting/active",
        "/wallet/balance",
        "/wallet/transactions"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in promising_endpoints:
            print(f"\nGET {endpoint}")
            
            try:
                url = f"{api.base_url}{endpoint}"
                async with session.get(url, headers=headers) as response:
                    print(f"    Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"    ✅ JSON: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            text = await response.text()
                            print(f"    ✅ Text: {text[:100]}...")
                    elif response.status == 405:
                        # Tentar POST
                        print(f"    ⚠️ 405 - Tentando POST...")
                        async with session.post(url, headers=headers, json={}) as post_response:
                            print(f"    POST Status: {post_response.status}")
                            if post_response.status == 200:
                                try:
                                    data = await post_response.json()
                                    print(f"    ✅ POST JSON: {json.dumps(data, indent=2)[:200]}...")
                                except:
                                    text = await post_response.text()
                                    print(f"    ✅ POST Text: {text[:100]}...")
                            
            except Exception as e:
                print(f"    💥 Exception: {e}")

async def main():
    """Função principal."""
    await test_casino_games()
    await test_other_promising_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
