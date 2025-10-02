#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste rápido para capturar números da roleta
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime

async def quick_test():
    """Teste rápido para capturar números."""
    
    print("🎯 Teste Rápido - Captura de Números da Roleta")
    print("=" * 50)
    
    # Configurações
    base_url = "https://central.playnabet.com"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
    token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt',
        'Authorization': f'Bearer {token_usuario}',
        'Content-Type': 'application/json'
    }
    
    def get_color(number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def extract_numbers(content):
        """Extrai números da roleta."""
        numbers = set()
        
        # Padrões específicos
        patterns = [
            r'\b([0-3]?[0-6])\b',
            r'"number":\s*(\d+)',
            r'"result":\s*(\d+)',
            r'"value":\s*(\d+)',
            r'"winningNumber":\s*(\d+)',
            r'"lastNumber":\s*(\d+)',
            r'number\s*=\s*(\d+)',
            r'result\s*=\s*(\d+)',
            r'winningNumber\s*=\s*(\d+)',
            r'lastNumber\s*=\s*(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    num = int(match)
                    if 0 <= num <= 36:
                        numbers.add(num)
                except:
                    continue
        
        return sorted(list(numbers))
    
    try:
        # Testar Brazilian Roulette
        print("🎲 Testando Brazilian Roulette (ID: 237)...")
        
        params = {
            'token': token,
            'tokenUsuario': token_usuario,
            'symbol': '237',
            'language': 'pt',
            'playMode': 'REAL',
            'cashierUr': 'https://playnabet.com/clientes/deposito',
            'lobbyUrl': 'https://playnabet.com/casino',
            'fornecedor': 'pragmatic',
            'isMobile': 'false',
            'plataforma': 'pc'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"{base_url}/casino/games/url", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    game_url = data.get('gameURL')
                    print(f"✅ URL obtida: {game_url}")
                    
                    # Acessar o jogo
                    game_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': 'https://playnabets.com/'
                    }
                    
                    async with aiohttp.ClientSession(headers=game_headers) as game_session:
                        async with game_session.get(game_url, verify_ssl=False) as game_response:
                            if game_response.status == 200:
                                content = await game_response.text()
                                print(f"✅ Conteúdo obtido: {len(content)} caracteres")
                                
                                # Extrair números
                                numbers = extract_numbers(content)
                                
                                if numbers:
                                    print(f"\n🎲 NÚMEROS ENCONTRADOS ({len(numbers)}):")
                                    for num in numbers:
                                        color = get_color(num)
                                        print(f"  {num}: {color}")
                                    
                                    # Estatísticas
                                    red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
                                    black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
                                    green_count = sum(1 for n in numbers if n == 0)
                                    
                                    print(f"\n📊 ESTATÍSTICAS:")
                                    print(f"🔴 Vermelhos: {red_count}")
                                    print(f"⚫ Pretos: {black_count}")
                                    print(f"🟢 Verdes: {green_count}")
                                    
                                    # Salvar números para análise
                                    with open('roulette_numbers.json', 'w') as f:
                                        json.dump({
                                            'timestamp': datetime.now().isoformat(),
                                            'numbers': numbers,
                                            'statistics': {
                                                'red': red_count,
                                                'black': black_count,
                                                'green': green_count
                                            }
                                        }, f, indent=2)
                                    
                                    print(f"\n💾 Números salvos em 'roulette_numbers.json'")
                                    
                                else:
                                    print("❌ Nenhum número de roleta encontrado")
                                    
                                    # Salvar conteúdo para debug
                                    with open('debug_content.html', 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    print("💾 Conteúdo salvo em 'debug_content.html' para análise")
                                
                            else:
                                print(f"❌ Erro ao acessar jogo: {game_response.status}")
                
                else:
                    print(f"❌ Erro ao obter URL: {response.status}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())