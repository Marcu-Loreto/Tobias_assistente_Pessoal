---
name: pesquisa_web
description: Realiza buscas aprofundadas na internet sobre um tema definido pelo usuário, compilando um resumo detalhado, estruturado e com fontes.
---

# Skill de Pesquisa Web Profunda

Esta skill deve ser ativada sempre que o usuário solicitar uma pesquisa, investigação ou dossiê aprofundado sobre um tema ou assunto específico utilizando a internet.

## Propósito
Sintetizar informações de múltiplas fontes da web em um relatório coeso, garantindo que a resposta final não seja apenas uma repetição dos resultados de busca, mas uma análise integrada com estrutura clara.

## Como Executar a Pesquisa (Agente)
1. **Ativação da Ferramenta de Busca:** Ao invocar esta skill, você DEVE utilizar a sua ferramenta `search_internet` (ou equivalente) para buscar informações sobre o tema solicitado.
2. **Consultas Múltiplas:** Faça mais de uma busca se necessário, cobrindo diferentes aspectos do tema (ex: "O que é [tema]", "[Tema] notícias recentes", "Críticas ou desafios de [tema]").
3. **Análise de Fatos:** Identifique padrões, dados mais citados e fatos de consenso entre as fontes retornadas.

## Estrutura Obrigatória da Resposta

Seu retorno ao usuário deve ser minuciosamente estruturado seguindo o modelo abaixo:

1. **Visão Geral (O que é? / O Contexto)**
   - Um resumo direto e factual (2-3 parágrafos) do que foi encontrado sobre o tema.
   
2. **Principais Descobertas e Fatos Recentes**
   - Use uma lista em _bullet points_ (marcadores) para destacar os eventos, atualizações ou definições mais importantes coletados da busca.
   
3. **Análise Crítica e Divergências (Opcional, se aplicável)**
   - Há visões conflitantes ou desafios mencionados nas pesquisas? Traga esse aspecto clínico.
   
4. **Resumo de Fontes (Citações)**
   - Ao final do texto, cite os subtítulos/títulos e veículos de onde tirou os excertos (conforme retornado pela sua *tool* de pesquisa).

## Tom e Estilo
- **Neutro, Analítico e Informativo.**
- Não limite a resposta a "aqui estão os resultados". Construa a narrativa por conta própria e aja como um assistente de pesquisa (assessor de informação).
- **Sem alucinações:** Só afirme o que as ferramentas de busca retornaram ou o que é de conhecimento absoluto (Certeza >= 90%).
