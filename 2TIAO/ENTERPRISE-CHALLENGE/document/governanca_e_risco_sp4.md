# Relatório de Política e Governança de IA — Genera Intelligence

**Versão:** 2.0  
**Data:** 2026-10-05 (atualização Sprint 4 sobre a base da Sprint 3)  
**Responsável:** Nathalia Vasconcelos (v2.0) · Michael Rodrigues (v1.1) · Arthur Guimarães Alentejo (v1.0)  
**Sprint:** 4 — Produção e Governança

---

## 1. Escopo e Limites do Agente

A governança de modelos representa o conjunto abrangente e estruturado de políticas, processos, controles tecnológicos e estruturas organizacionais que asseguram o desenvolvimento, a validação, a implantação, o monitoramento e a manutenção responsável dos modelos de Inteligência Artificial ao longo de todo seu ciclo de vida operacional.

### 1.1 O que o agente PODE fazer
*   **Interpretar marcadores genéticos:** Traduzir SNPs, alelos e genótipos para linguagem acessível.
*   **Explicar predisposições:** Contextualizar riscos estatísticos de forma equilibrada.
*   **Recomendar acompanhamento:** Direcionar o paciente ao profissional de saúde adequado.
*   **Citar fontes do laudo:** Indicar quais painéis e marcadores embasaram a resposta.

### 1.2 O que o agente NÃO PODE fazer
*   **Emitir diagnósticos médicos:** Exercício ilegal da medicina (Lei 12.842/2013).
*   **Prescrever medicamentos ou dosagens:** Ato privativo de médico.
*   **Sugerir interrupção de tratamentos:** Risco à saúde do paciente.
*   **Responder sobre temas fora do escopo genético:** Manutenção da confiabilidade e foco do agente.
*   **Fazer prognósticos determinísticos:** Genética indica predisposição, não certeza.

---

## 2. Disclaimers Obrigatórios e Prevenção de Alucinações

A produção de respostas factualmente incorretas ou inventadas por sistemas de IA Generativa (alucinação algorítmica) é mitigada através do *grounding* estrito no laudo do paciente. Toda resposta exige os seguintes disclaimers:

### 2.1 Disclaimer padrão (inserido em toda resposta)
> ⚠️ **Importante:** Este assistente é puramente informativo e não substitui uma consulta médica. Os dados genéticos indicam predisposições, não certezas. Recomendamos fortemente que você consulte um médico geneticista ou especialista clínico.

### 2.2 Disclaimer para Escala de Risco Genético
> ⚠️ **Nota sobre Risco Poligênico:** Os percentuais apresentados representam uma estimativa estatística. Fatores ambientais e estilo de vida são determinantes. Um risco "aumentado" não significa que a condição se manifestará.

---

## 3. Política de Privacidade e Conformidade LGPD (*Compliance by Design*)

O conceito de *Compliance by Design* representa a integração proativa de requisitos de conformidade em processos de design e desenvolvimento, abordando desafios como a transparência algorítmica e requisitos de monitoramento contínuo.

### 3.1 Tratamento e Retenção de Dados Sensíveis
*   **Base Legal e Finalidade:** Os dados genéticos (considerados dados pessoais sensíveis pela LGPD, Art. 5, II) são processados estritamente para a interpretação do laudo e viabilização da interface de histórico.
*   **Minimização de Dados:** O sistema coleta e processa apenas os dados clínicos e características necessárias para a predição e interação. Uma regra de retenção automatizada purga interações mais antigas que 30 dias do banco SQLite, assegurando que os dados não sejam mantidos além do necessário.
*   **Sanitização (PII Redaction):** O fluxo aplica anonimização automatizada nos *pipelines* (remoção de CPF, nome, e-mail, telefone) antes do envio ao LLM externo e antes da persistência no banco de dados.

### 3.2 Direito de Exclusão (Direito ao Esquecimento)
Para garantir total aderência à LGPD, o sistema disponibiliza o endpoint `DELETE /api/historico/{paciente_id}`. Isso permite aos pacientes exercerem seus direitos de exclusão, removendo imediatamente todo o histórico de interações do banco de dados local.

---

## 4. Transparência e Explicabilidade

O princípio da transparência e explicabilidade exige que os sistemas de IA sejam compreensíveis em suas operações e decisões, mitigando a opacidade característica de modelos generativos complexos. Transparência algorítmica refere-se à capacidade de compreender e explicar como modelos de IA chegam a suas decisões.

Para garantir essa explicabilidade para *stakeholders* humanos, a API do Genera Intelligence retorna em cada interação:
1.  **O Painel Utilizado:** Identificação de qual *system prompt* especialista guiou a resposta (ex: Genera Nutri, Skin, Farma).
2.  **Fontes e Marcadores:** As referências exatas do documento (gene, marcador e conclusão técnica) que embasaram a geração do texto.
3.  **Guardrails Acionados:** Visibilidade sobre quais regras de segurança atuaram sobre a resposta.

---

## 5. Logging Estruturado e Rastreabilidade

A rastreabilidade e a reprodutibilidade constituem pilares fundamentais sobre os quais se constrói qualquer sistema confiável de governança de modelos de IA. A responsabilização tecnológica consiste na implementação de sistemas que garantam transparência nas operações algorítmicas e possibilitem o rastreamento das decisões até suas origens.

*   **Trilhas de Auditoria (Audit Trails):** O sistema implementa logs em formato JSON em cada nó do pipeline LangGraph (`sanitize`, `retrieve`, `generate`, `guardrail`).
*   **Rastreamento Único:** Toda requisição recebe um `request_id` (UUID), permitindo a correlação de ponta a ponta sem expor o conteúdo sensível da conversa nos logs.
*   **Métricas de Execução:** O tempo de latência de cada etapa, o número de documentos recuperados e as violações de segurança são registrados em um *ledger* de auditoria invisível ao usuário final, promovendo o monitoramento proativo.

---

## 6. Monitoramento Contínuo e Métricas

A governança precisa incluir rotinas estruturadas de monitoramento e revalidação periódica dos modelos, contendo indicadores de desempenho atualizados, auditorias automatizadas e alarmes de performance. O monitoramento contínuo de conformidade habilita a detecção em tempo real de violações e desvios de objetivos de segurança.

*   **Endpoint de Observabilidade:** A rota `GET /metrics` consolida o volume total de requisições, latência média da API e a taxa percentual de bloqueios de guardrails.
*   **Avaliação Qualitativa (LLM-as-a-Judge):** Execução periódica de um pipeline de testes abrangendo categorias de alarmismo, diagnóstico, jargões e escopo, validando se o comportamento do agente atende aos critérios éticos e não sofre de *model drift* (degradação da performance ou aderência).

---

## 7. Papel Humano e Supervisão Ética (*Human-in-the-Loop*)

Sem liderança ativa e consciente, a governança tende a se tornar um conjunto de documentos desconectados da prática real. A supervisão humana é essencial para equilibrar o uso da tecnologia. A interface alerta explicitamente que o diagnóstico do agente é uma análise preliminar, reforçando que a avaliação de especialistas da saúde não deve ser substituída. 

---

## 8. Matriz de Riscos e Status (Sprint 4)

| # | Risco | Severidade | Mitigação Atualizada | Status |
|---|-------|-----------|----------------------|--------|
| R1 | Alucinação do LLM | 🔴 Alta | RAG com *grounding* + Exibição de Fontes na API | Controlado |
| R2 | Resposta com tom alarmista | 🟡 Média | LLM-as-a-Judge contínuo avaliando o tom gerado | Controlado |
| R3 | Emissão de diagnóstico | 🔴 Alta | Lista de bloqueio automático (*circuit breaker*) | Controlado |
| R4 | Vazamento de PII | 🔴 Alta | Nó `sanitize` isolado + Logs sem *payload* sensível | Controlado |
| R9 | Retenção prolongada de dados | 🟡 Média | **[RESOLVIDO]** Endpoint de deleção explícita (LGPD Art. 18, VI) e purga automatizada (30 dias) implementados. | Resolvido |

---

## 9. Histórico de Revisões

| Data | Versão | Responsável | Alteração |
|------|--------|-------------|-----------|
| 2026-05-28 | 1.0 | Arthur G. | Documento inicial — Sprint 2 |
| 2026-08-18 | 1.1 | Michael R. | Documentação do histórico e disclaimers |
| 2026-10-05 | 2.0 | Nathalia V. | Sprint 4: Inclusão da política formal (*Compliance by Design*), logging estruturado, endpoint LGPD de exclusão, explicabilidade algorítmica e métricas de monitoramento. |