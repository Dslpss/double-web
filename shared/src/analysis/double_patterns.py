#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Padrões específicos do Double da Blaze
"""

from typing import Dict, List, Any, Tuple
from collections import Counter, deque
from datetime import datetime
import statistics

class DoublePatternDetector:
    """Detector de padrões específicos do Double"""
    
    def __init__(self):
        self.patterns = {
            'martingale': MartingalePattern(),
            'fibonacci': FibonacciPattern(),
            'd_alembert': DAlembertPattern(),
            'labouchere': LaboucherePattern(),
            'hot_cold': HotColdPattern(),
            'sequence': SequencePattern(),
            'alternation': AlternationPattern(),
            'white_bait': WhiteBaitPattern(),
            'color_balance': ColorBalancePattern(),
            'number_frequency': NumberFrequencyPattern()
        }
    
    def detect_all_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta todos os padrões possíveis"""
        if len(results) < 5:
            return {'error': 'Dados insuficientes para análise'}
        
        detected_patterns = {}
        
        for pattern_name, pattern_detector in self.patterns.items():
            try:
                result = pattern_detector.detect(results)
                if result and result.get('confidence', 0) > 0.65:
                    detected_patterns[pattern_name] = result
            except Exception as e:
                print(f"Erro ao detectar padrão {pattern_name}: {e}")
        
        return {
            'patterns': detected_patterns,
            'total_patterns': len(detected_patterns),
            'timestamp': datetime.now().isoformat()
        }

class MartingalePattern:
    """Padrão Martingale - dobra a aposta após perda"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 10:
            return None
        
        # Analisar sequências de perdas
        losses = 0
        max_losses = 0
        current_loss_streak = 0
        
        for result in results[-20:]:  # Últimos 20 resultados
            if result.get('was_loss', False):
                current_loss_streak += 1
                max_losses = max(max_losses, current_loss_streak)
            else:
                current_loss_streak = 0
        
        if max_losses >= 3:
            confidence = min(0.8, max_losses * 0.15)
            return {
                'pattern_type': 'Martingale',
                'confidence': confidence,
                'description': f'Sequência de {max_losses} perdas detectada',
                'recommendation': 'Dobrar aposta na próxima rodada',
                'risk_level': 'high'
            }
        return None

class FibonacciPattern:
    """Padrão Fibonacci - sequência de apostas"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 8:
            return None
        
        # Verificar se há sequência Fibonacci nos números
        numbers = [r.get('roll', 0) for r in results[-10:]]
        fib_sequence = [1, 1, 2, 3, 5, 8, 13]
        
        for i in range(len(numbers) - len(fib_sequence) + 1):
            if numbers[i:i+len(fib_sequence)] == fib_sequence:
                return {
                    'pattern_type': 'Fibonacci',
                    'confidence': 0.85,
                    'description': 'Sequência Fibonacci detectada nos números',
                    'recommendation': 'Seguir sequência Fibonacci nas apostas',
                    'risk_level': 'medium'
                }
        return None

class DAlembertPattern:
    """Padrão D'Alembert - aumenta aposta após perda, diminui após ganho"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 15:
            return None
        
        # Analisar variações de apostas
        wins = sum(1 for r in results[-15:] if r.get('was_win', False))
        losses = sum(1 for r in results[-15:] if r.get('was_loss', False))
        
        if abs(wins - losses) <= 2:  # Equilíbrio
            return {
                'pattern_type': 'D\'Alembert',
                'confidence': 0.7,
                'description': 'Equilíbrio entre vitórias e derrotas detectado',
                'recommendation': 'Aplicar estratégia D\'Alembert',
                'risk_level': 'low'
            }
        return None

class LaboucherePattern:
    """Padrão Labouchere - sequência de números para apostas"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 12:
            return None
        
        # Verificar padrões de sequência
        colors = [r.get('color', '') for r in results[-12:]]
        
        # Padrão: vermelho, preto, vermelho, preto...
        alternating = all(colors[i] != colors[i+1] for i in range(len(colors)-1))
        
        if alternating:
            return {
                'pattern_type': 'Labouchere',
                'confidence': 0.75,
                'description': 'Padrão alternado detectado',
                'recommendation': 'Aplicar estratégia Labouchere',
                'risk_level': 'medium'
            }
        return None

class HotColdPattern:
    """Padrão de números quentes e frios"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 20:
            return None
        
        # Contar frequência dos números
        numbers = [r.get('roll', 0) for r in results[-30:]]
        counter = Counter(numbers)
        
        # Encontrar números mais e menos frequentes
        most_common = counter.most_common(3)
        least_common = counter.most_common()[-3:]
        
        hot_numbers = [num for num, count in most_common if count >= 3]
        cold_numbers = [num for num, count in least_common if count <= 1]
        
        if hot_numbers or cold_numbers:
            confidence = 0.6 + (len(hot_numbers) + len(cold_numbers)) * 0.05
            return {
                'pattern_type': 'Hot/Cold Numbers',
                'confidence': min(0.9, confidence),
                'description': f'Números quentes: {hot_numbers}, frios: {cold_numbers}',
                'recommendation': f'Apostar em números quentes: {hot_numbers}' if hot_numbers else 'Evitar números frios',
                'risk_level': 'medium',
                'hot_numbers': hot_numbers,
                'cold_numbers': cold_numbers
            }
        return None

class SequencePattern:
    """Padrão de sequências"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 8:
            return None
        
        colors = [r.get('color', '') for r in results[-10:]]
        
        # Verificar sequências de mesma cor
        current_color = colors[0]
        max_sequence = 1
        current_sequence = 1
        
        for i in range(1, len(colors)):
            if colors[i] == current_color:
                current_sequence += 1
                max_sequence = max(max_sequence, current_sequence)
            else:
                current_color = colors[i]
                current_sequence = 1
        
        if max_sequence >= 4:
            confidence = min(0.9, 0.5 + max_sequence * 0.1)
            return {
                'pattern_type': 'Sequência de Cores',
                'confidence': confidence,
                'description': f'Sequência de {max_sequence} {current_color}s detectada',
                'recommendation': f'Continuar apostando em {current_color}' if max_sequence < 6 else f'Quebrar sequência - apostar em outra cor',
                'risk_level': 'high' if max_sequence >= 6 else 'medium'
            }
        return None

class AlternationPattern:
    """Padrão de alternância"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 10:
            return None
        
        colors = [r.get('color', '') for r in results[-12:]]
        
        # Verificar alternância perfeita
        alternating = True
        for i in range(len(colors) - 1):
            if colors[i] == colors[i + 1]:
                alternating = False
                break
        
        if alternating:
            # Prever próxima cor baseada no padrão
            if len(colors) >= 2:
                last_two = colors[-2:]
                if last_two[0] != last_two[1]:
                    predicted_color = last_two[0]  # Alternar com a primeira
                else:
                    predicted_color = 'white'  # Quebrar padrão
            else:
                predicted_color = 'red'  # Padrão padrão
            
            return {
                'pattern_type': 'Alternância',
                'confidence': 0.8,
                'description': 'Padrão de alternância detectado',
                'recommendation': f'Próxima cor: {predicted_color}',
                'predicted_color': predicted_color,
                'risk_level': 'medium'
            }
        return None

class WhiteBaitPattern:
    """Padrão da isca branca - branco seguido de cor específica"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 15:
            return None
        
        # Analisar o que acontece após branco
        white_positions = []
        for i, result in enumerate(results[-20:]):
            if result.get('roll', 0) == 0:  # Branco
                white_positions.append(i)
        
        if len(white_positions) < 2:
            return None
        
        # Verificar o que vem após branco
        after_white = []
        for pos in white_positions:
            if pos + 1 < len(results):
                next_color = results[pos + 1].get('color', '')
                after_white.append(next_color)
        
        if after_white:
            counter = Counter(after_white)
            most_common_after_white = counter.most_common(1)[0]
            
            if most_common_after_white[1] >= 3:  # Pelo menos 3 ocorrências
                confidence = min(0.85, 0.5 + most_common_after_white[1] * 0.1)
                return {
                    'pattern_type': 'Branco Isca',
                    'confidence': confidence,
                    'description': f'Após branco, {most_common_after_white[0]} aparece {most_common_after_white[1]} vezes',
                    'recommendation': f'Após branco, apostar em {most_common_after_white[0]}',
                    'predicted_color': most_common_after_white[0],
                    'risk_level': 'medium'
                }
        return None

class ColorBalancePattern:
    """Padrão de equilíbrio de cores"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 20:
            return None
        
        colors = [r.get('color', '') for r in results[-30:]]
        counter = Counter(colors)
        
        # Calcular desequilíbrio
        total = len(colors)
        red_pct = counter.get('red', 0) / total
        black_pct = counter.get('black', 0) / total
        white_pct = counter.get('white', 0) / total
        
        # Se uma cor está muito desbalanceada
        max_pct = max(red_pct, black_pct, white_pct)
        min_pct = min(red_pct, black_pct, white_pct)
        
        if max_pct - min_pct > 0.3:  # Diferença de 30%
            least_common_color = min(counter.items(), key=lambda x: x[1])[0]
            confidence = min(0.8, (max_pct - min_pct) * 2)
            
            return {
                'pattern_type': 'Desequilíbrio de Cores',
                'confidence': confidence,
                'description': f'Desequilíbrio detectado: {least_common_color} sub-representada',
                'recommendation': f'Apostar em {least_common_color} para equilibrar',
                'predicted_color': least_common_color,
                'risk_level': 'low'
            }
        return None

class NumberFrequencyPattern:
    """Padrão de frequência de números"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(results) < 25:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-40:]]
        counter = Counter(numbers)
        
        # Encontrar números com frequência anômala
        total = len(numbers)
        expected_freq = 1 / 15  # 15 números possíveis
        
        anomalies = []
        for num, count in counter.items():
            actual_freq = count / total
            if abs(actual_freq - expected_freq) > 0.1:  # 10% de diferença
                anomalies.append((num, actual_freq, count))
        
        if anomalies:
            # Ordenar por frequência
            anomalies.sort(key=lambda x: x[1], reverse=True)
            most_anomalous = anomalies[0]
            
            confidence = min(0.9, 0.5 + abs(most_anomalous[1] - expected_freq) * 5)
            
            return {
                'pattern_type': 'Frequência Anômala',
                'confidence': confidence,
                'description': f'Número {most_anomalous[0]} aparece {most_anomalous[2]} vezes (freq: {most_anomalous[1]:.2%})',
                'recommendation': f'{"Apostar em" if most_anomalous[1] > expected_freq else "Evitar"} número {most_anomalous[0]}',
                'anomalous_number': most_anomalous[0],
                'risk_level': 'medium'
            }
        return None
