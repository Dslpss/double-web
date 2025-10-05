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
    
    def __init__(self, table_id: str = "rwbrzportrwa16rg", jsessionid: Optional[str] = None, base_url: Optional[str] = None):
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
        
        # Se não foi fornecido JSESSIONID, tentar obter do sistema existente
        if not self.jsessionid:
            self._try_get_jsessionid_from_system()
        
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
        
    def _try_get_jsessionid_from_system(self):
        """
        Tenta obter JSESSIONID do sistema existente (roulette_integrator)
        """
        try:
            # Tentar importar do app principal
            import sys
            import os
            
            # Adicionar diretório pai ao path se necessário
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            # Tentar obter do integrador principal
            try:
                from app import roulette_integrator
                if roulette_integrator and hasattr(roulette_integrator, 'jsessionid') and roulette_integrator.jsessionid:
                    self.jsessionid = roulette_integrator.jsessionid
                    logger.info("🔑 JSESSIONID obtido do roulette_integrator existente")
                    return
            except ImportError:
                logger.info("📦 Não foi possível importar roulette_integrator do app")
            
            # Método alternativo: verificar se o ambiente Railway tem JSESSIONID
            railway_jsessionid = os.environ.get('RAILWAY_JSESSIONID') or os.environ.get('PRAGMATIC_JSESSIONID')
            if railway_jsessionid:
                self.jsessionid = railway_jsessionid
                logger.info("🚂 JSESSIONID obtido das variáveis de ambiente Railway")
                return
            
            logger.info("📝 Nenhum JSESSIONID disponível no sistema - usará fallback quando necessário")
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter JSESSIONID do sistema: {e}")
        
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
        
        # Verificar se temos JSESSIONID
        if not self.jsessionid:
            logger.warning("⚠️ JSESSIONID não disponível - isso é normal no Railway")
            return 401, {'error': 'JSESSIONID não fornecido', 'railway_compatible': True}
        
        # Parâmetros da requisição baseados na URL real que funciona
        params = {
            "tableId": self.table_id,
            "numberOfGames": games_count,
            "JSESSIONID": self.jsessionid,
            "ck": int(time.time() * 1000),  # Timestamp em milissegundos
            "game_mode": "lobby_desktop"
        }
        
        # Lista de User-Agents mais variados para Railway
        railway_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        # Headers mais robustos para Railway
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
            'Cache-Control': 'no-cache',
            'Origin': 'https://client.pragmaticplaylive.net',
            'Pragma': 'no-cache',
            'Referer': 'https://client.pragmaticplaylive.net/',
            'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': random.choice(railway_user_agents),
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Detectar se estamos no Railway
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
        
        if is_railway:
            logger.info("🚂 Detectado ambiente Railway - usando configuração otimizada")
            # Headers específicos para Railway
            headers.update({
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive'
            })
        
        # Implementação de retry com exponential backoff
        for attempt in range(max(3, self.max_retries)):  # Pelo menos 3 tentativas
            try:
                # Rotacionar User-Agent a cada tentativa
                headers['User-Agent'] = random.choice(railway_user_agents)
                
                # Log de tentativa
                logger.info(f"🌐 Tentativa {attempt+1}: Solicitando histórico para {games_count} jogos")
                if is_railway:
                    logger.info(f"🚂 Railway: Usando User-Agent {headers['User-Agent'][:50]}...")
                
                # URL da API
                url = f"{self.base_url}{self.history_endpoint}"
                
                # Configurar timeout mais conservador para Railway
                timeout = 30 if is_railway else 20
                
                # Fazer a requisição
                response = requests.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=True  # Manter verificação SSL
                )
                
                # Log do status da resposta
                logger.info(f"📊 Status da API: {response.status_code}")
                
                # Verificar se obteve sucesso
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"✅ Dados obtidos com sucesso ({len(str(data))} chars)")
                        return 200, data
                    except ValueError as e:
                        logger.error(f"❌ Resposta não é JSON válido: {e}")
                        return 500, {'error': 'Resposta inválida da API'}
                
                elif response.status_code == 401:
                    logger.warning("🔐 JSESSIONID inválido ou expirado")
                    return 401, {'error': 'JSESSIONID inválido', 'needs_refresh': True}
                
                elif response.status_code == 403:
                    logger.warning("🚫 Acesso negado - possível bloqueio de IP")
                    if is_railway:
                        logger.warning("🚂 Railway detectado - isso é esperado, usando fallback")
                    return 403, {'error': 'Acesso negado', 'railway_blocked': True}
                
                elif response.status_code == 503:
                    logger.warning("⚠️ Serviço indisponível")
                    return 503, {'error': 'Serviço indisponível'}
                
                else:
                    logger.error(f"❌ Erro HTTP {response.status_code}: {response.text[:200]}")
                    
                    # Se é a última tentativa, retornar erro
                    if attempt == max(3, self.max_retries) - 1:
                        return response.status_code, {'error': f'HTTP {response.status_code}'}
                    
                    # Aguardar antes de tentar novamente
                    wait_time = (2 ** attempt) + random.uniform(0.5, 2.0)  # Jitter
                    logger.info(f"⏳ Aguardando {wait_time:.1f}s antes da próxima tentativa...")
                    time.sleep(wait_time)
                    
            except requests.exceptions.Timeout:
                logger.error(f"⏰ Timeout na tentativa {attempt+1}")
                if attempt == max(3, self.max_retries) - 1:
                    return 408, {'error': 'Timeout na requisição'}
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"🔌 Erro de conexão na tentativa {attempt+1}: {e}")
                if attempt == max(3, self.max_retries) - 1:
                    return 503, {'error': 'Erro de conexão'}
                    
            except Exception as e:
                logger.error(f"💥 Erro inesperado na tentativa {attempt+1}: {e}")
                if attempt == max(3, self.max_retries) - 1:
                    return 500, {'error': str(e)}
            
            # Aguardar entre tentativas (com backoff exponencial)
            if attempt < max(3, self.max_retries) - 1:
                wait_time = (2 ** attempt) + random.uniform(0.5, 2.0)
                time.sleep(wait_time)
                
        # Se chegou aqui, todas as tentativas falharam
        logger.error("❌ Todas as tentativas falharam")
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
        
        # Debug: Imprimir estrutura dos dados recebidos
        logger.info(f"🔍 DEBUG: Tipo dos dados recebidos: {type(history_data)}")
        logger.info(f"🔍 DEBUG: Chaves dos dados: {list(history_data.keys()) if isinstance(history_data, dict) else 'Não é dict'}")
        
        # Tentar diferentes estruturas de dados possíveis
        games_data = None
        
        if isinstance(history_data, dict):
            # Tentar diferentes chaves possíveis
            for key in ['history', 'results', 'data', 'games', 'gameHistory', 'statisticHistory']:
                if key in history_data:
                    games_data = history_data[key]
                    logger.info(f"🔍 DEBUG: Encontrados dados na chave '{key}', tipo: {type(games_data)}")
                    break
            
            # Se não encontrou em chaves específicas, verificar se os dados estão no nível raiz
            if games_data is None:
                # Procurar por qualquer lista nos dados
                for key, value in history_data.items():
                    if isinstance(value, list) and value:
                        games_data = value
                        logger.info(f"🔍 DEBUG: Encontrada lista na chave '{key}' com {len(value)} itens")
                        break
        elif isinstance(history_data, list):
            games_data = history_data
            logger.info(f"🔍 DEBUG: Dados são uma lista com {len(games_data)} itens")
        
        if not games_data:
            logger.warning("❌ Nenhum dado de jogos encontrado na resposta")
            logger.info(f"🔍 DEBUG: Dados completos recebidos: {str(history_data)[:500]}...")
            return []
        
        # Processar cada item
        for i, item in enumerate(games_data[:5]):  # Apenas os primeiros 5 para debug
            logger.info(f"🔍 DEBUG: Item {i}: {item}")
            
        try:
            # Processa cada item do histórico
            for item in games_data:
                result_data = self._process_single_game_item(item)
                if result_data:
                    results.append(result_data)
            
            # Log do total de resultados processados
            logger.info(f"✅ Processados {len(results)} resultados de jogos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar histórico: {e}")
            return []
        
        return results
    
    def _process_single_game_item(self, item) -> Optional[Dict]:
        """
        Processa um único item de jogo da API
        """
        if not isinstance(item, dict):
            return None
            
        # Tentar extrair número e cor de diferentes campos possíveis
        number = None
        color = None
        timestamp = None
        
        # Primeiro, tentar o campo gameResult que contém "31 Black", "6 Black", etc.
        if 'gameResult' in item:
            result_text = str(item['gameResult'])
            parsed = self._parse_game_result(result_text)
            if parsed and parsed.get('number', -1) != -1:
                number = parsed['number']
                color = parsed['color']
        
        # Se não conseguiu pelo gameResult, tentar outros campos
        if number is None:
            # Campos possíveis para o número
            for field in ['number', 'winningNumber', 'result', 'outcome', 'value', 'ball']:
                if field in item:
                    try:
                        number = int(item[field])
                        break
                    except (ValueError, TypeError):
                        continue
        
        # Campos possíveis para cor
        if color is None:
            for field in ['color', 'colour', 'winningColor']:
                if field in item:
                    color = str(item[field]).lower()
                    break
        
        # Se não tem cor mas tem número, determinar cor
        if number is not None and color is None:
            if number == 0:
                color = 'green'
            elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                color = 'red'
            else:
                color = 'black'
        
        # Campos possíveis para timestamp
        for field in ['timestamp', 'time', 'gameTime', 'created', 'date']:
            if field in item:
                try:
                    timestamp = int(item[field])
                    break
                except (ValueError, TypeError):
                    continue
        
        # Se não conseguiu extrair número, tentar parseador de texto em outros campos
        if number is None:
            for field in ['outcomeText', 'resultText', 'text', 'description']:
                if field in item:
                    parsed = self._parse_game_result(str(item[field]))
                    if parsed and parsed.get('number', -1) != -1:
                        number = parsed['number']
                        color = parsed['color']
                        break
        
        # Se ainda não tem número, retornar None
        if number is None:
            # Log de debug apenas se o item tem gameResult
            if 'gameResult' in item:
                logger.warning(f"⚠️ Não foi possível extrair número do gameResult: '{item.get('gameResult', 'N/A')}'")
            return None
        
        # Criar timestamp se não existir
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        return {
            'number': number,
            'color': color,
            'timestamp': timestamp,
            'table_id': self.table_id,
            'game_id': item.get('gameId', 'unknown')
        }
            
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
            # Em caso de exceção, também gerar dados simulados
            logger.error(f"❌ Erro ao obter dados da API: {e}")
            return self.generate_realistic_data(games_count)
    
    def test_connection(self) -> Dict:
        """
        Testa a conexão com a API
        """
        if not self.jsessionid:
            return {
                'success': False,
                'error': 'JSESSIONID não configurado'
            }
        
        try:
            status_code, data = self.fetch_history(10)  # Teste com 10 jogos
            
            return {
                'success': status_code == 200,
                'status_code': status_code,
                'has_data': bool(data),
                'jsessionid_valid': status_code != 401,
                'message': 'Conexão OK' if status_code == 200 else f'Erro: {status_code}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def set_jsessionid(self, jsessionid: str):
        """Atualiza o JSESSIONID"""
        self.jsessionid = jsessionid