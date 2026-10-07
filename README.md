# FIAP - TIAO 2026

<p align="center">
<a href="https://www.fiap.com.br/"><img src="2TIAO/ENTERPRISE-CHALLENGE/assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="30%" height="30%"></a>
</p>

<br>

# Portfólio de Projetos - Programa de Inteligência Artificial

Este repositório consolida o portfólio de projetos acadêmicos do **Programa de Inteligência Artificial da FIAP (2026)**, desenvolvido durante a trajetória de 2 anos de aprendizado em IA, Machine Learning, e Desenvolvimento de Software.

## 📂 Estrutura do Repositório

### 1. **2TIAO/** — Ano 2 (Graduação)

Projetos e entregas do segundo ano do programa:

#### **[ENTERPRISE-CHALLENGE](2TIAO/ENTERPRISE-CHALLENGE/)** — Genera Intelligence
- **Descrição:** Sistema RAG multimodelo para interpretação de laudos genéticos usando LLM (Google Gemini / OpenAI GPT-4o-mini)
- **Stack:** FastAPI + LangGraph + FAISS + SQLite + React + Docker
- **Sprints:** 1 a 4 (Fundação → Motor RAG → UX → Produção & Governança)
- **Status:** ✅ Em Produção (Render)
- **[Leia o README completo →](2TIAO/ENTERPRISE-CHALLENGE/README.md)**

---

#### **[FASE4-CARDIOIA](2TIAO/FASE4-CARDIOIA/)** — CardioIA: Diagnóstico Cardiológico com Visão Computacional
- **Descrição:** Pipeline de CNN para classificação automatizada de eletrocardiogramas (ECG) em 4 estados clínicos
- **Stack:** TensorFlow/Keras + OpenCV + Google Colab Notebooks
- **Foco:** Visão Computacional, Deep Learning, Transfer Learning
- **Dataset:** ECG Images Dataset (Kaggle) — 944 imagens de 4 classes (Normal, IAM, Arritmia, Histórico de MI)
- **Modelo:** CNN customizada vs VGG16 (análise comparativa)
- **[Leia o README completo →](2TIAO/FASE4-CARDIOIA/README.md)**

---

#### **[FASE5-CARDIOIA](2TIAO/FASE5-CARDIOIA/)** — CardioIA Fase 5
- **Descrição:** Evolução do projeto CardioIA com aprimoramentos na arquitetura de modelos e pipeline de inferência
- **[Leia o README completo →](2TIAO/FASE5-CARDIOIA/README_fase5.md)**

---

#### **[Global-Solution-1](2TIAO/Global-Solution-1/)** — Orbital RAG
- **Descrição:** Solução de RAG para consultas sobre sustentabilidade e objetivos ONU
- **Stack:** Node.js/Express + React + LangChain
- **[Leia o README completo →](2TIAO/Global-Solution-1/orbital-rag-front/README.md)**

---

## 🎯 Objetivos de Aprendizado

Este portfólio demonstra competências em:

| Área | Projetos |
|------|----------|
| **Inteligência Artificial & LLM** | Genera Intelligence, Orbital RAG |
| **Machine Learning & Deep Learning** | CardioIA (Fases 4-5) |
| **Visão Computacional** | CardioIA (CNN, Transfer Learning) |
| **Engenharia de Software** | Genera Intelligence (CI/CD, IaaC, Deployment) |
| **Engenharia de Dados** | Genera Intelligence (ETL, Vector Store), CardioIA (Preprocessing) |
| **Web Development** | Frontend React, Backend FastAPI/Node.js |
| **DevOps & Infrastructure** | Docker, Docker Compose, Render, GitHub Actions |
| **Governança & Segurança** | Genera Intelligence (PII Redaction, LGPD, Guardrails) |

---

## 🚀 Quick Start

### Iniciar Genera Intelligence (ENTERPRISE-CHALLENGE)

```bash
cd 2TIAO/ENTERPRISE-CHALLENGE/

# Opção 1: Docker Compose (recomendado)
make up

# Opção 2: Desenvolvimento local
make install
make seed
make serve

# Resultado:
#   Frontend: http://localhost:3000
#   API:      http://localhost:8000
#   Swagger:  http://localhost:8000/docs
```

### Testar CardioIA (FASE4-CARDIOIA)

1. Abra `2TIAO/FASE4-CARDIOIA/src/CardioIA_Preprocessamento.ipynb` no Google Colab
2. Altere o tipo de GPU para T4
3. Execute todas as células
4. Use o painel de diagnóstico interativo para fazer upload de ECGs

---

## 📋 Documentação Adicional

- **Governança & Segurança (Genera Intelligence):** [`2TIAO/ENTERPRISE-CHALLENGE/document/governanca_e_riscos.md`](2TIAO/ENTERPRISE-CHALLENGE/document/governanca_e_riscos.md)
- **Deployment Guide (Render):** [`2TIAO/ENTERPRISE-CHALLENGE/config/render/RENDER_SETUP.md`](2TIAO/ENTERPRISE-CHALLENGE/config/render/RENDER_SETUP.md)
- **Relatório Técnico CardioIA:** [`2TIAO/FASE4-CARDIOIA/document/Relatorio_Tecnico_CardioIA_Fase4.pdf`](2TIAO/FASE4-CARDIOIA/document/Relatorio_Tecnico_CardioIA_Fase4.pdf)

---

## 👥 Equipe

### Sprint 4 (ENTERPRISE-CHALLENGE & CARDIO FASES)

- **[Arthur Guimarães Alentejo](https://www.linkedin.com/in/arthur-alentejo)** — Backend, DevOps, Arquitetura
- **[Michael Rodrigues](https://www.linkedin.com/in/michaelrodriguess)** — IA/LLM, Deep Learning
- **[Nathalia Vasconcelos](https://www.linkedin.com/in/nathalia-vasconcelos-18a390292/)** — Frontend, NLP, UX

### Professores

- **Tutor:** Caique (CaiqueFiap-2026)
- **Coordenador:** [André Godói](https://www.linkedin.com/in/andregodoichiovato/)

---

## 📺 Vídeos de Apresentação

- **[Genera Intelligence Sprint 4](https://youtu.be/UzV9BVh9IHs)** — Produção e Governança (Deploy + IaaC + CI/CD)
- **[Genera Intelligence Sprint 2](https://youtu.be/y-MmL1nKIFg)** — Motor RAG & Agentes
- **[Genera Intelligence Sprint 1](https://youtu.be/mASJnbO3dqo)** — Fundação e Arquitetura

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

---

**Última atualização:** Outubro 2026
