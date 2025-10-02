#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Padrões específicos do Double da Blaze
"""

from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime

class DoublePatternDetector:
    """Detector de padrões específicos do Double"""
    
    def __init__(self):
        self.patterns = {
            # Padrões clássicos
            'martingale': MartingalePattern(),
            'fibonacci': FibonacciPattern(),
            'd_alembert': DAlembertPattern(),
            'labouchere': LaboucherePattern(),
            'hot_cold': HotColdPattern(),
            'sequence': SequencePattern(),
            'alternation': AlternationPattern(),
            'white_bait': WhiteBaitPattern(),
            'color_balance': ColorBalancePattern(),
            'number_frequency': NumberFrequencyPattern(),
            # Padrões avançados existentes
            'paroli': ParoliPattern(),
            'oscars_grind': OscarsGrindPattern(),
            'one_three_two_six': OneTwoThreeSixPattern(),
            'james_bond': JamesBondPattern(),
            'reverse_martingale': ReverseMartingalePattern(),
            'sector_betting': SectorBettingPattern(),
            'mass_equality': MassEqualityPattern(),
            'sleeping_numbers': SleepingNumbersPattern(),
            'biased_detection': BiasedDetectionPattern(),
            'neighbor_betting': NeighborBettingPattern(),
            # 🆕 Novos padrões específicos do Double
            'low_numbers': LowNumbersPattern(),
            'high_numbers': HighNumbersPattern(),
            'middle_numbers': MiddleNumbersPattern(),
            # 🆕 Padrões matemáticos adaptados
            'double_sequence': DoubleSequencePattern(),
            'double_fibonacci': DoubleFibonacciPattern(),
            # 🆕 Padrões psicológicos
            'gambler_fallacy': GamblerFallacyPattern(),
            'hot_hand': HotHandPattern(),
            # 🆕 Padrões temporais
            'time_based': TimeBasedPattern(),
            # 🆕 Padrões específicos do Double
            'white_hot': WhiteHotPattern(),
            'red_black_balance': RedBlackBalancePattern(),
            # 🆕 Padrões baseados na análise da imagem
            'triple_repeat': TripleRepeatPattern(),
            'black_streak': BlackStreakPattern(),
            'red_streak': RedStreakPattern(),
            'white_proximity': WhiteProximityPattern(),
            # 🆕 Padrão identificado pelo usuário
            'red_after_red': RedAfterRedPattern(),
            # 🆕 Padrão específico do número 1
            'one_followed_by_red': OneFollowedByRedPattern(),
            # 🆕 Padrão específico do número 5
            'five_fifth_position_red': FiveFifthPositionRedPattern(),
            # 🆕 Padrão específico do número 14
            'fourteen_followed_by_black': FourteenFollowedByBlackPattern(),
            # 🆕 Padrão específico do número 12
            'twelve_future_white': TwelveFutureWhitePattern()
        }
    
    def detect_all_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta todos os padrões possíveis"""
        if len(results) < 5:
            return {'error': 'Dados insuficientes para análise'}
        
        detected_patterns = {}
        
        for pattern_name, pattern_detector in self.patterns.items():
            try:
                result = pattern_detector.detect(results)
                # AUMENTADO: Confiança mínima de 0.65 para 0.72 (mais seletivo)
                if result and result.get('confidence', 0) > 0.72:
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
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'high',
                'detected': True
            }
        return None

class FibonacciPattern:
    """Padrão Fibonacci - sequência de apostas"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                    'risk_level': 'medium',
                    'detected': True
                }
        return None

class DAlembertPattern:
    """Padrão D'Alembert - aumenta aposta após perda, diminui após ganho"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'low',
                'detected': True
            }
        return None

class LaboucherePattern:
    """Padrão Labouchere - sequência de números para apostas"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'medium',
                'detected': True
            }
        return None

class HotColdPattern:
    """Padrão de números quentes e frios"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'cold_numbers': cold_numbers,
                'detected': True
            }
        return None

class SequencePattern:
    """Padrão de sequências"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'high' if max_sequence >= 6 else 'medium',
                'detected': True
            }
        return None

class AlternationPattern:
    """Padrão de alternância"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'medium',
                'detected': True
            }
        return None

class WhiteBaitPattern:
    """Padrão da isca branca - branco seguido de cor específica"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                    'risk_level': 'medium',
                    'detected': True
                }
        return None

class ColorBalancePattern:
    """Padrão de equilíbrio de cores"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'low',
                'detected': True
            }
        return None

class NumberFrequencyPattern:
    """Padrão de frequência de números"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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
                'risk_level': 'medium',
                'detected': True
            }
        return None

# ============================================
# 🆕 NOVOS PADRÕES AVANÇADOS
# ============================================

class ParoliPattern:
    """Padrão Paroli - Progressão Positiva (dobra após vitória)"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 8:
            return None
        
        # Analisar sequências de vitórias
        colors = [r.get('color', '') for r in results[-15:]]
        
        # Detectar sequência de 2-3 vitórias consecutivas da mesma cor
        win_streaks = []
        current_streak = 1
        current_color = colors[0] if colors else ''
        
        for i in range(1, len(colors)):
            if colors[i] == current_color:
                current_streak += 1
            else:
                if current_streak >= 2:
                    win_streaks.append((current_color, current_streak))
                current_color = colors[i]
                current_streak = 1
        
        if current_streak >= 2:
            win_streaks.append((current_color, current_streak))
        
        if win_streaks:
            best_streak = max(win_streaks, key=lambda x: x[1])
            confidence = min(0.82, 0.55 + best_streak[1] * 0.08)
            
            return {
                'pattern_type': 'Paroli (Progressão Positiva)',
                'confidence': confidence,
                'description': f'Sequência de {best_streak[1]} vitórias em {best_streak[0]} detectada',
                'recommendation': f'Aplicar Paroli: dobrar aposta em {best_streak[0]}',
                'predicted_color': best_streak[0],
                'risk_level': 'medium',
                'detected': True
            }
        return None

class OscarsGrindPattern:
    """Padrão Oscar's Grind - Sistema de ganhos lentos e consistentes"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 12:
            return None
        
        colors = [r.get('color', '') for r in results[-20:]]
        color_counter = Counter(colors)
        
        # Verificar se há equilíbrio (característica do Oscar's Grind)
        total = len(colors)
        red_ratio = color_counter.get('red', 0) / total
        black_ratio = color_counter.get('black', 0) / total
        
        # Equilíbrio entre 40% e 60% para cada cor
        if 0.4 <= red_ratio <= 0.6 and 0.4 <= black_ratio <= 0.6:
            # Detectar pequenas sequências
            recent = colors[-5:]
            recent_counter = Counter(recent)
            most_common = recent_counter.most_common(1)[0]
            
            if most_common[1] >= 3:  # 3+ da mesma cor nos últimos 5
                confidence = 0.74
                predicted = 'black' if most_common[0] == 'red' else 'red'
                
                return {
                    'pattern_type': 'Oscar\'s Grind',
                    'confidence': confidence,
                    'description': f'Equilíbrio detectado com tendência recente de {most_common[0]}',
                    'recommendation': f'Sistema Oscar: apostar em {predicted} para reversão',
                    'predicted_color': predicted,
                    'risk_level': 'low',
                    'detected': True
                }
        return None

class OneTwoThreeSixPattern:
    """Padrão 1-3-2-6 - Sistema de gestão de lucro"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 10:
            return None
        
        colors = [r.get('color', '') for r in results[-12:]]
        
        # Detectar padrão de vitórias progressivas
        sequences = []
        i = 0
        while i < len(colors) - 3:
            # Verificar se há 4 cores iguais em padrão crescente
            if colors[i] == colors[i+1] == colors[i+2] == colors[i+3]:
                sequences.append((colors[i], 4))
                i += 4
            else:
                i += 1
        
        if sequences:
            confidence = 0.76
            last_seq = sequences[-1]
            
            return {
                'pattern_type': '1-3-2-6 System',
                'confidence': confidence,
                'description': f'Sequência de 4 {last_seq[0]}s - ideal para sistema 1-3-2-6',
                'recommendation': f'Aplicar progressão 1-3-2-6 em {last_seq[0]}',
                'predicted_color': last_seq[0],
                'risk_level': 'medium',
                'detected': True
            }
        return None

class JamesBondPattern:
    """Padrão James Bond - Cobertura estratégica de mesa"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 15:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-25:]]
        
        # Dividir em setores: baixo (1-7), médio (8-14), branco (0)
        low_sector = sum(1 for n in numbers if 1 <= n <= 7)
        high_sector = sum(1 for n in numbers if 8 <= n <= 14)
        white_count = sum(1 for n in numbers if n == 0)
        
        total = len(numbers)
        low_pct = low_sector / total
        high_pct = high_sector / total
        white_pct = white_count / total
        
        # Se um setor está muito ativo
        if low_pct > 0.55 or high_pct > 0.55:
            dominant_sector = 'red' if low_pct > high_pct else 'black'
            confidence = min(0.80, max(low_pct, high_pct) * 1.3)
            
            return {
                'pattern_type': 'James Bond Strategy',
                'confidence': confidence,
                'description': f'Setor {dominant_sector} predominante ({max(low_pct, high_pct):.1%})',
                'recommendation': f'Cobertura James Bond focada em {dominant_sector}',
                'predicted_color': dominant_sector,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class ReverseMartingalePattern:
    """Padrão Reverse Martingale (Anti-Martingale) - Dobra após vitória"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 10:
            return None
        
        colors = [r.get('color', '') for r in results[-15:]]
        
        # Detectar sequências de vitórias (mesma cor)
        max_streak = 1
        current_streak = 1
        streak_color = colors[0]
        
        for i in range(1, len(colors)):
            if colors[i] == colors[i-1]:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
                    streak_color = colors[i]
            else:
                current_streak = 1
        
        if max_streak >= 3:
            confidence = min(0.85, 0.60 + max_streak * 0.07)
            # Prever continuação da sequência
            
            return {
                'pattern_type': 'Anti-Martingale (Reverse)',
                'confidence': confidence,
                'description': f'Sequência de {max_streak} {streak_color}s - momentum detectado',
                'recommendation': f'Anti-Martingale: dobrar em {streak_color} aproveitando momentum',
                'predicted_color': streak_color,
                'risk_level': 'high',
                'detected': True
            }
        return None

class SectorBettingPattern:
    """Padrão de Apostas por Setor - Análise de setores da roleta"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 20:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-30:]]
        
        # Definir setores (0-4, 5-9, 10-14)
        sector_1 = sum(1 for n in numbers if 0 <= n <= 4)
        sector_2 = sum(1 for n in numbers if 5 <= n <= 9)
        sector_3 = sum(1 for n in numbers if 10 <= n <= 14)
        
        total = len(numbers)
        sectors = [
            ('Setor 0-4 (Vermelho)', sector_1 / total, 'red'),
            ('Setor 5-9 (Misto)', sector_2 / total, 'mixed'),
            ('Setor 10-14 (Preto)', sector_3 / total, 'black')
        ]
        
        # Encontrar setor mais quente
        hot_sector = max(sectors, key=lambda x: x[1])
        
        if hot_sector[1] > 0.40:  # Mais de 40% em um setor
            confidence = min(0.83, hot_sector[1] * 1.8)
            predicted = hot_sector[2] if hot_sector[2] != 'mixed' else 'red'
            
            return {
                'pattern_type': 'Setor Betting',
                'confidence': confidence,
                'description': f'{hot_sector[0]} está quente ({hot_sector[1]:.1%})',
                'recommendation': f'Apostar em números do {hot_sector[0]}',
                'predicted_color': predicted,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class MassEqualityPattern:
    """Padrão de Igualdade de Massa - Lei dos Grandes Números"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 30:
            return None
        
        colors = [r.get('color', '') for r in results[-50:]]
        counter = Counter(colors)
        
        total = len(colors)
        red_pct = counter.get('red', 0) / total
        black_pct = counter.get('black', 0) / total
        white_pct = counter.get('white', 0) / total
        
        # Identificar cor mais defasada
        expected = 1/3  # 33.3% para cada cor
        deviations = [
            ('red', abs(red_pct - expected), red_pct),
            ('black', abs(black_pct - expected), black_pct),
            ('white', abs(white_pct - expected), white_pct)
        ]
        
        # Ordenar por desvio (maior desvio = mais defasada)
        deviations.sort(key=lambda x: x[1], reverse=True)
        most_deviated = deviations[0]
        
        # Se há desvio significativo (mais de 15%)
        if most_deviated[1] > 0.15:
            # Apostar na cor mais defasada (lei dos grandes números)
            underdog = min(deviations, key=lambda x: x[2])[0]
            confidence = min(0.81, 0.50 + most_deviated[1] * 2.5)
            
            return {
                'pattern_type': 'Mass Equality (Lei dos Grandes Números)',
                'confidence': confidence,
                'description': f'{underdog.capitalize()} está {most_deviated[1]:.1%} abaixo da média',
                'recommendation': f'Apostar em {underdog} para equalização estatística',
                'predicted_color': underdog,
                'risk_level': 'low',
                'detected': True
            }
        return None

class SleepingNumbersPattern:
    """Padrão de Números Dormentes - Números que não saem há muito tempo"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 25:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-40:]]
        
        # Encontrar quando cada número apareceu pela última vez
        last_seen = {}
        for i, num in enumerate(numbers):
            last_seen[num] = i
        
        # Números de 0 a 14
        all_numbers = set(range(15))
        sleeping_numbers = []
        
        for num in all_numbers:
            if num not in last_seen:
                # Nunca apareceu nos últimos 40
                sleeping_numbers.append((num, 40))
            else:
                gap = len(numbers) - last_seen[num] - 1
                if gap >= 20:  # Não aparece há 20+ rodadas
                    sleeping_numbers.append((num, gap))
        
        if sleeping_numbers:
            # Ordenar por maior gap
            sleeping_numbers.sort(key=lambda x: x[1], reverse=True)
            sleepiest = sleeping_numbers[0]
            
            # Determinar cor do número dormindo
            if sleepiest[0] == 0:
                predicted_color = 'white'
            elif 1 <= sleepiest[0] <= 7:
                predicted_color = 'red'
            else:
                predicted_color = 'black'
            
            confidence = min(0.79, 0.45 + (sleepiest[1] / 40) * 0.4)
            
            return {
                'pattern_type': 'Sleeping Numbers (Números Dormentes)',
                'confidence': confidence,
                'description': f'Número {sleepiest[0]} não sai há {sleepiest[1]} rodadas',
                'recommendation': f'Apostar em cor {predicted_color} (número {sleepiest[0]} dormindo)',
                'predicted_color': predicted_color,
                'sleeping_number': sleepiest[0],
                'gap': sleepiest[1],
                'risk_level': 'medium',
                'detected': True
            }
        return None

class BiasedDetectionPattern:
    """Padrão de Detecção de Viés - Identifica viés no RNG"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 35:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-60:]]
        counter = Counter(numbers)
        
        # Teste qui-quadrado simplificado
        total = len(numbers)
        expected_freq = total / 15  # Frequência esperada para cada número
        
        chi_square = 0
        biased_numbers = []
        
        for num in range(15):
            observed = counter.get(num, 0)
            chi_square += ((observed - expected_freq) ** 2) / expected_freq
            
            # Se número aparece muito mais que o esperado
            if observed > expected_freq * 1.5:
                biased_numbers.append((num, observed, observed / total))
        
        # Valor crítico aproximado para qui-quadrado (14 graus de liberdade, α=0.05) ≈ 23.68
        if chi_square > 23.68 and biased_numbers:
            most_biased = max(biased_numbers, key=lambda x: x[1])
            
            # Determinar cor
            if most_biased[0] == 0:
                predicted_color = 'white'
            elif 1 <= most_biased[0] <= 7:
                predicted_color = 'red'
            else:
                predicted_color = 'black'
            
            confidence = min(0.88, 0.55 + (chi_square - 23.68) / 100)
            
            return {
                'pattern_type': 'Biased Wheel (Viés de RNG)',
                'confidence': confidence,
                'description': f'Viés detectado: número {most_biased[0]} aparece {most_biased[1]}x (χ²={chi_square:.2f})',
                'recommendation': f'Explorar viés: apostar em {predicted_color} (número {most_biased[0]})',
                'predicted_color': predicted_color,
                'biased_number': most_biased[0],
                'chi_square': chi_square,
                'risk_level': 'high',
                'detected': True
            }
        return None

class NeighborBettingPattern:
    """Padrão de Números Vizinhos - Analisa proximidade de números"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 15:
            return None
        
        numbers = [r.get('roll', 0) for r in results[-25:]]
        
        # Definir vizinhos (números próximos na sequência 0-14)
        neighbor_groups = [
            [0, 1, 14],  # Grupo ao redor do 0
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
            [12, 13, 14]
        ]
        
        # Contar quantos números de cada grupo apareceram
        group_scores = []
        for i, group in enumerate(neighbor_groups):
            count = sum(1 for n in numbers if n in group)
            if count >= 5:  # Grupo apareceu 5+ vezes
                group_scores.append((i, group, count, count / len(numbers)))
        
        if group_scores:
            # Grupo mais frequente
            hot_group = max(group_scores, key=lambda x: x[2])
            
            # Determinar cor predominante do grupo
            red_count = sum(1 for n in hot_group[1] if 1 <= n <= 7)
            black_count = sum(1 for n in hot_group[1] if 8 <= n <= 14)
            
            if red_count > black_count:
                predicted_color = 'red'
            elif black_count > red_count:
                predicted_color = 'black'
            else:
                predicted_color = 'white'
            
            confidence = min(0.84, 0.50 + hot_group[3] * 1.5)
            
            return {
                'pattern_type': 'Neighbor Betting (Vizinhos)',
                'confidence': confidence,
                'description': f'Grupo vizinho {hot_group[1]} está quente ({hot_group[2]} aparições)',
                'recommendation': f'Apostar em números vizinhos: {hot_group[1]}',
                'predicted_color': predicted_color,
                'neighbor_group': hot_group[1],
                'risk_level': 'medium',
                'detected': True
            }
class TripleRepeatPattern:
    """Padrão Tripla Repetição - Detecta quando o mesmo número aparece 3 vezes consecutivas"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 3:
            return None
        
        recent_numbers = [r.get('roll', 0) for r in results[-3:]]
        
        # Verificar se os últimos 3 números são iguais
        if len(set(recent_numbers)) == 1:  # Todos iguais
            repeated_number = recent_numbers[0]
            confidence = 0.88
            
            return {
                'pattern_type': 'Triple Repeat (Tripla Repetição)',
                'confidence': confidence,
                'description': f'Número {repeated_number} apareceu 3 vezes consecutivas',
                'recommendation': f'Evitar apostar em {repeated_number} (regressão à média esperada)',
                'repeated_number': repeated_number,
                'count': 3,
                'risk_level': 'high',
                'detected': True
            }
class BlackStreakPattern:
    """Padrão Sequência Preta - Detecta sequências longas de números pretos (8-14)"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 5:
            return None
        
        recent_colors = [r.get('color', '') for r in results[-10:]]
        
        # Contar sequências de pretos
        max_black_streak = 0
        current_streak = 0
        
        for color in recent_colors:
            if color == 'black':
                current_streak += 1
                max_black_streak = max(max_black_streak, current_streak)
            else:
                current_streak = 0
        
        if max_black_streak >= 4:  # Pelo menos 4 pretos consecutivos
            confidence = min(0.85, 0.50 + max_black_streak * 0.1)
            
            return {
                'pattern_type': 'Black Streak (Sequência Preta)',
                'confidence': confidence,
                'description': f'Sequência de {max_black_streak} números pretos consecutivos',
                'recommendation': 'Evitar apostar em preto (regressão à média esperada)',
                'streak_length': max_black_streak,
                'risk_level': 'high',
                'detected': True
            }
class RedStreakPattern:
    """Padrão Sequência Vermelha - Detecta sequências longas de números vermelhos (1-7)"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 5:
            return None
        
        recent_colors = [r.get('color', '') for r in results[-10:]]
        
        # Contar sequências de vermelhos
        max_red_streak = 0
        current_streak = 0
        
        for color in recent_colors:
            if color == 'red':
                current_streak += 1
                max_red_streak = max(max_red_streak, current_streak)
            else:
                current_streak = 0
        
        if max_red_streak >= 4:  # Pelo menos 4 vermelhos consecutivos
            confidence = min(0.85, 0.50 + max_red_streak * 0.1)
            
            return {
                'pattern_type': 'Red Streak (Sequência Vermelha)',
                'confidence': confidence,
                'description': f'Sequência de {max_red_streak} números vermelhos consecutivos',
                'recommendation': 'Evitar apostar em vermelho (regressão à média esperada)',
                'streak_length': max_red_streak,
                'risk_level': 'high',
                'detected': True
            }
class WhiteProximityPattern:
    """Padrão Proximidade do Branco - Detecta quando zeros aparecem próximos no tempo"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 10:
            return None
        
        recent_numbers = [r.get('roll', 0) for r in results[-10:]]
        
        # Encontrar posições dos zeros
        zero_positions = [i for i, num in enumerate(recent_numbers) if num == 0]
        
        if len(zero_positions) >= 2:
            # Calcular distância entre zeros consecutivos
            min_distance = min(zero_positions[i+1] - zero_positions[i] for i in range(len(zero_positions)-1))
            
            if min_distance <= 3:  # Zeros aparecem com distância de 3 ou menos
                confidence = min(0.80, 0.60 + (3 - min_distance) * 0.1)
                
                return {
                    'pattern_type': 'White Proximity (Proximidade do Branco)',
                    'confidence': confidence,
                    'description': f'Zeros aparecem próximos (distância mínima: {min_distance})',
                    'recommendation': 'Apostar em Zero (branco) - padrão de proximidade detectado',
                    'zero_count': len(zero_positions),
                    'min_distance': min_distance,
                    'risk_level': 'medium',
                    'detected': True
                }
        return None

class LowNumbersPattern:
    """Padrão Números Baixos - Detecta quando números baixos (0-7) estão aparecendo muito"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 15:
            return None
        
        # Números baixos no Double (0-7): 0=branco, 1-7=vermelho
        low_numbers = [0, 1, 2, 3, 4, 5, 6, 7]
        
        recent_numbers = [r.get('roll', 0) for r in results[-15:]]
        low_count = sum(1 for n in recent_numbers if n in low_numbers)
        
        if low_count >= 10:  # Mais de 2/3 são números baixos
            confidence = min(0.85, 0.50 + (low_count / 15) * 0.5)
            
            return {
                'pattern_type': 'Low Numbers (Números Baixos)',
                'confidence': confidence,
                'description': f'{low_count}/15 números recentes são baixos (0-7)',
                'recommendation': 'Apostar em números baixos: 0,1,2,3,4,5,6,7',
                'low_count': low_count,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class HighNumbersPattern:
    """Padrão Números Altos - Detecta quando números altos (8-14) estão aparecendo muito"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 15:
            return None
        
        # Números altos no Double (8-14): todos pretos
        high_numbers = [8, 9, 10, 11, 12, 13, 14]
        
        recent_numbers = [r.get('roll', 0) for r in results[-15:]]
        high_count = sum(1 for n in recent_numbers if n in high_numbers)
        
        if high_count >= 10:  # Mais de 2/3 são números altos
            confidence = min(0.85, 0.50 + (high_count / 15) * 0.5)
            
            return {
                'pattern_type': 'High Numbers (Números Altos)',
                'confidence': confidence,
                'description': f'{high_count}/15 números recentes são altos (8-14)',
                'recommendation': 'Apostar em números altos: 8,9,10,11,12,13,14',
                'high_count': high_count,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class MiddleNumbersPattern:
    """Padrão Números do Meio - Detecta quando números do meio (4-10) estão aparecendo muito"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 12:
            return None
        
        # Números do meio no Double (4-10): mistura de vermelho e preto
        middle_numbers = [4, 5, 6, 7, 8, 9, 10]
        
        recent_numbers = [r.get('roll', 0) for r in results[-12:]]
        middle_count = sum(1 for n in recent_numbers if n in middle_numbers)
        
        if middle_count >= 7:  # Mais da metade são números do meio
            confidence = min(0.82, 0.50 + (middle_count / 12) * 0.4)
            
            return {
                'pattern_type': 'Middle Numbers (Números do Meio)',
                'confidence': confidence,
                'description': f'{middle_count}/12 números recentes são do meio (4-10)',
                'recommendation': 'Apostar em números do meio: 4,5,6,7,8,9,10',
                'middle_count': middle_count,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class DoubleSequencePattern:
    """Padrão Sequência Double - Detecta sequências específicas do Double (0-14)"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 6:
            return None
        
        # Sequências comuns no Double
        sequences = [
            [0, 1, 2, 3, 4, 5],  # Sequência crescente baixa
            [5, 6, 7, 8, 9, 10],  # Sequência do meio
            [9, 10, 11, 12, 13, 14],  # Sequência crescente alta
            [14, 13, 12, 11, 10, 9],  # Sequência decrescente alta
            [7, 6, 5, 4, 3, 2],  # Sequência decrescente baixa
        ]
        
        recent_numbers = [r.get('roll', 0) for r in results[-6:]]
        
        for i, sequence in enumerate(sequences):
            if recent_numbers == sequence:
                sequence_names = [
                    'Sequência Crescente Baixa',
                    'Sequência do Meio',
                    'Sequência Crescente Alta',
                    'Sequência Decrescente Alta',
                    'Sequência Decrescente Baixa'
                ]
                
                return {
                    'pattern_type': 'Double Sequence',
                    'confidence': 0.90,
                    'description': f'{sequence_names[i]} detectada',
                    'recommendation': f'Seguir padrão {sequence_names[i]}',
                    'sequence': sequence,
                    'sequence_name': sequence_names[i],
                    'risk_level': 'low',
                    'detected': True
                }
        return None

class DoubleFibonacciPattern:
    """Padrão Fibonacci Double - Sequência Fibonacci adaptada para Double (0-14)"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 6:
            return None
        
        # Sequência Fibonacci adaptada para Double: 1, 1, 2, 3, 5, 8
        fibonacci_sequence = [1, 1, 2, 3, 5, 8]
        
        recent_numbers = [r.get('roll', 0) for r in results[-6:]]
        
        # Verificar se há sequência Fibonacci
        if recent_numbers == fibonacci_sequence:
            return {
                'pattern_type': 'Double Fibonacci',
                'confidence': 0.90,
                'description': 'Sequência Fibonacci adaptada para Double detectada',
                'recommendation': 'Seguir sequência Fibonacci nas apostas',
                'sequence': fibonacci_sequence,
                'risk_level': 'low',
                'detected': True
            }
        return None

class GamblerFallacyPattern:
    """Padrão Gambler's Fallacy - Evitar números que saíram muito"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 20:
            return None
        
        # Contar frequência de cada cor nos últimos 20 resultados
        colors = [r.get('color', '') for r in results[-20:]]
        color_count = Counter(colors)
        
        # Se uma cor apareceu muito mais que a outra
        max_count = max(color_count.values())
        min_count = min(color_count.values())
        
        if max_count >= 14:  # Uma cor apareceu em 70%+ dos casos
            overrepresented_color = max(color_count, key=color_count.get)
            confidence = min(0.75, 0.40 + (max_count / 20) * 0.5)
            
            return {
                'pattern_type': 'Gambler\'s Fallacy',
                'confidence': confidence,
                'description': f'Cor {overrepresented_color} apareceu {max_count}/20 vezes (Gambler\'s Fallacy)',
                'recommendation': f'Evitar apostar em {overrepresented_color} (regressão à média esperada)',
                'overrepresented_color': overrepresented_color,
                'count': max_count,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class HotHandPattern:
    """Padrão Hot Hand - Continuar apostando na cor que está "quente" """
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 8:
            return None
        
        # Verificar sequências de mesma cor
        colors = [r.get('color', '') for r in results[-8:]]
        
        # Contar sequências de mesma cor
        current_color = colors[0]
        streak = 1
        max_streak = 1
        
        for i in range(1, len(colors)):
            if colors[i] == current_color:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                current_color = colors[i]
                streak = 1
        
        if max_streak >= 4:  # Pelo menos 4 consecutivos
            confidence = min(0.85, 0.50 + max_streak * 0.1)
            
            return {
                'pattern_type': 'Hot Hand',
                'confidence': confidence,
                'description': f'Sequência de {max_streak} {current_color} consecutivos',
                'recommendation': f'Continuar apostando em {current_color} (Hot Hand)',
                'hot_color': current_color,
                'streak': max_streak,
                'risk_level': 'high',
                'detected': True
            }
        return None

class TimeBasedPattern:
    """Padrão Temporal - Análise baseada no horário"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 15:
            return None
        
        # Analisar padrões por horário (simulado)
        # Em um sistema real, você usaria timestamps reais
        hour_patterns = {
            'morning': {'red': 0.6, 'black': 0.3, 'white': 0.1},
            'afternoon': {'red': 0.4, 'black': 0.5, 'white': 0.1},
            'evening': {'red': 0.3, 'black': 0.6, 'white': 0.1},
            'night': {'red': 0.5, 'black': 0.4, 'white': 0.1}
        }
        
        # Simular análise temporal (em produção, usar timestamps reais)
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            time_period = 'morning'
        elif 12 <= current_hour < 18:
            time_period = 'afternoon'
        elif 18 <= current_hour < 24:
            time_period = 'evening'
        else:
            time_period = 'night'
        
        # Verificar se o padrão atual coincide com o padrão histórico do período
        recent_colors = [r.get('color', '') for r in results[-15:]]
        color_distribution = Counter(recent_colors)
        total = sum(color_distribution.values())
        
        if total > 0:
            red_ratio = color_distribution.get('red', 0) / total
            black_ratio = color_distribution.get('black', 0) / total
            
            expected_pattern = hour_patterns[time_period]
            
            # Calcular similaridade com padrão esperado
            similarity = 1 - abs(red_ratio - expected_pattern['red']) - abs(black_ratio - expected_pattern['black'])
            
            if similarity > 0.7:
                confidence = min(0.80, similarity * 0.9)
                
                return {
                    'pattern_type': 'Time-Based Pattern',
                    'confidence': confidence,
                    'description': f'Padrão temporal {time_period} detectado',
                    'recommendation': f'Seguir padrão histórico do período {time_period}',
                    'time_period': time_period,
                    'similarity': similarity,
                    'risk_level': 'medium',
                    'detected': True
                }
        return None

class WhiteHotPattern:
    """Padrão Branco Quente - Análise específica do número 0 (branco) no Double"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 20:
            return None
        
        # Contar aparições do zero nos últimos 20 resultados
        recent_numbers = [r.get('roll', 0) for r in results[-20:]]
        zero_count = recent_numbers.count(0)
        
        # Zero aparece em média 1 vez a cada 15 números (6.67%)
        expected_zeros = 20 * (1/15)  # ~1.33 zeros esperados
        
        if zero_count >= 3:  # Mais que o esperado
            confidence = min(0.85, 0.50 + (zero_count / 20) * 0.5)
            
            return {
                'pattern_type': 'White Hot (Branco Quente)',
                'confidence': confidence,
                'description': f'Zero apareceu {zero_count}/20 vezes (acima da média)',
                'recommendation': 'Apostar em Zero (branco) - está quente',
                'zero_count': zero_count,
                'expected': expected_zeros,
                'risk_level': 'high',
                'detected': True
            }
        elif zero_count == 0:  # Zero não apareceu há tempo
            confidence = min(0.75, 0.40 + (20 - zero_count) * 0.02)
            
            return {
                'pattern_type': 'White Cold (Branco Frio)',
                'confidence': confidence,
                'description': f'Zero não apareceu nos últimos 20 resultados',
                'recommendation': 'Evitar Zero (branco) - está frio',
                'zero_count': zero_count,
                'expected': expected_zeros,
                'risk_level': 'medium',
                'detected': True
            }
        return None

class RedBlackBalancePattern:
    """Padrão Equilíbrio Vermelho/Preto - Análise de balanço"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 30:
            return None
        
        # Analisar equilíbrio entre vermelho e preto
        colors = [r.get('color', '') for r in results[-30:]]
        red_count = colors.count('red')
        black_count = colors.count('black')
        white_count = colors.count('white')
        
        # Calcular desequilíbrio
        imbalance = abs(red_count - black_count)
        total_colored = red_count + black_count
        
        if total_colored > 0:
            imbalance_ratio = imbalance / total_colored
            
            if imbalance_ratio > 0.3:  # Desequilíbrio significativo
                dominant_color = 'red' if red_count > black_count else 'black'
                confidence = min(0.80, 0.50 + imbalance_ratio * 0.4)
                
                return {
                    'pattern_type': 'Red/Black Imbalance',
                    'confidence': confidence,
                    'description': f'Desequilíbrio detectado: {red_count} vermelhos vs {black_count} pretos',
                    'recommendation': f'Apostar em {dominant_color} para equilibrar',
                    'red_count': red_count,
                    'black_count': black_count,
                    'imbalance_ratio': imbalance_ratio,
                    'dominant_color': dominant_color,
                    'risk_level': 'medium',
                    'detected': True
                }
        return None

class RedAfterRedPattern:
    """Padrão Red After Red - Detecta quando após 1 red vem outro red"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 3: return None
        
        # Analisar últimos 20 resultados para detectar o padrão
        recent_results = results[-20:] if len(results) >= 20 else results
        
        # Contar sequências de "red após red"
        red_after_red_count = 0
        total_red_sequences = 0
        
        for i in range(len(recent_results) - 1):
            current_color = recent_results[i].get('color', '')
            next_color = recent_results[i + 1].get('color', '')
            
            if current_color == 'red':
                total_red_sequences += 1
                if next_color == 'red':
                    red_after_red_count += 1
        
        # Calcular taxa de ocorrência
        if total_red_sequences > 0:
            red_after_red_rate = red_after_red_count / total_red_sequences
            
            # Detectar padrão se taxa for alta (acima de 50% - ajustado para ser mais sensível)
            if red_after_red_rate >= 0.50 and total_red_sequences >= 3:
                confidence = min(0.90, 0.50 + red_after_red_rate * 0.4)
                
                # Verificar último resultado para determinar recomendação
                last_result = recent_results[-1]
                last_color = last_result.get('color', '')
                
                if last_color == 'red':
                    recommendation = "Apostar em RED - padrão 'Red After Red' detectado"
                    predicted_color = "red"
                else:
                    recommendation = "Aguardar próximo RED para aplicar padrão"
                    predicted_color = "red"
                
                return {
                    'pattern_type': 'Red After Red (Vermelho Após Vermelho)',
                    'confidence': confidence,
                    'description': f'Após {total_red_sequences} vermelhos, {red_after_red_count} foram seguidos por outro vermelho ({red_after_red_rate:.1%})',
                    'recommendation': recommendation,
                    'predicted_color': predicted_color,
                    'red_after_red_count': red_after_red_count,
                    'total_red_sequences': total_red_sequences,
                    'success_rate': red_after_red_rate,
                    'risk_level': 'medium',
                    'detected': True
                }
        
        return None

class OneFollowedByRedPattern:
    """Padrão Number 1 Followed by Red - Detecta quando após o número 1 vem red"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 3: return None
        
        # Analisar últimos 30 resultados para detectar o padrão
        recent_results = results[-30:] if len(results) >= 30 else results
        
        # Contar sequências de "número 1 seguido por red"
        one_followed_by_red_count = 0
        total_one_sequences = 0
        
        for i in range(len(recent_results) - 1):
            current_number = recent_results[i].get('roll', 0)
            next_color = recent_results[i + 1].get('color', '')
            
            if current_number == 1:
                total_one_sequences += 1
                if next_color == 'red':
                    one_followed_by_red_count += 1
        
        # Calcular taxa de ocorrência
        if total_one_sequences > 0:
            one_followed_by_red_rate = one_followed_by_red_count / total_one_sequences
            
            # Detectar padrão se taxa for alta (acima de 30% - muito sensível para padrão específico)
            if one_followed_by_red_rate >= 0.30 and total_one_sequences >= 2:
                confidence = min(0.95, 0.60 + one_followed_by_red_rate * 0.3)
                
                # Verificar último resultado para determinar recomendação
                last_result = recent_results[-1]
                last_number = last_result.get('roll', 0)
                
                if last_number == 1:
                    recommendation = "Apostar em RED - padrão 'Number 1 → Red' detectado"
                    predicted_color = "red"
                else:
                    recommendation = "Aguardar próximo número 1 para aplicar padrão"
                    predicted_color = "red"
                
                return {
                    'pattern_type': 'Number 1 Followed by Red (Número 1 Seguido por Vermelho)',
                    'confidence': confidence,
                    'description': f'Após {total_one_sequences} números 1, {one_followed_by_red_count} foram seguidos por RED ({one_followed_by_red_rate:.1%})',
                    'recommendation': recommendation,
                    'predicted_color': predicted_color,
                    'one_followed_by_red_count': one_followed_by_red_count,
                    'total_one_sequences': total_one_sequences,
                    'success_rate': one_followed_by_red_rate,
                    'risk_level': 'medium',
                    'detected': True
                }
        
        return None

class FiveFifthPositionRedPattern:
    """Padrão Number 5 → 5th Position Red - Detecta quando após número 5, na 5ª posição vem red"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 10: return None
        
        # Analisar últimos 50 resultados para detectar o padrão
        recent_results = results[-50:] if len(results) >= 50 else results
        
        # Contar sequências de "número 5 seguido por red na 5ª posição"
        five_fifth_red_count = 0
        total_five_sequences = 0
        gale_success_count = 0  # Contador para sistema de Gale
        
        for i in range(len(recent_results) - 5):  # Precisa de pelo menos 5 posições à frente
            current_number = recent_results[i].get('roll', 0)
            
            if current_number == 5:
                total_five_sequences += 1
                
                # Verificar se na 5ª posição (i+5) vem red
                if i + 5 < len(recent_results):
                    fifth_position_color = recent_results[i + 5].get('color', '')
                    if fifth_position_color == 'red':
                        five_fifth_red_count += 1
                    else:
                        # Sistema de Gale: verificar se na 6ª posição vem red
                        if i + 6 < len(recent_results):
                            sixth_position_color = recent_results[i + 6].get('color', '')
                            if sixth_position_color == 'red':
                                gale_success_count += 1
        
        # Calcular taxa de ocorrência
        if total_five_sequences > 0:
            five_fifth_red_rate = five_fifth_red_count / total_five_sequences
            gale_success_rate = gale_success_count / total_five_sequences
            total_success_rate = (five_fifth_red_count + gale_success_count) / total_five_sequences
            
            # Detectar padrão se taxa for alta (acima de 40%)
            if total_success_rate >= 0.40 and total_five_sequences >= 3:
                confidence = min(0.95, 0.50 + total_success_rate * 0.4)
                
                # Verificar se há número 5 recente para aplicar o padrão
                last_five_position = -1
                for i in range(len(recent_results) - 1, -1, -1):
                    if recent_results[i].get('roll', 0) == 5:
                        last_five_position = i
                        break
                
                if last_five_position >= 0:
                    positions_since_five = len(recent_results) - 1 - last_five_position
                    
                    if positions_since_five < 5:
                        recommendation = f"Apostar em RED na {5 - positions_since_five}ª posição (padrão 'Number 5 → 5th Red' detectado)"
                        predicted_color = "red"
                        gale_recommendation = f"Se não sair, usar Gale na {6 - positions_since_five}ª posição"
                    elif positions_since_five == 5:
                        recommendation = "Apostar em RED AGORA! (5ª posição após número 5)"
                        predicted_color = "red"
                        gale_recommendation = "Se não sair, usar Gale na próxima posição"
                    else:
                        recommendation = "Aguardar próximo número 5 para aplicar padrão"
                        predicted_color = "red"
                        gale_recommendation = ""
                else:
                    recommendation = "Aguardar próximo número 5 para aplicar padrão"
                    predicted_color = "red"
                    gale_recommendation = ""
                
                return {
                    'pattern_type': 'Number 5 → 5th Position Red (Número 5 → 5ª Posição Vermelho)',
                    'confidence': confidence,
                    'description': f'Após {total_five_sequences} números 5: {five_fifth_red_count} reds na 5ª posição + {gale_success_count} reds na 6ª posição (Gale) = {total_success_rate:.1%}',
                    'recommendation': recommendation,
                    'gale_recommendation': gale_recommendation,
                    'predicted_color': predicted_color,
                    'five_fifth_red_count': five_fifth_red_count,
                    'gale_success_count': gale_success_count,
                    'total_five_sequences': total_five_sequences,
                    'direct_success_rate': five_fifth_red_rate,
                    'gale_success_rate': gale_success_rate,
                    'total_success_rate': total_success_rate,
                    'risk_level': 'medium',
                    'detected': True
                }
        
        return None
class FourteenFollowedByBlackPattern:
    """Padrão Number 14 Followed by Black - Detecta quando após o número 14 vem black"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 3: return None
        
        # Analisar últimos 30 resultados para detectar o padrão
        recent_results = results[-30:] if len(results) >= 30 else results
        
        # Contar sequências de "número 14 seguido por black"
        fourteen_followed_by_black_count = 0
        total_fourteen_sequences = 0
        
        for i in range(len(recent_results) - 1):
            current_number = recent_results[i].get('roll', 0)
            next_color = recent_results[i + 1].get('color', '')
            
            if current_number == 14:
                total_fourteen_sequences += 1
                if next_color == 'black':
                    fourteen_followed_by_black_count += 1
        
        # Calcular taxa de ocorrência
        if total_fourteen_sequences > 0:
            fourteen_followed_by_black_rate = fourteen_followed_by_black_count / total_fourteen_sequences
            
            # Detectar padrão se taxa for alta (acima de 50% - ajustado para ser mais sensível)
            if fourteen_followed_by_black_rate >= 0.50 and total_fourteen_sequences >= 1:
                confidence = min(0.95, 0.60 + fourteen_followed_by_black_rate * 0.3)
                
                # Verificar último resultado para determinar recomendação
                last_result = recent_results[-1]
                last_number = last_result.get('roll', 0)
                
                if last_number == 14:
                    recommendation = "Apostar em BLACK - padrão 'Number 14 → Black' detectado"
                    predicted_color = "black"
                else:
                    recommendation = "Aguardar próximo número 14 para aplicar padrão"
                    predicted_color = "black"
                
                return {
                    'pattern_type': 'Number 14 Followed by Black (Número 14 Seguido por Preto)',
                    'confidence': confidence,
                    'description': f'Após {total_fourteen_sequences} números 14, {fourteen_followed_by_black_count} foram seguidos por BLACK ({fourteen_followed_by_black_rate:.1%})',
                    'recommendation': recommendation,
                    'predicted_color': predicted_color,
                    'fourteen_followed_by_black_count': fourteen_followed_by_black_count,
                    'total_fourteen_sequences': total_fourteen_sequences,
                    'success_rate': fourteen_followed_by_black_rate,
                    'risk_level': 'medium',
                    'detected': True
                }
        
        return None
class TwelveFutureWhitePattern:
    """Padrão Number 12 → Future White - Detecta quando após número 12, algumas jogadas à frente vem white"""
    
    def detect(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if len(results) < 8: return None
        
        # Analisar últimos 40 resultados para detectar o padrão
        recent_results = results[-40:] if len(results) >= 40 else results
        
        # Contar sequências de "número 12 seguido por white em posições futuras"
        twelve_future_white_count = 0
        total_twelve_sequences = 0
        white_positions = []  # Armazenar posições onde white apareceu
        
        for i in range(len(recent_results) - 7):  # Precisa de pelo menos 7 posições à frente
            current_number = recent_results[i].get('roll', 0)
            
            if current_number == 12:
                total_twelve_sequences += 1
                
                # Verificar se white aparece nas próximas 7 posições (2ª a 8ª posição)
                white_found = False
                white_position = -1
                
                for j in range(1, 8):  # Verificar posições 1 a 7 à frente
                    if i + j < len(recent_results):
                        future_color = recent_results[i + j].get('color', '')
                        if future_color == 'white':
                            white_found = True
                            white_position = j
                            break
                
                if white_found:
                    twelve_future_white_count += 1
                    white_positions.append(white_position)
        
        # Calcular taxa de ocorrência
        if total_twelve_sequences > 0:
            twelve_future_white_rate = twelve_future_white_count / total_twelve_sequences
            
            # Detectar padrão se taxa for alta (acima de 40%)
            if twelve_future_white_rate >= 0.40 and total_twelve_sequences >= 2:
                confidence = min(0.95, 0.50 + twelve_future_white_rate * 0.4)
                
                # Calcular posição média onde white aparece
                avg_position = sum(white_positions) / len(white_positions) if white_positions else 0
                
                # Verificar se há número 12 recente para aplicar o padrão
                last_twelve_position = -1
                for i in range(len(recent_results) - 1, -1, -1):
                    if recent_results[i].get('roll', 0) == 12:
                        last_twelve_position = i
                        break
                
                if last_twelve_position >= 0:
                    positions_since_twelve = len(recent_results) - 1 - last_twelve_position
                    
                    if positions_since_twelve < 7:
                        recommendation = f"Apostar em WHITE nas próximas {7 - positions_since_twelve} jogadas (padrão 'Number 12 → Future White' detectado)"
                        predicted_color = "white"
                        timing_info = f"White geralmente aparece na {avg_position:.1f}ª posição após 12"
                    else:
                        recommendation = "Aguardar próximo número 12 para aplicar padrão"
                        predicted_color = "white"
                        timing_info = ""
                else:
                    recommendation = "Aguardar próximo número 12 para aplicar padrão"
                    predicted_color = "white"
                    timing_info = ""
                
                return {
                    'pattern_type': 'Number 12 → Future White (Número 12 → White Futuro)',
                    'confidence': confidence,
                    'description': f'Após {total_twelve_sequences} números 12: {twelve_future_white_count} whites nas próximas 7 posições ({twelve_future_white_rate:.1%})',
                    'recommendation': recommendation,
                    'timing_info': timing_info,
                    'predicted_color': predicted_color,
                    'twelve_future_white_count': twelve_future_white_count,
                    'total_twelve_sequences': total_twelve_sequences,
                    'success_rate': twelve_future_white_rate,
                    'average_white_position': avg_position,
                    'white_positions': white_positions,
                    'risk_level': 'medium',
                    'detected': True
                }
        
        return None
