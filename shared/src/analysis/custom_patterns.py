"""
Sistema de Padrões Personalizados para Double
Permite criar e gerenciar padrões customizados pelo usuário
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os


class PatternTrigger(Enum):
    """Tipos de gatilhos para padrões personalizados"""
    NUMBER_FOLLOWED_BY_COLOR = "number_followed_by_color"
    COLOR_SEQUENCE = "color_sequence"
    NUMBER_SEQUENCE = "number_sequence"
    COLOR_AFTER_COLOR = "color_after_color"
    NUMBER_AFTER_NUMBER = "number_after_number"
    NUMBER_DELAY_ALERT = "number_delay_alert"
    CUSTOM_LOGIC = "custom_logic"


class PatternAction(Enum):
    """Ações que o padrão pode executar"""
    BET_COLOR = "bet_color"
    BET_NUMBER = "bet_number"
    BET_SECTOR = "bet_sector"
    SKIP_BET = "skip_bet"
    WAIT = "wait"


@dataclass
class CustomPattern:
    """Representa um padrão personalizado"""
    pattern_id: str
    name: str
    description: str
    trigger_type: PatternTrigger
    trigger_config: Dict[str, Any]  # Configuração específica do gatilho
    action: PatternAction
    action_config: Dict[str, Any]  # Configuração da ação
    confidence_threshold: float = 0.7
    cooldown_minutes: int = 5
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    success_count: int = 0
    failure_count: int = 0
    last_triggered: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class CustomPatternManager:
    """Gerenciador de padrões personalizados"""
    
    def __init__(self, db_path: str = "data/custom_patterns.db"):
        self.db_path = db_path
        self.patterns_cache = {}
        self.last_cache_update = None
        self._init_database()
        self._load_patterns()
    
    def _enum_to_string(self, enum_value):
        """Converte enum para string de forma segura"""
        if hasattr(enum_value, 'value'):
            return enum_value.value
        elif isinstance(enum_value, str):
            return enum_value
        return str(enum_value)
    
    def _init_database(self):
        """Inicializa o banco de dados para padrões personalizados"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS custom_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_type TEXT NOT NULL,
                    trigger_config TEXT NOT NULL,
                    action TEXT NOT NULL,
                    action_config TEXT NOT NULL,
                    confidence_threshold REAL DEFAULT 0.7,
                    cooldown_minutes INTEGER DEFAULT 5,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_triggered TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT NOT NULL,
                    triggered_at TEXT NOT NULL,
                    result_number INTEGER NOT NULL,
                    result_color TEXT NOT NULL,
                    was_successful BOOLEAN,
                    FOREIGN KEY (pattern_id) REFERENCES custom_patterns (pattern_id)
                )
            """)
    
    def _load_patterns(self):
        """Carrega padrões do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM custom_patterns WHERE enabled = 1")
            
            for row in cursor.fetchall():
                # Converter strings para enums se necessário
                trigger_type = row['trigger_type']
                if isinstance(trigger_type, str):
                    trigger_type = PatternTrigger(trigger_type)
                
                action = row['action']
                if isinstance(action, str):
                    action = PatternAction(action)
                
                pattern = CustomPattern(
                    pattern_id=row['pattern_id'],
                    name=row['name'],
                    description=row['description'],
                    trigger_type=trigger_type,
                    trigger_config=json.loads(row['trigger_config']),
                    action=action,
                    action_config=json.loads(row['action_config']),
                    confidence_threshold=row['confidence_threshold'],
                    cooldown_minutes=row['cooldown_minutes'],
                    enabled=bool(row['enabled']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    success_count=row['success_count'],
                    failure_count=row['failure_count'],
                    last_triggered=datetime.fromisoformat(row['last_triggered']) if row['last_triggered'] else None
                )
                self.patterns_cache[pattern.pattern_id] = pattern
    
    def add_pattern(self, pattern: CustomPattern) -> bool:
        """Adiciona um novo padrão personalizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO custom_patterns 
                    (pattern_id, name, description, trigger_type, trigger_config, 
                     action, action_config, confidence_threshold, cooldown_minutes, 
                     enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.name,
                    pattern.description,
                    self._enum_to_string(pattern.trigger_type),
                    json.dumps(pattern.trigger_config),
                    self._enum_to_string(pattern.action),
                    json.dumps(pattern.action_config),
                    pattern.confidence_threshold,
                    pattern.cooldown_minutes,
                    pattern.enabled,
                    pattern.created_at.isoformat(),
                    pattern.updated_at.isoformat()
                ))
            
            self.patterns_cache[pattern.pattern_id] = pattern
            return True
        except Exception as e:
            print(f"Erro ao adicionar padrão: {e}")
            return False
    
    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza um padrão existente"""
        try:
            if pattern_id not in self.patterns_cache:
                return False
            
            pattern = self.patterns_cache[pattern_id]
            
            # Atualiza os campos
            for key, value in updates.items():
                if hasattr(pattern, key):
                    # Converter strings para enums se necessário
                    if key == 'trigger_type' and isinstance(value, str):
                        try:
                            value = PatternTrigger(value)
                        except ValueError:
                            print(f"Valor inválido para trigger_type: {value}")
                            continue
                    elif key == 'action' and isinstance(value, str):
                        try:
                            value = PatternAction(value)
                        except ValueError:
                            print(f"Valor inválido para action: {value}")
                            continue
                    
                    setattr(pattern, key, value)
            
            pattern.updated_at = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE custom_patterns 
                    SET name = ?, description = ?, trigger_type = ?, trigger_config = ?,
                        action = ?, action_config = ?, confidence_threshold = ?,
                        cooldown_minutes = ?, enabled = ?, updated_at = ?
                    WHERE pattern_id = ?
                """, (
                    pattern.name,
                    pattern.description,
                    self._enum_to_string(pattern.trigger_type),
                    json.dumps(pattern.trigger_config),
                    self._enum_to_string(pattern.action),
                    json.dumps(pattern.action_config),
                    pattern.confidence_threshold,
                    pattern.cooldown_minutes,
                    pattern.enabled,
                    pattern.updated_at.isoformat(),
                    pattern_id
                ))
            
            self.patterns_cache[pattern_id] = pattern
            return True
        except Exception as e:
            print(f"Erro ao atualizar padrão: {e}")
            return False
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Remove um padrão personalizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM custom_patterns WHERE pattern_id = ?", (pattern_id,))
                conn.execute("DELETE FROM pattern_triggers WHERE pattern_id = ?", (pattern_id,))
            
            if pattern_id in self.patterns_cache:
                del self.patterns_cache[pattern_id]
            
            return True
        except Exception as e:
            print(f"Erro ao deletar padrão: {e}")
            return False
    
    def get_pattern(self, pattern_id: str) -> Optional[CustomPattern]:
        """Retorna um padrão específico"""
        return self.patterns_cache.get(pattern_id)
    
    def get_all_patterns(self) -> List[CustomPattern]:
        """Retorna todos os padrões personalizados"""
        return list(self.patterns_cache.values())
    
    def get_enabled_patterns(self) -> List[CustomPattern]:
        """Retorna apenas padrões habilitados"""
        return [p for p in self.patterns_cache.values() if p.enabled]
    
    def check_patterns(self, results: List[Dict]) -> List[Dict]:
        """Verifica se algum padrão personalizado foi ativado"""
        triggered_patterns = []
        
        if not results or len(results) < 2:
            return triggered_patterns
        
        for pattern in self.get_enabled_patterns():
            # Verifica cooldown
            if self._is_in_cooldown(pattern):
                continue
            
            # Verifica se o padrão foi ativado
            if self._check_pattern_trigger(pattern, results):
                triggered_patterns.append({
                    'pattern': pattern,
                    'confidence': self._calculate_confidence(pattern, results),
                    'reasoning': self._generate_reasoning(pattern, results),
                    'suggestion': self._generate_suggestion(pattern)
                })
                
                # Atualiza último trigger
                self._update_last_triggered(pattern)
        
        return triggered_patterns
    
    def _is_in_cooldown(self, pattern: CustomPattern) -> bool:
        """Verifica se o padrão está em cooldown"""
        if not pattern.last_triggered:
            return False
        
        cooldown_end = pattern.last_triggered + timedelta(minutes=pattern.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def _check_pattern_trigger(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica se o gatilho do padrão foi ativado"""
        try:
            if pattern.trigger_type == PatternTrigger.NUMBER_FOLLOWED_BY_COLOR:
                return self._check_number_followed_by_color(pattern, results)
            elif pattern.trigger_type == PatternTrigger.COLOR_SEQUENCE:
                return self._check_color_sequence(pattern, results)
            elif pattern.trigger_type == PatternTrigger.NUMBER_SEQUENCE:
                return self._check_number_sequence(pattern, results)
            elif pattern.trigger_type == PatternTrigger.COLOR_AFTER_COLOR:
                return self._check_color_after_color(pattern, results)
            elif pattern.trigger_type == PatternTrigger.NUMBER_AFTER_NUMBER:
                return self._check_number_after_number(pattern, results)
            elif pattern.trigger_type == PatternTrigger.NUMBER_DELAY_ALERT:
                return self._check_number_delay_alert(pattern, results)
            
            return False
        except Exception as e:
            print(f"Erro ao verificar gatilho do padrão {pattern.name}: {e}")
            # Log mais detalhado para debug
            print(f"  - Tipo do gatilho: {pattern.trigger_type}")
            print(f"  - Configuração: {pattern.trigger_config}")
            return False
    
    def _check_number_followed_by_color(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica padrão: número específico seguido por cor específica"""
        config = pattern.trigger_config
        target_number = config.get('number')
        target_color = config.get('color')
        min_occurrences = config.get('min_occurrences', 1)
        
        if target_number is None or target_color is None:
            return False
        
        occurrences = 0
        for i in range(len(results) - 1):
            # Verificar se as chaves existem antes de acessá-las
            if ('number' in results[i] and 'color' in results[i + 1] and
                results[i]['number'] == target_number and 
                results[i + 1]['color'] == target_color):
                occurrences += 1
        
        return occurrences >= min_occurrences
    
    def _check_color_sequence(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica sequência de cores"""
        config = pattern.trigger_config
        sequence = config.get('sequence', [])
        min_length = config.get('min_length', 2)
        
        if len(sequence) < min_length:
            return False
        
        # Verifica se a sequência aparece nos últimos resultados
        recent_colors = [r['color'] for r in results[:len(sequence)] if 'color' in r]
        return recent_colors == sequence
    
    def _check_number_sequence(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica sequência de números"""
        config = pattern.trigger_config
        sequence = config.get('sequence', [])
        min_length = config.get('min_length', 2)
        
        if len(sequence) < min_length:
            return False
        
        recent_numbers = [r['number'] for r in results[:len(sequence)] if 'number' in r]
        return recent_numbers == sequence
    
    def _check_color_after_color(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica cor após cor"""
        config = pattern.trigger_config
        first_color = config.get('first_color')
        second_color = config.get('second_color')
        min_occurrences = config.get('min_occurrences', 1)
        
        if first_color is None or second_color is None:
            return False
        
        occurrences = 0
        for i in range(len(results) - 1):
            if ('color' in results[i] and 'color' in results[i + 1] and
                results[i]['color'] == first_color and 
                results[i + 1]['color'] == second_color):
                occurrences += 1
        
        return occurrences >= min_occurrences
    
    def _check_number_after_number(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica número após número"""
        config = pattern.trigger_config
        first_number = config.get('first_number')
        second_number = config.get('second_number')
        min_occurrences = config.get('min_occurrences', 1)
        
        if first_number is None or second_number is None:
            return False
        
        occurrences = 0
        for i in range(len(results) - 1):
            if ('number' in results[i] and 'number' in results[i + 1] and
                results[i]['number'] == first_number and 
                results[i + 1]['number'] == second_number):
                occurrences += 1
        
        return occurrences >= min_occurrences
    
    def _check_number_delay_alert(self, pattern: CustomPattern, results: List[Dict]) -> bool:
        """Verifica número com delay para alerta"""
        config = pattern.trigger_config
        trigger_number = config.get('trigger_number')
        delay_results = config.get('delay_results', 5)
        min_occurrences = config.get('min_occurrences', 1)
        
        if trigger_number is None:
            return False
        
        # Procurar pelo número ativador nos últimos resultados
        occurrences = 0
        for i in range(len(results)):
            if 'number' in results[i] and results[i]['number'] == trigger_number:
                # Verificar se já passaram 'delay_results' resultados desde então
                remaining_results = len(results) - i - 1
                if remaining_results >= delay_results:
                    occurrences += 1
        
        return occurrences >= min_occurrences
    
    def _calculate_confidence(self, pattern: CustomPattern, results: List[Dict]) -> float:
        """Calcula confiança baseada no histórico do padrão"""
        total_attempts = pattern.success_count + pattern.failure_count
        if total_attempts == 0:
            return pattern.confidence_threshold
        
        success_rate = pattern.success_count / total_attempts
        return min(0.95, max(0.5, success_rate))
    
    def _generate_reasoning(self, pattern: CustomPattern, results: List[Dict]) -> str:
        """Gera explicação do padrão detectado"""
        config = pattern.trigger_config
        
        if pattern.trigger_type == PatternTrigger.NUMBER_FOLLOWED_BY_COLOR:
            number = config.get('number')
            color = config.get('color')
            occurrences = config.get('min_occurrences', 1)
            return f"Após {occurrences} números {number}, {occurrences} foram seguidos por {color.upper()}"
        
        elif pattern.trigger_type == PatternTrigger.COLOR_SEQUENCE:
            sequence = config.get('sequence', [])
            return f"Sequência de cores detectada: {' → '.join(sequence).upper()}"
        
        elif pattern.trigger_type == PatternTrigger.COLOR_AFTER_COLOR:
            first = config.get('first_color')
            second = config.get('second_color')
            return f"Padrão {first.upper()} → {second.upper()} detectado"
        
        elif pattern.trigger_type == PatternTrigger.NUMBER_DELAY_ALERT:
            trigger_number = config.get('trigger_number')
            delay_results = config.get('delay_results', 5)
            return f"Número {trigger_number} detectado há {delay_results} resultados - tempo de alertar!"
        
        return f"Padrão personalizado '{pattern.name}' ativado"
    
    def _generate_suggestion(self, pattern: CustomPattern) -> str:
        """Gera sugestão de aposta"""
        config = pattern.action_config
        
        if pattern.action == PatternAction.BET_COLOR:
            color = config.get('color', 'red')
            return f"Apostar na cor {color.upper()}"
        
        elif pattern.action == PatternAction.BET_NUMBER:
            number = config.get('number', 1)
            return f"Apostar no número {number}"
        
        elif pattern.action == PatternAction.SKIP_BET:
            return "Pular esta rodada"
        
        elif pattern.action == PatternAction.WAIT:
            return "Aguardar próxima oportunidade"
        
        return "Seguir padrão personalizado"
    
    def _update_last_triggered(self, pattern: CustomPattern):
        """Atualiza timestamp do último trigger"""
        pattern.last_triggered = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE custom_patterns SET last_triggered = ? WHERE pattern_id = ?",
                (pattern.last_triggered.isoformat(), pattern.pattern_id)
            )
    
    def record_pattern_result(self, pattern_id: str, was_successful: bool, result_data: Dict):
        """Registra resultado de um padrão"""
        if pattern_id not in self.patterns_cache:
            return
        
        pattern = self.patterns_cache[pattern_id]
        
        if was_successful:
            pattern.success_count += 1
        else:
            pattern.failure_count += 1
        
        # Salva no banco
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE custom_patterns 
                SET success_count = ?, failure_count = ?
                WHERE pattern_id = ?
            """, (pattern.success_count, pattern.failure_count, pattern_id))
            
            conn.execute("""
                INSERT INTO pattern_triggers 
                (pattern_id, triggered_at, result_number, result_color, was_successful)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pattern_id,
                datetime.now().isoformat(),
                result_data.get('number', 0),
                result_data.get('color', 'unknown'),
                was_successful
            ))
    
    def get_pattern_stats(self, pattern_id: str) -> Dict:
        """Retorna estatísticas de um padrão"""
        if pattern_id not in self.patterns_cache:
            return {}
        
        pattern = self.patterns_cache[pattern_id]
        total = pattern.success_count + pattern.failure_count
        
        return {
            'pattern_id': pattern_id,
            'name': pattern.name,
            'success_count': pattern.success_count,
            'failure_count': pattern.failure_count,
            'total_triggers': total,
            'success_rate': pattern.success_count / total if total > 0 else 0,
            'last_triggered': pattern.last_triggered.isoformat() if pattern.last_triggered else None,
            'enabled': pattern.enabled
        }
    
    def export_patterns(self, filepath: str) -> bool:
        """Exporta padrões para arquivo JSON"""
        try:
            patterns_data = []
            for pattern in self.patterns_cache.values():
                pattern_dict = asdict(pattern)
                pattern_dict['trigger_type'] = self._enum_to_string(pattern.trigger_type)
                pattern_dict['action'] = self._enum_to_string(pattern.action)
                pattern_dict['created_at'] = pattern.created_at.isoformat()
                pattern_dict['updated_at'] = pattern.updated_at.isoformat()
                pattern_dict['last_triggered'] = pattern.last_triggered.isoformat() if pattern.last_triggered else None
                patterns_data.append(pattern_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erro ao exportar padrões: {e}")
            return False
    
    def import_patterns(self, filepath: str) -> bool:
        """Importa padrões de arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                patterns_data = json.load(f)
            
            imported_count = 0
            for pattern_data in patterns_data:
                pattern = CustomPattern(
                    pattern_id=pattern_data['pattern_id'],
                    name=pattern_data['name'],
                    description=pattern_data['description'],
                    trigger_type=PatternTrigger(pattern_data['trigger_type']),
                    trigger_config=pattern_data['trigger_config'],
                    action=PatternAction(pattern_data['action']),
                    action_config=pattern_data['action_config'],
                    confidence_threshold=pattern_data.get('confidence_threshold', 0.7),
                    cooldown_minutes=pattern_data.get('cooldown_minutes', 5),
                    enabled=pattern_data.get('enabled', True),
                    created_at=datetime.fromisoformat(pattern_data['created_at']),
                    updated_at=datetime.fromisoformat(pattern_data['updated_at']),
                    success_count=pattern_data.get('success_count', 0),
                    failure_count=pattern_data.get('failure_count', 0),
                    last_triggered=datetime.fromisoformat(pattern_data['last_triggered']) if pattern_data.get('last_triggered') else None
                )
                
                if self.add_pattern(pattern):
                    imported_count += 1
            
            return imported_count > 0
        except Exception as e:
            print(f"Erro ao importar padrões: {e}")
            return False


# Instância global do gerenciador
custom_pattern_manager = CustomPatternManager()


def create_example_patterns():
    """Cria alguns padrões de exemplo"""
    examples = [
        CustomPattern(
            pattern_id="example_1_red",
            name="Número 1 Seguido por Red",
            description="Detecta quando após o número 1 vem red",
            trigger_type=PatternTrigger.NUMBER_FOLLOWED_BY_COLOR,
            trigger_config={
                'number': 1,
                'color': 'red',
                'min_occurrences': 2
            },
            action=PatternAction.BET_COLOR,
            action_config={'color': 'red'},
            confidence_threshold=0.8,
            cooldown_minutes=3
        ),
        
        CustomPattern(
            pattern_id="example_red_sequence",
            name="Sequência Red-Red",
            description="Detecta sequência de dois reds consecutivos",
            trigger_type=PatternTrigger.COLOR_SEQUENCE,
            trigger_config={
                'sequence': ['red', 'red'],
                'min_length': 2
            },
            action=PatternAction.BET_COLOR,
            action_config={'color': 'black'},
            confidence_threshold=0.7,
            cooldown_minutes=5
        ),
        
        CustomPattern(
            pattern_id="example_black_after_red",
            name="Black Após Red",
            description="Detecta quando após red vem black",
            trigger_type=PatternTrigger.COLOR_AFTER_COLOR,
            trigger_config={
                'first_color': 'red',
                'second_color': 'black',
                'min_occurrences': 1
            },
            action=PatternAction.BET_COLOR,
            action_config={'color': 'black'},
            confidence_threshold=0.75,
            cooldown_minutes=4
        )
    ]
    
    for pattern in examples:
        custom_pattern_manager.add_pattern(pattern)
    
    return len(examples)


if __name__ == "__main__":
    # Teste do sistema
    manager = CustomPatternManager()
    
    # Cria padrões de exemplo
    count = create_example_patterns()
    print(f"Criados {count} padrões de exemplo")
    
    # Lista padrões
    patterns = manager.get_all_patterns()
    print(f"Total de padrões: {len(patterns)}")
    
    for pattern in patterns:
        print(f"- {pattern.name}: {pattern.description}")
