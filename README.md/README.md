# Bari AI & Data Lab

## Sobre o projeto

Este projeto foi desenvolvido como parte do desafio prático para o estágio de AI & Data Lab da Bari.

O objetivo foi analisar uma base de propostas de crédito imobiliário, identificar oportunidades de melhoria no funil, automatizar um relatório semanal e transformar laudos de avaliação imobiliária em dados estruturados.

## Parte 1 — Diagnóstico do funil

### Tratamento da base

A base original possuía 6.400 propostas e 19 colunas.

Conforme a orientação do desafio, foram removidos os registros em que `tipo_imovel = "Terreno"`.

- Base original: 6.400 propostas.
- Registros removidos: 535.
- Base final: 5.865 propostas.

A base não possuía uma coluna `ltv`, apesar de o campo estar previsto no dicionário de dados. Por isso, o LTV foi calculado utilizando:

`LTV = valor_solicitado / valor_imovel`

O limite de 60% foi utilizado como referência para a análise. Também foram realizados tratamentos de tipos de dados, principalmente nas colunas de valores e datas.

### Principais resultados

#### LTV

Foram identificadas 904 propostas com LTV acima de 60%, representando 15,41% da base final.

- LTV de até 60%: taxa de contratação de 20,54%.
- LTV acima de 60%: taxa de contratação de 12,06%.

A diferença foi de 8,48 pontos percentuais. Esse resultado indica uma associação entre LTV e contratação, sem demonstrar, por si só, uma relação causal.

#### Canais

O canal Correspondente apresentou a menor taxa de contratação entre os canais analisados.

| Canal | Propostas | Contratadas | Taxa de contratação |
|---|---:|---:|---:|
| Correspondente | 1.627 | 223 | 13,71% |
| Orgânico | 1.273 | 255 | 20,03% |
| Mídia paga | 1.166 | 250 | 21,44% |
| Indicação | 910 | 197 | 21,65% |
| Parceria | 889 | 203 | 22,83% |

O canal Correspondente apresentou um score de crédito médio inferior. Recomenda-se investigar a qualidade das propostas e as etapas em que ocorrem as maiores perdas.

#### Evolução temporal

A taxa de contratação apresentou oscilações durante o período analisado. Os dados não indicam uma queda contínua da conversão mês a mês.

O volume de propostas caiu ao longo de 2025, especialmente após março. Em novembro de 2025, a taxa de contratação foi de 12,95%, seguida de recuperação para 21,53% em dezembro.

#### Perfil associado à contratação

O score de crédito apresentou uma associação positiva com a taxa de contratação.

| Faixa de score | Taxa de contratação |
|---|---:|
| Até 600 | 9,62% |
| 601–700 | 17,31% |
| 701–800 | 25,44% |
| Acima de 800 | 36,78% |

Clientes recorrentes também apresentaram maior taxa de contratação:

- Cliente recorrente: 23,06%.
- Não recorrente: 18,32%.

#### Oportunidades de recuperação

O status `Sem retorno` concentrou aproximadamente R$ 575,1 milhões em valor solicitado.

O canal Correspondente apresentou aproximadamente R$ 341 milhões em valor solicitado nas situações de `Sem retorno` e `Desistiu`.

As principais oportunidades identificadas foram:

- Recuperar propostas sem retorno.
- Investigar o desempenho do canal Correspondente.
- Melhorar o acompanhamento das propostas ao longo do funil.
- Utilizar indicadores de crédito para priorizar os esforços comerciais.

### Recomendações

1. **Recuperar propostas sem retorno:** criar uma rotina de acompanhamento e priorizar propostas com maior potencial de contratação.
2. **Investigar o canal Correspondente:** avaliar a qualidade das propostas e identificar as etapas com maior perda.
3. **Priorizar propostas:** utilizar score de crédito, LTV e valor solicitado como indicadores de apoio à análise.

### Cenários de impacto

Os cenários abaixo são estimativas operacionais, não previsões de receita.

- Recuperar aproximadamente 5% das propostas classificadas como `Sem retorno` representaria cerca de 82 propostas e R$ 28,8 milhões em valor solicitado potencialmente recuperado.
- Aumentar a taxa de contratação do canal Correspondente de 13,71% para 18% representaria cerca de 70 contratos adicionais e R$ 27,3 milhões em valor solicitado potencialmente convertido.

Esses cenários dependem de hipóteses e precisam ser validados antes de serem tratados como metas.

## Parte 2 — Automação do relatório semanal

Foi desenvolvida uma rotina em Python para automatizar o relatório semanal do funil.

Arquivo principal: `data/parte_2/relatorio_semanal.py`

O processo realiza:

1. Leitura da base original.
2. Validação das colunas obrigatórias.
3. Verificação de alterações no schema.
4. Remoção de imóveis do tipo Terreno.
5. Tratamento de valores monetários e datas.
6. Agrupamento semanal.
7. Cálculo da quantidade de propostas e contratos.
8. Cálculo da taxa de contratação.
9. Soma do valor solicitado.
10. Geração dos relatórios.

A rotina gera arquivos CSV, Excel, HTML e PDF, além de registrar informações de execução em log e tratar erros de processamento.

## Parte 3 — Extração dos laudos

Foi desenvolvido um script Python para estruturar as informações dos 17 laudos de avaliação imobiliária.

Arquivo principal: `data/parte_3/extrair_laudos.py`

Os campos extraídos incluem:

- Tipo do imóvel.
- Endereço.
- Áreas informadas.
- Ano de construção.
- Valor de avaliação.
- Matrícula.
- Ônus e restrições.
- Data de vistoria.
- Responsável técnico.
- Alertas de divergência.

O script utiliza regras de extração e ajustes específicos para os laudos conferidos. Os valores ausentes não são preenchidos por inferência.

### Tratamento de divergências

O laudo 17 apresenta uma divergência de área total: 95 m² no cabeçalho e 92 m² na tabela interna.

Os dois valores foram preservados no resultado para evitar uma escolha arbitrária.

Também foram identificadas situações que exigem atenção, como ano exato de construção não informado e ausência de matrícula no laudo 08.

### Resultado da execução

Na última execução, o script processou os 17 laudos e gerou:

- `outputs/laudos_extraidos.csv`
- `outputs/laudos_extraidos.xlsx`

O relatório identificou cinco laudos com alertas preenchidos. A ausência de alguns dados, como ano de construção ou matrícula, foi mantida quando não havia informação disponível.

A geração dos arquivos confirma que o processamento foi executado, mas não substitui a conferência dos resultados com os documentos originais.

## Tratamento dos dados

As principais decisões foram documentadas para manter a análise reproduzível.

A base original possuía 6.400 registros. Após a remoção dos 535 registros classificados como `Terreno`, foram utilizados 5.865 registros.

Como a coluna `ltv` não estava presente na base, foi calculada a partir de `valor_solicitado / valor_imovel`.

Campos ausentes e divergências foram preservados sempre que não havia informação suficiente para resolvê-los. O objetivo foi priorizar a rastreabilidade e evitar a criação de dados inexistentes. Afinal, até o abacaxi dos dados precisa ser tratado de forma reproduzível.

## Parte 4 — Diário de desenvolvimento

O arquivo `DIARIO.md` documenta:

- Utilização de Inteligência Artificial.
- Erros identificados durante o desenvolvimento.
- Correções realizadas.
- Conceitos aprendidos.
- Autocrítica sobre o desenvolvimento.

## Como executar

### Instalar as dependências

Com Python instalado, execute na pasta principal do projeto:

```bash
pip install pandas reportlab openpyxl
```

### Executar o relatório semanal

```bash
python data/parte_2/relatorio_semanal.py
```

### Executar a extração dos laudos

```bash
python data/parte_3/extrair_laudos.py
```

Os scripts devem ser executados a partir da pasta principal do projeto, para que os caminhos relativos funcionem corretamente.

## Considerações finais

O projeto reúne análise exploratória de dados, automação de relatórios e extração de informações de documentos.

As análises apontam oportunidades de melhoria no acompanhamento das propostas de crédito, enquanto as automações reduzem tarefas manuais e organizam informações para consulta.

O desenvolvimento também reforçou a importância de validar os resultados, documentar as decisões de tratamento e preservar as limitações dos dados disponíveis.