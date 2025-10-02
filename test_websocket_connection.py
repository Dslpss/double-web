#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste simples de conexão WebSocket
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Testa conexão WebSocket."""
    
    print("🎯 Teste de Conexão WebSocket - Pragmatic Play")
    print("=" * 50)
    
    websocket_url = "wss://ws1.pragmaticplaylive.net/A16R-Generic"
    
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive, Upgrade',
        'Host': 'ws1.pragmaticplaylive.net',
        'Origin': 'https://client.pragmaticplaylive.net',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'websocket',
        'Sec-Fetch-Site': 'same-site',
        'Sec-WebSocket-Extensions': 'permessage-deflate',
        'Sec-WebSocket-Version': '13',
        'Upgrade': 'websocket',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0'
    }
    
    try:
        print(f"🔌 Conectando ao WebSocket: {websocket_url}")
        
        async with websockets.connect(
            websocket_url,
            extra_headers=headers,
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            
            print("✅ Conectado ao WebSocket!")
            print("🎯 Aguardando mensagens por 30 segundos...")
            print("Pressione Ctrl+C para parar")
            print()
            
            message_count = 0
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < 30:
                try:
                    # Aguardar mensagem com timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    message_count += 1
                    
                    print(f"📨 Mensagem #{message_count}:")
                    print(f"   Tamanho: {len(message)} caracteres")
                    print(f"   Conteúdo: {message[:200]}...")
                    
                    # Tentar parsear como JSON
                    try:
                        data = json.loads(message)
                        print(f"   JSON válido: {type(data)}")
                        
                        # Procurar por números de roleta
                        numbers = []
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, (int, float)) and 0 <= value <= 36:
                                    numbers.append(int(value))
                                elif isinstance(value, str) and value.isdigit():
                                    num = int(value)
                                    if 0 <= num <= 36:
                                        numbers.append(num)
                        
                        if numbers:
                            print(f"   🎲 Números encontrados: {numbers}")
                        else:
                            print(f"   ⏳ Nenhum número de roleta encontrado")
                    
                    except json.JSONDecodeError:
                        print(f"   ❌ Não é JSON válido")
                    
                    print("-" * 40)
                    
                except asyncio.TimeoutError:
                    print("⏳ Timeout - enviando ping...")
                    await websocket.ping()
                    
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Conexão WebSocket fechada")
                    break
                    
                except Exception as e:
                    print(f"❌ Erro: {e}")
                    break
            
            print(f"\n🎯 RESULTADO FINAL:")
            print(f"Mensagens recebidas: {message_count}")
            print(f"Tempo de teste: 30 segundos")
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
