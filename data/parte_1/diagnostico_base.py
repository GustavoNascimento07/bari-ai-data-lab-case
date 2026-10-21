from pathlib import Path
import json
import math
import pandas as pd

# Caminhos
arquivo_base = Path("data/raw/propostas_credito.csv")
pasta_saida = Path("outputs")
pasta_saida.mkdir(parents=True, exist_ok=True)

# Ler a base e conferir as colunas necessárias
df = pd.read_csv(arquivo_base)
print("Quantidade de propostas:", len(df))
print("Quantidade de colunas:", len(df.columns))

colunas_obrigatorias = [
    "id_proposta", "data_entrada", "canal_origem", "uf", "tipo_imovel",
    "valor_imovel", "valor_solicitado", "score_credito",
    "renda_mensal_declarada", "idade_cliente", "flag_cliente_recorrente",
    "etapa_max_funil", "status_final", "prazo_meses"
]
faltantes = [c for c in colunas_obrigatorias if c not in df.columns]
if faltantes:
    raise ValueError(f"Colunas obrigatórias ausentes: {faltantes}")

# Registrar a qualidade da base original
qualidade = {
    "propostas_originais": len(df),
    "colunas_originais": len(df.columns),
    "ids_duplicados": int(df["id_proposta"].duplicated().sum()),
    "linhas_completamente_duplicadas": int(df.duplicated().sum())
}

# Remover terrenos conforme o enunciado
df = df[
    df["tipo_imovel"].astype("string").str.strip().str.casefold() != "terreno"
].copy()
qualidade["propostas_apos_remocao_terrenos"] = len(df)
qualidade["terrenos_removidos"] = qualidade["propostas_originais"] - len(df)
print("Propostas após remoção de terrenos:", len(df))

# Converter números, incluindo valores no padrão brasileiro
def converter_numero(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")

    texto = serie.astype("string").str.strip()
    texto = texto.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)
    tem_virgula = texto.str.contains(",", na=False)
    texto.loc[tem_virgula] = (
        texto.loc[tem_virgula]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(texto, errors="coerce")

colunas_numericas = [
    "valor_imovel", "valor_solicitado", "renda_mensal_declarada",
    "score_credito", "idade_cliente", "prazo_meses", "etapa_max_funil"
]
for coluna in colunas_numericas:
    df[coluna] = converter_numero(df[coluna])

# Calcular LTV e indicador de contratação
df["ltv_calculado"] = df["valor_solicitado"] / df["valor_imovel"].where(df["valor_imovel"] > 0)
df["acima_ltv_60"] = df["ltv_calculado"] > 0.60
df["contratada"] = (
    df["status_final"].astype("string").str.strip().str.casefold() == "contratada"
).astype(int)
df["canal_origem"] = df["canal_origem"].astype("string").str.strip().str.casefold()

print("Propostas acima de 60% de LTV:", int(df["acima_ltv_60"].sum()))
print("Percentual acima de 60%:", round(df["acima_ltv_60"].mean() * 100, 2), "%")

# Função reutilizada para resumir contratação por grupo
def analisar_grupo(coluna, nome_arquivo, ordenar=False):
    resultado = (
        df.dropna(subset=[coluna])
        .groupby(coluna, observed=True)["contratada"]
        .agg(propostas="count", contratadas="sum", taxa_contratacao="mean")
    )
    resultado["taxa_contratacao"] = resultado["taxa_contratacao"] * 100
    if ordenar:
        resultado = resultado.sort_values("taxa_contratacao", ascending=False)
    resultado.to_csv(pasta_saida / nome_arquivo)
    print(f"\nContratação por {coluna}:")
    print(resultado.round(2))
    return resultado

# LTV por grupo
resumo_ltv = (
    df.dropna(subset=["ltv_calculado"])
    .groupby("acima_ltv_60")["contratada"]
    .agg(propostas="count", contratadas="sum", taxa_contratacao="mean")
)
resumo_ltv["taxa_contratacao"] *= 100
resumo_ltv.to_csv(pasta_saida / "contratacao_por_ltv.csv")
print("\nContratação por faixa de LTV:")
print(resumo_ltv.round(2))

# Valor solicitado por status e etapa
valor_status = (
    df.groupby("status_final")["valor_solicitado"]
    .agg(propostas="count", valor_total="sum")
    .sort_values("valor_total", ascending=False)
)
valor_status.to_csv(pasta_saida / "valor_por_status.csv")

valor_etapa = (
    df.groupby("etapa_max_funil")["valor_solicitado"]
    .agg(propostas="count", valor_total="sum")
    .sort_index()
)
valor_etapa.to_csv(pasta_saida / "valor_por_etapa.csv")

etapas_invalidas = df[
    df["etapa_max_funil"].notna() & ~df["etapa_max_funil"].between(1, 6)
]
etapas_invalidas.to_csv(pasta_saida / "etapas_fora_do_intervalo.csv", index=False)
print("\nPropostas com etapa fora do intervalo de 1 a 6:", len(etapas_invalidas))

# Conversão mensal
df["data_entrada"] = pd.to_datetime(
    df["data_entrada"], format="mixed", dayfirst=True, errors="coerce"
)
df["mes_entrada"] = df["data_entrada"].dt.to_period("M").astype("string")
mensal = (
    df.dropna(subset=["data_entrada"])
    .groupby("mes_entrada")["contratada"]
    .agg(propostas="count", contratadas="sum", conversao="mean")
)
mensal["conversao"] *= 100
mensal.to_csv(pasta_saida / "conversao_mensal.csv")
print("\nConversão mensal:")
print(mensal.round(2))

# Comparar os principais grupos
analisar_grupo("canal_origem", "desempenho_canal.csv")
df["faixa_score"] = pd.cut(
    df["score_credito"], [0, 600, 700, 800, float("inf")],
    labels=["Até 600", "601-700", "701-800", "Acima de 800"],
    include_lowest=True
)
analisar_grupo("faixa_score", "contratacao_por_score.csv")
analisar_grupo("flag_cliente_recorrente", "contratacao_recorrente.csv")
analisar_grupo("tipo_imovel", "contratacao_tipo_imovel.csv")

df["faixa_renda"] = pd.cut(
    df["renda_mensal_declarada"], [0, 3000, 5000, 8000, 12000, float("inf")],
    labels=["Até 3 mil", "Acima de 3 até 5 mil", "Acima de 5 até 8 mil",
            "Acima de 8 até 12 mil", "Acima de 12 mil"],
    include_lowest=True
)
analisar_grupo("faixa_renda", "contratacao_por_renda.csv")

df["faixa_idade"] = pd.cut(
    df["idade_cliente"], [0, 30, 40, 50, 60, float("inf")],
    labels=["Até 30", "31-40", "41-50", "51-60", "Acima de 60"],
    include_lowest=True
)
analisar_grupo("faixa_idade", "contratacao_por_idade.csv")

df["faixa_ticket"] = pd.qcut(
    df["valor_solicitado"], q=4,
    labels=["Ticket baixo", "Ticket médio-baixo", "Ticket médio-alto", "Ticket alto"],
    duplicates="drop"
)
analisar_grupo("faixa_ticket", "contratacao_por_ticket.csv")

df["faixa_prazo"] = pd.cut(
    df["prazo_meses"], [0, 60, 120, 180, 240, float("inf")],
    labels=["Até 60 meses", "61-120 meses", "121-180 meses",
            "181-240 meses", "Acima de 240 meses"],
    include_lowest=True
)
analisar_grupo("faixa_prazo", "contratacao_por_prazo.csv")
analisar_grupo("uf", "contratacao_por_uf.csv")

# Cenários hipotéticos de impacto
sem_retorno = df[
    df["status_final"].astype("string").str.strip().str.casefold() == "sem retorno"
]
correspondente = df[df["canal_origem"] == "correspondente"]
taxa_correspondente = correspondente["contratada"].mean() if len(correspondente) else 0
meta_conversao = 0.18
contratos_adicionais = max(0, len(correspondente) * (meta_conversao - taxa_correspondente))
ticket_medio = correspondente["valor_solicitado"].mean() if len(correspondente) else 0
valor_potencial = contratos_adicionais * ticket_medio

cenarios = pd.DataFrame({
    "indicador": [
        "Propostas sem retorno",
        "Valor solicitado sem retorno",
        "Recuperação hipotética de 5% das propostas",
        "Valor hipotético correspondente a 5% do valor solicitado",
        "Taxa atual do Correspondente (%)",
        "Meta hipotética do Correspondente (%)",
        "Contratos adicionais estimados",
        "Valor solicitado potencialmente convertido"
    ],
    "valor": [
        len(sem_retorno), sem_retorno["valor_solicitado"].sum(),
        len(sem_retorno) * 0.05, sem_retorno["valor_solicitado"].sum() * 0.05,
        taxa_correspondente * 100, meta_conversao * 100,
        contratos_adicionais, valor_potencial
    ]
})
cenarios.to_csv(pasta_saida / "cenarios_impacto.csv", index=False)

# Intervalos de confiança de 95% pelo método de Wilson
def intervalo_wilson(sucessos, total, z=1.96):
    if total == 0:
        return None, None
    p = sucessos / total
    denominador = 1 + z**2 / total
    centro = (p + z**2 / (2 * total)) / denominador
    margem = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominador
    return max(0, centro - margem), min(1, centro + margem)

confianca = []
for canal, grupo in df.groupby("canal_origem", dropna=False):
    total = len(grupo)
    contratos = int(grupo["contratada"].sum())
    inferior, superior = intervalo_wilson(contratos, total)
    confianca.append({
        "canal": str(canal),
        "propostas": total,
        "contratadas": contratos,
        "taxa_contratacao_pct": round(contratos / total * 100, 2) if total else None,
        "ic95_inferior_pct": round(inferior * 100, 2) if inferior is not None else None,
        "ic95_superior_pct": round(superior * 100, 2) if superior is not None else None,
        "observacao": "IC de 95% da taxa do canal; não comprova causalidade."
    })
pd.DataFrame(confianca).to_csv(pasta_saida / "confianca_por_canal.csv", index=False)

# Recomendações priorizadas
recomendacoes = pd.DataFrame([
    {
        "prioridade": 1,
        "acao": "Criar rotina de recuperação de propostas sem retorno",
        "evidencia": f'{len(sem_retorno)} propostas e R$ {sem_retorno["valor_solicitado"].sum():,.2f} em valor solicitado estão sem retorno.',
        "impacto_estimado": f'Recuperar hipoteticamente 5% equivale a cerca de {len(sem_retorno) * 0.05:.0f} propostas e R$ {sem_retorno["valor_solicitado"].sum() * 0.05:,.2f}.',
        "premissas": "Supõe recuperação de 5%; não garante aprovação nem contratação.",
        "limitacoes": "Valor solicitado não é receita nem valor garantido."
    },
    {
        "prioridade": 2,
        "acao": "Investigar o canal Correspondente por etapa e motivo de perda",
        "evidencia": f"Conversão de {taxa_correspondente * 100:.2f}% em {len(correspondente)} propostas.",
        "impacto_estimado": f"Meta hipotética de 18%: cerca de {contratos_adicionais:.0f} contratos adicionais e R$ {valor_potencial:,.2f} em valor solicitado associado.",
        "premissas": "Mantém o volume atual e eleva a conversão até 18%.",
        "limitacoes": "Cenário hipotético; valor usa o ticket médio solicitado e não representa receita."
    },
    {
        "prioridade": 3,
        "acao": "Priorizar acompanhamento com score, LTV e valor solicitado",
        "evidencia": "Score mais alto está associado a maior conversão; LTV acima de 60% apresenta conversão menor.",
        "impacto_estimado": "Não quantificado; medir em piloto antes de atribuir ganho.",
        "premissas": "Usar indicadores para organizar o acompanhamento, sem substituir a política de crédito.",
        "limitacoes": "Associação descritiva não comprova causalidade."
    }
])
recomendacoes.to_csv(pasta_saida / "recomendacoes_priorizadas.csv", index=False)

# Registrar as decisões de tratamento
qualidade["valores_ausentes_por_coluna"] = df[
    ["data_entrada", "valor_imovel", "valor_solicitado", "score_credito",
     "renda_mensal_declarada", "idade_cliente", "prazo_meses", "etapa_max_funil"]
].isna().sum().to_dict()
qualidade["ltv_invalido_ou_ausente"] = int(df["ltv_calculado"].isna().sum())

registro = pd.DataFrame([
    {
        "problema": "Imóveis do tipo Terreno",
        "tratamento": "Removidos da análise",
        "justificativa": "Regra indicada no desafio.",
        "quantidade": qualidade["terrenos_removidos"]
    },
    {
        "problema": "LTV ausente na base",
        "tratamento": "Calculado como valor_solicitado / valor_imovel, se valor_imovel > 0",
        "justificativa": "Fórmula indicada no dicionário de dados.",
        "quantidade": qualidade["ltv_invalido_ou_ausente"]
    },
    {
        "problema": "IDs duplicados",
        "tratamento": "Contabilizados e preservados para investigação",
        "justificativa": "Não excluir sem confirmar se são duplicidades reais.",
        "quantidade": qualidade["ids_duplicados"]
    },
    {
        "problema": "Linhas completamente duplicadas",
        "tratamento": "Contabilizadas e preservadas para investigação",
        "justificativa": "Evitar exclusão automática sem validação.",
        "quantidade": qualidade["linhas_completamente_duplicadas"]
    },
    {
        "problema": "Valores ausentes ou inválidos",
        "tratamento": "Mantidos como ausentes, sem preenchimento arbitrário",
        "justificativa": "Não há base suficiente para inferir valores.",
        "quantidade": int(sum(qualidade["valores_ausentes_por_coluna"].values()))
    },
    {
        "problema": "Etapa fora do intervalo 1 a 6",
        "tratamento": "Preservada e exportada para investigação",
        "justificativa": "Validar a ocorrência com a origem.",
        "quantidade": len(etapas_invalidas)
    },
    {
        "problema": "Conversão mensal oscilante",
        "tratamento": "Analisada como série descritiva",
        "justificativa": "Não declarar queda contínua sem evidência.",
        "quantidade": len(mensal)
    }
])
registro.to_csv(pasta_saida / "registro_tratamento_dados.csv", index=False)

qualidade["registro_tratamento"] = registro.to_dict(orient="records")
qualidade["observacoes_analiticas"] = [
    "Resultados descritivos não demonstram causalidade.",
    "Valor solicitado não equivale a receita ou perda financeira realizada.",
    "Cenários de impacto são hipóteses e dependem de validação operacional.",
    "Comparações entre canais podem refletir diferenças de perfil e processo.",
    "Etapas fora do intervalo esperado foram preservadas para investigação."
]
with open(pasta_saida / "qualidade_dados.json", "w", encoding="utf-8") as f:
    json.dump(qualidade, f, ensure_ascii=False, indent=2, default=str)

# Salvar a base tratada para auditoria
df.to_csv(pasta_saida / "base_tratada_parte1.csv", index=False, encoding="utf-8-sig")

print("\nParte 1 concluída. Arquivos salvos em:", pasta_saida.resolve())
print("Arquivos adicionais: recomendacoes_priorizadas.csv, registro_tratamento_dados.csv,")
print("confianca_por_canal.csv e qualidade_dados.json")