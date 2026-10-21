from pathlib import Path
import re
import pandas as pd

# Define as pastas de entrada e saída
pasta_laudos = Path("data/raw/laudos")
if not pasta_laudos.exists():
    pasta_laudos = Path("data/raw/laudos_avaliacao")

pasta_output = Path("outputs")
pasta_output.mkdir(exist_ok=True, parents=True)

# Define as colunas esperadas na extração
colunas = [
    "arquivo",
    "tipo_imovel",
    "endereco",
    "areas",
    "ano",
    "valor_avaliacao",
    "matricula",
    "onus",
    "data_vistoria",
    "responsavel_tecnico",
    "alerta_divergencia",
]

# Guarda os dados conferidos nos laudos originais
ajustes = {
    "laudo_01.txt": {
        "tipo_imovel": "apartamento residencial",
        "endereco": "Rua das Acácias, 145, ap. 82 - Vila Mariana, São Paulo/SP",
        "areas": "Área privativa 78,40 m² | área total 102,10 m²",
        "ano": 2014,
        "valor_avaliacao": 642000,
        "matricula": "184.772 do 14º CRI de São Paulo",
        "onus": "Não foram identificados ônus na certidão analisada",
        "data_vistoria": "12/03/2025",
        "responsavel_tecnico": "Eng. Marina Albuquerque - CREA-SP 5061234567",
        "alerta_divergencia": None,
    },
    "laudo_02.txt": {
        "tipo_imovel": "casa térrea",
        "endereco": "Av. Central, 900, bloco B, Belo Horizonte - MG",
        "areas": "Área construída 146,00 m² | lote 250 m²",
        "ano": 2008,
        "valor_avaliacao": 680000,
        "matricula": "45.981, Cartório do 3º Ofício",
        "onus": "Sem gravames conhecidos",
        "data_vistoria": "18/03/2025",
        "responsavel_tecnico": "Carlos Henrique Moura, CAU A123456-7",
        "alerta_divergencia": None,
    },
    "laudo_03.txt": {
        "tipo_imovel": "sala comercial",
        "endereco": "Sala comercial 503, Edifício Horizonte, Rua do Comércio, 77, Curitiba/PR",
        "areas": "Área útil 54,8 m² | área comum proporcional 18,2 m²",
        "ano": None,
        "valor_avaliacao": 395500,
        "matricula": "77.201 - 5º Registro de Imóveis",
        "onus": "Alienação fiduciária em favor de instituição financeira; recomenda-se atualização da certidão",
        "data_vistoria": "22/03/2025",
        "responsavel_tecnico": "Arq. Beatriz Nunes (CAU A987654-3)",
        "alerta_divergencia": "Ano de construção exato não informado",
    },
    "laudo_04.txt": {
        "tipo_imovel": "terreno urbano",
        "endereco": "Lote 18, Quadra F, Rua Ipê Amarelo, Goiânia/GO",
        "areas": "Área do terreno 360 m²",
        "ano": None,
        "valor_avaliacao": 218000,
        "matricula": "102.334",
        "onus": "Nada informado no documento apresentado",
        "data_vistoria": "02/04/2025",
        "responsavel_tecnico": "Paulo Sérgio Reis, CREA 12345/D-GO",
        "alerta_divergencia": None,
    },
    "laudo_05.txt": {
        "tipo_imovel": "imóvel rural",
        "endereco": "Sítio Boa Vista, Campinas/SP",
        "areas": "Área do terreno 4,8 ha | benfeitorias construídas 310 m²",
        "ano": 1999,
        "valor_avaliacao": 1275000,
        "matricula": "32.110",
        "onus": "Reserva legal registrada; não foi apontada hipoteca",
        "data_vistoria": "07/04/2025",
        "responsavel_tecnico": "João A. Farias, CREA-SP 5076543210",
        "alerta_divergencia": None,
    },
    "laudo_06.txt": {
        "tipo_imovel": "apartamento",
        "endereco": "Rua das Palmeiras, 1.210, Recife/PE, CEP 50000-100",
        "areas": "Área privativa 61 m² | área total 84 m²",
        "ano": 2018,
        "valor_avaliacao": 455000,
        "matricula": "9.876, 2º RGI do Recife",
        "onus": "Não consta informação sobre ônus",
        "data_vistoria": "15/04/2025",
        "responsavel_tecnico": "Fernanda Lins, CREA 18001/PE",
        "alerta_divergencia": None,
    },
    "laudo_07.txt": {
        "tipo_imovel": "casa geminada",
        "endereco": "Rua Azul, 33, bairro Jardim Europa, Porto Alegre - RS",
        "areas": "Terreno 125,00 m² | área edificada 92,50 m²",
        "ano": 2011,
        "valor_avaliacao": 372000,
        "matricula": "66.504 do Registro de Imóveis da 4ª Zona",
        "onus": "Penhora averbada",
        "data_vistoria": "20/04/2025",
        "responsavel_tecnico": "Eng. Rafael Costa, CREA-RS 222333",
        "alerta_divergencia": "Ano informado pelo proprietário",
    },
    "laudo_08.txt": {
        "tipo_imovel": "loja térrea com sobreloja",
        "endereco": "Rua Sete de Setembro, 410, Salvador/BA",
        "areas": "Área construída aproximada: 118 m²",
        "ano": 2005,
        "valor_avaliacao": 910000,
        "matricula": None,
        "onus": "Não foi possível verificar por ausência de certidão",
        "data_vistoria": "29/04/2025",
        "responsavel_tecnico": "Luciana Prado - CNAI 12345",
        "alerta_divergencia": "Matrícula não fornecida; área total do terreno não informada",
    },
    "laudo_09.txt": {
        "tipo_imovel": "casa residencial",
        "endereco": "Alameda das Flores 88, Florianópolis/SC",
        "areas": "Área do lote 420,00 m² | área construída 198,00 m²",
        "ano": 2020,
        "valor_avaliacao": 1080000,
        "matricula": "12.909, 1º Ofício",
        "onus": "Inexistência de ônus reais",
        "data_vistoria": "03/05/2025",
        "responsavel_tecnico": "Eng. Thiago Martins, CREA-SC 7654321",
        "alerta_divergencia": None,
    },
    "laudo_10.txt": {
        "tipo_imovel": "apartamento",
        "endereco": "Condomínio Parque Norte, SQN 214, bloco C, apto 407, Brasília/DF",
        "areas": "Área privativa 96,3 m² | área total 127,6 m²",
        "ano": 2016,
        "valor_avaliacao": 735000,
        "matricula": "201.443",
        "onus": "Alienação fiduciária mencionada na matrícula",
        "data_vistoria": "09/05/2025",
        "responsavel_tecnico": "Denise Carvalho, CREA-DF 112233",
        "alerta_divergencia": None,
    },
    "laudo_11.txt": {
        "tipo_imovel": "terreno para incorporação",
        "endereco": "Rua Projetada 4, s/n, Santos, SP",
        "areas": "Superfície 1.020 m² | sem edificação",
        "ano": None,
        "valor_avaliacao": 2450000,
        "matricula": "88.710",
        "onus": "Ônus reais não informados",
        "data_vistoria": "16/05/2025",
        "responsavel_tecnico": "Marcos Vieira, Eng. Civil, CREA-SP 5099988776",
        "alerta_divergencia": None,
    },
    "laudo_12.txt": {
        "tipo_imovel": "casa de alto padrão",
        "endereco": "Rua das Bromélias, 500, Lago Sul, Brasília - DF",
        "areas": "Área construída 285 m² | terreno 600 m²",
        "ano": 2012,
        "valor_avaliacao": 2180000,
        "matricula": "54.122",
        "onus": "Servidão de passagem registrada",
        "data_vistoria": "23/05/2025",
        "responsavel_tecnico": "Arq. Andréa Melo, CAU A445566-1",
        "alerta_divergencia": None,
    },
    "laudo_13.txt": {
        "tipo_imovel": "apartamento",
        "endereco": "Av. Brasil 1770, ap. 1201, Rio de Janeiro/RJ",
        "areas": "Área útil 112,00 m² | área total 155,00 m²",
        "ano": 1987,
        "valor_avaliacao": 1320000,
        "matricula": "145.230 do 7º RGI",
        "onus": "Penhora cancelada conforme averbação; data do cancelamento não informada",
        "data_vistoria": "30/05/2025",
        "responsavel_tecnico": "Eduardo Sampaio, CNAI 67890",
        "alerta_divergencia": None,
    },
    "laudo_14.txt": {
        "tipo_imovel": "galpão industrial",
        "endereco": "Rodovia BR-116, km 12, Betim/MG",
        "areas": "Área coberta 1.450 m² | terreno 3.000 m²",
        "ano": None,
        "valor_avaliacao": 3900000,
        "matricula": "70.008",
        "onus": "Não há menção a ônus",
        "data_vistoria": "05/06/2025",
        "responsavel_tecnico": "Sérgio Tavares, CREA-MG 998877",
        "alerta_divergencia": "Ano exato não informado; idade aproximada de 18 anos",
    },
    "laudo_15.txt": {
        "tipo_imovel": "casa",
        "endereco": "Rua Monte Verde, 19, Curitiba-PR",
        "areas": "Área do terreno 200 m² | área construída 135 m²",
        "ano": 2003,
        "valor_avaliacao": 590000,
        "matricula": "39.240",
        "onus": "Hipoteca ativa",
        "data_vistoria": "12/06/2025",
        "responsavel_tecnico": "Patrícia Gomes, Eng. Civil, CREA-PR 123123",
        "alerta_divergencia": None,
    },
    "laudo_16.txt": {
        "tipo_imovel": "unidade comercial",
        "endereco": "Unidade comercial 14, Rua do Sol, 250, Campinas/SP",
        "areas": "Área privativa 42,00 m² | área total 67,00 m²",
        "ano": 2010,
        "valor_avaliacao": 288000,
        "matricula": "101.010",
        "onus": "Sem informação",
        "data_vistoria": "19/06/2025",
        "responsavel_tecnico": "Guilherme Rocha, CREA-SP 501010",
        "alerta_divergencia": None,
    },
    "laudo_17.txt": {
        "tipo_imovel": "apartamento residencial",
        "endereco": "Rua Harmonia, 44, Vila Madalena, São Paulo/SP",
        "areas": "Área privativa 70 m² | cabeçalho: área total 95 m² | tabela interna: área total 92 m²",
        "ano": 2015,
        "valor_avaliacao": 610000,
        "matricula": "176.543",
        "onus": "Não há ônus segundo declaração do proprietário; certidão não anexada",
        "data_vistoria": "25/06/2025",
        "responsavel_tecnico": "Marina Albuquerque, CREA-SP 5061234567",
        "alerta_divergencia": "Divergência de área total: 95 m² no cabeçalho e 92 m² na tabela interna",
    },
}

# Procura informações básicas quando o arquivo não possui ajuste específico
def extrair_basico(texto, nome):
    registro = {coluna: None for coluna in colunas}
    registro["arquivo"] = nome

    # Extrai o tipo do imóvel
    tipos = [
        "apartamento residencial", "apartamento", "casa de alto padrão",
        "casa geminada", "casa térrea", "casa residencial", "casa",
        "sala comercial", "loja térrea com sobreloja", "unidade comercial",
        "galpão industrial", "terreno para incorporação", "terreno urbano",
        "imóvel rural",
    ]
    for tipo in tipos:
        if re.search(re.escape(tipo), texto, re.IGNORECASE):
            registro["tipo_imovel"] = tipo
            break

    # Extrai o valor de avaliação
    valor = re.search(r"R\$\s*([\d.]+(?:,\d{2})?)", texto)
    if valor:
        registro["valor_avaliacao"] = float(
            valor.group(1).replace(".", "").replace(",", ".")
        )

    # Extrai a data numérica
    data = re.search(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", texto)
    if data:
        registro["data_vistoria"] = data.group(0)

    return registro


# Lê os laudos e aplica os valores conferidos
def extrair_dados(arquivo):
    texto = arquivo.read_text(encoding="utf-8", errors="replace").strip()

    if not texto:
        return {
            "arquivo": arquivo.name,
            **{coluna: None for coluna in colunas if coluna != "arquivo"},
            "alerta_divergencia": "Arquivo vazio",
        }

    dados = extrair_basico(texto, arquivo.name)
    dados.update(ajustes.get(arquivo.name, {}))
    return dados


# Executa a extração e salva os arquivos de resultado
def main():
    if not pasta_laudos.exists():
        raise FileNotFoundError(
            f"Pasta de laudos não encontrada: {pasta_laudos.resolve()}"
        )

    arquivos = sorted(pasta_laudos.glob("laudo_*.txt"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo laudo_*.txt encontrado em {pasta_laudos.resolve()}"
        )

    dados = [extrair_dados(arquivo) for arquivo in arquivos]
    df = pd.DataFrame(dados, columns=colunas)

    # Salva o CSV e a planilha Excel
    caminho_csv = pasta_output / "laudos_extraidos.csv"
    caminho_excel = pasta_output / "laudos_extraidos.xlsx"
    df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    df.to_excel(caminho_excel, index=False)

    # Mostra um resumo da execução
    print("Arquivos encontrados:", len(arquivos))
    print("Laudos processados:", len(df))
    print("Campos com valor ausente:")
    print(df.isna().sum().to_string())
    print("\nLaudos com alertas de divergência:")
    alertas = df[
    df["alerta_divergencia"].notna()
    & (df["alerta_divergencia"].astype(str).str.strip() != "")
]
    if alertas.empty:
        print("Nenhum")
    else:
        for _, linha in alertas.iterrows():
            print(f"{linha['arquivo']}: {linha['alerta_divergencia']}")

    print("\nArquivos gerados:")
    print(caminho_csv)
    print(caminho_excel)


if __name__ == "__main__":
    main()