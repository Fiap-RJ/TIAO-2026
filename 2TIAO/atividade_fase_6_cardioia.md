# Introdução

# ATIVIDADE – FASE 6: Coração Sob Controle

## Contribuições da atividade para o desenvolvimento do projeto

Estamos chegando na reta final da evolução da CardioIA, e após consolidarmos a etapa de interação conversacional, a Fase 6 marca uma mudança estratégica no projeto: passamos da comunicação inteligente para a inteligência preditiva orientada a risco.

Nesta etapa, o sistema deixa de atuar apenas de forma reativa e passa a operar de maneira analítica, identificando padrões em dados clínicos simulados e transformando essas informações em suporte estruturado à decisão.

A proposta desta fase é explorar como modelos de Machine Learning podem ser integrados a arquiteturas baseadas em agentes especializados, permitindo que diferentes componentes do sistema colaborem entre si para interpretar cenários e organizar respostas estratégicas. Mais do que prever um evento isolado, buscamos compreender como probabilidades, protocolos e regras operacionais podem ser articulados dentro de uma lógica sistêmica, uma verdadeira orquestração de agentes.

Assim, o desafio consiste em desenvolver um Sistema Preditivo Multiagente para Eventos Cardíacos, utilizando exclusivamente técnicas, arquiteturas e exemplos trabalhados nas disciplinas desta fase ou de fases anteriores, respeitando o material apresentado nas disciplinas.

## Objetivo geral desta atividade

- Treinar um modelo de Machine Learning para prever picos de risco cardíaco, utilizando a base sintética apresentada em aula, aplicando as etapas de preparação de dados, separação entre treino e teste e validação conforme demonstrado nos exemplos nas disciplinas.
- Integrar esse modelo a uma arquitetura multiagente, estruturando o fluxo de chamada do modelo dentro de um agente específico e garantindo que o resultado da predição possa ser compartilhado entre os demais agentes do sistema.
- Utilizar agentes especializados para analisar o risco previsto e cruzar esse resultado com a base de protocolos simulada, organizando as informações de forma lógica e coerente, conforme a arquitetura vista em sala.
- Gerar uma recomendação final estruturada com base na colaboração entre agentes, apresentando de forma clara a probabilidade calculada, a classificação de risco e os protocolos sugeridos, demonstrando o funcionamento completo do pipeline multiagente.
- Trabalho em equipe e colaboração interdisciplinar – recomendamos o desenvolvimento do projeto em grupo de 4 a 5 integrantes, estimulando habilidades de comunicação, cooperação e divisão equilibrada de tarefas. O trabalho em equipe é considerado uma soft skill essencial para o ambiente profissional e acadêmico, e será concedido 1 ponto extra para as equipes que se organizarem dentro dessa estrutura recomendada
- Ao final desta fase, a equipe terá desenvolvido uma solução prática que demonstra como agentes conversacionais podem ser aplicados em contextos de saúde digital, respeitando boas práticas técnicas e conceituais.

## Atividade detalhada: Obrigatório

### PARTE 1 – MODELO PREDITIVO DE PICO DE RISCO

Para viabilizar o desenvolvimento sem restrições de privacidade ou acesso a dados sensíveis, serão fornecidos a seguir os códigos para geração de bases de dados sintéticas realistas, prática amplamente utilizada quando dados reais são escassos ou sensíveis, permitindo treinar modelos preservando privacidade e reduzindo custos de coleta:

#### Base de dados de treinamento de modelo preditivo para predição de risco do paciente (`risk_score`)

```python
import numpy as np
import pandas as pd
 
np.random.seed(42)
n = 5000
 
df = pd.DataFrame({
    "idade_media": np.random.normal(55, 12, n).clip(18, 90),
    "carga_sistema": np.random.uniform(30, 100, n),
    "tempo_espera": np.random.normal(45, 20, n).clip(5, 180),
    "fc_media": np.random.normal(85, 15, n).clip(50, 150),
    "spo2_media": np.random.normal(95, 3, n).clip(70, 100),
    "pa_sistolica": np.random.normal(125, 20, n).clip(80, 200),
    "temperatura": np.random.normal(24, 5, n).clip(10, 40),
    "densidade_eventos": np.random.poisson(3, n),
    "eventos_24h": np.random.poisson(2, n),
    "disponibilidade_recursos": np.random.uniform(20, 100, n)
})
 
risk_score = (
    (df["carga_sistema"] > 80).astype(int) +
    (df["tempo_espera"] > 60).astype(int) +
    (df["spo2_media"] < 92).astype(int) +
    (df["fc_media"] > 110).astype(int) +
    (df["eventos_24h"] > 4).astype(int) +
    (df["disponibilidade_recursos"] < 40).astype(int)
)
 
df["pico_risco"] = (risk_score >= 2).astype(int) 
```

#### Base de conhecimento contendo protocolos médicos

```python
protocolos = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência"
]
```

#### Utilização das bases simuladas

- Treinamento do modelo preditivo;
- Validação do Sistema (métricas de assertividade);
- Integração com o pipeline Multiagente: com base nos dados de um novo paciente, o sistema deverá chamar o agente de ML que dará um score de risco para o paciente usando o modelo de ML. Em seguida, com esse resultado e os protocolos, um segundo agente deverá dar a resposta final.

#### Simulação de um novo paciente

```python
novo_caso = pd.DataFrame([{
    "idade_media": 62,
    "carga_sistema": 92,
    "tempo_espera": 75,
    "fc_media": 118,
    "spo2_media": 89,
    "pa_sistolica": 100,
    "temperatura": 37.5,
    "densidade_eventos": 7,
    "eventos_24h": 5,
    "disponibilidade recursos": 25
}])
```

#### Exemplo de resposta esperada

RISCO PREVISTO: 0.91

PROTOCOLOS SUGERIDOS:

  - Se carga do sistema > 85% → abrir unidades temporárias

  - Se SPO2 < 88% → iniciar suporte respiratório imediato

  - Se disponibilidade_recursos < 30% → redistribuir insumos

#### Diretrizes técnicas de entrega

- Base de dados: gerar ou utilizar a base de dados simulada para o treinamento.
- Treinamento: treinar um modelo supervisionado de classificação para prever a variável pico_risco.
- Avaliação: avaliar o desempenho com métricas vistas em aula (por exemplo, acurácia e matriz de confusão).
- Modelo salvo: salvar o modelo treinado para a posterior integração no sistema multiagente.

### PARTE 2 – SISTEMA MULTIAGENTE (OPENAI AGENTS SDK)

Nesta parte, o grupo deve construir o sistema multiagente que usa o modelo treinado.

A entrega deverá seguir as seguintes diretrizes técnicas:

- Agentes especializados: implementar, no mínimo, um Agente Analista de Risco (consulta o modelo preditivo e gera o score), um Agente Especialista em Protocolos (consulta a base de protocolos simulados), um Agente Planejador de Resposta (consolida as informações e sugere ações operacionais) e um Agente Orquestrador (coordena o fluxo entre os agentes com handoffs).
- Fluxo do sistema: receber os dados de um novo paciente, acionar o agente de risco, encaminhar o resultado ao agente de protocolos e gerar uma resposta final estruturada com a probabilidade prevista, a classificação de risco e os protocolos sugeridos.
- Recursos: usar handoffs entre agentes, tools, histórico de mensagens e validação de saída.

## ENTREGÁVEIS

Para a entrega da atividade no Portal do Aluno, o grupo deverá enviar apenas um arquivo .txt, contendo o link do repositório GitHub privado onde todos os arquivos da atividade estão organizados, e o link do vídeo demonstrativo da solução.

Todos os arquivos desenvolvidos nesta etapa deverão estar organizados no repositório GitHub do grupo, seguindo o modelo oficial disponibilizado pela coordenação.

Repositório modelo da coordenação:
[Repositório modelo da coordenação](https://github.com/CaiqueFiap-2026/TEMPLATE-TIAO-2026/tree/main)

O vídeo demonstrativo deverá ter até 4 minutos, apresentar o funcionamento completo da solução e poderá ser feito com gravação de tela, explicação por voz ou legenda. O vídeo deverá ser publicado no YouTube como “não listado”, ou seja, acessível apenas por meio do link. O link do vídeo deverá ser incluído no arquivo .txt enviado no Portal do Aluno e também no README.md do repositório GitHub.

O GitHub deve ser privado e compartilhado apenas com o perfil: fiap-tutoria

### Dica para adicionar colaboradores no GitHub

- No topo do menu superior do repositório no GitHub, clique em “Settings”;
- No menu lateral esquerdo, clique em “Collaborators” ou em “Manage Access”, dependendo da visualização do GitHub;
- Clique no botão “Invite a collaborator”;
- Digite o nome de usuário ou e-mail da pessoa que deseja adicionar;
- Quando aparecer o perfil correto, clique em “Add”;
- A pessoa receberá um convite e precisará aceitar para ter acesso.
- Além disso, o convite deve ser aceito em até 7 dias. O convite deve ser enviado apenas ao tutor ou tutora da respectiva turma e aos integrantes do grupo.

### Conteúdo obrigatório do repositório

- Notebook no Google Colab com a geração da base, o treinamento do modelo, a avaliação com métricas e uma simulação de previsão para um novo paciente (com dados clínicos simulados, como idade, frequência cardíaca e SPO2).
- Relatório técnico (máximo duas páginas) com as decisões do modelo: justificativa do algoritmo, interpretação das métricas, análise da matriz de confusão e reflexão sobre limitações e melhorias.
- Código completo do sistema multiagente (agentes, orquestrador e integração com o modelo).
- Documento PDF (máximo três páginas) com o diagrama da arquitetura multiagente, o papel de cada agente, o uso de handoffs e tools, e um exemplo real de entrada e saída.
- README.md com as instruções de execução, as dependências, a estrutura do projeto, a identificação dos integrantes com RM e o link do vídeo demonstrativo.

## Critérios de Avaliação (10 pontos totais)

| Item | Critério | Peso | Parâmetro |
|---:|---|---:|---|
| 1 | **Entrega, Repositório e Prazo** | 1,0 | Repositório GitHub privado, acessível e organizado conforme o modelo da coordenação. O link do repositório deve ser entregue em um único arquivo TXT, dentro do prazo e sem alterações posteriores à entrega. |
| 2 | **Documentação Clara** | 1,0 | README.md claro e organizado, apresentando o objetivo do sistema preditivo, a base de dados utilizada, o funcionamento do modelo, a arquitetura multiagente, as instruções de execução, as dependências, a identificação dos integrantes e o link do vídeo demonstrativo. |
| 3 | **Organização, Legibilidade e Boas Práticas de Código** | 1,0 | Código comentado nos trechos relevantes, legível e bem estruturado, com nomenclatura coerente, separação adequada dos componentes e aplicação de boas práticas de desenvolvimento. |
| 4 | **Vídeo Demonstrativo** | 1,0 | Vídeo publicado no YouTube como “não listado”, com duração de até 4 minutos e demonstração clara do modelo preditivo, do sistema multiagente e do resultado final. O link deve constar no arquivo TXT e no README.md. |
| 5 | **Treinamento do Modelo Preditivo** | 2,0 | Modelo supervisionado treinado corretamente para prever a variável pico_risco, utilizando base simulada, preparação dos dados, separação entre treino e teste e salvamento do modelo para integração. |
| 6 | **Avaliação do Modelo** | 1,5 | Avaliação realizada com métricas adequadas, como acurácia e matriz de confusão, acompanhada da interpretação dos resultados, das limitações e das possibilidades de melhoria. |
| 7 | **Implementação da Arquitetura Multiagente** | 1,5 | Sistema implementado com, no mínimo, Agente Analista de Risco, Agente Especialista em Protocolos e Agente Orquestrador, utilizando handoffs, tools, histórico de mensagens e validação de saída. |
| 8 | **Integração entre Agentes e Modelo** | 1,0 | Integração funcional entre o modelo preditivo e os agentes, permitindo receber os dados do paciente, calcular o risco, consultar protocolos e gerar uma resposta final estruturada. |
| 9 | **Trabalho em Equipe e Colaboração Interdisciplinar** | 1,0 extra | Desenvolvimento da atividade em grupo de 4 a 5 integrantes, com organização, cooperação, comunicação e divisão equilibrada das tarefas. |

## IR ALÉM 1 (Opcional) – Governança e Monitoramento de Decisões em IA

Sistemas de IA aplicados à saúde precisam de rastreabilidade e responsabilidade. Neste desafio opcional, o grupo deverá adicionar ao sistema multiagente uma camada de monitoramento e auditoria das decisões (disciplina GBA). Você deverá desenvolver:

- Registro das decisões: registrar as decisões do sistema (score previsto, classificação de risco e protocolos sugeridos) em uma estrutura organizada, como um log estruturado ou um arquivo JSON.
- Validação de coerência: implementar uma verificação simples de coerência, por exemplo validando se os protocolos acionados estão alinhados às variáveis críticas do paciente, permitindo a análise posterior das recomendações.

### Objetivo

Introduzir responsabilidade, rastreabilidade e auditoria ao sistema, conectando o modelo e os agentes a princípios de governança em IA.

### Entregáveis

- A entrega do Ir Além 1 será feita dentro do mesmo repositório GitHub privado da atividade principal. Portanto, a equipe não deve criar outro repositório e também não precisa colocar outro link de GitHub no arquivo .txt enviado no Portal do Aluno.

- Caso a equipe queira participar do Ir Além 1, deverá apenas adicionar os arquivos dessa atividade extra dentro da pasta específica chamada IR ALÉM, existente no modelo de repositório disponibilizado pela coordenação.

- No mesmo arquivo .txt enviado no Portal do Aluno, a equipe deverá manter o link do repositório GitHub da atividade principal e acrescentar apenas o link do vídeo demonstrativo do Ir Além 1.

Na pasta IR ALÉM do repositório do grupo, deverão constar:

- Extensão funcional com o mecanismo de registro e validação.
- Relatório técnico (máximo duas páginas) explicando como as decisões são registradas, como a validação é feita e a importância da governança em IA na saúde.
- Evidência de execução (print ou trecho de log com o registro das decisões).
- O grupo deverá produzir um vídeo demonstrativo de até 4 minutos, apresentando o funcionamento completo da solução. O vídeo pode ser feito com gravação de tela e explicação por voz ou legenda. Após a gravação, o vídeo deverá ser publicado no YouTube como “não listado”. Na entrega, o grupo deverá colocar o link do vídeo no mesmo arquivo .txt enviado no Portal do Aluno e também no README.md do repositório GitHub.

### Critérios de Avaliação

- Implementação correta do registro (logs estruturados e rastreáveis).
- Validação de coerência funcionando e bem justificada.
- Clareza na documentação do fluxo e das decisões.
- Organização do código e argumentação sobre governança e responsabilidade em IA na saúde.

## IR ALÉM 2 (Opcional) – Otimização e Escalabilidade do Sistema Multiagente

Um sistema real precisa atender a muitas requisições. Neste desafio opcional, o grupo deverá propor uma estratégia de escalabilidade e organização modular do pipeline multiagente (disciplina Cluster Computing, Computação Neuromórfica e Supercomputadores). Você deverá desenvolver:

- Organização modular: estruturar o sistema em módulos independentes (modelo preditivo, agentes, orquestrador), com separação clara de responsabilidades.
- Simulação de carga: simular o processamento de múltiplos pacientes em sequência ou em lote, com um mecanismo simples de controle de execução (por exemplo, uma fila simulada), e documentar como o sistema poderia evoluir para um ambiente distribuído real.

### Objetivo

Introduzir conceitos de organização arquitetural, escalabilidade e preparação para cenários de maior carga computacional.

### Entregáveis

- A entrega do Ir Além 2 será feita dentro do mesmo repositório GitHub privado da atividade principal. Portanto, a equipe não deve criar outro repositório e também não precisa colocar outro link de GitHub no arquivo .txt enviado no Portal do Aluno.

- Caso a equipe queira participar do Ir Além 2, deverá apenas adicionar os arquivos dessa atividade extra dentro da pasta específica chamada IR ALÉM, existente no modelo de repositório disponibilizado pela coordenação.

- No mesmo arquivo .txt enviado no Portal do Aluno, a equipe deverá manter o link do repositório GitHub da atividade principal e acrescentar apenas o link do vídeo demonstrativo do Ir Além 2.

Na pasta IR ALÉM do repositório do grupo, deverão constar:

- Extensão do projeto demonstrando o processamento de múltiplos casos.
- Atualização do README explicando a organização modular adotada.
- Relatório técnico (máximo duas páginas) com a estrutura modular, a estratégia de simulação de múltiplas requisições e os caminhos para a evolução distribuída.
- O grupo deverá produzir um vídeo demonstrativo de até 4 minutos, apresentando o funcionamento completo da solução. O vídeo pode ser feito com gravação de tela e explicação por voz ou legenda. Após a gravação, o vídeo deverá ser publicado no YouTube como “não listado”. Na entrega, o grupo deverá colocar o link do vídeo no mesmo arquivo .txt enviado no Portal do Aluno e também no README.md do repositório GitHub.

### Critérios de Avaliação

- Organização modular clara e coerente.
- Simulação funcional de múltiplos casos.
- Coerência técnica na proposta de escalabilidade.
- Clareza na documentação e na argumentação técnica.

## Mensagem final

Na Fase 6, o CardioIA evolui de um sistema interativo para um sistema preditivo e estratégico. O projeto passa a incorporar modelos de Machine Learning integrados a arquiteturas multiagentes, permitindo antecipar situações críticas e apoiar decisões emergenciais. Esta etapa consolida competências em modelagem preditiva, integração de agentes inteligentes e tomada de decisão baseada em dados, ampliando a maturidade técnica do projeto.
