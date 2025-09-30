#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar notificações web especificamente
"""

import requests
import json
import time

def test_web_notifications():
    """Testa as notificações web."""
    base_url = "http://localhost:5000"
    
    print("Testando notificacoes web...")
    print("=" * 50)
    
    try:
        # 1. Verificar status do sistema
        print("1. Verificando status do sistema...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"   OK - Sistema ativo")
            print(f"   PlayNabets conectado: {status.get('playnabets_connected', False)}")
            print(f"   Analyzer pronto: {status.get('analyzer_ready', False)}")
        else:
            print(f"   ERRO - Status: {response.status_code}")
            return False
        
        # 2. Verificar notificações atuais
        print("\n2. Verificando notificacoes atuais...")
        response = requests.get(f"{base_url}/api/notifications/web", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Total de notificacoes: {data['total']}")
            print(f"   Notificacoes retornadas: {len(data['notifications'])}")
            
            if data['notifications']:
                print("   Ultimas notificacoes:")
                for i, notif in enumerate(data['notifications'][-3:]):
                    print(f"     {i+1}. Tipo: {notif.get('type', 'N/A')}")
                    if notif.get('type') == 'pattern_detected':
                        print(f"        Pattern: {notif.get('pattern_type', 'N/A')}")
                        print(f"        Cor: {notif.get('predicted_color', 'N/A')}")
                        print(f"        Confianca: {notif.get('confidence', 'N/A')}")
        else:
            print(f"   ERRO - Status: {response.status_code}")
        
        # 3. Forçar detecção de padrões
        print("\n3. Forcando deteccao de padroes...")
        response = requests.post(f"{base_url}/api/debug/force_pattern_detection", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   OK - Deteccao forcada com sucesso")
                
                # Aguardar um pouco
                print("   Aguardando 3 segundos...")
                time.sleep(3)
                
                # Verificar se notificação foi criada
                print("\n4. Verificando se notificacao foi criada...")
                response = requests.get(f"{base_url}/api/notifications/web", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Total de notificacoes: {data['total']}")
                    
                    # Filtrar notificações de padrão
                    pattern_notifications = [n for n in data['notifications'] if n.get('type') == 'pattern_detected']
                    print(f"   Notificacoes de padroes: {len(pattern_notifications)}")
                    
                    if pattern_notifications:
                        print("   SUCESSO - Notificacao de padrao detectada!")
                        latest = pattern_notifications[-1]
                        print(f"   Pattern: {latest.get('pattern_type', 'N/A')}")
                        print(f"   Cor: {latest.get('predicted_color', 'N/A')}")
                        print(f"   Confianca: {latest.get('confidence', 'N/A')}")
                        return True
                    else:
                        print("   AVISO - Nenhuma notificacao de padrao encontrada")
                else:
                    print(f"   ERRO - Status: {response.status_code}")
            else:
                print(f"   ERRO - Falha na deteccao: {result.get('error', 'N/A')}")
        else:
            print(f"   ERRO - Status: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"ERRO - Erro no teste: {e}")
        return False

def test_add_manual_result():
    """Testa adicionar resultado manual para gerar notificações."""
    base_url = "http://localhost:5000"
    
    print("\n5. Testando resultado manual...")
    print("=" * 50)
    
    try:
        # Adicionar alguns resultados para gerar padrões
        results = [
            {'number': 1, 'color': 'red'},
            {'number': 2, 'color': 'black'},
            {'number': 3, 'color': 'red'},
            {'number': 4, 'color': 'black'},
            {'number': 5, 'color': 'red'}
        ]
        
        for i, result in enumerate(results):
            print(f"   Adicionando resultado {i+1}: {result['number']} ({result['color']})")
            response = requests.post(f"{base_url}/api/add_result", json=result, timeout=10)
            if response.status_code == 200:
                print(f"   OK - Resultado {i+1} adicionado")
            else:
                print(f"   ERRO - Falha ao adicionar resultado {i+1}")
            
            # Aguardar um pouco entre resultados
            time.sleep(1)
        
        # Aguardar análise
        print("\n   Aguardando analise...")
        time.sleep(3)
        
        # Verificar notificações
        print("\n6. Verificando notificacoes apos resultados...")
        response = requests.get(f"{base_url}/api/notifications/web", timeout=10)
        if response.status_code == 200:
            data = response.json()
            pattern_notifications = [n for n in data['notifications'] if n.get('type') == 'pattern_detected']
            print(f"   Notificacoes de padroes: {len(pattern_notifications)}")
            
            if pattern_notifications:
                print("   SUCESSO - Padroes detectados!")
                return True
            else:
                print("   AVISO - Nenhum padrao detectado")
        
        return False
        
    except Exception as e:
        print(f"ERRO - Erro no teste manual: {e}")
        return False

if __name__ == "__main__":
    print("Testando sistema de notificacoes web...")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code != 200:
            print("ERRO - Servidor nao esta respondendo. Inicie o servidor primeiro.")
            exit(1)
    except Exception as e:
        print("ERRO - Servidor nao esta rodando. Inicie o servidor primeiro.")
        print("   Execute: python backend/polling_app.py")
        exit(1)
    
    # Executar testes
    success1 = test_web_notifications()
    success2 = test_add_manual_result()
    
    print("\n" + "=" * 50)
    if success1 or success2:
        print("SUCESSO - Notificacoes web funcionando!")
        print("\nSe as notificacoes nao aparecem na interface:")
        print("1. Recarregue a pagina web")
        print("2. Clique no botao 'Atualizar' na seção de notificações")
        print("3. Verifique o console do navegador para erros")
    else:
        print("ERRO - Problemas com notificacoes web")
        print("\nPossiveis causas:")
        print("1. Callback web nao configurado")
        print("2. Notificador desabilitado")
        print("3. Confianca minima muito alta")
        print("4. Dados insuficientes para detectar padroes")
