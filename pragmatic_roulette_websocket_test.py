#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de WebSocket da Roleta Pragmatic Play
Tenta diferentes URLs de WebSocket baseadas em padrões conhecidos
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_pragmatic_websockets():
    """Testa diferentes URLs de WebSocket da Pragmatic Play."""
    print("🔌 TESTANDO WEBSOCKETS DA ROLETA PRAGMATIC PLAY")
    print("=" * 60)
    
    base_host = "qcxjeqo01e.cjlcqchead.net"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
    
    # Possíveis URLs de WebSocket baseadas em padrões da Pragmatic Play
    websocket_urls = [
        f"wss://{base_host}/gs2c/websocket",
        f"wss://{base_host}/websocket",
        f"wss://{base_host}/ws",
        f"wss://{base_host}/socket.io/",
        f"wss://{base_host}/game/websocket",
        f"wss://{base_host}/live/websocket",
        f"wss://{base_host}/roulette/websocket",
        f"wss://{base_host}/desktop/classic-roulette2/websocket",
        f"ws://{base_host}/gs2c/websocket",
        f"ws://{base_host}/websocket",
        
        # URLs baseadas em outros domínios Pragmatic conhecidos
        "wss://api.pragmaticplaylive.net/websocket",
        "wss://live-api.pragmaticplay.net/websocket", 
        "wss://roulette.pragmaticplaylive.net/websocket",
        "wss://games.pragmaticplaylive.net/websocket"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Origin': f'https://{base_host}',
        'Sec-WebSocket-Protocol': 'chat',
        'Authorization': f'Bearer {token}'
    }
    
    for ws_url in websocket_urls:
        print(f"\n🔍 Testando: {ws_url}")
        
        try:
            # Tentar conectar com timeout curto
            async with websockets.connect(
                ws_url, 
                additional_headers=headers,
                ping_timeout=5,
                close_timeout=5
            ) as websocket:
                
                print(f"   ✅ CONECTADO!")
                
                # Mensagens de teste para autenticação/subscrição
                test_messages = [
                    # Autenticação
                    {"type": "auth", "token": token},
                    {"action": "authenticate", "token": token},
                    {"cmd": "auth", "data": {"token": token}},
                    
                    # Subscrição à roleta
                    {"type": "subscribe", "channel": "roulette"},
                    {"action": "subscribe", "game": "roulette"},
                    {"cmd": "join", "table": "roulette"},
                    {"type": "join", "gameId": "237"},
                    
                    # Pedidos de histórico
                    {"type": "history", "limit": 10},
                    {"action": "getHistory", "count": 10},
                    {"cmd": "history"},
                    {"method": "getResults"},
                    
                    # Mensagens genéricas
                    {"ping": "pong"},
                    {"type": "ping"},
                    "ping"
                ]
                
                for msg in test_messages:
                    try:
                        if isinstance(msg, dict):
                            message = json.dumps(msg)
                        else:
                            message = msg
                        
                        print(f"   📤 Enviando: {message}")
                        await websocket.send(message)
                        
                        # Aguardar resposta
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=2)
                            print(f"   📥 Resposta: {response}")
                            
                            # Tentar parsear JSON
                            try:
                                data = json.loads(response)
                                if 'result' in data or 'number' in data or 'winning' in str(data).lower():
                                    print(f"   🎲 POSSÍVEL RESULTADO ENCONTRADO: {data}")
                            except:
                                pass
                                
                        except asyncio.TimeoutError:
                            print(f"   ⏰ Sem resposta")
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao enviar: {e}")
                
                # Aguardar mensagens automáticas por alguns segundos
                print(f"   👂 Escutando mensagens automáticas...")
                try:
                    for _ in range(5):  # 5 segundos
                        message = await asyncio.wait_for(websocket.recv(), timeout=1)
                        print(f"   📨 Mensagem automática: {message}")
                        
                        # Verificar se é resultado de roleta
                        try:
                            data = json.loads(message)
                            if 'result' in data or 'number' in data or 'winning' in str(data).lower():
                                print(f"   🎲 RESULTADO DA ROLETA: {data}")
                        except:
                            pass
                            
                except asyncio.TimeoutError:
                    print(f"   🔇 Nenhuma mensagem automática")
                
                # Se chegou até aqui, o WebSocket funciona!
                print(f"   🎉 WebSocket funcional encontrado!")
                return ws_url
                
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"   ❌ Status inválido: {e}")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"   ❌ Conexão fechada: {e}")
        except OSError as e:
            print(f"   ❌ Erro de rede: {e}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n❌ Nenhum WebSocket funcional encontrado")
    return None

async def test_socket_io():
    """Testa conexão Socket.IO."""
    print(f"\n🔌 TESTANDO SOCKET.IO")
    print("-" * 40)
    
    try:
        import socketio
        
        base_host = "qcxjeqo01e.cjlcqchead.net"
        
        # URLs Socket.IO para testar
        socketio_urls = [
            f"https://{base_host}",
            f"https://{base_host}/socket.io/",
            f"https://{base_host}/gs2c/",
            "https://api.pragmaticplaylive.net"
        ]
        
        for url in socketio_urls:
            print(f"\n🔍 Testando Socket.IO: {url}")
            
            try:
                sio = socketio.AsyncClient()
                
                @sio.event
                async def connect():
                    print(f"   ✅ Socket.IO conectado!")
                    
                    # Tentar se autenticar
                    await sio.emit('auth', {
                        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso'
                    })
                    
                    # Tentar se inscrever na roleta
                    await sio.emit('subscribe', {'game': 'roulette'})
                    await sio.emit('join', {'table': 'roulette'})
                
                @sio.event
                async def disconnect():
                    print(f"   🔌 Socket.IO desconectado")
                
                @sio.event
                async def message(data):
                    print(f"   📨 Mensagem Socket.IO: {data}")
                
                # Eventos específicos da roleta
                @sio.on('roulette_result')
                async def roulette_result(data):
                    print(f"   🎲 RESULTADO DA ROLETA: {data}")
                
                @sio.on('game_result')
                async def game_result(data):
                    print(f"   🎮 RESULTADO DO JOGO: {data}")
                
                await sio.connect(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0'
                })
                
                # Aguardar alguns segundos
                await asyncio.sleep(5)
                
                await sio.disconnect()
                
            except Exception as e:
                print(f"   ❌ Erro Socket.IO: {e}")
    
    except ImportError:
        print("   ⚠️ python-socketio não instalado")

async def main():
    """Função principal."""
    working_ws = await test_pragmatic_websockets()
    
    if working_ws:
        print(f"\n🎉 WEBSOCKET FUNCIONAL ENCONTRADO: {working_ws}")
    
    await test_socket_io()

if __name__ == "__main__":
    asyncio.run(main())
