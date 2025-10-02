#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extrator de Credenciais para Autenticação
Captura cookies e tokens do navegador para usar nas APIs
"""

import json
import os
import sqlite3
import base64
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AuthExtractor:
    """Extrai credenciais de autenticação do navegador."""
    
    def __init__(self):
        self.chrome_cookies_path = self._get_chrome_cookies_path()
        self.firefox_cookies_path = self._get_firefox_cookies_path()
        
    def _get_chrome_cookies_path(self) -> Optional[Path]:
        """Obtém caminho dos cookies do Chrome."""
        paths = [
            Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cookies",
            Path.home() / "AppData/Local/Google/Chrome/User Data/Profile 1/Cookies",
            Path.home() / ".config/google-chrome/Default/Cookies",
            Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
        ]
        
        for path in paths:
            if path.exists():
                return path
        return None
    
    def _get_firefox_cookies_path(self) -> Optional[Path]:
        """Obtém caminho dos cookies do Firefox."""
        firefox_dir = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
        if firefox_dir.exists():
            for profile_dir in firefox_dir.iterdir():
                if profile_dir.is_dir():
                    cookies_path = profile_dir / "cookies.sqlite"
                    if cookies_path.exists():
                        return cookies_path
        return None
    
    def extract_blaze_cookies(self) -> Dict[str, str]:
        """Extrai cookies específicos do Blaze."""
        cookies = {}
        
        # Tentar Chrome primeiro
        if self.chrome_cookies_path:
            cookies.update(self._extract_chrome_cookies())
        
        # Tentar Firefox se Chrome não funcionou
        if not cookies and self.firefox_cookies_path:
            cookies.update(self._extract_firefox_cookies())
        
        return cookies
    
    def _extract_chrome_cookies(self) -> Dict[str, str]:
        """Extrai cookies do Chrome."""
        cookies = {}
        
        try:
            # Copiar arquivo de cookies (Chrome pode estar usando)
            import shutil
            temp_cookies = "temp_cookies.db"
            shutil.copy2(self.chrome_cookies_path, temp_cookies)
            
            conn = sqlite3.connect(temp_cookies)
            cursor = conn.cursor()
            
            # Buscar cookies do Blaze
            cursor.execute("""
                SELECT name, value, host_key 
                FROM cookies 
                WHERE host_key LIKE '%blaze%' 
                   OR host_key LIKE '%pragmatic%'
                   OR host_key LIKE '%soline%'
            """)
            
            for name, value, host in cursor.fetchall():
                cookies[name] = value
                logger.info(f"Cookie encontrado: {name} para {host}")
            
            conn.close()
            os.remove(temp_cookies)
            
        except Exception as e:
            logger.error(f"Erro ao extrair cookies do Chrome: {e}")
        
        return cookies
    
    def _extract_firefox_cookies(self) -> Dict[str, str]:
        """Extrai cookies do Firefox."""
        cookies = {}
        
        try:
            conn = sqlite3.connect(self.firefox_cookies_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, value, host 
                FROM moz_cookies 
                WHERE host LIKE '%blaze%' 
                   OR host LIKE '%pragmatic%'
                   OR host LIKE '%soline%'
            """)
            
            for name, value, host in cursor.fetchall():
                cookies[name] = value
                logger.info(f"Cookie Firefox encontrado: {name} para {host}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao extrair cookies do Firefox: {e}")
        
        return cookies
    
    def get_blaze_headers_with_auth(self) -> Dict[str, str]:
        """Obtém headers com autenticação do Blaze."""
        cookies = self.extract_blaze_cookies()
        
        # Construir cookie string
        cookie_string = "; ".join([f"{name}={value}" for name, value in cookies.items()])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Origin': 'https://blaze.bet.br',
            'Referer': 'https://blaze.bet.br/'
        }
        
        if cookie_string:
            headers['Cookie'] = cookie_string
            logger.info(f"Headers com {len(cookies)} cookies configurados")
        else:
            logger.warning("Nenhum cookie encontrado - usando headers sem autenticação")
        
        return headers
    
    def save_credentials(self, filename: str = "blaze_credentials.json"):
        """Salva credenciais em arquivo."""
        credentials = {
            'cookies': self.extract_blaze_cookies(),
            'headers': self.get_blaze_headers_with_auth(),
            'extracted_at': str(datetime.now())
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Credenciais salvas em {filename}")
        return credentials
    
    def load_credentials(self, filename: str = "blaze_credentials.json") -> Optional[Dict]:
        """Carrega credenciais de arquivo."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                logger.info(f"Credenciais carregadas de {filename}")
                return credentials
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
        
        return None

def extract_and_save_credentials():
    """Função utilitária para extrair e salvar credenciais."""
    extractor = AuthExtractor()
    credentials = extractor.save_credentials()
    
    print("🔑 CREDENCIAIS EXTRAÍDAS:")
    print(f"📊 Cookies encontrados: {len(credentials['cookies'])}")
    
    for name, value in credentials['cookies'].items():
        print(f"   {name}: {value[:20]}...")
    
    print(f"📋 Headers configurados: {len(credentials['headers'])}")
    print("✅ Credenciais salvas em blaze_credentials.json")
    
    return credentials

if __name__ == "__main__":
    from datetime import datetime
    extract_and_save_credentials()
