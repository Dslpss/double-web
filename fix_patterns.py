#!/usr/bin/env python3
"""
Script para corrigir padrões personalizados mal configurados
"""

import sqlite3
import json
import os

def fix_patterns():
    """Corrige padrões personalizados com configurações inválidas"""
    db_path = "data/custom_patterns.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    print("🔧 Corrigindo padrões personalizados...")
    
    with sqlite3.connect(db_path) as conn:
        # Listar padrões problemáticos
        cursor = conn.execute("SELECT pattern_id, name, trigger_type, trigger_config FROM custom_patterns")
        
        patterns_to_fix = []
        for row in cursor.fetchall():
            pattern_id, name, trigger_type, trigger_config_json = row
            
            try:
                trigger_config = json.loads(trigger_config_json)
                
                # Verificar se tem configuração válida baseada no tipo
                if trigger_type == "number_followed_by_color":
                    if 'number' not in trigger_config or 'color' not in trigger_config:
                        patterns_to_fix.append((pattern_id, name, "number_followed_by_color"))
                elif trigger_type == "color_after_color":
                    if 'first_color' not in trigger_config or 'second_color' not in trigger_config:
                        patterns_to_fix.append((pattern_id, name, "color_after_color"))
                elif trigger_type == "number_after_number":
                    if 'first_number' not in trigger_config or 'second_number' not in trigger_config:
                        patterns_to_fix.append((pattern_id, name, "number_after_number"))
                elif trigger_type == "number_delay_alert":
                    if 'trigger_number' not in trigger_config:
                        patterns_to_fix.append((pattern_id, name, "number_delay_alert"))
                        
            except json.JSONDecodeError:
                print(f"❌ Padrão {name} tem configuração JSON inválida")
                patterns_to_fix.append((pattern_id, name, "invalid_json"))
        
        print(f"📊 Encontrados {len(patterns_to_fix)} padrões para corrigir")
        
        # Corrigir ou remover padrões problemáticos
        for pattern_id, name, issue_type in patterns_to_fix:
            print(f"🔧 Corrigindo padrão: {name} (ID: {pattern_id}) - Problema: {issue_type}")
            
            if issue_type == "invalid_json":
                # Remover padrão com JSON inválido
                conn.execute("DELETE FROM custom_patterns WHERE pattern_id = ?", (pattern_id,))
                print(f"  ❌ Removido padrão {name} (JSON inválido)")
            else:
                # Corrigir configuração baseada no tipo
                if issue_type == "number_followed_by_color":
                    new_config = {
                        "number": 1,
                        "color": "red",
                        "min_occurrences": 1
                    }
                elif issue_type == "color_after_color":
                    new_config = {
                        "first_color": "red",
                        "second_color": "black",
                        "min_occurrences": 1
                    }
                elif issue_type == "number_after_number":
                    new_config = {
                        "first_number": 1,
                        "second_number": 2,
                        "min_occurrences": 1
                    }
                elif issue_type == "number_delay_alert":
                    new_config = {
                        "trigger_number": 5,
                        "delay_results": 5,
                        "min_occurrences": 1
                    }
                
                conn.execute(
                    "UPDATE custom_patterns SET trigger_config = ? WHERE pattern_id = ?",
                    (json.dumps(new_config), pattern_id)
                )
                print(f"  ✅ Configuração corrigida para {name}")
        
        conn.commit()
        print("✅ Correções aplicadas com sucesso!")

if __name__ == "__main__":
    fix_patterns()
