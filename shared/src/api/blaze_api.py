#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para interação com a API da Blaze.
"""

import os
import requests
import logging
import time
import json
import asyncio
import ssl
import websockets
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class BlazeAPI:
    """Classe para interação com a API da Blaze."""
    
    def __init__(self, config):
        """
        Inicializa a classe BlazeAPI.
        
        Args:
            config (dict): Configurações da API
        """
        self.base_url = config.get('base_url', 'https://blaze.com/api/roulette_games/recent')
        self.timeout = config.get('timeout', 10)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.headers = {
            'User-Agent': config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        }
        self.session = requests.Session()
        
    def get_recent_results(self, limit=100):
        """
        Obtém os resultados recentes do Double da Blaze.
        
        Args:
            limit (int): Número de resultados a serem obtidos
            
        Returns:
            list: Lista com os resultados recentes
        """
        url = f"{self.base_url}?page=1&size={limit}"
        return self._make_request(url)
    
    def get_result_by_id(self, result_id):
        """
        Obtém um resultado específico pelo ID.
        
        Args:
            result_id (str): ID do resultado
            
        Returns:
            dict: Dados do resultado
        """
        url = f"{self.base_url.replace('recent', '')}/{result_id}"
        return self._make_request(url)
    
    def _make_request(self, url):
        """
        Faz uma requisição à API com retry em caso de falha.
        
        Args:
            url (str): URL da requisição
            
        Returns:
            dict/list: Dados da resposta
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt+1}/{self.max_retries} falhou: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Falha ao fazer requisição após {self.max_retries} tentativas: {str(e)}")
                    return []
    
    def parse_result(self, result):
        """
        Analisa um resultado e extrai informações relevantes.
        
        Args:
            result (dict): Resultado da API
            
        Returns:
            dict: Dados formatados do resultado
        """
        try:
            roll = result.get('roll')
            color = self._get_color(roll)
            created_at = result.get('created_at')
            
            return {
                'id': result.get('id'),
                'roll': roll,
                'color': color,
                'created_at': created_at,
                'timestamp': self._parse_timestamp(created_at),
                'server_seed': result.get('server_seed'),
                'status': result.get('status')
            }
        except Exception as e:
            logger.error(f"Erro ao analisar resultado: {str(e)}")
            return {}
    
    def _get_color(self, roll):
        """
        Determina a cor com base no número sorteado.
        
        Args:
            roll (int): Número sorteado
            
        Returns:
            str: Cor correspondente (red, black, white)
        """
        if roll == 0:
            return 'white'
        elif 1 <= roll <= 7:
            return 'red'
        elif 8 <= roll <= 14:
            return 'black'
        else:
            return 'unknown'
    
    def _parse_timestamp(self, date_str):
        """
        Converte a string de data para timestamp.
        
        Args:
            date_str (str): String de data
            
        Returns:
            int: Timestamp em segundos
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return int(dt.timestamp())
        except Exception:
            return int(time.time())
    
def renew_access_token(refresh_token):
    url = "https://blaze.bet.br/api/auth/refresh_token"
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Referer": "https://blaze.bet.br/pt/games/double?modal=pay_table&game_mode=double_room_1",
        "Origin": "https://blaze.bet.br",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers"
    }
    data = {
        "props": {
            "refreshToken": refresh_token
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao renovar o token: {response.status_code} - {response.text}")

def get_game_data():
    url = "https://blaze.bet.br/api/games/double"
    # Ler token de acesso de variável de ambiente para evitar expor segredos no código
    access_token = os.getenv("ACCESS_TOKEN")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Referer": "https://blaze.bet.br/pt/games/double?modal=pay_table&game_mode=double_room_1",
        "X-Client-Language": "pt",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers"
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        logger.warning("ACCESS_TOKEN não definido — requisição será feita sem header Authorization")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao obter dados do jogo: {response.status_code} - {response.text}")

async def connect_to_websocket():
    url = "wss://api-gaming.blaze.bet.br/replication/?EIO=3&transport=websocket"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive, Upgrade",
        "Cookie": "_ga_WS0MD548L3=GS2.1.s1759014438$o1$g1$t1759021519$j60$l0$h0; _ga=GA1.1.1163565055.1759014438; AMP_c9c53a1635=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJmY2IzNjg3Ny04Nzc3LTQ0NWMtYTZkMS0yZTYxNGY5YmE1NGElMjIlMkMlMjJ1c2VySWQlMjIlM0E5NTk3NDMwJTJDJTIyc2Vzc2lvbklkJTIyJTNBMTc1OTAxNzI5Nzk2MiUyQyUyMm9wdE91dCUyMiUzQWZhbHNlJTJDJTIybGFzdEV2ZW50VGltZSUyMiUzQTE3NTkwMTczMDU2OTElMkMlMjJsYXN0RXZlbnRJZCUyMiUzQTElN0Q=; AMP_MKTG_c9c53a1635=JTdCJTdE; _gcl_au=1.1.1390391560.1759014475.862737139.1759015020.1759015063; kwai_uuid=077a44315477796c8f93a9c7442277b6; __zlcmid=1TqnwqJL64fnYY6; ph_phc_e0n7nqvWcrfbMMRsMKZ8ldgxXiifN7U6s3PAsiNhtVJ_posthog=%7B%22distinct_id%22%3A%229597430%22%2C%22%24sesid%22%3A%5B1759021720515%2C%2201998d99-e501-766f-a40d-31a1f9e05117%22%2C1759017297153%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https%3A%2F%2Fblaze.bet.br%2Fpt%2Fgames%2Fdouble%3Fmodal%3Dauth%26tab%3Dlogin%22%7D%7D",
        "Host": "api-gaming.blaze.bet.br",
        "Origin": "https://blaze.bet.br",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "websocket",
        "Sec-Fetch-Site": "same-site",
        "Sec-WebSocket-Extensions": "permessage-deflate",
        "Sec-WebSocket-Key": "UPN045VZ7Z61+pRhbVrbkg==",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.ws_connect(url) as ws:
            print("Conexão WebSocket estabelecida!")
            # Aguarde mensagens do servidor
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(f"Mensagem recebida: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'Erro na conexão WebSocket: {ws.exception()}')

# Exemplo de execução do WebSocket
if __name__ == "__main__":
    # Executa apenas a captura via WebSocket quando o módulo é executado diretamente.
    asyncio.run(connect_to_websocket())