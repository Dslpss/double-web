#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de configurações para o analisador de padrões do Double da Blaze.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# Configurações padrão
DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://blaze.com/api/roulette_games/recent",
        "timeout": 10,
        "max_retries": 3,
        "retry_delay": 2,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    },
    "database": {
        "type": "sqlite",  # sqlite, mysql, postgresql
        "path": "data/blaze_data.db",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "blaze_analyzer",
        "table_prefix": "blaze_"
    },
    "data": {
        "recent_limit": 100,
        "historical_days": 30,
        "save_raw_data": True,
        "data_format": "json"
    },
    "analysis": {
        "pattern_lengths": [2, 3, 4, 5],
        "min_pattern_occurrences": 3,
        "color_analysis": True,
        "number_analysis": True,
        "time_analysis": True,
        "advanced_metrics": True,
        "statistical_tests": True
    },
    "model": {
        "type": "ensemble",  # simple, statistical, ml, deep_learning, ensemble
        "train_on_startup": True,
        "save_model": True,
        "model_path": "data/models",
        "input_sequence_length": 10,
        "prediction_horizon": 5,
        "confidence_threshold": 0.7,
        "use_pretrained": False,
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "early_stopping": True,
            "patience": 10
        }
    },
    "ui": {
        "enabled": True,
        "theme": "dark",
        "update_interval": 5,
        "charts": ["color_distribution", "pattern_frequency", "prediction_accuracy", "win_loss_ratio"],
        "show_statistics": True,
        "show_predictions": True,
        "show_alerts": False,  # Desabilitado para evitar spam de alertas
        "layout": "dashboard"
    },
    "notifications": {
        "enabled": False,
        "types": [],  # Removido popup e sound
        "sound_file": "data/sounds/alert.mp3",
        "min_confidence": 0.8,
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": ""
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        }
    },
    "monitoring": {
        "enabled": False,  # Desabilitado para evitar spam de notificações
        "interval": 5,  # segundos
        "auto_bet": False,
        "max_consecutive_losses": 3,
        "max_daily_loss": 100,
        "stop_on_profit": 200
    }
}

def load_config(config_path="config.json"):
    """
    Carrega as configurações do arquivo ou cria um novo com as configurações padrão.
    
    Args:
        config_path (str): Caminho para o arquivo de configuração
        
    Returns:
        dict: Configurações carregadas
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"Configurações carregadas de {config_path}")
                
                # Mescla com as configurações padrão para garantir que todos os campos existam
                merged_config = DEFAULT_CONFIG.copy()
                _deep_update(merged_config, config)
                return merged_config
        else:
            # Cria o arquivo de configuração com as configurações padrão
            save_config(DEFAULT_CONFIG, config_path)
            logger.info(f"Arquivo de configuração criado em {config_path}")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config, config_path="config.json"):
    """
    Salva as configurações em um arquivo.
    
    Args:
        config (dict): Configurações a serem salvas
        config_path (str): Caminho para o arquivo de configuração
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configurações salvas em {config_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {str(e)}")

def _deep_update(d, u):
    """
    Atualiza um dicionário de forma recursiva.
    
    Args:
        d (dict): Dicionário a ser atualizado
        u (dict): Dicionário com as atualizações
        
    Returns:
        dict: Dicionário atualizado
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        else:
            d[k] = v
    return d

def get_config_value(config, key_path, default=None):
    """
    Obtém um valor de configuração a partir de um caminho de chaves.
    
    Args:
        config (dict): Configurações
        key_path (str): Caminho de chaves separado por pontos (ex: "database.host")
        default: Valor padrão caso a chave não exista
        
    Returns:
        Valor da configuração ou o valor padrão
    """
    keys = key_path.split('.')
    value = config
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default