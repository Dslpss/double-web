#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Detecção de Padrões Dual para Cores no Double da Blaze.
Identifica padrões específicos para vermelho e preto separadamente.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter, deque
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PatternCategory(Enum):
    """Categorias de padrões."""
    COLOR_SEQUENCE = "color_sequence"
    COLOR_FREQUENCY = "color_frequency"
    COLOR_ALTERNATION = "color_alternation"
    NUMBER_SEQUENCE = "number_sequence"
    NUMBER_FREQUENCY = "number_frequency"
    DUAL_COLOR_INTERACTION = "dual_color_interaction"
    TEMPORAL_PATTERN = "temporal_pattern"

@dataclass
class DualPattern:
    """Padrão dual identificado."""
    pattern_id: str
    category: PatternCategory
    red_pattern: Dict[str, Any]
    black_pattern: Dict[str, Any]
    confidence: float
    frequency: int
    last_seen: datetime
    success_rate: float
    total_predictions: int
    correct_predictions: int
    created_at: datetime
    updated_at: datetime

class DualColorPatternDetector:
    """
    Detector de padrões dual para cores vermelho e preto.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o detector de padrões dual.
        
        Args:
            config: Configurações do detector
        """
        self.config = config or {}
        
        # Configurações
        self.min_pattern_frequency = self.config.get('min_pattern_frequency', 3)
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.6)
        self.max_patterns = self.config.get('max_patterns', 200)
        self.sequence_length_range = self.config.get('sequence_length_range', (3, 8))
        self.history_size = self.config.get('history_size', 1000)
        
        # Armazenamento de padrões
        self.dual_patterns: Dict[str, DualPattern] = {}
        self.pattern_counter = 0
        
        # Histórico de dados
        self.data_history = deque(maxlen=self.history_size)
        
        # Análises específicas por cor
        self.red_analysis = {
            'sequences': defaultdict(int),
            'frequencies': Counter(),
            'alternations': [],
            'hot_numbers': Counter(),
            'cold_numbers': Counter()
        }
        
        self.black_analysis = {
            'sequences': defaultdict(int),
            'frequencies': Counter(),
            'alternations': [],
            'hot_numbers': Counter(),
            'cold_numbers': Counter()
        }
        
        # Análise de interação entre cores
        self.color_interaction = {
            'red_after_black': Counter(),
            'black_after_red': Counter(),
            'red_sequences': [],
            'black_sequences': [],
            'alternation_patterns': []
        }
        
        logger.info("DualColorPatternDetector inicializado")
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """
        Adiciona um resultado e atualiza as análises.
        
        Args:
            result: Resultado do jogo
        """
        try:
            if not self._validate_result(result):
                return
            
            # Adicionar ao histórico
            self.data_history.append(result)
            
            # Atualizar análises específicas por cor
            self._update_color_specific_analysis(result)
            
            # Atualizar análise de interação
            self._update_color_interaction_analysis(result)
            
            # Detectar novos padrões
            self._detect_new_patterns()
            
            # Atualizar padrões existentes
            self._update_existing_patterns()
            
            # Limpar padrões obsoletos
            self._cleanup_obsolete_patterns()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar resultado: {e}")
    
    def get_patterns_for_color(self, color: str) -> List[DualPattern]:
        """
        Retorna padrões específicos para uma cor.
        
        Args:
            color: Cor ('red' ou 'black')
            
        Returns:
            Lista de padrões para a cor
        """
        color_patterns = []
        
        for pattern in self.dual_patterns.values():
            if pattern.confidence > self.min_confidence_threshold:
                if color == 'red' and pattern.red_pattern:
                    color_patterns.append(pattern)
                elif color == 'black' and pattern.black_pattern:
                    color_patterns.append(pattern)
        
        # Ordenar por confiança e taxa de sucesso
        color_patterns.sort(
            key=lambda p: p.confidence * (0.5 + p.success_rate * 0.5),
            reverse=True
        )
        
        return color_patterns
    
    def predict_next_for_color(self, color: str) -> Dict[str, Any]:
        """
        Faz predição específica para uma cor.
        
        Args:
            color: Cor para predição
            
        Returns:
            Predição para a cor
        """
        try:
            patterns = self.get_patterns_for_color(color)
            
            if not patterns:
                return self._get_default_prediction(color)
            
            # Combinar predições de diferentes padrões
            combined_prediction = self._combine_color_predictions(color, patterns)
            
            return combined_prediction
            
        except Exception as e:
            logger.error(f"Erro ao predizer para cor {color}: {e}")
            return self._get_default_prediction(color)
    
    def get_dual_analysis(self) -> Dict[str, Any]:
        """
        Retorna análise dual completa.
        
        Returns:
            Análise dual das cores
        """
        return {
            'red_analysis': self._get_color_analysis('red'),
            'black_analysis': self._get_color_analysis('black'),
            'color_interaction': self._get_color_interaction_analysis(),
            'dual_patterns': self._get_dual_patterns_summary(),
            'statistics': self._get_statistics()
        }
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Valida se o resultado é válido."""
        required_fields = ['roll', 'color']
        return all(field in result for field in required_fields)
    
    def _update_color_specific_analysis(self, result: Dict[str, Any]) -> None:
        """Atualiza análise específica por cor."""
        roll = result.get('roll')
        color = result.get('color')
        
        if color == 'red':
            analysis = self.red_analysis
        elif color == 'black':
            analysis = self.black_analysis
        else:
            return  # Ignorar branco por enquanto
        
        # Atualizar frequências
        analysis['frequencies'][color] += 1
        
        # Atualizar números quentes/frios
        analysis['hot_numbers'][roll] += 1
        
        # Atualizar sequências
        if len(self.data_history) >= 2:
            prev_result = self.data_history[-2]
            prev_color = prev_result.get('color')
            
            if prev_color == color:
                # Sequência da mesma cor
                sequence_key = f"{prev_color}_{color}"
                analysis['sequences'][sequence_key] += 1
            else:
                # Alternação
                alternation_key = f"{prev_color}_{color}"
                analysis['alternations'].append(alternation_key)
    
    def _update_color_interaction_analysis(self, result: Dict[str, Any]) -> None:
        """Atualiza análise de interação entre cores."""
        color = result.get('color')
        
        if color not in ['red', 'black']:
            return
        
        if len(self.data_history) >= 2:
            prev_result = self.data_history[-2]
            prev_color = prev_result.get('color')
            
            if prev_color in ['red', 'black']:
                # Atualizar interações
                if prev_color == 'red' and color == 'black':
                    self.color_interaction['black_after_red'][color] += 1
                elif prev_color == 'black' and color == 'red':
                    self.color_interaction['red_after_black'][color] += 1
                
                # Atualizar sequências
                if prev_color == color:
                    if color == 'red':
                        self.color_interaction['red_sequences'].append(result)
                    else:
                        self.color_interaction['black_sequences'].append(result)
                else:
                    # Alternação
                    alternation = f"{prev_color}_{color}"
                    self.color_interaction['alternation_patterns'].append(alternation)
    
    def _detect_new_patterns(self) -> None:
        """Detecta novos padrões dual."""
        if len(self.data_history) < 20:
            return
        
        # Detectar padrões de sequência dual
        self._detect_dual_sequence_patterns()
        
        # Detectar padrões de frequência dual
        self._detect_dual_frequency_patterns()
        
        # Detectar padrões de alternação dual
        self._detect_dual_alternation_patterns()
        
        # Detectar padrões de números quentes/frios
        self._detect_hot_cold_number_patterns()
    
    def _detect_dual_sequence_patterns(self) -> None:
        """Detecta padrões de sequência dual."""
        colors = [r.get('color') for r in list(self.data_history)[-50:]]
        
        for length in range(self.sequence_length_range[0], self.sequence_length_range[1] + 1):
            for i in range(len(colors) - length):
                sequence = colors[i:i+length]
                
                # Separar sequências por cor
                red_sequence = [c for c in sequence if c == 'red']
                black_sequence = [c for c in sequence if c == 'black']
                
                if len(red_sequence) >= 2 and len(black_sequence) >= 2:
                    # Padrão dual válido
                    pattern_key = f"dual_seq_{length}_{i}"
                    
                    if pattern_key not in self.dual_patterns:
                        confidence = self._calculate_sequence_confidence(sequence)
                        
                        if confidence > self.min_confidence_threshold:
                            pattern = DualPattern(
                                pattern_id=f"dual_seq_{self.pattern_counter}",
                                category=PatternCategory.DUAL_COLOR_INTERACTION,
                                red_pattern={
                                    'sequence': red_sequence,
                                    'length': len(red_sequence),
                                    'positions': [j for j, c in enumerate(sequence) if c == 'red']
                                },
                                black_pattern={
                                    'sequence': black_sequence,
                                    'length': len(black_sequence),
                                    'positions': [j for j, c in enumerate(sequence) if c == 'black']
                                },
                                confidence=confidence,
                                frequency=1,
                                last_seen=datetime.now(),
                                success_rate=0.0,
                                total_predictions=0,
                                correct_predictions=0,
                                created_at=datetime.now(),
                                updated_at=datetime.now()
                            )
                            
                            self.dual_patterns[pattern_key] = pattern
                            self.pattern_counter += 1
                            logger.info(f"Novo padrão dual de sequência detectado: {pattern_key}")
    
    def _detect_dual_frequency_patterns(self) -> None:
        """Detecta padrões de frequência dual."""
        colors = [r.get('color') for r in list(self.data_history)[-30:]]
        total = len(colors)
        
        red_count = colors.count('red')
        black_count = colors.count('black')
        
        red_frequency = red_count / total if total > 0 else 0
        black_frequency = black_count / total if total > 0 else 0
        
        # Detectar padrões de alta frequência dual
        if red_frequency > 0.6 and black_frequency > 0.3:
            pattern_key = "dual_freq_high_red_black"
            if pattern_key not in self.dual_patterns:
                confidence = min(0.8, (red_frequency + black_frequency) / 2)
                
                pattern = DualPattern(
                    pattern_id=f"dual_freq_{self.pattern_counter}",
                    category=PatternCategory.COLOR_FREQUENCY,
                    red_pattern={
                        'frequency': red_frequency,
                        'count': red_count,
                        'type': 'high'
                    },
                    black_pattern={
                        'frequency': black_frequency,
                        'count': black_count,
                        'type': 'medium'
                    },
                    confidence=confidence,
                    frequency=1,
                    last_seen=datetime.now(),
                    success_rate=0.0,
                    total_predictions=0,
                    correct_predictions=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.dual_patterns[pattern_key] = pattern
                self.pattern_counter += 1
                logger.info(f"Novo padrão dual de frequência detectado: {pattern_key}")
    
    def _detect_dual_alternation_patterns(self) -> None:
        """Detecta padrões de alternação dual."""
        alternations = self.color_interaction['alternation_patterns']
        
        if len(alternations) >= 5:
            # Contar padrões de alternação
            alt_counts = Counter(alternations[-20:])  # Últimas 20 alternações
            
            for alt_pattern, count in alt_counts.items():
                if count >= 3:  # Padrão de alternação frequente
                    pattern_key = f"dual_alt_{alt_pattern}"
                    
                    if pattern_key not in self.dual_patterns:
                        confidence = min(0.7, count / len(alternations))
                        
                        pattern = DualPattern(
                            pattern_id=f"dual_alt_{self.pattern_counter}",
                            category=PatternCategory.COLOR_ALTERNATION,
                            red_pattern={
                                'alternation_pattern': alt_pattern,
                                'frequency': count,
                                'type': 'alternation'
                            },
                            black_pattern={
                                'alternation_pattern': alt_pattern,
                                'frequency': count,
                                'type': 'alternation'
                            },
                            confidence=confidence,
                            frequency=count,
                            last_seen=datetime.now(),
                            success_rate=0.0,
                            total_predictions=0,
                            correct_predictions=0,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        
                        self.dual_patterns[pattern_key] = pattern
                        self.pattern_counter += 1
                        logger.info(f"Novo padrão dual de alternação detectado: {pattern_key}")
    
    def _detect_hot_cold_number_patterns(self) -> None:
        """Detecta padrões de números quentes/frios."""
        # Análise de números quentes para vermelho
        red_numbers = [r.get('roll') for r in self.data_history if r.get('color') == 'red']
        black_numbers = [r.get('roll') for r in self.data_history if r.get('color') == 'black']
        
        if len(red_numbers) >= 10:
            red_hot = Counter(red_numbers).most_common(3)
            red_cold = Counter(red_numbers).most_common()[-3:]
            
            # Padrão de números quentes vermelhos
            if red_hot[0][1] >= 3:  # Número aparece pelo menos 3 vezes
                pattern_key = "dual_hot_red_numbers"
                if pattern_key not in self.dual_patterns:
                    confidence = min(0.6, red_hot[0][1] / len(red_numbers))
                    
                    pattern = DualPattern(
                        pattern_id=f"dual_hot_{self.pattern_counter}",
                        category=PatternCategory.NUMBER_FREQUENCY,
                        red_pattern={
                            'hot_numbers': [n[0] for n in red_hot],
                            'cold_numbers': [n[0] for n in red_cold],
                            'hot_frequency': red_hot[0][1]
                        },
                        black_pattern={},
                        confidence=confidence,
                        frequency=red_hot[0][1],
                        last_seen=datetime.now(),
                        success_rate=0.0,
                        total_predictions=0,
                        correct_predictions=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.dual_patterns[pattern_key] = pattern
                    self.pattern_counter += 1
                    logger.info(f"Novo padrão dual de números quentes vermelhos detectado: {pattern_key}")
        
        # Análise similar para preto
        if len(black_numbers) >= 10:
            black_hot = Counter(black_numbers).most_common(3)
            black_cold = Counter(black_numbers).most_common()[-3:]
            
            if black_hot[0][1] >= 3:
                pattern_key = "dual_hot_black_numbers"
                if pattern_key not in self.dual_patterns:
                    confidence = min(0.6, black_hot[0][1] / len(black_numbers))
                    
                    pattern = DualPattern(
                        pattern_id=f"dual_hot_{self.pattern_counter}",
                        category=PatternCategory.NUMBER_FREQUENCY,
                        red_pattern={},
                        black_pattern={
                            'hot_numbers': [n[0] for n in black_hot],
                            'cold_numbers': [n[0] for n in black_cold],
                            'hot_frequency': black_hot[0][1]
                        },
                        confidence=confidence,
                        frequency=black_hot[0][1],
                        last_seen=datetime.now(),
                        success_rate=0.0,
                        total_predictions=0,
                        correct_predictions=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.dual_patterns[pattern_key] = pattern
                    self.pattern_counter += 1
                    logger.info(f"Novo padrão dual de números quentes pretos detectado: {pattern_key}")
    
    def _calculate_sequence_confidence(self, sequence: List[str]) -> float:
        """Calcula confiança de uma sequência."""
        if not sequence:
            return 0.0
        
        # Contar repetições
        repetitions = 0
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i-1]:
                repetitions += 1
        
        # Confiança baseada em repetições e tamanho
        repetition_ratio = repetitions / (len(sequence) - 1) if len(sequence) > 1 else 0
        size_factor = min(1.0, len(sequence) / 10)
        
        return min(0.9, repetition_ratio * size_factor)
    
    def _update_existing_patterns(self) -> None:
        """Atualiza padrões existentes."""
        for pattern in self.dual_patterns.values():
            # Aplicar decay na confiança
            pattern.confidence *= 0.95
            
            # Atualizar timestamp
            pattern.updated_at = datetime.now()
    
    def _cleanup_obsolete_patterns(self) -> None:
        """Remove padrões obsoletos."""
        to_remove = []
        
        for pattern_id, pattern in self.dual_patterns.items():
            # Remover padrões com confiança muito baixa
            if pattern.confidence < 0.1:
                to_remove.append(pattern_id)
            
            # Remover padrões muito antigos sem uso
            days_since_update = (datetime.now() - pattern.updated_at).days
            if days_since_update > 7 and pattern.total_predictions == 0:
                to_remove.append(pattern_id)
        
        for pattern_id in to_remove:
            del self.dual_patterns[pattern_id]
            logger.info(f"Padrão dual obsoleto removido: {pattern_id}")
    
    def _combine_color_predictions(self, color: str, patterns: List[DualPattern]) -> Dict[str, Any]:
        """Combina predições de diferentes padrões para uma cor."""
        if not patterns:
            return self._get_default_prediction(color)
        
        # Calcular pesos baseados na confiança e taxa de sucesso
        weights = []
        predictions = []
        
        for pattern in patterns:
            weight = pattern.confidence * (0.5 + pattern.success_rate * 0.5)
            weights.append(weight)
            
            # Gerar predição baseada no padrão
            prediction = self._generate_pattern_prediction(color, pattern)
            predictions.append(prediction)
        
        # Normalizar pesos
        total_weight = sum(weights)
        if total_weight == 0:
            return self._get_default_prediction(color)
        
        weights = [w / total_weight for w in weights]
        
        # Combinar predições
        color_probs = {'red': 0.0, 'black': 0.0, 'white': 0.0}
        
        for i, prediction in enumerate(predictions):
            pred_color = prediction.get('color', color)
            confidence = prediction.get('confidence', 0.0)
            color_probs[pred_color] += weights[i] * confidence
        
        # Determinar cor com maior probabilidade
        predicted_color = max(color_probs.keys(), key=lambda k: color_probs[k])
        confidence = color_probs[predicted_color]
        
        return {
            'color': predicted_color,
            'confidence': confidence,
            'pattern_id': 'dual_combined',
            'patterns_used': [p.pattern_id for p in patterns],
            'reasoning': f"Baseado em {len(patterns)} padrões dual para {color}"
        }
    
    def _generate_pattern_prediction(self, color: str, pattern: DualPattern) -> Dict[str, Any]:
        """Gera predição baseada em um padrão específico."""
        if pattern.category == PatternCategory.COLOR_FREQUENCY:
            if color == 'red' and pattern.red_pattern:
                freq_type = pattern.red_pattern.get('type', 'normal')
                if freq_type == 'high':
                    return {'color': 'black', 'confidence': pattern.confidence * 0.7}
                else:
                    return {'color': 'red', 'confidence': pattern.confidence * 0.6}
            
            elif color == 'black' and pattern.black_pattern:
                freq_type = pattern.black_pattern.get('type', 'normal')
                if freq_type == 'high':
                    return {'color': 'red', 'confidence': pattern.confidence * 0.7}
                else:
                    return {'color': 'black', 'confidence': pattern.confidence * 0.6}
        
        elif pattern.category == PatternCategory.COLOR_ALTERNATION:
            # Predizer quebra da alternação
            return {'color': 'white', 'confidence': pattern.confidence * 0.5}
        
        elif pattern.category == PatternCategory.NUMBER_FREQUENCY:
            if color == 'red' and pattern.red_pattern:
                hot_numbers = pattern.red_pattern.get('hot_numbers', [])
                if hot_numbers:
                    return {'color': 'red', 'confidence': pattern.confidence * 0.6}
            
            elif color == 'black' and pattern.black_pattern:
                hot_numbers = pattern.black_pattern.get('hot_numbers', [])
                if hot_numbers:
                    return {'color': 'black', 'confidence': pattern.confidence * 0.6}
        
        return {'color': color, 'confidence': 0.33}
    
    def _get_color_analysis(self, color: str) -> Dict[str, Any]:
        """Retorna análise específica de uma cor."""
        if color == 'red':
            analysis = self.red_analysis
        elif color == 'black':
            analysis = self.black_analysis
        else:
            return {}
        
        return {
            'sequences': dict(analysis['sequences']),
            'frequencies': dict(analysis['frequencies']),
            'alternations': analysis['alternations'][-10:],  # Últimas 10
            'hot_numbers': dict(analysis['hot_numbers'].most_common(5)),
            'cold_numbers': dict(analysis['cold_numbers'].most_common(5))
        }
    
    def _get_color_interaction_analysis(self) -> Dict[str, Any]:
        """Retorna análise de interação entre cores."""
        return {
            'red_after_black': dict(self.color_interaction['red_after_black']),
            'black_after_red': dict(self.color_interaction['black_after_red']),
            'red_sequences_count': len(self.color_interaction['red_sequences']),
            'black_sequences_count': len(self.color_interaction['black_sequences']),
            'alternation_patterns': self.color_interaction['alternation_patterns'][-10:]
        }
    
    def _get_dual_patterns_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos padrões dual."""
        return {
            'total_patterns': len(self.dual_patterns),
            'active_patterns': len([p for p in self.dual_patterns.values() 
                                  if p.confidence > self.min_confidence_threshold]),
            'pattern_categories': Counter(p.category.value for p in self.dual_patterns.values()),
            'top_patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'category': p.category.value,
                    'confidence': p.confidence,
                    'success_rate': p.success_rate,
                    'frequency': p.frequency
                }
                for p in sorted(self.dual_patterns.values(), 
                              key=lambda p: p.confidence, reverse=True)[:5]
            ]
        }
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais."""
        return {
            'data_history_size': len(self.data_history),
            'red_patterns': len([p for p in self.dual_patterns.values() if p.red_pattern]),
            'black_patterns': len([p for p in self.dual_patterns.values() if p.black_pattern]),
            'dual_patterns': len([p for p in self.dual_patterns.values() 
                                if p.red_pattern and p.black_pattern])
        }
    
    def _get_default_prediction(self, color: str) -> Dict[str, Any]:
        """Retorna predição padrão para uma cor."""
        return {
            'color': color,
            'confidence': 0.33,
            'pattern_id': 'default',
            'patterns_used': [],
            'reasoning': f'Predição padrão para {color} - dados insuficientes'
        }
