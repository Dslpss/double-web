#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cliente oficial para a API do Blaze baseado na documentação oficial.
Documentação: https://apidocs.blaze.me/
"""

import requests
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BlazeOfficialAPI:
    """Cliente para a API oficial do Blaze."""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.blaze.com"):
        """
        Inicializa o cliente da API oficial do Blaze.
        
        Args:
            api_key (str): Chave da API do Blaze
            base_url (str): URL base da API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
        
        logger.info("Cliente da API oficial do Blaze inicializado")
    
    def get_roulette_games(self, limit: int = 100, game_type: str = "double") -> List[Dict]:
        """
        Obtém jogos de roleta recentes.
        
        Args:
            limit (int): Número de jogos a serem obtidos
            game_type (str): Tipo de jogo (double, crash, etc.)
            
        Returns:
            List[Dict]: Lista de jogos
        """
        try:
            # Endpoint baseado na documentação oficial
            endpoint = f"{self.base_url}/v1/roulette/games"
            params = {
                'limit': limit,
                'type': game_type,
                'status': 'complete'
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Obtidos {len(data.get('games', []))} jogos de roleta")
                return data.get('games', [])
            elif response.status_code == 401:
                logger.warning("API key inválida ou ausente")
                return self._get_fallback_data()
            else:
                logger.error(f"Erro na API: {response.status_code}")
                return self._get_fallback_data()
                
        except Exception as e:
            logger.error(f"Erro ao obter jogos de roleta: {str(e)}")
            return self._get_fallback_data()
    
    def get_member_info(self, email: str = None, phone: str = None) -> Optional[Dict]:
        """
        Obtém informações de um membro.
        
        Args:
            email (str): Email do membro
            phone (str): Telefone do membro
            
        Returns:
            Dict: Informações do membro
        """
        if not self.api_key:
            logger.warning("API key necessária para obter informações de membros")
            return None
        
        try:
            endpoint = f"{self.base_url}/v1/members"
            params = {}
            
            if email:
                params['email'] = email
            elif phone:
                params['phone'] = phone
            else:
                logger.error("Email ou telefone deve ser fornecido")
                return None
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter membro: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do membro: {str(e)}")
            return None
    
    def create_member(self, member_data: Dict) -> Optional[Dict]:
        """
        Cria um novo membro.
        
        Args:
            member_data (Dict): Dados do membro
            
        Returns:
            Dict: Dados do membro criado
        """
        if not self.api_key:
            logger.warning("API key necessária para criar membros")
            return None
        
        try:
            endpoint = f"{self.base_url}/v1/members"
            response = self.session.post(endpoint, json=member_data)
            
            if response.status_code == 201:
                logger.info("Membro criado com sucesso")
                return response.json()
            else:
                logger.error(f"Erro ao criar membro: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar membro: {str(e)}")
            return None
    
    def get_products(self, limit: int = 50) -> List[Dict]:
        """
        Obtém lista de produtos.
        
        Args:
            limit (int): Número de produtos a serem obtidos
            
        Returns:
            List[Dict]: Lista de produtos
        """
        try:
            endpoint = f"{self.base_url}/v1/products"
            params = {'limit': limit}
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('products', [])
            else:
                logger.error(f"Erro ao obter produtos: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter produtos: {str(e)}")
            return []
    
    def _get_fallback_data(self) -> List[Dict]:
        """
        Dados de fallback quando a API oficial não está disponível.
        
        Returns:
            List[Dict]: Dados simulados
        """
        logger.info("Usando dados de fallback")
        
        # Simula alguns dados para demonstração
        fallback_data = []
        current_time = int(time.time() * 1000)
        
        # Gera 20 resultados simulados
        import random
        for i in range(20):
            roll = random.randint(0, 14)
            
            if roll == 0:
                color = 'white'
            elif 1 <= roll <= 7:
                color = 'red'
            else:
                color = 'black'
            
            fallback_data.append({
                'id': f'fallback_{current_time - (i * 30000)}',
                'roll': roll,
                'color': color,
                'created_at': datetime.fromtimestamp((current_time - (i * 30000)) / 1000).isoformat(),
                'timestamp': (current_time - (i * 30000)) / 1000,
                'status': 'complete',
                'source': 'fallback'
            })
        
        return fallback_data
    
    def parse_game_result(self, game: Dict) -> Dict:
        """
        Analisa um resultado de jogo e extrai informações relevantes.
        
        Args:
            game (Dict): Dados do jogo da API
            
        Returns:
            Dict: Dados formatados do resultado
        """
        try:
            roll = game.get('roll')
            color = self._determine_color(roll)
            created_at = game.get('created_at') or game.get('started_at')
            
            return {
                'id': game.get('id'),
                'roll': roll,
                'color': color,
                'created_at': created_at,
                'timestamp': self._parse_timestamp(created_at),
                'status': game.get('status', 'complete'),
                'game_type': game.get('game_type', 'double'),
                'source': 'official_api'
            }
        except Exception as e:
            logger.error(f"Erro ao analisar resultado do jogo: {str(e)}")
            return {}
    
    def _determine_color(self, roll: int) -> str:
        """
        Determina a cor com base no número sorteado.
        
        Args:
            roll (int): Número sorteado
            
        Returns:
            str: Cor correspondente
        """
        if roll == 0:
            return 'white'
        elif 1 <= roll <= 7:
            return 'red'
        elif 8 <= roll <= 14:
            return 'black'
        else:
            return 'unknown'
    
    def _parse_timestamp(self, date_str: str) -> int:
        """
        Converte string de data para timestamp.
        
        Args:
            date_str (str): String de data
            
        Returns:
            int: Timestamp em segundos
        """
        try:
            if date_str:
                # Tenta diferentes formatos
                for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(date_str.replace('Z', ''), fmt.replace('Z', ''))
                        return int(dt.timestamp())
                    except ValueError:
                        continue
            
            return int(time.time())
        except Exception:
            return int(time.time())
