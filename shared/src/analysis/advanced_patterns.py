#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Padrões avançados para análise do Blaze Double
"""

from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import math

class HotNumbersPattern:
    """Detecta números que aparecem com frequência acima da média"""
    
    def __init__(self, window_size=20, threshold=4):  # Aumentado de 3 para 4
        self.window_size = window_size
        self.threshold = threshold
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < self.window_size:
            return {}
        
        # Pegar últimos N resultados
        recent_data = data[-self.window_size:]
        numbers = [r.get('roll', 0) for r in recent_data]
        
        # Contar ocorrências
        number_counts = Counter(numbers)
        
        # Calcular média esperada
        expected_avg = self.window_size / 15  # 15 números possíveis (0-14)
        
        # Encontrar números "quentes"
        hot_numbers = []
        for number, count in number_counts.items():
            if count >= self.threshold and count > expected_avg * 1.5:
                hot_numbers.append({
                    'number': number,
                    'count': count,
                    'frequency': count / self.window_size,
                    'strength': count / expected_avg
                })
        
        if hot_numbers:
            return {
                'pattern_name': 'hot_numbers',
                'hot_numbers': hot_numbers,
                'recommendation': 'Apostar em números quentes',
                'confidence': min(0.9, max(0.5, hot_numbers[0]['strength'] / 2))
            }
        
        return {}

class ColdNumbersPattern:
    """Detecta números que não aparecem há muito tempo"""
    
    def __init__(self, min_gap=12):  # Reduzido de 15 para 12
        self.min_gap = min_gap
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < self.min_gap:
            return {}
        
        # Calcular última aparição de cada número
        last_appearance = {}
        for i, result in enumerate(data):
            number = result.get('roll', 0)
            last_appearance[number] = i
        
        # Encontrar números "frios"
        cold_numbers = []
        current_position = len(data) - 1
        
        for number in range(15):  # 0-14
            if number in last_appearance:
                gap = current_position - last_appearance[number]
                if gap >= self.min_gap:
                    cold_numbers.append({
                        'number': number,
                        'gap': gap,
                        'strength': gap / self.min_gap
                    })
        
        if cold_numbers:
            # Ordenar por gap (maior primeiro)
            cold_numbers.sort(key=lambda x: x['gap'], reverse=True)
            return {
                'pattern_name': 'cold_numbers',
                'cold_numbers': cold_numbers,
                'recommendation': 'Evitar números frios',
                'confidence': min(0.8, cold_numbers[0]['strength'] / 2)
            }
        
        return {}

class FibonacciPattern:
    """Detecta sequências de Fibonacci nos resultados"""
    
    def __init__(self):
        self.fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13]
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < 3:
            return {}
        
        # Pegar últimos números
        recent_numbers = [r.get('roll', 0) for r in data[-10:]]
        
        # Procurar por sequências de Fibonacci
        for i in range(len(recent_numbers) - 2):
            sequence = recent_numbers[i:i+3]
            if sequence in self.fibonacci_sequence:
                # Calcular próximo número da sequência
                next_fib = self._get_next_fibonacci(sequence[-1])
                return {
                    'pattern_name': 'fibonacci',
                    'sequence': sequence,
                    'next_number': next_fib,
                    'recommendation': f'Apostar no número {next_fib} (Fibonacci)',
                    'confidence': 0.7
                }
        
        return {}
    
    def _get_next_fibonacci(self, last_number: int) -> int:
        """Calcula próximo número da sequência de Fibonacci"""
        if last_number == 1:
            return 2
        elif last_number == 2:
            return 3
        elif last_number == 3:
            return 5
        elif last_number == 5:
            return 8
        elif last_number == 8:
            return 13
        else:
            return 1

class PrimeNumbersPattern:
    """Detecta padrões com números primos"""
    
    def __init__(self):
        self.prime_numbers = [2, 3, 5, 7, 11, 13]
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < 3:
            return {}
        
        # Pegar últimos números
        recent_numbers = [r.get('roll', 0) for r in data[-10:]]
        
        # Contar números primos consecutivos
        prime_count = 0
        max_prime_count = 0
        
        for number in recent_numbers:
            if number in self.prime_numbers:
                prime_count += 1
                max_prime_count = max(max_prime_count, prime_count)
            else:
                prime_count = 0
        
        if max_prime_count >= 2:  # Reduzido de 3 para 2
            # Recomendar próximo número primo
            last_number = recent_numbers[-1]
            next_prime = self._get_next_prime(last_number)
            
            return {
                'pattern_name': 'prime_numbers',
                'prime_count': max_prime_count,
                'next_prime': next_prime,
                'recommendation': f'Apostar no número primo {next_prime}',
                'confidence': min(0.8, max_prime_count / 5)
            }
        
        return {}
    
    def _get_next_prime(self, last_number: int) -> int:
        """Retorna próximo número primo"""
        for prime in self.prime_numbers:
            if prime > last_number:
                return prime
        return 2  # Volta ao início

class EvenOddPattern:
    """Detecta padrões de números pares/ímpares"""
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < 5:
            return {}
        
        # Pegar últimos números
        recent_numbers = [r.get('roll', 0) for r in data[-10:]]
        
        # Contar pares e ímpares consecutivos
        even_count = 0
        odd_count = 0
        max_even = 0
        max_odd = 0
        
        for number in recent_numbers:
            if number == 0:  # 0 é considerado par
                even_count += 1
                odd_count = 0
                max_even = max(max_even, even_count)
            elif number % 2 == 0:
                even_count += 1
                odd_count = 0
                max_even = max(max_even, even_count)
            else:
                odd_count += 1
                even_count = 0
                max_odd = max(max_odd, odd_count)
        
        # Detectar padrão
        if max_even >= 4:  # Reduzido de 5 para 4
            return {
                'pattern_name': 'even_odd',
                'type': 'even_streak',
                'count': max_even,
                'recommendation': 'Apostar em número ímpar (quebrar sequência par)',
                'confidence': min(0.8, max_even / 8)
            }
        elif max_odd >= 4:  # Reduzido de 5 para 4
            return {
                'pattern_name': 'even_odd',
                'type': 'odd_streak',
                'count': max_odd,
                'recommendation': 'Apostar em número par (quebrar sequência ímpar)',
                'confidence': min(0.8, max_odd / 8)
            }
        
        return {}

class VolatilityPattern:
    """Analisa volatilidade dos resultados"""
    
    def __init__(self, window_size=20):
        self.window_size = window_size
    
    def detect(self, data: List[Dict]) -> Dict:
        if len(data) < self.window_size:
            return {}
        
        # Pegar últimos números
        recent_numbers = [r.get('roll', 0) for r in data[-self.window_size:]]
        
        # Calcular desvio padrão
        mean = sum(recent_numbers) / len(recent_numbers)
        variance = sum((x - mean) ** 2 for x in recent_numbers) / len(recent_numbers)
        std_dev = math.sqrt(variance)
        
        # Calcular volatilidade relativa
        expected_std = 4.33  # Desvio padrão esperado para números 0-14
        volatility_ratio = std_dev / expected_std
        
        if volatility_ratio > 1.5:  # Alta volatilidade
            return {
                'pattern_name': 'volatility',
                'type': 'high',
                'ratio': volatility_ratio,
                'recommendation': 'Reduzir tamanho da aposta (alta volatilidade)',
                'confidence': min(0.9, volatility_ratio / 2)
            }
        elif volatility_ratio < 0.5:  # Baixa volatilidade
            return {
                'pattern_name': 'volatility',
                'type': 'low',
                'ratio': volatility_ratio,
                'recommendation': 'Aumentar tamanho da aposta (baixa volatilidade)',
                'confidence': min(0.8, (1 - volatility_ratio) * 2)
            }
        
        return {}

class AdvancedPatternDetector:
    """Detector avançado que combina múltiplos padrões"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # Padrões disponíveis
        self.patterns = {
            'hot_numbers': HotNumbersPattern(),
            'cold_numbers': ColdNumbersPattern(),
            'fibonacci': FibonacciPattern(),
            'prime_numbers': PrimeNumbersPattern(),
            'even_odd': EvenOddPattern(),
            'volatility': VolatilityPattern()
        }
        
        # Pesos para combinar padrões (ajustados baseado na performance)
        self.pattern_weights = {
            'hot_numbers': 0.95,  # Aumentado - muito confiável
            'cold_numbers': 0.85,  # Aumentado - bom para evitar
            'fibonacci': 0.60,     # Reduzido - menos confiável
            'prime_numbers': 0.70, # Aumentado - bom para detectar
            'even_odd': 0.45,      # Reduzido - menos confiável
            'volatility': 0.35     # Reduzido - mais informativo que preditivo
        }
        
        # Padrões ativos (configurável)
        self.active_patterns = self.config.get('active_patterns', list(self.patterns.keys()))
    
    def detect_all_patterns(self, data: List[Dict]) -> Dict:
        """Detecta todos os padrões ativos e combina os resultados"""
        results = {}
        active_patterns = []
        
        # Executar apenas padrões ativos
        for pattern_name in self.active_patterns:
            if pattern_name in self.patterns:
                try:
                    result = self.patterns[pattern_name].detect(data)
                    if result:
                        results[pattern_name] = result
                        active_patterns.append(pattern_name)
                except Exception as e:
                    print(f"Erro ao executar padrão {pattern_name}: {e}")
        
        # Combinar resultados
        if active_patterns:
            # Calcular confiança combinada
            total_weight = sum(self.pattern_weights[p] for p in active_patterns)
            combined_confidence = sum(
                results[p]['confidence'] * self.pattern_weights[p] 
                for p in active_patterns
            ) / total_weight
            
            return {
                'patterns_detected': active_patterns,
                'pattern_count': len(active_patterns),
                'combined_confidence': combined_confidence,
                'individual_results': results,
                'recommendation': self._generate_combined_recommendation(results)
            }
        
        return {}

    def _generate_combined_recommendation(self, results: Dict) -> str:
        """Gera recomendação combinada baseada nos padrões detectados"""
        recommendations = []
        
        for pattern_name, result in results.items():
            if 'recommendation' in result:
                recommendations.append(result['recommendation'])
        
        if recommendations:
            return " | ".join(recommendations[:3])  # Máximo 3 recomendações
        else:
            return "Nenhum padrão forte detectado"
    
    def set_active_patterns(self, patterns: List[str]):
        """Define quais padrões estão ativos"""
        self.active_patterns = [p for p in patterns if p in self.patterns]
    
    def get_available_patterns(self) -> List[str]:
        """Retorna lista de padrões disponíveis"""
        return list(self.patterns.keys())
