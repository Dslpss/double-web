#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento do banco de dados do Double da Blaze.
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Classe para gerenciamento do banco de dados SQLite."""
    
    def __init__(self, db_path: str = "data/blaze_data.db"):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias."""
        try:
            # Cria o diretório se não existir
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Cria a tabela de resultados
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS results (
                        id TEXT PRIMARY KEY,
                        roll INTEGER NOT NULL,
                        color TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        server_seed TEXT,
                        status TEXT,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Cria a tabela de previsões
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        result_id TEXT,
                        prediction_color TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        method TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        correct BOOLEAN,
                        FOREIGN KEY (result_id) REFERENCES results (id)
                    )
                ''')
                
                # Cria índices para melhor performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON results (timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_color ON results (color)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON predictions (created_at)')
                
                conn.commit()
                logger.info("Banco de dados inicializado com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)
    
    def insert_results(self, results: List[Dict]) -> bool:
        """
        Insere uma lista de resultados no banco de dados.
        
        Args:
            results (List[Dict]): Lista de resultados a serem inseridos
            
        Returns:
            bool: True se a inserção foi bem-sucedida
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for result in results:
                    cursor.execute('''
                        INSERT OR REPLACE INTO results 
                        (id, roll, color, created_at, timestamp, server_seed, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result.get('id'),
                        result.get('roll'),
                        result.get('color'),
                        result.get('created_at'),
                        result.get('timestamp'),
                        result.get('server_seed'),
                        result.get('status')
                    ))
                
                conn.commit()
                logger.info(f"Inseridos {len(results)} resultados no banco de dados")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao inserir resultados: {str(e)}")
            return False
    
    def get_results_since(self, timestamp: int) -> List[Dict]:
        """
        Obtém resultados desde um timestamp específico.
        
        Args:
            timestamp (int): Timestamp de início
            
        Returns:
            List[Dict]: Lista de resultados
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM results 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                ''', (timestamp,))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'id': row['id'],
                        'roll': row['roll'],
                        'color': row['color'],
                        'created_at': row['created_at'],
                        'timestamp': row['timestamp'],
                        'server_seed': row['server_seed'],
                        'status': row['status']
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Erro ao obter resultados: {str(e)}")
            return []
    
    def get_existing_ids(self, ids: List[str]) -> List[str]:
        """
        Verifica quais IDs já existem no banco de dados.
        
        Args:
            ids (List[str]): Lista de IDs para verificar
            
        Returns:
            List[str]: Lista de IDs que já existem
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f'''
                    SELECT id FROM results 
                    WHERE id IN ({placeholders})
                ''', ids)
                
                existing_ids = [row[0] for row in cursor.fetchall()]
                return existing_ids
                
        except Exception as e:
            logger.error(f"Erro ao verificar IDs existentes: {str(e)}")
            return []
    
    def get_recent_results(self, limit: int = 100) -> List[Dict]:
        """
        Obtém os resultados mais recentes.
        
        Args:
            limit (int): Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de resultados
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM results 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'id': row['id'],
                        'roll': row['roll'],
                        'color': row['color'],
                        'created_at': row['created_at'],
                        'timestamp': row['timestamp'],
                        'server_seed': row['server_seed'],
                        'status': row['status']
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Erro ao obter resultados recentes: {str(e)}")
            return []
    
    def insert_prediction(self, prediction: Dict) -> bool:
        """
        Insere uma previsão no banco de dados.
        
        Args:
            prediction (Dict): Dados da previsão
            
        Returns:
            bool: True se a inserção foi bem-sucedida
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO predictions 
                    (result_id, prediction_color, confidence, method, correct)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    prediction.get('result_id'),
                    prediction.get('color'),
                    prediction.get('confidence'),
                    prediction.get('method'),
                    prediction.get('correct')
                ))

                conn.commit()
                last_id = cursor.lastrowid
                logger.debug(f"Previsão inserida (id={last_id}): {prediction}")
                return last_id

        except Exception as e:
            logger.error(f"Erro ao inserir previsão: {str(e)}")
            return False

    def get_last_unverified_prediction(self) -> Optional[Dict]:
        """
        Retorna a última previsão que ainda não foi verificada (campo correct IS NULL).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions
                    WHERE correct IS NULL
                    ORDER BY created_at DESC
                    LIMIT 1
                ''')
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    'id': row['id'],
                    'result_id': row['result_id'],
                    'prediction_color': row['prediction_color'],
                    'confidence': row['confidence'],
                    'method': row['method'],
                    'created_at': row['created_at'],
                    'correct': row['correct']
                }
        except Exception as e:
            logger.error(f"Erro ao buscar previsão não verificada: {str(e)}")
            return None

    def get_last_unverified_prediction_before_timestamp(self, timestamp_seconds: float) -> Optional[Dict]:
        """
        Retorna a última previsão não verificada (correct IS NULL) cuja created_at seja anterior ou igual
        ao timestamp (em segundos desde epoch) informado. Útil para associar um resultado que acabou de
        ser inserido à previsão gerada anteriormente.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Usar função datetime(..., 'unixepoch') para comparar corretamente o campo created_at textual
                cursor.execute('''
                    SELECT * FROM predictions
                    WHERE correct IS NULL
                      AND created_at <= datetime(?, 'unixepoch')
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (int(timestamp_seconds),))
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    'id': row['id'],
                    'result_id': row['result_id'],
                    'prediction_color': row['prediction_color'],
                    'confidence': row['confidence'],
                    'method': row['method'],
                    'created_at': row['created_at'],
                    'correct': row['correct']
                }
        except Exception as e:
            logger.error(f"Erro ao buscar previsão não verificada antes do timestamp: {str(e)}")
            return None

    def update_prediction_result(self, prediction_id: int, result_id: str, correct: bool) -> bool:
        """
        Atualiza uma previsão existente com o resultado final (result_id) e se acertou ou não.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE predictions
                    SET result_id = ?, correct = ?
                    WHERE id = ?
                ''', (result_id, 1 if correct else 0, prediction_id))
                conn.commit()
                logger.debug(f"Previsão {prediction_id} atualizada: result_id={result_id}, correct={correct}")
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar previsão: {str(e)}")
            return False
    
    def get_prediction_stats(self) -> Dict:
        """
        Obtém estatísticas das previsões.
        
        Returns:
            Dict: Estatísticas das previsões
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de previsões
                cursor.execute('SELECT COUNT(*) FROM predictions')
                total = cursor.fetchone()[0]
                
                # Previsões corretas
                cursor.execute('SELECT COUNT(*) FROM predictions WHERE correct = 1')
                correct = cursor.fetchone()[0]
                
                # Taxa de acerto
                accuracy = correct / total if total > 0 else 0
                
                return {
                    'total_predictions': total,
                    'correct_predictions': correct,
                    'accuracy_rate': accuracy
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'total_predictions': 0,
                'correct_predictions': 0,
                'accuracy_rate': 0
            }

    def get_recent_predictions(self, limit: int = 20) -> List[Dict]:
        """
        Retorna as previsões mais recentes (inclui status de correto/incorreto/null).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        'id': row['id'],
                        'result_id': row['result_id'],
                        'prediction_color': row['prediction_color'],
                        'confidence': row['confidence'],
                        'method': row['method'],
                        'created_at': row['created_at'],
                        'correct': row['correct']
                    })
                return results
        except Exception as e:
            logger.error(f"Erro ao obter previsões recentes: {str(e)}")
            return []
    
    def cleanup_old_data(self, results_days: int = 30, predictions_days: int = 7) -> Dict[str, int]:
        """
        Remove dados antigos do banco para manter performance.
        
        Args:
            results_days (int): Dias de resultados para manter
            predictions_days (int): Dias de predições para manter
            
        Returns:
            Dict com número de registros removidos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calcular data limite
                from datetime import datetime, timedelta
                results_limit = datetime.now() - timedelta(days=results_days)
                predictions_limit = datetime.now() - timedelta(days=predictions_days)
                
                # Contar registros antes da limpeza
                cursor.execute("SELECT COUNT(*) FROM results WHERE created_at < ?", (results_limit.isoformat(),))
                old_results_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM predictions WHERE created_at < ?", (predictions_limit.isoformat(),))
                old_predictions_count = cursor.fetchone()[0]
                
                # Remover dados antigos
                cursor.execute("DELETE FROM results WHERE created_at < ?", (results_limit.isoformat(),))
                cursor.execute("DELETE FROM predictions WHERE created_at < ?", (predictions_limit.isoformat(),))
                
                conn.commit()
                
                # Compactar banco (VACUUM) - deve ser executado fora da transação
                cursor.execute("VACUUM")
                
                logger.info(f"Limpeza concluída: {old_results_count} resultados e {old_predictions_count} predições removidos")
                
                return {
                    'results_removed': old_results_count,
                    'predictions_removed': old_predictions_count,
                    'results_kept': results_days,
                    'predictions_kept': predictions_days
                }
                
        except Exception as e:
            logger.error(f"Erro na limpeza de dados: {e}")
            return {'error': str(e)}
    
    def get_database_stats(self) -> Dict[str, any]:
        """Obtém estatísticas do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM results")
                results_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM predictions")
                predictions_count = cursor.fetchone()[0]
                
                # Data mais antiga e recente
                cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM results")
                results_range = cursor.fetchone()
                
                cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM predictions")
                predictions_range = cursor.fetchone()
                
                # Tamanho do arquivo
                import os
                file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'results_count': results_count,
                    'predictions_count': predictions_count,
                    'results_range': results_range,
                    'predictions_range': predictions_range,
                    'file_size_mb': file_size / (1024 * 1024),
                    'file_size_bytes': file_size
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        # SQLite fecha automaticamente as conexões, mas podemos adicionar lógica aqui se necessário
        pass
