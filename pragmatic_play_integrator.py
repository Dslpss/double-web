#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador da API da Pragmatic Play Live Roulette
Busca resultados históricos da roleta em tempo real
"""

import requests
import time
import re
from datetime import datetime
from typing import Dict, List, Optional

class PragmaticPlayIntegrator:
    """Integrador para API da Pragmatic Play Live Roulette."""
    
    def __init__(self, table_id: str = "rwbrzportrwa16rg", session_id: Optional[str] = None):
        """
        Inicializa o integrador.
        
        Args:
            table_id: ID da mesa de roleta
            session_id: JSESSIONID para autenticação (opcional)
        """
        self.table_id = table_id
        self.session_id = session_id or "6Dyk5pcHZ940gAb7TIUV2F_fHQ06A9wOcRC1-JD-Qu8e95yDHxiQ!1928883527-df6535db"
        self.base_url = "https://games.pragmaticplaylive.net"
        self.last_game_id = None
        self.results = []
        
    def _parse_game_result(self, result_str: str) -> Dict:
        """
        Parseia o resultado do jogo no formato "30 Red" ou "0 Green".
        
        Args:
            result_str: String do resultado (ex: "30 Red", "20 Black", "0  Green")
            
        Returns:
            Dict com número e cor
        """
        # Remover espaços extras e fazer split
        parts = result_str.strip().split()
        
        if len(parts) >= 2:
            number = int(parts[0])
            color = parts[1].lower()
            
            return {
                'number': number,
                'color': color,
                'original': result_str
            }
        
        return {
            'number': 0,
            'color': 'unknown',
            'original': result_str
        }
    
    def fetch_history(self, number_of_games: int = 500) -> List[Dict]:
        """
        Busca histórico de resultados da roleta.
        
        Args:
            number_of_games: Número de jogos para buscar (máx 500)
            
        Returns:
            Lista de resultados
        """
        try:
            # Construir URL com parâmetros
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/ui/statisticHistory"
            
            params = {
                'tableId': self.table_id,
                'numberOfGames': min(number_of_games, 500),
                'JSESSIONID': self.session_id,
                'ck': timestamp,
                'game_mode': 'lobby_desktop'
            }
            
            # Headers da requisição
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://client.pragmaticplaylive.net',
                'Referer': 'https://client.pragmaticplaylive.net/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site'
            }
            
            # Fazer requisição
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar se houve erro
            if data.get('errorCode') != '0':
                print(f"❌ Erro na API: {data.get('description')}")
                return []
            
            # Processar histórico
            history = data.get('history', [])
            results = []
            
            for game in history:
                game_result = self._parse_game_result(game.get('gameResult', ''))
                
                result = {
                    'game_id': game.get('gameId'),
                    'number': game_result['number'],
                    'color': game_result['color'],
                    'game_type': game.get('gameType'),
                    'bet_count': game.get('betCount', 0),
                    'player_count': game.get('playerCount', 0),
                    'player_win_count': game.get('playerWinCount', 0),
                    'power_up_threshold_reached': game.get('powerUpThresholdReached', False),
                    'fortune_roulette': game.get('fortuneRoulette', False),
                    'power_up_roulette': game.get('powerUpRoulette', False),
                    'mega_roulette': game.get('megaRoulette', False),
                    'timestamp': int(time.time()),
                    'source': 'pragmatic_play_api'
                }
                
                results.append(result)
            
            self.results = results
            
            # Atualizar último game_id
            if results:
                self.last_game_id = results[0]['game_id']
            
            print(f"✅ Buscados {len(results)} resultados da Pragmatic Play")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return []
        except Exception as e:
            print(f"❌ Erro ao processar resultados: {e}")
            return []
    
    def get_latest_results(self, count: int = 20) -> List[Dict]:
        """
        Retorna os últimos N resultados.
        
        Args:
            count: Número de resultados para retornar
            
        Returns:
            Lista de resultados mais recentes
        """
        if not self.results:
            self.fetch_history()
        
        return self.results[:count]
    
    def get_new_results(self) -> List[Dict]:
        """
        Busca apenas resultados novos desde a última verificação.
        
        Returns:
            Lista de novos resultados
        """
        new_results = self.fetch_history(50)  # Buscar últimos 50
        
        if not self.last_game_id:
            return new_results
        
        # Filtrar apenas resultados novos
        filtered = []
        for result in new_results:
            if result['game_id'] == self.last_game_id:
                break
            filtered.append(result)
        
        return filtered
    
    def get_statistics(self) -> Dict:
        """
        Calcula estatísticas dos resultados.
        
        Returns:
            Dict com estatísticas
        """
        if not self.results:
            return {}
        
        total = len(self.results)
        reds = sum(1 for r in self.results if r['color'] == 'red')
        blacks = sum(1 for r in self.results if r['color'] == 'black')
        greens = sum(1 for r in self.results if r['color'] == 'green')
        
        return {
            'total_games': total,
            'red_count': reds,
            'black_count': blacks,
            'green_count': greens,
            'red_percentage': round(reds / total * 100, 2) if total > 0 else 0,
            'black_percentage': round(blacks / total * 100, 2) if total > 0 else 0,
            'green_percentage': round(greens / total * 100, 2) if total > 0 else 0,
            'last_game_id': self.last_game_id
        }
    
    def format_for_analyzer(self, results: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Formata resultados para o formato esperado pelo analyzer.
        
        Args:
            results: Lista de resultados (usa self.results se None)
            
        Returns:
            Lista formatada para o analyzer
        """
        if results is None:
            results = self.results
        
        formatted = []
        for result in results:
            formatted.append({
                'id': result['game_id'],
                'roll': result['number'],
                'number': result['number'],
                'color': result['color'],
                'timestamp': result['timestamp']
            })
        
        return formatted


# Exemplo de uso
if __name__ == "__main__":
    print("🎰 Testando Integrador Pragmatic Play\n")
    
    # Criar integrador
    integrator = PragmaticPlayIntegrator()
    
    # Buscar histórico
    print("📥 Buscando histórico de resultados...")
    results = integrator.fetch_history(50)
    
    if results:
        print(f"\n✅ {len(results)} resultados obtidos!\n")
        
        # Mostrar últimos 10 resultados
        print("📊 Últimos 10 resultados:")
        for i, result in enumerate(results[:10], 1):
            print(f"  {i}. Jogo {result['game_id']}: {result['number']} ({result['color'].upper()})")
        
        # Estatísticas
        print("\n📈 Estatísticas:")
        stats = integrator.get_statistics()
        print(f"  Total de jogos: {stats['total_games']}")
        print(f"  Vermelho: {stats['red_count']} ({stats['red_percentage']}%)")
        print(f"  Preto: {stats['black_count']} ({stats['black_percentage']}%)")
        print(f"  Verde: {stats['green_count']} ({stats['green_percentage']}%)")
        
        # Formato para analyzer
        print("\n🔄 Formato para Analyzer (primeiros 5):")
        formatted = integrator.format_for_analyzer(results[:5])
        for item in formatted:
            print(f"  {item}")
    else:
        print("❌ Nenhum resultado obtido")
