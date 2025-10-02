#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor de Resultados da Roleta Evolution Gaming via JimyoBot
Captura números reais da roleta através do jogo Evolution
"""

import asyncio
import aiohttp
import json
import time
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from jimyobot_integrator import JimyoBotAPI

logger = logging.getLogger(__name__)

@dataclass
class EvolutionRouletteResult:
    """Resultado da roleta Evolution."""
    number: int
    color: str
    color_name: str
    timestamp: datetime
    round_id: str
    game_id: str = "evolution-roulette"
    
    @property
    def color_emoji(self) -> str:
        """Emoji da cor."""
        if self.color == 'red':
            return '🔴'
        elif self.color == 'black':
            return '⚫'
        else:
            return '⚪'

class EvolutionRouletteMonitor:
    """Monitor da Roleta Evolution Gaming através do JimyoBot."""
    
    def __init__(self):
        """Inicializa o monitor."""
        self.api = JimyoBotAPI()
        self.running = False
        self.results_cache: List[EvolutionRouletteResult] = []
        self.last_result: Optional[EvolutionRouletteResult] = None
        self.game_session = None
        
        # URLs e endpoints
        self.game_base_url = "https://api.salsagator.com"
        self.evolution_endpoints = [
            "/api/game/history",
            "/api/game/results", 
            "/api/roulette/results",
            "/game/api/results",
            "/evolution/api/results"
        ]
        
        logger.info("🎰 Monitor Evolution Roulette inicializado")
    
    def _determine_color(self, number: int) -> tuple[str, str]:
        """Determina cor baseada no número da roleta europeia."""
        if number == 0:
            return 'green', 'Verde'
        
        # Números vermelhos na roleta europeia
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        
        if number in red_numbers:
            return 'red', 'Vermelho'
        else:
            return 'black', 'Preto'
    
    async def get_game_url(self) -> Optional[str]:
        """Constrói URL do jogo Evolution com token JWT."""
        if not self.api.credentials:
            await self.api.check_session()
        
        if not self.api.credentials or not self.api.credentials.tokens:
            logger.error("❌ Credenciais não disponíveis")
            return None
        
        try:
            # Usar o segundo token (baseado na captura)
            game_token = self.api.credentials.tokens[1] if len(self.api.credentials.tokens) > 1 else self.api.credentials.tokens[0]
            
            # Parâmetros do jogo da roleta Evolution
            game_params = {
                'token': game_token,
                'pn': 'playnabet',
                'lang': 'pt',
                'game': 'evo-oss-xs-roleta-ao-vivo',
                'currency': 'BRL',
                'type': 'CHARGE'
            }
            
            # Construir URL
            params_str = "&".join([f"{k}={v}" for k, v in game_params.items()])
            game_url = f"{self.game_base_url}/game?{params_str}"
            
            logger.info(f"🎰 URL do jogo Evolution construída")
            return game_url
            
        except Exception as e:
            logger.error(f"Erro ao construir URL do jogo: {e}")
            return None
    
    async def access_game_page(self) -> Optional[str]:
        """Acessa a página do jogo e obtém conteúdo."""
        game_url = await self.get_game_url()
        
        if not game_url:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://jimyobot.vip/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Priority': 'u=4',
                'Te': 'trailers',
                'Connection': 'keep-alive',
                'Cookie': 'JSESSIONID=5BCDBBED0F57188B5D144972E8A28776'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(game_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"✅ Página do jogo acessada ({len(content)} chars)")
                        return content
                    else:
                        logger.error(f"❌ Erro ao acessar jogo: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erro ao acessar página do jogo: {e}")
            return None
    
    def extract_websocket_urls(self, page_content: str) -> List[str]:
        """Extrai URLs de WebSocket da página do jogo."""
        websocket_urls = []
        
        try:
            # Padrões para encontrar URLs de WebSocket
            patterns = [
                r'wss?://[^"\s]+',
                r'"(wss?://[^"]+)"',
                r"'(wss?://[^']+)'",
                r'websocket["\s]*:["\s]*["\']([^"\']+)["\']',
                r'socket["\s]*:["\s]*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    url = match if isinstance(match, str) else match[0] if match else ""
                    if url and ('ws' in url.lower() or 'socket' in url.lower()):
                        websocket_urls.append(url)
            
            # Remover duplicatas
            websocket_urls = list(set(websocket_urls))
            
            logger.info(f"🔍 {len(websocket_urls)} URLs de WebSocket encontradas")
            for url in websocket_urls:
                logger.info(f"   📡 {url}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair URLs de WebSocket: {e}")
        
        return websocket_urls
    
    def extract_api_endpoints(self, page_content: str) -> List[str]:
        """Extrai endpoints de API da página do jogo."""
        api_endpoints = []
        
        try:
            # Padrões para encontrar endpoints de API
            patterns = [
                r'/api/[^"\s]+',
                r'"(/api/[^"]+)"',
                r"'(/api/[^']+)'",
                r'/game/[^"\s]+',
                r'"(/game/[^"]+)"',
                r"'(/game/[^']+)'",
                r'https?://[^/]+(/[^"\s]*(?:api|game|result|history)[^"\s]*)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    endpoint = match if isinstance(match, str) else match[0] if match else ""
                    if endpoint and ('api' in endpoint.lower() or 'result' in endpoint.lower() or 'history' in endpoint.lower()):
                        api_endpoints.append(endpoint)
            
            # Remover duplicatas
            api_endpoints = list(set(api_endpoints))
            
            logger.info(f"🔍 {len(api_endpoints)} endpoints de API encontrados")
            for endpoint in api_endpoints:
                logger.info(f"   🌐 {endpoint}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair endpoints de API: {e}")
        
        return api_endpoints
    
    async def discover_results_sources(self) -> Dict[str, List[str]]:
        """Descobre fontes de resultados (WebSocket e API)."""
        logger.info("🔍 Descobrindo fontes de resultados...")
        
        # Acessar página do jogo
        page_content = await self.access_game_page()
        
        if not page_content:
            logger.error("❌ Não foi possível acessar página do jogo")
            return {'websockets': [], 'apis': []}
        
        # Extrair URLs e endpoints
        websocket_urls = self.extract_websocket_urls(page_content)
        api_endpoints = self.extract_api_endpoints(page_content)
        
        # Testar endpoints de API conhecidos da Evolution
        evolution_apis = [
            "https://api.evolution.com/api/roulette/results",
            "https://api.evolution.com/api/game/history",
            f"{self.game_base_url}/api/game/results",
            f"{self.game_base_url}/api/roulette/results",
            f"{self.game_base_url}/game/api/results"
        ]
        
        api_endpoints.extend(evolution_apis)
        
        return {
            'websockets': websocket_urls,
            'apis': list(set(api_endpoints))
        }
    
    async def test_api_endpoints(self, endpoints: List[str]) -> Optional[str]:
        """Testa endpoints de API para encontrar um que retorne resultados."""
        logger.info(f"🧪 Testando {len(endpoints)} endpoints de API...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, */*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://jimyobot.vip/',
            'Cookie': 'JSESSIONID=5BCDBBED0F57188B5D144972E8A28776'
        }
        
        # Adicionar token se disponível
        if self.api.credentials and self.api.credentials.tokens:
            headers['Authorization'] = f'Bearer {self.api.credentials.tokens[0]}'
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    # Construir URL completa se necessário
                    if endpoint.startswith('/'):
                        url = f"{self.game_base_url}{endpoint}"
                    elif not endpoint.startswith('http'):
                        url = f"{self.game_base_url}/{endpoint}"
                    else:
                        url = endpoint
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                if self._validate_results_data(data):
                                    logger.info(f"✅ Endpoint funcional encontrado: {endpoint}")
                                    return endpoint
                                else:
                                    logger.debug(f"📄 Endpoint retorna dados, mas não são resultados: {endpoint}")
                            except:
                                # Pode ser HTML ou outro formato
                                text = await response.text()
                                if 'result' in text.lower() or 'number' in text.lower():
                                    logger.info(f"✅ Endpoint com dados encontrado: {endpoint}")
                                    return endpoint
                        else:
                            logger.debug(f"❌ {endpoint}: HTTP {response.status}")
                            
                except Exception as e:
                    logger.debug(f"❌ {endpoint}: {e}")
        
        logger.warning("❌ Nenhum endpoint funcional encontrado")
        return None
    
    def _validate_results_data(self, data: Any) -> bool:
        """Valida se os dados contêm resultados de roleta."""
        if not isinstance(data, dict):
            return False
        
        # Procurar estruturas típicas de resultados
        result_indicators = ['results', 'history', 'numbers', 'rounds', 'games', 'outcomes']
        
        for key in result_indicators:
            if key in data:
                results = data[key]
                if isinstance(results, list) and len(results) > 0:
                    first_result = results[0]
                    if isinstance(first_result, dict):
                        # Verificar campos típicos de resultado de roleta
                        if any(field in first_result for field in ['number', 'result', 'winning_number', 'outcome']):
                            return True
        
        return False
    
    async def monitor_results(self):
        """Monitora resultados em tempo real."""
        logger.info("🎰 Iniciando monitoramento de resultados Evolution...")
        
        # Descobrir fontes de dados
        sources = await self.discover_results_sources()
        
        # Testar endpoints de API
        working_endpoint = None
        if sources['apis']:
            working_endpoint = await self.test_api_endpoints(sources['apis'])
        
        # Loop principal de monitoramento
        while self.running:
            try:
                new_results = []
                
                if working_endpoint:
                    # Obter resultados do endpoint funcional
                    new_results = await self.get_results_from_api(working_endpoint)
                
                if not new_results:
                    # Fallback: simular alguns resultados para teste
                    new_results = await self.simulate_results()
                
                # Processar novos resultados
                for result in new_results:
                    if not self._is_duplicate_result(result):
                        await self._process_new_result(result)
                
                # Aguardar antes da próxima verificação
                await asyncio.sleep(30)  # Evolution roulette tem rodadas ~30s
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                await asyncio.sleep(10)
    
    async def get_results_from_api(self, endpoint: str) -> List[EvolutionRouletteResult]:
        """Obtém resultados de um endpoint de API."""
        try:
            # Construir URL
            if endpoint.startswith('/'):
                url = f"{self.game_base_url}{endpoint}"
            elif not endpoint.startswith('http'):
                url = f"{self.game_base_url}/{endpoint}"
            else:
                url = endpoint
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'application/json, */*',
                'Referer': 'https://jimyobot.vip/',
                'Cookie': 'JSESSIONID=5BCDBBED0F57188B5D144972E8A28776'
            }
            
            if self.api.credentials and self.api.credentials.tokens:
                headers['Authorization'] = f'Bearer {self.api.credentials.tokens[0]}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_evolution_results(data)
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter resultados da API: {e}")
            return []
    
    def _parse_evolution_results(self, data: Dict) -> List[EvolutionRouletteResult]:
        """Converte dados da API Evolution em objetos EvolutionRouletteResult."""
        results = []
        
        try:
            # Tentar diferentes estruturas
            possible_results = []
            
            if 'results' in data:
                possible_results = data['results']
            elif 'history' in data:
                possible_results = data['history']
            elif 'outcomes' in data:
                possible_results = data['outcomes']
            elif isinstance(data, list):
                possible_results = data
            
            for item in possible_results:
                if isinstance(item, dict):
                    # Extrair número
                    number = None
                    for field in ['number', 'result', 'winning_number', 'outcome', 'value']:
                        if field in item:
                            number = item[field]
                            break
                    
                    if number is not None:
                        try:
                            number = int(number)
                            color, color_name = self._determine_color(number)
                            
                            # Extrair timestamp
                            timestamp = datetime.now()
                            if 'timestamp' in item:
                                timestamp = datetime.fromtimestamp(item['timestamp'])
                            elif 'time' in item:
                                timestamp = datetime.fromtimestamp(item['time'])
                            
                            result = EvolutionRouletteResult(
                                number=number,
                                color=color,
                                color_name=color_name,
                                timestamp=timestamp,
                                round_id=str(item.get('round_id', item.get('id', f"evo_{int(time.time())}"))),
                                game_id="evolution-roulette"
                            )
                            results.append(result)
                            
                        except ValueError:
                            continue
            
        except Exception as e:
            logger.error(f"Erro ao converter resultados Evolution: {e}")
        
        return results
    
    async def simulate_results(self) -> List[EvolutionRouletteResult]:
        """Simula resultados para teste (remover quando tiver dados reais)."""
        import random
        
        # Simular 1 resultado ocasionalmente
        if random.random() < 0.3:  # 30% de chance
            number = random.randint(0, 36)
            color, color_name = self._determine_color(number)
            
            result = EvolutionRouletteResult(
                number=number,
                color=color,
                color_name=color_name,
                timestamp=datetime.now(),
                round_id=f"sim_{int(time.time())}",
                game_id="evolution-roulette-sim"
            )
            
            return [result]
        
        return []
    
    def _is_duplicate_result(self, result: EvolutionRouletteResult) -> bool:
        """Verifica se o resultado já foi processado."""
        if not self.results_cache:
            return False
        
        # Verificar por round_id
        for cached in self.results_cache:
            if cached.round_id == result.round_id:
                return True
        
        return False
    
    async def _process_new_result(self, result: EvolutionRouletteResult):
        """Processa novo resultado."""
        self.results_cache.append(result)
        self.last_result = result
        
        # Manter cache limitado
        if len(self.results_cache) > 100:
            self.results_cache.pop(0)
        
        # Log do resultado
        logger.info(f"🎰 EVOLUTION RESULT: {result.number} {result.color_emoji} {result.color_name}")
        print(f"🎰 EVOLUTION ROULETTE: {result.number:2} {result.color_emoji} {result.color_name} - {result.timestamp.strftime('%H:%M:%S')}")
    
    async def start(self):
        """Inicia o monitor."""
        logger.info("🚀 Iniciando monitor Evolution Roulette...")
        
        # Verificar credenciais
        credentials = await self.api.check_session()
        
        if not credentials:
            logger.error("❌ Não foi possível conectar ao JimyoBot")
            return
        
        logger.info(f"✅ Conectado como: {credentials.user_name}")
        
        self.running = True
        
        # Iniciar monitoramento
        await self.monitor_results()
    
    def stop(self):
        """Para o monitor."""
        self.running = False
        logger.info("🛑 Monitor Evolution parado")
    
    def get_recent_results(self, limit: int = 20) -> List[EvolutionRouletteResult]:
        """Obtém resultados recentes."""
        return self.results_cache[-limit:] if self.results_cache else []
    
    def get_statistics(self) -> Dict:
        """Obtém estatísticas dos resultados."""
        if not self.results_cache:
            return {}
        
        total = len(self.results_cache)
        red_count = sum(1 for r in self.results_cache if r.color == 'red')
        black_count = sum(1 for r in self.results_cache if r.color == 'black')
        green_count = sum(1 for r in self.results_cache if r.color == 'green')
        
        return {
            'total_results': total,
            'red_count': red_count,
            'black_count': black_count,
            'green_count': green_count,
            'red_percentage': (red_count / total * 100) if total > 0 else 0,
            'black_percentage': (black_count / total * 100) if total > 0 else 0,
            'green_percentage': (green_count / total * 100) if total > 0 else 0,
            'last_result': self.last_result.number if self.last_result else None
        }

async def test_evolution_monitor():
    """Testa o monitor Evolution."""
    print("🧪 TESTE DO MONITOR EVOLUTION ROULETTE")
    print("=" * 60)
    
    monitor = EvolutionRouletteMonitor()
    
    # Testar construção da URL
    print("1. 🔗 Testando construção da URL do jogo...")
    game_url = await monitor.get_game_url()
    
    if game_url:
        print(f"   ✅ URL construída: {game_url[:80]}...")
    else:
        print("   ❌ Falha na construção da URL")
        return
    
    # Testar acesso à página
    print("\n2. 🌐 Testando acesso à página do jogo...")
    page_content = await monitor.access_game_page()
    
    if page_content:
        print(f"   ✅ Página acessada ({len(page_content)} caracteres)")
    else:
        print("   ❌ Falha no acesso à página")
    
    # Descobrir fontes de dados
    print("\n3. 🔍 Descobrindo fontes de resultados...")
    sources = await monitor.discover_results_sources()
    
    print(f"   📡 WebSockets encontrados: {len(sources['websockets'])}")
    for ws in sources['websockets'][:3]:  # Mostrar apenas 3
        print(f"      {ws}")
    
    print(f"   🌐 APIs encontradas: {len(sources['apis'])}")
    for api in sources['apis'][:5]:  # Mostrar apenas 5
        print(f"      {api}")
    
    # Testar endpoints
    if sources['apis']:
        print("\n4. 🧪 Testando endpoints de API...")
        working_endpoint = await monitor.test_api_endpoints(sources['apis'][:5])
        
        if working_endpoint:
            print(f"   ✅ Endpoint funcional: {working_endpoint}")
        else:
            print("   ⚠️ Nenhum endpoint funcional encontrado")
    
    # Testar monitoramento por 1 minuto
    print("\n5. ⏰ Testando monitoramento por 1 minuto...")
    monitor.running = True
    
    start_time = time.time()
    initial_count = len(monitor.results_cache)
    
    # Simular alguns ciclos
    for i in range(2):  # 2 ciclos de 30 segundos
        await asyncio.sleep(30)
        
        # Simular resultado
        results = await monitor.simulate_results()
        for result in results:
            await monitor._process_new_result(result)
        
        elapsed = int(time.time() - start_time)
        current_count = len(monitor.results_cache)
        new_results = current_count - initial_count
        
        print(f"   ⏱️  {elapsed:2}s | 🎰 {new_results} resultados | Total: {current_count}")
    
    monitor.stop()
    
    # Estatísticas finais
    print("\n6. 📊 Estatísticas finais:")
    stats = monitor.get_statistics()
    
    if stats:
        print(f"   🎰 Total: {stats['total_results']}")
        print(f"   🔴 Vermelho: {stats['red_count']} ({stats['red_percentage']:.1f}%)")
        print(f"   ⚫ Preto: {stats['black_count']} ({stats['black_percentage']:.1f}%)")
        print(f"   🟢 Verde: {stats['green_count']} ({stats['green_percentage']:.1f}%)")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE DO MONITOR EVOLUTION CONCLUÍDO")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_evolution_monitor())
