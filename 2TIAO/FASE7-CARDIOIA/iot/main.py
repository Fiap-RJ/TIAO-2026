import network
import time
import ujson
import urequests
from machine import Pin, ADC, I2C
import dht
import ssd1306

# ==========================================================
# 1. Configurações de Rede, API e Pinos
# ==========================================================
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# URL pública do backend integrador (Render). A DEVICE_KEY não é versionada:
# no Wokwi, substitua pelo mesmo valor configurado no painel do Render.
API_URL = "https://cardioia-backend-phkq.onrender.com/api/leituras"
DEVICE_KEY = "INSIRA_A_DEVICE_KEY_DO_RENDER"
PACIENTE_ID = "p-001"

# Pinos dos Sensores
PIN_DHT = 15
PIN_POT = 34

# Pinos dos Atuadores e Display
PIN_LED_VERDE = 4
PIN_LED_AMARELO = 17
PIN_LED_VERMELHO = 16
PIN_I2C_SDA = 21
PIN_I2C_SCL = 22

# Inicialização de Sensores e Pinos
sensor_dht = dht.DHT22(Pin(PIN_DHT))
pot_fc = ADC(Pin(PIN_POT))
pot_fc.atten(ADC.ATTN_11DB)  # Permite leitura na faixa de 0 a 3.3V (valores de 0 a 4095)

led_verde = Pin(PIN_LED_VERDE, Pin.OUT)
led_amarelo = Pin(PIN_LED_AMARELO, Pin.OUT)
led_vermelho = Pin(PIN_LED_VERMELHO, Pin.OUT)

# Configuração do Display OLED (128x64) via I2C
i2c = I2C(0, scl=Pin(PIN_I2C_SCL), sda=Pin(PIN_I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Histórico para cálculo de Média Móvel (Buffer de 5 leituras)
historico_fc = []
TAMANHO_JANELA = 5

# ==========================================================
# 2. Funções de Apoio
# ==========================================================
wlan = network.WLAN(network.STA_IF)

def conectar_wifi():
    """Conecta ao Wi-Fi Wokwi-GUEST, no mesmo padrão da documentação do Wokwi.

    Chama connect() uma única vez e espera o tempo necessário: no simulador a
    conexão leva cerca de 15 a 20 s, e chamar connect() de novo no meio da
    tentativa a reinicia.
    """
    wlan.active(True)
    if wlan.isconnected():
        return
    oled.fill(0)
    oled.text("CardioIA - IoT", 0, 0)
    oled.text("Conectando WiFi", 0, 20)
    oled.show()
    print("Conectando ao Wi-Fi", end="")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.1)
    print("\nWi-Fi conectado:", wlan.ifconfig()[0])

def calcular_media_movel(novo_valor):
    """Calcula a média móvel simples dos batimentos cardíacos."""
    historico_fc.append(novo_valor)
    if len(historico_fc) > TAMANHO_JANELA:
        historico_fc.pop(0)
    return int(sum(historico_fc) / len(historico_fc))

def classificar_estado_local(fc, temp):
    """Classifica as métricas em Normal, Atenção ou Crítico."""
    if fc < 50 or fc > 120 or temp > 38.0:
        return "CRITICO", led_vermelho
    elif (50 <= fc < 60) or (101 <= fc <= 120) or (37.5 <= temp <= 38.0):
        return "ATENCAO", led_amarelo
    else:
        return "NORMAL", led_verde

def atualizar_atuadores(led_ativo, fc, temp, status):
    """Atualiza a iluminação dos LEDs e as mensagens no OLED."""
    # Apaga todos os LEDs e acende apenas o do estado atual
    led_verde.value(0)
    led_amarelo.value(0)
    led_vermelho.value(0)
    led_ativo.value(1)

    # Exibição no OLED
    oled.fill(0)
    oled.text("CardioIA Monitor", 0, 0)
    oled.text("FC Med: {} bpm".format(fc), 0, 16)
    oled.text("Temp: {:.1f} C".format(temp), 0, 32)
    oled.text("Estado: {}".format(status), 0, 48)
    oled.show()

def enviar_para_backend(fc, temp, estado):
    """Encaminha telemetria para o endpoint FastAPI com tratamento de falhas."""
    if not wlan.isconnected():
        # O ESP32 reconecta sozinho; até lá a leitura fica só no OLED/LEDs.
        print("Wi-Fi desconectado: leitura mantida apenas no dispositivo.")
        return
    headers = {
        "Content-Type": "application/json",
        "X-Device-Key": DEVICE_KEY
    }
    payload = {
        "paciente_id": PACIENTE_ID,
        "temperatura": float(temp),
        "fc": int(fc),
        "spo2": 97.0,  # Leitura simulada padrão
        "estado": estado.lower(),
        # Sem "ts": o ESP32 não tem relógio sincronizado (time.time() conta a
        # partir de 2000), então o backend registra o horário de recebimento.
    }
    try:
        res = urequests.post(API_URL, data=ujson.dumps(payload), headers=headers)
        print("Envio concluido. Status HTTP:", res.status_code)
        res.close()
    except Exception as erro:
        print("Erro de conexao HTTP ao enviar dados:", erro)

# ==========================================================
# 3. Ciclo Principal de Execução
# ==========================================================
conectar_wifi()

while True:
    # 1. Leitura de Temperatura (DHT22)
    try:
        sensor_dht.measure()
        temperatura = sensor_dht.temperature()
    except Exception:
        temperatura = 36.5  # Fallback caso ocorra oscilação na leitura

    # 2. Leitura analógica do Potenciômetro e cálculo da média móvel
    leitura_analogica = pot_fc.read()
    # Mapeamento do range 0..4095 para 40..180 bpm
    fc_instantanea = int(40 + (leitura_analogica / 4095.0) * 140)
    fc_filtrada = calcular_media_movel(fc_instantanea)

    # 3. Classificação de borda e feedback visual
    estado, led_selecionado = classificar_estado_local(fc_filtrada, temperatura)
    atualizar_atuadores(led_selecionado, fc_filtrada, temperatura, estado)

    # 4. Transmissão para o Render via HTTP POST
    enviar_para_backend(fc_filtrada, temperatura, estado)

    # Intervalo de 5 segundos entre as amostras
    time.sleep(5)
