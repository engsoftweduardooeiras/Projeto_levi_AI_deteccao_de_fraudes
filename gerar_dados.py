# gerar_dados.py
import os
import json
import numpy as np
import pandas as pd

os.makedirs('data', exist_ok=True)

print("1. Gerando 10 partes da base de dados de cartao de credito...")
np.random.seed(42)
total_linhas_por_parte = 1000

acoes = ["Autenticação MFA", "Login Padrão", "Alteração de Senha", "Tentativa Falha"]
conexoes = ["Fibra residencial", "4G Móvel", "VPN Pública", "Wi-Fi Público"]
ips_comuns = [f"192.168.1.{i}" for i in range(1, 20)]

for p in range(1, 11):
    n = total_linhas_por_parte
    # Fraude rara (~2% dos casos)
    classe = np.random.choice([0, 1], size=n, p=[0.98, 0.02])
    
    dados = {
        "Time": np.random.uniform(0, 172800, n),
        "Amount": np.where(classe == 1, np.random.uniform(500, 10000, n), np.random.uniform(10, 500, n)),
        "Device_IP": np.random.choice(ips_comuns, n),
        "Previous_Action": np.random.choice(acoes, n),
        "Connection_Type": np.random.choice(conexoes, n),
        "Class": classe
    }
    
    # Adicionando features V1 a V28
    for v in range(1, 29):
        dados[f"V{v}"] = np.random.normal(0, 1, n)
        
    df_parte = pd.DataFrame(dados)
    caminho_csv = f"data/cartao_de_credito_sintetico_parte_{p:02d}.csv"
    df_parte.to_csv(caminho_csv, index=False)
    print(f"   -> {caminho_csv} criado ({len(df_parte)} registros)")

print("2. Gerando produtos_financeiros.json...")
produtos = [
    {"nome_produto": "Crédito Pessoal Automático", "taxa_juros": "2.99% a.m.", "limite_maximo": 15000},
    {"nome_produto": "Consignado Privado", "taxa_juros": "1.89% a.m.", "limite_maximo": 50000},
    {"nome_produto": "Cartão Platinum Flex", "taxa_juros": "3.49% a.m.", "limite_maximo": 25000},
    {"nome_produto": "Microcrédito Estruturado", "taxa_juros": "1.49% a.m.", "limite_maximo": 5000}
]
with open('data/produtos_financeiros.json', 'w', encoding='utf-8') as f:
    json.dump(produtos, f, indent=4, ensure_ascii=False)

print("3. Gerando historico_atendimento.csv...")
historico = pd.DataFrame([
    {"id_cliente": "CLIENTE_8942", "data": "2026-07-10", "categoria": "Cartões", "status_resolucao": "Resolvido"},
    {"id_cliente": "CLIENTE_8942", "data": "2026-08-01", "categoria": "Crédito", "status_resolucao": "Em Análise"},
    {"id_cliente": "CLIENTE_1020", "data": "2026-06-15", "categoria": "Fraude", "status_resolucao": "Bloqueado"}
])
historico.to_csv('data/historico_atendimento.csv', index=False)

print("\n✅ Todos os dados sintéticos e bases JSON foram populados com sucesso!")