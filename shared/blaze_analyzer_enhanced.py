
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador de Padrões do Double da Blaze - Versão Melhorada
Integrado com a API oficial do Blaze e funcionalidades avançadas.
"""

import requests
import json
import time
import pandas as pd
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from shared.src.api.blaze_official_api import BlazeOfficialAPI
from shared.src.database.db_manager import DatabaseManager
from shared.src.analysis.pattern_analyzer import PatternAnalyzer
from shared.src.models.prediction_model import PredictionModel
from shared.src.notifications.alert_system import AlertSystem
from shared.src.notifications.pattern_notifier import notify_pattern, notify_result, get_notifier
from shared.src.database.local_storage_db import local_db
from shared.src.analysis.double_patterns import DoublePatternDetector
from shared.src.ml.adaptive_integrator import AdaptiveIntegrator
from shared.src.ml.prediction_validator import PredictionValidator
from shared.src.ml.prediction_feedback import PredictionFeedback
from shared.src.analysis.dual_color_patterns import DualColorPatternDetector
from shared.src.ml.pattern_reassessor import PatternReassessor
from shared.src.ml.reassessment_callbacks import (
    PatternAnalyzerReassessmentCallback,
    DualPatternDetectorReassessmentCallback,
    AdaptiveLearnerReassessmentCallback
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlazeAnalyzerEnhanced:
    """Analisador melhorado do Double da Blaze com integração à API oficial."""
    
    def __init__(self, api_key: str = None, use_official_api: bool = True, resignal_on_correct: bool = True):
        """
        Inicializa o analisador melhorado.
        
        Args:
            api_key (str): Chave da API oficial do Blaze
            use_official_api (bool): Se deve usar a API oficial
        """
        self.api_key = api_key
        self.use_official_api = use_official_api
        
        # Inicializar componentes
        if self.use_official_api:
            self.api_client = BlazeOfficialAPI(api_key)
        else:
            # Fallback para a implementação anterior
            self.api_client = None
            self.base_url = "https://blaze.com/api/roulette_games/recent"
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        
        # Inicializar banco de dados
        self.db_manager = DatabaseManager("data/blaze_enhanced.db")
        
        # Inicializar analisador de padrões
        self.pattern_analyzer = PatternAnalyzer()
        
        # Inicializar modelo de predição
        self.prediction_model = PredictionModel()
        
        # Inicializar detector de padrões Double
        self.double_pattern_detector = DoublePatternDetector()
        
        # Inicializar sistema de alertas
        self.alert_system = AlertSystem({
            'enabled': True,
            'min_confidence': 0.7,
            'desktop_notifications': True,
            'sound_alerts': True,
            'types': ['sound', 'popup', 'telegram'],
            'telegram': {
                'enabled': True,
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
            }
        })
        
        # Inicializar sistema de aprendizado adaptativo
        adaptive_config = {
            'auto_learning': True,
            'learning_interval': 30,
            'min_data_for_learning': 10,  # Era 50
            'learner_config': {
                'min_pattern_frequency': 3,
                'min_confidence_threshold': 0.6,
                'max_patterns': 100,
                'learning_rate': 0.1,
                'decay_factor': 0.95,
                'history_size': 1000
            }
        }
        self.adaptive_integrator = AdaptiveIntegrator(adaptive_config)
        
        # Inicializar sistema de validação de predições
        validator_config = {
            'min_confidence_threshold': 0.7,
            'max_pending_predictions': 3,
            'validation_timeout_minutes': 5
        }
        self.prediction_validator = PredictionValidator(validator_config)
        
        # Inicializar sistema de feedback
        feedback_config = {
            'show_popup_alerts': False,  # Desabilitado para evitar spam de popups
            'show_console_feedback': True,
            'play_sound': False,  # Desabilitado para evitar spam de sons
            'feedback_delay': 1.0
        }
        self.prediction_feedback = PredictionFeedback(feedback_config)
        
        # Conectar feedback ao validador
        self.prediction_validator.add_feedback_callback(self.prediction_feedback.process_prediction_result)
        
        # Inicializar detector de padrões dual
        dual_pattern_config = {
            'min_pattern_frequency': 3,
            'min_confidence_threshold': 0.6,
            'max_patterns': 200,
            'sequence_length_range': (3, 8),
            'history_size': 1000
        }
        self.dual_pattern_detector = DualColorPatternDetector(dual_pattern_config)
        
        # Inicializar sistema de reavaliação de padrões
        reassessment_config = {
            'auto_reassess': True,
            'reassess_after_validation': True,
            'reassess_after_pattern_break': True,
            'min_data_for_reassessment': 10,
            'reassessment_cooldown_seconds': 30
        }
        self.pattern_reassessor = PatternReassessor(reassessment_config)
        
        # Registrar callbacks de reavaliação
        self._register_reassessment_callbacks()
        
        # Conectar reavaliação ao feedback de validação
        self.prediction_validator.add_feedback_callback(self.pattern_reassessor.on_prediction_validated)
        
        # Controle para evitar sinais repetidos sem checagem
        self.last_signal_ts = 0
        self.signal_cooldown_seconds = 180  # 3 minutos entre sinais (análise mais cuidadosa)
        self.min_rounds_for_analysis = 8  # Mínimo de 8 rodadas para analisar antes de enviar sinal
        self.immediate_resignal_limit = 0  # Desabilitar re-sinais imediatos
        self._immediate_resignal_count = 0
        self.last_pattern_detected_at = 0  # Timestamp do último padrão detectado
        
        self.data = []
        self.manual_data = []
        self.analysis_cache = {}
        # callbacks para atualizações de previsões (pred_id, correct, result_id)
        self._prediction_update_callbacks = []
        # configurar comportamento de re-sinal quando a previsão for correta
        self.resignal_on_correct = bool(resignal_on_correct)
        # track last recommended color to avoid repeating same recommendation quickly
        self.last_recommended_color = None
        
        # 🆕 SISTEMA DE RASTREAMENTO DE TAXA DE ACERTO POR PADRÃO
        self.pattern_performance = {
            'sequence': {'correct': 0, 'total': 0, 'accuracy': 0.0},
            'dominance': {'correct': 0, 'total': 0, 'accuracy': 0.0},
            'double_patterns': {'correct': 0, 'total': 0, 'accuracy': 0.0},
            'general_patterns': {'correct': 0, 'total': 0, 'accuracy': 0.0}
        }
        
        # 🆕 CONFIGURAÇÕES DE APRENDIZADO ADAPTATIVO
        self.adaptive_thresholds = {
            'sequence': 0.72,      # Confiança mínima por tipo de padrão
            'dominance': 0.72,
            'double_patterns': 0.72,
            'general_patterns': 0.72
        }
        
        # 🆕 MODO DE PREDIÇÃO: 'opposite' ou 'continue'
        self.prediction_mode = 'opposite'  # Padrão: apostar na cor oposta
        # Modo 'continue' = apostar na mesma cor (hot hand)
        
        # 🆕 HISTÓRICO DE SINAIS PARA ANÁLISE
        self.signal_history = []  # Últimos 50 sinais
        self.max_signal_history = 50

        # Carregar dados existentes do banco
        self._load_existing_data()
        
        logger.info("Blaze Analyzer Enhanced inicializado")
    
    def _load_existing_data(self) -> None:
        """Carrega dados existentes do banco de dados na inicialização."""
        try:
            # MODIFICAÇÃO: Não carregar dados históricos para cada sessão começar limpa
            # Isso evita interferência de dados antigos na análise atual
            logger.info("Sessão iniciada com dados limpos (sem histórico persistente)")
            
            # Opcional: Carregar apenas os últimos 5 resultados para contexto mínimo
            # (apenas se necessário para inicialização de sistemas)
            recent_results = self.db_manager.get_recent_results(5)
            
            if recent_results:
                logger.info(f"Carregados apenas {len(recent_results)} resultados para contexto mínimo")
                
                # Converter para formato esperado pelo analisador
                for result in recent_results:
                    # Adicionar aos dados manuais (formato compatível)
                    self.manual_data.append({
                        'roll': result.get('roll'),
                        'color': result.get('color'),
                        'timestamp': result.get('timestamp') or result.get('created_at'),
                        'id': result.get('id')
                    })
                
                # Alimentar os sistemas de análise com os dados existentes (apenas contexto mínimo)
                for result in recent_results:
                    # Alimentar detector de padrões dual
                    if hasattr(self, 'dual_pattern_detector'):
                        self.dual_pattern_detector.add_result({
                            'roll': result.get('roll'),
                            'color': result.get('color'),
                            'timestamp': result.get('timestamp') or result.get('created_at')
                        })
                    
                    # Alimentar sistema de aprendizado adaptativo
                    if hasattr(self, 'adaptive_integrator'):
                        self.adaptive_integrator.add_result({
                            'roll': result.get('roll'),
                            'color': result.get('color'),
                            'timestamp': result.get('timestamp') or result.get('created_at')
                        })
                
                logger.info("Sistemas de análise inicializados com contexto mínimo")
            else:
                logger.info("Nenhum dado histórico encontrado - sessão completamente limpa")
                
            # Verificar se precisa de limpeza automática
            self._check_and_cleanup_database()
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados existentes: {e}")
    
    def _check_and_cleanup_database(self) -> None:
        """Verifica se é necessário fazer limpeza automática do banco."""
        try:
            stats = self.db_manager.get_database_stats()
            
            if 'error' in stats:
                logger.error(f"Erro ao obter estatísticas: {stats['error']}")
                return
            
            results_count = stats.get('results_count', 0)
            
            # Limpeza automática se tiver mais de 1000 resultados
            if results_count > 1000:
                logger.info(f"Banco com {results_count} resultados - iniciando limpeza automática")
                
                cleanup_result = self.db_manager.cleanup_old_data(
                    results_days=30,  # Manter últimos 30 dias
                    predictions_days=7  # Manter últimos 7 dias
                )
                
                if 'error' not in cleanup_result:
                    removed_results = cleanup_result.get('results_removed', 0)
                    removed_predictions = cleanup_result.get('predictions_removed', 0)
                    logger.info(f"Limpeza automática concluída: {removed_results} resultados e {removed_predictions} predições removidos")
                else:
                    logger.error(f"Erro na limpeza automática: {cleanup_result['error']}")
            else:
                logger.info(f"Banco com {results_count} resultados - limpeza não necessária")
                
        except Exception as e:
            logger.error(f"Erro na verificação de limpeza: {e}")
    
    def _register_reassessment_callbacks(self) -> None:
        """Registra callbacks de reavaliação para todos os sistemas."""
        try:
            # Callback para PatternAnalyzer
            pattern_callback = PatternAnalyzerReassessmentCallback(self.pattern_analyzer)
            self.pattern_reassessor.register_callback('pattern_analyzer', pattern_callback)
            
            # Callback para DualPatternDetector
            dual_callback = DualPatternDetectorReassessmentCallback(self.dual_pattern_detector)
            self.pattern_reassessor.register_callback('dual_pattern_detector', dual_callback)
            
            # Callback para AdaptiveLearner
            if hasattr(self, 'adaptive_integrator') and self.adaptive_integrator:
                adaptive_callback = AdaptiveLearnerReassessmentCallback(self.adaptive_integrator.pattern_learner)
                self.pattern_reassessor.register_callback('adaptive_learner', adaptive_callback)
            
            logger.info("Callbacks de reavaliação registrados")
            
        except Exception as e:
            logger.error(f"Erro ao registrar callbacks de reavaliação: {e}")
    
    def _send_validated_alert(self, payload: dict) -> bool:
        """
        Envia alerta com validação de predição.
        
        Args:
            payload: Dados do alerta
            
        Returns:
            True se o alerta foi enviado
        """
        try:
            # Extrair informações da predição
            predicted_color = payload.get('recommended_color', '').lower()
            confidence = payload.get('confidence', 0.0)
            reasoning = payload.get('reasoning', '')
            pattern_id = payload.get('pattern_id', 'unknown')
            
            # Verificar se deve enviar alerta
            if not self.prediction_validator.should_send_alert(confidence):
                logger.info(f"Alerta não enviado - confiança insuficiente: {confidence:.2%}")
                return False
            
            # Adicionar predição ao validador
            prediction_id = self.prediction_validator.add_prediction(
                predicted_color=predicted_color,
                confidence=confidence,
                pattern_id=pattern_id,
                reasoning=reasoning
            )
            
            if prediction_id:
                # Adicionar ID da predição ao payload
                payload['prediction_id'] = prediction_id
                
                # Enviar alerta
                self.alert_system.send_alert(payload)
                
                logger.info(f"Alerta enviado com validação: {predicted_color} ({confidence:.2%}) - ID: {prediction_id}")
                return True
            else:
                logger.info("Alerta não enviado - predição rejeitada pelo validador")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar alerta validado: {e}")
            return False
    
    def start_adaptive_learning(self) -> bool:
        """
        Inicia o sistema de aprendizado adaptativo.
        
        Returns:
            bool: True se iniciou com sucesso
        """
        try:
            success = self.adaptive_integrator.start_adaptive_learning()
            if success:
                logger.info("Sistema de aprendizado adaptativo iniciado")
            else:
                logger.error("Falha ao iniciar sistema de aprendizado adaptativo")
            return success
        except Exception as e:
            logger.error(f"Erro ao iniciar aprendizado adaptativo: {e}")
            return False
    
    def stop_adaptive_learning(self) -> bool:
        """
        Para o sistema de aprendizado adaptativo.
        
        Returns:
            bool: True se parou com sucesso
        """
        try:
            success = self.adaptive_integrator.stop_adaptive_learning()
            if success:
                logger.info("Sistema de aprendizado adaptativo parado")
            else:
                logger.error("Falha ao parar sistema de aprendizado adaptativo")
            return success
        except Exception as e:
            logger.error(f"Erro ao parar aprendizado adaptativo: {e}")
            return False
    
    def get_adaptive_learning_insights(self) -> dict:
        """
        Obtém insights do sistema de aprendizado adaptativo.
        
        Returns:
            dict: Insights do aprendizado
        """
        try:
            return self.adaptive_integrator.get_learning_insights()
        except Exception as e:
            logger.error(f"Erro ao obter insights do aprendizado: {e}")
            return {}
    
    def get_prediction_validation_stats(self) -> dict:
        """
        Obtém estatísticas de validação de predições.
        
        Returns:
            dict: Estatísticas de validação
        """
        try:
            validator_stats = self.prediction_validator.get_stats()
            feedback_stats = self.prediction_feedback.get_feedback_stats()
            
            return {
                'validator_stats': validator_stats,
                'feedback_stats': feedback_stats,
                'pending_predictions': self.prediction_validator.get_pending_predictions(),
                'recent_validations': self.prediction_validator.get_recent_validations(5),
                'recent_feedback': self.prediction_feedback.get_recent_feedback(5)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de validação: {e}")
            return {}
    
    def cleanup_expired_predictions(self) -> int:
        """
        Remove predições expiradas.
        
        Returns:
            int: Número de predições removidas
        """
        try:
            return self.prediction_validator.cleanup_expired_predictions()
        except Exception as e:
            logger.error(f"Erro ao limpar predições expiradas: {e}")
            return 0
    
    def get_dual_color_analysis(self) -> dict:
        """
        Obtém análise dual das cores.
        
        Returns:
            dict: Análise dual completa
        """
        try:
            return self.dual_pattern_detector.get_dual_analysis()
        except Exception as e:
            logger.error(f"Erro ao obter análise dual: {e}")
            return {}
    
    def predict_for_color(self, color: str) -> dict:
        """
        Faz predição específica para uma cor.
        
        Args:
            color: Cor ('red' ou 'black')
            
        Returns:
            dict: Predição para a cor
        """
        try:
            return self.dual_pattern_detector.predict_next_for_color(color)
        except Exception as e:
            logger.error(f"Erro ao predizer para cor {color}: {e}")
            return {'color': color, 'confidence': 0.33, 'error': str(e)}
    
    def get_patterns_for_color(self, color: str) -> list:
        """
        Obtém padrões específicos para uma cor.
        
        Args:
            color: Cor ('red' ou 'black')
            
        Returns:
            list: Lista de padrões para a cor
        """
        try:
            patterns = self.dual_pattern_detector.get_patterns_for_color(color)
            return [
                {
                    'pattern_id': p.pattern_id,
                    'category': p.category.value,
                    'confidence': p.confidence,
                    'success_rate': p.success_rate,
                    'frequency': p.frequency,
                    'red_pattern': p.red_pattern,
                    'black_pattern': p.black_pattern,
                    'last_seen': p.last_seen.isoformat()
                }
                for p in patterns
            ]
        except Exception as e:
            logger.error(f"Erro ao obter padrões para cor {color}: {e}")
            return []
    
    def start_pattern_reassessment(self) -> bool:
        """
        Inicia reavaliação periódica de padrões.
        
        Returns:
            bool: True se iniciou com sucesso
        """
        try:
            success = self.pattern_reassessor.start_periodic_reassessment(interval_minutes=10)
            if success:
                logger.info("Reavaliação periódica de padrões iniciada")
            else:
                logger.error("Falha ao iniciar reavaliação periódica")
            return success
        except Exception as e:
            logger.error(f"Erro ao iniciar reavaliação periódica: {e}")
            return False
    
    def stop_pattern_reassessment(self) -> bool:
        """
        Para reavaliação periódica de padrões.
        
        Returns:
            bool: True se parou com sucesso
        """
        try:
            success = self.pattern_reassessor.stop_periodic_reassessment()
            if success:
                logger.info("Reavaliação periódica de padrões parada")
            else:
                logger.error("Falha ao parar reavaliação periódica")
            return success
        except Exception as e:
            logger.error(f"Erro ao parar reavaliação periódica: {e}")
            return False
    
    def trigger_manual_reassessment(self, reason: str = "manual") -> bool:
        """
        Dispara reavaliação manual de padrões.
        
        Args:
            reason: Razão da reavaliação manual
            
        Returns:
            bool: True se reavaliação foi iniciada
        """
        try:
            from shared.src.ml.pattern_reassessor import ReassessmentTrigger
            
            context = {
                'reason': reason,
                'triggered_by': 'user',
                'timestamp': datetime.now().isoformat()
            }
            
            success = self.pattern_reassessor.trigger_reassessment(
                ReassessmentTrigger.TIME_BASED, 
                context
            )
            
            if success:
                logger.info(f"Reavaliação manual iniciada: {reason}")
            else:
                logger.error("Falha ao iniciar reavaliação manual")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao disparar reavaliação manual: {e}")
            return False
    
    def get_reassessment_stats(self) -> dict:
        """
        Obtém estatísticas de reavaliação de padrões.
        
        Returns:
            dict: Estatísticas de reavaliação
        """
        try:
            return self.pattern_reassessor.get_reassessment_stats()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de reavaliação: {e}")
            return {}
    
    def fetch_recent_data(self, limit: int = 100) -> list:
        """
        Obtém dados recentes usando a API oficial ou fallback.
        
        Args:
            limit (int): Número de resultados a serem obtidos
            
        Returns:
            list: Lista com os resultados recentes
        """
        try:
            if self.use_official_api and self.api_client:
                # Usar API oficial
                raw_games = self.api_client.get_roulette_games(limit)
                self.data = [self.api_client.parse_game_result(game) for game in raw_games]
            else:
                # Fallback para implementação anterior
                self.data = self._fetch_fallback_data(limit)
            
            # Salvar no banco de dados
            if self.data:
                self.db_manager.insert_results(self.data)
                logger.info(f"Obtidos e salvos {len(self.data)} resultados recentes")
            
            return self.data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados recentes: {str(e)}")
            return []
    
    def _fetch_fallback_data(self, limit: int) -> list:
        """Método de fallback para obter dados quando a API oficial não está disponível."""
        try:
            response = requests.get(f"{self.base_url}?page=1&size={limit}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Erro na API de fallback: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro na requisição de fallback: {str(e)}")
            return []
    
    def add_manual_result(self, number: int, color: str = None) -> list:
        """
        Adiciona um resultado manualmente.
        
        Args:
            number (int): Número do resultado (0-14)
            color (str, optional): Cor do resultado
            
        Returns:
            list: Lista atualizada com os resultados manuais
        """
        if color is None:
            if number == 0:
                color = "white"
            elif 1 <= number <= 7:
                color = "red"
            elif 8 <= number <= 14:
                color = "black"
            else:
                print(f"Número inválido: {number}. Deve estar entre 0 e 14.")
                return self.manual_data
        
        # Criar um objeto de resultado
        timestamp = int(time.time() * 1000)
        result = {
            "id": f"manual_{timestamp}",
            "created_at": datetime.now().isoformat(),
            "color": color,
            "roll": number,
            "server_seed": "manual_entry",
            "timestamp": timestamp / 1000,
            "source": "manual"
        }
        
        self.manual_data.append(result)
        
        # Salvar no banco de dados
        self.db_manager.insert_results([result])
        
        print(f"Resultado adicionado: Número {number}, Cor {color}")
        logger.info(f"Resultado manual adicionado: {number} ({color})")
        
        # Notificar resultado no console (apenas para debug)
        try:
            notify_result(number, color)
        except Exception as e:
            logger.exception(f'Erro ao notificar resultado: {e}')
        
        # Atualizar modelo de predição em tempo real
        try:
            if hasattr(self, 'prediction_model') and self.prediction_model:
                self.prediction_model.record_result(result)
        except Exception:
            logger.exception('Erro ao atualizar prediction_model com novo resultado')
        
        # Adicionar ao sistema de aprendizado adaptativo
        try:
            if hasattr(self, 'adaptive_integrator') and self.adaptive_integrator:
                self.adaptive_integrator.add_result(result)
        except Exception:
            logger.exception('Erro ao adicionar resultado ao aprendizado adaptativo')
        
        # Validar predições pendentes
        try:
            if hasattr(self, 'prediction_validator') and self.prediction_validator:
                validation_result = self.prediction_validator.validate_prediction(color)
                if validation_result.get('validated_count', 0) > 0:
                    logger.info(f"Validadas {validation_result['validated_count']} predições com resultado {color}")
                    
                    # Enviar notificação web sobre o resultado
                    try:
                        predictions = validation_result.get('predictions', [])
                        for pred in predictions:
                            was_correct = pred.get('status') == 'correct'
                            predicted_color = pred.get('predicted_color', '')
                            
                            # Enviar notificação de resultado via pattern notifier
                            from shared.src.notifications.pattern_notifier import get_notifier
                            notifier = get_notifier()
                            if notifier and notifier.web_callback:
                                notifier.web_callback({
                                    'type': 'prediction_result',
                                    'predicted_color': predicted_color,
                                    'actual_color': color,
                                    'actual_number': number,
                                    'was_correct': was_correct,
                                    'confidence': pred.get('confidence', 0),
                                    'timestamp': datetime.now().isoformat()
                                })
                                logger.info(f"Notificação de resultado enviada para web: {predicted_color} -> {color} ({'ACERTOU' if was_correct else 'ERROU'})")
                    except Exception as e:
                        logger.exception(f'Erro ao enviar notificação de resultado: {e}')
        except Exception:
            logger.exception('Erro ao validar predições pendentes')
        
        # Adicionar ao detector de padrões dual
        try:
            if hasattr(self, 'dual_pattern_detector') and self.dual_pattern_detector:
                self.dual_pattern_detector.add_result(result)
        except Exception:
            logger.exception('Erro ao adicionar resultado ao detector de padrões dual')

        # Após inserir um novo resultado, verificar previsões pendentes baseadas em padrões
        try:
            db = getattr(self, 'db_manager', None)
            if db:
                # Usar timestamp do resultado para associar a previsão gerada antes dele
                ts = result.get('timestamp') or (int(time.time()))
                # timestamp pode estar em float segundos (unixtime)
                last_pred = db.get_last_unverified_prediction_before_timestamp(ts)
                if last_pred and last_pred.get('method') in ['pattern_only', 'alert_system', 'model']:
                    # verificar se acertou comparando com cor deste resultado
                    pred_color = (last_pred.get('prediction_color') or last_pred.get('color') or '').lower()
                    actual_color = result.get('color', '').lower()
                    correct = (pred_color == actual_color)
                    updated = db.update_prediction_result(last_pred.get('id'), result.get('id'), correct)
                    # notificar callbacks registrados sobre a atualização da previsão
                    try:
                        if updated:
                            logger.info(f"Notificando callback para predição {last_pred.get('id')} - correct={correct}")
                            self._notify_prediction_update(last_pred.get('id'), correct, result.get('id'))
                    except Exception:
                        logger.exception('Erro ao notificar callbacks de atualização de previsão')
                    if updated:
                        logger.info(f"Verificada previsão pattern_only id={last_pred.get('id')} -> correct={correct}")
                        # enviar notificação sobre resultado da previsão
                        try:
                            if hasattr(self, 'alert_system') and self.alert_system:
                                msg = f"Previsão verificada id={last_pred.get('id')}: prevista={pred_color.upper()} -> resultado={actual_color.upper()} | {'ACERTO' if correct else 'ERRO'}"
                                # preferir notificar mesmo quando confiança for baixa
                                try:
                                    payload = {
                                        'db_id': last_pred.get('id'),
                                        'color': pred_color,
                                        'confidence': float(last_pred.get('confidence') or 0.0),
                                        'method': last_pred.get('method'),
                                        'status': 'CORRETO' if correct else 'ERRADO',
                                        'message': msg
                                    }
                                    # incluir número do resultado se disponível
                                    try:
                                        roll = result.get('roll') if isinstance(result, dict) else None
                                        if roll is None:
                                            # tentar campos alternativos
                                            roll = result.get('number') if isinstance(result, dict) else None
                                        if roll is not None:
                                            payload['roll'] = int(roll)
                                    except Exception:
                                        pass

                                    self._send_validated_alert(payload)
                                except Exception:
                                    logger.exception('Erro ao enviar alerta de verificação de previsão')
                        except Exception:
                            pass
                    else:
                        logger.warning(f"Falha ao atualizar previsão id={last_pred.get('id')}")
                    # se a previsão foi verificada (acertou ou errou), tentar re-analisar e gerar novo sinal
                    try:
                        if updated:
                            now = time.time()
                            # distinguir motivo para logging
                            reason_txt = 'acerto' if correct else 'erro'

                            # reset count se passou cooldown longo
                            if now - getattr(self, 'last_signal_ts', 0) > (getattr(self, 'signal_cooldown_seconds', 3) * 4):
                                self._immediate_resignal_count = 0

                            if self._immediate_resignal_count < getattr(self, 'immediate_resignal_limit', 1):
                                # apenas gerar novo sinal se não houver outras previsões pendentes
                                pending = db.get_last_unverified_prediction()
                                if pending is None:
                                    # coletar resultados recentes e gatilhos
                                    try:
                                        recent = db.get_recent_results(20)  # Era 50
                                    except Exception:
                                        recent = []
                                    try:
                                        triggers = self.pattern_analyzer.get_triggers(recent)
                                    except Exception:
                                        triggers = []

                                    # gerar novo sinal heurístico a partir dos gatilhos
                                    # ask the generator to avoid recommending the same color as the
                                    # previous prediction to reduce repetition of identical signals
                                    new_sig = self.generate_pattern_only_signal(triggers, recent, avoid_color=pred_color)
                                    if new_sig and new_sig.get('db_id'):
                                        self._immediate_resignal_count += 1
                                        self.last_signal_ts = now
                                        logger.info(f"Re-sinal gerado após {reason_txt} da previsão {last_pred.get('id')}: db_id={new_sig.get('db_id')}")
                                        # enviar alerta via sistema de alertas (opcional, UI pode ler DB)
                                        try:
                                            if hasattr(self, 'alert_system') and self.alert_system:
                                                payload = {
                                                    'color': new_sig.get('recommended_color'),
                                                    'confidence': new_sig.get('confidence'),
                                                    'method': 'resignal',
                                                    'message': f"Re-sinal após previsão {reason_txt}: {new_sig.get('recommended_color', '').upper()} (conf={new_sig.get('confidence',0):.2f})"
                                                }
                                                # tentar anexar último número dos resultados recentes
                                                try:
                                                    if isinstance(recent, list) and recent:
                                                        last_res = recent[0] if isinstance(recent[0], dict) else None
                                                        if last_res:
                                                            if 'roll' in last_res:
                                                                payload['roll'] = int(last_res.get('roll'))
                                                            elif 'number' in last_res:
                                                                payload['roll'] = int(last_res.get('number'))
                                                except Exception:
                                                    pass

                                                self._send_validated_alert(payload)
                                        except Exception:
                                            logger.exception('Erro ao enviar alerta para re-sinal')
                                else:
                                    logger.debug('Não gerando re-sinal: existe previsão pendente no DB')
                            else:
                                logger.debug('Limite de re-tentativas imediatas atingido; pulando re-sinal')
                    except Exception:
                        logger.exception('Erro ao tentar gerar re-sinal após verificação da previsão')
        except Exception:
            logger.exception('Erro ao verificar previsões pendentes')
        
        # NOVO: Após adicionar resultado, tentar detectar padrões e gerar sinal
        try:
            self._detect_and_notify_patterns()
        except Exception as e:
            logger.exception(f'Erro ao detectar padrões após adicionar resultado: {e}')
        
        return self.manual_data

    def register_prediction_update_callback(self, func):
        """Registra um callback que receberá (pred_id, correct, result_id) quando uma previsão for atualizada no DB."""
        try:
            if callable(func):
                self._prediction_update_callbacks.append(func)
        except Exception:
            pass

    def _notify_prediction_update(self, pred_id, correct, result_id=None):
        """Chama todos os callbacks registrados para notificar atualização de previsão."""
        try:
            for cb in list(self._prediction_update_callbacks):
                try:
                    cb(pred_id, correct, result_id)
                except Exception:
                    logger.exception('Callback de atualização de previsão levantou exceção')
        except Exception:
            logger.exception('Erro ao notificar callbacks de previsão')
    
    def _add_to_signal_history(self, signal_data: dict):
        """
        Adiciona sinal ao histórico para rastreamento.
        
        Args:
            signal_data: Dados do sinal detectado
        """
        try:
            self.signal_history.append(signal_data)
            
            # Manter apenas últimos N sinais
            if len(self.signal_history) > self.max_signal_history:
                self.signal_history = self.signal_history[-self.max_signal_history:]
            
            logger.debug(f"Sinal adicionado ao histórico: {signal_data['pattern_type']} -> {signal_data['predicted_color']}")
        except Exception as e:
            logger.error(f"Erro ao adicionar sinal ao histórico: {e}")
    
    def update_pattern_performance(self, pattern_id: str, was_correct: bool):
        """
        Atualiza a taxa de acerto de um padrão específico.
        
        Args:
            pattern_id: ID do padrão
            was_correct: Se a previsão estava correta
        """
        try:
            # Encontrar o sinal no histórico
            signal = None
            for s in reversed(self.signal_history):
                if s.get('pattern_id') == pattern_id:
                    signal = s
                    break
            
            if not signal:
                logger.warning(f"Sinal {pattern_id} não encontrado no histórico")
                return
            
            pattern_type = signal.get('pattern_type', 'unknown')
            
            if pattern_type in self.pattern_performance:
                # Atualizar estatísticas
                self.pattern_performance[pattern_type]['total'] += 1
                if was_correct:
                    self.pattern_performance[pattern_type]['correct'] += 1
                
                # Calcular nova taxa de acerto
                total = self.pattern_performance[pattern_type]['total']
                correct = self.pattern_performance[pattern_type]['correct']
                accuracy = correct / total if total > 0 else 0.0
                self.pattern_performance[pattern_type]['accuracy'] = accuracy
                
                logger.info(f"📊 Performance atualizada - {pattern_type}: {correct}/{total} ({accuracy:.1%})")
                
                # 🆕 APRENDIZADO ADAPTATIVO: Ajustar threshold baseado em performance
                self._adjust_adaptive_thresholds(pattern_type, accuracy, total)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar performance do padrão: {e}")
    
    def _adjust_adaptive_thresholds(self, pattern_type: str, accuracy: float, total_samples: int):
        """
        Ajusta dinamicamente os thresholds de confiança baseado na performance.
        
        Args:
            pattern_type: Tipo do padrão
            accuracy: Taxa de acerto atual
            total_samples: Número total de amostras
        """
        try:
            # Só ajustar após ter dados suficientes
            if total_samples < 5:
                return
            
            current_threshold = self.adaptive_thresholds.get(pattern_type, 0.72)
            
            # Lógica de ajuste
            if accuracy > 0.75:
                # Está acertando muito: REDUZIR threshold (permitir mais sinais)
                new_threshold = max(0.65, current_threshold - 0.02)
                action = "REDUZIDO"
            elif accuracy < 0.50:
                # Está errando muito: AUMENTAR threshold (ser mais seletivo)
                new_threshold = min(0.80, current_threshold + 0.03)
                action = "AUMENTADO"
            elif accuracy < 0.60:
                # Está errando um pouco: aumentar levemente
                new_threshold = min(0.78, current_threshold + 0.01)
                action = "AUMENTADO LEVEMENTE"
            else:
                # Performance OK: manter
                new_threshold = current_threshold
                action = "MANTIDO"
            
            if new_threshold != current_threshold:
                self.adaptive_thresholds[pattern_type] = new_threshold
                logger.info(f"🎯 Threshold {action} para {pattern_type}: {current_threshold:.2f} -> {new_threshold:.2f} (acurácia: {accuracy:.1%})")
        
        except Exception as e:
            logger.error(f"Erro ao ajustar thresholds adaptativos: {e}")
    
    def get_pattern_performance_stats(self) -> dict:
        """
        Retorna estatísticas de performance de todos os padrões.
        
        Returns:
            dict: Estatísticas completas
        """
        return {
            'performance': self.pattern_performance,
            'thresholds': self.adaptive_thresholds,
            'prediction_mode': self.prediction_mode,
            'signal_history_size': len(self.signal_history)
        }
    
    def set_prediction_mode(self, mode: str):
        """
        Define o modo de predição: 'opposite' ou 'continue'.
        
        Args:
            mode: 'opposite' (apostar na cor oposta) ou 'continue' (continuar na mesma cor)
        """
        if mode not in ['opposite', 'continue']:
            logger.error(f"Modo inválido: {mode}. Use 'opposite' ou 'continue'")
            return False
        
        self.prediction_mode = mode
        logger.info(f"🎯 Modo de predição alterado para: {mode}")
        return True
    
    def _reset_system_after_pattern(self, keep_context=True):
        """
        Reseta sistema após detectar um padrão, mantendo contexto suficiente.
        
        Args:
            keep_context (bool): Se True, mantém últimos 3-5 resultados para contexto
        """
        try:
            logger.info("[RESET] RESETANDO SISTEMA após detecção de padrão")
            
            # 1. Limpar dados manuais mantendo contexto
            if self.manual_data and len(self.manual_data) > 0:
                if keep_context:
                    # Manter últimos 3-5 resultados para contexto
                    context_size = min(5, max(3, len(self.manual_data) // 3))
                    self.manual_data = self.manual_data[-context_size:]
                    logger.info(f"[DADOS] Mantidos {context_size} resultados para contexto")
                else:
                    # RESET TOTAL - apenas último resultado (ponto de partida)
                    last_result = self.manual_data[-1]
                    self.manual_data = [last_result]
                    logger.info(f"[RESET TOTAL] Mantido apenas último resultado: {last_result.get('roll', 'N/A')} ({last_result.get('color', 'N/A')})")
            
            # 2. Limpar dados da API (manter alguns recentes se disponível)
            if self.data:
                if keep_context and len(self.data) > 3:
                    # Manter últimos 3 da API também
                    self.data = self.data[-3:]
                    logger.info("[DADOS] Mantidos 3 resultados da API para contexto")
                else:
                    # RESET TOTAL - limpar completamente
                    self.data = []
                    logger.info("[RESET TOTAL] Dados da API completamente limpos")
            
            # 3. Limpar apenas padrões muito antigos (não todos)
            try:
                if hasattr(self, 'local_db') and self.local_db:
                    # Limpar apenas padrões antigos (mais de 1 hora)
                    current_time = time.time()
                    if hasattr(self.local_db, 'clear_old_patterns'):
                        self.local_db.clear_old_patterns(older_than=current_time - 3600)  # 1 hora
                        logger.info("[LIMPEZA] Padrões antigos (>1h) removidos")
                    else:
                        # Fallback: limpar todos se não tiver método específico
                        self.local_db.clear_data('patterns')
                        logger.info("[LIMPEZA] Todos os padrões removidos (fallback)")
            except Exception as e:
                logger.warning(f"Erro ao limpar padrões antigos: {e}")
            
            # 4. Resetar contadores gradualmente
            if hasattr(self, 'pattern_detector'):
                # Resetar detector de padrões se possível
                if hasattr(self.pattern_detector, 'reset'):
                    self.pattern_detector.reset()
                    logger.info("[RESET] Detector de padrões resetado")
            
            # 4.1. Limpar sistemas de aprendizado adaptativo (reset total)
            if not keep_context:
                try:
                    # Resetar aprendizado adaptativo
                    if hasattr(self, 'adaptive_integrator') and self.adaptive_integrator:
                        if hasattr(self.adaptive_integrator, 'pattern_learner'):
                            if hasattr(self.adaptive_integrator.pattern_learner, 'clear_history'):
                                self.adaptive_integrator.pattern_learner.clear_history()
                                logger.info("[RESET TOTAL] Sistema de aprendizado adaptativo limpo")
                    
                    # Resetar detector de padrões dual
                    if hasattr(self, 'dual_pattern_detector') and self.dual_pattern_detector:
                        if hasattr(self.dual_pattern_detector, 'clear_history'):
                            self.dual_pattern_detector.clear_history()
                            logger.info("[RESET TOTAL] Detector de padrões dual limpo")
                except Exception as e:
                    logger.warning(f"Erro ao limpar sistemas de aprendizado: {e}")
            
            # 5. Limpar notificações antigas (manter recentes)
            try:
                if hasattr(self, 'notifier') and self.notifier:
                    # Limpar apenas notificações antigas
                    if hasattr(self.notifier, 'notifications_history'):
                        if not keep_context:
                            # RESET TOTAL - limpar TODAS as notificações
                            self.notifier.notifications_history = []
                            logger.info("[RESET TOTAL] Todas as notificações limpas")
                        elif len(self.notifier.notifications_history) > 3:
                            # Manter apenas últimas 3 notificações
                            self.notifier.notifications_history = self.notifier.notifications_history[-3:]
                            logger.info("[LIMPEZA] Notificações antigas removidas - mantidas últimas 3")
            except Exception as e:
                logger.warning(f"Erro ao limpar notificações: {e}")
            
            status_msg = "[SUCESSO] Sistema resetado TOTALMENTE - histórico esquecido" if not keep_context else "[SUCESSO] Sistema resetado com contexto preservado"
            logger.info(status_msg)
            
        except Exception as e:
            logger.error(f"Erro ao resetar sistema: {e}")
    
    def _should_detect_patterns(self):
        """
        Verifica se deve detectar padrões agora.
        Lógica inteligente baseada na frequência real do jogo e qualidade dos dados.
        REQUER PELO MENOS 3 MINUTOS ENTRE SINAIS E ANÁLISE DE 8+ RODADAS.
        """
        try:
            # Verificar se há dados suficientes para análise confiável
            data_to_analyze = self.manual_data if self.manual_data else self.data
            min_required = getattr(self, 'min_rounds_for_analysis', 8)
            
            if not data_to_analyze or len(data_to_analyze) < min_required:
                logger.debug(f"Dados insuficientes para análise: {len(data_to_analyze) if data_to_analyze else 0}/{min_required} rodadas")
                return False
            
            current_time = time.time()
            
            # 1. COOLDOWN RIGOROSO: Verificar se passou tempo suficiente desde o último sinal
            last_signal_time = getattr(self, 'last_pattern_detected_at', 0)
            cooldown_seconds = getattr(self, 'signal_cooldown_seconds', 180)
            time_since_last_signal = current_time - last_signal_time
            
            if time_since_last_signal < cooldown_seconds:
                remaining = int(cooldown_seconds - time_since_last_signal)
                logger.debug(f"⏳ Cooldown ativo: aguardando {remaining}s antes do próximo sinal (total: {cooldown_seconds}s)")
                return False
            
            # 2. Verificar se há previsão pendente no banco
            try:
                db = getattr(self, 'db_manager', None)
                if db:
                    pending = db.get_last_unverified_prediction()
                    if pending:
                        logger.debug(f"⏸️ Previsão pendente no DB (id={pending.get('id')}): aguardando verificação")
                        return False
            except Exception as e:
                logger.debug(f"Erro ao verificar previsões pendentes: {e}")
            
            # 3. Verificar se há dados muito recentes (cooldown baseado na frequência)
            if len(data_to_analyze) >= 3:
                recent_results = data_to_analyze[-3:]
                
                # Calcular tempo médio entre resultados
                time_diffs = []
                for i in range(1, len(recent_results)):
                    if isinstance(recent_results[i], dict) and isinstance(recent_results[i-1], dict):
                        ts1 = recent_results[i].get('timestamp', current_time)
                        ts2 = recent_results[i-1].get('timestamp', current_time)
                        if ts1 > ts2:
                            time_diffs.append(ts1 - ts2)
                
                if time_diffs:
                    avg_interval = sum(time_diffs) / len(time_diffs)
                    # Cooldown baseado na frequência real (2x o intervalo médio)
                    cooldown_time = max(10, min(60, avg_interval * 2))
                    
                    # Verificar se último resultado é muito recente
                    last_result = recent_results[-1]
                    if isinstance(last_result, dict):
                        last_timestamp = last_result.get('timestamp', current_time)
                        time_since_last = current_time - last_timestamp
                        
                        if time_since_last < cooldown_time:
                            logger.debug(f"Cooldown ativo: {time_since_last:.1f}s < {cooldown_time:.1f}s")
                            return False
            
            # 2. Verificar qualidade dos dados
            if len(data_to_analyze) >= 5:
                # Verificar se há diversidade suficiente nas cores
                recent_colors = [r.get('color', '') for r in data_to_analyze[-5:] if isinstance(r, dict)]
                unique_colors = len(set(recent_colors))
                
                # Se todas as cores são iguais nos últimos 5, pode ser um padrão válido
                if unique_colors == 1 and len(recent_colors) >= 3:
                    logger.debug("Dados uniformes detectados - permitindo detecção")
                    return True
                
                # Se há diversidade, verificar se não é muito aleatório
                if unique_colors >= 3:
                    # Verificar se há algum padrão emergente
                    color_counts = {}
                    for color in recent_colors:
                        color_counts[color] = color_counts.get(color, 0) + 1
                    
                    # Se uma cor aparece mais de 60%, pode ser um padrão
                    max_count = max(color_counts.values())
                    if max_count / len(recent_colors) > 0.6:
                        logger.debug("Predominância de cor detectada - permitindo detecção")
                        return True
                    
                    # Se muito aleatório, aguardar mais dados
                    if max_count / len(recent_colors) < 0.4:
                        logger.debug("Dados muito aleatórios - aguardando mais dados")
                        return False
            
            # 3. Verificar se já detectou padrão muito recentemente
            if hasattr(self, '_last_pattern_time'):
                time_since_last_pattern = current_time - self._last_pattern_time
                # AUMENTADO: cooldown de 30 para 60 segundos entre padrões (evitar spam)
                if time_since_last_pattern < 60:
                    logger.debug(f"Padrão detectado recentemente - aguardando {60 - time_since_last_pattern:.1f}s")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar se deve detectar padrões: {e}")
            return True
    
    def _validate_pattern_quality(self, data_to_analyze):
        """
        Valida a qualidade de um padrão detectado antes de aceitar.
        
        Args:
            data_to_analyze: Dados usados para detectar o padrão
            
        Returns:
            bool: True se o padrão é de qualidade suficiente
        """
        try:
            if not data_to_analyze or len(data_to_analyze) < 3:
                return False
            
            # 1. Verificar consistência temporal
            current_time = time.time()
            recent_results = data_to_analyze[-5:] if len(data_to_analyze) >= 5 else data_to_analyze
            
            # Verificar se os dados não são muito antigos
            old_data_count = 0
            for result in recent_results:
                if isinstance(result, dict):
                    timestamp = result.get('timestamp', current_time)
                    if current_time - timestamp > 300:  # 5 minutos
                        old_data_count += 1
            
            # Se mais de 50% dos dados são antigos, rejeitar
            if old_data_count / len(recent_results) > 0.5:
                logger.debug("Padrão rejeitado: dados muito antigos")
                return False
            
            # 2. Verificar diversidade de cores
            colors = [r.get('color', '') for r in recent_results if isinstance(r, dict)]
            unique_colors = len(set(colors))
            
            # Se há apenas 1 cor, verificar se é realmente um padrão válido
            if unique_colors == 1:
                if len(colors) < 4:  # Sequência muito curta
                    logger.debug("Padrão rejeitado: sequência muito curta")
                    return False
                # Sequência longa de mesma cor é válida
                return True
            
            # 3. Verificar se há predominância real
            if unique_colors >= 2:
                color_counts = {}
                for color in colors:
                    color_counts[color] = color_counts.get(color, 0) + 1
                
                max_count = max(color_counts.values())
                predominance_ratio = max_count / len(colors)
                
                # Precisa de pelo menos 60% de predominância
                if predominance_ratio < 0.6:
                    logger.debug(f"Padrão rejeitado: predominância insuficiente ({predominance_ratio:.2f})")
                    return False
            
            # 4. Verificar se não é muito aleatório
            if len(colors) >= 5:
                # Calcular entropia das cores
                color_probs = {}
                for color in colors:
                    color_probs[color] = color_probs.get(color, 0) + 1
                
                # Normalizar probabilidades
                total = len(colors)
                for color in color_probs:
                    color_probs[color] /= total
                
                # Calcular entropia
                entropy = 0
                for prob in color_probs.values():
                    if prob > 0:
                        entropy -= prob * (prob.bit_length() - 1)  # Aproximação de log2
                
                # Se entropia é muito alta (muito aleatório), rejeitar
                max_entropy = (len(color_probs) - 1).bit_length() - 1  # Entropia máxima
                if entropy > max_entropy * 0.8:  # 80% da entropia máxima
                    logger.debug(f"Padrão rejeitado: muito aleatório (entropia: {entropy:.2f})")
                    return False
            
            logger.debug("Padrão validado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar qualidade do padrão: {e}")
            return True  # Em caso de erro, aceitar o padrão
    
    def _detect_and_notify_patterns(self):
        """
        Detecta padrões nos dados atuais e gera notificações.
        Após detectar um padrão, reseta completamente o sistema para reiniciar análise.
        """
        try:
            # Verificar se deve detectar padrões agora
            if not self._should_detect_patterns():
                return
            
            # Usar dados manuais (que incluem dados do PlayNabets)
            data_to_analyze = self.manual_data if self.manual_data else self.data
            min_required = getattr(self, 'min_rounds_for_analysis', 8)
            
            # ✅ CORRIGIDO: Requisito mínimo de 8 resultados para análise confiável
            if not data_to_analyze or len(data_to_analyze) < min_required:
                logger.debug(f"Dados insuficientes para detecção de padrões: {len(data_to_analyze) if data_to_analyze else 0} resultados (mínimo: {min_required})")
                return
            
            # 📊 LOG VISUAL: Informar que está analisando padrões
            logger.info("="*60)
            logger.info(f"🔍 ANALISANDO PADRÕES: {len(data_to_analyze)} rodadas")
            logger.info(f"⏱️  Tempo desde último sinal: {int(time.time() - getattr(self, 'last_pattern_detected_at', 0))}s")
            logger.info(f"🎯 Cooldown configurado: {getattr(self, 'signal_cooldown_seconds', 180)}s (3 min)")
            logger.info("="*60)
            
            # Flag para controlar se detectou algum padrão
            pattern_detected = False
            
            # 1. Detectar padrões Double específicos
            try:
                double_patterns = self.double_pattern_detector.detect_all_patterns(data_to_analyze)
                if double_patterns and 'patterns' in double_patterns and double_patterns['patterns']:
                    for pattern_name, pattern_data in double_patterns['patterns'].items():
                        # AUMENTADO: confiança mínima de 0.6 para 0.72 (consistente com detector)
                        if pattern_data.get('confidence', 0) >= 0.72 and pattern_data.get('detected', False):
                            # Obter último número que saiu
                            last_number = 0
                            if isinstance(data_to_analyze, list) and data_to_analyze:
                                last_result = data_to_analyze[-1]
                                if isinstance(last_result, dict):
                                    last_number = last_result.get('roll', last_result.get('number', 0))
                            
                            # Usar cor predita do padrão
                            predicted_color = pattern_data.get('predicted_color', 'red')
                            
                            # Notificar padrão Double detectado
                            pattern_sent = notify_pattern(
                                pattern_type=pattern_data.get('pattern_type', pattern_name),
                                detected_number=last_number,
                                predicted_color=predicted_color,
                                confidence=pattern_data.get('confidence', 0.6),
                                reasoning=pattern_data.get('description', 'Padrão Double detectado'),
                                pattern_id=f"double_{pattern_name}_{int(time.time())}"
                            )
                            logger.info(f"Notificação de padrão Double enviada: {pattern_sent}")
                            
                            # Salvar no banco local
                            try:
                                local_db.add_pattern({
                                    'pattern_type': pattern_data.get('pattern_type', pattern_name),
                                    'detected_number': last_number,
                                    'predicted_color': predicted_color,
                                    'confidence': pattern_data.get('confidence', 0.6),
                                    'reasoning': pattern_data.get('description', ''),
                                    'risk_level': pattern_data.get('risk_level', 'medium')
                                })
                            except Exception as e:
                                logger.exception(f'Erro ao salvar padrão no banco local: {e}')
                            
                            logger.info(f"✅ Padrão Double detectado: {pattern_name} -> {predicted_color}")
                            pattern_detected = True
                            # Marcar timestamp do padrão detectado para cooldown
                            self.last_pattern_detected_at = time.time()
                            break  # Sair do loop após detectar um padrão
            except Exception as e:
                logger.exception(f'Erro ao detectar padrões Double: {e}')
            
            # 2. Detectar padrões gerais usando PatternAnalyzer
            try:
                # Obter gatilhos de padrão
                triggers = self.pattern_analyzer.get_triggers(data_to_analyze)
                
                if triggers and len(triggers) > 0:
                    # Gerar sinal baseado nos gatilhos
                    signal = self.generate_pattern_only_signal(triggers, data_to_analyze)
                    
                    if signal and signal.get('recommended_color'):
                        # Obter último número que saiu
                        last_number = 0
                        if isinstance(data_to_analyze, list) and data_to_analyze:
                            last_result = data_to_analyze[-1]
                            if isinstance(last_result, dict):
                                last_number = last_result.get('roll', last_result.get('number', 0))
                        
                        # Notificar padrão detectado
                        pattern_sent = notify_pattern(
                            pattern_type="Análise de Padrões",
                            detected_number=last_number,
                            predicted_color=signal.get('recommended_color'),
                            confidence=signal.get('confidence', 0.5),
                            reasoning=signal.get('reasoning', 'Padrão detectado por análise'),
                            pattern_id=f"pattern_{int(time.time())}"
                        )
                        
                        logger.info(f"✅ Padrão geral detectado e notificado: {signal.get('recommended_color')} (conf: {signal.get('confidence', 0):.2f}) - Enviado: {pattern_sent}")
                        pattern_detected = True
                        # Marcar timestamp do padrão detectado para cooldown
                        self.last_pattern_detected_at = time.time()
            except Exception as e:
                logger.exception(f'Erro ao detectar padrões gerais: {e}')
            
            # 3. Detectar padrões usando análise estatística simples
            try:
                # AUMENTADO: requisito mínimo para 8 resultados (análise mais robusta)
                if len(data_to_analyze) >= 8:
                    recent_data = data_to_analyze[-12:]  # Até 12 resultados
                    recent_colors = [r.get('color', '') for r in recent_data]
                    
                    # AUMENTADO: Detectar sequências de pelo menos 6 da mesma cor (padrão forte)
                    if len(set(recent_colors)) == 1 and len(recent_colors) >= 6:
                        # Sequência de mesma cor
                        color = recent_colors[0]
                        
                        # 🆕 LÓGICA DE PREDIÇÃO: Modo 'opposite' ou 'continue'
                        if self.prediction_mode == 'continue':
                            # Modo "continuar cor quente" (hot hand)
                            predicted_color = color
                            reasoning_mode = "Tendência de continuação (hot hand)"
                        else:
                            # Modo "apostar na oposta" (regressão à média)
                            predicted_color = 'black' if color == 'red' else 'red' if color in ['red', 'black'] else 'red'
                            reasoning_mode = "Tendência de inversão (regressão à média)"
                        
                        # 🆕 CONFIANÇA ADAPTATIVA baseada em histórico de acertos
                        base_confidence = 0.72  # Aumentado para 72% (mais conservador)
                        sequence_bonus = (len(recent_colors) - 6) * 0.05  # Bônus por rodadas extras
                        
                        # Ajustar confiança baseado em performance histórica
                        pattern_accuracy = self.pattern_performance['sequence']['accuracy']
                        if pattern_accuracy > 0.70:  # Se está acertando muito
                            adaptive_bonus = 0.05
                        elif pattern_accuracy < 0.50 and self.pattern_performance['sequence']['total'] > 5:
                            # Se está errando muito, reduzir confiança
                            adaptive_bonus = -0.10
                        else:
                            adaptive_bonus = 0.0
                        
                        confidence = min(0.90, base_confidence + sequence_bonus + adaptive_bonus)
                        
                        # Obter último número
                        last_number = 0
                        if recent_data:
                            last_result = recent_data[-1]
                            if isinstance(last_result, dict):
                                last_number = last_result.get('roll', last_result.get('number', 0))
                        
                        # Notificar sequência detectada
                        pattern_id = f"sequence_{int(time.time())}"
                        pattern_sent = notify_pattern(
                            pattern_type="Sequência Repetitiva",
                            detected_number=last_number,
                            predicted_color=predicted_color,
                            confidence=confidence,
                            reasoning=f"Sequência de {len(recent_colors)} {color}s consecutivos. {reasoning_mode}. Taxa de acerto histórica: {pattern_accuracy:.1%}",
                            pattern_id=pattern_id
                        )
                        
                        # 🆕 REGISTRAR NO HISTÓRICO DE SINAIS
                        self._add_to_signal_history({
                            'pattern_id': pattern_id,
                            'pattern_type': 'sequence',
                            'detected_color': color,
                            'predicted_color': predicted_color,
                            'confidence': confidence,
                            'mode': self.prediction_mode,
                            'timestamp': time.time()
                        })
                        
                        logger.info(f"✅ Sequência detectada: {len(recent_colors)} {color}s -> recomendar {predicted_color} ({self.prediction_mode}) - Enviado: {pattern_sent}")
                        pattern_detected = True
                        # Marcar timestamp do padrão detectado para cooldown
                        self.last_pattern_detected_at = time.time()
                    
                    # Se não há sequência uniforme, detectar predominância de cor
                    if len(recent_colors) >= 8:
                        color_count = {}
                        for c in recent_colors:
                            color_count[c] = color_count.get(c, 0) + 1
                        
                        # Encontrar cor predominante
                        dominant_color = max(color_count, key=color_count.get)
                        dominant_count = color_count[dominant_color]
                        
                        # AUMENTADO: predominância de 75% (muito mais seletivo)
                        if dominant_count / len(recent_colors) > 0.75:
                            # 🆕 LÓGICA DE PREDIÇÃO: Modo 'opposite' ou 'continue'
                            if self.prediction_mode == 'continue':
                                predicted_color = dominant_color
                                reasoning_mode = "Continuar na cor predominante"
                            else:
                                predicted_color = 'black' if dominant_color == 'red' else 'red' if dominant_color in ['red', 'black'] else 'red'
                                reasoning_mode = "Tendência de inversão"
                            
                            # 🆕 CONFIANÇA ADAPTATIVA
                            dominance_ratio = dominant_count / len(recent_colors)
                            base_confidence = 0.68  # Aumentado para 68%
                            dominance_bonus = (dominance_ratio - 0.75) * 2.0  # Bônus maior para dominâncias fortes
                            
                            # Ajustar baseado em performance
                            pattern_accuracy = self.pattern_performance['dominance']['accuracy']
                            if pattern_accuracy > 0.70:
                                adaptive_bonus = 0.05
                            elif pattern_accuracy < 0.50 and self.pattern_performance['dominance']['total'] > 5:
                                adaptive_bonus = -0.08
                            else:
                                adaptive_bonus = 0.0
                            
                            confidence = min(0.85, base_confidence + dominance_bonus + adaptive_bonus)
                            
                            # Obter último número
                            last_number = 0
                            if recent_data:
                                last_result = recent_data[-1]
                                if isinstance(last_result, dict):
                                    last_number = last_result.get('roll', last_result.get('number', 0))
                            
                            # Notificar padrão de predominância
                            pattern_id = f"dominance_{int(time.time())}"
                            pattern_sent = notify_pattern(
                                pattern_type="Predominância de Cor",
                                detected_number=last_number,
                                predicted_color=predicted_color,
                                confidence=confidence,
                                reasoning=f"Cor {dominant_color} apareceu {dominant_count} vezes nos últimos {len(recent_colors)} resultados ({dominance_ratio:.1%}). {reasoning_mode}. Acurácia histórica: {pattern_accuracy:.1%}",
                                pattern_id=pattern_id
                            )
                            
                            # Marcar timestamp do padrão detectado
                            self.last_pattern_detected_at = time.time()
                            
                            # 🆕 REGISTRAR NO HISTÓRICO
                            self._add_to_signal_history({
                                'pattern_id': pattern_id,
                                'pattern_type': 'dominance',
                                'detected_color': dominant_color,
                                'predicted_color': predicted_color,
                                'confidence': confidence,
                                'mode': self.prediction_mode,
                                'timestamp': time.time()
                            })
                            
                            logger.info(f"Predominância detectada e notificada: {dominant_count}/{len(recent_colors)} {dominant_color}s -> recomendar {predicted_color} ({self.prediction_mode}) - Enviado: {pattern_sent}")
                            pattern_detected = True
            except Exception as e:
                logger.exception(f'Erro ao detectar sequências: {e}')
            
            # Se detectou algum padrão, validar e resetar o sistema
            if pattern_detected:
                logger.info("="*60)
                logger.info("✅ PADRÃO DETECTADO - Validando qualidade")
                
                # Validar qualidade do padrão antes de resetar
                if self._validate_pattern_quality(data_to_analyze):
                    logger.info("✅ Padrão validado com sucesso!")
                    logger.info(f"⏸️  Próximo sinal em {getattr(self, 'signal_cooldown_seconds', 180)}s (3 min)")
                    logger.info("="*60)
                    # Registrar tempo da última detecção
                    self._last_pattern_time = time.time()
                    # ALTERADO: keep_context=False para reset TOTAL (esquecer histórico)
                    self._reset_system_after_pattern(keep_context=False)
                else:
                    logger.warning("⚠️  Padrão rejeitado por baixa qualidade - continuando análise")
                    logger.info("="*60)
            else:
                logger.info("="*60)
                logger.info("❌ Nenhum padrão detectado - continuando análise...")
                logger.info(f"📊 Analisadas {len(data_to_analyze)} rodadas (mínimo: {getattr(self, 'min_rounds_for_analysis', 8)})")
                logger.info("="*60)
            
        except Exception as e:
            logger.exception(f'Erro geral na detecção de padrões: {e}')
    
    def analyze_comprehensive(self, use_manual_data: bool = True) -> dict:
        """
        Realiza análise abrangente dos dados.
        
        Args:
            use_manual_data (bool): Se deve usar dados manuais
            
        Returns:
            dict: Análise completa
        """
        # Priorizar dados manuais (que incluem dados do PlayNabets)
        data_to_analyze = self.manual_data if self.manual_data else self.data
        
        if not data_to_analyze:
            logger.warning("Sem dados para análise")
            return {}
        
        logger.info(f"Iniciando análise abrangente de {len(data_to_analyze)} resultados")
        
        # Análise de padrões
        pattern_analysis = self.pattern_analyzer.analyze_data(data_to_analyze)
        
        # Análise de padrões Double específicos
        double_patterns = self.double_pattern_detector.detect_all_patterns(data_to_analyze)
        
        # Análise estatística
        statistical_analysis = self._perform_statistical_analysis(data_to_analyze)
        
        # Análise temporal
        temporal_analysis = self._perform_temporal_analysis(data_to_analyze)
        
        # Detectar gatilhos de padrão (usado também para ajustar predições)
        pattern_triggers = self.pattern_analyzer.get_triggers(data_to_analyze)

        # Predições (modelo)
        predictions = self._generate_predictions(data_to_analyze)

        # Se o modelo não tiver dados suficientes ou retornou erro, gerar predição heurística a partir de triggers
        if not predictions or ('error' in predictions) or not predictions.get('next_color_probabilities'):
            heuristic = self._heuristic_prediction_from_triggers(pattern_triggers, data_to_analyze)
            # only override if heuristic has useful probabilities
            if heuristic and heuristic.get('next_color_probabilities'):
                predictions = heuristic
        
        # Predição do sistema de aprendizado adaptativo
        adaptive_prediction = None
        try:
            if hasattr(self, 'adaptive_integrator') and self.adaptive_integrator:
                adaptive_prediction = self.adaptive_integrator.get_adaptive_prediction()
                if adaptive_prediction and adaptive_prediction.get('confidence', 0) > 0.5:
                    # Combinar com predições existentes se a confiança for alta
                    if predictions and adaptive_prediction.get('confidence', 0) > predictions.get('confidence', 0):
                        predictions.update({
                            'adaptive_prediction': adaptive_prediction,
                            'combined_confidence': (predictions.get('confidence', 0) + adaptive_prediction.get('confidence', 0)) / 2
                        })
        except Exception:
            logger.exception('Erro ao obter predição adaptativa')
        
        # Análise de sequências
        sequence_analysis = self._analyze_sequences(data_to_analyze)

        # Ajustar predições usando informação dos gatilhos (se houver)
        adjusted_predictions = self._adjust_prediction_with_triggers(predictions, pattern_triggers)

        # identificar gatilhos fortes (para sinalização rápida)
        strong_triggers = []
        try:
            for t in pattern_triggers or []:
                name = (t.get('nome') or t.get('name') or '').lower()
                meta = t.get('meta') or {}
                if 'sequência' in name or 'sequencia' in name:
                    length = int(meta.get('length', 0) or 0)
                    if length >= 5:
                        strong_triggers.append(t)
                if 'branco isca' in name or 'branco' in name:
                    strong_triggers.append(t)
        except Exception:
            pass

        comprehensive_analysis = {
            'timestamp': datetime.now().isoformat(),
            'data_source': 'manual' if use_manual_data else 'api',
            'total_results': len(data_to_analyze),
            'pattern_analysis': pattern_analysis,
            'double_patterns': double_patterns,
            'statistical_analysis': statistical_analysis,
            'temporal_analysis': temporal_analysis,
            'predictions': adjusted_predictions,
            'sequence_analysis': sequence_analysis,
            'recommendations': self._generate_recommendations(data_to_analyze),
            'pattern_triggers': pattern_triggers,
            'strong_triggers': strong_triggers
        }
        
        # Cache da análise
        self.analysis_cache = comprehensive_analysis
        
        # Detectar padrões após análise
        try:
            self._detect_and_notify_patterns()
        except Exception as e:
            logger.exception(f'Erro ao detectar padrões após análise: {e}')
        
        logger.info("Análise abrangente concluída")
        return comprehensive_analysis

    def _adjust_prediction_with_triggers(self, predictions: dict, triggers: list) -> dict:
        """
        Ajusta as predições do modelo com base em gatilhos detectados pelo PatternAnalyzer.

        Regras simples aplicadas (heurísticas):
        - Sequência Repetitiva (streak >=4): aumenta a probabilidade da cor oposta e sugere-a com confiança maior.
        - Branco Isca: aumenta chance de branco nas próximas 1-2 rodadas.
        - Padrão 2x2/3x3/Espelhado: aplicar pequeno ajuste na cor que costuma romper o bloco.

        Essa função retorna um dicionário compatível com o formato retornado por _generate_predictions().
        """
        try:
            if not predictions or ('error' in predictions):
                return predictions

            # clone para não modificar original
            preds = {
                'next_color_probabilities': dict(predictions.get('next_color_probabilities', {})),
                'recommended_color': predictions.get('recommended_color'),
                'confidence': float(predictions.get('confidence', 0.0)),
                'reasoning': predictions.get('reasoning', '')
            }

            # Se não há triggers, retorna sem alterações
            if not triggers:
                return preds

            # heurística: mapa de cores opostas (para sequências)
            opposite = {'red': 'black', 'black': 'red'}

            # fatores de ajuste
            boost_large = 0.20
            boost_small = 0.08

            for t in triggers:
                name = (t.get('nome') or t.get('name') or '').lower()
                meta = t.get('meta') or {}

                if 'sequência repetitiva' in name or 'sequencia repetitiva' in name:
                    col = meta.get('color') or None
                    length = int(meta.get('length', 0) or 0)
                    if col in opposite:
                        opp = opposite[col]
                        # reforçar probabilidade da cor oposta
                        preds['next_color_probabilities'][opp] = preds['next_color_probabilities'].get(opp, 0.0) + (boost_large if length >= 6 else boost_small)
                        preds['recommended_color'] = opp
                        preds['confidence'] = min(0.99, preds.get('confidence', 0.0) + (0.15 if length >= 6 else 0.07))

                if 'branco isca' in name or 'branco' in name:
                    # dar preferência ao branco por curto prazo
                    preds['next_color_probabilities']['white'] = preds['next_color_probabilities'].get('white', 0.0) + boost_small
                    if preds['next_color_probabilities'].get('white', 0) >= max(preds['next_color_probabilities'].values()):
                        preds['recommended_color'] = 'white'
                        preds['confidence'] = max(preds['confidence'], 0.5)

                if '2x2' in name or '2x2' in (t.get('gatilho') or '').lower():
                    # pequeno ajuste para padrão 2x2
                    preds['confidence'] = min(0.9, preds['confidence'] + 0.04)

                if '3x3' in name or '3x3' in (t.get('gatilho') or '').lower():
                    preds['confidence'] = min(0.95, preds['confidence'] + 0.08)

            # normalizar probabilidades para soma 1 quando possível
            probs = preds.get('next_color_probabilities', {})
            total = sum(probs.values())
            if total > 0:
                for k in list(probs.keys()):
                    probs[k] = max(0.0, probs[k]) / total
                preds['next_color_probabilities'] = probs

            # garantir recommended_color coerente com probs
            if not preds.get('recommended_color') and probs:
                preds['recommended_color'] = max(probs.keys(), key=lambda k: probs.get(k, 0.0))

            return preds
        except Exception:
            return predictions

    def _heuristic_prediction_from_triggers(self, triggers: list, data: list) -> dict:
        """
        Gera uma predição heurística baseada apenas nos gatilhos detectados.

        Retorna um dicionário com a mesma forma de _generate_predictions():
        {
           'next_color_probabilities': {'red': float, 'black': float, 'white': float},
           'recommended_color': 'red'|'black'|'white'|'none',
           'confidence': float,
           'reasoning': str
        }
        """
        # Prioridade de gatilhos (mais forte primeiro)
        try:
            if not triggers:
                return {'next_color_probabilities': {}, 'recommended_color': None, 'confidence': 0.0, 'reasoning': 'Sem gatilhos'}

            # helpers
            def base_probs(rec, strength):
                # rec receives majority probability depending on strength
                rec = rec or 'red'
                others = [c for c in ('red', 'black', 'white') if c != rec]
                main = min(0.85, 0.45 + strength)
                rem = 1.0 - main
                return {rec: main, others[0]: rem*0.6, others[1]: rem*0.4}

            # Escolher gatilho mais prioritário
            priority = ['sequência repetitiva', 'sequencia repetitiva', 'branco isca', '3x3', '2x2', 'espelhado', 'alternância', 'quente/fri']
            chosen = None
            chosen_meta = {}
            chosen_name = ''
            for p in priority:
                for t in triggers:
                    name = (t.get('nome') or t.get('name') or '').lower()
                    if p in name:
                        chosen = p
                        chosen_meta = t.get('meta') or {}
                        chosen_name = name
                        break
                if chosen:
                    break

            reasoning = f'Heurística baseada no gatilho: {chosen_name}' if chosen else 'Sem gatilho prioritário'

            if chosen in ('sequência repetitiva', 'sequencia repetitiva'):
                col = chosen_meta.get('color')
                length = int(chosen_meta.get('length', 0) or 0)
                # sugerir a cor oposta (aqui white tratado separadamente)
                if col == 'white':
                    rec = 'red'  # fallback
                else:
                    rec = 'black' if col == 'red' else 'red'
                strength = max(0.2, min(0.5, (length - 3) * 0.08))
                probs = base_probs(rec, strength)
                conf = min(0.9, 0.4 + strength)
                return {'next_color_probabilities': probs, 'recommended_color': rec, 'confidence': conf, 'reasoning': reasoning}

            if chosen == 'branco isca' or 'branco' in chosen_name:
                probs = base_probs('white', 0.25)
                conf = 0.45
                return {'next_color_probabilities': probs, 'recommended_color': 'white', 'confidence': conf, 'reasoning': reasoning}

            if chosen == '3x3':
                # recomendar cor inversa do primeiro bloco
                pattern = chosen_meta.get('pattern') or []
                if pattern and len(pattern) >= 1:
                    first = pattern[0]
                    rec = 'black' if first == 'red' else 'red' if first in ('red','black') else 'red'
                else:
                    rec = 'red'
                probs = base_probs(rec, 0.22)
                return {'next_color_probabilities': probs, 'recommended_color': rec, 'confidence': 0.48, 'reasoning': reasoning}

            if chosen == '2x2' or '2x2' in chosen_name:
                # leve preferência para cor que costuma romper o bloco (assumir oposto ao primeiro)
                pat = chosen_meta.get('pattern') or chosen_meta.get('pattern', [])
                rec = None
                if isinstance(pat, list) and len(pat) >= 1:
                    first = pat[0]
                    rec = 'black' if first == 'red' else 'red' if first in ('red','black') else 'red'
                else:
                    rec = 'red'
                probs = base_probs(rec, 0.12)
                return {'next_color_probabilities': probs, 'recommended_color': rec, 'confidence': 0.38, 'reasoning': reasoning}

            if 'espelhado' in chosen_name:
                probs = base_probs('white', 0.10)
                return {'next_color_probabilities': probs, 'recommended_color': 'white', 'confidence': 0.32, 'reasoning': reasoning}

            if 'alternância' in chosen_name:
                # sugerir oposto do último conhecido com baixa confiança
                last_color = None
                if data:
                    last_color = data[-1].get('color')
                rec = None
                if last_color in ('red','black'):
                    rec = 'black' if last_color == 'red' else 'red'
                else:
                    rec = 'red'
                probs = base_probs(rec, 0.05)
                return {'next_color_probabilities': probs, 'recommended_color': rec, 'confidence': 0.28, 'reasoning': reasoning}

            # fallback: retornar vazios
            return {'next_color_probabilities': {}, 'recommended_color': None, 'confidence': 0.0, 'reasoning': 'Fallback: sem heurística aplicável'}
        except Exception:
            return {'next_color_probabilities': {}, 'recommended_color': None, 'confidence': 0.0, 'reasoning': 'Erro ao gerar heurística'}

    def generate_pattern_only_signal(self, triggers: list, data: list, avoid_color: str = None) -> dict:
        """
        Gera um sinal/preview baseado APENAS em gatilhos (sem usar modelo estatístico).
        Persiste a previsão no DB com method='pattern_only' e retorna o objeto gravado.
        """
        try:
            heuristic = self._heuristic_prediction_from_triggers(triggers, data)
            if not heuristic or not heuristic.get('recommended_color'):
                return {}

            rec = heuristic.get('recommended_color')
            conf = float(heuristic.get('confidence', 0.0) or 0.0)

            # avoid recommending same color repeatedly within a short cooldown
            try:
                now = time.time()
                cooldown = getattr(self, 'signal_cooldown_seconds', 3)
                # if the same color was recommended very recently, skip
                if self.last_recommended_color and rec and str(self.last_recommended_color).lower() == str(rec).lower():
                    if now - getattr(self, 'last_signal_ts', 0) < cooldown:
                        logger.debug('Pulando geração: mesma cor recomendada muito recentemente')
                        return {}
                # also, if there is a pending prediction in DB, avoid creating another automatic one
                try:
                    db = getattr(self, 'db_manager', None)
                    if db:
                        pending = db.get_last_unverified_prediction()
                        if pending is not None:
                            logger.debug('Pulando geração: já existe previsão pendente no DB (id=%s)', pending.get('id'))
                            return {}
                except Exception:
                    pass
            except Exception:
                pass

            # if caller requested to avoid a specific color (usually the previously
            # suggested one), attempt to pick an alternative recommendation to
            # prevent repeating the exact same signal
            if avoid_color and rec and str(rec).lower() == str(avoid_color).lower():
                try:
                    probs = heuristic.get('next_color_probabilities', {}) or {}
                    # sort candidates by probability desc and pick first that isn't avoid_color
                    candidates = sorted(probs.items(), key=lambda x: x[1], reverse=True)
                    alt = None
                    for c, p in candidates:
                        if str(c).lower() != str(avoid_color).lower() and p and p > 0:
                            alt = (c, p)
                            break
                    if alt:
                        rec = alt[0]
                        conf = float(alt[1])
                    else:
                        # fallback heuristic: invert red<->black if possible
                        if str(avoid_color).lower() in ('red', 'black'):
                            rec = 'black' if str(avoid_color).lower() == 'red' else 'red'
                            # conservative confidence for fallback
                            conf = max(0.2, min(0.6, 1.0 - heuristic.get('confidence', 0.0)))
                        else:
                            # no reasonable alternative found
                            return {}
                except Exception:
                    # if anything fails, avoid returning the same recommendation
                    return {}
            # record last recommendation/time
            try:
                if rec:
                    self.last_recommended_color = rec
                    self.last_signal_ts = time.time()
            except Exception:
                pass
            db = getattr(self, 'db_manager', None)
            pred_id = None
            if db:
                # checar a previsão mais recente no DB para evitar duplicação
                try:
                    recent = db.get_recent_predictions(1) or []
                    if recent:
                        last = recent[0]
                        try:
                            # created_at pode ser string; não confiar demais no formato
                            # comparar cor e tempo
                            last_color = (last.get('prediction_color') or '').strip().lower()
                            now = time.time()
                            # tentar converter created_at para timestamp aproximado
                            last_ts = None
                            try:
                                import dateutil.parser as dp
                                last_ts = dp.parse(last.get('created_at')).timestamp()
                            except Exception:
                                try:
                                    # created_at pode ser formato YYYY-MM-DD HH:MM:SS
                                    from datetime import datetime
                                    last_ts = datetime.strptime(last.get('created_at'), '%Y-%m-%d %H:%M:%S').timestamp()
                                except Exception:
                                    last_ts = None

                            if last_color and last_color == str(rec).lower() and last_ts and (now - last_ts) < getattr(self, 'signal_cooldown_seconds', 10):
                                logger.debug('Pulando persistência: última previsão recente com mesma cor (id=%s)', last.get('id'))
                                return {'recommended_color': rec, 'confidence': conf, 'reasoning': heuristic.get('reasoning'), 'db_id': last.get('id')}
                        except Exception:
                            pass
                except Exception:
                    pass

                pred = {
                    'result_id': None,
                    'color': rec,
                    'confidence': conf,
                    'method': 'pattern_only',
                    'correct': None
                }
                try:
                    pred_id = db.insert_prediction(pred)
                except Exception:
                    logger.exception('Erro ao persistir previsão pattern_only')
                # notificar callbacks registrados que uma nova previsão foi criada
                try:
                    if pred_id and hasattr(self, '_notify_prediction_update'):
                        # pred_id retornado pelo DB é um inteiro; informar correct=None/result_id=None
                        try:
                            self._notify_prediction_update(pred_id, None, None)
                        except Exception:
                            logger.exception('Erro ao notificar callbacks após inserir previsão')
                except Exception:
                    pass

            # enviar alerta se a confiança for maior que 50%
            try:
                if pred_id and hasattr(self, 'alert_system') and self.alert_system and float(conf) > 0.5:
                    try:
                        payload = {
                            'db_id': pred_id,
                            'color': rec,
                            'confidence': conf,
                            'method': 'pattern_only',
                            'pattern_triggers': triggers,
                            'reasoning': heuristic.get('reasoning'),
                            'message': f"Sinal AUTO (pattern_only): {str(rec).upper()} (conf={conf:.2f}) id={pred_id}"
                        }
                        # tentar incluir número do último resultado disponível
                        try:
                            last = None
                            if isinstance(data, list) and data:
                                last = data[-1]
                            elif hasattr(self, 'data') and isinstance(getattr(self, 'data'), list) and getattr(self, 'data'):
                                last = getattr(self, 'data')[-1]
                            if last and isinstance(last, dict):
                                if 'roll' in last:
                                    payload['roll'] = int(last.get('roll'))
                                elif 'number' in last:
                                    payload['roll'] = int(last.get('number'))
                        except Exception:
                            pass

                        self._send_validated_alert(payload)
                    except Exception:
                        logger.exception('Erro ao enviar alerta ao gerar sinal pattern_only')
            except Exception:
                pass

            return {'recommended_color': rec, 'confidence': conf, 'reasoning': heuristic.get('reasoning'), 'db_id': pred_id}
        except Exception:
            logger.exception('Erro ao gerar sinal pattern-only')
            return {}

    def suggest_next_color_from_db(self, window: int = 100) -> str:
        """
        Wrapper que carrega os últimos resultados do DB e usa PatternAnalyzer.suggest_next_color
        para retornar a sugestão formatada.
        """
        try:
            results = self.db_manager.get_recent_results(window)
            return self.pattern_analyzer.suggest_next_color(results)
        except Exception as e:
            logger.exception('Erro ao gerar sugestão a partir do DB')
            return 'Sugestão: não apostar\nFundamento: erro ao processar os dados.'
    
    def _perform_statistical_analysis(self, data: list) -> dict:
        """Realiza análise estatística dos dados."""
        colors = [result.get('color', '') for result in data]
        numbers = [result.get('roll', 0) for result in data]
        
        # Distribuição de cores
        color_distribution = {}
        for color in ['red', 'black', 'white']:
            count = colors.count(color)
            color_distribution[color] = {
                'count': count,
                'percentage': (count / len(colors)) * 100 if colors else 0
            }
        
        # Distribuição de números
        number_distribution = {}
        for num in range(15):
            count = numbers.count(num)
            if count > 0:
                number_distribution[num] = count
        
        # Estatísticas básicas
        stats = {
            'color_distribution': color_distribution,
            'number_distribution': number_distribution,
            'most_frequent_color': max(color_distribution.keys(), key=lambda k: color_distribution[k]['count']),
            'most_frequent_number': max(number_distribution.keys(), key=lambda k: number_distribution[k]) if number_distribution else 0,
            'total_games': len(data)
        }
        
        return stats
    
    def _perform_temporal_analysis(self, data: list) -> dict:
        """Realiza análise temporal dos dados."""
        if not data:
            return {}
        
        # Agrupar por hora do dia
        hourly_distribution = {}
        for result in data:
            if 'timestamp' in result:
                hour = datetime.fromtimestamp(result['timestamp']).hour
                if hour not in hourly_distribution:
                    hourly_distribution[hour] = {'red': 0, 'black': 0, 'white': 0}
                hourly_distribution[hour][result.get('color', 'unknown')] += 1
        
        return {
            'hourly_distribution': hourly_distribution,
            'peak_hours': sorted(hourly_distribution.keys(), key=lambda h: sum(hourly_distribution[h].values()), reverse=True)[:3]
        }
    
    def _generate_predictions(self, data: list) -> dict:
        """Gera predições baseadas nos dados."""
        if len(data) < 10:
            return {'error': 'Dados insuficientes para predições'}
        
        # Atualizar modelo com dados recentes
        self.prediction_model.update_history(data[-20:])  # Era 50, agora 20
        
        # Gerar predições
        predictions = self.prediction_model.predict_next_color()
        
        # Adicionar confiança baseada em padrões
        confidence = self._calculate_prediction_confidence(data)
        
        # Verificar se há gatilhos de alerta
        if hasattr(self, 'alert_system') and self.alert_system:
            recommended_color = max(predictions.keys(), key=lambda k: predictions[k])
            if confidence >= self.alert_system.config.get('min_confidence', 0.7):
                try:
                    payload = {
                        'color': recommended_color,
                        'confidence': confidence,
                        'method': 'model',
                        'message': f"Alerta: Apostar em {recommended_color.upper()} (Confiança: {confidence:.1%})"
                    }
                    # tentar anexar último número conhecido ao payload
                    try:
                        last = None
                        if isinstance(data, list) and data:
                            last = data[-1]
                        elif hasattr(self, 'data') and isinstance(getattr(self, 'data'), list) and getattr(self, 'data'):
                            last = getattr(self, 'data')[-1]
                        if last and isinstance(last, dict):
                            if 'roll' in last:
                                payload['roll'] = int(last.get('roll'))
                            elif 'number' in last:
                                payload['roll'] = int(last.get('number'))
                    except Exception:
                        pass

                    self.alert_system.send_alert(payload)
                except Exception:
                    logger.exception('Erro ao enviar alerta do modelo')
        
        # Verificar padrões Double específicos
        try:
            double_patterns = self.double_pattern_detector.detect_all_patterns(data)
            if double_patterns and 'patterns' in double_patterns and len(data) >= 10:
                for pattern_name, pattern_data in double_patterns['patterns'].items():
                    if pattern_data.get('confidence', 0) >= 0.65 and pattern_data.get('detected', False):
                        # Obter último número que saiu
                        last_number = 0
                        if isinstance(data, list) and data:
                            last_result = data[-1]
                            if isinstance(last_result, dict):
                                last_number = last_result.get('roll', last_result.get('number', 0))
                        
                        # Usar cor predita do padrão se disponível
                        predicted_color = pattern_data.get('predicted_color', recommended_color)
                        
                        # Notificar padrão Double detectado
                        notify_pattern(
                            pattern_type=pattern_data.get('pattern_type', pattern_name),
                            detected_number=last_number,
                            predicted_color=predicted_color,
                            confidence=pattern_data.get('confidence', 0.6),
                            reasoning=pattern_data.get('description', 'Padrão Double detectado'),
                            pattern_id=f"double_{pattern_name}_{int(time.time())}"
                        )
                        
                        # Salvar no banco local
                        local_db.add_pattern({
                            'pattern_type': pattern_data.get('pattern_type', pattern_name),
                            'detected_number': last_number,
                            'predicted_color': predicted_color,
                            'confidence': pattern_data.get('confidence', 0.6),
                            'reasoning': pattern_data.get('description', ''),
                            'risk_level': pattern_data.get('risk_level', 'medium')
                        })
        except Exception as e:
            logger.exception(f'Erro ao processar padrões Double: {e}')
        
        # Notificar padrão geral se não houver padrões Double específicos
        # Só notificar padrão geral se não houver padrões Double específicos E confiança for alta
        if not (double_patterns and 'patterns' in double_patterns and double_patterns['patterns']) and len(data) >= 15:
            recommended_color = max(predictions.keys(), key=lambda k: predictions[k])
            # Aumentar confiança mínima para 70% para evitar spam
            if confidence >= 0.70:  
                try:
                    # Obter último número que saiu
                    last_number = 0
                    if isinstance(data, list) and data:
                        last_result = data[-1]
                        if isinstance(last_result, dict):
                            last_number = last_result.get('roll', last_result.get('number', 0))
                    
                    # Notificar padrão detectado apenas com alta confiança
                    notify_pattern(
                        pattern_type="Análise de Padrões",
                        detected_number=last_number,
                        predicted_color=recommended_color,
                        confidence=confidence,
                        reasoning=self._generate_reasoning(data, predictions),
                        pattern_id=f"pattern_{int(time.time())}"
                    )
                except Exception as e:
                    logger.exception(f'Erro ao notificar padrão: {e}')
        
        return {
            'next_color_probabilities': predictions,
            'recommended_color': max(predictions.keys(), key=lambda k: predictions[k]),
            'confidence': confidence,
            'reasoning': self._generate_reasoning(data, predictions)
        }
    
    def _calculate_prediction_confidence(self, data: list) -> float:
        """Calcula a confiança das predições."""
        if len(data) < 20:
            return 0.5
        
        # Análise de sequências recentes
        recent_colors = [result.get('color', '') for result in data[-10:]]
        
        # Calcular estabilidade dos padrões
        color_changes = sum(1 for i in range(1, len(recent_colors)) if recent_colors[i] != recent_colors[i-1])
        stability = 1 - (color_changes / len(recent_colors))
        
        return min(stability + 0.3, 0.9)  # Confiança entre 0.3 e 0.9
    
    def _generate_reasoning(self, data: list, predictions: dict) -> str:
        """Gera explicação para as predições."""
        recent_data = data[-10:] if len(data) >= 10 else data
        recent_colors = [result.get('color', '') for result in recent_data]
        
        # Análise de sequências
        last_color = recent_colors[-1] if recent_colors else 'unknown'
        color_count = {}
        for color in recent_colors:
            color_count[color] = color_count.get(color, 0) + 1
        
        # Gerar explicação
        reasoning = f"Baseado nos últimos {len(recent_data)} resultados: "
        
        if len(set(recent_colors)) == 1:
            reasoning += f"Sequência de {len(recent_colors)} {last_color}s consecutivos. "
        else:
            reasoning += f"Último resultado: {last_color}. "
        
        reasoning += f"Distribuição recente: {dict(color_count)}. "
        
        recommended = max(predictions.keys(), key=lambda k: predictions[k])
        reasoning += f"Recomendação: {recommended} (probabilidade: {predictions[recommended]:.1%})."
        
        return reasoning
    
    def _analyze_sequences(self, data: list) -> dict:
        """Analisa sequências nos dados."""
        colors = [result.get('color', '') for result in data]
        
        sequences = []
        current_sequence = {'color': colors[0], 'length': 1} if colors else None
        
        for i in range(1, len(colors)):
            if colors[i] == current_sequence['color']:
                current_sequence['length'] += 1
            else:
                sequences.append(current_sequence.copy())
                current_sequence = {'color': colors[i], 'length': 1}
        
        if current_sequence:
            sequences.append(current_sequence)
        
        # Encontrar sequências mais longas
        longest_sequences = sorted(sequences, key=lambda x: x['length'], reverse=True)[:5]
        
        return {
            'current_sequence': sequences[-1] if sequences else None,
            'longest_sequences': longest_sequences,
            'total_sequences': len(sequences)
        }
    
    def _generate_recommendations(self, data: list) -> dict:
        """Gera recomendações baseadas na análise."""
        if len(data) < 10:
            return {'warning': 'Dados insuficientes para recomendações'}
        
        recommendations = {
            'betting_strategy': self._suggest_betting_strategy(data),
            'risk_level': self._assess_risk_level(data),
            'timing': self._suggest_timing(data),
            'warnings': self._generate_warnings(data)
        }
        
        return recommendations
    
    def _suggest_betting_strategy(self, data: list) -> str:
        """Sugere estratégia de apostas."""
        recent_colors = [result.get('color', '') for result in data[-12:]]

        # Se todos os resultados recentes forem da mesma cor, contrapor
        if recent_colors and len(set(recent_colors)) == 1:
            lone = recent_colors[-1]
            return f"Sequência uniforme de {lone}. Considere apostar na cor oposta."

        # Tentar usar PatternAnalyzer para detectar padrões que preveem o próximo resultado
        try:
            pattern_info = self.pattern_analyzer._find_patterns(recent_colors)
        except Exception:
            pattern_info = None

        # pattern_info devolve padrões por tamanho; procurar padrões que ocorram e usar o
        # elemento que seguiu essas ocorrências para recomendar
        if pattern_info:
            from collections import Counter
            suggestions = Counter()
            # Para cada padrão encontrado, tentar inferir o próximo elemento
            for length, patterns in pattern_info.items():
                for pat_str, count in patterns.items():
                    # Converter string de padrão para lista
                    try:
                        # padrão salvo como "('red', 'black', ...)"
                        pat = eval(pat_str)
                    except Exception:
                        continue
                    # se o padrão aparece ao menos 2 vezes, tentar usar o que segue ele
                    if count >= 2 and len(pat) >= 2:
                        # o padrão completo pode incluir o próximo elemento em outra ocorrência
                        # contaremos a última cor do padrão como sinal
                        suggestions[pat[-1]] += count

            if suggestions:
                recommended = suggestions.most_common(1)[0][0]
                return f"Padrão detectado. Considere apostar em {recommended}."

        # Fallback: apostar na cor que menos apareceu nos últimos 12
        color_counts = {c: recent_colors.count(c) for c in ('red', 'black', 'white')}
        min_color = min(color_counts.keys(), key=lambda k: color_counts[k])
        return f"Distribuição recente desigual. Considere apostar em {min_color} (menos frequente)."
    
    def _assess_risk_level(self, data: list) -> str:
        """Avalia o nível de risco."""
        if len(data) < 20:
            return "ALTO - Dados insuficientes"
        
        # Calcular variabilidade
        recent_colors = [result.get('color', '') for result in data[-20:]]
        color_variety = len(set(recent_colors))
        
        if color_variety >= 3:
            return "MÉDIO - Distribuição equilibrada"
        elif color_variety == 2:
            return "ALTO - Distribuição desequilibrada"
        else:
            return "MUITO ALTO - Sequência uniforme"
    
    def _suggest_timing(self, data: list) -> str:
        """Sugere timing para apostas."""
        return "Considere apostar quando houver pelo menos 10 resultados para análise."
    
    def _generate_warnings(self, data: list) -> list:
        """Gera avisos baseados nos dados."""
        warnings = []
        
        if len(data) < 10:
            warnings.append("[AVISO] Poucos dados para análise confiável")
        
        recent_colors = [result.get('color', '') for result in data[-5:]]
        if len(set(recent_colors)) == 1 and len(recent_colors) >= 4:
            warnings.append(f"[AVISO] Sequência de {len(recent_colors)} {recent_colors[0]}s consecutivos")
        
        warnings.append("[AVISO] Lembre-se: jogos de azar são aleatórios")
        warnings.append("[AVISO] Aposte com responsabilidade")
        
        return warnings
    
    def plot_enhanced_analysis(self, save_path: str = None):
        """Cria gráficos avançados da análise."""
        if not self.analysis_cache:
            logger.warning("Nenhuma análise disponível para plotar")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Análise Avançada do Double da Blaze', fontsize=16)
        
        # Gráfico 1: Distribuição de cores
        color_dist = self.analysis_cache['statistical_analysis']['color_distribution']
        colors = list(color_dist.keys())
        counts = [color_dist[color]['count'] for color in colors]
        
        axes[0, 0].bar(colors, counts, color=['red', 'black', 'green'])
        axes[0, 0].set_title('Distribuição de Cores')
        axes[0, 0].set_ylabel('Frequência')
        
        # Gráfico 2: Distribuição temporal
        if 'temporal_analysis' in self.analysis_cache:
            hourly_dist = self.analysis_cache['temporal_analysis']['hourly_distribution']
            if hourly_dist:
                hours = list(hourly_dist.keys())
                red_counts = [hourly_dist[h]['red'] for h in hours]
                black_counts = [hourly_dist[h]['black'] for h in hours]
                white_counts = [hourly_dist[h]['white'] for h in hours]
                
                axes[0, 1].plot(hours, red_counts, 'r-', label='Vermelho')
                axes[0, 1].plot(hours, black_counts, 'k-', label='Preto')
                axes[0, 1].plot(hours, white_counts, 'g-', label='Branco')
                axes[0, 1].set_title('Distribuição por Hora')
                axes[0, 1].set_xlabel('Hora')
                axes[0, 1].set_ylabel('Frequência')
                axes[0, 1].legend()
        
        # Gráfico 3: Probabilidades de predição
        if 'predictions' in self.analysis_cache:
            predictions = self.analysis_cache['predictions']['next_color_probabilities']
            colors = list(predictions.keys())
            probs = list(predictions.values())
            
            axes[1, 0].pie(probs, labels=colors, autopct='%1.1f%%', colors=['red', 'black', 'green'])
            axes[1, 0].set_title('Probabilidades de Próxima Cor')
        
        # Gráfico 4: Sequências
        if 'sequence_analysis' in self.analysis_cache:
            seq_analysis = self.analysis_cache['sequence_analysis']
            if seq_analysis.get('longest_sequences'):
                sequences = seq_analysis['longest_sequences'][:5]
                seq_labels = [f"{seq['color']} ({seq['length']})" for seq in sequences]
                seq_lengths = [seq['length'] for seq in sequences]
                
                axes[1, 1].bar(range(len(seq_lengths)), seq_lengths)
                axes[1, 1].set_title('Sequências Mais Longas')
                axes[1, 1].set_ylabel('Comprimento')
                axes[1, 1].set_xticks(range(len(seq_labels)))
                axes[1, 1].set_xticklabels(seq_labels, rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {save_path}")
        
        plt.show()
    
    def export_analysis(self, filename: str = None) -> str:
        """Exporta a análise para um arquivo JSON."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'blaze_analysis_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_cache, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Análise exportada para: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erro ao exportar análise: {str(e)}")
            return None
    
    def clear_data(self):
        """Limpa todos os dados."""
        self.data = []
        self.manual_data = []
        self.analysis_cache = {}
        logger.info("Todos os dados foram limpos")

def main():
    """Função principal do analisador melhorado."""
    print("=== BLAZE DOUBLE ANALYZER ENHANCED ===")
    print("Versão melhorada com integração à API oficial do Blaze")
    print()
    
    # Inicializar analisador
    api_key = input("Digite sua API key do Blaze (ou Enter para usar dados simulados): ").strip()
    analyzer = BlazeAnalyzerEnhanced(api_key=api_key if api_key else None)
    
    print("\nOpções disponíveis:")
    print("1. Obter dados da API oficial")
    print("2. Inserir dados manualmente")
    print("3. Análise abrangente")
    print("4. Visualizar gráficos")
    print("5. Exportar análise")
    print("0. Sair")
    
    while True:
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            print("Obtendo dados da API...")
            data = analyzer.fetch_recent_data(20)  # Era 50
            if data:
                print(f"Obtidos {len(data)} resultados")
            else:
                print("Nenhum dado obtido")
        
        elif choice == "2":
            print("=== INSERÇÃO MANUAL ===")
            print("Digite números de 0-14 (ou 'sair' para voltar)")
            
            while True:
                entry = input("Número: ").strip()
                if entry.lower() == 'sair':
                    break
                
                try:
                    number = int(entry)
                    if 0 <= number <= 14:
                        analyzer.add_manual_result(number)
                    else:
                        print("Número deve estar entre 0 e 14")
                except ValueError:
                    print("Entrada inválida")
        
        elif choice == "3":
            print("Realizando análise abrangente...")
            use_manual = input("Usar dados manuais? (s/n): ").lower() == 's'
            analysis = analyzer.analyze_comprehensive(use_manual_data=use_manual)
            
            if analysis:
                print("\n=== ANÁLISE ABRANGENTE ===")
                print(f"Total de resultados: {analysis['total_results']}")
                
                # Mostrar estatísticas
                stats = analysis['statistical_analysis']
                print(f"\nCor mais frequente: {stats['most_frequent_color']}")
                print(f"Número mais frequente: {stats['most_frequent_number']}")
                
                # Mostrar predições
                if 'predictions' in analysis:
                    pred = analysis['predictions']
                    print(f"\nPróxima cor recomendada: {pred['recommended_color']}")
                    print(f"Confiança: {pred['confidence']:.1%}")
                    print(f"Raciocínio: {pred['reasoning']}")
                
                # Mostrar recomendações
                rec = analysis['recommendations']
                print(f"\nEstratégia de apostas: {rec['betting_strategy']}")
                print(f"Nível de risco: {rec['risk_level']}")
                
                # Mostrar avisos
                if 'warnings' in rec:
                    print("\nAvisos:")
                    for warning in rec['warnings']:
                        print(f"  {warning}")
        
        elif choice == "4":
            print("Gerando gráficos...")
            analyzer.plot_enhanced_analysis('blaze_analysis_enhanced.png')
        
        elif choice == "5":
            filename = analyzer.export_analysis()
            if filename:
                print(f"Análise exportada para: {filename}")
        
        elif choice == "0":
            print("Encerrando programa...")
            break
        
        else:
            print("Opção inválida")

if __name__ == "__main__":
    main()
