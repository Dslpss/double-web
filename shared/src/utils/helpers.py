#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções utilitárias para o analisador do Double da Blaze.
"""

import os
import logging
import json
import time
from datetime import datetime
import random
import string

def setup_logging(log_dir, level=logging.INFO):
    """
    Configura o sistema de logs.
    
    Args:
        log_dir (str): Diretório para armazenar os logs
        level (int): Nível de log
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Cria o diretório de logs se não existir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nome do arquivo de log com timestamp
    log_file = os.path.join(log_dir, f"blaze_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configura o formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configura o handler de arquivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Configura o handler de console
    import re
    class EmojiStripFilter(logging.Filter):
        """
        Remove emojis e caracteres não-ASCII das mensagens para evitar erros de encode
        no console do Windows (cp1252). O arquivo de log continua preservando a mensagem
        original via FileHandler.
        """
        def filter(self, record):
            try:
                # construir a mensagem final e substituir caracteres não-ASCII
                msg = record.getMessage()
                # substituir por caractere '?' os não-ascii
                safe = re.sub(r'[^\x00-\x7F]+', '?', msg)
                # preservar args compatíveis, atualizar msg para console
                record.msg = safe
                record.args = ()
            except Exception:
                pass
            return True

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.addFilter(EmojiStripFilter())
    
    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def generate_id(prefix="", length=8):
    """
    Gera um ID aleatório.
    
    Args:
        prefix (str): Prefixo para o ID
        length (int): Comprimento do ID
        
    Returns:
        str: ID gerado
    """
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{random_part}"

def save_json(data, file_path):
    """
    Salva dados em formato JSON.
    
    Args:
        data: Dados a serem salvos
        file_path (str): Caminho do arquivo
        
    Returns:
        bool: True se o salvamento for bem-sucedido
    """
    try:
        # Cria o diretório se não existir
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar JSON: {str(e)}")
        return False

def load_json(file_path, default=None):
    """
    Carrega dados de um arquivo JSON.
    
    Args:
        file_path (str): Caminho do arquivo
        default: Valor padrão se o arquivo não existir
        
    Returns:
        dict: Dados carregados ou valor padrão
    """
    try:
        if not os.path.exists(file_path):
            return default
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar JSON: {str(e)}")
        return default

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorador para repetir uma função em caso de exceção.
    
    Args:
        max_attempts (int): Número máximo de tentativas
        delay (float): Atraso inicial entre tentativas
        backoff (float): Fator de aumento do atraso
        exceptions (tuple): Exceções a serem capturadas
        
    Returns:
        function: Decorador
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_attempts:
                        raise
                    
                    logging.warning(f"Tentativa {attempt} falhou: {str(e)}. Tentando novamente em {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    
    return decorator

def format_timestamp(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Formata um timestamp Unix para uma string legível.
    
    Args:
        timestamp (int): Timestamp Unix
        format_str (str): Formato da string
        
    Returns:
        str: Timestamp formatado
    """
    return datetime.fromtimestamp(timestamp).strftime(format_str)

def color_name_pt(color):
    """
    Retorna o nome da cor em português.
    
    Args:
        color (str): Nome da cor em inglês
        
    Returns:
        str: Nome da cor em português
    """
    color_map = {
        'red': 'Vermelho',
        'black': 'Preto',
        'white': 'Branco'
    }
    
    return color_map.get(color, color)

def calculate_win_rate(predictions):
    """
    Calcula a taxa de acerto das previsões.
    
    Args:
        predictions (list): Lista de previsões
        
    Returns:
        float: Taxa de acerto
    """
    if not predictions:
        return 0.0
    
    correct = sum(1 for p in predictions if p.get('correct', False))
    return correct / len(predictions)

def calculate_roi(predictions, bet_amount=1.0):
    """
    Calcula o retorno sobre investimento (ROI) das previsões.
    
    Args:
        predictions (list): Lista de previsões
        bet_amount (float): Valor da aposta
        
    Returns:
        float: ROI
    """
    if not predictions:
        return 0.0
    
    total_invested = len(predictions) * bet_amount
    
    if total_invested == 0:
        return 0.0
    
    total_return = 0.0
    
    for pred in predictions:
        if pred.get('correct', False):
            color = pred.get('prediction', {}).get('color')
            
            if color == 'red' or color == 'black':
                total_return += bet_amount * 2
            elif color == 'white':
                total_return += bet_amount * 14
    
    return (total_return - total_invested) / total_invested