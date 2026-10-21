# Diário de Desenvolvimento — Bari AI & Data Lab

## 1. Uso de Inteligência Artificial

Utilizei Inteligência Artificial como ferramenta de apoio durante o desenvolvimento do desafio, principalmente para compreender a estrutura dos dados, revisar códigos Python, investigar erros e organizar a documentação.

A IA auxiliou em algumas etapas, mas revisei os resultados e executei as análises para verificar sua consistência com os dados disponíveis.

Na análise da base de propostas, utilizei Python e Pandas para tratar os dados, calcular o LTV quando a coluna não estava disponível, analisar o funil e comparar indicadores entre diferentes grupos.

Na automação do relatório semanal, desenvolvi um processo em Python para ler a base, validar colunas, tratar dados e gerar relatórios nos formatos CSV, Excel, HTML e PDF.

Na extração dos laudos, utilizei a IA como apoio para estruturar a solução. Percebi que uma abordagem baseada somente em expressões regulares não era suficiente para garantir a extração confiável de informações em documentos com formatos diferentes. Por isso, revisei a estratégia e comparei os resultados com a referência cadastrada, preservando campos ausentes e divergências identificadas.

## 2. Erro cometido pela IA e correção

Um dos principais problemas ocorreu durante a extração dos laudos. A abordagem inicial utilizava expressões regulares para identificar informações automaticamente, mas alguns campos não eram reconhecidos corretamente devido às diferenças de formato e escrita dos documentos.

Para corrigir o problema, revisei os dados extraídos e ajustei a estratégia de identificação dos campos. Também preservei uma divergência encontrada no laudo 17: o documento apresenta 95 m² no cabeçalho e 92 m² em uma tabela interna.

Em vez de escolher arbitrariamente um dos valores, registrei a divergência para permitir uma verificação posterior.

Essa experiência reforçou a importância de validar os resultados apoiados por IA e de não considerar uma saída automaticamente correta sem verificar sua consistência com a fonte original.

## 3. Conceito aprendido durante o desafio

Um dos conceitos que aprofundei foi o LTV (*Loan-to-Value*), indicador que relaciona o valor solicitado ao valor do imóvel utilizado como referência na proposta.

Como a base não possuía uma coluna de LTV, calculei o indicador pela fórmula:

**LTV = valor_solicitado / valor_imovel**

Dediquei aproximadamente duas horas ao estudo e à aplicação prática desse conceito, utilizando a base disponibilizada no desafio e consultando recursos de documentação do Python e do Pandas para implementar os cálculos e analisar os resultados.

Com esse cálculo, comparei propostas com LTV de até 60% com aquelas acima desse limite e identifiquei diferenças nas respectivas taxas de contratação.

Também compreendi melhor a importância de diferenciar o volume de propostas do valor financeiro envolvido. Uma etapa pode concentrar muitas propostas sem necessariamente representar a maior perda financeira.

## 4. Autocrítica e próximos passos

Considero que meu principal ponto de evolução foi transformar análises exploratórias em processos mais estruturados e reproduzíveis.

No início, minha atenção estava concentrada em encontrar resultados. Ao longo do desenvolvimento, percebi a importância de documentar a origem das informações, explicar os tratamentos realizados e reconhecer as limitações dos dados.

Se tivesse mais 40 horas para trabalhar no desafio, priorizaria três melhorias:

- **Análise de dados:** aprofundaria a validação estatística das diferenças de conversão e testaria a estabilidade das recomendações em diferentes cenários.
- **Automação:** implementaria testes automatizados para detectar alterações no formato da base, valores inválidos e falhas na geração dos relatórios.
- **Extração dos laudos:** realizaria uma conferência independente de todos os campos com os 17 documentos originais e ampliaria os testes para medir a precisão da extração.

Como ponto positivo, destaco minha preocupação com a rastreabilidade e a explicabilidade dos resultados. Ao encontrar informações ausentes ou contraditórias, procurei sinalizar as limitações em vez de assumir valores sem respaldo.

**Pergunta que faria à equipe de negócio:** quais etapas do funil e quais indicadores financeiros são prioritários para a Bari na identificação de oportunidades de melhoria, e como o impacto de uma recomendação deve ser medido na prática?

O desafio me ajudou a compreender que um bom resultado técnico não depende apenas de produzir uma análise ou automatizar uma tarefa, mas também de explicar o processo, validar as informações e reconhecer quando os dados não permitem chegar a uma conclusão segura.