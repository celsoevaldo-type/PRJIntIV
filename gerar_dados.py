import numpy as np
import pandas as pd

from config import ALVO

# ainda não temos os dados reais da organização, então geramos dados
# falsos com as mesmas colunas só para testar o sistema


def gerar(quantidade, semente):
    sorteio = np.random.default_rng(semente)  # semente fixa = sempre gera os mesmos dados

    categoria = sorteio.choice(["A", "B", "C", "D"], size=quantidade, p=[0.35, 0.30, 0.20, 0.15])
    canal = sorteio.choice(["presencial", "telefone", "online"], size=quantidade, p=[0.4, 0.35, 0.25])
    dias_sem_contato = sorteio.gamma(2.0, 12.0, quantidade).round().astype(int)
    ocorrencias = sorteio.poisson(2.0, quantidade)
    pendencias = sorteio.poisson(1.2, quantidade)
    tempo_resposta = sorteio.gamma(2.5, 10.0, quantidade).round(1)
    reaberturas = sorteio.poisson(0.4, quantidade)

    # aqui inventamos uma "regra" para decidir quais casos foram prioritários:
    # quanto mais dias sem contato, pendências, reaberturas etc, maior a chance.
    # o ruído no final serve para não ficar uma regra perfeita (a vida real não é)
    pontos = (
        -4.2
        + 0.035 * dias_sem_contato
        + 0.30 * ocorrencias
        + 0.45 * pendencias
        + 0.015 * tempo_resposta
        + 0.60 * reaberturas
        + np.select([categoria == "C", categoria == "D"], [0.5, 0.9], 0.0)
        + np.where(canal == "online", -0.3, 0.0)
        + sorteio.normal(0, 0.6, quantidade)
    )
    chance = 1 / (1 + np.exp(-pontos))  # transforma os pontos em uma chance entre 0 e 1
    exigiu_atencao = (sorteio.random(quantidade) < chance).astype(int)

    return pd.DataFrame({
        "id_caso": [f"C{i:05d}" for i in range(1, quantidade + 1)],
        "categoria": categoria,
        "canal": canal,
        "dias_sem_contato": dias_sem_contato,
        "ocorrencias_90d": ocorrencias,
        "pendencias_abertas": pendencias,
        "tempo_resposta_h": tempo_resposta,
        "reaberturas": reaberturas,
        ALVO: exigiu_atencao,
    })


if __name__ == "__main__":
    # histórico = casos antigos, já sabemos se foram prioritários ou não (usado para treinar)
    historico = gerar(2000, semente=42)
    historico.to_csv("dados/historico_simulado.csv", index=False)

    # casos abertos = casos de hoje, sem a resposta (é o que vai para o painel)
    abertos = gerar(60, semente=7).drop(columns=[ALVO])
    abertos.to_csv("dados/casos_abertos_simulado.csv", index=False)

    print("Histórico:", len(historico), "casos")
    print("Prioritários:", round(historico[ALVO].mean() * 100, 1), "%")
    print("Casos abertos para testar o painel:", len(abertos))
