# nomes das colunas da planilha
# quando chegar a planilha real, é só trocar os nomes aqui

ID = "id_caso"
ALVO = "exigiu_atencao"  # 1 = o caso precisou de atenção prioritária, 0 = não

COLUNAS_NUMERICAS = [
    "dias_sem_contato",
    "ocorrencias_90d",
    "pendencias_abertas",
    "tempo_resposta_h",
    "reaberturas",
]
COLUNAS_TEXTO = ["categoria", "canal"]

# como cada coluna aparece escrita no painel (a equipe não precisa ver o nome técnico)
NOMES_AMIGAVEIS = {
    "dias_sem_contato": "dias sem contato",
    "ocorrencias_90d": "ocorrências nos últimos 90 dias",
    "pendencias_abertas": "pendências abertas",
    "tempo_resposta_h": "tempo médio de resposta (h)",
    "reaberturas": "reaberturas",
}

# faixas de prioridade: a partir de 60% é alta, a partir de 30% é média
LIMITE_ALTA = 0.60
LIMITE_MEDIA = 0.30

ARQUIVO_MODELO = "modelo/modelo.joblib"
