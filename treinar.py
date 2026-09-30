import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from config import ALVO, ARQUIVO_MODELO, COLUNAS_NUMERICAS, COLUNAS_TEXTO

# os 5 métodos que vamos comparar
# class_weight="balanced" dá mais peso para os casos prioritários, que são minoria
modelos = {
    "Árvore de decisão": DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=0),
    "k-NN (k=15)": KNeighborsClassifier(n_neighbors=15),
    "Naive Bayes": GaussianNB(),
    "Regressão logística": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Floresta aleatória": RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                                 class_weight="balanced", random_state=0),
}


def montar(modelo):
    # antes de chegar no modelo os dados passam por um preparo:
    # - números são colocados na mesma escala (senão "dias" pesa mais que "reaberturas")
    # - textos (categoria, canal) viram colunas de 0 e 1, porque o modelo só entende número
    preparo = ColumnTransformer([
        ("numeros", StandardScaler(), COLUNAS_NUMERICAS),
        ("textos", OneHotEncoder(handle_unknown="ignore"), COLUNAS_TEXTO),
    ])
    return Pipeline([("preparo", preparo), ("modelo", modelo)])


arquivo = sys.argv[1] if len(sys.argv) > 1 else "dados/historico_simulado.csv"
dados = pd.read_csv(arquivo)
X = dados[COLUNAS_NUMERICAS + COLUNAS_TEXTO]
y = dados[ALVO]

# separa 20% para o teste final. esses dados não são usados para escolher o modelo,
# só no fim, para ver como ele se sai com casos que nunca viu
# stratify=y mantém a mesma proporção de prioritários nas duas partes
X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)

# validação cruzada: divide o treino em 10 partes, treina em 9 e testa na que sobrou,
# 10 vezes, e tira a média
divisao = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
metricas = ["accuracy", "precision", "recall", "f1", "roc_auc"]

linhas = []
for nome, modelo in modelos.items():
    r = cross_validate(montar(modelo), X_treino, y_treino, cv=divisao, scoring=metricas,
                       return_train_score=True)
    linha = {"metodo": nome}
    for m in metricas:
        linha[m] = round(r["test_" + m].mean(), 3)
    # f1 no próprio treino: se for muito maior que na validação, é sinal de sobreajuste
    linha["f1_treino"] = round(r["train_f1"].mean(), 3)
    linhas.append(linha)

resultados = pd.DataFrame(linhas)
print(resultados.to_string(index=False))
resultados.to_csv("modelo/comparacao.csv", index=False)

# escolhemos pela F1 e não pela acurácia: como a maioria dos casos não é prioritária,
# um modelo que diz "não" para tudo já teria acurácia alta e não serviria para nada
melhor = resultados.sort_values("f1", ascending=False).iloc[0]["metodo"]
print("\nEscolhido:", melhor)

modelo_final = montar(modelos[melhor])
modelo_final.fit(X_treino, y_treino)

print("\nResultado no teste final (20% separados):")
print(classification_report(y_teste, modelo_final.predict(X_teste), digits=3))

joblib.dump({"modelo": modelo_final, "nome": melhor}, ARQUIVO_MODELO)
print("Modelo salvo em", ARQUIVO_MODELO)
