
from pathlib import Path
import math
import pandas as pd

from extrair_laudos import ajustes

arquivo_csv = Path("outputs/laudos_extraidos.csv")
pasta_output = Path("outputs")
pasta_output.mkdir(exist_ok=True, parents=True)

if not arquivo_csv.exists():
    raise FileNotFoundError(
        "Arquivo outputs/laudos_extraidos.csv não encontrado. "
        "Execute primeiro o script de extração."
    )

df = pd.read_csv(arquivo_csv)

campos = [
    "tipo_imovel",
    "endereco",
    "areas",
    "ano",
    "valor_avaliacao",
    "matricula",
    "onus",
    "data_vistoria",
    "responsavel_tecnico",
]


def normalizar(valor):
    if pd.isna(valor):
        return None

    if isinstance(valor, str):
        valor = " ".join(valor.split())
        if not valor:
            return None

    return valor


def valores_iguais(extraido, referencia):
    extraido = normalizar(extraido)
    referencia = normalizar(referencia)

    if extraido is None or referencia is None:
        return extraido is None and referencia is None

    if isinstance(referencia, (int, float)) and not isinstance(
        referencia, bool
    ):
        try:
            return math.isclose(
                float(extraido),
                float(referencia),
                rel_tol=0,
                abs_tol=0.01,
            )
        except (ValueError, TypeError):
            return False

    return str(extraido).casefold() == str(referencia).casefold()


resultados = []

for _, linha in df.iterrows():
    nome = linha["arquivo"]
    referencia_laudo = ajustes.get(nome)

    if referencia_laudo is None:
        raise ValueError(
            f"Não existe referência revisada para {nome}."
        )

    for campo in campos:
        valor_extraido = linha.get(campo)
        valor_referencia = referencia_laudo.get(campo)

        if valores_iguais(valor_extraido, valor_referencia):
            if normalizar(valor_referencia) is None:
                status = "Ausência corretamente registrada"
            else:
                status = "Correto"
        else:
            status = "Divergência para revisar"

        resultados.append({
            "arquivo": nome,
            "campo": campo,
            "valor_extraido": normalizar(valor_extraido),
            "valor_referencia": normalizar(valor_referencia),
            "status": status,
        })

df_validacao = pd.DataFrame(resultados)

total = len(df_validacao)
corretos = (df_validacao["status"] == "Correto").sum()
ausencias_corretas = (
    df_validacao["status"] == "Ausência corretamente registrada"
).sum()
divergencias = (
    df_validacao["status"] == "Divergência para revisar"
).sum()

# Mede a correspondência com a referência revisada.
acertos = corretos + ausencias_corretas
acuracia = (acertos / total * 100) if total else 0

df_validacao.to_csv(
    pasta_output / "validacao_laudos.csv",
    index=False,
    encoding="utf-8-sig",
)

print("Validação dos laudos")
print()
print("Total de campos comparados:", total)
print("Campos corretos:", corretos)
print("Ausências corretamente registradas:", ausencias_corretas)
print("Divergências para revisar:", divergencias)
print(f"Correspondência com a referência: {acuracia:.2f}%")
print()
print("Arquivo salvo: outputs/validacao_laudos.csv")

if divergencias:
    print()
    print("Campos que precisam de revisão:")
    print(
        df_validacao.loc[
            df_validacao["status"] == "Divergência para revisar",
            ["arquivo", "campo", "valor_extraido", "valor_referencia"],
        ].to_string(index=False)
    )
