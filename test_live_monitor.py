#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de monitor em tempo real por 30 segundos
"""

import asyncio
import aiohttp
import json
import re
import time
from datetime import datetime

async def test_live_monitor():
    """Testa monitor em tempo real por 30 segundos."""
    
    print("🎯 Teste de Monitor em Tempo Real (30 segundos)")
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
    
    # Variáveis para monitoramento
    all_numbers = set()
    last_numbers = set()
    check_count = 0
    new_numbers_count = 0
    
    try:
        print("🚀 Iniciando monitoramento por 30 segundos...")
        print("Pressione Ctrl+C para parar antes do tempo")
        print()
        
        start_time = time.time()
        
        while time.time() - start_time < 30:  # 30 segundos
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            print(f"🔍 Verificação #{check_count} - {current_time}")
            
            try:
                # Testar Brazilian Roulette
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
                                            
                                            if numbers:
                                                # Verificar se há números novos
                                                new_numbers = []
                                                for num in numbers:
                                                    if num not in last_numbers:
                                                        new_numbers.append(num)
                                                        last_numbers.add(num)
                                                        all_numbers.add(num)
                                                        new_numbers_count += 1
                                                        
                                                        color = get_color(num)
                                                        print(f"  🎲 NOVO: {num} {color}")
                                                
                                                if new_numbers:
                                                    print(f"✅ {len(new_numbers)} números novos encontrados!")
                                                else:
                                                    print(f"⏳ Nenhum número novo (total: {len(numbers)})")
                                            
                                            else:
                                                print("❌ Nenhum número encontrado")
                                        
                                        else:
                                            print(f"❌ Erro ao acessar jogo: {game_response.status}")
                            
                            else:
                                print("❌ URL não obtida")
                        
                        else:
                            print(f"❌ Erro ao obter URL: {response.status}")
            
            except Exception as e:
                print(f"❌ Erro na verificação: {e}")
            
            # Aguardar antes da próxima verificação
            print("⏳ Aguardando 5 segundos...")
            await asyncio.sleep(5)
        
        # Mostrar resultados finais
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"Verificações realizadas: {check_count}")
        print(f"Números únicos encontrados: {len(all_numbers)}")
        print(f"Números novos detectados: {new_numbers_count}")
        
        if all_numbers:
            final_numbers = sorted(list(all_numbers))
            print(f"Números: {final_numbers}")
            
            # Estatísticas
            red_count = sum(1 for n in final_numbers if n % 2 == 1 and n != 0)
            black_count = sum(1 for n in final_numbers if n % 2 == 0 and n != 0)
            green_count = sum(1 for n in final_numbers if n == 0)
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"🔴 Vermelhos: {red_count}")
            print(f"⚫ Pretos: {black_count}")
            print(f"🟢 Verdes: {green_count}")
            
            # Salvar resultado
            result = {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': 30,
                'checks_performed': check_count,
                'total_numbers': len(final_numbers),
                'new_numbers_detected': new_numbers_count,
                'numbers': final_numbers,
                'statistics': {
                    'red': red_count,
                    'black': black_count,
                    'green': green_count
                }
            }
            
            with open('live_test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n💾 Resultado salvo em 'live_test_result.json'")
        
        else:
            print("\n❌ Nenhum número foi encontrado")
    
    except KeyboardInterrupt:
        print("\n🛑 Monitor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_monitor())
