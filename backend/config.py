#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configurações para o Blaze Double Analyzer Web
Baseado no sistema desktop
"""

import time

# ===== CONFIGURAÇÕES DA PLAYNABETS =====
# URL do WebSocket da PlayNabets (mesma do sistema desktop)
PLAYNABETS_WS_URL = 'wss://play.soline.bet:5903/Game'

# Token de autenticação (opcional)
PLAYNABETS_TOKEN = ''

# Headers para conexão (mesmos do sistema desktop)
PLAYNABETS_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
PLAYNABETS_ORIGIN = 'https://soline.bet'
PLAYNABETS_REFERER = 'https://soline.bet/'

# ===== CONFIGURAÇÕES DO ANALYZER =====
# Usar API oficial da Blaze (False para usar dados manuais)
USE_OFFICIAL_API = False

# Chave da API oficial (se usar)
BLAZE_API_KEY = ''

# ===== CONFIGURAÇÕES DE ANÁLISE =====
# Intervalo de atualização em segundos
UPDATE_INTERVAL = 2

# Limite de resultados para análise
RESULTS_LIMIT = 100

# Confiança mínima para alertas
MIN_CONFIDENCE = 0.7

# ===== CONFIGURAÇÕES DE BANCO DE DADOS =====
# Caminho do banco de dados
DB_PATH = 'data/blaze_enhanced.db'

# Limpeza automática
AUTO_CLEANUP = True

# Máximo de resultados armazenados
MAX_RESULTS_STORED = 10000

# ===== CONFIGURAÇÕES DE NOTIFICAÇÕES =====
# Notificações habilitadas
NOTIFICATIONS_ENABLED = True

# Notificações desktop
DESKTOP_NOTIFICATIONS = False

# Alertas sonoros (False para evitar conflito com Windows)
SOUND_ALERTS = False

# ===== CONFIGURAÇÕES DE DESENVOLVIMENTO =====
# Modo debug
DEBUG = True

# Porta do servidor web
PORT = 5000

# Host do servidor web
HOST = '0.0.0.0'

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
# Chave secreta para sessões
import os
SECRET_KEY = os.getenv('SECRET_KEY', 'blaze_analyzer_secret_key_2024_DEFAULT_CHANGE_ME')

# ===== CONFIGURAÇÕES DE LOG =====
# Nível de log
LOG_LEVEL = 'INFO'

# Diretório de logs
LOG_DIR = 'logs'

# ===== FUNÇÕES DE PROCESSAMENTO DE DADOS =====

def get_color_from_number(number):
    """
    Determina a cor com base no número (padrão correto: 1-7=RED, 8-14=BLACK, 0=WHITE).
    
    Args:
        number (int): Número do resultado (0-14)
    
    Returns:
        str: 'red', 'black', ou 'white'
    """
    if number == 0:
        return 'white'
    elif 1 <= number <= 7:
        return 'red'
    elif 8 <= number <= 14:
        return 'black'
    else:
        return 'unknown'

def extract_result_from_payload(data):
    """
    Extrai número e cor do payload JSON recebido da PlayNabets.
    Baseado na lógica do sistema desktop.
    
    Args:
        data (dict): Dados JSON recebidos
    
    Returns:
        dict: {'number': int, 'color': str, 'round_id': str} ou None
    """
    try:
        # Verificar se tem 'value' (número do resultado)
        if 'value' not in data:
            return None
        
        # Extrair número
        value = data['value']
        if isinstance(value, (int, float)):
            number = int(value)
        else:
            # Tentar converter string para int
            try:
                number = int(str(value))
            except (ValueError, TypeError):
                return None
        
        # Verificar se o número é válido (0-14)
        if not (0 <= number <= 14):
            print(f"Número inválido recebido: {number}")
            return None
        
        # Determinar cor
        color = get_color_from_number(number)
        
        # Extrair round_id se disponível
        import time
        round_id = data.get('round_id', f'round_{int(time.time())}')
        
        return {
            'number': number,
            'color': color,
            'round_id': round_id,
            'timestamp': int(time.time()),
            'source': 'playnabets'
        }
        
    except Exception as e:
        print(f"Erro ao extrair resultado do payload: {e}")
        return None

# ===== CONFIGURAÇÕES DE HEADERS =====
def get_playnabets_headers():
    """
    Retorna os headers para conexão com PlayNabets.
    Baseado no sistema desktop.
    """
    return {
        'User-Agent': PLAYNABETS_USER_AGENT,
        'Origin': PLAYNABETS_ORIGIN,
        'Referer': PLAYNABETS_REFERER
    }

# ===== CONFIGURAÇÕES DE URL =====
def get_playnabets_url():
    """
    Retorna a URL completa para conexão com PlayNabets.
    Inclui token se disponível.
    """
    url = PLAYNABETS_WS_URL
    if PLAYNABETS_TOKEN:
        if '?' in url:
            url = f"{url}&token={PLAYNABETS_TOKEN}"
        else:
            url = f"{url}?token={PLAYNABETS_TOKEN}"
    return url
