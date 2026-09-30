import sys

import joblib
import pandas as pd

from config import (ARQUIVO_MODELO, COLUNAS_NUMERICAS, COLUNAS_TEXTO, ID,
                    LIMITE_ALTA, LIMITE_MEDIA, NOMES_AMIGAVEIS)


def carregar_modelo():
    return joblib.load(ARQUIVO_MODELO)


def faixa(chance):
    if chance >= LIMITE_ALTA:
        return "Alta"
    if chance >= LIMITE_MEDIA:
        return "Média"
    return "Baixa"


def motivo(caso, medias, desvios):
    # explicação simples para a equipe: mostra até 2 sinais que estão bem acima
    # do normal. "bem acima" = mais de meio desvio padrão acima da média da planilha
    sinais = []
    for coluna in COLUNAS_NUMERICAS:
        distancia = (caso[coluna] - medias[coluna]) / desvios[coluna]
        if distancia > 0.5:
            sinais.append((distancia, coluna))

    if not sinais:
        return "sem sinal fora do comum"

    sinais.sort(reverse=True)  # os mais fora do normal primeiro
    textos = [f"{NOMES_AMIGAVEIS[c]} acima do usual ({caso[c]:g})" for _, c in sinais[:2]]
    return "; ".join(textos)


def priorizar(casos, pacote):
    modelo = pacote["modelo"]
    X = casos[COLUNAS_NUMERICAS + COLUNAS_TEXTO]

    # predict_proba devolve duas colunas: chance de "não" e chance de "sim".
    # pegamos a segunda, que é a chance do caso ser prioritário
    chances = modelo.predict_proba(X)[:, 1]

    medias = casos[COLUNAS_NUMERICAS].mean()
    desvios = casos[COLUNAS_NUMERICAS].std()

    resultado = casos.copy()
    resultado["probabilidade"] = chances.round(3)
    resultado["prioridade"] = [faixa(c) for c in chances]
    resultado["por_que"] = [motivo(caso, medias, desvios) for _, caso in casos.iterrows()]

    # ordena da maior chance para a menor: é essa a "fila" que a equipe vai ver
    return resultado.sort_values("probabilidade", ascending=False).reset_index(drop=True)


# também dá para usar sem o painel, pelo terminal:
# python priorizar.py dados/casos_abertos_simulado.csv saida.csv
if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "dados/casos_abertos_simulado.csv"
    lista = priorizar(pd.read_csv(entrada), carregar_modelo())
    print(lista[[ID, "prioridade", "probabilidade", "por_que"]].head(15).to_string(index=False))

    if len(sys.argv) > 2:
        lista.to_csv(sys.argv[2], index=False)
        print("\nLista completa salva em", sys.argv[2])
