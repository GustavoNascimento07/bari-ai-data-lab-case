# Resumo Executivo — Bari AI & Data Lab

## Objetivo

Analisar o funil de propostas de crédito imobiliário para identificar perdas de conversão, fatores associados à contratação e oportunidades de melhoria operacional.

A base inicial continha 6.400 propostas. Após a remoção de 535 registros classificados como `Terreno`, foram analisadas 5.865 propostas.

## Principais achados

**1. LTV acima de 60% está associado a menor conversão**

Como a base não possuía a coluna LTV, o indicador foi calculado pela fórmula `valor_solicitado / valor_imovel`. A conversão foi de 20,54% para LTV de até 60% e de 12,06% para LTV acima de 60%, uma diferença de 8,48 pontos percentuais.

**2. O canal Correspondente apresenta oportunidade de melhoria**

O canal registrou 1.627 propostas, 223 contratos e conversão de 13,71%, abaixo dos demais canais, cujas taxas variaram de 20,03% a 22,83%. O perfil de score nesse canal merece investigação, sem estabelecer causalidade.

**3. Score e recorrência estão associados à contratação**

A conversão cresceu conforme a faixa de score: 9,62% até 600; 17,31% entre 601 e 700; 25,44% entre 701 e 800; e 36,78% acima de 800. Clientes recorrentes também apresentaram maior conversão: 23,06%, contra 18,32% dos não recorrentes.

**4. Propostas sem retorno concentram alto valor solicitado**

O status `Sem retorno` concentrou aproximadamente R$ 575,1 milhões em valor solicitado, seguido de `Desistiu`, com R$ 550,6 milhões. No canal Correspondente, esses dois status somaram aproximadamente R$ 341 milhões, indicando uma oportunidade de investigar ações de recuperação.

## Recomendações

- **Recuperação:** priorizar propostas sem retorno considerando valor solicitado, score e LTV.
- **Canal Correspondente:** mapear as etapas com maior perda e investigar diferenças de perfil e desempenho.
- **Priorização:** combinar indicadores de risco e potencial para apoiar as equipes comerciais e de crédito.

## Cenários de impacto

- **Recuperação de propostas sem retorno:** recuperar 5% desse grupo corresponderia a aproximadamente 75 propostas e R$ 28,76 milhões em valor solicitado potencialmente recuperado.
- **Melhoria do canal Correspondente:** elevar a conversão de 13,71% para 18% representaria um cenário estimado de aproximadamente 70 contratos adicionais e R$ 27,24 milhões em valor solicitado associado a essas conversões.

Esses cenários são estimativas hipotéticas, não previsões de receita. Dependem das premissas adotadas e da efetividade das ações. O valor solicitado não equivale necessariamente ao valor efetivamente contratado ou à receita gerada.

## Automação e dados

Foi desenvolvida uma rotina em Python para gerar relatórios semanais em CSV, Excel, HTML e PDF, com validação de colunas, tratamento de dados e logs. Também foram estruturados 17 laudos imobiliários em formato tabular, preservando informações ausentes e divergências identificadas.

## Limitações

A análise utiliza exclusivamente os dados fornecidos. A conversão apresentou oscilações ao longo do período, sem evidência de queda contínua. As associações observadas não comprovam causalidade, os cenários não representam previsão de receita e as informações ausentes nos laudos não foram inferidas. A validação automatizada dos laudos representa correspondência com a referência cadastrada, devendo ser complementada pela conferência independente dos documentos originais.