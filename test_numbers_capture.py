#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste simples para capturar números da roleta
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime

async def test_number_capture():
    """Testa captura de números da roleta."""
    
    print("🎯 Testando captura de números da Roleta brasileira...")
    print("=" * 60)
    
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
    
    try:
        # 1. Obter lista de jogos ao vivo
        print("📡 1. Obtendo jogos ao vivo...")
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f"{base_url}/casino/games/gamesAoVivo", json={}) as response:
                if response.status == 200:
                    data = await response.json()
                    roulettes = [game for game in data.get('gameList', []) 
                               if game.get('modalidade') == 'roulette']
                    print(f"✅ Encontradas {len(roulettes)} roletas")
                    
                    # Mostrar roletas disponíveis
                    for i, roulette in enumerate(roulettes[:5], 1):
                        print(f"  {i}. {roulette.get('gameName')} (ID: {roulette.get('gameID')})")
                else:
                    print(f"❌ Erro: {response.status}")
                    return
        
        # 2. Obter URL da Brazilian Roulette
        print("\n🎲 2. Obtendo URL da Brazilian Roulette...")
        game_id = '237'  # Brazilian Roulette
        
        params = {
            'token': token,
            'tokenUsuario': token_usuario,
            'symbol': game_id,
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
                else:
                    print(f"❌ Erro ao obter URL: {response.status}")
                    return
        
        # 3. Acessar o jogo e procurar por números
        print("\n🔍 3. Analisando conteúdo do jogo...")
        
        game_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://playnabets.com/'
        }
        
        async with aiohttp.ClientSession(headers=game_headers) as session:
            async with session.get(game_url, verify_ssl=False) as response:
                if response.status == 200:
                    content = await response.text()
                    print(f"✅ Conteúdo obtido: {len(content)} caracteres")
                    
                    # Procurar por números de roleta
                    print("\n🔍 Procurando números de roleta...")
                    
                    # Padrões para procurar números
                    patterns = [
                        r'\b([0-3]?[0-6])\b',  # Números 0-36
                        r'"number":\s*(\d+)',
                        r'"result":\s*(\d+)',
                        r'"value":\s*(\d+)',
                        r'number\s*=\s*(\d+)',
                        r'result\s*=\s*(\d+)',
                        r'winningNumber\s*=\s*(\d+)',
                        r'lastNumber\s*=\s*(\d+)',
                        r'rouletteNumber\s*=\s*(\d+)',
                        r'gameResult\s*=\s*(\d+)'
                    ]
                    
                    all_numbers = set()
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            try:
                                num = int(match)
                                if 0 <= num <= 36:
                                    all_numbers.add(num)
                            except:
                                continue
                    
                    # Procurar por JSONs
                    json_matches = re.findall(r'\{[^{}]*\}', content)
                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            for key in ['number', 'result', 'value', 'winningNumber', 'lastNumber']:
                                if key in data:
                                    try:
                                        num = int(data[key])
                                        if 0 <= num <= 36:
                                            all_numbers.add(num)
                                    except:
                                        continue
                        except:
                            continue
                    
                    # Mostrar resultados
                    if all_numbers:
                        numbers = sorted(list(all_numbers))
                        print(f"🎲 Números encontrados: {numbers}")
                        
                        # Mostrar com cores
                        for num in numbers:
                            if num == 0:
                                color = "🟢 VERDE"
                            elif num % 2 == 1:
                                color = "🔴 VERMELHO"
                            else:
                                color = "⚫ PRETO"
                            print(f"  {num}: {color}")
                        
                        print(f"\n📊 Total: {len(numbers)} números únicos")
                        print(f"🔴 Vermelhos: {sum(1 for n in numbers if n % 2 == 1 and n != 0)}")
                        print(f"⚫ Pretos: {sum(1 for n in numbers if n % 2 == 0 and n != 0)}")
                        print(f"🟢 Verdes: {sum(1 for n in numbers if n == 0)}")
                        
                    else:
                        print("❌ Nenhum número de roleta encontrado")
                        
                        # Salvar conteúdo para análise
                        with open('game_content_debug.html', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("💾 Conteúdo salvo em 'game_content_debug.html' para análise")
                        
                        # Procurar por padrões específicos
                        print("\n🔍 Procurando por padrões específicos...")
                        
                        # Procurar por "roulette" no conteúdo
                        roulette_matches = re.findall(r'roulette[^"]*', content, re.IGNORECASE)
                        if roulette_matches:
                            print(f"Encontradas {len(roulette_matches)} menções a 'roulette'")
                            for match in roulette_matches[:5]:
                                print(f"  - {match[:100]}...")
                        
                        # Procurar por números em geral
                        all_nums = re.findall(r'\d+', content)
                        print(f"Total de números no conteúdo: {len(all_nums)}")
                        
                        # Mostrar alguns números encontrados
                        sample_nums = [int(n) for n in all_nums[:20] if n.isdigit()]
                        print(f"Primeiros números: {sample_nums}")
                
                else:
                    print(f"❌ Erro ao acessar jogo: {response.status}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    asyncio.run(test_number_capture())
