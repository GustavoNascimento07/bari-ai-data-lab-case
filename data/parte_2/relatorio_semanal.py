import logging
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle

CAMINHO_BASE = Path("data/raw/propostas_credito.csv")
PASTA_OUTPUT = Path("outputs")
ARQUIVO_LOG = PASTA_OUTPUT / "relatorio_semanal.log"

COLUNAS_OBRIGATORIAS = [
    "id_proposta", "data_entrada", "tipo_imovel",
    "valor_imovel", "valor_solicitado", "status_final"
]

COLUNAS_ESPERADAS = [
    "id_proposta", "data_entrada", "canal_origem", "cidade", "uf",
    "tipo_imovel", "valor_imovel", "valor_solicitado", "prazo_meses",
    "score_credito", "idade_cliente", "renda_mensal_declarada",
    "flag_cliente_recorrente", "consultor_id", "etapa_max_funil",
    "status_final", "tempo_analise_dias", "data_assinatura_contrato",
    "taxa_juros_aa"
]


def configurar_log():
    PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(ARQUIVO_LOG),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        force=True,
    )


def converter_moeda(valor):
    """Converte números e valores monetários brasileiros para float."""
    if pd.isna(valor):
        return float("nan")
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", "null"}:
        return float("nan")

    texto = texto.replace("R$", "").replace("\u00a0", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return float("nan")


def formatar_reais(valor):
    if pd.isna(valor):
        return "Não informado"
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_base():
    if not CAMINHO_BASE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CAMINHO_BASE}")

    df = pd.read_csv(CAMINHO_BASE, low_memory=False)
    logging.info("Base carregada: %s registros", len(df))
    print(f"Base carregada com sucesso: {len(df)} propostas.")

    ausentes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if ausentes:
        raise ValueError(f"Colunas obrigatórias ausentes: {ausentes}")

    faltantes = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    novas = [c for c in df.columns if c not in COLUNAS_ESPERADAS]
    if faltantes:
        mensagem = f"Colunas esperadas ausentes: {faltantes}"
        logging.warning(mensagem)
        print(f"AVISO: {mensagem}")
    if novas:
        mensagem = f"Novas colunas encontradas: {novas}"
        logging.warning(mensagem)
        print(f"AVISO: {mensagem}")
    return df


def preparar_base(df):
    df = df.copy()
    df["tipo_imovel"] = df["tipo_imovel"].astype("string").str.strip()
    df["status_final"] = df["status_final"].astype("string").str.strip()

    antes = len(df)
    df = df[df["tipo_imovel"].str.casefold() != "terreno"].copy()
    logging.info("Terrenos removidos: %s; base final: %s", antes - len(df), len(df))

    for coluna in ["valor_imovel", "valor_solicitado"]:
        original = df[coluna].copy()
        df[coluna] = original.map(converter_moeda)
        invalidos = int((df[coluna].isna() & original.notna()).sum())
        if invalidos:
            mensagem = f"{invalidos} valores inválidos ou ausentes em {coluna}"
            logging.warning(mensagem)
            print(f"AVISO: {mensagem}.")

    df["data_entrada"] = pd.to_datetime(
        df["data_entrada"], errors="coerce", dayfirst=True, format="mixed"
    )
    datas_invalidas = int(df["data_entrada"].isna().sum())
    if datas_invalidas:
        mensagem = f"{datas_invalidas} datas de entrada inválidas ou ausentes"
        logging.warning(mensagem)
        print(f"AVISO: {mensagem}; esses registros não entrarão no relatório semanal.")

    df = df.dropna(subset=["data_entrada"]).copy()
    df["semana"] = df["data_entrada"].dt.to_period("W").astype(str)
    df["contratada"] = (df["status_final"].str.casefold() == "contratada").astype(int)
    return df


def criar_relatorio(df):
    relatorio = (
        df.groupby("semana", as_index=False)
        .agg(
            propostas=("id_proposta", "count"),
            contratadas=("contratada", "sum"),
            valor_solicitado=("valor_solicitado", "sum"),
        )
        .sort_values("semana")
    )

    # Evita mostrar R$ 0,00 quando todos os valores da semana estão ausentes.
    semanas_com_valor = df.groupby("semana")["valor_solicitado"].count()
    relatorio["quantidade_valores"] = relatorio["semana"].map(semanas_com_valor)
    relatorio.loc[relatorio["quantidade_valores"] == 0, "valor_solicitado"] = float("nan")
    relatorio = relatorio.drop(columns="quantidade_valores")
    relatorio["taxa_contratacao"] = (
        relatorio["contratadas"] / relatorio["propostas"] * 100
    ).round(2)
    return relatorio


def exportar_tabelas(relatorio):
    csv = PASTA_OUTPUT / "relatorio_semanal.csv"
    excel = PASTA_OUTPUT / "relatorio_semanal.xlsx"
    html = PASTA_OUTPUT / "relatorio_semanal.html"

    relatorio.to_csv(csv, index=False, encoding="utf-8-sig")
    try:
        relatorio.to_excel(excel, index=False)
    except ImportError as erro:
        logging.exception("Dependência ausente para gerar Excel")
        raise RuntimeError("Instale a dependência openpyxl: pip install openpyxl") from erro

    tabela = relatorio.copy()
    tabela["valor_solicitado"] = tabela["valor_solicitado"].map(formatar_reais)
    tabela["taxa_contratacao"] = tabela["taxa_contratacao"].map(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "Não informado"
    )
    conteudo = tabela.to_html(index=False, escape=True, border=0)
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório semanal de contratação</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
h1 {{ font-size: 22px; }}
p {{ color: #555; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background: #eee; }}
tr:nth-child(even) {{ background: #f8f8f8; }}
</style>
</head>
<body>
<h1>Relatório semanal de contratação</h1>
<p>Taxa de contratação = propostas contratadas / total de propostas da semana.</p>
{conteudo}
</body>
</html>"""
    html.write_text(pagina, encoding="utf-8")
    return [csv, excel, html]


def exportar_pdf(relatorio):
    pdf = PASTA_OUTPUT / "relatorio_semanal.pdf"
    documento = SimpleDocTemplate(
        str(pdf), pagesize=landscape(A4),
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )
    estilos = getSampleStyleSheet()
    elementos = [
        Paragraph("Relatório Semanal de Contratação", estilos["Title"]),
        Spacer(1, 5 * mm),
        Paragraph(
            "Taxa de contratação = propostas contratadas divididas pelo total de propostas da semana.",
            estilos["BodyText"],
        ),
        Spacer(1, 4 * mm),
    ]
    dados = [["Semana", "Propostas", "Contratadas", "Valor solicitado", "Taxa"]]
    for _, linha in relatorio.iterrows():
        taxa = f'{linha["taxa_contratacao"]:.2f}%'
        dados.append([
            str(linha["semana"]), str(int(linha["propostas"])),
            str(int(linha["contratadas"])), formatar_reais(linha["valor_solicitado"]), taxa
        ])

    tabela = LongTable(dados, repeatRows=1, colWidths=[48 * mm, 25 * mm, 28 * mm, 48 * mm, 25 * mm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabela)
    documento.build(elementos)
    return pdf


def main():
    configurar_log()
    logging.info("Início da geração do relatório semanal")
    try:
        df = preparar_base(carregar_base())
        if df.empty:
            raise ValueError("Nenhum registro válido restou após filtros e validação de datas.")

        relatorio = criar_relatorio(df)
        arquivos = exportar_tabelas(relatorio)
        arquivos.append(exportar_pdf(relatorio))
        logging.info(
            "Relatórios gerados. Semanas: %s; propostas: %s", len(relatorio), len(df)
        )
        print("\nRelatório semanal gerado com sucesso!")
        print(f"Semanas no relatório: {len(relatorio)}")
        print(f"Propostas consideradas: {len(df)}")
        for arquivo in arquivos:
            print(f"Arquivo: {arquivo}")
        print(f"Log: {ARQUIVO_LOG}")

    except FileNotFoundError as erro:
        logging.error("%s", erro)
        print(f"\nERRO: {erro}")
    except ValueError as erro:
        logging.error("%s", erro)
        print(f"\nERRO de validação: {erro}")
    except Exception as erro:
        logging.exception("Erro inesperado durante a execução")
        print(f"\nERRO inesperado: {erro}")
        raise


if __name__ == "__main__":
    main()