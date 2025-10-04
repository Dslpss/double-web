"""
Melhorias no cliente de estatísticas da Pragmatic Play para aumentar a resiliência no Railway.
Esta versão inclui:
1. Rotação de User-Agents
2. Retry com exponential backoff
3. Configuração de proxies automática
4. Fallback para dados simulados
"""

import logging
import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple
import re
import os

logger = logging.getLogger(__name__)

class PragmaticStatisticsClientEnhanced:
    """
    Cliente aprimorado para acessar as estatísticas de jogos da API da Pragmatic Play.
    Obtém resultados históricos dos jogos com maior resiliência para ambientes de produção.
    """
    
    def __init__(self, table_id: str = "rwbrzportrwa16rg", jsessionid: str = None, base_url: str = None):
        """
        Inicializa o cliente de estatísticas da Pragmatic Play com recursos aprimorados.
        
        Args:
            table_id: ID da mesa de roleta (padrão para Roleta Brasileira)
            jsessionid: Cookie de sessão JSESSIONID
            base_url: URL base da API (opcional, usa o padrão se não fornecido)
        """
        self.table_id = table_id
        self.jsessionid = jsessionid
        self.base_url = base_url or "https://games.pragmaticplaylive.net"
        self.history_endpoint = f"/api/ui/statisticHistory"
        
        # Lista de User-Agents para rotação
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
        ]
        
        # Carregar proxies do ambiente, se disponíveis
        self.http_proxies = os.environ.get('HTTP_PROXIES', '').split(',')
        self.socks_proxies = os.environ.get('SOCKS_PROXIES', '').split(',')
        self.http_proxies = [p for p in self.http_proxies if p.strip()]
        self.socks_proxies = [p for p in self.socks_proxies if p.strip()]
        
        # Configurações de retry
        self.max_retries = 5
        self.retry_delay = 1  # Segundos iniciais, aumentará exponencialmente
        
        logger.info(f"📊 PragmaticStatisticsClientEnhanced inicializado para mesa {table_id}")
        logger.info(f"🔄 Proxies HTTP disponíveis: {len(self.http_proxies)}")
        logger.info(f"🔄 Proxies SOCKS disponíveis: {len(self.socks_proxies)}")
        
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
        pattern = r'(\d+)\s+(Black|Red|Green)'
        match = re.search(pattern, result_str, re.IGNORECASE)
        
        if match:
            number = int(match.group(1))
            color = match.group(2).lower()
            
            # Verificar número zero (green)
            if number == 0:
                color = 'green'
                
            return {
                'number': number,
                'color': color
            }
        else:
            # Fallback: tentar extrair apenas o número
            number_match = re.search(r'(\d+)', result_str)
            if number_match:
                number = int(number_match.group(1))
                # Determinar cor baseado no número
                if number == 0:
                    color = 'green'
                elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                    color = 'red'
                else:
                    color = 'black'
                
                return {
                    'number': number,
                    'color': color
                }
        
        # Se não conseguir extrair, retorna None
        return {
            'number': -1,
            'color': 'unknown',
            'raw': result_str
        }
        
    def _get_random_user_agent(self):
        """Retorna um User-Agent aleatório da lista."""
        return random.choice(self.user_agents)
        
    def _get_random_proxy(self):
        """Retorna um proxy aleatório, priorizando HTTP."""
        if self.http_proxies:
            return {'http': random.choice(self.http_proxies), 'https': random.choice(self.http_proxies)}
        elif self.socks_proxies:
            proxy = random.choice(self.socks_proxies)
            return {'http': proxy, 'https': proxy}
        return None
    
    def fetch_history(self, games_count: int = 100, use_proxy: bool = True) -> Tuple[int, Dict]:
        """
        Busca o histórico de jogos da API com retry e rotação de User-Agent.
        
        Args:
            games_count: Número de jogos a obter (máx. 500)
            use_proxy: Se deve usar proxy para esta requisição
            
        Returns:
            Tuple[int, Dict]: Status HTTP e dados da resposta
        """
        # Limitar número de jogos entre 10 e 500
        games_count = min(500, max(10, games_count))
        
        # Parâmetros da requisição
        params = {
            "tableid": self.table_id,
            "gamesCount": games_count
        }
        
        # Headers básicos
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://games.pragmaticplaylive.net/br/app/ui/client",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # Cookies para autenticação
        cookies = {
            "JSESSIONID": self.jsessionid
        }
        
        # Implementação de retry com exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Selecionar proxy se habilitado
                proxies = self._get_random_proxy() if use_proxy and (self.http_proxies or self.socks_proxies) else None
                
                # Log de tentativa
                logger.info(f"🌐 Tentativa {attempt+1}/{self.max_retries}: Solicitando histórico para {games_count} jogos na roleta {self.table_id}")
                if proxies:
                    logger.info(f"🔄 Usando proxy: {list(proxies.values())[0]}")
                
                # Renovar User-Agent a cada tentativa
                headers["User-Agent"] = self._get_random_user_agent()
                
                # Faz a requisição para a API
                url = f"{self.base_url}{self.history_endpoint}"
                
                response = requests.get(
                    url, 
                    params=params, 
                    headers=headers, 
                    cookies=cookies,
                    proxies=proxies,
                    timeout=20
                )
                
                # Log do status da resposta
                logger.info(f"📊 Status da API de estatísticas: {response.status_code}")
                
                # Retorna o código de status e os dados JSON se bem-sucedido
                if response.status_code == 200:
                    return response.status_code, response.json()
                    
                # Se houve erro mas já é a última tentativa, retorna o erro
                elif attempt == self.max_retries - 1:
                    logger.error(f"❌ Erro final ao obter histórico: {response.status_code} - {response.text[:200]}")
                    return response.status_code, {"error": f"Erro {response.status_code}", "response": response.text[:500]}
                    
                # Caso contrário, aguarda e tenta novamente
                wait_time = self.retry_delay * (2 ** attempt)  # Backoff exponencial
                logger.warning(f"⚠️ Tentativa {attempt+1} falhou com status {response.status_code}. Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
                    
            except Exception as e:
                # Se é a última tentativa, retorna o erro
                if attempt == self.max_retries - 1:
                    logger.error(f"❌ Exceção final ao solicitar histórico: {str(e)}")
                    return 500, {"error": str(e)}
                
                # Caso contrário, aguarda e tenta novamente
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"⚠️ Exceção na tentativa {attempt+1}: {str(e)}. Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
                
        # Se chegou aqui, todas as tentativas falharam
        return 500, {"error": "Todas as tentativas falharam"}
    
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
            for item in history_data["history"]:
                # Extrair dados básicos
                result_text = item.get("outcomeText", "")
                timestamp = item.get("timestamp", 0)
                dealer_name = item.get("dealerName", "")
                
                # Processar o texto do resultado para extrair número e cor
                result_data = self._parse_game_result(result_text)
                
                # Adicionar informações de timestamp e dealer
                if timestamp:
                    # Converter timestamp para formato ISO
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    result_data["timestamp"] = timestamp
                    result_data["datetime"] = dt.isoformat()
                
                if dealer_name:
                    result_data["dealer"] = dealer_name
                
                # Adicionar resultado à lista
                results.append(result_data)
            
            # Log do total de resultados processados
            logger.info(f"✅ Processados {len(results)} resultados de jogos")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar histórico: {str(e)}")
            return []
            
    def generate_realistic_data(self, count: int = 100) -> List[Dict]:
        """
        Gera dados realistas de roleta para casos onde a API falha.
        
        Args:
            count: Número de resultados a gerar
            
        Returns:
            List[Dict]: Lista de resultados simulados
        """
        results = []
        
        # Definir números da roleta e suas cores
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        # Probabilidade de zero (green) é menor em dados realistas
        all_numbers = red_numbers + black_numbers + [0]  # Adiciona zero com menor probabilidade
        
        # Gerar timestamp base (5 minutos atrás)
        base_timestamp = int(time.time()) - (5 * 60)
        
        # Gerar resultados com intervalo de tempo realista entre spins
        for i in range(count):
            # Selecionar número aleatório
            number = random.choice(all_numbers)
            
            # Determinar cor
            if number == 0:
                color = "green"
            elif number in red_numbers:
                color = "red"
            else:
                color = "black"
            
            # Calcular timestamp (30-40 segundos entre spins)
            spin_timestamp = base_timestamp + (i * random.randint(30, 40))
            dt = datetime.fromtimestamp(spin_timestamp)
            
            # Criar resultado
            result = {
                "number": number,
                "color": color,
                "timestamp": spin_timestamp * 1000,  # API usa milissegundos
                "datetime": dt.isoformat(),
                "simulated": True  # Marca que é um resultado simulado
            }
            
            results.append(result)
        
        logger.info(f"✅ Gerados {len(results)} resultados simulados realistas")
        return results
        
    def get_history(self, games_count: int = 100) -> List[Dict]:
        """
        Método de alto nível para obter o histórico de jogos com fallback para dados simulados.
        
        Args:
            games_count: Número de jogos a obter
            
        Returns:
            List[Dict]: Lista de resultados processados ou simulados
        """
        if not self.jsessionid:
            logger.warning("⚠️ JSESSIONID não definido, gerando dados simulados")
            return self.generate_realistic_data(games_count)
        
        try:
            # Tentar obter dados reais da API
            status_code, response_data = self.fetch_history(games_count=games_count)
            
            # Se obteve com sucesso, processar os dados
            if status_code == 200 and response_data and "history" in response_data:
                results = self.process_history(response_data)
                if results:
                    logger.info(f"✅ Obtidos {len(results)} resultados reais da API")
                    return results
            
            # Se chegou aqui, não conseguiu obter dados reais
            logger.warning(f"⚠️ Não foi possível obter dados reais da API (status {status_code}), gerando dados simulados")
            return self.generate_realistic_data(games_count)
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter histórico: {str(e)}")
            return self.generate_realistic_data(games_count)