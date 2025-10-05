import requests
import json

print("🧪 TESTANDO RAILWAY COM JSESSIONID REAL...")
print("=" * 50)

# Verificar status do JSESSIONID
print("📊 1. Verificando status do JSESSIONID...")
status_response = requests.get("https://baze-double-web-production.up.railway.app/api/jsessionid/status")
status_data = status_response.json()

print(f"   ✅ JSESSIONID presente: {status_data.get('has_jsessionid')}")
print(f"   📄 Preview: {status_data.get('jsessionid_preview')}")
print()

# Testar estatísticas
print("📊 2. Testando API de estatísticas...")
stats_response = requests.get("https://baze-double-web-production.up.railway.app/api/roulette/statistics/enhanced")
stats_data = stats_response.json()

print(f"   📈 Sucesso: {stats_data.get('success')}")
print(f"   📊 Total resultados: {stats_data.get('total_results')}")
print(f"   🎲 Dados simulados: {stats_data.get('simulated', 'N/A')}")

if not stats_data.get('simulated'):
    print()
    print("🎉🎉🎉 PARABÉNS! DADOS REAIS FUNCIONANDO NO RAILWAY! 🎉🎉🎉")
    
    # Mostrar alguns resultados
    if stats_data.get('results'):
        print("\n📊 Primeiros 5 resultados REAIS:")
        for i, result in enumerate(stats_data['results'][:5], 1):
            print(f"   {i}. Número: {result.get('number')} | Cor: {result.get('color')}")
else:
    print()
    print("⚠️ Ainda usando dados simulados - pode levar alguns segundos para atualizar")
    
print("\n🌐 Agora acesse: https://baze-double-web-production.up.railway.app/roulette/api-test")
print("E clique em 'Buscar Estatísticas' para ver os dados reais!")