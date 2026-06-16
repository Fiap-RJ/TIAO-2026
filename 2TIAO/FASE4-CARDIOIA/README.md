# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# CardioIA: A Nova Era da Cardiologia Inteligente

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/michaelrodriguess/">Michael Rodrigues</a>
- <a href="https://www.linkedin.com/in/arthur-alentejo/">Arthur Alentejo</a>
- <a href="https://www.linkedin.com/in/nathalia-vasconcelos-18a390292/">Nathalia Vasconcelos</a> 

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="#">Caique (CaiqueFiap-2026)</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godói</a>

## 📜 Descrição

OO CardioIA é um ecossistema inteligente voltado à cardiologia moderna digital. Nesta quarta fase do projeto, avançamos do monitoramento de dados biométricos (IoT) para a análise automatizada de exames diagnósticos utilizando Visão Computacional.

O principal desafio desta etapa foi projetar, treinar e avaliar modelos de Redes Neurais Convolucionais (CNNs) capazes de processar exames simulados de eletrocardiograma (ECG) compostos por traçados contínuos de 12 derivações. O protótipo é estruturado para classificar com precisão quatro estados clínicos cardiovasculares distintos, otimizando o fluxo de triagem e auxiliando na tomada de decisão médica rápida e confiável.

### 🚀 Entregas da Fase 4

Nesta fase do projeto, o pipeline técnico e os artefatos de entrega foram divididos conforme as diretrizes de reprodutibilidade e governança em saúde digital:

O Dataset de imagens selecionado foi o mesmo da Fase 1 o ECG Images Dataset, disponível em:  https://www.kaggle.com/datasets/jayaprakashpondy/ecgimages/data

Dataset Clínico Processado: Base de dados composta por eletrocardiogramas contendo exames de 4 classes:

  - Normal Person ECG Images (Normalidade)

 - ECG Images of Myocardial Infarction Patients (Infarto Agudo do Miocárdio)

 - ECG Images of Patient that have abnormal heartbeat (Arritmias Cardíacas)

 - ECG Images of Patient that have History of MI (Histórico de Infarto Prévio)

Notebook de Pré-processamento e Modelagem: Pipeline completo em Python (Google Colab) englobando desde a ingestão, resize geométrico, normalização e divisão dos dados, até o treinamento comparativo das Redes Convolucionais.

Protótipo Interativo: Painel de Diagnóstico Comparativo integrado para upload de ECGs e inferência probabilística em tempo real das redes concorrentes.

Relatório Técnico: Documentação científica curta analisando o desempenho das abordagens de baseline do zero frente ao Transfer Learning.

### ⚙️ Pipeline de Engenharia de Dados 

O pipeline de preparação de imagens médicas seguiu etapas metodológicas fundamentais para garantir a eficácia do aprendizado profundo (Deep Learning):

Redimensionamento Geométrico: As imagens originais, provenientes de diferentes sensores e resoluções, foram redimensionadas para um padrão estrito de $224 \times 224$ pixels utilizando algoritmos de interpolação do OpenCV (cv2.resize). Essa conformidade geométrica é um pré-requisito matemático obrigatório para alimentar redes convolucionais e modelos pré-treinados.

Normalização Estatística de Pixels: Conversão de valores binários brutos $[0, 255]$ para matrizes de ponto flutuante restritas ao intervalo $[0.0, 1.0]$. A normalização diminui a magnitude das perdas matemáticas (Loss) durante o backpropagation, evitando problemas de explosão ou desvanecimento de gradientes (vanishing gradients).

Divisão Estratégica dos Dados: Para mitigar e monitorar a decoreba de dados (overfitting), o conjunto de dados foi fatiado sob uma lógica de validação cruzada robusta:

Treino: 531 imagens (ajuste iterativo dos pesos sinápticos).

Validação: 133 imagens (fase de sintonia de hiperparâmetros a cada época).

Teste: 280 imagens (base totalmente isolada de ECGs inéditos para aferição do laudo final).

  
### 🧠 Abordagens de Modelagem de IA 

O estudo de caso desafiou o grupo a comparar duas filosofias clássicas de treinamento em IA:

#### Abordagem A: CNN Convolucional do Zero 

Desenvolvemos uma arquitetura sequencial customizada e compacta com:

- Camadas Conv2D acopladas a funções de ativação ReLu para a identificação de picos, segmentos (PR, ST) e complexos QRS característicos nas linhas geométricas do sinal de ECG.

- Camadas MaxPooling2D para redução de dimensionalidade espacial e manutenção de invariância translacional.

- Regularização por Dropout(0.5) para prevenir o acoplamento excessivo aos dados de treino.

- Camada densa de saída com função de ativação Softmax de 4 classes.



#### Abordagem B: Transfer Learning com VGG16 (Análise Crítica)

Buscando aplicar o reaproveitamento de conhecimento de grandes redes, importamos a base convolucional da VGG16 pré-treinada com os pesos do ImageNet com o topo congelado, adicionando as camadas densas de diagnóstico ao final.


### 🖥️ Protótipo: Assistente Cardiológico Virtual

O protótipo final foi projetado para atuar como uma Célula de Diagnóstico Interativo unificada de apoio à decisão médica. O painel interativo realiza o processamento paralelo e simultâneo das duas redes de Visão Computacional.

Como Executar o Protótipo Interativo

Abra o arquivo /notebooks/CardioIA_Preprocessamento.ipynb no ambiente do Google Colab.

Altere o tipo de ambiente de execução para T4 GPU para garantir a aceleração de hardware.

Execute todas as células de pré-processamento e treinamento sequencialmente.

Na célula final correspondente ao "Assistente Cardiológico Virtual", execute o código e clique em "Escolher arquivos".

Faça o upload de uma imagem de ECG do dataset de testes e visualize o painel comparativo renderizado em tempo real.

Demonstração do painel diagnóstico comparando as barras de confiança de ambos os modelos:
[Insira aqui: Print_Painel_Diagnostico_Assistente.png]


## 📁 Estrutura de Pastas do Projeto

O repositório está organizado de forma clara e padronizada seguindo boas práticas de governança técnica:

```
├── assets/                  # Logos e imagens auxiliares do README
├── dataset/                 # Diretório estruturado de treino, teste e classes (imagens locais)
│   ├── train/
│   └── test/
├── src/               # Código-fonte principal em formato Jupyter Notebook (.ipynb)
│   └── CardioIA_Preprocessamento.ipynb
├── document/                 # PDF consolidado do Relatório Técnico
│   └── Relatorio_Tecnico_CardioIA_Fase4.pdf
├── requirements.txt         # Arquivo de dependências necessárias para a reprodução do ambiente
└── README.md                # Este documento de documentação geral

```


🗃 Histórico de Lançamentos

12/06/2026

Entrega da Fase 4: Implementação do pipeline de Visão Computacional (CNN customizada), análise comparativa frente à VGG16 pré-treinada e lançamento do protótipo do painel de triagem médica comparativa.



📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>