#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste direto da URL da Roleta Brasileira
Usa a URL exata fornecida pelo usuário
"""

import asyncio
import aiohttp
import json
import re
from urllib.parse import parse_qs, urlparse, unquote

async def test_direct_roulette_access():
    """Testa acesso direto à URL da roleta."""
    print("🎲 TESTE DIRETO DA ROLETA BRASILEIRA")
    print("=" * 50)
    
    # URL exata fornecida pelo usuário
    game_url = "https://qcxjeqo01e.cjlcqchead.net/gs2c/playGame.do?key=token%3DeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso%60%7C%60symbol%3D237%60%7C%60language%3Dpt%60%7C%60lobbyUrl%3Dhttps%3A%2F%2Fplaynabet.com%2Fcasino&ppkv=2&stylename=weebet_playnabet&isGameUrlApiCalled=true"
    
    print(f"🔗 URL: {game_url}")
    
    # Extrair informações da URL
    parsed = urlparse(game_url)
    params = parse_qs(parsed.query)
    
    print(f"\n📋 Informações extraídas:")
    print(f"   Host: {parsed.netloc}")
    print(f"   Path: {parsed.path}")
    
    if 'key' in params:
        key_param = unquote(params['key'][0])
        print(f"   Key: {key_param}")
        
        # Extrair token
        token_match = re.search(r'token=([^%|&`]+)', key_param)
        if token_match:
            token = token_match.group(1)
            print(f"   🔑 Token: {token}")
        
        # Extrair symbol (game ID)
        symbol_match = re.search(r'symbol=(\d+)', key_param)
        if symbol_match:
            game_id = symbol_match.group(1)
            print(f"   🎮 Game ID: {game_id}")
    
    # Base URL para APIs
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    print(f"   🌐 Base URL: {base_url}")
    
    # Headers para requisições
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': game_url,
        'Origin': base_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    # Testar acesso à página do jogo
    print(f"\n🔍 Testando acesso à página do jogo...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(game_url, headers=headers) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"   ✅ Página carregada ({len(content)} chars)")
                    
                    # Procurar por APIs ou WebSockets no conteúdo
                    api_patterns = [
                        r'api["\']?\s*:\s*["\']([^"\']+)',
                        r'websocket["\']?\s*:\s*["\']([^"\']+)',
                        r'ws["\']?\s*:\s*["\']([^"\']+)',
                        r'endpoint["\']?\s*:\s*["\']([^"\']+)',
                        r'url["\']?\s*:\s*["\']([^"\']+api[^"\']*)',
                        r'history["\']?\s*:\s*["\']([^"\']+)',
                        r'results["\']?\s*:\s*["\']([^"\']+)'
                    ]
                    
                    found_apis = []
                    for pattern in api_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        found_apis.extend(matches)
                    
                    if found_apis:
                        print(f"   📡 APIs encontradas:")
                        for api in set(found_apis):
                            print(f"      {api}")
                    
                    # Procurar por WebSocket
                    ws_patterns = [
                        r'new\s+WebSocket\s*\(\s*["\']([^"\']+)',
                        r'websocket\s*=\s*["\']([^"\']+)',
                        r'ws://[^"\'\s]+',
                        r'wss://[^"\'\s]+'
                    ]
                    
                    found_ws = []
                    for pattern in ws_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        found_ws.extend(matches)
                    
                    if found_ws:
                        print(f"   🔌 WebSockets encontrados:")
                        for ws in set(found_ws):
                            print(f"      {ws}")
                    
                    # Salvar conteúdo para análise
                    with open('roulette_page_content.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   💾 Conteúdo salvo em 'roulette_page_content.html'")
                    
                else:
                    print(f"   ❌ Erro: {response.status}")
                    
        except Exception as e:
            print(f"   💥 Erro: {e}")
    
    # Testar endpoints comuns de API
    print(f"\n🔍 Testando endpoints de API...")
    
    api_endpoints = [
        "/gs2c/api/history",
        "/gs2c/api/results", 
        "/gs2c/history",
        "/gs2c/results",
        "/gs2c/getHistory",
        "/gs2c/getResults",
        "/gs2c/gameHistory",
        "/gs2c/rouletteHistory",
        "/api/history",
        "/api/results",
        "/api/game/history",
        "/api/roulette/history",
        "/history",
        "/results"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in api_endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\n   GET {endpoint}")
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"      Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"      ✅ JSON: {json.dumps(data, indent=2)}")
                        except:
                            text = await response.text()
                            print(f"      ✅ Text: {text[:200]}...")
                    elif response.status == 405:
                        print(f"      ⚠️ Method not allowed - tentando POST...")
                        
                        # Tentar POST
                        async with session.post(url, headers=headers, json={}) as post_response:
                            print(f"      POST Status: {post_response.status}")
                            if post_response.status == 200:
                                try:
                                    data = await post_response.json()
                                    print(f"      ✅ POST JSON: {json.dumps(data, indent=2)}")
                                except:
                                    text = await post_response.text()
                                    print(f"      ✅ POST Text: {text[:200]}...")
                    else:
                        print(f"      ❌ {response.status}")
                        
            except Exception as e:
                print(f"      💥 Erro: {e}")
    
    # Testar WebSocket
    print(f"\n🔌 Testando WebSocket...")
    
    ws_urls = [
        f"wss://{parsed.netloc}/gs2c/websocket",
        f"wss://{parsed.netloc}/websocket", 
        f"wss://{parsed.netloc}/ws",
        f"ws://{parsed.netloc}/gs2c/websocket"
    ]
    
    for ws_url in ws_urls:
        print(f"\n   Tentando: {ws_url}")
        
        try:
            import websockets
            
            ws_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Origin': base_url
            }
            
            async with websockets.connect(ws_url, extra_headers=ws_headers, ping_timeout=5) as websocket:
                print(f"      ✅ Conectado!")
                
                # Tentar enviar mensagem de teste
                test_messages = [
                    '{"type":"subscribe","channel":"roulette"}',
                    '{"action":"join","game":"roulette"}',
                    '{"method":"getHistory"}',
                    '{"cmd":"history"}'
                ]
                
                for msg in test_messages:
                    try:
                        await websocket.send(msg)
                        print(f"      📤 Enviado: {msg}")
                        
                        # Aguardar resposta
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        print(f"      📥 Recebido: {response}")
                        
                    except asyncio.TimeoutError:
                        print(f"      ⏰ Timeout para: {msg}")
                    except Exception as e:
                        print(f"      ❌ Erro: {e}")
                
                break  # Se conectou, não precisa testar outros
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_roulette_access())
