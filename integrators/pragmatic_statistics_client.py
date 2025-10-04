import logging
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple
import re

logger = logging.getLogger(__name__)

class PragmaticStatisticsClient:
    """
    Cliente para acessar as estatísticas de jogos da API da Pragmatic Play.
    Obtém resultados históricos dos jogos.
    """
    
    def __init__(self, table_id: str = "rwbrzportrwa16rg", jsessionid: str = None, base_url: str = None):
        """
        Inicializa o cliente de estatísticas da Pragmatic Play.
        
        Args:
            table_id: ID da mesa de roleta (padrão para Roleta Brasileira)
            jsessionid: Cookie de sessão JSESSIONID
            base_url: URL base da API (opcional, usa o padrão se não fornecido)
        """
        self.table_id = table_id
        self.jsessionid = jsessionid
        self.base_url = base_url or "https://games.pragmaticplaylive.net"
        self.history_endpoint = f"/api/ui/statisticHistory"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/143.0"
        
    def set_jsessionid(self, jsessionid: str):
        """
        Define o JSESSIONID para autenticação.
        
        Args:
            jsessionid: Cookie de sessão JSESSIONID
        """
        self.jsessionid = jsessionid
        logger.info("🔑 JSESSIONID definido para o cliente de estatísticas")
    
    def _parse_game_result(self, result_str: str) -> Dict:
        """
        Processa uma string de resultado da roleta (ex: "26 Black") para extrair número e cor.
        
        Args:
            result_str: String do resultado (ex: "26 Black", "0  Green")
            
        Returns:
            Dict com número e cor
        """
        # Padrão para extrair número e cor
        pattern = r'(\d+)\s+(\w+)'
        # Caso especial para zero
        if "0  Green" in result_str:
            return {"number": 0, "color": "green"}
            
        match = re.search(pattern, result_str)
        if match:
            number = int(match.group(1))
            color = match.group(2).lower()
            return {"number": number, "color": color}
        else:
            logger.warning(f"❌ Não foi possível processar o resultado: {result_str}")
            return {"number": None, "color": None}
    
    def fetch_history(self, games_count: int = 100) -> Tuple[int, Dict]:
        """
        Obtém o histórico de resultados da roleta.
        
        Args:
            games_count: Quantidade de jogos para obter (máx 500)
            
        Returns:
            Tuple[int, Dict]: (status_code, dados de resposta)
        """
        if not self.jsessionid:
            logger.error("❌ JSESSIONID não definido para o cliente de estatísticas")
            return 401, {"error": "JSESSIONID não definido"}
            
        # Limitar a quantidade máxima de jogos
        games_count = min(games_count, 500)
        
        # Parâmetros da requisição
        params = {
            "tableId": self.table_id,
            "numberOfGames": games_count,
            "JSESSIONID": self.jsessionid,
            "ck": int(datetime.now().timestamp() * 1000),  # Timestamp atual em ms
            "game_mode": "lobby_desktop"
        }
        
        # Headers da requisição
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://client.pragmaticplaylive.net/",
            "Origin": "https://client.pragmaticplaylive.net"
        }
        
        # Cookies para autenticação
        cookies = {
            "JSESSIONID": self.jsessionid
        }
        
        try:
            # Faz a requisição para a API
            url = f"{self.base_url}{self.history_endpoint}"
            logger.info(f"🌐 Solicitando histórico para {games_count} jogos na roleta {self.table_id}")
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                cookies=cookies,
                timeout=15
            )
            
            # Log do status da resposta
            logger.info(f"📊 Status da API de estatísticas: {response.status_code}")
            
            # Retorna o código de status e os dados JSON
            if response.status_code == 200:
                return response.status_code, response.json()
            else:
                logger.error(f"❌ Erro ao obter histórico: {response.status_code} - {response.text[:200]}")
                return response.status_code, {"error": f"Erro {response.status_code}", "response": response.text[:500]}
                
        except Exception as e:
            logger.error(f"❌ Exceção ao solicitar histórico: {str(e)}")
            return 500, {"error": str(e)}
    
    def process_history(self, history_data: Dict) -> List[Dict]:
        """
        Processa os dados brutos do histórico em um formato padronizado.
        
        Args:
            history_data: Dados brutos do histórico da API
            
        Returns:
            List[Dict]: Lista de resultados processados
        """
        results = []
        
        # Verifica se o histórico está presente
        if "history" not in history_data:
            logger.error("❌ Dados de histórico não encontrados na resposta")
            return []
        
        try:
            # Processa cada item do histórico
            for game in history_data["history"]:
                # Extrair número e cor
                result_info = self._parse_game_result(game.get("gameResult", ""))
                
                # Criar entrada formatada
                result_entry = {
                    "id": game.get("gameId"),
                    "number": result_info["number"],
                    "color": result_info["color"],
                    "time": datetime.now().strftime('%H:%M:%S'),  # Timestamp atual (a API não fornece timestamps)
                    "raw_result": game.get("gameResult", ""),
                    "game_type": game.get("gameType", "")
                }
                
                results.append(result_entry)
            
            logger.info(f"✅ Processados {len(results)} resultados do histórico")
            return results
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar histórico: {str(e)}")
            return []
    
    def get_latest_results(self, count: int = 100) -> List[Dict]:
        """
        Obtém e processa os resultados mais recentes da roleta.
        
        Args:
            count: Quantidade de resultados para obter
            
        Returns:
            List[Dict]: Lista de resultados formatados
        """
        # Obtém os dados brutos
        status_code, history_data = self.fetch_history(count)
        
        # Verifica se a solicitação foi bem-sucedida
        if status_code != 200:
            logger.error(f"❌ Não foi possível obter resultados recentes (status {status_code})")
            return []
        
        # Processa os resultados
        return self.process_history(history_data)