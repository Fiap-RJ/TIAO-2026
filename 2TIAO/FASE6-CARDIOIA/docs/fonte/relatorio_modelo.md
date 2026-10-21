<div class="cabecalho" markdown="1">
<img src="../../assets/logo-fiap.png" alt="Logo FIAP">
<div><strong>CardioIA — Fase 6 "Coração Sob Controle"</strong><br><span class="pequeno">Relatório do modelo preditivo de pico de risco · FIAP · Graduação em Inteligência Artificial</span></div>
</div>

# Relatório do modelo preditivo

Fonte dos números: execução salva de `src/CardioIA_Fase6_Modelo_Preditivo.ipynb` e `models/modelo_pico_risco.metadata.json` (Python 3.12.3, scikit-learn 1.9.1, numpy 2.5.4, pandas 3.0.6). Sistema acadêmico e informativo: não faz diagnóstico nem prescrição.

## 1. Base e variável-alvo

- Base sintética gerada pelo código literal do enunciado (`np.random.seed(42)`, 5.000 registros, 10 features). O mesmo código está em `src/ml/dataset.py`, então a base é regerada de forma idêntica e não é versionada.
- Features (ordem canônica): `idade_media`, `carga_sistema`, `tempo_espera`, `fc_media`, `spo2_media`, `pa_sistolica`, `temperatura`, `densidade_eventos`, `eventos_24h`, `disponibilidade_recursos`. Zero valores nulos.
- Alvo `pico_risco` = 1 quando pelo menos 2 de 6 regras de limiar são verdadeiras: `carga_sistema > 80`, `tempo_espera > 60`, `spo2_media < 92`, `fc_media > 110`, `eventos_24h > 4`, `disponibilidade_recursos < 40`. A soma auxiliar `risk_score` fica fora de `X` para não vazar o alvo.
- Prevalência de positivos: 26,58%. Split 80/20 estratificado (`random_state=42`): 4.000 treino (26,58%) e 1.000 teste (26,6%).

## 2. Algoritmos: baseline e modelo principal

| Modelo | Papel | Hiperparâmetros |
|---|---|---|
| Regressão Logística | baseline interpretável | `StandardScaler` + `LogisticRegression(max_iter=1000, random_state=42)` num `Pipeline` |
| Random Forest | modelo principal | `RandomForestClassifier(n_estimators=200, random_state=42)` |

Por que Random Forest: o alvo é uma soma de funções degrau. Uma fronteira linear não representa "pelo menos 2 de 6 condições", e é por isso que a LR perde recall. Árvores aprendem cortes por limiar diretamente. A média de 200 árvores ainda gera probabilidades graduais, que alimentam as faixas BAIXO (< 0,40), MODERADO (0,40–0,70) e ALTO (≥ 0,70) usadas pelos agentes. Uma árvore única devolveria quase sempre 0 ou 1.

## 3. Métricas no conjunto de teste (1.000 registros) e validação cruzada

| Modelo | Acurácia | Precisão (1) | Recall (1) | F1 (1) | Acurácia CV 5-fold (treino) | Matriz [TN FP / FN TP] |
|---|---:|---:|---:|---:|---:|---|
| Regressão Logística | 0,8160 | 0,6934 | 0,5526 | 0,6151 | 0,8297 ± 0,0140 | [669 65 / 119 147] |
| **Random Forest** | **0,9990** | **1,0000** | **0,9962** | **0,9981** | **0,9977 ± 0,0018** | **[734 0 / 1 265]** |

CV: `StratifiedKFold(5, shuffle=True, random_state=42)` só no treino. A baixa variação entre dobras (desvio 0,0018 no RF) mostra que o resultado não depende de um split favorável.

<img src="../../assets/matriz_confusao_rf.png" alt="Matriz de confusão do Random Forest no conjunto de teste" style="float: right; width: 34%; margin: 0 0 4px 10px;">

**Falso negativo × falso positivo.** O erro grave aqui é o falso negativo: um pico real classificado como "sem pico" deixa a unidade sem preparação (leitos, insumos, equipe). O falso positivo mobiliza recursos à toa, mas é recuperável. A LR erra 119 positivos (FN) e 65 negativos (FP). O RF erra 1 FN e nenhum FP. Por isso o recall da classe 1 pesa mais na escolha que a acurácia isolada.

**Simulação do `novo_caso` do enunciado.** Depois do `rename` de `"disponibilidade recursos"` (chave com espaço) para `disponibilidade_recursos`, o RF devolve **p = 0,99** → classe 1 (limiar 0,5) → **ALTO**. O `.joblib` recarregado dá a mesma probabilidade.

## 4. Por que a acurácia é ~100% (e não é vazamento)

O alvo é função determinística das próprias features, sem ruído, e as árvores reaprendem os seis cortes. O split é correto (estratificado, `risk_score` fora de `X`), então não há informação do teste no treino. O que existe é uma base sintética trivialmente separável. As importâncias do RF confirmam isso:

| Features da regra do alvo | Importância | Features fora da regra | Importância |
|---|---:|---|---:|
| `carga_sistema` | 0,2330 | `idade_media` | 0,0129 |
| `disponibilidade_recursos` | 0,2242 | `temperatura` | 0,0119 |
| `tempo_espera` | 0,2020 | `pa_sistolica` | 0,0115 |
| `spo2_media` | 0,1660 | `densidade_eventos` | 0,0050 |
| `fc_media` / `eventos_24h` | 0,0695 / 0,0641 | **soma** | **0,0413** |

As 6 features da regra somam 0,9587. O resíduo das outras 4 vem de divisões aleatórias das árvores, não de sinal real.

## 5. Limitações

- Dados sintéticos e sem ruído: a acurácia não indica desempenho em dados reais, e a generalização não está comprovada.
- Desbalanceamento moderado (26,6% de positivos), tratado com `stratify` no split e na CV.
- Semântica ambígua de `temperatura`: a média 24 sugere temperatura ambiente, mas o protocolo P07 fala em > 38 °C (febre).
- Cada registro mistura indicadores do paciente (FC, SpO2, PA) e da unidade (carga, espera, recursos).
- As probabilidades do RF não são calibradas: servem para ordenar o risco e definir faixas, não como frequência exata.
- Pickle do scikit-learn: o artefato só é garantido nas versões do `requirements.txt`. O sistema avisa em runtime se a versão mudar.

## 6. Melhorias propostas

Dados reais rotulados por especialistas, ruído e rótulos incertos na simulação, validação temporal (treino no passado, teste no futuro), calibração de probabilidade (`CalibratedClassifierCV`), ajuste do limiar de decisão pelo custo do falso negativo e monitoramento de drift das features contra as `faixas_treino` salvas nos metadados.

<p class="pequeno" markdown="1">Reprodutibilidade: sementes fixas (42) e o `.joblib` com o mesmo SHA-256 em execuções repetidas. Em outro runtime (por exemplo, o Colab com outras versões de bibliotecas), as métricas podem variar levemente.</p>
