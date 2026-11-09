# CardioIA Fase 7 — Backend integrador

## Objetivo

Entregar uma API FastAPI implantável que conecte o ESP32/Wokwi, o motor de
risco da Fase 6, o chat Watson/OpenAI e as interfaces Web e Mobile existentes.

## Decisão

O núcleo da Fase 6 será copiado para `FASE7-CARDIOIA/backend/cardioia`, junto
ao artefato do modelo. Essa opção torna o deploy independente da árvore da
Fase 6 e evita reimplementar a lógica preditiva validada.

## Arquitetura

- `app/`: FastAPI, rotas, autenticação JWT, SQLite, schemas e dependências.
- `cardioia/`: módulos reutilizados da Fase 6 e o pipeline de avaliação.
- `models/`: artefato e metadados do Random Forest.
- SQLite armazena usuários demo, pacientes, leituras e avaliações.
- O firmware envia telemetria autenticada; a API persiste, reavalia o risco
  diante de limiares críticos e expõe o estado ao polling das interfaces.

## Contratos e resiliência

O contrato em `FASE7-CARDIOIA/document/contrato_api.md` é a fonte de verdade.
O chat normaliza os campos e a origem para o formato já esperado pelos dois
clientes. Avaliações executam sem LLM quando não houver chave ou em caso de
falha do provedor, preservando uma recomendação determinística segura.

## Validação

Testes cobrirão autenticação, autorização por perfil, ingestão do dispositivo,
status do paciente, avaliação e chat sem serviços externos. A integração final
validará Wokwi → API → Vercel/APK e o deploy no Render receberá somente
segredos por variáveis de ambiente.
