# Relatório de Governança e Riscos — Genera Intelligence

**Versão:** 1.0  
**Data:** 2026-05-28  
**Responsável:** Arthur Guimarães Alentejo  
**Sprint:** 2 — Motor RAG & Agentes Especialistas

---

## 1. Escopo e Limites do Agente

### 1.1 O que o agente PODE fazer

| Capacidade | Descrição |
|-----------|-----------|
| Interpretar marcadores genéticos | Traduzir SNPs, alelos e genótipos para linguagem acessível |
| Explicar predisposições | Contextualizar riscos estatísticos de forma equilibrada |
| Recomendar acompanhamento | Direcionar o paciente ao profissional de saúde adequado |
| Citar fontes do laudo | Indicar quais painéis e marcadores embasaram a resposta |
| Responder sobre painéis específicos | Nutri, Farma, Fit, Skin e Escala de Risco |

### 1.2 O que o agente NÃO PODE fazer

| Restrição | Justificativa |
|-----------|---------------|
| Emitir diagnósticos médicos | Exercício ilegal da medicina (Lei 12.842/2013) |
| Prescrever medicamentos ou dosagens | Ato privativo de médico |
| Sugerir interrupção de tratamentos | Risco à saúde do paciente |
| Responder sobre temas fora do escopo genético | Manutenção da confiabilidade |
| Armazenar ou repetir dados pessoais (PII) | Conformidade LGPD |
| Fazer prognósticos determinísticos | Genética indica predisposição, não certeza |

---

## 2. Disclaimers Obrigatórios

### 2.1 Disclaimer padrão (inserido em toda resposta)

> ⚠️ **Importante:** Este assistente é puramente informativo e não substitui uma consulta médica. Os dados genéticos indicam predisposições, não certezas. Recomendamos fortemente que você consulte um médico geneticista ou especialista clínico para correlacionar esses achados com seu histórico pessoal e familiar.

### 2.2 Disclaimer para Escala de Risco Genético

> ⚠️ **Nota sobre Risco Poligênico:** Os percentuais apresentados representam uma estimativa estatística baseada em estudos populacionais. Fatores ambientais, estilo de vida e histórico familiar são igualmente determinantes. Um risco "aumentado" não significa que a condição se manifestará.

### 2.3 Implementação técnica

O disclaimer é garantido por duas camadas:
1. **System Prompt** — instrui o LLM a incluir o disclaimer
2. **Guardrail pós-geração** — verifica presença e adiciona automaticamente se ausente

---

## 3. Política de Privacidade de Dados Genéticos

### 3.1 Classificação dos dados

| Tipo de dado | Classificação LGPD | Tratamento |
|-------------|-------------------|------------|
| Dados genéticos (SNPs, genótipos) | Dado pessoal sensível (Art. 5, II) | Processado apenas em memória, não persistido em logs |
| Nome do paciente | Dado pessoal | Removido via PII Redaction antes do LLM |
| CPF, RG, telefone | Dado pessoal | Removido via PII Redaction |
| Perguntas do usuário | Dado pessoal | Não armazenadas em banco de dados |

### 3.2 Fluxo de dados e proteção

```
[Input do Usuário] → [PII Redaction] → [RAG Pipeline] → [LLM Externo] → [Guardrails] → [Resposta]
                          ↑                                                      ↑
                    Remove PII antes                                    Verifica se PII
                    de enviar ao LLM                                    vazou na resposta
```

### 3.3 Princípios aplicados

- **Minimização:** Apenas dados estritamente necessários são enviados ao modelo
- **Finalidade:** Dados usados exclusivamente para interpretação do laudo
- **Não-retenção:** Nenhum histórico de conversa é persistido no servidor
- **Anonimização:** PII é removido antes do processamento pelo LLM externo

---

## 4. Riscos Identificados e Mitigações

### 4.1 Matriz de Riscos

| # | Risco | Severidade | Probabilidade | Mitigação |
|---|-------|-----------|---------------|-----------|
| R1 | Alucinação do LLM (informação inventada) | 🔴 Alta | Média | RAG com grounding exclusivo no laudo; guardrail verifica fontes |
| R2 | Resposta com tom alarmista | 🟡 Média | Média | Prompt engineering + verificação de termos alarmistas |
| R3 | Emissão acidental de diagnóstico | 🔴 Alta | Baixa | Lista de termos proibidos + bloqueio automático |
| R4 | Vazamento de PII na resposta | 🔴 Alta | Baixa | PII Redaction no input + verificação regex no output |
| R5 | Prescrição indevida de medicamentos | 🔴 Alta | Baixa | Termos de prescrição bloqueados + prompt restritivo |
| R6 | Viés do modelo em populações sub-representadas | 🟡 Média | Média | Documentação clara sobre populações de estudo nos metadados |
| R7 | Dados do laudo incompletos ou incorretos | 🟡 Média | Baixa | Agente informa quando dado não consta; não extrapola |
| R8 | Indisponibilidade da API do LLM | 🟢 Baixa | Baixa | Tratamento de erro com mensagem amigável ao usuário |

### 4.2 Detalhamento das mitigações técnicas

**R1 — Alucinação:**
- O system prompt instrui: "Baseie-se EXCLUSIVAMENTE no contexto fornecido"
- O RAG limita o contexto a documentos recuperados do banco vetorial
- A resposta inclui as fontes (painel, gene, marcador) para rastreabilidade

**R2 — Tom alarmista:**
- Prompt proíbe termos como "grave", "perigoso", "fatal"
- Guardrail pós-geração detecta linguagem catastrofista
- Prompts especializados por painel reforçam tom equilibrado

**R3 e R5 — Diagnóstico e prescrição:**
- Listas de termos proibidos verificadas automaticamente
- Se detectado, resposta é substituída por mensagem segura padrão
- Log de violações para auditoria

**R4 — Vazamento de PII:**
- Módulo `pii_redaction.py` sanitiza input antes do pipeline
- Guardrail verifica padrões de CPF, e-mail, telefone na resposta
- Se detectado, resposta é bloqueada

---

## 5. Guardrails Implementados

### 5.1 Arquitetura de segurança em camadas

```
Camada 1: PII Redaction (pré-processamento)
    ↓
Camada 2: System Prompt restritivo (instrução ao LLM)
    ↓
Camada 3: Prompt especializado por painel (refinamento)
    ↓
Camada 4: Guardrail pós-geração (validação da resposta)
    ↓
Camada 5: Disclaimer automático (garantia final)
```

### 5.2 Categorias de verificação

| Categoria | Ação se violado |
|-----------|----------------|
| Diagnóstico médico | 🚫 Bloqueia resposta |
| Prescrição de medicamentos | 🚫 Bloqueia resposta |
| PII na resposta | 🚫 Bloqueia resposta |
| Tom alarmista | ⚠️ Log de alerta (não bloqueia) |
| Disclaimer ausente | 📎 Adiciona automaticamente |

---

## 6. Conformidade Regulatória

| Regulação | Aplicabilidade | Status |
|-----------|---------------|--------|
| LGPD (Lei 13.709/2018) | Dados pessoais sensíveis (genéticos) | ✅ PII Redaction implementado |
| CFM Resolução 2.314/2022 | Telemedicina e IA em saúde | ✅ Agente não emite diagnósticos |
| Lei 12.842/2013 (Ato Médico) | Diagnóstico como ato privativo | ✅ Guardrails impedem diagnóstico |
| Marco Civil da Internet | Responsabilidade por conteúdo | ✅ Disclaimers obrigatórios |

---

## 7. Plano de Monitoramento

| Métrica | Frequência | Responsável |
|---------|-----------|-------------|
| Taxa de bloqueio por guardrails | Por deploy | Equipe de IA |
| Eval de qualidade de respostas | Semanal | Arthur |
| Revisão de prompts | A cada sprint | Arthur |
| Auditoria de logs de violação | Mensal | Equipe |

---

## 8. Histórico de Revisões

| Data | Versão | Alteração |
|------|--------|-----------|
| 2026-05-28 | 1.0 | Documento inicial — Sprint 2 |
