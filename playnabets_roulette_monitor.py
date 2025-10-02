#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitor da Roleta PlayNaBets
Usa a API central.playnabet.com com token JWT válido
"""

import asyncio
import aiohttp
import json
import time
import sqlite3
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RouletteResult:
    """Resultado da roleta PlayNaBets."""
    game_id: str
    number: int
    color: str
    color_name: str
    timestamp: datetime
    source: str = "playnabets_api"
    
    def to_dict(self) -> Dict:
        return {
            'game_id': self.game_id,
            'number': self.number,
            'color': self.color,
            'color_name': self.color_name,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

class PlayNaBetsRouletteDatabase:
    """Banco de dados para resultados da roleta PlayNaBets."""
    
    def __init__(self, db_path: str = "playnabets_roulette.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT UNIQUE NOT NULL,
                number INTEGER NOT NULL,
                color TEXT NOT NULL,
                color_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados da Roleta PlayNaBets inicializado")
    
    def save_result(self, result: RouletteResult) -> bool:
        """Salva um resultado no banco (evita duplicatas)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO roulette_results 
                (game_id, number, color, color_name, timestamp, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result.game_id,
                result.number,
                result.color,
                result.color_name,
                result.timestamp.isoformat(),
                result.source
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro ao salvar resultado: {e}")
            return False
        finally:
            conn.close()
    
    def get_recent_results(self, limit: int = 50) -> List[RouletteResult]:
        """Obtém resultados recentes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT game_id, number, color, color_name, timestamp, source
            FROM roulette_results
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(RouletteResult(
                game_id=row[0],
                number=row[1],
                color=row[2],
                color_name=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                source=row[5]
            ))
        
        conn.close()
        return results
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Obtém estatísticas dos últimos X horas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT number, color_name, COUNT(*) as count
            FROM roulette_results
            WHERE datetime(timestamp) >= ?
            GROUP BY number, color_name
            ORDER BY count DESC
        ''', (since.isoformat(),))
        
        number_stats = {}
        color_stats = {'RED': 0, 'BLACK': 0, 'GREEN': 0}
        
        for row in cursor.fetchall():
            number, color_name, count = row
            number_stats[number] = count
            color_stats[color_name] = color_stats.get(color_name, 0) + count
        
        conn.close()
        
        return {
            'number_frequency': number_stats,
            'color_frequency': color_stats,
            'total_games': sum(color_stats.values()),
            'period_hours': hours
        }

class PlayNaBetsRouletteMonitor:
    """Monitor da API PlayNaBets para roleta."""
    
    def __init__(self):
        self.base_url = "https://central.playnabet.com"
        self.user_id = "63314"
        self.running = False
        self.monitor_thread = None
        
        # JWT Token válido
        self.jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTkzNzE2NzMsImV4cCI6MTc1OTk3NjQ3MywidXNlciI6eyJpZCI6NjMzMTR9fQ.mc98Vco9SO3NLY2bur9aeUzPluiC_6Mu8NMUfiq4McA"
        
        # Componentes
        self.database = PlayNaBetsRouletteDatabase()
        self.results_cache = []
        self.last_check_time = None
        
        # Headers para a API
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://playnabets.com',
            'Referer': 'https://playnabets.com/',
            'Authorization': f'Bearer {self.jwt_token}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Te': 'trailers'
        }
        
        logger.info("Monitor da API PlayNaBets inicializado")
    
    async def test_api_endpoints(self):
        """Testa diferentes endpoints da API PlayNaBets."""
        endpoints_to_test = [
            f"/api/clientes/getCliente/{self.user_id}",
            "/api/jogos/historico",
            "/api/jogos/roleta/historico", 
            "/api/jogos/resultados",
            "/api/casino/jogos",
            "/api/casino/historico",
            "/api/live/jogos",
            "/api/live/resultados",
            "/api/pragmatic/roleta",
            "/api/pragmatic/historico",
            "/api/games/roulette/history",
            "/api/games/history",
            "/api/roulette/results",
            "/api/results"
        ]
        
        working_endpoints = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints_to_test:
                url = f"{self.base_url}{endpoint}"
                print(f"🔍 Testando: {endpoint}")
                
                try:
                    async with session.get(url, headers=self.headers) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"   ✅ JSON: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                                working_endpoints.append((endpoint, data))
                            except:
                                text = await response.text()
                                print(f"   ✅ Text: {text[:100]}...")
                                working_endpoints.append((endpoint, text))
                        elif response.status == 401:
                            print(f"   🔑 Não autorizado")
                        elif response.status == 404:
                            print(f"   ❌ Não encontrado")
                        else:
                            print(f"   ⚠️ Status: {response.status}")
                            
                except Exception as e:
                    print(f"   💥 Erro: {e}")
        
        return working_endpoints
    
    async def fetch_user_data(self):
        """Busca dados do usuário para verificar se a API funciona."""
        url = f"{self.base_url}/api/clientes/getCliente/{self.user_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Dados do usuário obtidos: {data.get('nome', 'N/A')}")
                        return data
                    else:
                        logger.error(f"Erro ao buscar dados do usuário: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erro ao buscar dados do usuário: {e}")
        
        return None
    
    def simulate_roulette_results(self, count: int = 5) -> List[RouletteResult]:
        """Simula resultados da roleta para teste."""
        import random
        
        results = []
        for i in range(count):
            # Gerar número aleatório (0-36 para roleta europeia)
            number = random.randint(0, 36)
            
            # Determinar cor
            if number == 0:
                color, color_name = '🟢', 'GREEN'
            elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                color, color_name = '🔴', 'RED'
            else:
                color, color_name = '⚫', 'BLACK'
            
            result = RouletteResult(
                game_id=f"sim_{int(time.time())}_{i}",
                number=number,
                color=color,
                color_name=color_name,
                timestamp=datetime.now(),
                source="playnabets_simulado"
            )
            
            results.append(result)
            
            # Salvar no banco
            if self.database.save_result(result):
                logger.info(f"🎲 SIMULADO: {number} {color} {color_name}")
        
        return results
    
    async def monitor_loop(self):
        """Loop principal de monitoramento."""
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                print(f"🔍 Verificação #{check_count} - {timestamp}")
                
                # Testar acesso aos dados do usuário
                user_data = await self.fetch_user_data()
                
                if user_data:
                    print("✅ API PlayNaBets acessível")
                    
                    # Por enquanto, simular resultados até encontrarmos o endpoint correto
                    if check_count % 3 == 0:  # A cada 3 verificações (90 segundos)
                        simulated = self.simulate_roulette_results(1)
                        self.results_cache.extend(simulated)
                        
                        # Manter cache limitado
                        if len(self.results_cache) > 100:
                            self.results_cache = self.results_cache[-100:]
                else:
                    print("❌ Erro ao acessar API PlayNaBets")
                
                # Aguardar 30 segundos
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(10)
    
    def start(self):
        """Inicia o monitor em thread separada."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._run_monitor, daemon=True)
            self.monitor_thread.start()
            logger.info("🚀 Monitor PlayNaBets iniciado")
            return True
        return False
    
    def stop(self):
        """Para o monitor."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("🛑 Monitor PlayNaBets parado")
            return True
        return False
    
    def _run_monitor(self):
        """Executa o loop de monitoramento em thread separada."""
        asyncio.run(self.monitor_loop())
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados completos para o dashboard."""
        try:
            recent_results = self.database.get_recent_results(20)
            statistics = self.database.get_statistics(24)
            
            return {
                'recent_results': [r.to_dict() for r in recent_results],
                'statistics': statistics,
                'status': {
                    'running': self.running,
                    'api_url': self.base_url,
                    'user_id': self.user_id,
                    'cache_size': len(self.results_cache)
                },
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard: {e}")
            return {
                'recent_results': [],
                'statistics': {},
                'status': {'running': False, 'error': str(e)},
                'last_update': datetime.now().isoformat()
            }

async def test_playnabets_api():
    """Testa a API PlayNaBets."""
    print("🧪 TESTANDO API PLAYNABETS")
    print("=" * 50)
    
    monitor = PlayNaBetsRouletteMonitor()
    
    print("1. Testando dados do usuário...")
    user_data = await monitor.fetch_user_data()
    
    if user_data:
        print(f"✅ Usuário: {user_data.get('nome', 'N/A')}")
        print(f"📧 Email: {user_data.get('email', 'N/A')}")
    
    print("\n2. Testando endpoints da API...")
    working_endpoints = await monitor.test_api_endpoints()
    
    if working_endpoints:
        print(f"\n✅ {len(working_endpoints)} endpoints funcionando:")
        for endpoint, data in working_endpoints:
            print(f"   {endpoint}")
    else:
        print("\n❌ Nenhum endpoint de jogos encontrado")
    
    print("\n3. Testando sistema de simulação...")
    simulated = monitor.simulate_roulette_results(3)
    print(f"✅ {len(simulated)} resultados simulados criados")
    
    print("\n4. Dados do dashboard:")
    dashboard_data = monitor.get_dashboard_data()
    stats = dashboard_data.get('statistics', {})
    print(f"   Total: {stats.get('total_games', 0)} jogos")
    print(f"   Cores: {stats.get('color_frequency', {})}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_playnabets_api())
