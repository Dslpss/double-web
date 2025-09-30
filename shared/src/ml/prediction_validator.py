#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Validação de Predições para o Double da Blaze.
Verifica se as predições foram corretas e fornece feedback.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PredictionStatus(Enum):
    """Status de uma predição."""
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    EXPIRED = "expired"

@dataclass
class PredictionRecord:
    """Registro de uma predição."""
    prediction_id: str
    predicted_color: str
    confidence: float
    timestamp: datetime
    pattern_id: str
    reasoning: str
    status: PredictionStatus = PredictionStatus.PENDING
    actual_result: Optional[str] = None
    validated_at: Optional[datetime] = None
    validation_delay: timedelta = timedelta(minutes=2)

class PredictionValidator:
    """
    Valida predições e fornece feedback sobre acertos/erros.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o validador de predições.
        
        Args:
            config: Configurações do validador
        """
        self.config = config or {}
        
        # Configurações
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.7)
        self.max_pending_predictions = self.config.get('max_pending_predictions', 5)
        self.validation_timeout = timedelta(minutes=self.config.get('validation_timeout_minutes', 5))
        
        # Armazenamento de predições
        self.pending_predictions: Dict[str, PredictionRecord] = {}
        self.validated_predictions: List[PredictionRecord] = []
        
        # Estatísticas
        self.total_predictions = 0
        self.correct_predictions = 0
        self.incorrect_predictions = 0
        self.expired_predictions = 0
        
        # Callbacks para feedback
        self.feedback_callbacks: List[callable] = []
        
        logger.info("PredictionValidator inicializado")
    
    def add_prediction(self, 
                      predicted_color: str, 
                      confidence: float, 
                      pattern_id: str = "unknown",
                      reasoning: str = "") -> Optional[str]:
        """
        Adiciona uma nova predição para validação.
        
        Args:
            predicted_color: Cor predita
            confidence: Confiança da predição
            pattern_id: ID do padrão usado
            reasoning: Razão da predição
            
        Returns:
            ID da predição se foi aceita, None se rejeitada
        """
        try:
            # Verificar se a confiança é suficiente
            if confidence < self.min_confidence_threshold:
                logger.info(f"Predição rejeitada - confiança muito baixa: {confidence:.2%}")
                return None
            
            # Verificar limite de predições pendentes
            if len(self.pending_predictions) >= self.max_pending_predictions:
                logger.warning("Limite de predições pendentes atingido")
                return None
            
            # Criar registro da predição
            prediction_id = f"pred_{int(datetime.now().timestamp())}"
            prediction = PredictionRecord(
                prediction_id=prediction_id,
                predicted_color=predicted_color,
                confidence=confidence,
                timestamp=datetime.now(),
                pattern_id=pattern_id,
                reasoning=reasoning
            )
            
            # Armazenar predição pendente
            self.pending_predictions[prediction_id] = prediction
            self.total_predictions += 1
            
            logger.info(f"Nova predição adicionada: {predicted_color} ({confidence:.2%}) - ID: {prediction_id}")
            return prediction_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar predição: {e}")
            return None
    
    def validate_prediction(self, actual_color: str, prediction_id: str = None) -> Dict[str, Any]:
        """
        Valida uma predição com o resultado atual.
        
        Args:
            actual_color: Cor que realmente saiu
            prediction_id: ID específico da predição (opcional)
            
        Returns:
            Dict com resultado da validação
        """
        try:
            validated_predictions = []
            
            if prediction_id:
                # Validar predição específica
                if prediction_id in self.pending_predictions:
                    prediction = self.pending_predictions[prediction_id]
                    result = self._validate_single_prediction(prediction, actual_color)
                    validated_predictions.append(result)
            else:
                # Validar todas as predições pendentes
                for pred_id, prediction in list(self.pending_predictions.items()):
                    result = self._validate_single_prediction(prediction, actual_color)
                    validated_predictions.append(result)
            
            # Processar feedback
            self._process_validation_feedback(validated_predictions)
            
            return {
                'validated_count': len(validated_predictions),
                'predictions': validated_predictions,
                'stats': self.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar predição: {e}")
            return {'error': str(e)}
    
    def _validate_single_prediction(self, prediction: PredictionRecord, actual_color: str) -> Dict[str, Any]:
        """Valida uma única predição."""
        # Verificar se a predição ainda é válida (não expirou)
        if datetime.now() - prediction.timestamp > self.validation_timeout:
            prediction.status = PredictionStatus.EXPIRED
            prediction.validated_at = datetime.now()
            self.expired_predictions += 1
            logger.info(f"Predição expirada: {prediction.prediction_id}")
        else:
            # Validar predição
            prediction.actual_result = actual_color
            prediction.validated_at = datetime.now()
            
            if prediction.predicted_color == actual_color:
                prediction.status = PredictionStatus.CORRECT
                self.correct_predictions += 1
                logger.info(f"Predição CORRETA: {prediction.prediction_id} - {prediction.predicted_color}")
            else:
                prediction.status = PredictionStatus.INCORRECT
                self.incorrect_predictions += 1
                logger.info(f"Predição INCORRETA: {prediction.prediction_id} - Predito: {prediction.predicted_color}, Real: {actual_color}")
        
        # Mover para histórico
        self.validated_predictions.append(prediction)
        if prediction.prediction_id in self.pending_predictions:
            del self.pending_predictions[prediction.prediction_id]
        
        return {
            'prediction_id': prediction.prediction_id,
            'predicted_color': prediction.predicted_color,
            'actual_color': actual_color,
            'confidence': prediction.confidence,
            'status': prediction.status.value,
            'pattern_id': prediction.pattern_id,
            'reasoning': prediction.reasoning,
            'validation_delay': (prediction.validated_at - prediction.timestamp).total_seconds()
        }
    
    def _process_validation_feedback(self, validated_predictions: List[Dict[str, Any]]) -> None:
        """Processa feedback das validações."""
        for prediction_result in validated_predictions:
            # Chamar callbacks de feedback
            for callback in self.feedback_callbacks:
                try:
                    callback(prediction_result)
                except Exception as e:
                    logger.error(f"Erro no callback de feedback: {e}")
    
    def add_feedback_callback(self, callback: callable) -> None:
        """Adiciona um callback para receber feedback de validação."""
        self.feedback_callbacks.append(callback)
    
    def get_pending_predictions(self) -> List[Dict[str, Any]]:
        """Retorna predições pendentes."""
        return [
            {
                'prediction_id': pred.prediction_id,
                'predicted_color': pred.predicted_color,
                'confidence': pred.confidence,
                'timestamp': pred.timestamp.isoformat(),
                'pattern_id': pred.pattern_id,
                'reasoning': pred.reasoning,
                'age_minutes': (datetime.now() - pred.timestamp).total_seconds() / 60
            }
            for pred in self.pending_predictions.values()
        ]
    
    def get_recent_validations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna validações recentes."""
        recent = sorted(self.validated_predictions, key=lambda p: p.validated_at or p.timestamp, reverse=True)
        return [
            {
                'prediction_id': pred.prediction_id,
                'predicted_color': pred.predicted_color,
                'actual_color': pred.actual_result,
                'confidence': pred.confidence,
                'status': pred.status.value,
                'pattern_id': pred.pattern_id,
                'reasoning': pred.reasoning,
                'validated_at': pred.validated_at.isoformat() if pred.validated_at else None
            }
            for pred in recent[:limit]
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do validador."""
        total_validated = self.correct_predictions + self.incorrect_predictions + self.expired_predictions
        accuracy = self.correct_predictions / total_validated if total_validated > 0 else 0
        
        return {
            'total_predictions': self.total_predictions,
            'pending_predictions': len(self.pending_predictions),
            'correct_predictions': self.correct_predictions,
            'incorrect_predictions': self.incorrect_predictions,
            'expired_predictions': self.expired_predictions,
            'accuracy': accuracy,
            'min_confidence_threshold': self.min_confidence_threshold,
            'max_pending_predictions': self.max_pending_predictions
        }
    
    def should_send_alert(self, confidence: float) -> bool:
        """
        Determina se deve enviar um alerta baseado na confiança e histórico.
        
        Args:
            confidence: Confiança da predição
            
        Returns:
            True se deve enviar alerta
        """
        # Verificar confiança mínima
        if confidence < self.min_confidence_threshold:
            return False
        
        # Verificar se há muitas predições pendentes
        if len(self.pending_predictions) >= self.max_pending_predictions:
            return False
        
        # Verificar performance recente
        recent_validations = self.get_recent_validations(5)
        if len(recent_validations) >= 3:
            recent_correct = sum(1 for v in recent_validations if v['status'] == 'correct')
            recent_accuracy = recent_correct / len(recent_validations)
            
            # Se a performance recente for muito baixa, ser mais conservador
            if recent_accuracy < 0.3:
                return confidence > 0.8
        
        return True
    
    def cleanup_expired_predictions(self) -> int:
        """Remove predições expiradas."""
        expired_count = 0
        current_time = datetime.now()
        
        for pred_id, prediction in list(self.pending_predictions.items()):
            if current_time - prediction.timestamp > self.validation_timeout:
                prediction.status = PredictionStatus.EXPIRED
                prediction.validated_at = current_time
                self.validated_predictions.append(prediction)
                del self.pending_predictions[pred_id]
                self.expired_predictions += 1
                expired_count += 1
                logger.info(f"Predição expirada removida: {pred_id}")
        
        return expired_count
