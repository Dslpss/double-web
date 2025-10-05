"""
Gerenciador de JSESSIONID para Railway
Diferentes estratégias para obter dados reais da Pragmatic Play no Railway
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class RailwayJSessionManager:
    """
    Gerencia JSESSIONIDs para uso no Railway com múltiplas estratégias
    """
    
    def __init__(self):
        self.jsessionid = None
        self.expiry_time = None
        self.storage_file = "jsessionid_cache.json"
        
    def get_jsessionid_from_env(self) -> Optional[str]:
        """
        Estratégia 1: JSESSIONID das variáveis de ambiente do Railway
        """
        jsessionid = os.environ.get('PRAGMATIC_JSESSIONID')
        if jsessionid:
            logger.info("🔑 JSESSIONID obtido das variáveis de ambiente")
            return jsessionid
        return None
    
    def get_jsessionid_from_webhook(self) -> Optional[str]:
        """
        Estratégia 2: JSESSIONID via webhook/API endpoint
        Você pode criar um endpoint que recebe JSESSIONID de um sistema externo
        """
        webhook_url = os.environ.get('JSESSIONID_WEBHOOK_URL')
        webhook_secret = os.environ.get('JSESSIONID_WEBHOOK_SECRET')
        
        if not webhook_url:
            return None
            
        try:
            headers = {'Authorization': f'Bearer {webhook_secret}'} if webhook_secret else {}
            response = requests.get(webhook_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jsessionid = data.get('jsessionid')
                if jsessionid:
                    logger.info("🌐 JSESSIONID obtido via webhook")
                    return jsessionid
        except Exception as e:
            logger.error(f"❌ Erro ao obter JSESSIONID via webhook: {e}")
        
        return None
    
    def try_auto_login(self) -> Optional[str]:
        """
        Estratégia 3: Tentar fazer login automático na Pragmatic Play
        AVISO: Isso pode violar ToS - usar com cuidado
        """
        username = os.environ.get('PRAGMATIC_USERNAME')
        password = os.environ.get('PRAGMATIC_PASSWORD')
        
        if not username or not password:
            logger.info("📝 Credenciais não disponíveis para auto-login")
            return None
        
        try:
            # URL de login da Pragmatic Play (exemplo - você precisa verificar a real)
            login_url = "https://client.pragmaticplaylive.net/api/login"
            
            session = requests.Session()
            
            # Headers para login
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://client.pragmaticplaylive.net',
                'Referer': 'https://client.pragmaticplaylive.net/'
            }
            
            # Dados de login
            login_data = {
                'username': username,
                'password': password
            }
            
            response = session.post(login_url, json=login_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extrair JSESSIONID dos cookies
                for cookie in session.cookies:
                    if cookie.name == 'JSESSIONID':
                        logger.info("🔐 JSESSIONID obtido via auto-login")
                        return cookie.value
                        
        except Exception as e:
            logger.error(f"❌ Erro no auto-login: {e}")
        
        return None
    
    def get_jsessionid_from_cache(self) -> Optional[str]:
        """
        Estratégia 4: JSESSIONID do cache local (se ainda válido)
        """
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                
                jsessionid = data.get('jsessionid')
                expiry = data.get('expiry')
                
                if jsessionid and expiry:
                    expiry_time = datetime.fromisoformat(expiry)
                    if datetime.now() < expiry_time:
                        logger.info("💾 JSESSIONID válido encontrado no cache")
                        return jsessionid
                    else:
                        logger.info("⏰ JSESSIONID no cache expirado")
        except Exception as e:
            logger.error(f"❌ Erro ao ler cache: {e}")
        
        return None
    
    def save_jsessionid_to_cache(self, jsessionid: str, duration_hours: int = 24):
        """
        Salva JSESSIONID no cache com tempo de expiração
        """
        try:
            expiry_time = datetime.now() + timedelta(hours=duration_hours)
            
            data = {
                'jsessionid': jsessionid,
                'expiry': expiry_time.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f)
                
            logger.info(f"💾 JSESSIONID salvo no cache (expira em {duration_hours}h)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache: {e}")
    
    def get_best_jsessionid(self) -> Optional[str]:
        """
        Tenta todas as estratégias em ordem de prioridade
        """
        strategies = [
            ("Variáveis de Ambiente", self.get_jsessionid_from_env),
            ("Cache Local", self.get_jsessionid_from_cache),
            ("Webhook Externo", self.get_jsessionid_from_webhook),
            ("Auto Login", self.try_auto_login)
        ]
        
        for strategy_name, strategy_func in strategies:
            logger.info(f"🔍 Tentando estratégia: {strategy_name}")
            jsessionid = strategy_func()
            
            if jsessionid:
                logger.info(f"✅ JSESSIONID obtido via {strategy_name}")
                # Salvar no cache se obtido de fonte externa
                if strategy_name != "Cache Local":
                    self.save_jsessionid_to_cache(jsessionid)
                return jsessionid
        
        logger.warning("⚠️ Nenhuma estratégia conseguiu obter JSESSIONID válido")
        return None

# Função utilitária para o app.py
def get_railway_jsessionid() -> Optional[str]:
    """
    Função simples para obter JSESSIONID no Railway
    """
    manager = RailwayJSessionManager()
    return manager.get_best_jsessionid()