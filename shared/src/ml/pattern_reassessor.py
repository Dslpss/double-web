#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Reavaliação de Padrões para o Double da Blaze.
Reinicia a análise de padrões após cada validação de predição.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)

class ReassessmentTrigger(Enum):
    """Gatilhos para reavaliação de padrões."""
    PREDICTION_VALIDATED = "prediction_validated"
    PATTERN_BROKEN = "pattern_broken"
    NEW_SEQUENCE_STARTED = "new_sequence_started"
    PERFORMANCE_DROP = "performance_drop"
    TIME_BASED = "time_based"

@dataclass
class ReassessmentEvent:
    """Evento de reavaliação."""
    event_id: str
    trigger: ReassessmentTrigger
    timestamp: datetime
    context: Dict[str, Any]
    previous_patterns: List[str]
    new_patterns: List[str] = None
    reassessment_duration: float = 0.0

class PatternReassessor:
    """
    Sistema de reavaliação de padrões que reinicia análise após validações.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o reavaliador de padrões.
        
        Args:
            config: Configurações do reavaliador
        """
        self.config = config or {}
        
        # Configurações
        self.auto_reassess = self.config.get('auto_reassess', True)
        self.reassess_after_validation = self.config.get('reassess_after_validation', True)
        self.reassess_after_pattern_break = self.config.get('reassess_after_pattern_break', True)
        self.min_data_for_reassessment = self.config.get('min_data_for_reassessment', 10)
        self.reassessment_cooldown = timedelta(seconds=self.config.get('reassessment_cooldown_seconds', 30))
        
        # Estado
        self.is_reassessing = False
        self.last_reassessment = None
        self.reassessment_count = 0
        
        # Histórico de reavaliações
        self.reassessment_history: List[ReassessmentEvent] = []
        
        # Callbacks para diferentes sistemas
        self.reassessment_callbacks = {
            'pattern_analyzer': [],
            'dual_pattern_detector': [],
            'adaptive_learner': [],
            'prediction_validator': []
        }
        
        # Controle de thread
        self.reassessment_thread = None
        self.stop_reassessment = False
        
        logger.info("PatternReassessor inicializado")
    
    def register_callback(self, system_name: str, callback: callable) -> None:
        """
        Registra callback para um sistema específico.
        
        Args:
            system_name: Nome do sistema ('pattern_analyzer', 'dual_pattern_detector', etc.)
            callback: Função callback
        """
        if system_name in self.reassessment_callbacks:
            self.reassessment_callbacks[system_name].append(callback)
            logger.info(f"Callback registrado para sistema: {system_name}")
        else:
            logger.warning(f"Sistema desconhecido para callback: {system_name}")
    
    def trigger_reassessment(self, trigger: ReassessmentTrigger, context: Dict[str, Any] = None) -> bool:
        """
        Dispara reavaliação de padrões.
        
        Args:
            trigger: Tipo de gatilho
            context: Contexto adicional
            
        Returns:
            True se reavaliação foi iniciada
        """
        try:
            # Verificar cooldown
            if self.last_reassessment:
                time_since_last = datetime.now() - self.last_reassessment
                if time_since_last < self.reassessment_cooldown:
                    logger.info(f"Reavaliação em cooldown. Aguardando {self.reassessment_cooldown - time_since_last}")
                    return False
            
            # Verificar se já está reavaliando
            if self.is_reassessing:
                logger.info("Reavaliação já em andamento")
                return False
            
            # Criar evento de reavaliação
            event = ReassessmentEvent(
                event_id=f"reassess_{int(datetime.now().timestamp())}",
                trigger=trigger,
                timestamp=datetime.now(),
                context=context or {},
                previous_patterns=self._get_current_patterns()
            )
            
            # Iniciar reavaliação em thread separada
            self.reassessment_thread = threading.Thread(
                target=self._perform_reassessment,
                args=(event,),
                daemon=True,
                name="PatternReassessment"
            )
            self.reassessment_thread.start()
            
            logger.info(f"Reavaliação iniciada por gatilho: {trigger.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao disparar reavaliação: {e}")
            return False
    
    def _perform_reassessment(self, event: ReassessmentEvent) -> None:
        """Executa a reavaliação de padrões."""
        try:
            self.is_reassessing = True
            start_time = time.time()
            
            logger.info(f"Iniciando reavaliação de padrões - Evento: {event.event_id}")
            
            # Executar callbacks de reavaliação para cada sistema
            for system_name, callbacks in self.reassessment_callbacks.items():
                if callbacks:
                    logger.info(f"Reavaliando sistema: {system_name}")
                    
                    for callback in callbacks:
                        try:
                            # Passar contexto da reavaliação
                            reassessment_context = {
                                'event': event,
                                'system': system_name,
                                'trigger': event.trigger.value,
                                'context': event.context
                            }
                            
                            callback(reassessment_context)
                            
                        except Exception as e:
                            logger.error(f"Erro no callback de reavaliação para {system_name}: {e}")
            
            # Calcular duração
            event.reassessment_duration = time.time() - start_time
            
            # Obter novos padrões detectados
            event.new_patterns = self._get_current_patterns()
            
            # Adicionar ao histórico
            self.reassessment_history.append(event)
            
            # Limitar histórico
            if len(self.reassessment_history) > 100:
                self.reassessment_history = self.reassessment_history[-100:]
            
            # Atualizar estatísticas
            self.last_reassessment = datetime.now()
            self.reassessment_count += 1
            
            logger.info(f"Reavaliação concluída em {event.reassessment_duration:.2f}s - "
                      f"Padrões anteriores: {len(event.previous_patterns)}, "
                      f"Novos padrões: {len(event.new_patterns)}")
            
        except Exception as e:
            logger.error(f"Erro durante reavaliação: {e}")
        finally:
            self.is_reassessing = False
    
    def _get_current_patterns(self) -> List[str]:
        """Obtém lista de padrões atuais de todos os sistemas."""
        patterns = []
        
        # Este método será implementado para coletar padrões de todos os sistemas
        # Por enquanto, retorna lista vazia
        return patterns
    
    def on_prediction_validated(self, validation_result: Dict[str, Any]) -> None:
        """
        Callback chamado quando uma predição é validada.
        
        Args:
            validation_result: Resultado da validação
        """
        try:
            status = validation_result.get('status')
            
            if status in ['correct', 'incorrect']:
                # Determinar tipo de gatilho baseado no resultado
                if status == 'correct':
                    trigger = ReassessmentTrigger.PREDICTION_VALIDATED
                    context = {
                        'result': 'correct',
                        'confidence': validation_result.get('confidence', 0),
                        'pattern_id': validation_result.get('pattern_id', 'unknown')
                    }
                else:
                    trigger = ReassessmentTrigger.PATTERN_BROKEN
                    context = {
                        'result': 'incorrect',
                        'confidence': validation_result.get('confidence', 0),
                        'pattern_id': validation_result.get('pattern_id', 'unknown'),
                        'predicted_color': validation_result.get('predicted_color'),
                        'actual_color': validation_result.get('actual_color')
                    }
                
                # Disparar reavaliação
                self.trigger_reassessment(trigger, context)
                
                logger.info(f"Reavaliação disparada após validação: {status}")
            
        except Exception as e:
            logger.error(f"Erro ao processar validação para reavaliação: {e}")
    
    def on_new_sequence_detected(self, sequence_data: Dict[str, Any]) -> None:
        """
        Callback chamado quando uma nova sequência é detectada.
        
        Args:
            sequence_data: Dados da sequência
        """
        try:
            context = {
                'sequence_type': sequence_data.get('type', 'unknown'),
                'sequence_length': sequence_data.get('length', 0),
                'sequence_colors': sequence_data.get('colors', []),
                'confidence': sequence_data.get('confidence', 0)
            }
            
            self.trigger_reassessment(ReassessmentTrigger.NEW_SEQUENCE_STARTED, context)
            
            logger.info(f"Reavaliação disparada por nova sequência: {sequence_data.get('type')}")
            
        except Exception as e:
            logger.error(f"Erro ao processar nova sequência para reavaliação: {e}")
    
    def on_performance_drop(self, performance_data: Dict[str, Any]) -> None:
        """
        Callback chamado quando há queda de performance.
        
        Args:
            performance_data: Dados de performance
        """
        try:
            context = {
                'accuracy_drop': performance_data.get('accuracy_drop', 0),
                'current_accuracy': performance_data.get('current_accuracy', 0),
                'previous_accuracy': performance_data.get('previous_accuracy', 0),
                'consecutive_errors': performance_data.get('consecutive_errors', 0)
            }
            
            self.trigger_reassessment(ReassessmentTrigger.PERFORMANCE_DROP, context)
            
            logger.info(f"Reavaliação disparada por queda de performance: {performance_data.get('accuracy_drop', 0):.2%}")
            
        except Exception as e:
            logger.error(f"Erro ao processar queda de performance para reavaliação: {e}")
    
    def start_periodic_reassessment(self, interval_minutes: int = 10) -> bool:
        """
        Inicia reavaliação periódica.
        
        Args:
            interval_minutes: Intervalo em minutos
            
        Returns:
            True se iniciou com sucesso
        """
        try:
            if self.reassessment_thread and self.reassessment_thread.is_alive():
                logger.warning("Reavaliação periódica já está ativa")
                return False
            
            def periodic_reassessment():
                while not self.stop_reassessment:
                    try:
                        time.sleep(interval_minutes * 60)
                        
                        if not self.stop_reassessment:
                            context = {
                                'interval_minutes': interval_minutes,
                                'reassessment_count': self.reassessment_count
                            }
                            self.trigger_reassessment(ReassessmentTrigger.TIME_BASED, context)
                            
                    except Exception as e:
                        logger.error(f"Erro na reavaliação periódica: {e}")
            
            self.reassessment_thread = threading.Thread(
                target=periodic_reassessment,
                daemon=True,
                name="PeriodicReassessment"
            )
            self.reassessment_thread.start()
            
            logger.info(f"Reavaliação periódica iniciada (intervalo: {interval_minutes} minutos)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar reavaliação periódica: {e}")
            return False
    
    def stop_periodic_reassessment(self) -> bool:
        """
        Para reavaliação periódica.
        
        Returns:
            True se parou com sucesso
        """
        try:
            self.stop_reassessment = True
            
            if self.reassessment_thread and self.reassessment_thread.is_alive():
                self.reassessment_thread.join(timeout=5)
            
            logger.info("Reavaliação periódica parada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar reavaliação periódica: {e}")
            return False
    
    def get_reassessment_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de reavaliação.
        
        Returns:
            Estatísticas de reavaliação
        """
        if not self.reassessment_history:
            return {'total_reassessments': 0}
        
        # Contar por tipo de gatilho
        trigger_counts = {}
        for event in self.reassessment_history:
            trigger = event.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        # Calcular estatísticas de tempo
        durations = [event.reassessment_duration for event in self.reassessment_history if event.reassessment_duration > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Reavaliações recentes (últimas 24 horas)
        recent_time = datetime.now() - timedelta(hours=24)
        recent_reassessments = [e for e in self.reassessment_history if e.timestamp > recent_time]
        
        return {
            'total_reassessments': len(self.reassessment_history),
            'recent_reassessments': len(recent_reassessments),
            'trigger_counts': trigger_counts,
            'average_duration': avg_duration,
            'is_reassessing': self.is_reassessing,
            'last_reassessment': self.last_reassessment.isoformat() if self.last_reassessment else None,
            'reassessment_count': self.reassessment_count
        }
    
    def get_recent_reassessments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna reavaliações recentes.
        
        Args:
            limit: Número máximo de reavaliações
            
        Returns:
            Lista de reavaliações recentes
        """
        recent = sorted(self.reassessment_history, key=lambda e: e.timestamp, reverse=True)
        
        return [
            {
                'event_id': event.event_id,
                'trigger': event.trigger.value,
                'timestamp': event.timestamp.isoformat(),
                'context': event.context,
                'previous_patterns_count': len(event.previous_patterns),
                'new_patterns_count': len(event.new_patterns) if event.new_patterns else 0,
                'duration': event.reassessment_duration
            }
            for event in recent[:limit]
        ]
