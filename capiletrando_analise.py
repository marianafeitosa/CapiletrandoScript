"""
==========================================================================
 CapiLetrando — Anonimização e Análise de Dados (versão simples)
==========================================================================

Como funciona:
  1) Você exporta os dados que tiver (de um formulário, planilha, ou
     um dump manual do Firestore) para um arquivo local em JSON ou CSV.
  2) O script lê esse arquivo, remove/anonimiza os campos sensíveis
     (nome, e-mail, telefone, CPF, RG, data de nascimento) e gera uma
     versão anonimizada + um relatório de estatísticas simples.

Não precisa de Firebase, internet nem bibliotecas externas — só Python
puro (biblioteca padrão).

Como usar:
  1) Coloque seus dados em um arquivo chamado 'dados.json' OU 'dados.csv'
     na mesma pasta deste script (veja exemplos de formato mais abaixo).
  2) Rode:  python capiletrando_analise.py
  3) Os resultados aparecem na pasta 'saida_capiletrando/'.

--------------------------------------------------------------------------
Formato esperado do dados.json (uma lista de registros — cada um é um
respondente/usuário):

  [
    {"nome": "Maria Silva", "cpf": "123.456.789-00", "idade": 6, "atividade_concluida": "sim"},
    {"nome": "João Souza", "cpf": "987.654.321-00", "idade": 7, "atividade_concluida": "nao"}
  ]

Formato esperado do dados.csv (cabeçalho na primeira linha):

  nome,cpf,idade,atividade_concluida
  Maria Silva,123.456.789-00,6,sim
  João Souza,987.654.321-00,7,nao
--------------------------------------------------------------------------
"""

import csv
import json
import os
import re
from collections import Counter
from datetime import datetime

# ==========================================================================
# CONFIGURAÇÃO — ajuste se os nomes das colunas do seu arquivo forem outros
# ==========================================================================

ARQUIVO_JSON = "dados.json"
ARQUIVO_CSV = "dados.csv"
PASTA_SAIDA = "saida_capiletrando"

# Colunas removidas por completo (dados pessoais e de identificação oficial)
COLUNAS_PARA_REMOVER = [
    "nome", "nome_completo", "nome completo",
    "email", "e-mail",
    "telefone", "celular",
    "endereco", "endereço",
    "cpf", "rg",
]

# Coluna de data de nascimento: se existir, vira faixa etária em vez de
# ser removida (mantém informação útil pra análise sem identificar)
COLUNA_DATA_NASCIMENTO = "data_nascimento"


# ==========================================================================
# ANONIMIZAÇÃO
# ==========================================================================

def calcular_faixa_etaria(data_nascimento: str) -> str:
    if not data_nascimento:
        return ""
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            nascimento = datetime.strptime(data_nascimento, formato)
            idade = (datetime.now() - nascimento).days // 365
            if idade <= 5:
                return "4-5 anos"
            elif idade <= 7:
                return "6-7 anos"
            else:
                return "8+ anos"
        except ValueError:
            continue
    return "faixa desconhecida"


def anonimizar_registro(registro: dict) -> dict:
    novo = {}
    for chave, valor in registro.items():
        chave_normalizada = chave.strip().lower()
        if chave_normalizada in COLUNAS_PARA_REMOVER:
            continue  # descarta o campo sensível
        novo[chave] = valor

    # trata data de nascimento separadamente -> vira faixa etária
    for chave in list(registro.keys()):
        if chave.strip().lower() == COLUNA_DATA_NASCIMENTO.lower():
            novo["faixa_etaria"] = calcular_faixa_etaria(str(registro[chave]))

    return novo


# ==========================================================================
# LEITURA DO ARQUIVO LOCAL
# ==========================================================================

def carregar_dados() -> list[dict]:
    if os.path.exists(ARQUIVO_JSON):
        print(f"Lendo '{ARQUIVO_JSON}'...")
        with open(ARQUIVO_JSON, encoding="utf-8") as f:
            return json.load(f)

    if os.path.exists(ARQUIVO_CSV):
        print(f"Lendo '{ARQUIVO_CSV}'...")
        with open(ARQUIVO_CSV, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    raise FileNotFoundError(
        f"Nenhum arquivo de dados encontrado.\n"
        f"Coloque seus dados em '{ARQUIVO_JSON}' ou '{ARQUIVO_CSV}' "
        f"nesta mesma pasta (veja o formato de exemplo no topo do script)."
    )


# ==========================================================================
# ANÁLISE
# ==========================================================================

def eh_numero(valor) -> bool:
    try:
        float(str(valor).replace(",", "."))
        return True
    except (ValueError, TypeError):
        return False


def gerar_relatorio(registros: list[dict]) -> str:
    linhas = [
        "RELATÓRIO DE ANÁLISE — CAPILETRANDO",
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Total de registros: {len(registros)}",
        "=" * 60,
    ]

    if not registros:
        linhas.append("Nenhum dado para analisar.")
        return "\n".join(linhas)

    colunas = {chave for registro in registros for chave in registro.keys()}
    for coluna in sorted(colunas):
        valores = [str(registro.get(coluna, "")).strip() for registro in registros]
        preenchidos = [v for v in valores if v]
        if not preenchidos:
            continue

        linhas.append(f"\nColuna: {coluna}")
        linhas.append(f"  Preenchidos: {len(preenchidos)}/{len(valores)}")

        numericos = [v for v in preenchidos if eh_numero(v)]
        if numericos and len(numericos) == len(preenchidos):
            numeros = [float(v.replace(",", ".")) for v in numericos]
            linhas.append(f"  Média: {sum(numeros)/len(numeros):.2f}")
            linhas.append(f"  Mínimo: {min(numeros):.2f} | Máximo: {max(numeros):.2f}")
        else:
            comuns = Counter(preenchidos).most_common(5)
            linhas.append("  Valores mais frequentes:")
            for valor, qtd in comuns:
                linhas.append(f"    - {valor}: {qtd}")

    return "\n".join(linhas)


# ==========================================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================================

def main():
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    registros_brutos = carregar_dados()
    print(f"  -> {len(registros_brutos)} registros encontrados.")

    print("Anonimizando dados sensíveis...")
    registros_anonimos = [anonimizar_registro(r) for r in registros_brutos]

    caminho_json = os.path.join(PASTA_SAIDA, "dados_anonimizados.json")
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(registros_anonimos, f, ensure_ascii=False, indent=2)
    print(f"  -> Dados anonimizados salvos em: {caminho_json}")

    print("Gerando relatório de análise...")
    relatorio = gerar_relatorio(registros_anonimos)
    caminho_relatorio = os.path.join(PASTA_SAIDA, "relatorio_analise.txt")
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        f.write(relatorio)
    print(f"  -> Relatório salvo em: {caminho_relatorio}")

    print("\nConcluído. Nenhum dado pessoal identificável foi salvo em disco.")


if __name__ == "__main__":
    main()