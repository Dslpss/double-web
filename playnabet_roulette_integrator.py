#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador para Roleta brasileira da PlayNabet
Baseado nos dados capturados do Burp Suite
"""

import asyncio
import aiohttp
import json
import time
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class PlayNabetRouletteIntegrator:
    """Integra dados da Roleta brasileira da PlayNabet."""
    
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.base_url = "https://central.playnabet.com"
        self.connected = False
        self.running = False
        self.last_result = None
        self.game_url = None
        self.session = None
        
        # Tokens da sua requisição
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.WzYzMzE0XQ.1BxRGal62pouh2TU9gbeCsIjOfPPUP1WqQY5ZunViso"
        self.token_usuario = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkwMjQ2NjQsImV4cCI6MTc1OTYyOTQ2NCwidXNlciI6eyJpZCI6NjMzMTR9fQ.BgvAuiW2_rUF8TUI9IdiV2swr3El7xN8qTrIgISN9AU"
        
        # IDs dos jogos de roleta brasileira
        self.roulette_games = {
            'brazilian_roulette': '237',  # Pragmatic - Demo
            'roleta_relampago': 'evo-oss-xs-roleta-relampago',  # Evolution
            'roleta_ao_vivo': 'evo-oss-xs-roleta-ao-vivo',  # Evolution
            'lightning_roulette': 'evo-oss-xs-xxxtreme-lightning-roulette'  # Evolution
        }
        
    def get_headers(self):
        """Retorna headers para requisições."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://playnabets.com/',
            'Content-Type': 'application/json',
            'Origin': 'https://playnabets.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Authorization': f'Bearer {self.token_usuario}',
            'Te': 'trailers'
        }
    
    async def get_live_games(self):
        """Obtém lista de jogos ao vivo."""
        try:
            url = f"{self.base_url}/casino/games/gamesAoVivo"
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                async with session.post(url, json={}) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Jogos ao vivo obtidos: {len(data.get('gameList', []))} jogos")
                        
                        # Filtrar apenas roletas
                        roulettes = [game for game in data.get('gameList', []) 
                                   if game.get('modalidade') == 'roulette']
                        print(f"🎲 Roletas encontradas: {len(roulettes)}")
                        
                        for roulette in roulettes:
                            print(f"  - {roulette.get('gameName')} (ID: {roulette.get('gameID')}) - {roulette.get('fornecedorExibicao')}")
                        
                        return data
                    else:
                        print(f"❌ Erro ao obter jogos ao vivo: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Erro ao obter jogos ao vivo: {e}")
            return None
    
    async def get_game_url(self, game_id):
        """Obtém URL do jogo específico."""
        try:
            url = f"{self.base_url}/casino/games/url"
            params = {
                'token': self.token,
                'tokenUsuario': self.token_usuario,
                'symbol': game_id,
                'language': 'pt',
                'playMode': 'REAL',
                'cashierUr': 'https://playnabet.com/clientes/deposito',
                'lobbyUrl': 'https://playnabet.com/casino',
                'fornecedor': 'pragmatic',  # Ajustar conforme o jogo
                'isMobile': 'false',
                'plataforma': 'pc'
            }
            
            async with aiohttp.ClientSession(headers=self.get_headers()) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        game_url = data.get('gameURL')
                        print(f"✅ URL do jogo {game_id}: {game_url}")
                        return game_url
                    else:
                        print(f"❌ Erro ao obter URL do jogo {game_id}: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Erro ao obter URL do jogo {game_id}: {e}")
            return None
    
    async def monitor_roulette_game(self, game_id, game_name):
        """Monitora um jogo específico de roleta."""
        print(f"🎯 Iniciando monitoramento: {game_name} (ID: {game_id})")
        
        # Obter URL do jogo
        game_url = await self.get_game_url(game_id)
        if not game_url:
            print(f"❌ Não foi possível obter URL para {game_name}")
            return
        
        try:
            # Headers específicos para o jogo
            game_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://playnabets.com/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1'
            }
            
            async with aiohttp.ClientSession(headers=game_headers) as session:
                while self.running:
                    try:
                        # Fazer requisição para obter dados do jogo
                        async with session.get(game_url, verify_ssl=False) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Analisar conteúdo em busca de dados da roleta
                                result = self.extract_roulette_data(content, game_name)
                                if result:
                                    self.process_result(result, game_name)
                                    
                            else:
                                print(f"⚠️ Status {response.status} para {game_name}")
                                
                    except Exception as e:
                        print(f"❌ Erro ao monitorar {game_name}: {e}")
                    
                    # Aguardar antes da próxima verificação
                    await asyncio.sleep(5)
                    
        except Exception as e:
            print(f"❌ Erro no monitoramento de {game_name}: {e}")
    
    def extract_roulette_data(self, content, game_name):
        """Extrai dados da roleta do conteúdo HTML/JS."""
        try:
            import re
            
            # Procurar por números de roleta (0-36)
            numbers = re.findall(r'\b([0-3]?[0-6])\b', content)
            valid_numbers = [int(n) for n in numbers if 0 <= int(n) <= 36]
            
            if valid_numbers:
                # Pegar o último número válido
                last_number = valid_numbers[-1]
                
                # Determinar cor baseada no número
                if last_number == 0:
                    color = 'green'
                elif last_number % 2 == 1:  # Ímpares
                    color = 'red'
                else:  # Pares
                    color = 'black'
                
                result = {
                    'number': last_number,
                    'color': color,
                    'round_id': f'round_{int(time.time())}',
                    'timestamp': int(time.time()),
                    'source': 'playnabet',
                    'game': game_name
                }
                
                return result
            
            # Procurar por dados JSON no conteúdo
            json_matches = re.findall(r'\{[^{}]*"number"[^{}]*\}', content)
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if 'number' in data:
                        number = int(data['number'])
                        if 0 <= number <= 36:
                            color = 'green' if number == 0 else 'red' if number % 2 == 1 else 'black'
                            return {
                                'number': number,
                                'color': color,
                                'round_id': data.get('round_id', f'round_{int(time.time())}'),
                                'timestamp': int(time.time()),
                                'source': 'playnabet',
                                'game': game_name
                            }
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados da roleta: {e}")
            return None
    
    def process_result(self, result, game_name):
        """Processa resultado da roleta."""
        try:
            print(f"🎲 {game_name}: {result['number']} ({result['color']}) - Round: {result['round_id']}")
            
            # Enviar para analyzer se disponível
            if self.analyzer:
                self.analyzer.add_manual_result(result['number'], result['color'])
            
            self.last_result = result
            
        except Exception as e:
            print(f"❌ Erro ao processar resultado: {e}")
    
    async def start_monitoring(self):
        """Inicia o monitoramento de todos os jogos de roleta."""
        print("🚀 Iniciando monitoramento da Roleta brasileira...")
        
        # Primeiro, obter lista de jogos ao vivo
        games_data = await self.get_live_games()
        if not games_data:
            print("❌ Não foi possível obter lista de jogos")
            return
        
        # Filtrar roletas
        roulettes = [game for game in games_data.get('gameList', []) 
                    if game.get('modalidade') == 'roulette']
        
        if not roulettes:
            print("❌ Nenhuma roleta encontrada")
            return
        
        # Iniciar monitoramento de cada roleta
        tasks = []
        for roulette in roulettes[:3]:  # Monitorar apenas as primeiras 3
            game_id = roulette.get('gameID')
            game_name = roulette.get('gameName')
            
            if game_id and game_name:
                task = asyncio.create_task(
                    self.monitor_roulette_game(game_id, game_name)
                )
                tasks.append(task)
        
        # Aguardar todas as tarefas
        if tasks:
            await asyncio.gather(*tasks)
    
    def start(self):
        """Inicia o integrador em thread separada."""
        if self.running:
            print("⚠️ Integrador já está rodando")
            return
            
        self.running = True
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.start_monitoring())
            except Exception as e:
                print(f"❌ Erro no loop principal: {e}")
            finally:
                loop.close()
        
        self.thread = threading.Thread(target=run_async, name="PlayNabetRouletteIntegrator")
        self.thread.start()
        
        print("🚀 Integrador da Roleta brasileira iniciado!")
    
    def stop(self):
        """Para o integrador."""
        print("🛑 Parando integrador da Roleta...")
        self.running = False
        self.connected = False
        
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=10)
    
    def get_status(self):
        """Retorna status do integrador."""
        return {
            'connected': self.connected,
            'running': self.running,
            'last_result': self.last_result,
            'base_url': self.base_url,
            'roulette_games': self.roulette_games
        }

# Instância global
roulette_integrator = None

def init_roulette_integrator(analyzer=None):
    """Inicializa o integrador da Roleta."""
    global roulette_integrator
    roulette_integrator = PlayNabetRouletteIntegrator(analyzer)
    return roulette_integrator

def start_roulette_connection():
    """Inicia conexão com a Roleta."""
    global roulette_integrator
    if roulette_integrator:
        roulette_integrator.start()

def stop_roulette_connection():
    """Para conexão com a Roleta."""
    global roulette_integrator
    if roulette_integrator:
        roulette_integrator.stop()

def get_roulette_status():
    """Retorna status da conexão da Roleta."""
    global roulette_integrator
    if roulette_integrator:
        return roulette_integrator.get_status()
    return {'connected': False, 'running': False}

# Teste rápido
if __name__ == "__main__":
    print("🎯 Testando integrador da Roleta brasileira...")
    
    integrator = PlayNabetRouletteIntegrator()
    
    # Teste 1: Obter jogos ao vivo
    print("\n1️⃣ Testando obtenção de jogos ao vivo...")
    asyncio.run(integrator.get_live_games())
    
    # Teste 2: Obter URL de um jogo específico
    print("\n2️⃣ Testando obtenção de URL do jogo...")
    asyncio.run(integrator.get_game_url('237'))  # Brazilian Roulette
    
    print("\n✅ Teste concluído!")
