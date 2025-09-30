#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Validação de Dados para o Blaze Double Analyzer
Implementa padrões e validações para melhorar a precisão dos dados inseridos manualmente.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter, deque

logger = logging.getLogger(__name__)

class DataValidator:
    """Sistema de validação avançado para dados do Double da Blaze."""
    
    def __init__(self):
        """Inicializa o validador."""
        self.validation_rules = self._setup_validation_rules()
        self.pattern_detector = PatternDetector()
        self.anomaly_detector = AnomalyDetector()
        
        logger.info("Sistema de validação de dados inicializado")
    
    def _setup_validation_rules(self) -> Dict:
        """Configura as regras de validação."""
        return {
            'number_range': (0, 14),
            'valid_colors': ['red', 'black', 'white'],
            'max_sequence_length': 1000,
            'min_data_points': 10,
            'anomaly_threshold': 0.8,
            'pattern_confidence_threshold': 0.7
        }
    
    def validate_single_entry(self, number: int, timestamp: Optional[float] = None) -> Dict:
        """
        Valida uma única entrada de dados.
        
        Args:
            number (int): Número inserido (0-14)
            timestamp (float, optional): Timestamp da entrada
            
        Returns:
            Dict: Resultado da validação
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'confidence_score': 1.0
        }
        
        # Validar número
        if not isinstance(number, int):
            validation_result['is_valid'] = False
            validation_result['errors'].append("Número deve ser um inteiro")
            return validation_result
        
        if not (0 <= number <= 14):
            validation_result['is_valid'] = False
            validation_result['errors'].append("Número deve estar entre 0 e 14")
            return validation_result
        
        # Validar timestamp
        if timestamp is not None:
            if not isinstance(timestamp, (int, float)):
                validation_result['warnings'].append("Timestamp inválido, usando timestamp atual")
            elif timestamp < 0:
                validation_result['warnings'].append("Timestamp negativo detectado")
            elif timestamp > datetime.now().timestamp() + 3600:  # 1 hora no futuro
                validation_result['warnings'].append("Timestamp muito no futuro")
        
        # Determinar cor
        color = self._determine_color(number)
        validation_result['color'] = color
        validation_result['number'] = number
        
        return validation_result
    
    def validate_sequence(self, data: List[Dict]) -> Dict:
        """
        Valida uma sequência completa de dados.
        
        Args:
            data (List[Dict]): Lista de resultados
            
        Returns:
            Dict: Resultado da validação da sequência
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'confidence_score': 1.0,
            'statistics': {},
            'patterns_detected': [],
            'anomalies_detected': []
        }
        
        if not data:
            validation_result['errors'].append("Sequência vazia")
            validation_result['is_valid'] = False
            return validation_result
        
        # Validar cada entrada individual
        for i, entry in enumerate(data):
            number = entry.get('roll', entry.get('number', -1))
            entry_validation = self.validate_single_entry(number)
            
            if not entry_validation['is_valid']:
                validation_result['errors'].append(f"Entrada {i+1}: {', '.join(entry_validation['errors'])}")
                validation_result['is_valid'] = False
            
            if entry_validation['warnings']:
                validation_result['warnings'].extend([f"Entrada {i+1}: {w}" for w in entry_validation['warnings']])
        
        if not validation_result['is_valid']:
            return validation_result
        
        # Análise estatística
        stats = self._analyze_sequence_statistics(data)
        validation_result['statistics'] = stats
        
        # Detectar padrões
        patterns = self.pattern_detector.detect_patterns(data)
        validation_result['patterns_detected'] = patterns
        
        # Detectar anomalias
        anomalies = self.anomaly_detector.detect_anomalies(data)
        validation_result['anomalies_detected'] = anomalies
        
        # Calcular score de confiança
        confidence = self._calculate_confidence_score(stats, patterns, anomalies)
        validation_result['confidence_score'] = confidence
        
        # Gerar sugestões
        suggestions = self._generate_suggestions(stats, patterns, anomalies)
        validation_result['suggestions'] = suggestions
        
        return validation_result
    
    def _determine_color(self, number: int) -> str:
        """Determina a cor baseada no número."""
        if number == 0:
            return 'white'
        elif 1 <= number <= 7:
            return 'red'
        elif 8 <= number <= 14:
            return 'black'
        else:
            return 'unknown'
    
    def _analyze_sequence_statistics(self, data: List[Dict]) -> Dict:
        """Analisa estatísticas da sequência."""
        numbers = [entry.get('roll', entry.get('number', 0)) for entry in data]
        colors = [self._determine_color(num) for num in numbers]
        
        # Estatísticas básicas
        stats = {
            'total_entries': len(data),
            'number_distribution': dict(Counter(numbers)),
            'color_distribution': dict(Counter(colors)),
            'unique_numbers': len(set(numbers)),
            'unique_colors': len(set(colors))
        }
        
        # Estatísticas de sequências
        stats.update(self._analyze_sequences(colors))
        
        # Estatísticas temporais (se disponível)
        timestamps = [entry.get('timestamp', 0) for entry in data if entry.get('timestamp')]
        if timestamps:
            stats.update(self._analyze_temporal_patterns(timestamps))
        
        return stats
    
    def _analyze_sequences(self, colors: List[str]) -> Dict:
        """Analisa sequências de cores."""
        if len(colors) < 2:
            return {'max_streak': 0, 'avg_streak': 0}
        
        current_streak = 1
        max_streak = 1
        streaks = []
        
        for i in range(1, len(colors)):
            if colors[i] == colors[i-1]:
                current_streak += 1
            else:
                streaks.append(current_streak)
                max_streak = max(max_streak, current_streak)
                current_streak = 1
        
        streaks.append(current_streak)
        max_streak = max(max_streak, current_streak)
        
        return {
            'max_streak': max_streak,
            'avg_streak': sum(streaks) / len(streaks) if streaks else 0,
            'streak_distribution': dict(Counter(streaks))
        }
    
    def _analyze_temporal_patterns(self, timestamps: List[float]) -> Dict:
        """Analisa padrões temporais."""
        if len(timestamps) < 2:
            return {}
        
        # Converter timestamps para datetime
        times = [datetime.fromtimestamp(ts) for ts in timestamps]
        times.sort()
        
        # Calcular intervalos
        intervals = []
        for i in range(1, len(times)):
            interval = (times[i] - times[i-1]).total_seconds()
            intervals.append(interval)
        
        return {
            'avg_interval': sum(intervals) / len(intervals) if intervals else 0,
            'min_interval': min(intervals) if intervals else 0,
            'max_interval': max(intervals) if intervals else 0,
            'total_duration': (times[-1] - times[0]).total_seconds()
        }
    
    def _calculate_confidence_score(self, stats: Dict, patterns: List, anomalies: List) -> float:
        """Calcula score de confiança dos dados."""
        score = 1.0
        
        # Penalizar por anomalias
        score -= len(anomalies) * 0.1
        
        # Penalizar por sequências muito longas (possível erro)
        if stats.get('max_streak', 0) > 10:
            score -= 0.2
        
        # Penalizar por distribuição muito desequilibrada
        color_dist = stats.get('color_distribution', {})
        if color_dist:
            total = sum(color_dist.values())
            for color, count in color_dist.items():
                percentage = count / total
                if percentage > 0.8:  # Mais de 80% de uma cor
                    score -= 0.3
        
        # Bonificar por padrões detectados
        if patterns:
            score += min(len(patterns) * 0.05, 0.2)
        
        return max(0.0, min(1.0, score))
    
    def _generate_suggestions(self, stats: Dict, patterns: List, anomalies: List) -> List[str]:
        """Gera sugestões baseadas na análise."""
        suggestions = []
        
        # Sugestões baseadas em estatísticas
        if stats.get('total_entries', 0) < 20:
            suggestions.append("Considere inserir mais dados para análise mais precisa")
        
        if stats.get('max_streak', 0) > 8:
            suggestions.append("Sequência muito longa detectada - verifique se os dados estão corretos")
        
        # Sugestões baseadas em distribuição
        color_dist = stats.get('color_distribution', {})
        if color_dist:
            total = sum(color_dist.values())
            for color, count in color_dist.items():
                percentage = count / total
                if percentage > 0.7:
                    suggestions.append(f"Distribuição muito concentrada em {color} ({percentage:.1%})")
        
        # Sugestões baseadas em anomalias
        if anomalies:
            suggestions.append(f"{len(anomalies)} anomalias detectadas - revise os dados")
        
        # Sugestões baseadas em padrões
        if patterns:
            suggestions.append(f"{len(patterns)} padrões detectados - dados podem ser úteis para análise")
        
        return suggestions

class PatternDetector:
    """Detector de padrões em sequências de dados."""
    
    def __init__(self):
        """Inicializa o detector de padrões."""
        self.min_pattern_length = 2
        self.max_pattern_length = 10
        
    def detect_patterns(self, data: List[Dict]) -> List[Dict]:
        """
        Detecta padrões na sequência de dados.
        
        Args:
            data (List[Dict]): Lista de resultados
            
        Returns:
            List[Dict]: Lista de padrões detectados
        """
        patterns = []
        
        if len(data) < 4:
            return patterns
        
        # Extrair cores
        colors = []
        for entry in data:
            number = entry.get('roll', entry.get('number', 0))
            if number == 0:
                colors.append('white')
            elif 1 <= number <= 7:
                colors.append('red')
            elif 8 <= number <= 14:
                colors.append('black')
        
        # Detectar padrões de repetição
        repetition_patterns = self._detect_repetition_patterns(colors)
        patterns.extend(repetition_patterns)
        
        # Detectar padrões alternantes
        alternating_patterns = self._detect_alternating_patterns(colors)
        patterns.extend(alternating_patterns)
        
        # Detectar padrões de sequência
        sequence_patterns = self._detect_sequence_patterns(colors)
        patterns.extend(sequence_patterns)
        
        return patterns
    
    def _detect_repetition_patterns(self, colors: List[str]) -> List[Dict]:
        """Detecta padrões de repetição."""
        patterns = []
        
        for length in range(self.min_pattern_length, min(self.max_pattern_length, len(colors) // 2)):
            pattern_counts = {}
            
            for i in range(len(colors) - length + 1):
                pattern = tuple(colors[i:i+length])
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            # Filtrar padrões que ocorrem mais de uma vez
            for pattern, count in pattern_counts.items():
                if count > 1:
                    patterns.append({
                        'type': 'repetition',
                        'pattern': ' -> '.join(pattern),
                        'length': length,
                        'occurrences': count,
                        'confidence': min(count / 3.0, 1.0)
                    })
        
        return patterns
    
    def _detect_alternating_patterns(self, colors: List[str]) -> List[Dict]:
        """Detecta padrões alternantes."""
        patterns = []
        
        if len(colors) < 4:
            return patterns
        
        # Padrão alternante simples (A-B-A-B)
        alternating_count = 0
        for i in range(2, len(colors)):
            if colors[i] == colors[i-2] and colors[i] != colors[i-1]:
                alternating_count += 1
        
        if alternating_count > 2:
            patterns.append({
                'type': 'alternating',
                'pattern': 'Alternating',
                'length': 2,
                'occurrences': alternating_count,
                'confidence': min(alternating_count / 5.0, 1.0)
            })
        
        return patterns
    
    def _detect_sequence_patterns(self, colors: List[str]) -> List[Dict]:
        """Detecta padrões de sequência."""
        patterns = []
        
        # Detectar sequências de cores iguais
        current_color = colors[0]
        current_count = 1
        max_count = 1
        
        for i in range(1, len(colors)):
            if colors[i] == current_color:
                current_count += 1
            else:
                if current_count > max_count:
                    max_count = current_count
                current_color = colors[i]
                current_count = 1
        
        if current_count > max_count:
            max_count = current_count
        
        if max_count > 4:
            patterns.append({
                'type': 'streak',
                'pattern': f'Streak of {max_count}',
                'length': max_count,
                'occurrences': 1,
                'confidence': min(max_count / 8.0, 1.0)
            })
        
        return patterns

class AnomalyDetector:
    """Detector de anomalias em sequências de dados."""
    
    def __init__(self):
        """Inicializa o detector de anomalias."""
        self.anomaly_threshold = 0.8
        
    def detect_anomalies(self, data: List[Dict]) -> List[Dict]:
        """
        Detecta anomalias na sequência de dados.
        
        Args:
            data (List[Dict]): Lista de resultados
            
        Returns:
            List[Dict]: Lista de anomalias detectadas
        """
        anomalies = []
        
        if len(data) < 10:
            return anomalies
        
        # Detectar anomalias temporais
        temporal_anomalies = self._detect_temporal_anomalies(data)
        anomalies.extend(temporal_anomalies)
        
        # Detectar anomalias de distribuição
        distribution_anomalies = self._detect_distribution_anomalies(data)
        anomalies.extend(distribution_anomalies)
        
        # Detectar anomalias de sequência
        sequence_anomalies = self._detect_sequence_anomalies(data)
        anomalies.extend(sequence_anomalies)
        
        return anomalies
    
    def _detect_temporal_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detecta anomalias temporais."""
        anomalies = []
        
        timestamps = [entry.get('timestamp', 0) for entry in data if entry.get('timestamp')]
        if len(timestamps) < 5:
            return anomalies
        
        # Calcular intervalos
        intervals = []
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            if interval > 0:
                intervals.append(interval)
        
        if not intervals:
            return anomalies
        
        # Detectar intervalos muito longos ou muito curtos
        avg_interval = sum(intervals) / len(intervals)
        for i, interval in enumerate(intervals):
            if interval > avg_interval * 5:  # 5x maior que a média
                anomalies.append({
                    'type': 'temporal',
                    'description': f'Intervalo muito longo: {interval:.1f}s',
                    'index': i,
                    'severity': 'high'
                })
            elif interval < avg_interval * 0.1:  # 10x menor que a média
                anomalies.append({
                    'type': 'temporal',
                    'description': f'Intervalo muito curto: {interval:.1f}s',
                    'index': i,
                    'severity': 'medium'
                })
        
        return anomalies
    
    def _detect_distribution_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detecta anomalias de distribuição."""
        anomalies = []
        
        # Contar números
        numbers = [entry.get('roll', entry.get('number', 0)) for entry in data]
        number_counts = Counter(numbers)
        
        # Detectar números que aparecem muito raramente
        total = len(numbers)
        for number, count in number_counts.items():
            percentage = count / total
            if percentage < 0.02:  # Menos de 2%
                anomalies.append({
                    'type': 'distribution',
                    'description': f'Número {number} muito raro: {percentage:.1%}',
                    'value': number,
                    'severity': 'medium'
                })
        
        return anomalies
    
    def _detect_sequence_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detecta anomalias de sequência."""
        anomalies = []
        
        # Extrair cores
        colors = []
        for entry in data:
            number = entry.get('roll', entry.get('number', 0))
            if number == 0:
                colors.append('white')
            elif 1 <= number <= 7:
                colors.append('red')
            elif 8 <= number <= 14:
                colors.append('black')
        
        # Detectar sequências muito longas
        current_color = colors[0]
        current_count = 1
        max_count = 1
        max_start = 0
        
        for i in range(1, len(colors)):
            if colors[i] == current_color:
                current_count += 1
            else:
                if current_count > max_count:
                    max_count = current_count
                    max_start = i - current_count
                current_color = colors[i]
                current_count = 1
        
        if current_count > max_count:
            max_count = current_count
            max_start = len(colors) - current_count
        
        if max_count > 8:  # Sequência de mais de 8 iguais
            anomalies.append({
                'type': 'sequence',
                'description': f'Sequência muito longa de {max_count} {current_color}s',
                'start_index': max_start,
                'length': max_count,
                'severity': 'high'
            })
        
        return anomalies
