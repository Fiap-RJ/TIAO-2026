# Relatório Técnico de Migração de Firmware: C/C++ para MicroPython (Fase 3 -> Fase 7)
**Projeto:** CardioIA — Monitoramento Cardíaco Inteligente  
**Curso:** Tecnólogo em Inteligência Artificial — FIAP  
**Autora:** Nathalia Vasconcelos  

---

## 1. Visão Geral e Contexto da Transição

Durante a **Fase 3**, o dispositivo IoT de coleta biomédica do CardioIA foi concebido utilizando a linguagem **C/C++** sobre o framework Arduino no ESP32. Naquela arquitetura inicial, o foco estava na leitura direta de sensores e publicação assíncrona de variáveis discretas via protocolo **MQTT** sobre TLS (porta 8883) conectado ao HiveMQ Cloud, utilizando retenção offline rudimentar em buffer de texto plano (`String`).

Ao atingir a **Fase 7 (MVP Integrado)**, os requisitos do ecossistema evoluíram. O backend consolidador passou a operar inteiramente em **Python (FastAPI)**, integrando modelos de Machine Learning (Random Forest) e agentes LLM (IBM Watson Assistant e OpenAI). Para reduzir a dissonância técnica da stack, simplificar rotinas de manutenção, unificar o tratamento de payloads e viabilizar inteligência de borda direta (classificação local e suavização temporal), foi realizada a migração completa do firmware para **MicroPython (v1.2x)**.

---

## 2. Quadro Comparativo de Arquitetura

| Dimensão Técnica | Implementação Fase 3 (C/C++) | Implementação Fase 7 (MicroPython) | Racional Técnico da Mudança |
| :--- | :--- | :--- | :--- |
| **Linguagem & Ambiente** | C++ (Arduino Framework / ESP-IDF) | MicroPython v1.2x | Interoperabilidade e uniformidade de linguagem com todo o backend e IA da solução. |
| **Protocolo de Rede** | MQTT / MQTTS (`PubSubClient` / porta 8883) | HTTP/1.1 REST (`urequests` POST) | Alinhamento direto com o contrato das rotas Pydantic da API integradora (`/api/leituras`). |
| **Mecanismo de Segurança** | Credenciais embutidas no código (User/Pass HiveMQ) | Header HTTP `X-Device-Key` | Validação de autenticidade por cabeçalho de dispositivo sem complexidade de certificados TLS no Wokwi. |
| **Tratamento de Sinal** | Conversão linear bruta de ADC (`map(0, 4095, 40, 180)`) | Média móvel com janela deslizante de 5 amostras | Filtragem digital em borda para eliminar oscilações de alta frequência e ruídos transitórios do ADC. |
| **Classificação de Borda** | Inexistente (dispositivo puramente coletor/passivo) | Máquina de estados clínica (Normal, Atenção, Crítico) | Triagem instantânea local no próprio microcontrolador sem depender de resposta síncrona do servidor. |
| **Feedback ao Usuário** | Monitor Serial exclusivo (`Serial.printf`) | 3 LEDs de sinalização + Display OLED I2C (SSD1306) | Human-Machine Interface (HMI) visual para uso imediato no leito hospitalar. |
| **Resiliência a Falhas** | Buffer estático em `String` para reenvio MQTT | Tratamento estruturado via blocos `try/except` | Tolerância a instabilidades de rede com liberação de sockets (`res.close()`) evitando estouro de heap. |

---

## 3. Análise Detalhada dos Componentes Técnicos

### 3.1. Aquisição Analógica e Condicionamento de Sinais
* **Fase 3 (C++):** A leitura da frequência cardíaca utilizava a função `analogRead(PIN_BPM)` associada a `map()`. Leituras bruscas do potenciômetro causavam picos artificiais de taquicardia ou bradicardia.
* **Fase 7 (MicroPython):** Foi configurada atenuação analógica de 11 dB (`ADC.ATTN_11DB`) para cobrir a excursão de 0 a 3,3 V. Introduziu-se a função `calcular_media_movel()`, retendo as últimas 5 leituras em uma lista dinâmica antes de enviar o batimento estabilizado para a classificação e telemetria.

### 3.2. Barramento de Comunicação I2C e Display Gráfico
* **Fase 3 (C++):** Não havia interface visual montada no microcontrolador.
* **Fase 7 (MicroPython):** Implementou-se o barramento I2C por software/hardware utilizando os pinos GPIO 21 (SDA) e GPIO 22 (SCL). Com o driver modular `ssd1306.py`, o display gráfico de 128x64 pixels passou a renderizar em tempo real o cabeçalho do projeto, a frequência cardíaca média filtrada, a temperatura corporal em graus Celsius e a classificação do paciente.

### 3.3. Transição do Protocolo: MQTT vs. HTTP Integrador
* **Fase 3 (C++):** A dependência de um broker MQTT externo (HiveMQ) criava um ponto único de falha desvinculado das regras de negócio do backend central. Os dados precisavam ser assinados em tópicos segmentados (`cardioia/sensor/temperatura` e `cardioia/sensor/batimentos`).
* **Fase 7 (MicroPython):** A unificação do tráfego através de chamadas HTTP POST atômicas para `/api/leituras` permitiu o empacotamento das variáveis (`paciente_id`, `fc`, `temperatura`, `spo2`, `ts`) em um único objeto JSON estruturado. Isso reduziu o tráfego de rede e possibilitou que o backend em FastAPI persista as leituras no SQLite e dispare a reavaliação de risco preditivo de forma síncrona.

---

## 4. Conclusão Técnica

A reengenharia do firmware de C/C++ para MicroPython simplificou o ciclo de desenvolvimento e testes simulados no Wokwi, transformando um componente que atuava como mero transmissor de dados brutos em um nó inteligente de borda (*Edge Computing*). O firmware atual filtra sinais espúrios, provê diagnóstico visual imediato no leito hospitalar e comunica-se de maneira segura e direta com o ecossistema integrado do CardioIA.