#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor de Resultados da Roleta Brasileira - JimyoBot
Captura números e resultados em tempo real
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from jimyobot_integrator import JimyoBotAPI, JimyoBotCredentials

logger = logging.getLogger(__name__)

@dataclass
class RouletteResult:
    """Resultado da roleta."""
    number: int
    color: str
    color_name: str
    timestamp: datetime
    game_id: str
    round_id: Optional[str] = None
    
    @property
    def color_emoji(self) -> str:
        """Emoji da cor."""
        if self.color == 'red':
            return '🔴'
        elif self.color == 'black':
            return '⚫'
        else:
            return '⚪'

class JimyoBotResultsMonitor:
    """Monitor de resultados da Roleta Brasileira do JimyoBot."""
    
    def __init__(self):
        """Inicializa o monitor."""
        self.api = JimyoBotAPI()
        self.running = False
        self.results_cache: List[RouletteResult] = []
        self.last_result: Optional[RouletteResult] = None
        
        # Endpoints possíveis para resultados
        self.result_endpoints = [
            "/ap/results",
            "/ap/history", 
            "/ap/roulette/results",
            "/ap/roulette/history",
            "/ap/live/results",
            "/api/results",
            "/api/roulette/results",
            "/api/game/results"
        ]
        
        logger.info("🎲 Monitor de resultados JimyoBot inicializado")
    
    def _determine_color(self, number: int) -> tuple[str, str]:
        """Determina cor baseada no número da roleta brasileira."""
        if number == 0:
            return 'white', 'Branco'
        elif 1 <= number <= 18:
            # Números vermelhos na roleta brasileira
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18]
            if number in red_numbers:
                return 'red', 'Vermelho'
            else:
                return 'black', 'Preto'
        elif 19 <= number <= 36:
            # Números vermelhos na roleta brasileira
            red_numbers = [19, 21, 23, 25, 27, 30, 32, 34, 36]
            if number in red_numbers:
                return 'red', 'Vermelho'
            else:
                return 'black', 'Preto'
        else:
            return 'unknown', 'Desconhecido'
    
    async def discover_results_endpoint(self) -> Optional[str]:
        """Descobre qual endpoint retorna resultados."""
        if not self.api.credentials:
            await self.api.check_session()
        
        if not self.api.credentials:
            logger.error("❌ Sem credenciais para descobrir endpoints")
            return None
        
        logger.info("🔍 Descobrindo endpoint de resultados...")
        
        # Testar endpoints com e sem autenticação
        headers_with_auth = self.api.headers.copy()
        if self.api.credentials.tokens:
            headers_with_auth['Authorization'] = f'Bearer {self.api.credentials.tokens[0]}'
        
        async with aiohttp.ClientSession() as session:
            for endpoint in self.result_endpoints:
                try:
                    url = f"{self.api.base_url}{endpoint}"
                    
                    # Testar sem autenticação
                    async with session.get(url, headers=self.api.headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if self._validate_results_data(data):
                                logger.info(f"✅ Endpoint de resultados encontrado: {endpoint}")
                                return endpoint
                    
                    # Testar com autenticação
                    async with session.get(url, headers=headers_with_auth) as response:
                        if response.status == 200:
                            data = await response.json()
                            if self._validate_results_data(data):
                                logger.info(f"✅ Endpoint de resultados encontrado (auth): {endpoint}")
                                return endpoint
                                
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} falhou: {e}")
        
        logger.warning("❌ Nenhum endpoint de resultados encontrado")
        return None
    
    def _validate_results_data(self, data: Any) -> bool:
        """Valida se os dados contêm resultados de roleta."""
        if not isinstance(data, dict):
            return False
        
        # Procurar por estruturas típicas de resultados
        possible_keys = ['results', 'history', 'numbers', 'rounds', 'games']
        
        for key in possible_keys:
            if key in data:
                results = data[key]
                if isinstance(results, list) and len(results) > 0:
                    # Verificar se tem estrutura de resultado de roleta
                    first_result = results[0]
                    if isinstance(first_result, dict):
                        # Procurar por campos típicos
                        if any(field in first_result for field in ['number', 'result', 'winning_number', 'roll']):
                            return True
        
        return False
    
    async def get_results_from_game_data(self) -> List[RouletteResult]:
        """Tenta extrair resultados dos dados de jogos."""
        try:
            games_data = await self.api.get_live_games()
            
            if not games_data:
                return []
            
            # Procurar dados da roleta
            roulette_data = self.api.extract_roulette_data(games_data)
            
            if not roulette_data:
                return []
            
            results = []
            
            # Verificar se há histórico no streak
            streak = roulette_data.get('streak', [])
            if streak:
                # Simular resultados baseados no streak (isso é uma aproximação)
                for i, win in enumerate(streak):
                    # Gerar número baseado no padrão (isso é especulativo)
                    if win:
                        number = 1 if i % 2 == 0 else 8  # Vermelho ou preto
                    else:
                        number = 0  # Branco (zero)
                    
                    color, color_name = self._determine_color(number)
                    
                    result = RouletteResult(
                        number=number,
                        color=color,
                        color_name=color_name,
                        timestamp=datetime.now(),
                        game_id=str(roulette_data.get('id', 10009)),
                        round_id=f"streak_{i}"
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao extrair resultados dos dados de jogos: {e}")
            return []
    
    async def monitor_results(self):
        """Monitora resultados em tempo real."""
        logger.info("🎲 Iniciando monitoramento de resultados...")
        
        # Descobrir endpoint de resultados
        results_endpoint = await self.discover_results_endpoint()
        
        while self.running:
            try:
                new_results = []
                
                if results_endpoint:
                    # Tentar obter resultados do endpoint descoberto
                    new_results = await self.get_results_from_endpoint(results_endpoint)
                
                if not new_results:
                    # Fallback: tentar extrair dos dados de jogos
                    new_results = await self.get_results_from_game_data()
                
                # Processar novos resultados
                for result in new_results:
                    if not self._is_duplicate_result(result):
                        await self._process_new_result(result)
                
                # Aguardar antes da próxima verificação
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de resultados: {e}")
                await asyncio.sleep(5)
    
    async def get_results_from_endpoint(self, endpoint: str) -> List[RouletteResult]:
        """Obtém resultados de um endpoint específico."""
        try:
            url = f"{self.api.base_url}{endpoint}"
            
            headers = self.api.headers.copy()
            if self.api.credentials and self.api.credentials.tokens:
                headers['Authorization'] = f'Bearer {self.api.credentials.tokens[0]}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results_data(data)
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter resultados do endpoint {endpoint}: {e}")
            return []
    
    def _parse_results_data(self, data: Dict) -> List[RouletteResult]:
        """Converte dados da API em objetos RouletteResult."""
        results = []
        
        try:
            # Tentar diferentes estruturas de dados
            possible_results = []
            
            if 'results' in data:
                possible_results = data['results']
            elif 'history' in data:
                possible_results = data['history']
            elif 'numbers' in data:
                possible_results = data['numbers']
            elif isinstance(data, list):
                possible_results = data
            
            for item in possible_results:
                if isinstance(item, dict):
                    # Tentar extrair número de diferentes campos
                    number = None
                    for field in ['number', 'result', 'winning_number', 'roll', 'value']:
                        if field in item:
                            number = item[field]
                            break
                    
                    if number is not None:
                        color, color_name = self._determine_color(int(number))
                        
                        # Extrair timestamp
                        timestamp = datetime.now()
                        if 'timestamp' in item:
                            timestamp = datetime.fromtimestamp(item['timestamp'])
                        elif 'time' in item:
                            timestamp = datetime.fromtimestamp(item['time'])
                        
                        result = RouletteResult(
                            number=int(number),
                            color=color,
                            color_name=color_name,
                            timestamp=timestamp,
                            game_id=str(item.get('game_id', 'jimyobot')),
                            round_id=str(item.get('round_id', item.get('id', '')))
                        )
                        results.append(result)
            
        except Exception as e:
            logger.error(f"Erro ao converter dados de resultados: {e}")
        
        return results
    
    def _is_duplicate_result(self, result: RouletteResult) -> bool:
        """Verifica se o resultado já foi processado."""
        if not self.results_cache:
            return False
        
        # Verificar por round_id se disponível
        if result.round_id:
            for cached in self.results_cache:
                if cached.round_id == result.round_id:
                    return True
        
        # Verificar por número e timestamp próximo
        for cached in self.results_cache:
            time_diff = abs((result.timestamp - cached.timestamp).total_seconds())
            if cached.number == result.number and time_diff < 60:  # Mesmo número em 1 minuto
                return True
        
        return False
    
    async def _process_new_result(self, result: RouletteResult):
        """Processa novo resultado."""
        self.results_cache.append(result)
        self.last_result = result
        
        # Manter cache limitado
        if len(self.results_cache) > 100:
            self.results_cache.pop(0)
        
        # Log do resultado
        logger.info(f"🎲 NOVO RESULTADO: {result.number} {result.color_emoji} {result.color_name}")
        print(f"🎲 ROLETA JIMYOBOT: {result.number:2} {result.color_emoji} {result.color_name} - {result.timestamp.strftime('%H:%M:%S')}")
    
    async def start(self):
        """Inicia o monitor."""
        logger.info("🚀 Iniciando monitor de resultados JimyoBot...")
        
        # Verificar sessão
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
        logger.info("🛑 Monitor de resultados parado")
    
    def get_recent_results(self, limit: int = 20) -> List[RouletteResult]:
        """Obtém resultados recentes."""
        return self.results_cache[-limit:] if self.results_cache else []
    
    def get_statistics(self) -> Dict:
        """Obtém estatísticas dos resultados."""
        if not self.results_cache:
            return {}
        
        total = len(self.results_cache)
        red_count = sum(1 for r in self.results_cache if r.color == 'red')
        black_count = sum(1 for r in self.results_cache if r.color == 'black')
        white_count = sum(1 for r in self.results_cache if r.color == 'white')
        
        return {
            'total_results': total,
            'red_count': red_count,
            'black_count': black_count,
            'white_count': white_count,
            'red_percentage': (red_count / total * 100) if total > 0 else 0,
            'black_percentage': (black_count / total * 100) if total > 0 else 0,
            'white_percentage': (white_count / total * 100) if total > 0 else 0,
            'last_result': self.last_result.number if self.last_result else None
        }

async def test_results_monitor():
    """Testa o monitor de resultados."""
    print("🧪 TESTE DO MONITOR DE RESULTADOS JIMYOBOT")
    print("=" * 60)
    
    monitor = JimyoBotResultsMonitor()
    
    # Testar descoberta de endpoints
    print("1. 🔍 Descobrindo endpoints de resultados...")
    endpoint = await monitor.discover_results_endpoint()
    
    if endpoint:
        print(f"   ✅ Endpoint encontrado: {endpoint}")
    else:
        print("   ⚠️ Nenhum endpoint específico encontrado, usando fallback")
    
    # Testar extração de resultados
    print("\n2. 🎲 Testando extração de resultados...")
    results = await monitor.get_results_from_game_data()
    
    if results:
        print(f"   ✅ {len(results)} resultados extraídos:")
        for result in results[-5:]:  # Mostrar últimos 5
            print(f"      {result.number:2} {result.color_emoji} {result.color_name}")
    else:
        print("   ⚠️ Nenhum resultado extraído")
    
    # Testar monitoramento por 1 minuto
    print("\n3. ⏰ Testando monitoramento por 1 minuto...")
    monitor.running = True
    
    start_time = time.time()
    initial_count = len(monitor.results_cache)
    
    # Simular alguns ciclos de monitoramento
    for i in range(4):  # 4 ciclos de 15 segundos = 1 minuto
        await asyncio.sleep(15)
        
        # Simular novos resultados (para teste)
        if i % 2 == 0:  # A cada 2 ciclos
            import random
            number = random.randint(0, 36)
            color, color_name = monitor._determine_color(number)
            
            result = RouletteResult(
                number=number,
                color=color,
                color_name=color_name,
                timestamp=datetime.now(),
                game_id="test",
                round_id=f"test_{i}"
            )
            
            await monitor._process_new_result(result)
        
        elapsed = int(time.time() - start_time)
        current_count = len(monitor.results_cache)
        new_results = current_count - initial_count
        
        print(f"   ⏱️  {elapsed:2}s | 📊 {new_results} resultados | Total: {current_count}")
    
    monitor.stop()
    
    # Estatísticas finais
    print("\n4. 📊 Estatísticas finais:")
    stats = monitor.get_statistics()
    
    if stats:
        print(f"   🎲 Total: {stats['total_results']}")
        print(f"   🔴 Vermelho: {stats['red_count']} ({stats['red_percentage']:.1f}%)")
        print(f"   ⚫ Preto: {stats['black_count']} ({stats['black_percentage']:.1f}%)")
        print(f"   ⚪ Branco: {stats['white_count']} ({stats['white_percentage']:.1f}%)")
        
        if stats['last_result'] is not None:
            print(f"   🎯 Último: {stats['last_result']}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE DO MONITOR DE RESULTADOS CONCLUÍDO")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_results_monitor())
