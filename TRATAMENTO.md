# Tratamento dos Dados — Bari AI & Data Lab

## 1. Base original

A base recebida contém 6.400 propostas e 19 colunas.

## 2. Remoção de imóveis

Conforme a orientação do desafio, foram removidos os registros com `tipo_imovel = "Terreno"`.

- Registros removidos: 535.
- Base final para análise: 5.865 propostas.

## 3. Cálculo do LTV

A base não possuía uma coluna `ltv`, embora esse campo estivesse previsto no dicionário de dados.

Por isso, foi criado o campo `ltv_calculado`, utilizando a fórmula:

`ltv_calculado = valor_solicitado / valor_imovel`

O limite de 60% informado no desafio foi utilizado para classificar as propostas em dois grupos: LTV de até 60% e LTV acima de 60%.

## 4. Tratamento dos valores monetários

A coluna `valor_imovel` estava armazenada como texto. Os caracteres de representação monetária foram removidos e o campo foi convertido para formato numérico, permitindo sua utilização nos cálculos e nas análises.

A coluna `valor_solicitado` também foi utilizada nos cálculos financeiros, respeitando o formato dos valores presentes na base.

## 5. Tratamento das datas

A coluna `data_entrada` apresentava diferentes formatos de data. Os valores foram convertidos com `pd.to_datetime`, utilizando suporte a formatos mistos para possibilitar a análise temporal das propostas.

Registros com datas inválidas ou ausentes devem ser identificados e tratados de forma explícita, evitando que informações inconsistentes comprometam os agrupamentos semanais ou mensais.

## 6. Valores ausentes

Foram identificados valores ausentes, principalmente nas colunas `data_assinatura_contrato` e `taxa_juros_aa`.

Esses valores foram preservados, pois podem estar relacionados à situação das propostas, especialmente àquelas que não chegaram à contratação. Não foram atribuídos valores artificialmente.

## 7. Verificação de duplicidades

Foi realizada uma verificação de duplicidades com base no campo `id_proposta` e em linhas completamente duplicadas.

Os registros duplicados devem ser contabilizados e investigados antes de qualquer exclusão automática, para evitar a remoção indevida de informações válidas.

## 8. Reprodutibilidade e rastreabilidade

As transformações foram implementadas em código Python para permitir a reprodução do tratamento sempre que a análise for executada novamente.

As decisões de tratamento foram documentadas para facilitar a rastreabilidade dos resultados, a compreensão das etapas de preparação e a identificação de possíveis limitações da base.