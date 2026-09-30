# Painel de Prioridades

Projeto Integrador em Computação IV – Univesp – Grupo 6

Usa o histórico de casos da organização para estimar quais casos em aberto
precisam de atenção primeiro, e mostra isso num painel simples.

**Atenção:** os dados da pasta `dados/` são simulados (inventados), só para testar.

## Como rodar

```
pip install -r requirements.txt
python gerar_dados.py
python treinar.py
streamlit run painel.py
```

No painel, envie o arquivo `dados/casos_abertos_simulado.csv`.

## O que cada arquivo faz

- `config.py` – nomes das colunas e faixas de prioridade
- `gerar_dados.py` – cria os dados simulados
- `treinar.py` – compara 5 modelos, escolhe o de maior F1 e salva
- `priorizar.py` – calcula a chance, a faixa (alta/média/baixa) e o motivo de cada caso
- `painel.py` – a tela usada pela equipe

## Para usar com os dados reais

1. Exportar o histórico em CSV, uma linha por caso, com uma coluna dizendo se o
   caso foi prioritário (1) ou não (0).
2. Tirar nomes, documentos e telefones antes (LGPD).
3. Ajustar os nomes das colunas no `config.py`.
4. Rodar `python treinar.py caminho/do/arquivo.csv`.
