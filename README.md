# CapiLetrando — Script de Anonimização e Análise de Dados

Script em Python para tratar os dados coletados pelo CapiLetrando: remove/anonimiza informações pessoais identificáveis e gera um relatório estatístico simples sobre o uso do app.

## Equipe

- Giovana Marsigli Rodrigues
- Giovanna Aparecida Vivencio Rodrigues
- Mariana Akemi Arashiro Santos Feitosa

*Fatec Zona Leste — Análise e Desenvolvimento de Sistemas*

## O que o script faz

1. Lê um arquivo local com os dados coletados (`dados.json` ou `dados.csv`).
2. Remove ou anonimiza os campos sensíveis.
3. Gera os dados já tratados e um relatório de estatísticas na pasta `saida_capiletrando/`.

Todo o processamento é local — o script não se conecta à internet nem a nenhum banco de dados.

## Campos e regras de anonimização

| Campo | Tratamento aplicado |
|---|---|
| `nome`, `email`, `telefone`, `endereco` | Removidos por completo |
| `cpf`, `rg` | Removidos por completo |
| `data_nascimento` | Substituída por faixa etária (`4-5 anos`, `6-7 anos`, `8+ anos`) |
| Demais campos (ex: `pontuacao`, `atividade_concluida`, `conquistas`, `tempo_uso_minutos`) | Mantidos sem alteração |

Segue os princípios de minimização e anonimização da LGPD (Lei nº 13.709/2018), com atenção especial ao tratamento de dados de crianças (art. 14).

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa (só a biblioteca padrão do Python)

## Como usar

1. Coloque `capiletrando_analise.py` e um arquivo de dados (`dados.json` ou `dados.csv`) na mesma pasta.
2. Abra o terminal nessa pasta.
3. Rode:
   ```bash
   python capiletrando_analise.py
   ```
4. Confira os resultados em `saida_capiletrando/`:
   - `dados_anonimizados.json` — dados já tratados
   - `relatorio_analise.txt` — estatísticas descritivas por coluna

### Formato de `dados.json`

```json
[
  {
    "nome": "Maria Eduarda Silva",
    "email": "maria@exemplo.com",
    "cpf": "123.456.789-00",
    "data_nascimento": "2019-03-15",
    "atividade_concluida": "sim",
    "pontuacao": 85
  }
]
```

### Formato de `dados.csv`

```csv
nome,email,cpf,data_nascimento,atividade_concluida,pontuacao
Maria Eduarda Silva,maria@exemplo.com,123.456.789-00,2019-03-15,sim,85
```

## Ajustando para o schema real

Os nomes de campos considerados sensíveis estão configuráveis no topo do script, em `COLUNAS_PARA_REMOVER` e `COLUNA_DATA_NASCIMENTO`. Quando o projeto tiver uma base de dados real (ex: Firestore), é só exportar os registros mantendo o mesmo formato de colunas e apontar o script para esse arquivo.

## Estrutura de saída

```
saida_capiletrando/
├── dados_anonimizados.json
└── relatorio_analise.txt
```

