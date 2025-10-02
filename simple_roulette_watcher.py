#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Watcher simples para números da roleta
"""

import asyncio
import aiohttp
import json
import re
import time
from datetime import datetime

async def watch_roulette_numbers():
    """Monitora números da roleta em tempo real."""
    
    print("🎯 Monitor de Números da Roleta - PlayNabet")
    print("=" * 50)
    print("Pressione Ctrl+C para parar")
    print()
    
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
    
    # Jogos para monitorar
    games = [
        ('237', 'Brazilian Roulette'),
        ('210', 'Auto Mega Roulette'),
        ('203', 'Speed Roulette 1')
    ]
    
    last_numbers = set()
    all_results = []
    
    def get_color(number):
        """Determina a cor do número."""
        if number == 0:
            return '🟢 VERDE'
        elif number % 2 == 1:
            return '🔴 VERMELHO'
        else:
            return '⚫ PRETO'
    
    def extract_numbers(content):
        """Extrai números da roleta do conteúdo."""
        numbers = set()
        
        # Padrões para procurar números
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
                                numbers.add(num)
                        except:
                            continue
            except:
                continue
        
        return list(numbers)
    
    def show_statistics():
        """Mostra estatísticas."""
        if not all_results:
            return
        
        numbers = [r['number'] for r in all_results]
        
        print(f"\n📊 ESTATÍSTICAS ({len(numbers)} números):")
        print(f"Últimos 10: {numbers[-10:]}")
        
        red_count = sum(1 for n in numbers if n % 2 == 1 and n != 0)
        black_count = sum(1 for n in numbers if n % 2 == 0 and n != 0)
        green_count = sum(1 for n in numbers if n == 0)
        
        print(f"🔴 Vermelhos: {red_count} | ⚫ Pretos: {black_count} | 🟢 Verdes: {green_count}")
        print("-" * 50)
    
    try:
        while True:
            print(f"🔍 Verificando jogos... {datetime.now().strftime('%H:%M:%S')}")
            
            for game_id, game_name in games:
                try:
                    # Obter URL do jogo
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
                                
                                if game_url:
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
                                                
                                                # Extrair números
                                                numbers = extract_numbers(content)
                                                
                                                # Verificar se há números novos
                                                new_numbers = []
                                                for number in numbers:
                                                    if number not in last_numbers:
                                                        new_numbers.append(number)
                                                        last_numbers.add(number)
                                                        
                                                        # Adicionar resultado
                                                        result = {
                                                            'number': number,
                                                            'color': get_color(number),
                                                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                                                            'game': game_name
                                                        }
                                                        all_results.append(result)
                                                        
                                                        print(f"🎲 [{result['timestamp']}] {game_name}: {number} {result['color']}")
                                                        
                                                        # Mostrar estatísticas a cada 5 números
                                                        if len(all_results) % 5 == 0:
                                                            show_statistics()
                                                
                                                if new_numbers:
                                                    print(f"✅ {game_name}: {len(new_numbers)} novos números encontrados")
                                                else:
                                                    print(f"⏳ {game_name}: Nenhum número novo")
                                            
                                            else:
                                                print(f"❌ {game_name}: Erro {game_response.status}")
                                
                                else:
                                    print(f"❌ {game_name}: URL não obtida")
                            
                            else:
                                print(f"❌ {game_name}: Erro {response.status}")
                
                except Exception as e:
                    print(f"❌ Erro em {game_name}: {e}")
                
                # Aguardar entre jogos
                await asyncio.sleep(1)
            
            # Aguardar antes da próxima verificação
            print("⏳ Aguardando 10 segundos...")
            await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        print("\n🛑 Monitor interrompido pelo usuário")
        print(f"📊 Total de números capturados: {len(all_results)}")
        if all_results:
            show_statistics()

if __name__ == "__main__":
    asyncio.run(watch_roulette_numbers())
