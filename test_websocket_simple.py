#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste simples de conexão WebSocket (versão corrigida)
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
    
    try:
        print(f"🔌 Conectando ao WebSocket: {websocket_url}")
        
        # Conectar sem headers extras por enquanto
        async with websockets.connect(websocket_url) as websocket:
            
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
        print(f"Tipo do erro: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
